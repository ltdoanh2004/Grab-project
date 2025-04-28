import requests
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)

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