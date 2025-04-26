#!/bin/bash

# Configuration
OUTPUT_DIR="data_restaurants"
LOCATION="hcmc"
DELAY=4.0
THREADS=4
MAX_PAGES=100000
SAVE_INTERVAL=15  # minutes between saves
STATE_FILE="$OUTPUT_DIR/crawler_state.json"
LAST_PAGE_FILE="$OUTPUT_DIR/last_page.txt"
LOG_FILE="$OUTPUT_DIR/crawler.log"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Initialize or read last crawled page
if [ -f "$LAST_PAGE_FILE" ]; then
    CURRENT_PAGE=$(cat "$LAST_PAGE_FILE")
else
    CURRENT_PAGE=1
fi

# Function to log messages with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to cleanup old files
cleanup_old_files() {
    # Keep only the latest 3 JSON files for each date
    for date_dir in "$OUTPUT_DIR"/*; do
        if [ -d "$date_dir" ]; then
            cd "$date_dir" || continue
            # List files by modification time and keep only the latest 3
            ls -t *.json 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null
            cd - > /dev/null
        fi
    done
}

# Main crawling loop
while true; do
    log_message "Starting crawl from page $CURRENT_PAGE"
    
    # Run the crawler
    python3 food_crawl.py \
        --url "https://www.tripadvisor.com/FindRestaurants?geo=293925&establishmentTypes=10591%2C11776%2C16548%2C16556%2C21908%2C9900%2C9901%2C9909&broadened=false" \
        --max-pages "$MAX_PAGES" \
        --start-page "$CURRENT_PAGE" \
        --delay "$DELAY" \
        --threads "$THREADS" \
        --output-dir "$OUTPUT_DIR" \
        --location "$LOCATION" \
        --save-interval "$SAVE_INTERVAL"

    # Check if crawler completed successfully
    if [ $? -eq 0 ]; then
        # Update last crawled page
        CURRENT_PAGE=$((CURRENT_PAGE + MAX_PAGES))
        echo "$CURRENT_PAGE" > "$LAST_PAGE_FILE"
        log_message "Successfully completed crawl up to page $CURRENT_PAGE"
        
        # Cleanup old files
        cleanup_old_files
        
        # Optional: Add a delay between crawl sessions
        log_message "Waiting 5 minutes before next crawl session..."
        sleep 300
    else
        log_message "Crawler failed. Retrying in 10 minutes..."
        sleep 600
    fi
done 