# TripAdvisor Crawler

An enhanced web crawler for TripAdvisor that collects detailed information about attractions, hotels, restaurants, and tours.

## Features

- Extracts comprehensive data from TripAdvisor listings including:

  - Basic information (name, category, location)
  - Geographical data (latitude/longitude)
  - Ratings and reviews
  - Price levels
  - Recommended duration
  - Opening hours
  - Images
  - And many more attributes

- Supports multiple entity types:

  - Attractions
  - Hotels
  - Restaurants
  - Tours

- Built-in protection mechanisms:
  - Random delays between requests
  - User-agent rotation
  - Error handling and retries
  - Captcha detection

## Installation

```bash
# Clone the repository (if applicable)
git clone <repository_url>
cd <repository_directory>

# Install dependencies
pip install requests beautifulsoup4
```

## Usage

### Basic Usage

```bash
python tripadvisor_crawler.py --url "https://www.tripadvisor.com/Attractions-g293924-Activities-Hanoi.html" --max 5
```

This will scrape 5 attractions from Hanoi and save the data to a CSV file.

### Command Line Arguments

| Argument     | Description                                                              | Default                          |
| ------------ | ------------------------------------------------------------------------ | -------------------------------- |
| `--url`      | URL of the TripAdvisor page to crawl                                     | Hanoi attractions URL            |
| `--output`   | Output CSV file name                                                     | data/tripadvisor_attractions.csv |
| `--max`      | Maximum number of entities to crawl                                      | 2                                |
| `--delay`    | Minimum delay between requests (seconds)                                 | 3.0                              |
| `--debug`    | Enable debug logging                                                     | False                            |
| `--type`     | Type of entities to crawl (attractions, hotels, restaurants, tours, all) | attractions                      |
| `--location` | Location name (e.g., "Hanoi")                                            | Auto-detected from URL           |

### Examples

**Scrape restaurants in Ho Chi Minh City:**

```bash
python tripadvisor_crawler.py --url "https://www.tripadvisor.com/Restaurants-g293925-Ho_Chi_Minh_City.html" --type restaurants --max 10
```

**Scrape hotels with debug logging:**

```bash
python tripadvisor_crawler.py --url "https://www.tripadvisor.com/Hotels-g293924-Hanoi-Hotels.html" --type hotels --debug --max 5
```

**Scrape multiple entity types at once:**

```bash
python tripadvisor_crawler.py --location "Danang" --type all --max 3
```

## Data Fields

The crawler extracts many data points for each entity, depending on availability on the page:

1. **name** - Name of the place, tour, restaurant, or hotel
2. **category** - Type: Attractions / Tours / Restaurants / Hotels / Things To Do
3. **location** - Address or area (city, country, specific neighborhood if available)
4. **latitude** / **longitude** - GPS coordinates for routing calculations
5. **rating** - Average user rating (e.g., 4.5/5)
6. **number_of_reviews** - Total number of reviews
7. **review_summary** - Highlighted reviews from user reviews (good for sentiment analysis/NLP)
8. **price_level** - Price range: $ – $$ – $$$ (for restaurants, hotels, tours)
9. **recommended_duration** - Suggested time to spend at this place (if available)
10. **tags** - Descriptive tags (family-friendly, romantic, hidden gem, etc.)
11. **suitable_for** - Appropriate audience (derived from tags): solo, couple, family, group
12. **opening_hours** - Opening and closing times (may vary by day of week)
13. **image_url** - Link to representative image
14. **activities** - Highlighted activities (from description or tags: hiking, sightseeing, etc.)
15. **website** / **contact_info** - Official website, phone number if available
16. **popular_times** - Peak hours (often seen for restaurants or tourist attractions)
17. **nearby_places** - Places suggested in the "You may also like" section
18. **review_date** - Date of most recent review – to check if data is "fresh"
19. **reviewer_origin** - Nationality of reviewers – useful for understanding suitable audience
20. **rank_in_city** - Ranking in the city (e.g., #5 of 230 Things to Do in Da Nang)

## Testing

Run the test script to verify the crawler is working correctly:

```bash
python test_crawler.py
```

## Notes

- TripAdvisor's website structure changes frequently, which may break the crawler. If you encounter issues, please report them.
- Be respectful of TripAdvisor's servers by using reasonable delays between requests.
- This crawler is for educational purposes only. Please comply with TripAdvisor's terms of service.

## License

[Specify your license here]
