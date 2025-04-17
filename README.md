# Hanoi TripAdvisor Attraction & Tour Crawler

A specialized web crawler for extracting comprehensive attraction and tour information from TripAdvisor's Hanoi pages.

## Features

- Extracts detailed information about Hanoi attractions and tours from TripAdvisor
- Handles multiple pages of listings
- Collects comprehensive data points including activities, weather types, and departure info
- Extracts user comments for better insights
- Exports data in both CSV and JSON formats
- Configurable crawling parameters (delay, max pages, max items)
- Robust error handling and retry mechanism
- Rate limiting to avoid being blocked

## Data Collected

The crawler extracts the following information for each attraction/tour:

| Field                | Description                                                                          |
| -------------------- | ------------------------------------------------------------------------------------ |
| name                 | Name of the attraction or tour                                                       |
| location             | Specific location (city/province/country)                                            |
| coordinates          | GPS coordinates (latitude, longitude) for distance calculations                      |
| category             | Type of place: beach, mountain, nature, spiritual, cultural, shopping, entertainment |
| activities           | Activities available (extracted from "What to expect")                               |
| recommended_duration | Recommended time to stay (hours or days)                                             |
| departure_and_return | Departure and return information for tours                                           |
| average_cost         | Average cost (estimated or specific)                                                 |
| suitable_for         | Suitable groups: solo, couples, friends, family, seniors                             |
| user_rating          | Rating score (e.g., 4.3/5 stars from TripAdvisor)                                    |
| image_url            | Image links (for UI display)                                                         |
| description          | Short description (about the place/tour) from Overview section                       |
| weather_type         | Suitable weather types (sunny, dry, cold, mild, no rain)                             |
| tags                 | Suggested keywords: "adventure", "romantic", "family-friendly", etc.                 |
| nearby_attractions   | Nearby attractions (for easy itinerary building)                                     |
| comments             | 2 comments from the comments section with commenter info                             |

## Requirements

- Python 3.6+
- Required packages:
  - requests
  - beautifulsoup4

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install requests beautifulsoup4
   ```

## Usage

### Basic Usage

Run the crawler with default settings:

```
python hanoi_tour_crawler.py
```

This will crawl up to 3 pages and save the data to `data/hanoi_attractions.csv` and `data/hanoi_attractions.json`.

### Advanced Usage

Customize the crawler behavior with command-line arguments:

```
python hanoi_tour_crawler.py --max-pages 5 --max-tours 20 --delay 5 --output-prefix data/custom_data --debug
```

### Command-line Arguments

- `--url`: URL of TripAdvisor page to crawl (default: Hanoi attractions page)
- `--output-prefix`: Prefix for output files (.csv and .json will be added)
- `--max-pages`: Maximum number of pages to crawl (default: 3)
- `--max-tours`: Maximum number of items to crawl (default: unlimited)
- `--delay`: Minimum delay between requests in seconds (default: 3.0)
- `--debug`: Enable debug logging

## Example Output

```json
{
  "name": "Ninh Binh Full Day Tour From Hanoi",
  "location": "Hanoi, Vietnam",
  "coordinates": {
    "latitude": 21.0278,
    "longitude": 105.8342
  },
  "category": "nature, cultural",
  "activities": ["sightseeing", "boat ride", "temple visit", "hiking"],
  "recommended_duration": "12 hours",
  "departure_and_return": "Departure: Your hotel in Hanoi Old Quarter. Return: Returns to original departure point",
  "average_cost": "$35",
  "suitable_for": "couples, families, groups",
  "user_rating": "4.5/5",
  "image_url": "https://media-cdn.tripadvisor.com/media/attractions-splice-spp-720x480/...",
  "image_urls": [
    "https://media-cdn.tripadvisor.com/media/attractions-splice-spp-720x480/..."
  ],
  "description": "Escape from bustling big city in a full day. Visit Rural life & quiet places in Ninh Binh...",
  "weather_type": "sunny, dry",
  "tags": ["nature", "cultural", "photography", "history"],
  "nearby_attractions": ["Tam Coc", "Trang An", "Bai Dinh Pagoda"],
  "comments": [
    {
      "commenter": "John D",
      "rating": 5.0,
      "title": "Amazing day trip!",
      "text": "This tour was the highlight of our Vietnam trip. Our guide was knowledgeable and fun...",
      "date": "February 2025"
    },
    {
      "commenter": "Maria S",
      "rating": 4.0,
      "title": "Great sights but long drive",
      "text": "Beautiful landscape and impressive temples. The drive from Hanoi is quite long...",
      "date": "January 2025"
    }
  ]
}
```

## Notes

- The crawler implements a random delay between requests to avoid being blocked
- It can handle various TripAdvisor page layouts and selectors
- Image URLs are processed to get the highest quality available
- Weather information is extracted from descriptions or inferred based on location
- The crawler respects robots.txt and implements ethical web scraping practices

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Always respect TripAdvisor's terms of service and robots.txt when using this crawler. Rate limits are implemented to avoid overloading their servers.
