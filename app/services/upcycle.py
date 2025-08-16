"""
Service to suggest upcycling ideas for wardrobe items.
"""

from typing import Dict, List


# Simple ruleset — can be expanded or loaded from a JSON file
UPCYCLE_RULES = {
    "tshirt": ["Turn into cleaning rags", "Cut into a tote bag", "Use as pillow stuffing"],
    "jeans": ["Convert into shorts", "Patchwork tote bag", "Denim coasters"],
    "shirt": ["Make an apron", "Reuse buttons for crafts"],
    "dress": ["Turn into a skirt", "Make doll clothes"],
    "sweater": ["Make hand warmers", "Pet bed stuffing"],
}


def suggest_upcycle(item_type: str) -> List[str]:
    """
    Suggest upcycling ideas based on clothing type.
    """
    item_type = item_type.lower()
    return UPCYCLE_RULES.get(item_type, ["No suggestions available. Try a donation or recycle center."])


def suggest_generic() -> List[str]:
    """
    Provide general sustainable ideas.
    """
    return [
        "Organize a clothing swap with friends.",
        "Donate clothes in good condition.",
        "Use scraps for DIY crafts."
    ]
