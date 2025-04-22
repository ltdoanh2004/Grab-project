#!/bin/bash

OUTPUT_DIR="data_attractions"
mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

LAST_INDEX=0
for file in "$OUTPUT_DIR"/hanoi_attractions_*_index_*.json; do
    if [ -f "$file" ]; then
        INDEX=$(echo "$file" | grep -o 'index_[0-9]*' | grep -o '[0-9]*')
        if [ -n "$INDEX" ] && [ "$INDEX" -gt "$LAST_INDEX" ]; then
            LAST_INDEX=$INDEX
        fi
    fi
done

NEW_INDEX=$((LAST_INDEX + 1))

OUTPUT_FILE="$OUTPUT_DIR/hanoi_attractions_${TIMESTAMP}_index_${NEW_INDEX}.json"

echo "Starting crawl at $TIMESTAMP"
echo "Output will be saved to: $OUTPUT_FILE"
echo "Using index: $NEW_INDEX"

python patch.py \
    --start-page 101 \
    --max-pages 130 \
    --delay 5.0 \
    --save-interval 5 \
    --threads 10 \
    --output "$OUTPUT_FILE"

echo "Crawl completed at $(date +"%Y-%m-%d %H:%M:%S")"
echo "Data saved to: $OUTPUT_FILE"