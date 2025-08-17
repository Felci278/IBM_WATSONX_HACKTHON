import json
import os
from typing import List, Dict

DB_PATH = "backend/wardrobe.json"

def _load_db() -> List[Dict]:
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_db(items: List[Dict]):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

def add_item(item: Dict) -> Dict:
    items = _load_db()
    item_id = len(items) + 1
    item["id"] = item_id
    items.append(item)
    _save_db(items)
    return item

def list_items(action: str = None) -> List[Dict]:
    items = _load_db()
    if action:
        # Filter by action if present in metadata
        return [item for item in items if item.get("action") == action]
    return items

def get_item(item_id: int) -> Dict:
    items = _load_db()
    for item in items:
        if item.get("id") == item_id:
            return item
    raise ValueError(f"Item with ID {item_id} not found.")

def delete_item(item_id: int) -> bool:
    items = _load_db()
    for i, item in enumerate(items):
        if item.get("id") == item_id:
            del items[i]
            _save_db(items)
            return True
    raise ValueError(f"Item with ID {item_id} not found.")