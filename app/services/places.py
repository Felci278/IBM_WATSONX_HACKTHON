import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"


class PlacesServiceError(Exception):
    """Custom exception for Places API errors."""
    pass


def _search_places(query: str, location: str, radius_km: int = 5):
    """
    Generic search wrapper for Google Places API.
    
    Args:
        query (str): Search keyword (e.g. "donation center", "tailor")
        location (str): City name or address (will be geocoded by Places API)
        radius_km (int): Search radius in kilometers

    Returns:
        list: List of places with name, address, and rating
    """
    if not GOOGLE_API_KEY:
        raise PlacesServiceError("Google Places API key is missing. Set GOOGLE_PLACES_API_KEY in .env")

    params = {
        "query": f"{query} near {location}",
        "key": GOOGLE_API_KEY,
        "radius": radius_km * 1000,  # Convert to meters
    }

    try:
        response = requests.get(GOOGLE_PLACES_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            raise PlacesServiceError(f"Google API error: {data.get('status')} - {data.get('error_message')}")

        results = []
        for place in data.get("results", []):
            results.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating", "N/A"),
                "location": place.get("geometry", {}).get("location", {}),
                "types": place.get("types", []),
            })
        return results

    except requests.exceptions.RequestException as e:
        raise PlacesServiceError(f"Request failed: {str(e)}")


def find_donation_centers(location: str, radius_km: int = 5):
    """
    Find nearby clothing donation centers.
    """
    return _search_places("clothing donation center", location, radius_km)


def find_tailors(location: str, radius_km: int = 5):
    """
    Find nearby tailoring/repair shops.
    """
    return _search_places("tailor", location, radius_km)
