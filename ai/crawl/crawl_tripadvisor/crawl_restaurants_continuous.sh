#!/bin/bash

# Default Configuration
OUTPUT_DIR="data_restaurants"
LOCATION="hcmc"
DELAY=4.0
THREADS=4
MAX_PAGES=100000
SAVE_INTERVAL=15  # minutes between saves
START_PAGE=1

# Help function
show_help() {
    echo "Usage: $0 [options] <url>"
    echo "Options:"
    echo "  -o, --output-dir DIR     Output directory (default: data_restaurants)"
    echo "  -l, --location LOC       Location name (default: hcmc)"
    echo "  -d, --delay SEC         Delay between requests (default: 4.0)"
    echo "  -t, --threads NUM       Number of threads (default: 4)"
    echo "  -m, --max-pages NUM     Maximum pages to crawl (default: 100000)"
    echo "  -s, --save-interval MIN Save interval in minutes (default: 15)"
    echo "  -p, --start-page NUM    Start from page number (default: 1)"
    echo "  -r, --reset            Reset crawl (delete tracking files)"
    echo "  -h, --help             Show this help message"
    echo
    echo "Example:"
    echo "  $0 \"https://www.tripadvisor.com/Restaurants-g293925-Ho_Chi_Minh_City.html\""
    echo "  $0 -l hanoi -d 5 \"https://www.tripadvisor.com/Restaurants-g293924-Hanoi.html\""
}

# Parse command line arguments
RESET=false
URL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -l|--location)
            LOCATION="$2"
            shift 2
            ;;
        -d|--delay)
            DELAY="$2"
            shift 2
            ;;
        -t|--threads)
            THREADS="$2"
            shift 2
            ;;
        -m|--max-pages)
            MAX_PAGES="$2"
            shift 2
            ;;
        -s|--save-interval)
            SAVE_INTERVAL="$2"
            shift 2
            ;;
        -p|--start-page)
            START_PAGE="$2"
            shift 2
            ;;
        -r|--reset)
            RESET=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        http*)
            URL="$1"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if URL is provided
if [ -z "$URL" ]; then
    echo "Error: URL is required"
    show_help
    exit 1
fi

# Setup directories and files
STATE_FILE="$OUTPUT_DIR/crawler_state.json"
LAST_PAGE_FILE="$OUTPUT_DIR/last_page.txt"
LOG_FILE="$OUTPUT_DIR/crawler.log"
VISITED_URLS="visited_urls.json"
ALL_RESTAURANTS="all_restaurants.json"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Reset if requested
if [ "$RESET" = true ]; then
    echo "Resetting crawler state..."
    rm -f "$LAST_PAGE_FILE" "$VISITED_URLS" "$ALL_RESTAURANTS"
    echo "$START_PAGE" > "$LAST_PAGE_FILE"
    CURRENT_PAGE=$START_PAGE
else
    # Initialize or read last crawled page
    if [ -f "$LAST_PAGE_FILE" ]; then
        CURRENT_PAGE=$(cat "$LAST_PAGE_FILE")
    else
        CURRENT_PAGE=$START_PAGE
        echo "$CURRENT_PAGE" > "$LAST_PAGE_FILE"
    fi
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
log_message "Starting crawler with URL: $URL"
log_message "Output directory: $OUTPUT_DIR"
log_message "Location: $LOCATION"
log_message "Delay: $DELAY seconds"
log_message "Threads: $THREADS"

while true; do
    log_message "Starting crawl from page $CURRENT_PAGE"
    
    # Run the crawler
    python3 food_crawl.py \
        --url "$URL" \
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