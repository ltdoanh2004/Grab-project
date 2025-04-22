#!/bin/bash

# Define locations to search
LOCATIONS=("Hà Nội, Việt Nam")

# Define queries for each type of place
QUERIES=(
    "nhà hàng"
    "cafe"
    "khách sạn"
    "địa điểm vui chơi"
    "quán ăn"
    "bar"
    "cửa hàng tiện lợi"
    "siêu thị"
    "bệnh viện"
)

# Create main output directory
mkdir -p output

# Function to run crawler for a specific location and query
run_crawler() {
    local location="$1"
    local query="$2"
    echo "Starting crawler for $query in $location"
    python3 crwal_ggmaps.py --location "$location" --queries "$query" --radius 10000 --max-results-per-type 1500
}

# Run crawlers in parallel for each location and query
for location in "${LOCATIONS[@]}"; do
    for query in "${QUERIES[@]}"; do
        run_crawler "$location" "$query" &
        # Add a small delay to avoid overwhelming the system
        sleep 2
    done
done

# Wait for all background processes to complete
wait

echo "All crawlers have completed their tasks!"
echo "Data has been saved in type-specific folders under the output directory" 