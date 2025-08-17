from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend import google_api, closet
from backend.services import ml_recommender

router = APIRouter()

@router.get("/donate")
async def donate_items(
    location: str = Query(..., description="User's location (city, address, or lat,lng)"),
    radius_km: float = Query(10, description="Search radius in kilometers")
):
    """
    Find donation centers near the user using Google Places API.
    """
    try:
        centers = google_api.find_donation_centers(location, radius_km)
        return {"status": "ok", "centers": centers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding donation centers: {e}")

@router.get("/sell")
async def sell_items(
    location: str = Query(..., description="User's location (city, address, or lat,lng)"),
    radius_km: float = Query(10, description="Search radius in kilometers")
):
    """
    Find thrifting stores near the user using Google Places API.
    """
    try:
        stores = google_api.find_thrift_stores(location, radius_km)
        return {"status": "ok", "stores": stores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding thrift stores: {e}")

@router.get("/recycle")
async def get_upcycling_ideas(
    item_type: Optional[str] = Query(None, description="Type of clothing item (optional)")
):
    """
    Provide upcycling ideas for a clothing item using ML model.
    """
    try:
        suggestions = ml_recommender.get_upcycle_ideas(item_type)
        return {"status": "ok", "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting upcycling ideas: {e}")

@router.get("/style")
async def style_recommendation(
    itemid: int = Query(..., description="ID of the wardrobe item to style"),
    event_details: Optional[str] = Query(None, description="Event details for styling (optional)")
):
    """
    Provide styling recommendations using wardrobe items and ML model.
    """
    try:
        item = closet.get_item(itemid)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found in wardrobe")
        wardrobe = closet.list_items()
        recommendation = ml_recommender.get_styling_recommendation(item, wardrobe, event_details)
        return {"status": "ok", "recommendation": recommendation}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating styling recommendation: {e}")