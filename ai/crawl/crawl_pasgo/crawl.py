#!/usr/bin/env python3
"""
PasGo Restaurant Crawler
A specialized crawler that extracts clean, structured restaurant details from PasGo.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
import random
import re
import logging
from urllib.parse import urljoin
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# --------------------------- LOGGING --------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pasgo_crawler.log")
    ]
)
logger = logging.getLogger(__name__)

class PasGoCrawler:
    """Crawler for PasGo restaurants with data extraction"""

    def __init__(self, base_url=None, delay=3.0, save_interval=15):
        self.base_url = base_url or "https://pasgo.vn/tim-kiem?search="
        self.min_delay = delay
        self.max_delay = delay * 2
        self.save_interval = save_interval  # Minutes between saves
        self.last_save_time = time.time()
        self.headers = {
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/123.0.0.0 Safari/537.36'),
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://pasgo.vn/'
        }
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _random_delay(self):
        """Add a random delay between requests to avoid being blocked"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.info(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)

    def _should_save(self):
        """Check if it's time to save data"""
        minutes_since_last_save = (time.time() - self.last_save_time) / 60
        return minutes_since_last_save >= self.save_interval

    def save_data(self, data, output_dir, location):
        """Save data to a new file with timestamp and index"""
        if not data:
            logger.warning("No data to save")
            return

        # Create location-specific directory
        location_dir = os.path.join(output_dir, location)
        os.makedirs(location_dir, exist_ok=True)

        # Find the next available index
        index = 0
        while True:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(location_dir, f'restaurants_{timestamp}_index_{index}.json')
            if not os.path.exists(filename):
                break
            index += 1

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(data)} restaurants to {filename}")
            self.last_save_time = time.time()
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {str(e)}")
            # Create error backup
            error_backup = f"error_backup_{int(time.time())}.json"
            try:
                with open(error_backup, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Created error backup at {error_backup}")
            except Exception as backup_error:
                logger.error(f"Failed to create error backup: {str(backup_error)}")

    def get_soup(self, url, retries=3):
        """Get BeautifulSoup object from URL with retries"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching URL: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Check if we got a captcha page
                if "captcha" in response.text.lower() or "please enable js" in response.text.lower():
                    logger.warning("Captcha detected! Try using a different approach or wait longer between requests")
                    if attempt < retries - 1:
                        wait_time = (attempt + 1) * 60  # Incremental backoff
                        logger.info(f"Retrying after {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching URL {url}: {e}")
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 30
                    logger.info(f"Retrying after {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
        return None

    def get_restaurant_listings(self, page=1):
        """Get restaurant listings from a page"""
        self._random_delay()
        
        current_url = f"{self.base_url}&page={page}"
        soup = self.get_soup(current_url)
        if not soup:
            return [], False

        restaurants = []
        
        # Find restaurant listings - adjust selectors based on actual HTML structure
        listings = soup.select('div.restaurant-item')  # Adjust this selector
        
        for listing in listings:
            try:
                # Extract restaurant details - adjust selectors based on actual HTML structure
                name = listing.select_one('h3.restaurant-name').text.strip()  # Adjust selector
                url = listing.select_one('a.restaurant-link')['href']  # Adjust selector
                
                if not url.startswith('http'):
                    url = urljoin("https://pasgo.vn", url)
                
                if url in self.visited_urls:
                    continue
                    
                restaurants.append({
                    "name": name,
                    "url": url
                })
                
            except Exception as e:
                logger.error(f"Error parsing restaurant listing: {e}")
                continue

        # Check for next page
        next_page = soup.select_one('a.next-page')  # Adjust selector
        has_next_page = bool(next_page)
        
        return restaurants, has_next_page

    def get_restaurant_details(self, restaurant_url):
        """Get detailed information about a restaurant"""
        self._random_delay()
        
        soup = self.get_soup(restaurant_url)
        if not soup:
            return {"url": restaurant_url, "error": "Failed to fetch restaurant page"}
            
        details = {
            "url": restaurant_url
        }
        
        try:
            # Extract name
            name = soup.select_one('h1.restaurant-title')  # Adjust selector
            if name:
                details["name"] = name.text.strip()
            
            # Extract address
            address = soup.select_one('div.restaurant-address')  # Adjust selector
            if address:
                details["address"] = address.text.strip()
            
            # Extract description
            description = soup.select_one('div.restaurant-description')  # Adjust selector
            if description:
                details["description"] = description.text.strip()
            
            # Extract opening hours
            hours = soup.select_one('div.opening-hours')  # Adjust selector
            if hours:
                details["opening_hours"] = hours.text.strip()
            
            # Extract price range
            price = soup.select_one('div.price-range')  # Adjust selector
            if price:
                details["price_range"] = price.text.strip()
            
            # Extract rating
            rating = soup.select_one('div.rating')  # Adjust selector
            if rating:
                details["rating"] = rating.text.strip()
            
            # Extract images
            images = []
            for img in soup.select('div.restaurant-images img'):  # Adjust selector
                if img.get('src'):
                    img_url = img['src']
                    if not img_url.startswith('http'):
                        img_url = urljoin("https://pasgo.vn", img_url)
                    images.append(img_url)
            
            if images:
                details["image_urls"] = images
                details["main_image"] = images[0]
            
            # Extract cuisine type
            cuisine = soup.select_one('div.cuisine-type')  # Adjust selector
            if cuisine:
                details["cuisine"] = cuisine.text.strip()
            
            # Extract features/amenities
            features = []
            for feature in soup.select('div.features li'):  # Adjust selector
                features.append(feature.text.strip())
            if features:
                details["features"] = features
            
        except Exception as e:
            logger.error(f"Error parsing restaurant details for {restaurant_url}: {e}")
            details["error"] = str(e)
            
        return details

    def crawl_restaurants(self, max_pages=3, max_restaurants=None, threads=4, start_page=1, output_dir="data_restaurants", location="hanoi"):
        all_listings, page, more = [], start_page, True
        detailed = []
        
        logger.info(f"Starting crawl from page {start_page} with max_pages={max_pages}, max_restaurants={max_restaurants}")
        
        # First, collect all listings
        while more and (page - start_page + 1) <= max_pages:
            logger.info(f"Crawling page {page}")
            lst, more = self.get_restaurant_listings(page=page)
            logger.info(f"Found {len(lst)} restaurants on page {page}")
            
            if not lst:
                logger.warning(f"No restaurants found on page {page}, stopping listing collection")
                break
                
            all_listings.extend(lst)
            if max_restaurants and len(all_listings) >= max_restaurants:
                logger.info(f"Reached max_restaurants limit ({max_restaurants})")
                all_listings = all_listings[:max_restaurants]
                break
                
            page += 1
            self._random_delay()

        if not all_listings:
            logger.warning("No restaurant listings found.")
            return detailed

        logger.info(f"Starting to crawl details for {len(all_listings)} restaurants")
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_map = {executor.submit(self.get_restaurant_details, it["url"]): it for it in all_listings}
            for fut in as_completed(future_map):
                it = future_map[fut]
                try:
                    det = fut.result()
                    if "error" in det:
                        logger.warning(f"Error getting details for {it['url']}: {det['error']}")
                        continue
                    if det["url"] in self.visited_urls:
                        logger.info(f"Skipping duplicate: {det['name']}")
                        continue
                    self.visited_urls.add(det["url"])
                    detailed.append({**it, **det})
                    logger.info(f"✓ {det.get('name')}")
                    
                    # Save periodically
                    if self._should_save():
                        self.save_data(detailed, output_dir, location)
                        
                except Exception as e:
                    logger.error(f"{e} – {it['url']}")

        # Final save
        self.save_data(detailed, output_dir, location)
        logger.info(f"Found {len(detailed)} unique restaurants")
        return detailed

# ----------------------------- CLI ----------------------------- #
def main():
    parser = argparse.ArgumentParser(description='PasGo Restaurant Crawler')
    parser.add_argument('--url', type=str, default="https://pasgo.vn/tim-kiem?search=",
                      help='URL to crawl')
    parser.add_argument('--max-pages', type=int, default=3,
                      help='Maximum number of pages to crawl')
    parser.add_argument('--start-page', type=int, default=1,
                      help='Page number to start crawling from')
    parser.add_argument('--max-restaurants', type=int,
                      help='Maximum number of restaurants to crawl')
    parser.add_argument('--delay', type=float, default=4.0,
                      help='Delay between requests in seconds')
    parser.add_argument('--threads', type=int, default=4,
                      help='Number of concurrent threads')
    parser.add_argument('--output-dir', default='data_restaurants',
                      help='Output directory for JSON files')
    parser.add_argument('--location', default='hanoi',
                      help='Location name for organizing files')
    parser.add_argument('--save-interval', type=int, default=15,
                      help='Minutes between periodic saves (default: 15)')
    args = parser.parse_args()

    crawler = PasGoCrawler(
        base_url=args.url,
        delay=args.delay,
        save_interval=args.save_interval
    )
    
    crawler.crawl_restaurants(
        max_pages=args.max_pages,
        start_page=args.start_page,
        max_restaurants=args.max_restaurants,
        threads=args.threads,
        output_dir=args.output_dir,
        location=args.location
    )

if __name__ == "__main__":
    main()