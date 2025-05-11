import requests
from typing import List, Dict, Any, Optional, Union
import os
import sys
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from src.agents.travel_agent import TravelModel
from src.utils.logger import setup_logger
from src.models.request_models import TripSuggestionRequest
from src.models.reponse_models import SuggestWithIDAndType

logger = setup_logger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

recommend_router = APIRouter(tags=["Recommendations"])

@recommend_router.get("/health")
async def health_check():
    """Health check endpoint for the recommendation service"""
    return {"status": "ok", "service": "recommendations"}

@recommend_router.post("/suggest/all", response_model=List[SuggestWithIDAndType])
async def suggest_trips(request: TripSuggestionRequest):
    """
    Endpoint to suggest complete trips based on various criteria
    """
    try:
        activities = [option.name for option in request.personalOptions if option.type == "activities"]
        
        start_date = request.travelTime.startDate
        end_date = request.travelTime.endDate
        duration_days = (end_date - start_date).days + 1
        if duration_days < 1:
            duration_days = 1
            
        budget = request.budget.type
        
        accommodation_prefs = [option.name for option in request.personalOptions if option.type == "accommodation"]
        food_prefs = [option.name for option in request.personalOptions if option.type == "food"]
        transport_prefs = [option.name for option in request.personalOptions if option.type == "transportation"]
        place_prefs = [option.name for option in request.personalOptions if option.type == "places"]
        extra_prefs = [option.name for option in request.personalOptions if option.type == "extra"]
        
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
            
        travel_style = "family" if request.people.children > 0 else "couple" if request.people.adults == 2 else "solo"
        
        query = f"""
        Planning a trip to {request.destination_id} with the following details:
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
        - Extra: {', '.join(extra_prefs) if extra_prefs else 'No specific preference'}

        IMPORTANT: Please focus on finding recommendations specifically in {request.destination_id}. All suggestions should be located in or near this destination.
        
        Please suggest:
        1. Suitable accommodations in {request.destination_id}
        2. Interesting activities and places to visit in {request.destination_id}
        3. Recommended restaurants and food options in {request.destination_id}
        
        Consider:
        - The travel style and preferences
        - The season and weather conditions in {request.destination_id}
        - The budget constraints
        - The duration of stay
        - The location and its unique offerings
        - All recommendations must be in {request.destination_id}
        """
        
        logger.info(f"Processing recommendation query for {request.destination_id}")
        
        travel_model = TravelModel()
        raw_recommendations = travel_model.process_query(query, destination_id=request.destination_id)
        
        logger.info(f"Recommendation query processed successfully, got {len(raw_recommendations)} items")
        
        # Group the recommendations by type to ensure we have at least one of each type
        accommodations = [r for r in raw_recommendations if r["type"] == "accommodation"]
        places = [r for r in raw_recommendations if r["type"] == "place"]
        restaurants = [r for r in raw_recommendations if r["type"] == "restaurant"]
        
        logger.info(f"Grouped recommendations: {len(accommodations)} accommodations, {len(places)} places, {len(restaurants)} restaurants")
        
        # Ensure we have at least one of each type
        if not accommodations:
            accommodations = [{"name": "Luxury Hotel", "type": "accommodation", "args": "luxury", "id": "hotel_000003"}]
        if not places:
            places = [{"name": "City Museum", "type": "place", "args": "cultural", "id": "place_000003"}]
        if not restaurants:
            restaurants = [{"name": "Local Restaurant", "type": "restaurant", "args": "local cuisine", "id": "restaurant_000003"}]
            
        # Add all recommendations to response, with type-specific ones first
        response = []
        for rec in accommodations + places + restaurants:
            response.append(SuggestWithIDAndType(**rec))
            
        logger.info(f"Final response has {len(response)} items")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing recommendation query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

