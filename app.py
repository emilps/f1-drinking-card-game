try:
    import streamlit as st
    import pandas as pd
    import time
    import base64
    import os
    from PIL import Image
    import io
except ImportError:
    # For handling LSP checks where modules might not be available
    pass
from game_logic import (
    initialize_game,
    draw_card,
    move_horse,
    check_checkpoint,
    check_winner,
    reset_game
)
from assets.card_images import get_card_image, get_card_back
from assets.animations import (
    animation_css, 
    animate_card_draw, 
    animate_horse_movement,
    animate_checkpoint_flip,
    apply_animations
)

# Page config
st.set_page_config(
    page_title="Drinking Card Game",
    page_icon="🃏",
    layout="wide"
)

# Add animation CSS
st.markdown(animation_css(), unsafe_allow_html=True)

# Initialize session state
if 'game_initialized' not in st.session_state:
    st.session_state.game_initialized = False
    
if 'players' not in st.session_state:
    st.session_state.players = []
    
if 'game_state' not in st.session_state:
    st.session_state.game_state = None
    
if 'drawn_cards' not in st.session_state:
    st.session_state.drawn_cards = []
    
if 'winner' not in st.session_state:
    st.session_state.winner = None
    
if 'total_stakes' not in st.session_state:
    st.session_state.total_stakes = 0
    
if 'horse_names' not in st.session_state:
    st.session_state.horse_names = {
        'hearts': 'Hearts',
        'diamonds': 'Diamonds',
        'clubs': 'Clubs',
        'spades': 'Spades'
    }

# Function to display racing car images
def get_racecar_image(suit):
    """
    Returns an HTML img element for the corresponding racing team based on the suit.
    
    Args:
        suit (str): Card suit (hearts, diamonds, clubs, spades)
        
    Returns:
        str: HTML img element with the racing team logo
    """
    # Map suits to racing team image files
    team_images = {
        'hearts': 'attached_assets/mclaren.avif',
        'diamonds': 'attached_assets/mercedes.avif',
        'clubs': 'attached_assets/ferrari.avif',
        'spades': 'attached_assets/red-bull-racing.avif'
    }
    
    if suit not in team_images:
        # Fallback to displaying the team name as text
        return st.session_state.horse_names.get(suit, suit)
    
    try:
        # Try to open and convert the image
        with open(team_images[suit], "rb") as img_file:
            img_data = img_file.read()
            # Use base64 encoding to embed the image directly in HTML
            encoded = base64.b64encode(img_data).decode()
            return f'<img src="data:image/avif;base64,{encoded}" style="max-width:100px; max-height:40px;" alt="{st.session_state.horse_names.get(suit, suit)}">'
    except Exception as e:
        # If there's an error, fallback to displaying the team name as text
        print(f"Error loading image for {suit}: {e}")
        return st.session_state.horse_names.get(suit, suit)

# Main title
st.title("Drinking Card Game Visualizer")

