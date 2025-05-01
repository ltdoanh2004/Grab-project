#!/usr/bin/env python3
"""
Main API server entry point that registers all routers.
This script is responsible for initializing the FastAPI app
and registering all router components from different modules.
"""

import os
import sys
import uvicorn
import logging
from fastapi import FastAPI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Initialize main FastAPI app
app = FastAPI(
    title="Travel API",
    description="Travel planning and recommendation API",
    version="1.0.0"
)

def register_routers():
    """Register all router components from different modules"""
    try:
        # Import routers
        from api.backend_api import recommend_router, backend_router
        from api.trip_plan_api import router as trip_plan_router
        
        # Register routers with appropriate prefixes
        app.include_router(recommend_router, prefix="/api/v1")
        app.include_router(trip_plan_router, prefix="/api/v1")
        app.include_router(backend_router, prefix="/api")
        
        logger.info("All routers registered successfully")
    except Exception as e:
        logger.error(f"Error registering routers: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Register all routers before starting the server
    register_routers()
    
    # Get port from environment variable or use default
    port = int(os.getenv("API_PORT", 8001))
    
    print(f"Starting Travel API server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True) 