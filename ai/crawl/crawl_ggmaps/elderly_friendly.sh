#!/bin/bash

# Create output directory
mkdir -p output/elderly_friendly

# Set up Google Cloud credentials for NLP API
# Uncomment and set this if you have a credentials file
# export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"

echo "Starting elderly-friendly places search in Hanoi..."

# Run the Python script
python3 elderly_friendly_places.py

echo "Search completed!"
echo "Results saved in output/elderly_friendly/" 