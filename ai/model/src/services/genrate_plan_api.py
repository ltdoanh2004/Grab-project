from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import logging
from datetime import datetime, timedelta
from src.agents.plan_agent import PlanModel
from src.utils.logger import setup_logger
from src.utils.helper_function import to_dict
from src.models import (
    TripPlanRequest,
    TripPlanResponse,
    SimpleTripPlanRequest
)
from dotenv import load_dotenv
model = PlanModel()
logger = setup_logger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

router = APIRouter(tags=["Trip Planning"])



@router.post("/suggest/trip", response_model=TripPlanResponse)
async def get_trip_plan(request: dict):
    """
    Endpoint to generate a comprehensive trip plan based on selected accommodations, places, and restaurants
    """
    try:
        logger.info(f"Received raw trip plan request: {request.keys()}")
        # logger.info(f"Request: {request}")
        accommodations = []
        places = []
        restaurants = []
        destination = request["destination_id"]
        
        if "accommodation" in request and "accommodations" in request["accommodation"]:
            accommodations = request["accommodation"]["accommodations"]
            
        
        if "places" in request and "places" in request["places"]:
            places = request["places"]["places"]
            
        
        if "restaurants" in request and "restaurants" in request["restaurants"]:
            restaurants = request["restaurants"]["restaurants"]
            
        logger.info(f"Extracted {len(accommodations)} accommodations, {len(places)} places, and {len(restaurants)} restaurants")
        logger.info(f"Destination identified as: {destination}")
        

        input_data = {
            "destination": destination,
            "accommodations": [to_dict(acc) for acc in accommodations],
            "places": [to_dict(place) for place in places], 
            "restaurants": [to_dict(rest) for rest in restaurants]
        }
        
        total_cost = 0
        for acc in accommodations:
            if "price" in acc:
                total_cost += float(getattr(acc, "price", 0) or 0)
        
        current_date = datetime.now()
        end_date = current_date + timedelta(days=2)  # 3-day trip
        
        meta = {
            "trip_name": f"Trip to {destination.capitalize()}",
            "start_date": current_date.strftime("%Y-%m-%d"),  # Ensure valid date format
            "end_date": end_date.strftime("%Y-%m-%d"),        # Ensure valid date format
            "user_id": "user123"
        }
        
        logger.info(f"Generating plan with destination: {destination}")
        result = model.generate_plan(input_data, **meta)

        def standardize_activity(activity):
            activity_type = activity.get("type", "")
            original_id = activity.get("id", "")
            
            standard_fields = {
                "accommodation": {
                    "id": original_id,  
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
                    "id": original_id,  
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
                    "id": original_id,  
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
            
            if activity_type in standard_fields:
                return standard_fields[activity_type]
            
            return standard_fields["place"]

        if not result.get("start_date") or result["start_date"] == "":
            result["start_date"] = meta["start_date"]
        if not result.get("end_date") or result["end_date"] == "":
            result["end_date"] = meta["end_date"]
            
        for day_index, day in enumerate(result.get("plan_by_day", [])):
            if not day.get("date") or day["date"] == "":
                day_date = current_date + timedelta(days=day_index)
                day["date"] = day_date.strftime("%Y-%m-%d")
                
            for segment in day.get("segments", []):
                standardized_activities = []
                
                for activity in segment.get("activities", []):
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
                    
                    standardized_activity = standardize_activity(activity)
                    standardized_activities.append(standardized_activity)
                
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

