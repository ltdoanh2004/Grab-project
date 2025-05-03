from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup proper import paths
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Initialize plan model
try:
    from src.plan_model import PlanModel
    model = PlanModel()
    logger.info("PlanModel imported successfully")
except ImportError:
    logger.warning("Failed to import PlanModel from src.plan_model, trying alternative import path")
    try:
        from ai.model.src.plan_model import PlanModel
        model = PlanModel()
        logger.info("PlanModel imported successfully from alternative path")
    except ImportError as e:
        logger.error(f"Failed to import PlanModel: {e}")
        # For development, create a mock model
        class MockPlanModel:
            def generate_plan(self, input_data):
                return {
                    "itinerary": [
                        {
                            "day": 1,
                            "date": "Day 1",
                            "activities": []
                        }
                    ],
                    "summary": {
                        "total_duration": "1 day",
                        "total_cost": 0
                    }
                }
        model = MockPlanModel()
        logger.warning("Using MockPlanModel for development")

# Create router with tags for better API documentation
router = APIRouter(tags=["Trip Planning"])

# Models for trip plan retrieval
class ImageInfo(BaseModel):
    url: str
    alt: str

class RoomType(BaseModel):
    name: str
    bed_type: str
    occupancy: str
    price: str
    tax_and_fee: str
    conditions: str

class Accommodation(BaseModel):
    accommodation_id: str
    name: str
    description: str
    location: str
    city: str
    image_url: List[ImageInfo]
    price: float
    unit: str
    rating: float
    destination_id: str
    booking_link: str
    elderly_friendly: bool
    room_info: str
    room_types: List[RoomType]
    tax_info: str

class AccommodationData(BaseModel):
    accommodations: List[Accommodation]

class Location(BaseModel):
    lat: float
    lon: float

class Place(BaseModel):
    place_id: str
    name: str
    description: str
    address: str
    main_image: str
    images: List[ImageInfo]
    rating: float
    price: str
    opening_hours: str
    type: str
    categories: str
    url: str
    destination_id: str
    reviews: List[str]
    duration: str

class PlaceData(BaseModel):
    places: List[Place]

class Restaurant(BaseModel):
    restaurant_id: str
    name: str
    description: str
    address: str
    cuisines: str
    price_range: str
    rating: float
    main_image: str
    photo_url: str
    media_urls: str
    opening_hours: str
    is_opening: bool
    is_booking: bool
    is_delivery: bool
    reviews: List[str]
    num_reviews: int
    review_summary: str
    example_reviews: str
    phone: str
    url: str
    destination_id: str
    location: Location
    services: List[str]

class RestaurantData(BaseModel):
    restaurants: List[Restaurant]

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

@router.post("/suggest/trip", response_model=TripPlanResponse)
async def get_trip_plan(request: dict):
    """
    Endpoint to generate a comprehensive trip plan based on selected accommodations, places, and restaurants
    """
    try:
        logger.info(f"Received raw trip plan request: {request.keys()}")
        
        # Extract data from request, handling different possible structures
        accommodations = []
        places = []
        restaurants = []
        destination = "Unknown"
        
        # Handle accommodation data
        if "accommodation" in request and "accommodations" in request["accommodation"]:
            accommodations = request["accommodation"]["accommodations"]
            # Try to extract destination from accommodations
            if accommodations and "destination_id" in accommodations[0]:
                destination = accommodations[0]["destination_id"]
        
        # Handle places data
        if "places" in request and "places" in request["places"]:
            places = request["places"]["places"]
            # If destination not found yet, try to get from places
            if destination == "Unknown" and places and "destination_id" in places[0]:
                destination = places[0]["destination_id"]
        
        # Handle restaurants data
        if "restaurants" in request and "restaurants" in request["restaurants"]:
            restaurants = request["restaurants"]["restaurants"]
            # If destination still not found, try to get from restaurants
            if destination == "Unknown" and restaurants and "destination_id" in restaurants[0]:
                destination = restaurants[0]["destination_id"]
        
        logger.info(f"Extracted {len(accommodations)} accommodations, {len(places)} places, and {len(restaurants)} restaurants")
        logger.info(f"Destination identified as: {destination}")
        
        # Function to safely get dict attributes
        def to_dict(obj):
            # For newer Pydantic models using model_dump()
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            # For older Pydantic models using dict()
            elif hasattr(obj, "dict"):
                return obj.dict()
            # If it's already a dict
            elif isinstance(obj, dict):
                return obj
            # Fallback for other objects
            else:
                return {}
        
        # Prepare data for the model
        input_data = {
            "destination": destination,
            "accommodations": [to_dict(acc) for acc in accommodations],
            "places": [to_dict(place) for place in places], 
            "restaurants": [to_dict(rest) for rest in restaurants]
        }
        
        # Calculate total cost for metadata
        total_cost = 0
        for acc in accommodations:
            if "price" in acc:
                total_cost += float(getattr(acc, "price", 0) or 0)
        
        # Add metadata 
        meta = {
            "trip_name": f"Trip to {destination.capitalize()}",
            "start_date": "2023-09-01",  # Default date if not provided
            "end_date": "2023-09-03",    # Default date for a 3-day trip
            "user_id": "user123"
        }
        
        # Generate plan using the model
        logger.info(f"Generating plan with destination: {destination}")
        result = model.generate_plan(input_data, **meta)

        logger.info("Trip plan request processed successfully")
        return {
            "status": "success",
            "plan": result
        }
        
    except Exception as e:
        logger.error(f"Error processing trip plan request: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }

@router.post("/trip/generate_plan", response_model=TripPlanResponse)
async def generate_trip_plan(request: SimpleTripPlanRequest):
    """
    Simplified endpoint to generate a trip plan with more flexible input
    """
    try:
        logger.info(f"Received simplified trip plan request for {request.destination}")
        
        # Prepare input data
        input_data = {
            "destination": request.destination,
            "accommodations": request.accommodations,
            "places": request.places,
            "restaurants": request.restaurants
        }
        
        # Additional metadata
        meta = {}
        if request.trip_name:
            meta["trip_name"] = request.trip_name
        if request.start_date:
            meta["start_date"] = request.start_date
        if request.end_date:
            meta["end_date"] = request.end_date
        
        # Generate plan using our enhanced model
        result = model.generate_plan(input_data, **meta)
        
        logger.info("Trip plan generated successfully")
        return {
            "status": "success",
            "plan": result
        }
        
    except Exception as e:
        logger.error(f"Error generating trip plan: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        } 