# Game setup section
if not st.session_state.game_initialized:
    st.header("Game Setup")
    
    # Racecar naming
    st.subheader("Name Your Racecars (Card Suits)")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.session_state.horse_names['hearts'] = st.text_input("Hearts", value="McLaren")
    with col2:
        st.session_state.horse_names['diamonds'] = st.text_input("Diamonds", value="Mercedes")
    with col3:
        st.session_state.horse_names['clubs'] = st.text_input("Clubs", value="Ferrari")
    with col4:
        st.session_state.horse_names['spades'] = st.text_input("Spades", value="Red Bull")
    
    # Player management
    st.subheader("Add Players")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        new_player_name = st.text_input("Player Name", key="new_player")
    with col2:
        suit_options = [
            st.session_state.horse_names['hearts'],
            st.session_state.horse_names['diamonds'],
            st.session_state.horse_names['clubs'],
            st.session_state.horse_names['spades']
        ]
        new_player_horse = st.selectbox("Bet on Racecar", options=suit_options, key="new_player_horse")
    with col3:
        new_player_stakes = st.number_input("Stakes (Slurker)", min_value=1, value=1, step=1, key="new_player_stakes")
    
    if st.button("Add Player"):
        inverse_horse_names = {v: k for k, v in st.session_state.horse_names.items()}
        horse_key = inverse_horse_names[new_player_horse]
        
        st.session_state.players.append({
            "name": new_player_name,
            "horse": horse_key,
            "stakes": new_player_stakes
        })
        st.session_state.total_stakes += new_player_stakes
        st.rerun()
    
    # Display current players
    if st.session_state.players:
        st.subheader("Current Players")
        
        # Create an editable DataFrame-like interface
        for idx, player in enumerate(st.session_state.players):
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.write(player["name"])
            with col2:
                # Make racecar editable with dropdown
                suit_options = [
                    st.session_state.horse_names['hearts'],
                    st.session_state.horse_names['diamonds'],
                    st.session_state.horse_names['clubs'],
                    st.session_state.horse_names['spades']
                ]
                
                current_horse = st.session_state.horse_names[player["horse"]]
                new_racecar = st.selectbox(
                    "Racecar", 
                    options=suit_options, 
                    index=suit_options.index(current_horse), 
                    key=f"edit_racecar_setup_{idx}"
                )
                
                # Update the player's horse if changed
                inverse_horse_names = {v: k for k, v in st.session_state.horse_names.items()}
                new_horse_key = inverse_horse_names[new_racecar]
                if new_horse_key != player["horse"]:
                    player["horse"] = new_horse_key
            with col3:
                # Allow editing stakes
                new_stakes = st.number_input(
                    "Stakes",
                    min_value=1,
                    value=player["stakes"],
                    key=f"edit_stakes_{idx}"
                )
                # Update total stakes if changed
                if new_stakes != player["stakes"]:
                    st.session_state.total_stakes -= player["stakes"]
                    st.session_state.total_stakes += new_stakes
                    player["stakes"] = new_stakes
            with col4:
                # Button to remove this specific player
                if st.button("Remove", key=f"remove_{idx}"):
                    st.session_state.total_stakes -= player["stakes"]
                    st.session_state.players.pop(idx)
                    st.rerun()
        
        # Display total stakes
        st.write(f"Total stakes: {st.session_state.total_stakes} slurker")
    
    # Start the game
    if st.session_state.players and st.button("Start Game"):
        st.session_state.game_state = initialize_game()
        st.session_state.game_initialized = True
        # Every player drinks their stakes before the game starts
        st.info(f"All players drink their stakes ({st.session_state.total_stakes} slurker total) before starting!")
        st.rerun()

