import time
try:
    import streamlit as st
except ImportError:
    # For handling LSP checks where streamlit might not be available
    pass

def animation_css():
    """
    Returns the CSS styles needed for animations.
    """
    return """
    <style>
        @keyframes card-slide {
            0% {
                transform: translateY(-100px) rotateY(180deg);
                opacity: 0;
            }
            100% {
                transform: translateY(0) rotateY(0deg);
                opacity: 1;
            }
        }
        
        @keyframes horse-move {
            0% {
                transform: translateX(0);
            }
            50% {
                transform: translateX(20px);
            }
            100% {
                transform: translateX(0);
            }
        }
        
        @keyframes horse-move-back {
            0% {
                transform: translateX(0);
            }
            50% {
                transform: translateX(-20px);
            }
            100% {
                transform: translateX(0);
            }
        }
        
        @keyframes horse-move-start {
            0% {
                transform: translateX(0);
            }
            100% {
                transform: translateX(-100%);
            }
        }
        
        @keyframes checkpoint-flip {
            0% {
                transform: rotateY(0deg);
            }
            50% {
                transform: rotateY(90deg);
            }
            100% {
                transform: rotateY(0deg);
            }
        }
        
        .card-animation {
            animation: card-slide 0.5s ease-out forwards;
        }
        
        .horse-forward {
            animation: horse-move 0.6s ease-in-out;
        }
        
        .horse-backward {
            animation: horse-move-back 0.6s ease-in-out;
        }
        
        .horse-to-start {
            animation: horse-move-start 1s ease-in-out;
        }
        
        .checkpoint-flip {
            animation: checkpoint-flip 0.8s ease-in-out;
        }
    </style>
    """

def animate_card_draw(card_html, suit, last_action="draw"):
    """
    Wraps a card in animation classes and tracks the last action for sequential animations.
    
    Args:
        card_html (str): HTML representation of the card
        suit (str): The suit of the card (hearts, diamonds, etc.)
        last_action (str): The last action that occurred (for tracking animation sequence)
    
    Returns:
        str: Animated card HTML
    """
    animation_class = "card-animation"
    
    # Store the last action to enable sequential animations
    if "animation_sequence" not in st.session_state:
        st.session_state.animation_sequence = []
    
    # Add this action to the sequence
    st.session_state.animation_sequence.append({
        "action": last_action,
        "suit": suit,
        "timestamp": time.time()
    })
    
    # Wrap the card with the animation div
    return f"""
    <div class="{animation_class}" id="animated-card-{suit}">
        {card_html}
    </div>
    """

def animate_horse_movement(direction="forward", suit=None):
    """
    Creates animation HTML for horse movement.
    
    Args:
        direction (str): Direction of movement ('forward', 'backward', or 'to_start')
        suit (str): The suit of the horse (hearts, diamonds, etc.)
    
    Returns:
        str: JavaScript to trigger animation
    """
    animation_class = "horse-forward"
    if direction == "backward":
        animation_class = "horse-backward"
    elif direction == "to_start":
        animation_class = "horse-to-start"
    
    if "animation_sequence" not in st.session_state:
        st.session_state.animation_sequence = []
    
    # Add this action to the sequence
    st.session_state.animation_sequence.append({
        "action": f"move_{direction}",
        "suit": suit,
        "timestamp": time.time()
    })
    
    # Create JavaScript to add and remove the animation class
    return f"""
    <script>
        // Get the horse element by ID (needs to be specified in the HTML)
        var horseElement = document.getElementById("horse-{suit}");
        if (horseElement) {{
            // Add animation class
            horseElement.classList.add("{animation_class}");
            
            // Remove animation class after animation completes
            setTimeout(function() {{
                horseElement.classList.remove("{animation_class}");
            }}, 1000);
        }}
    </script>
    """

def animate_checkpoint_flip(checkpoint_position):
    """
    Creates animation HTML for checkpoint card flip.
    
    Args:
        checkpoint_position (int): Position of the checkpoint
    
    Returns:
        str: JavaScript to trigger animation
    """
    if "animation_sequence" not in st.session_state:
        st.session_state.animation_sequence = []
    
    # Add this action to the sequence
    st.session_state.animation_sequence.append({
        "action": "flip_checkpoint",
        "checkpoint": checkpoint_position,
        "timestamp": time.time()
    })
    
    # Create JavaScript to add and remove the animation class
    return f"""
    <script>
        // Get the checkpoint element by ID (needs to be specified in the HTML)
        var checkpointElement = document.getElementById("checkpoint-{checkpoint_position}");
        if (checkpointElement) {{
            // Add animation class
            checkpointElement.classList.add("checkpoint-flip");
            
            // Remove animation class after animation completes
            setTimeout(function() {{
                checkpointElement.classList.remove("checkpoint-flip");
            }}, 800);
        }}
    </script>
    """

def apply_animations():
    """
    Applies all animations in the sequence at the end of the page.
    """
    # Add the CSS once
    st.markdown(animation_css(), unsafe_allow_html=True)
    
    # Apply animations from the game state if initialized and has animation events
    if not hasattr(st, "session_state"):
        return
        
    if not hasattr(st.session_state, "game_initialized") or not st.session_state.game_initialized:
        return
        
    if not hasattr(st.session_state, "game_state") or st.session_state.game_state is None:
        return
        
    if "animation_events" not in st.session_state.game_state:
        return
    
    animation_events = st.session_state.game_state["animation_events"]
    
    # Process each animation event
    for event in animation_events:
        if not isinstance(event, dict) or "event" not in event:
            continue
            
        event_type = event["event"]
        
        if event_type == "draw_card":
            # Card drawing animation is applied directly to the card during rendering
            pass
        elif event_type == "move" and "suit" in event and "direction" in event:
            suit = event["suit"]
            direction = event["direction"]
            st.markdown(animate_horse_movement(direction, suit), unsafe_allow_html=True)
        elif event_type == "flip_checkpoint" and "checkpoint_position" in event:
            cp_pos = event["checkpoint_position"]
            st.markdown(animate_checkpoint_flip(cp_pos), unsafe_allow_html=True)
        elif event_type == "reveal_card":
            # Card reveal animations are handled through checkpoint flips
            pass
            
    # Clear animation events after processing
    st.session_state.game_state["animation_events"] = []