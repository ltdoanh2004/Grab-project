# Crawl Module

This module contains various web crawlers for collecting tourism and food-related data from different sources. Each subfolder contains a specific crawler implementation.

## Submodules

### 1. crawl_ggmaps
- **Purpose**: Crawls Google Maps data for places and locations
- **Features**:
  - Collects place information from Google Maps
  - Special focus on elderly-friendly places
  - Uses Google Maps API and Google Cloud Language API
- **Main Files**:
  - `crwal_ggmaps.py`: Main crawler implementation
  - `elderly_friendly_places.py`: Specialized crawler for elderly-friendly places

### 2. crawl_tripadvisor
- **Purpose**: Crawls TripAdvisor data for attractions and reviews
- **Features**:
  - Collects attraction information and reviews
  - Handles pagination and rate limiting
  - Includes image downloading capabilities
- **Main Files**:
  - `patch.py`: Main crawler implementation
  - `get_image.py`: Image downloader
  - `demo.py`: Example usage

### 3. crawl_booking_web
- **Purpose**: Crawls Booking.com data for hotels and attractions
- **Features**:
  - Collects hotel information and reviews
  - Specialized crawler for elderly-friendly accommodations
  - Attraction data collection
- **Main Files**:
  - `hotel_crawler.py`: Hotel data crawler
  - `attraction_crawler.py`: Attraction data crawler
  - `hotel_crawler_for_elderly_people.py`: Specialized crawler

### 4. crawl_food
- **Purpose**: Crawls food-related data from Foody.vn
- **Features**:
  - Collects restaurant and local food information
  - Handles restaurant reviews and ratings
  - Data export to CSV and JSON formats
- **Main Files**:
  - `foody_crawler.py`: Main crawler implementation
  - `bash_crawl_foody.sh`: Shell script for automation

### 5. crawl_hanoi_tourist
- **Purpose**: Crawls Hanoi-specific tourist information
- **Features**:
  - Focuses on Hanoi-specific attractions and activities
  - Includes test implementations and notebooks
- **Main Files**:
  - `crawl_hanoi_tourist.py`: Main crawler implementation
  - `test.py`: Testing and validation

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. For Playwright (used in crawl_food):
```bash
playwright install
```

3. Set up environment variables:
- Create a `.env` file in the root directory
- Add necessary API keys and credentials

## Usage

Each subfolder contains its own specific instructions and scripts. Refer to individual README files in each subfolder for detailed usage instructions.

## Data Storage

- Each crawler stores its data in its respective `data/` or `output/` directory
- Data formats include:
  - CSV files
  - JSON files
  - Log files for debugging

## Notes

- Some crawlers require API keys or authentication
- Rate limiting and politeness policies are implemented in each crawler
- Regular updates may be required to handle website changes 