from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .accommodation_models import AccommodationData
from .place_models import PlaceData
from .restaurant_models import RestaurantData

class TripPlanRequest(BaseModel):
    accommodation: Optional[AccommodationData] = None
    places: Optional[PlaceData] = None
    restaurants: Optional[RestaurantData] = None

    # Allow additional properties for flexibility
    class Config:
        extra = "allow"

class TripPlanResponse(BaseModel):
    status: str
    plan: Dict[str, Any] | None = None
    error: str | None = None

class SimpleTripPlanRequest(BaseModel):
    destination: str
    trip_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    accommodations: List[Dict[str, Any]] = []
    places: List[Dict[str, Any]] = []
    restaurants: List[Dict[str, Any]] = [] 