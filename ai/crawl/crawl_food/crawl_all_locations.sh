#!/bin/bash

# Bash script to crawl multiple locations simultaneously using the foody_crawler.py script

# Default settings
CRAWL_METHOD="api"  # web or api
PAGES=5000          # Number of pages to crawl (for web method)
ITEMS=100000         # Number of items to crawl (for api method) - Tăng lên để lấy nhiều dữ liệu hơn
OUTPUT_DIR="data"   # Base directory to save crawled data
MAX_PARALLEL=3      # Maximum number of parallel processes - Giảm xuống để tránh bị chặn
RETRY=true          # Retry failed crawlers
MAX_RETRIES=3       # Maximum number of retries
RETRY_DELAY=300     # Delay giữa các lần retry (giây)

# Function to display help message
function show_help {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help            Show this help message"
    echo "  -m, --method METHOD   Crawling method: 'web' or 'api' (default: api)"
    echo "  -p, --pages NUMBER    Number of pages to crawl for web method (default: 5000)"
    echo "  -i, --items NUMBER    Number of items to crawl for api method (default: 1000)"
    echo "  -o, --output DIR      Output directory for data (default: data)"
    echo "  -j, --parallel NUMBER Maximum number of parallel processes (default: 3)"
    echo "  -l, --locations LIST  Comma-separated list of locations to crawl"
    echo "                        Available locations: hanoi,hochiminh,danang,haiphong,nhatrang,cantho,khanhhoa,vungtau,binhthuan,lamdong"
    echo "                        If not specified, all locations will be crawled"
    echo "  -r, --retry           Enable/disable retrying failed crawlers (default: true)"
    echo "  --max-retries NUMBER  Maximum number of retries per location (default: 3)"
    echo "  --retry-delay NUMBER  Delay between retries in seconds (default: 300)"
    echo "  --restart             Restart any crawler that has failed or hasn't collected data"
    echo
    echo "Example:"
    echo "  $0 --method api --items 1000 --parallel 3 --locations hanoi,hochiminh,danang"
}

# Parse command line arguments
RESTART=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -m|--method)
            CRAWL_METHOD="$2"
            shift 2
            ;;
        -p|--pages)
            PAGES="$2"
            shift 2
            ;;
        -i|--items)
            ITEMS="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -j|--parallel)
            MAX_PARALLEL="$2"
            shift 2
            ;;
        -l|--locations)
            LOCATIONS="$2"
            shift 2
            ;;
        -r|--retry)
            RETRY="$2"
            shift 2
            ;;
        --max-retries)
            MAX_RETRIES="$2"
            shift 2
            ;;
        --retry-delay)
            RETRY_DELAY="$2"
            shift 2
            ;;
        --restart)
            RESTART=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Define all available locations
ALL_LOCATIONS=("hanoi" "hochiminh" "danang" "haiphong" "nhatrang" "cantho" "khanhhoa" "vungtau" "binhthuan" "lamdong")

# If no locations specified, use all locations
if [ -z "$LOCATIONS" ]; then
    LOCATIONS_ARRAY=("${ALL_LOCATIONS[@]}")
else
    # Convert comma-separated string to array
    IFS=',' read -ra LOCATIONS_ARRAY <<< "$LOCATIONS"
    
    # Validate locations
    for loc in "${LOCATIONS_ARRAY[@]}"; do
        valid=false
        for valid_loc in "${ALL_LOCATIONS[@]}"; do
            if [ "$loc" = "$valid_loc" ]; then
                valid=true
                break
            fi
        done
        
        if [ "$valid" = false ]; then
            echo "Error: Invalid location '$loc'"
            echo "Valid locations: ${ALL_LOCATIONS[*]}"
            exit 1
        fi
    done
fi

# Create log directory
LOG_DIR="logs"
mkdir -p "$LOG_DIR"
mkdir -p "$OUTPUT_DIR"