# Game play section
else:
    # Display game board
    st.header("Game Board")
    
    # Make sure game_state is not None before accessing its properties
    if st.session_state.game_state is None:
        st.error("Game state is not initialized properly. Please restart the game.")
        if st.button("Return to Setup"):
            st.session_state.game_initialized = False
            st.rerun()
    else:
        # Track positions
        positions = st.session_state.game_state["positions"]
        checkpoints = st.session_state.game_state["checkpoints"]
        flipped_checkpoints = st.session_state.game_state["flipped_checkpoints"]
        checkpoint_cards = st.session_state.game_state["checkpoint_cards"]
    
    # Initialize animations
    if "last_animation_time" not in st.session_state:
        st.session_state.last_animation_time = time.time()
    
    # Check if the game state is properly initialized before rendering the rest
    if st.session_state.game_state is None:
        st.error("Cannot display game board: game state is not initialized.")
    else:
        # Display current position of all racecars
        st.subheader("Racecar Positions")
        
        # Create a visual representation of the track
        track_length = 14  # 0-13 positions (start to finish)
        cols = st.columns(track_length)
        
        # Header for each position
        for i, col in enumerate(cols):
            if i == 0:
                col.markdown("Start")
            elif i == track_length - 1:
                col.markdown("Finish")
            elif i >= 1 and i <= 12:  # Checkpoints 1-12
                # Show checkpoint without text
                if i in flipped_checkpoints:
                    if i in checkpoint_cards:
                        # Get the original card name
                        checkpoint_card = checkpoint_cards[i]
                        # Create custom suit names map for card display
                        custom_suit_names = {
                            'hearts': st.session_state.horse_names['hearts'],
                            'diamonds': st.session_state.horse_names['diamonds'],
                            'clubs': st.session_state.horse_names['clubs'],
                            'spades': st.session_state.horse_names['spades']
                        }
                        # Display the card image with checkpoint ID for animation
                        card_image = get_card_image(checkpoint_card, custom_suit_names)
                        
                        # Style the cards at checkpoints 4, 8, and 12 to be horizontal
                        rotation_style = ""
                        if i in [4, 8, 12]:
                            rotation_style = 'style="transform: rotate(90deg);"'
                            
                        card_html = f'<div id="checkpoint-{i}" class="checkpoint-card" {rotation_style}>{card_image}</div>'
                        col.markdown(card_html, unsafe_allow_html=True)
                else:
                    # Display card back with racecar design for checkpoints not yet flipped
                    card_back = get_card_back()
                    
                    # Style the card backs at checkpoints 4, 8, and 12 to also be horizontal
                    rotation_style = ""
                    if i in [4, 8, 12]:
                        rotation_style = 'style="transform: rotate(90deg);"'
                        
                    card_html = f'<div id="checkpoint-{i}" class="checkpoint-card" {rotation_style}>{card_back}</div>'
                    col.markdown(card_html, unsafe_allow_html=True)
            else:
                col.markdown(f"Pos {i}")
        
        # Display horse positions
        for suit, position in positions.items():
            horse_row = [""] * track_length
            
            # Add animation ID for the horse to enable movement animations
            if position < track_length:
                # Get team logo image for the racecar
                racecar_image = get_racecar_image(suit)
                horse_row[position] = f'<div id="horse-{suit}" class="horse">{racecar_image}</div>'
            
            # Display the row
            horse_cols = st.columns(track_length)
            for i, col in enumerate(horse_cols):
                if horse_row[i]:
                    col.markdown(horse_row[i], unsafe_allow_html=True)
                else:
                    col.markdown("")
    
    # Display game status and last drawn card
    st.subheader("Game Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.drawn_cards:
            last_card = st.session_state.drawn_cards[-1]
            # Format the card text with custom suit names
            card_parts = last_card.split(" of ")
            if len(card_parts) == 2:
                value, suit = card_parts
                suit_lower = suit.lower()
                if suit_lower in st.session_state.horse_names:
                    custom_suit_name = st.session_state.horse_names[suit_lower]
                    formatted_card = f"{value} of {custom_suit_name}"
                    st.write(f"Last card drawn: {formatted_card}")
                else:
                    st.write(f"Last card drawn: {last_card}")
            else:
                st.write(f"Last card drawn: {last_card}")
                
            # Display the card image with animation
            # Create custom suit names map for card display
            custom_suit_names = {
                'hearts': st.session_state.horse_names['hearts'],
                'diamonds': st.session_state.horse_names['diamonds'],
                'clubs': st.session_state.horse_names['clubs'],
                'spades': st.session_state.horse_names['spades']
            }
            
            card_image = get_card_image(last_card, custom_suit_names)
            card_parts = last_card.split(" of ")
            if len(card_parts) == 2:
                suit = card_parts[1].lower()
                # Wrap the card in animation
                animated_card = animate_card_draw(card_image, suit)
                st.markdown(animated_card, unsafe_allow_html=True)
            else:
                st.markdown(card_image, unsafe_allow_html=True)
        else:
            st.write("No cards drawn yet")
    
    with col2:
        if st.session_state.winner:
            winner_horse = st.session_state.winner
            winning_players = [p for p in st.session_state.players if p["horse"] == winner_horse]
            
            st.success(f"**{st.session_state.horse_names[winner_horse]}** has won the race!")
            
            if winning_players:
                winners_text = ", ".join([p["name"] for p in winning_players])
                st.write(f"Winning player(s): {winners_text}")
                
                # Show how many drinks each winning player can distribute (double their own stake)
                for player in winning_players:
                    st.write(f"{player['name']} can distribute {player['stakes'] * 2} slurker to other players!")
            else:
                st.write("No players bet on the winning racecar.")
            
            if st.button("Reset Game"):
                # Reset the game but keep players
                reset_game(keep_players=True)
                st.rerun()
        else:
            # Draw card button
            if st.button("Draw Next Card"):
                card = draw_card(st.session_state.game_state)
                st.session_state.drawn_cards.append(card)
                
                # Get suit of drawn card
                card_parts = card.split(" of ")
                suit = card_parts[1].lower()
                
                # Move the corresponding racecar
                move_horse(st.session_state.game_state, suit)
                
                # Check if a checkpoint was reached
                check_checkpoint(st.session_state.game_state)
                
                # Check for a winner
                winner = check_winner(st.session_state.game_state)
                if winner:
                    st.session_state.winner = winner
                
                st.rerun()

    # Display player information
    st.subheader("Players")
    
    # Using columns for a custom table display with images
    if st.session_state.players:
        if st.session_state.game_initialized:
            # During gameplay, just display the information
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            # Header row
            with col1:
                st.markdown("**Name**")
            with col2:
                st.markdown("**Racecar**")
            with col3:
                st.markdown("**Stakes**")
            with col4:
                st.markdown("**Position**")
                
            # Create divider
            st.markdown("---")
            
            # Player rows
            for player in st.session_state.players:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(player["name"])
                with col2:
                    # Display team logo image
                    team_image = get_racecar_image(player["horse"])
                    team_name = st.session_state.horse_names[player["horse"]]
                    st.markdown(f"{team_image} {team_name}", unsafe_allow_html=True)
                with col3:
                    st.write(player["stakes"])
                with col4:
                    # Display position if game is active
                    if st.session_state.game_state is not None and "positions" in st.session_state.game_state:
                        st.write(st.session_state.game_state["positions"][player["horse"]])
                    else:
                        st.write("0")
        else:
            # During setup, allow editing racecars and stakes
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            # Header row
            with col1:
                st.markdown("**Name**")
            with col2:
                st.markdown("**Racecar**")
            with col3:
                st.markdown("**Stakes**")
            with col4:
                st.markdown("**Remove**")
                
            # Create divider
            st.markdown("---")
            
            # Player rows with editable fields
            for idx, player in enumerate(st.session_state.players):
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(player["name"])
                with col2:
                    # Make racecar editable with dropdown
                    suit_options = [
                        st.session_state.horse_names['hearts'],
                        st.session_state.horse_names['diamonds'],
                        st.session_state.horse_names['clubs'],
                        st.session_state.horse_names['spades']
                    ]
                    
                    current_horse = st.session_state.horse_names[player["horse"]]
                    new_racecar = st.selectbox(
                        "Racecar", 
                        options=suit_options, 
                        index=suit_options.index(current_horse), 
                        key=f"edit_racecar_{idx}"
                    )
                    
                    # Update the player's horse if changed
                    inverse_horse_names = {v: k for k, v in st.session_state.horse_names.items()}
                    new_horse_key = inverse_horse_names[new_racecar]
                    if new_horse_key != player["horse"]:
                        player["horse"] = new_horse_key
                        
                with col3:
                    # Allow editing stakes
                    new_stakes = st.number_input(
                        "Stakes",
                        min_value=1,
                        value=player["stakes"],
                        key=f"edit_stakes_{idx}"
                    )
                    # Update total stakes if changed
                    if new_stakes != player["stakes"]:
                        st.session_state.total_stakes -= player["stakes"]
                        st.session_state.total_stakes += new_stakes
                        player["stakes"] = new_stakes
                with col4:
                    # Button to remove this specific player
                    if st.button("Remove", key=f"remove_{idx}"):
                        st.session_state.total_stakes -= player["stakes"]
                        st.session_state.players.pop(idx)
                        st.rerun()
    
    # Option to reset game
    if st.button("Reset to Setup"):
        # Reset the game but keep players
        reset_game(keep_players=True)
        st.rerun()

# Display game rules in an expandable section
with st.expander("Game Rules"):
    st.markdown("""
    ### Game Rules
    
    1. **Setup**: 
       - Place all aces on the table in a horizontal line, face up.
       - Setup 12 checkpoints along the track, with different effects.
       
    2. **Checkpoint Types**:
       - Horizontal checkpoints: Move the matching racecar forward one position
       - Vertical checkpoints: Move the matching racecar back one position
       - Checkpoints 4, 8, and 12 are vertical (shown sideways), all others are horizontal
       
    3. **Betting**:
       - Each card suit (hearts, diamonds, clubs, spades) is a "racecar".
       - Players bet "slurker" (drinks) on their chosen racecar.
       - Players must drink their stakes before the game starts.
       
    4. **Gameplay**:
       - Draw cards one at a time from the deck.
       - The suit of the drawn card determines which racecar moves forward.
       - When all racecars pass or reach a checkpoint, it's flipped.
       - A card is drawn to determine which racecar is affected by the checkpoint.
       - The affected racecar moves forward one position or back one position, depending on the checkpoint type.
       
    5. **Winning**:
       - The first racecar to cross the finish line wins.
       - Players who bet on the winning racecar can distribute double their own stakes to other players.
    """)

# Apply any pending animations
if st.session_state.game_initialized and st.session_state.game_state is not None:
    if "animation_events" in st.session_state.game_state:
        # Process animation events
        animation_events = st.session_state.game_state["animation_events"]
        
        # Only apply animations for recent events (not already processed)
        animations_processed = st.session_state.game_state.get("animations_processed", False)
        if not animations_processed and animation_events:
            apply_animations()
            st.session_state.game_state["animations_processed"] = True
