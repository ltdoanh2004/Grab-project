#!/bin/bash

# Create output directory if it doesn't exist
OUTPUT_DIR="data_attractions"
mkdir -p "$OUTPUT_DIR"

# Get current timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Get the last index from existing files
LAST_INDEX=0
for file in "$OUTPUT_DIR"/hanoi_attractions_*_index_*.json; do
    if [ -f "$file" ]; then
        # Extract index number from filename
        INDEX=$(echo "$file" | grep -o 'index_[0-9]*' | grep -o '[0-9]*')
        if [ -n "$INDEX" ] && [ "$INDEX" -gt "$LAST_INDEX" ]; then
            LAST_INDEX=$INDEX
        fi
    fi
done

# Increment index for new file
NEW_INDEX=$((LAST_INDEX + 1))

# Create filename with timestamp and index
OUTPUT_FILE="$OUTPUT_DIR/hanoi_attractions_${TIMESTAMP}_index_${NEW_INDEX}.json"

# Log the start of crawling
echo "Starting crawl at $TIMESTAMP"
echo "Output will be saved to: $OUTPUT_FILE"
echo "Using index: $NEW_INDEX"

# Run the crawler with parameters
python patch.py \
    --start-page 11 \
    --max-pages 100 \
    --delay 5.0 \
    --save-interval 5 \
    --threads 10 \
    --output "$OUTPUT_FILE"

# Log completion
echo "Crawl completed at $(date +"%Y-%m-%d %H:%M:%S")"
echo "Data saved to: $OUTPUT_FILE"