# Foody.vn Restaurant Crawler

This is a Python-based web crawler for extracting restaurant data from Foody.vn using Playwright.

## Features

- Crawls restaurant data including:
  - Name
  - Address
  - Rating
  - Price range
  - Categories
  - Opening hours
  - Images
- Saves data in JSON format
- Implements rate limiting and random delays to avoid detection
- Logs crawling progress and errors

## Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:

```bash
playwright install
```

## Usage

Run the crawler:

```bash
python foody_crawler.py
```

The crawler will:

1. Create a `data` directory to store the results
2. Crawl restaurants from Foody.vn
3. Save each restaurant's data as a separate JSON file
4. Log progress to `foody_crawler.log`

## Configuration

You can modify the following parameters in `foody_crawler.py`:

- `max_pages`: Number of pages to crawl (default: 5)
- `base_url`: Base URL for crawling (default: "https://www.foody.vn")
- `output_dir`: Directory to save the data (default: "data")

## Output Format

Each restaurant's data is saved as a JSON file with the following structure:

```json
{
    "name": "Restaurant Name",
    "address": "Restaurant Address",
    "rating": "Rating",
    "price_range": "Price Range",
    "categories": ["Category1", "Category2", ...],
    "opening_hours": "Opening Hours",
    "images": ["image_url1", "image_url2", ...],
    "url": "Restaurant URL",
    "crawled_at": "Timestamp"
}
```