# Function to check if a location needs crawling
# Returns true (0) if it needs crawling, false (1) if not
function needs_crawling {
    local location=$1
    local location_dir="${OUTPUT_DIR}/${location}"
    
    # If restart flag is set, crawl all locations
    if [ "$RESTART" = true ]; then
        return 0
    fi
    
    # If location directory doesn't exist or is empty, it needs crawling
    if [ ! -d "$location_dir" ] || [ -z "$(ls -A "$location_dir")" ]; then
        return 0
    fi
    
    # If directory has very few files, it probably needs more crawling
    file_count=$(find "$location_dir" -type f -name "*.json" | wc -l)
    if [ "$file_count" -lt 50 ]; then  # Tăng ngưỡng số lượng file
        return 0
    fi
    
    # Location already has some data, does not need crawling
    return 1
}

# Function to crawl a location
function crawl_location {
    local location=$1
    local retry_count=${2:-0}  # Default retry count is 0
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local log_file="${LOG_DIR}/foody_${location}_${timestamp}.log"
    
    echo "Starting crawler for $location ($(date), retry: $retry_count)" | tee -a "$log_file"
    
    # Build command based on method
    if [ "$CRAWL_METHOD" = "web" ]; then
        cmd="python foody_crawler.py --location $location --crawl-method web --pages $PAGES --output-dir $OUTPUT_DIR"
    else
        cmd="python foody_crawler.py --location $location --crawl-method api --total-items $ITEMS --output-dir $OUTPUT_DIR"
    fi
    
    # MacOS terminal
    if [ "$(uname)" = "Darwin" ]; then
        osascript -e "tell application \"Terminal\" to do script \"cd $(pwd) && $cmd\""
    # Linux with gnome-terminal
    elif command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "$cmd; echo 'Press enter to close'; read"
    # Linux with xterm
    elif command -v xterm &> /dev/null; then
        xterm -e "$cmd; echo 'Press enter to close'; read" &
    # Fallback to background process
    else
        echo "No supported terminal found. Running in background..."
        $cmd >> "$log_file" 2>&1 &
    fi
    
    # Store PID and location for retry mechanism
    local pid=$!
    echo "$location:$pid:$retry_count" >> "$LOG_DIR/active_crawlers.txt"
    
    echo "Started crawler for $location with PID $! (log: $log_file)"
}

# Function to wait until we have fewer than MAX_PARALLEL processes running
function wait_for_slot {
    while [ $(jobs -r | wc -l) -ge $MAX_PARALLEL ]; do
        sleep 1
    done
}

# Initialize active crawlers file
> "$LOG_DIR/active_crawlers.txt"

# Main execution
echo "Starting crawlers for locations: ${LOCATIONS_ARRAY[*]}"
echo "Method: $CRAWL_METHOD, Max parallel: $MAX_PARALLEL"
echo "Output directory: $OUTPUT_DIR"

