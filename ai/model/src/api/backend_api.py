import requests
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Load environment variables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)

app = FastAPI(title="Travel Recommendation API")

# Import TravelModel sau khi đã định nghĩa các class cần thiết
from ai.model.src.travel_model import TravelModel
model = TravelModel()

class TripSuggestionRequest(BaseModel):
    activities: List[str]
    budget: str
    duration_days: int
    limit: int
    location: str
    season: str
    travel_style: str

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

@app.post("/api/v1/suggest/trips", response_model=TripSuggestionResponse)
async def suggest_trips(request: TripSuggestionRequest):
    """
    Endpoint to suggest complete trips based on various criteria
    """
    try:
        # Create a detailed query context
        query = f"""
        Planning a trip with the following details:
        - Activities: {', '.join(request.activities)}
        - Budget: {request.budget}
        - Duration: {request.duration_days} days
        - Location: {request.location}
        - Season: {request.season}
        - Travel Style: {request.travel_style}
        
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
        
        # Process the query using TravelModel
        result = model.process_query(query)
        
        return {
            "status": "success",
            "response": result,
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 