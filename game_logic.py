import random

def initialize_game():
    """Initialize the game state with default positions and checkpoints."""
    game_state = {
        # Track positions of each "horse" (card suit)
        "positions": {
            "hearts": 0,   # Start at position 0
            "diamonds": 0,
            "clubs": 0,
            "spades": 0
        },
        # Define checkpoints and their types
        "checkpoints": {
            1: "horizontal",   # Move back one position
            2: "horizontal",   # Move back one position  
            3: "horizontal",   # Move back one position
            4: "vertical",     # Move back to start
            5: "horizontal",   # Move back one position
            6: "horizontal",   # Move back one position
            7: "horizontal",   # Move back one position
            8: "vertical",     # Move back to start
            9: "horizontal",   # Move back one position
            10: "horizontal",  # Move back one position
            11: "horizontal",  # Move back one position
            12: "vertical"     # Move back to start
        },
        # Track which checkpoints have been flipped and which cards they hold
        "flipped_checkpoints": set(),
        "checkpoint_cards": {},
        # The deck of cards (excluding aces which are used for the track)
        "deck": create_deck(),
        # Track animation events
        "animation_events": [],
        # Track whether animations have been processed
        "animations_processed": False
    }
    
    return game_state

def create_deck():
    """Create a deck of cards without aces."""
    suits = ["hearts", "diamonds", "clubs", "spades"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"]
    
    deck = [f"{value} of {suit}" for suit in suits for value in values]
    random.shuffle(deck)
    
    return deck

def draw_card(game_state):
    """Draw a card from the deck."""
    # If deck is empty, create a new shuffled deck
    if not game_state["deck"]:
        game_state["deck"] = create_deck()
    
    card = game_state["deck"].pop()
    
    # Track card draw animation
    if "animation_events" not in game_state:
        game_state["animation_events"] = []
    
    # Get suit of the drawn card
    card_parts = card.split(" of ")
    if len(card_parts) == 2:
        suit = card_parts[1].lower()
        
        game_state["animation_events"].append({
            "event": "draw_card",
            "card": card,
            "suit": suit
        })
    
    return card

def move_horse(game_state, suit):
    """Move a horse forward one position."""
    # Save the old position for animation tracking
    old_position = game_state["positions"][suit]
    
    # Only move forward if the horse hasn't finished
    if game_state["positions"][suit] < 13:  # Finish line is at position 13
        game_state["positions"][suit] += 1
        
    # Track this movement for animations
    if "animation_events" not in game_state:
        game_state["animation_events"] = []
    
    game_state["animation_events"].append({
        "event": "move",
        "suit": suit,
        "direction": "forward",
        "from_position": old_position,
        "to_position": game_state["positions"][suit]
    })

def check_checkpoint(game_state):
    """Check if any checkpoints should be flipped and apply their effects."""
    positions = game_state["positions"]
    checkpoints = game_state["checkpoints"]
    flipped_checkpoints = game_state["flipped_checkpoints"]
    checkpoint_cards = game_state["checkpoint_cards"]
    
    # Initialize animation events if needed
    if "animation_events" not in game_state:
        game_state["animation_events"] = []
    
    # Check each checkpoint
    for checkpoint_pos, checkpoint_type in checkpoints.items():
        # If checkpoint is not flipped yet
        if checkpoint_pos not in flipped_checkpoints:
            # Check if all horses have passed or are at the checkpoint
            all_passed_or_at = all(pos >= checkpoint_pos for pos in positions.values())
            
            if all_passed_or_at:
                # Flip the checkpoint and draw a card for it
                flipped_checkpoints.add(checkpoint_pos)
                
                # Track checkpoint flip animation
                game_state["animation_events"].append({
                    "event": "flip_checkpoint",
                    "checkpoint_position": checkpoint_pos
                })
                
                # Draw a card to determine which horse is affected
                checkpoint_card = draw_card(game_state)
                checkpoint_cards[checkpoint_pos] = checkpoint_card
                
                # Get suit of drawn card
                card_parts = checkpoint_card.split(" of ")
                affected_suit = card_parts[1].lower()
                
                # Track card reveal animation
                game_state["animation_events"].append({
                    "event": "reveal_card",
                    "checkpoint_position": checkpoint_pos,
                    "card": checkpoint_card
                })
                
                # Save the old position for animation tracking
                old_position = positions[affected_suit]
                
                # Apply checkpoint effect
                if checkpoint_type == "horizontal":
                    # Move forward one position if not at finish
                    if positions[affected_suit] < 13:  # 13 is the finish line
                        positions[affected_suit] += 1
                        
                        # Track forward movement animation
                        game_state["animation_events"].append({
                            "event": "move",
                            "suit": affected_suit,
                            "direction": "forward",
                            "from_position": old_position,
                            "to_position": positions[affected_suit]
                        })
                elif checkpoint_type == "vertical":
                    # Move back one checkpoint (instead of back to start)
                    # Calculate the new position (one checkpoint back)
                    new_position = max(0, positions[affected_suit] - 1)
                    positions[affected_suit] = new_position
                    
                    # Track backward movement animation
                    game_state["animation_events"].append({
                        "event": "move",
                        "suit": affected_suit,
                        "direction": "backward",
                        "from_position": old_position,
                        "to_position": new_position
                    })

def check_winner(game_state):
    """Check if any horse has reached the finish line."""
    positions = game_state["positions"]
    
    for suit, position in positions.items():
        if position >= 13:  # Position 13 is the finish line
            return suit
    
    return None

def reset_game(keep_players=True):
    """
    Reset the game state.
    
    Args:
        keep_players (bool): Whether to keep the player list for the next game
    """
    if 'game_initialized' in st.session_state:
        st.session_state.game_initialized = False
    
    if 'game_state' in st.session_state:
        st.session_state.game_state = None
    
    if 'drawn_cards' in st.session_state:
        st.session_state.drawn_cards = []
    
    if 'winner' in st.session_state:
        st.session_state.winner = None
    
    # Keep player information if requested
    if not keep_players:
        if 'players' in st.session_state:
            st.session_state.players = []
        
        if 'total_stakes' in st.session_state:
            st.session_state.total_stakes = 0
    else:
        # Ensure total_stakes is calculated correctly
        if 'players' in st.session_state and 'total_stakes' in st.session_state:
            # Recalculate total stakes based on current players
            total = sum(player['stakes'] for player in st.session_state.players)
            st.session_state.total_stakes = total

# This import is needed for the reset_game function
# Placed at the bottom to avoid circular imports
try:
    import streamlit as st
except ImportError:
    # For handling LSP checks where streamlit might not be available
    pass