# Xoay vòng các địa điểm để phân bố đồng đều tải
if [ ${#LOCATIONS_ARRAY[@]} -gt 1 ]; then
    echo "Rotating locations to distribute load evenly"
    
    # Sắp xếp theo thứ tự kích thước dữ liệu (ít đến nhiều)
    declare -A location_sizes
    for loc in "${LOCATIONS_ARRAY[@]}"; do
        location_dir="${OUTPUT_DIR}/${loc}"
        if [ -d "$location_dir" ]; then
            file_count=$(find "$location_dir" -type f -name "*.json" | wc -l)
            location_sizes[$loc]=$file_count
        else
            location_sizes[$loc]=0
        fi
    done
    
    # In thông tin kích thước
    echo "Current location sizes:"
    for loc in "${LOCATIONS_ARRAY[@]}"; do
        echo "  $loc: ${location_sizes[$loc]} files"
    done
    
    # Sắp xếp các location theo số lượng file đã có (ít nhất trước)
    SORTED_LOCATIONS=()
    for loc in "${LOCATIONS_ARRAY[@]}"; do
        SORTED_LOCATIONS+=("$loc")
    done
    
    # Sắp xếp đơn giản bằng bubble sort
    for ((i=0; i<${#SORTED_LOCATIONS[@]}; i++)); do
        for ((j=i+1; j<${#SORTED_LOCATIONS[@]}; j++)); do
            if [ ${location_sizes[${SORTED_LOCATIONS[$i]}]} -gt ${location_sizes[${SORTED_LOCATIONS[$j]}]} ]; then
                # Swap
                temp=${SORTED_LOCATIONS[$i]}
                SORTED_LOCATIONS[$i]=${SORTED_LOCATIONS[$j]}
                SORTED_LOCATIONS[$j]=$temp
            fi
        done
    done
    
    echo "Order of crawling (lowest first):"
    for loc in "${SORTED_LOCATIONS[@]}"; do
        echo "  $loc: ${location_sizes[$loc]} files"
    done
    
    CRAWL_LOCATIONS=()
    for loc in "${SORTED_LOCATIONS[@]}"; do
        if needs_crawling "$loc"; then
            CRAWL_LOCATIONS+=("$loc")
        else
            echo "Skipping $loc - already has enough data (${location_sizes[$loc]} files)"
        fi
    done
else
    # Build list of locations that need crawling
    CRAWL_LOCATIONS=()
    for location in "${LOCATIONS_ARRAY[@]}"; do
        if needs_crawling "$location"; then
            CRAWL_LOCATIONS+=("$location")
        else
            echo "Skipping $location - already has data"
        fi
    done
fi

echo "Will crawl these locations: ${CRAWL_LOCATIONS[*]}"

# Start crawlers
for location in "${CRAWL_LOCATIONS[@]}"; do
    wait_for_slot
    crawl_location "$location" 0
    # Small delay to avoid terminal conflicts
    sleep 2
done

echo "All crawlers have been started. Check the $LOG_DIR directory for logs."
echo "To check crawler status: ps aux | grep python"
echo "To view log files: ls -la $LOG_DIR"

if [ "$RETRY" = true ]; then
    echo "Retry mechanism is enabled. Will monitor crawlers and restart if necessary."
    
    # Monitor running crawlers and restart if needed
    MAX_WAIT_TIME=7200  # Max wait time in seconds (2 hours)
    WAIT_INTERVAL=60    # Check every minute
    WAITED=0
    
    while [ $WAITED -lt $MAX_WAIT_TIME ]; do
        sleep $WAIT_INTERVAL
        WAITED=$((WAITED + WAIT_INTERVAL))
        
        echo "Checking crawler status after $WAITED seconds..."
        
        # Process each location to see if it needs a retry
        for location in "${CRAWL_LOCATIONS[@]}"; do
            # Check if crawler is still running
            if ps aux | grep -v grep | grep -q "python.*--location $location"; then
                echo "$location crawler is still running."
                continue
            fi
            
            # Get retry count from active_crawlers.txt
            retry_line=$(grep "^$location:" "$LOG_DIR/active_crawlers.txt" | tail -n 1)
            if [ -z "$retry_line" ]; then
                retry_count=0
            else
                retry_count=$(echo "$retry_line" | cut -d':' -f3)
            fi
            
            # Check if we've reached max retries
            if [ "$retry_count" -ge "$MAX_RETRIES" ]; then
                echo "$location has reached max retries ($MAX_RETRIES). Not restarting."
                continue
            fi
            
            # Check if the location has collected enough data
            file_count=$(find "${OUTPUT_DIR}/${location}" -type f -name "*.json" | wc -l)
            if [ "$file_count" -ge 100 ]; then
                echo "$location has collected $file_count files, which is enough. Not restarting."
                continue
            fi
            
            # Wait a bit between retries to avoid overwhelming the server
            echo "Waiting ${RETRY_DELAY} seconds before restarting $location crawler..."
            sleep $RETRY_DELAY
            
            # Restart the crawler
            echo "$location crawler seems to have stopped with only $file_count files. Restarting (retry $((retry_count + 1))/$MAX_RETRIES)..."
            wait_for_slot
            crawl_location "$location" $((retry_count + 1))
            sleep 2
        done
    done
    
    echo "Monitoring period has ended after $MAX_WAIT_TIME seconds."
else
    echo "Retry mechanism is disabled. Crawlers will not be automatically restarted."
fi

# Wait for all background jobs to complete
wait

echo "All crawlers completed." 