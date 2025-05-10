#!/usr/bin/env python3
"""
Main API server entry point that registers all routers.
This script is responsible for initializing the FastAPI app
and registering all router components from different modules.
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

app = FastAPI(
    title="Travel API",
    description="Travel planning and recommendation API",
    version="1.0.0"
)

def register_routers():
    try:
        from src.services.suggest_api import recommend_router
        from src.services.genrate_plan_api import router as trip_plan_router
        from src.services.comment_api import router as comment_router
        
        app.include_router(recommend_router, prefix="/api/v1")
        app.include_router(trip_plan_router, prefix="/api/v1")
        app.include_router(comment_router, prefix="/api/v1")
        logger.info("All routers registered successfully")
    except Exception as e:
        logger.error(f"Error registering routers: {e}", exc_info=True)
        raise

register_routers()

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "status": "ok", 
        "message": "Travel API is running", 
        "version": "1.0.0",
        "available_endpoints": [
            "/api/v1/trip/generate_plan",
            "/api/v1/trip/sample_plan",
            "/api/v1/trip/get_plan",
            "/api/health",
            "/api/v1/health"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8001))
    print(f"Starting Travel API server on port {port}...")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 