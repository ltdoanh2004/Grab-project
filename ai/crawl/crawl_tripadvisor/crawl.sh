#!/bin/bash

# Default values
DEFAULT_URL="https://www.tripadvisor.com/Attraction_Review-g297704-d30373-Reviews-Hanoi_Old_Quarter-Hanoi_Ha_Noi.html"
DEFAULT_START_PAGE=131
DEFAULT_MAX_PAGES=150
DEFAULT_DELAY=5.0
DEFAULT_SAVE_INTERVAL=5
DEFAULT_THREADS=10
DEFAULT_LOCATION="hanoi"

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

OUTPUT_DIR="data_attractions"
mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

LAST_INDEX=0
for file in "$OUTPUT_DIR"/"${LOCATION}"_attractions_*_index_*.json; do
    if [ -f "$file" ]; then
        INDEX=$(echo "$file" | grep -o 'index_[0-9]*' | grep -o '[0-9]*')
        if [ -n "$INDEX" ] && [ "$INDEX" -gt "$LAST_INDEX" ]; then
            LAST_INDEX=$INDEX
        fi
    fi
done

NEW_INDEX=$((LAST_INDEX + 1))

OUTPUT_FILE="$OUTPUT_DIR/${LOCATION}_attractions_${TIMESTAMP}_index_${NEW_INDEX}.json"

echo "Starting crawl at $TIMESTAMP"
echo "Output will be saved to: $OUTPUT_FILE"
echo "Using index: $NEW_INDEX"
echo "Parameters:"
echo "Location: $LOCATION"
echo "URL: $URL"
echo "Start Page: $START_PAGE"
echo "Max Pages: $MAX_PAGES"
echo "Delay: $DELAY"
echo "Save Interval: $SAVE_INTERVAL"
echo "Threads: $THREADS"

python patch.py \
    --url "$URL" \
    --start-page "$START_PAGE" \
    --max-pages "$MAX_PAGES" \
    --delay "$DELAY" \
    --save-interval "$SAVE_INTERVAL" \
    --threads "$THREADS" \
    --output "$OUTPUT_FILE"

echo "Crawl completed at $(date +"%Y-%m-%d %H:%M:%S")"
echo "Data saved to: $OUTPUT_FILE"