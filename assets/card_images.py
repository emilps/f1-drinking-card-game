import os
import base64
from PIL import Image
import io

def get_card_image(card_name, custom_suit_names=None):
    """
    Returns an SVG representation of a playing card.
    
    Args:
        card_name (str): Card name in format "value of suit" (e.g., "jack of hearts")
        custom_suit_names (dict, optional): Dictionary mapping suit names to custom names
        
    Returns:
        str: SVG image of the card as HTML
    """
    parts = card_name.split(" of ")
    if len(parts) != 2:
        return "<p>Invalid card name</p>"
    
    value, suit = parts
    suit_lower = suit.lower()
    
    # Map card value to display text
    value_map = {
        "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", 
        "8": "8", "9": "9", "10": "10", "jack": "J", "queen": "Q", 
        "king": "K", "ace": "A"
    }
    
    # Map suit to symbol and color
    suit_map = {
        "hearts": ("♥", "red"),
        "diamonds": ("♦", "red"),
        "clubs": ("♣", "black"),
        "spades": ("♠", "black")
    }
    
    display_value = value_map.get(value.lower(), value)
    suit_symbol, color = suit_map.get(suit_lower, ("?", "black"))
    
    # Create an SVG card
    svg = f"""
    <svg width="80" height="120" viewBox="0 0 80 120" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="80" height="120" rx="10" ry="10" fill="white" stroke="black" stroke-width="1"/>
        <text x="10" y="25" font-family="Arial" font-size="20" fill="{color}">{display_value}</text>
        <text x="10" y="50" font-family="Arial" font-size="30" fill="{color}">{suit_symbol}</text>
        <text x="40" y="75" font-family="Arial" font-size="40" text-anchor="middle" fill="{color}">{suit_symbol}</text>
        <text x="70" y="115" font-family="Arial" font-size="20" text-anchor="end" fill="{color}">{display_value}</text>
    </svg>
    """
    
    return svg

def get_card_back():
    """
    Returns an HTML img element with the McLaren F1 image as a base64-encoded source.
    
    Returns:
        str: HTML img element with the McLaren F1 image
    """
    # Path to the McLaren F1 image
    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             'attached_assets', 'aifaceswap-a73a29c5f276f2ab1862c31fb0f3cd7d.jpg')
    
    # Open and resize the image
    try:
        with Image.open(image_path) as img:
            # Resize to appropriate card dimensions while maintaining aspect ratio
            img = img.resize((80, 80), Image.Resampling.LANCZOS)
            
            # Create a new image with card proportions (80x120)
            card_img = Image.new('RGB', (80, 120), color=(255, 128, 0))  # Orange background
            
            # Calculate position to center the F1 image on the card
            position = ((80 - img.width) // 2, (120 - img.height) // 2)
            
            # Paste the resized F1 image onto the card
            card_img.paste(img, position)
            
            # Convert the image to base64 encoded string
            buffered = io.BytesIO()
            card_img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Return the image as an HTML img element
            return f'<img src="data:image/jpeg;base64,{img_str}" width="80" height="120" style="border-radius: 10px;">'
    except Exception as e:
        # Fallback if there's an error loading the image
        print(f"Error loading card back image: {e}")
        return """
        <svg width="80" height="120" viewBox="0 0 80 120" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="0" width="80" height="120" rx="10" ry="10" fill="#FF8000" stroke="black" stroke-width="1"/>
            <text x="40" y="60" font-family="Arial" font-size="10" text-anchor="middle" fill="#000000">McLaren F1</text>
        </svg>
        """
