#!/bin/bash

# Default values
URL="https://www.booking.com/attractions/searchresults/vn/hanoi.html?label=gen173nr-1FCAQoggJCEHNlYXJjaF9ow6AgbuG7mWlIKlgEaPQBiAEBmAEquAEHyAEM2AEB6AEB-AEDiAIBqAIDuAKV75HABsACAdICJDJjNTc3NTFlLTBkZjctNGFiOC05MjlhLTk3ZTJlYzBhMmE2ZtgCBeACAQ&aid=304142"
START_PAGE=1
END_PAGE=10000
OUTPUT="data_attractions/attractions"
SAVE_MINS=5
SAVE_ATTRACTIONS=10
DEBUG=false

# Help function
show_help() {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help                Show this help message"
    echo "  -u, --url URL            Set the URL to crawl (default: Booking.com Hanoi attractions)"
    echo "  -s, --start PAGE         Set the starting page number (default: 1)"
    echo "  -e, --end PAGE           Set the ending page number (default: 5)"
    echo "  -o, --output FILENAME    Set the output filename without extension (default: data_attractions/attractions)"
    echo "  -t, --time MINUTES       Save checkpoint every N minutes (default: 15)"
    echo "  -n, --number ATTRACTIONS Save checkpoint every N attractions (default: 10)"
    echo "  -d, --debug              Enable debug logging"
    echo
    echo "Example:"
    echo "  $0 --start 1 --end 3 --output data_attractions/hanoi_attractions"
    echo "  $0 -s 1 -e 10 -o data_attractions/top_attractions -t 10 -n 5"
    echo "  $0 -s 1 -e 5 --debug     # Run with debug logging"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--url)
            URL="$2"
            shift 2
            ;;
        -s|--start)
            START_PAGE="$2"
            shift 2
            ;;
        -e|--end)
            END_PAGE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -t|--time)
            SAVE_MINS="$2"
            shift 2
            ;;
        -n|--number)
            SAVE_ATTRACTIONS="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate input
if ! [[ "$START_PAGE" =~ ^[0-9]+$ ]] || ! [[ "$END_PAGE" =~ ^[0-9]+$ ]] || ! [[ "$SAVE_MINS" =~ ^[0-9]+$ ]] || ! [[ "$SAVE_ATTRACTIONS" =~ ^[0-9]+$ ]]; then
    echo "Error: Start page, end page, save minutes and save attractions must be numbers"
    exit 1
fi

if [ "$START_PAGE" -gt "$END_PAGE" ]; then
    echo "Error: Start page cannot be greater than end page"
    exit 1
fi

if [ "$SAVE_MINS" -lt 1 ] || [ "$SAVE_ATTRACTIONS" -lt 1 ]; then
    echo "Error: Save intervals must be positive numbers"
    exit 1
fi

# Create data directory if it doesn't exist
DATA_DIR=$(dirname "$OUTPUT")
mkdir -p "$DATA_DIR"

# Run the crawler
echo "Starting crawler with following parameters:"
echo "URL: $URL"
echo "Start page: $START_PAGE"
echo "End page: $END_PAGE"
echo "Output: $OUTPUT"
echo "Save every $SAVE_MINS minutes"
echo "Save every $SAVE_ATTRACTIONS attractions"
[ "$DEBUG" = true ] && echo "Debug mode: enabled"
echo

# Build the command
CMD="python attraction_crawler.py \
    --url \"$URL\" \
    --start-page $START_PAGE \
    --end-page $END_PAGE \
    --output \"$OUTPUT\" \
    --save-interval-mins $SAVE_MINS \
    --save-interval-attractions $SAVE_ATTRACTIONS"

# Add debug flag if enabled
[ "$DEBUG" = true ] && CMD="$CMD --debug"

# Run the command
eval "$CMD"

# Check if crawl was successful
if [ $? -eq 0 ]; then
    echo
    echo "Crawl completed successfully!"
    echo "Check output files in: $DATA_DIR/"
    echo "- Final results: $(basename $OUTPUT)_final.csv and $(basename $OUTPUT)_final.json"
    echo "- Checkpoints: $(basename $OUTPUT)_page*_*.csv and $(basename $OUTPUT)_page*_*.json"
else
    echo
    echo "Error: Crawl failed!"
    echo "Check for checkpoint files in: $DATA_DIR/"
fi 