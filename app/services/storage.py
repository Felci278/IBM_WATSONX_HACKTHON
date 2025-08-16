import json
import os
from jsonschema import validate, ValidationError

DB_PATH = "data/wardrobe.json"
SCHEMA_PATH = "app/models/wardrobe_schema.json"

# Load schema once
if os.path.exists(SCHEMA_PATH):
    with open(SCHEMA_PATH, "r") as f:
        SCHEMA = json.load(f)
else:
    SCHEMA = None


def _read_db():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        return json.load(f)


def _write_db(data):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)


def _validate_item(item):
    if SCHEMA:
        try:
            validate(instance=item, schema=SCHEMA)
        except ValidationError as e:
            raise ValueError(f"Invalid item: {e.message}")


def list_items():
    return _read_db()


def add_item(item_data):
    db = _read_db()
    next_id = 1 if not db else max(item.get("id", 0) for item in db) + 1
    item_data["id"] = next_id
    _validate_item(item_data)
    db.append(item_data)
    _write_db(db)
    return item_data


def get_item(item_id: int):
    db = _read_db()
    return next((item for item in db if item.get("id") == item_id), None)


def update_item(item_id: int, new_data: dict):
    """Update item fields"""
    db = _read_db()
    for i, item in enumerate(db):
        if item.get("id") == item_id:
            db[i].update(new_data)
            _validate_item(db[i])
            _write_db(db)
            return db[i]
    return None


def delete_item(item_id: int):
    db = _read_db()
    new_db = [item for item in db if item.get("id") != item_id]
    if len(new_db) == len(db):
        return False
    _write_db(new_db)
    return True
