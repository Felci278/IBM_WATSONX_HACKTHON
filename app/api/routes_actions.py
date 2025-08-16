from fastapi import APIRouter, Query, HTTPException
from app.services import places, upcycle, calendar, storage
from typing import Optional
from datetime import datetime

router = APIRouter()


@router.get("/donate")
async def donate_items(
    location: str = Query(..., description="User's location (city or address)"),
    radius_km: int = Query(5, description="Search radius in kilometers")
):
    """
    Find donation centers near the user.
    """
    try:
        centers = places.find_donation_centers(location, radius_km)
        return {"status": "ok", "count": len(centers), "donation_centers": centers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch donation centers: {str(e)}")


@router.get("/repair")
async def repair_items(
    location: str = Query(..., description="User's location (city or address)"),
    radius_km: int = Query(5, description="Search radius in kilometers")
):
    """
    Find nearby tailors / repair shops.
    """
    try:
        tailors = places.find_tailors(location, radius_km)
        return {"status": "ok", "count": len(tailors), "tailors": tailors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch repair shops: {str(e)}")


@router.get("/upcycle")
async def get_upcycling_ideas(
    item_type: Optional[str] = Query(None, description="Type of clothing (e.g. shirt, jeans)")
):
    """
    Provide upcycling suggestions for wardrobe items.
    """
    try:
        if item_type:
            ideas = upcycle.suggest_upcycle(item_type)
        else:
            ideas = upcycle.suggest_generic()
        return {"status": "ok", "count": len(ideas), "suggestions": ideas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch upcycling ideas: {str(e)}")


@router.post("/schedule")
async def schedule_action(
    item_id: int,
    action: str = Query(..., description="Action to schedule: donate | repair | upcycle"),
    date: str = Query(..., description="Date for scheduling in ISO format (YYYY-MM-DD)"),
    duration_minutes: int = Query(60, description="Duration of event in minutes")
):
    """
    Schedule an action (donation, repair, upcycle) in the user's calendar.
    """
    try:
        # Validate item exists
        item = storage.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Item with id={item_id} not found")

        # Parse date into datetime
        try:
            start_time = datetime.fromisoformat(date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Create event
        summary = f"{action.capitalize()} item: {item.get('type', 'Clothing')}"
        description = f"Action: {action}\nItem ID: {item_id}\nMaterial: {item.get('material', 'unknown')}"
        
        event = calendar.schedule_event(
            summary=summary,
            description=description,
            start_time=start_time,
            duration_minutes=duration_minutes,
        )

        return {"status": "scheduled", "event": event}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule event: {str(e)}")
