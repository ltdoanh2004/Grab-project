#!/bin/bash

# Create data directory if it doesn't exist
mkdir -p data

# Function to run crawler for a single city
run_city() {
    city=$1
    echo "Starting crawler for $city"
    python3 crawl.py --city "$city"
}

# List of cities to crawl
cities=(
    "ha-noi"
    "ho-chi-minh"
    "hai-phong"
    "da-nang"
    "khanh-hoa"
    "can-tho"
    "vung-tau"
    "bac-giang"
    "bac-ninh"
    "binh-duong"
    "binh-dinh"
    "binh-thuan"
    "hung-yen"
    "kien-giang"
    "lam-dong"
    "nghe-an"
    "quang-nam"
    "quang-ninh"
    "thanh-hoa"
    "thua-thien-hue"
)

# Number of parallel processes
MAX_PARALLEL=4

# Run cities in parallel with a limit
for city in "${cities[@]}"; do
    # Count running processes
    running=$(jobs -p | wc -l)
    
    # Wait if we've reached the parallel limit
    while [ $running -ge $MAX_PARALLEL ]; do
        sleep 1
        running=$(jobs -p | wc -l)
    done
    
    # Run the city crawler in background
    run_city "$city" &
done

# Wait for all background processes to complete
wait

echo "All cities have been crawled!" 