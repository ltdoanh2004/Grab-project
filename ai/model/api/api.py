from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add parent directory to system path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import TravelModel after path is set
from ai.model.src.travel_model import TravelModel
import uvicorn

# Import trip planning router
from trip_plan_api import router as trip_plan_router

app = FastAPI(title="Travel Recommendation API")
model = TravelModel()

# Include trip planning router
app.include_router(trip_plan_router, prefix="/api/v1")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    response: str | None = None
    error: str | None = None

class SuggestRequest(BaseModel):
    activities: List[str]
    budget: str
    duration_days: int
    limit: int
    location: str
    season: str
    travel_style: str

class SuggestResponse(BaseModel):
    status: str
    ids: List[str] | None = None
    error: str | None = None

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """
    Endpoint to handle general travel queries
    """
    try:
        result = model.process_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggest/accommodations", response_model=SuggestResponse)
async def suggest_accommodations(request: SuggestRequest):
    """
    Endpoint to suggest accommodations based on various criteria
    """
    try:
        # Setup hotel database
        model.setup_database("hotels")
        
        # Create context from request
        context = f"""
        Looking for accommodations with:
        - Activities: {', '.join(request.activities)}
        - Budget: {request.budget}
        - Duration: {request.duration_days} days
        - Location: {request.location}
        - Season: {request.season}
        - Travel Style: {request.travel_style}
        """
        
        # Query hotels
        hotel_ids = model.query_hotels(
            query_text=context,
            top_k=request.limit
        )
        
        return {
            "status": "success",
            "ids": hotel_ids
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/suggest/activities", response_model=SuggestResponse)
async def suggest_activities(request: SuggestRequest):
    """
    Endpoint to suggest activities based on various criteria
    """
    try:
        # Setup place database
        model.setup_database("places")
        
        # Create context from request
        context = f"""
        Looking for activities with:
        - Activities: {', '.join(request.activities)}
        - Budget: {request.budget}
        - Duration: {request.duration_days} days
        - Location: {request.location}
        - Season: {request.season}
        - Travel Style: {request.travel_style}
        """
        
        # Query places
        place_ids = model.query_places(
            query_text=context,
            top_k=request.limit
        )
        
        return {
            "status": "success",
            "ids": place_ids
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/suggest/restaurants", response_model=SuggestResponse)
async def suggest_restaurants(request: SuggestRequest):
    """
    Endpoint to suggest restaurants based on various criteria
    """
    try:
        # Setup FnB database
        model.setup_database("fnb")
        
        # Create context from request
        context = f"""
        Looking for restaurants with:
        - Activities: {', '.join(request.activities)}
        - Budget: {request.budget}
        - Duration: {request.duration_days} days
        - Location: {request.location}
        - Season: {request.season}
        - Travel Style: {request.travel_style}
        """
        
        # Query FnB
        fnb_ids = model.query_fnb(
            query_text=context,
            top_k=request.limit
        )
        
        return {
            "status": "success",
            "ids": fnb_ids
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 