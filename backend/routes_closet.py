from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services import  image_analyzer
from backend import closet
import os
import shutil
import uuid
import imghdr

router = APIRouter()
UPLOAD_DIR = "backend/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/closet/upload")
async def upload_item(file: UploadFile = File(...)):
    # Generate safe filename
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        ext = ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    try:
        # Save file
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Validate image
        if imghdr.what(path) is None:
            os.remove(path)
            raise HTTPException(status_code=400, detail="Invalid image file")
        # Analyze image
        metadata = image_analyzer.analyze_image(path)
        # Store in closet
        item = closet.add_item({
            "image_path": path,
            **metadata
        })
        return {"status": "added", "item": item}
    except Exception as e:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/closet")
async def list_wardrobe():
    """List all wardrobe items"""
    return {"items": closet.list_items()}

@router.get("/closet/{action}")
async def list_by_action(action: str):
    """
    List wardrobe items filtered by action: sell, recycle, donate, style
    """
    if action not in {"sell", "recycle", "donate", "style"}:
        raise HTTPException(status_code=400, detail="Invalid action")
    return {"items": closet.list_items(action=action)}