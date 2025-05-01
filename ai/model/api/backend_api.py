import requests
from typing import List, Dict, Any, Optional, Union
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)

# Setup proper import paths
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Create router for recommendation endpoints
recommend_router = APIRouter(tags=["Recommendations"])

# Create an API router for backend operations
backend_router = APIRouter(tags=["Backend"])

# Import TravelModel sau khi đã định nghĩa các class cần thiết
try:
    from src.travel_model import TravelModel
    recommend_model = TravelModel()
    logger.info("TravelModel imported successfully")
except ImportError:
    logger.warning("Failed to import TravelModel from src.travel_model, trying alternative import path")
    try:
        from ai.model.src.travel_model import TravelModel
        recommend_model = TravelModel()
        logger.info("TravelModel imported successfully from alternative path")
    except ImportError as e:
        logger.error(f"Failed to import TravelModel: {e}")
        # For development, create a mock model
        class MockTravelModel:
            def process_query(self, query):
                return {"mock": "This is a mock response for development"}
        recommend_model = MockTravelModel()
        logger.warning("Using MockTravelModel for development")

class BudgetInfo(BaseModel):
    type: str
    exactBudget: Optional[int] = None

class PeopleInfo(BaseModel):
    adults: int
    children: int
    infants: int
    pets: int

class TravelTimeInfo(BaseModel):
    type: str
    startDate: datetime
    endDate: datetime

class PersonalOption(BaseModel):
    type: str
    name: str
    description: str

class TripSuggestionRequest(BaseModel):
    destination: str
    budget: BudgetInfo
    people: PeopleInfo
    travelTime: TravelTimeInfo
    personalOptions: List[PersonalOption]

class TripSuggestionResponse(BaseModel):
    status: str
    response: Dict[str, Any] | None = None
    error: str | None = None

class BackendAPI:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        self.api_key = os.getenv("BACKEND_API_KEY")
        
    def get_location_details(self, location_ids: List[str], location_type: str = "hotels") -> Dict[str, Any]:
        """
        Get detailed information for locations from backend using their IDs
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "location_ids": location_ids,
                "location_type": location_type
            }
            
            response = requests.post(
                f"{self.base_url}/api/locations/details",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "error": f"Backend API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def suggest_accommodations(self, 
                             activities: List[str],
                             budget: str,
                             duration_days: int,
                             limit: int,
                             location: str,
                             season: str,
                             travel_style: str) -> Dict[str, Any]:
        """
        Suggest accommodations based on various criteria
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "activities": activities,
                "budget": budget,
                "duration_days": duration_days,
                "limit": limit,
                "location": location,
                "season": season,
                "travel_style": travel_style
            }
            
            response = requests.get(
                f"{self.base_url}/api/v1/suggest/accommodations",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "error": f"Backend API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def suggest_activities(self, 
                          activities: List[str],
                          budget: str,
                          duration_days: int,
                          limit: int,
                          location: str,
                          season: str,
                          travel_style: str) -> Dict[str, Any]:
        """
        Suggest activities based on various criteria
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "activities": activities,
                "budget": budget,
                "duration_days": duration_days,
                "limit": limit,
                "location": location,
                "season": season,
                "travel_style": travel_style
            }
            
            response = requests.get(
                f"{self.base_url}/api/v1/suggest/activities",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "error": f"Backend API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def suggest_restaurants(self, 
                           activities: List[str],
                           budget: str,
                           duration_days: int,
                           limit: int,
                           location: str,
                           season: str,
                           travel_style: str) -> Dict[str, Any]:
        """
        Suggest restaurants based on various criteria
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "activities": activities,
                "budget": budget,
                "duration_days": duration_days,
                "limit": limit,
                "location": location,
                "season": season,
                "travel_style": travel_style
            }
            
            response = requests.get(
                f"{self.base_url}/api/v1/suggest/restaurants",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "error": f"Backend API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def search_locations(self, query: str, location_type: str = "hotels", limit: int = 5) -> Dict[str, Any]:
        """
        Search locations through backend API
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": query,
                "location_type": location_type,
                "limit": limit
            }
            
            response = requests.post(
                f"{self.base_url}/api/locations/search",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "error": f"Backend API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Initialize backend API client
backend_api = BackendAPI()

@recommend_router.post("/suggest/trips", response_model=TripSuggestionResponse)
async def suggest_trips(request: TripSuggestionRequest):
    """
    Endpoint to suggest complete trips based on various criteria
    """
    try:
        # Extract activities from personalOptions
        activities = [option.name for option in request.personalOptions if option.type == "activities"]
        
        # Calculate duration in days
        start_date = request.travelTime.startDate
        end_date = request.travelTime.endDate
        duration_days = (end_date - start_date).days + 1
        if duration_days < 1:
            duration_days = 1
            
        # Extract budget level
        budget = request.budget.type
        
        # Extract travel preferences
        accommodation_prefs = [option.name for option in request.personalOptions if option.type == "accommodation"]
        food_prefs = [option.name for option in request.personalOptions if option.type == "food"]
        transport_prefs = [option.name for option in request.personalOptions if option.type == "transportation"]
        place_prefs = [option.name for option in request.personalOptions if option.type == "places"]
        
        # Determine season based on date
        month = start_date.month
        if 3 <= month <= 5:
            season = "spring"
        elif 6 <= month <= 8:
            season = "summer"
        elif 9 <= month <= 11:
            season = "autumn"
        else:
            season = "winter"
            
        # Determine travel style based on preferences
        travel_style = "family" if request.people.children > 0 else "couple" if request.people.adults == 2 else "solo"
        
        # Create a detailed query context
        query = f"""
        Planning a trip to {request.destination} with the following details:
        - Group: {request.people.adults} adults, {request.people.children} children, {request.people.infants} infants
        - Budget: {budget} (approx. {request.budget.exactBudget if request.budget.exactBudget else 'not specified'} VND)
        - Duration: {duration_days} days
        - Season: {season}
        - Travel Style: {travel_style}
        
        Preferences:
        - Transportation: {', '.join(transport_prefs) if transport_prefs else 'No specific preference'}
        - Accommodation: {', '.join(accommodation_prefs) if accommodation_prefs else 'No specific preference'}
        - Food: {', '.join(food_prefs) if food_prefs else 'No specific preference'}
        - Places to visit: {', '.join(place_prefs) if place_prefs else 'No specific preference'}
        - Activities: {', '.join(activities) if activities else 'No specific preference'}
        
        Please suggest:
        1. Suitable accommodations
        2. Interesting activities and places to visit
        3. Recommended restaurants and food options
        
        Consider:
        - The travel style and preferences
        - The season and weather conditions
        - The budget constraints
        - The duration of stay
        - The location and its unique offerings
        """
        
        logger.info(f"Processing recommendation query for {request.destination}")
        
        # Process the query using TravelModel
        result = recommend_model.process_query(query)
        
        logger.info("Recommendation query processed successfully")
        return {
            "status": "success",
            "response": result,
        }
        
    except Exception as e:
        logger.error(f"Error processing recommendation query: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }

@backend_router.post("/locations/details")
async def get_location_details(location_ids: List[str], location_type: str = "hotels"):
    """
    Get detailed information for locations using their IDs
    """
    result = backend_api.get_location_details(location_ids, location_type)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@backend_router.get("/locations/search")
async def search_locations(query: str, location_type: str = "hotels", limit: int = 5):
    """
    Search for locations by keywords
    """
    result = backend_api.search_locations(query, location_type, limit)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    return result 