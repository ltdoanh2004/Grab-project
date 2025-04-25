#!/bin/bash

# Default values
DEFAULT_URL="https://www.tripadvisor.com/Attraction_Review-g297704-d30373-Reviews-Hanoi_Old_Quarter-Hanoi_Ha_Noi.html"
DEFAULT_START_PAGE=1
DEFAULT_MAX_PAGES=1000
DEFAULT_DELAY=5.0
DEFAULT_SAVE_INTERVAL=5
DEFAULT_THREADS=10
DEFAULT_LOCATION="hanoi"
DEFAULT_MAX_ATTRACTIONS=100000

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            URL="$2"
            shift 2
            ;;
        --start-page)
            START_PAGE="$2"
            shift 2
            ;;
        --max-pages)
            MAX_PAGES="$2"
            shift 2
            ;;
        --delay)
            DELAY="$2"
            shift 2
            ;;
        --save-interval)
            SAVE_INTERVAL="$2"
            shift 2
            ;;
        --threads)
            THREADS="$2"
            shift 2
            ;;
        --location)
            LOCATION="$2"
            shift 2
            ;;
        --max-attractions)
            MAX_ATTRACTIONS="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# Use default values if parameters are not provided
URL=${URL:-$DEFAULT_URL}
START_PAGE=${START_PAGE:-$DEFAULT_START_PAGE}
MAX_PAGES=${MAX_PAGES:-$DEFAULT_MAX_PAGES}
DELAY=${DELAY:-$DEFAULT_DELAY}
SAVE_INTERVAL=${SAVE_INTERVAL:-$DEFAULT_SAVE_INTERVAL}
THREADS=${THREADS:-$DEFAULT_THREADS}
LOCATION=${LOCATION:-$DEFAULT_LOCATION}
MAX_ATTRACTIONS=${MAX_ATTRACTIONS:-$DEFAULT_MAX_ATTRACTIONS}

OUTPUT_DIR="data_attractions"
LOCATION_DIR="$OUTPUT_DIR/$LOCATION"
mkdir -p "$LOCATION_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

LAST_INDEX=0
for file in "$LOCATION_DIR"/attractions_*_index_*.json; do
    if [ -f "$file" ]; then
        INDEX=$(echo "$file" | grep -o 'index_[0-9]*' | grep -o '[0-9]*')
        if [ -n "$INDEX" ] && [ "$INDEX" -gt "$LAST_INDEX" ]; then
            LAST_INDEX=$INDEX
        fi
    fi
done

NEW_INDEX=$((LAST_INDEX + 1))

echo "Starting crawl at $TIMESTAMP"
echo "Using index: $NEW_INDEX"
echo "Parameters:"
echo "Location: $LOCATION"
echo "URL: $URL"
echo "Start Page: $START_PAGE"
echo "Max Pages: $MAX_PAGES"
echo "Max Attractions: $MAX_ATTRACTIONS"
echo "Delay: $DELAY"
echo "Save Interval: $SAVE_INTERVAL"
echo "Threads: $THREADS"

python patch.py \
    --url "$URL" \
    --start-page "$START_PAGE" \
    --max-pages "$MAX_PAGES" \
    --max-attractions "$MAX_ATTRACTIONS" \
    --delay "$DELAY" \
    --save-interval "$SAVE_INTERVAL" \
    --threads "$THREADS" \
    --location "$LOCATION" \
    --output-dir "$OUTPUT_DIR"

echo "Crawl completed at $(date +"%Y-%m-%d %H:%M:%S")"