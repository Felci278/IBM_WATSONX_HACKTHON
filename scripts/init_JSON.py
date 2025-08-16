import os, json

DB_PATH = "data/wardrobe.json"
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump([], f, indent=4)
    print("✅ Created empty wardrobe.json")
else:
    print("ℹ️ wardrobe.json already exists")
