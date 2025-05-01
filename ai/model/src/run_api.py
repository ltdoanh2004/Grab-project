#!/usr/bin/env python3
"""
Run script for the Travel Recommendation API server.
This ensures proper package context for imports.
"""

import os
import sys

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import and run the API
from api.backend_api import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 