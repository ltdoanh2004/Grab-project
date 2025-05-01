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
    accommodations: AccommodationData
    places: PlaceData
    restaurants: RestaurantData

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

@router.post("/trip/get_plan", response_model=TripPlanResponse)
async def get_trip_plan(request: TripPlanRequest):
    """
    Endpoint to generate a comprehensive trip plan based on selected accommodations, places, and restaurants
    """
    try:
        # Extract data from request
        accommodations = request.accommodations.accommodations
        places = request.places.places
        restaurants = request.restaurants.restaurants
        
        logger.info(f"Received trip plan request with {len(accommodations)} accommodations, {len(places)} places, and {len(restaurants)} restaurants")
        
        # Convert Pydantic models to dictionaries
        input_data = {
            "accommodations": [acc.model_dump() for acc in accommodations],
            "places": [place.model_dump() for place in places], 
            "restaurants": [restaurant.model_dump() for restaurant in restaurants]
        }
        
        # Here you would normally pass the input_data to your plan model to process
        # For now, we'll just return a simple response with the input data
        result = {
            "itinerary": [],  # This would be filled by the model
            "summary": {
                "total_duration": "0 days",
                "total_cost": sum([acc.price for acc in accommodations]),
                "accommodations": len(accommodations),
                "places": len(places),
                "restaurants": len(restaurants)
            },
            "input_data": input_data  # Including the input data for debugging
        }

        result = model.generate_plan(input_data)


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