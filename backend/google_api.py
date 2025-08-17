import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not set in environment variables or .env file.")

def _find_places(location: str, radius_km: float, keyword: str) -> List[Dict]:
    """
    Generic helper to find places using Google Places API.
    :param location: Address or "lat,lng" string.
    :param radius_km: Search radius in kilometers.
    :param keyword: Search keyword (e.g., 'donation center', 'thrift store').
    :return: List of places with name, address, and distance.
    """
    # Geocode the location if not already lat,lng
    latlng = _geocode_location(location)
    if not latlng:
        raise ValueError("Could not geocode location.")

    params = {
        "key": GOOGLE_API_KEY,
        "location": f"{latlng['lat']},{latlng['lng']}",
        "radius": int(radius_km * 1000),  # meters
        "keyword": keyword,
    }
    response = requests.get(GOOGLE_PLACES_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "OK":
        raise RuntimeError(f"Google Places API error: {data.get('status')} - {data.get('error_message', '')}")

    results = []
    for place in data.get("results", []):
        results.append({
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "location": place.get("geometry", {}).get("location"),
            "place_id": place.get("place_id"),
        })
    return results

def _geocode_location(location: str) -> Optional[Dict]:
    """
    Geocode a location string to lat/lng using Google Geocoding API.
    :param location: Address or "lat,lng"
    :return: Dict with 'lat' and 'lng'
    """
    # If already lat,lng, return as dict
    if "," in location and all(part.replace('.', '', 1).replace('-', '', 1).isdigit() for part in location.split(",")):
        lat, lng = map(float, location.split(","))
        return {"lat": lat, "lng": lng}

    GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location,
        "key": GOOGLE_API_KEY,
    }
    response = requests.get(GEOCODE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    if data.get("status") == "OK" and data["results"]:
        loc = data["results"][0]["geometry"]["location"]
        return {"lat": loc["lat"], "lng": loc["lng"]}
    return None

def find_donation_centers(location: str, radius_km: float = 10) -> List[Dict]:
    """
    Find donation centers near a location.
    :param location: Address or "lat,lng"
    :param radius_km: Search radius in kilometers
    :return: List of donation centers
    """
    return _find_places(location, radius_km, keyword="donation center")

def find_thrift_stores(location: str, radius_km: float = 10) -> List[Dict]:
    """
    Find thrift stores near a location.
    :param location: Address or "lat,lng"
    :param radius_km: Search radius in kilometers
    :return: List of thrift stores
    """
    return _find_places(location, radius_km, keyword="thrift store")

