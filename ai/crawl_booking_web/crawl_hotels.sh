#!/bin/bash

# Default values
URL="https://www.booking.com/searchresults.vi.html?aid=304142&label=gen173nr-1FCAQoggJCEHNlYXJjaF9ow6AgbuG7mWlIKlgEaPQBiAEBmAEquAEHyAEM2AEB6AEB-AEDiAIBqAIDuAKV75HABsACAdICJDJjNTc3NTFlLTBkZjctNGFiOC05MjlhLTk3ZTJlYzBhMmE2ZtgCBeACAQ&sid=7834fe4d42ec780609444a0dd3917e20&dest_id=-3714993&dest_type=city&srpvid=a99e1f4a6e6d022d&"
START_PAGE=1
END_PAGE=100
OUTPUT="data_hotels"
SAVE_MINS=30
SAVE_HOTELS=50
DEBUG=false

# Help function
show_help() {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help                Show this help message"
    echo "  -u, --url URL            Set the URL to crawl (default: Booking.com Hanoi hotels)"
    echo "  -s, --start PAGE         Set the starting page number (default: 1)"
    echo "  -e, --end PAGE           Set the ending page number (default: 100)"
    echo "  -o, --output FILENAME    Set the output filename without extension (default: data_hotels)"
    echo "  -t, --time MINUTES       Save checkpoint every N minutes (default: 30)"
    echo "  -n, --number HOTELS      Save checkpoint every N hotels (default: 50)"
    echo "  -d, --debug             Enable debug logging"
    echo
    echo "Example:"
    echo "  $0 --start 2 --end 4 --output hanoi_hotels"
    echo "  $0 -s 1 -e 10 -o saigon_hotels -t 15 -n 25"
    echo "  $0 -s 1 -e 50 --debug    # Run with debug logging"
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
            SAVE_HOTELS="$2"
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
if ! [[ "$START_PAGE" =~ ^[0-9]+$ ]] || ! [[ "$END_PAGE" =~ ^[0-9]+$ ]] || ! [[ "$SAVE_MINS" =~ ^[0-9]+$ ]] || ! [[ "$SAVE_HOTELS" =~ ^[0-9]+$ ]]; then
    echo "Error: Start page, end page, save minutes and save hotels must be numbers"
    exit 1
fi

if [ "$START_PAGE" -gt "$END_PAGE" ]; then
    echo "Error: Start page cannot be greater than end page"
    exit 1
fi

if [ "$SAVE_MINS" -lt 1 ] || [ "$SAVE_HOTELS" -lt 1 ]; then
    echo "Error: Save intervals must be positive numbers"
    exit 1
fi

# Create data directory if it doesn't exist
DATA_DIR="data_hotels"
mkdir -p "$DATA_DIR"

# Run the crawler
echo "Starting crawler with following parameters:"
echo "URL: $URL"
echo "Start page: $START_PAGE"
echo "End page: $END_PAGE"
echo "Output: $DATA_DIR/${OUTPUT}"
echo "Save every $SAVE_MINS minutes"
echo "Save every $SAVE_HOTELS hotels"
[ "$DEBUG" = true ] && echo "Debug mode: enabled"
echo

# Build the command
CMD="python hotel_crawler.py \
    --url \"$URL\" \
    --start-page $START_PAGE \
    --end-page $END_PAGE \
    --output \"$DATA_DIR/${OUTPUT}\" \
    --save-interval-mins $SAVE_MINS \
    --save-interval-hotels $SAVE_HOTELS"

# Add debug flag if enabled
[ "$DEBUG" = true ] && CMD="$CMD --debug"

# Run the command
eval "$CMD"

# Check if crawl was successful
if [ $? -eq 0 ]; then
    echo
    echo "Crawl completed successfully!"
    echo "Check output files in: $DATA_DIR/"
    echo "- Final results: ${OUTPUT}_final.csv and ${OUTPUT}_final.json"
    echo "- Checkpoints: ${OUTPUT}_page*_*.csv and ${OUTPUT}_page*_*.json"
else
    echo
    echo "Error: Crawl failed!"
    echo "Check for checkpoint files in: $DATA_DIR/"
fi 