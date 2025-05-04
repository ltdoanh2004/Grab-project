from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import logging
from datetime import datetime, timedelta

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
        
        # Generate current date and end date (3 days from now)
        current_date = datetime.now()
        end_date = current_date + timedelta(days=2)  # 3-day trip
        
        # Add metadata with properly formatted dates
        meta = {
            "trip_name": f"Trip to {destination.capitalize()}",
            "start_date": current_date.strftime("%Y-%m-%d"),  # Ensure valid date format
            "end_date": end_date.strftime("%Y-%m-%d"),        # Ensure valid date format
            "user_id": "user123"
        }
        
        # Generate plan using the model
        logger.info(f"Generating plan with destination: {destination}")
        result = model.generate_plan(input_data, **meta)

        # Function to standardize activity fields based on type
        def standardize_activity(activity):
            activity_type = activity.get("type", "")
            
            # Define standard fields for each type
            standard_fields = {
                "accommodation": {
                    "id": activity.get("id", ""),
                    "type": "accommodation",
                    "name": activity.get("name", ""),
                    "start_time": activity.get("start_time", ""),
                    "end_time": activity.get("end_time", ""),
                    "description": activity.get("description", ""),
                    "location": activity.get("location", activity.get("address", "")),
                    "rating": float(activity.get("rating", 4.5)),
                    "price": float(activity.get("price", 0)) if activity.get("price") else 0,
                    "image_url": activity.get("image_url", ""),
                    "booking_link": activity.get("booking_link", ""),
                    "room_info": activity.get("room_info", "Phòng tiêu chuẩn"),
                    "tax_info": activity.get("tax_info", "Đã bao gồm thuế"),
                    "elderly_friendly": activity.get("elderly_friendly", True),
                    "url": activity.get("url", "")
                },
                "place": {
                    "id": activity.get("id", ""),
                    "type": "place",
                    "name": activity.get("name", ""),
                    "start_time": activity.get("start_time", ""),
                    "end_time": activity.get("end_time", ""),
                    "description": activity.get("description", ""),
                    "address": activity.get("address", activity.get("location", "")),
                    "categories": activity.get("categories", "sightseeing"),
                    "duration": activity.get("duration", "2h"),
                    "opening_hours": activity.get("opening_hours", "08:00-17:00"),
                    "rating": float(activity.get("rating", 4.0)),
                    "price": float(activity.get("price", 0)) if activity.get("price") else 0,
                    "image_url": activity.get("image_url", ""),
                    "url": activity.get("url", "")
                },
                "restaurant": {
                    "id": activity.get("id", ""),
                    "type": "restaurant",
                    "name": activity.get("name", ""),
                    "start_time": activity.get("start_time", ""),
                    "end_time": activity.get("end_time", ""),
                    "description": activity.get("description", ""),
                    "address": activity.get("address", activity.get("location", "")),
                    "cuisines": activity.get("cuisines", "Đặc sản địa phương"),
                    "price_range": activity.get("price_range", "100,000-300,000 VND"),
                    "rating": float(activity.get("rating", 4.2)),
                    "phone": activity.get("phone", ""),
                    "services": activity.get("services", ["đặt bàn"]),
                    "image_url": activity.get("image_url", ""),
                    "url": activity.get("url", "")
                }
            }
            
            # Return standardized activity based on type
            if activity_type in standard_fields:
                return standard_fields[activity_type]
            
            # Default to place type if not recognized
            return standard_fields["place"]

        # Ensure all dates are valid and non-empty
        # Fix main trip dates
        if not result.get("start_date") or result["start_date"] == "":
            result["start_date"] = meta["start_date"]
        if not result.get("end_date") or result["end_date"] == "":
            result["end_date"] = meta["end_date"]
            
        # Fix dates in each day of the plan and standardize activities
        for day_index, day in enumerate(result.get("plan_by_day", [])):
            # If day date is empty, use a date based on the start_date plus day_index
            if not day.get("date") or day["date"] == "":
                day_date = current_date + timedelta(days=day_index)
                day["date"] = day_date.strftime("%Y-%m-%d")
                
            # Fix and standardize activities
            for segment in day.get("segments", []):
                standardized_activities = []
                
                for activity in segment.get("activities", []):
                    # Ensure start_time and end_time are non-empty
                    if not activity.get("start_time") or activity["start_time"] == "":
                        if segment["time_of_day"] == "morning":
                            activity["start_time"] = "08:00"
                        elif segment["time_of_day"] == "afternoon":
                            activity["start_time"] = "13:00"
                        elif segment["time_of_day"] == "evening":
                            activity["start_time"] = "19:00"
                    
                    if not activity.get("end_time") or activity["end_time"] == "":
                        if segment["time_of_day"] == "morning":
                            activity["end_time"] = "10:00"
                        elif segment["time_of_day"] == "afternoon":
                            activity["end_time"] = "15:00"
                        elif segment["time_of_day"] == "evening":
                            activity["end_time"] = "21:00"
                    
                    # Standardize the activity based on its type
                    standardized_activity = standardize_activity(activity)
                    standardized_activities.append(standardized_activity)
                
                # Replace activities with standardized ones
                segment["activities"] = standardized_activities
        
        logger.info(f"Generated plan: {result}")
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