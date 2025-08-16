from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services import storage, cv_inference
import os, shutil

router = APIRouter()
UPLOAD_DIR = "data/images"

# If a file accidentally exists, remove it and make a folder
if os.path.isfile(UPLOAD_DIR):
    os.remove(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)



@router.get("/")
async def get_items():
    """List all items in the wardrobe"""
    items = storage.list_items()
    return {"status": "ok", "count": len(items), "items": items}


@router.post("/ingest")
async def ingest_image(file: UploadFile = File(...)):
    """Upload an image, run CV model, store metadata + path in DB"""
    path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        # Save file locally
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run CV inference → metadata
        metadata = cv_inference.predict(path)

        # Attach image path
        metadata["image_path"] = path

        # Add to DB (with auto-ID + validation)
        item = storage.add_item(metadata)

        return {"status": "added", "item": item}

    except Exception as e:
        if os.path.exists(path):  # clean up failed file save
            os.remove(path)
        raise HTTPException(status_code=500, detail=f"Ingest failed: {str(e)}")


@router.get("/{item_id}")
async def get_item(item_id: int):
    """Fetch single wardrobe item by ID"""
    item = storage.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "ok", "item": item}


@router.put("/{item_id}")
async def update_item(item_id: int, updates: dict):
    """
    Update wardrobe item metadata.
    Example: {"status": "donated"} or {"color": "red"}.
    """
    updated = storage.update_item(item_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "updated", "item": updated}


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    """Remove item by ID (and delete image if exists)"""
    item = storage.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Delete file if present
    if "image_path" in item and os.path.exists(item["image_path"]):
        os.remove(item["image_path"])

    storage.delete_item(item_id)
    return {"status": "deleted", "id": item_id}

@router.post("/capture")
async def capture_item():
    """
    Open webcam, capture a clothing item, run inference, and save metadata.
    """
    metadata = cv_inference.capture_from_webcam()
    if not metadata:
        return {"status": "cancelled"}

    # Save to storage
    storage.add_item(metadata)
    return {"status": "added", "metadata": metadata}

