# TripAdvisor Tour Crawler

This is a specialized crawler for extracting detailed information about tours from TripAdvisor.

## Overview

The TripAdvisor Tour Crawler is designed to extract comprehensive data about tours, including:

- Basic information (name, description, price)
- Geographic data (location, coordinates)
- Reviews and ratings
- Tour details (duration, inclusions, cancellation policy)
- Media (images)
- And many more attributes

## Features

- **Multiple Extraction Methods**:

  - Direct web scraping with Selenium for dynamic content
  - Fallback extraction from structured data in page source
  - Manual extraction from screenshots/images when web access is limited

- **Rich Data Structure**:

  - Comprehensive tour details with 20+ attributes
  - Location information with coordinates
  - Review data and recommendations
  - Price and booking details

- **Robust Error Handling**:
  - Timeouts and retry logic
  - Captcha detection
  - Multiple selector strategies for resilience against site changes

## Components

This package includes three different crawlers, each suited for different scenarios:

1. **tour_crawler.py** - Generic tour category crawler that:

   - Extracts tour listings from category pages
   - Gets detailed information for each tour
   - Saves data in both CSV and JSON formats

2. **direct_tour_crawler.py** - Crawler for specific tour URLs:

   - Takes direct URLs to tour pages
   - Extracts all available details
   - More reliable for focused extraction

3. **extract_from_image.py** - Data extraction from screenshots:
   - Extracts visible data from TripAdvisor screenshots
   - Provides a fallback when direct scraping is unavailable
   - Adds inferred data based on tour type and location

## Data Fields

The crawler extracts a comprehensive set of attributes:

1. **name** - Tour name
2. **category** / **subcategory** - Tour type (e.g., "Tours"/"Limousine Tours")
3. **location** - Starting location or area covered
4. **latitude** / **longitude** - Geographic coordinates
5. **rating** - Average user rating (e.g., 4.9/5.0)
6. **number_of_reviews** - Total review count
7. **price** - Tour cost
8. **currency** - Price currency symbol
9. **price_level** - Price category (e.g., $$)
10. **recommended_duration** - Tour length (e.g., "6+ hours")
11. **description** - Tour description
12. **cancellation_policy** - Cancellation terms
13. **recommended_by** - Traveler recommendation percentage
14. **image_url** - Main tour image
15. **suitable_for** - Target audience demographics
16. **activities** - Activities included in the tour
17. **destinations** - Places visited during the tour
18. **includes** - What's included in the price
19. **review_summary** - Highlights from user reviews
20. **operator** - Tour company
21. **languages_offered** - Available languages
22. **tags** - Descriptive tags

## Usage

### General Tour Crawler

```bash
python tour_crawler.py --url "https://www.tripadvisor.com/Attractions-g293924-Activities-c42-Hanoi.html" --max 5
```

### Direct Tour Crawler

```bash
python direct_tour_crawler.py
```

This will scrape the predefined list of tour URLs in the script.

### Image-based Extraction

```bash
python extract_from_image.py
```

This will extract tour data from the information visible in the provided image.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Notes

- TripAdvisor frequently changes its website structure, which may require updating the CSS selectors.
- Use reasonable delays between requests to avoid being blocked.
- Respect TripAdvisor's terms of service when using this crawler.
