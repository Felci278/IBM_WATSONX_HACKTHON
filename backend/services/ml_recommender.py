# app/services/ml_recommender.py

from typing import Optional, List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import numpy as np

# -----------------------------
# Corpus for upcycle ideas
# -----------------------------
upcycle_data = {
    "t-shirt": [
        "Turn old t-shirts into reusable tote bags",
        "Cut into cleaning cloths",
        "Print designs and resell as upcycled fashion",
    ],
    "jeans": [
        "Make denim shorts",
        "Patchwork into a quilt",
        "Transform into a backpack",
    ],
    "jacket": [
        "Convert into a vest",
        "Add patches for streetwear look",
        "Reuse fabric for handbags",
    ],
    "dress": [
        "Convert into a skirt",
        "Turn into pillow covers",
        "Use fabric for patchwork art",
    ],
}

# Flatten dataset for ML vectorization
all_items, all_ideas = [], []
for k, v in upcycle_data.items():
    all_items.extend([k] * len(v))
    all_ideas.extend(v)

# Vectorize ideas
vectorizer = TfidfVectorizer(stop_words="english")
idea_vectors = vectorizer.fit_transform(all_ideas)

# NearestNeighbors model for idea retrieval
idea_model = NearestNeighbors(n_neighbors=3, metric="cosine").fit(idea_vectors)


# -----------------------------
# Upcycling ideas (ML-driven)
# -----------------------------
def get_upcycle_ideas(item_type: Optional[str]) -> List[str]:
    """
    Return upcycling ideas for a given clothing type using TF-IDF + NearestNeighbors.
    If item_type is None, returns top general ideas.
    """
    if not item_type:
        return ["Donate to charity", "Transform fabric into accessories", "DIY home decor projects"]

    query_vec = vectorizer.transform([item_type])
    _, idxs = idea_model.kneighbors(query_vec)
    suggestions = [all_ideas[i] for i in idxs[0]]
    return suggestions


# -----------------------------
# Styling recommendation (ML-driven)
# -----------------------------
def get_styling_recommendation(item: dict, wardrobe: list, event_details: Optional[str]) -> Dict:
    """
    Recommend styling based on wardrobe items and event context using similarity search.
    - item: dict {item_name, condition}
    - wardrobe: list of items [{item_name, condition, ...}]
    - event_details: optional event description
    """
    if not wardrobe:
        return {
            "base_item": item.get("item_name", "clothing"),
            "event": event_details or "casual",
            "suggested_matches": [],
            "style_tip": "No wardrobe data available",
        }

    base_item = item.get("item_name", "clothing")
    event = (event_details or "casual").lower()

    # Build corpus from wardrobe descriptions
    wardrobe_texts = [w["item_name"] + " " + w.get("condition", "") for w in wardrobe]
    X = vectorizer.fit_transform(wardrobe_texts + [base_item])
    
    # Fit nearest neighbors on wardrobe
    nn = NearestNeighbors(n_neighbors=min(3, len(wardrobe)), metric="cosine")
    nn.fit(X[:-1])  # exclude base_item

    # Find similar items to base_item
    _, idxs = nn.kneighbors(X[-1])
    suggested_matches = [wardrobe[i]["item_name"] for i in idxs[0]]

    # Style tip generation (basic rule-based for now)
    if "meeting" in event or "work" in event:
        style_tip = f"Pair {base_item} with formal items ({', '.join(suggested_matches)}) for {event}."
    elif "party" in event or "wedding" in event:
        style_tip = f"Combine {base_item} with festive matches ({', '.join(suggested_matches)}) for {event}."
    else:
        style_tip = f"Style {base_item} casually with {', '.join(suggested_matches)} for a relaxed {event} look."

    return {
        "base_item": base_item,
        "event": event,
        "suggested_matches": suggested_matches,
        "style_tip": style_tip,
    }
