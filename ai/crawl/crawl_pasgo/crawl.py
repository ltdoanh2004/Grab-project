#!/usr/bin/env python3
"""
PasGo Restaurant Crawler
A specialized crawler that extracts clean, structured restaurant details from PasGo.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import json
import time
import os
import random
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

    def __init__(self, base_url=None, delay=1.0, save_interval=15):
        self.base_url = base_url or "https://pasgo.vn/ha-noi/nha-hang"
        self.min_delay = delay
        self.max_delay = delay * 1.5
        self.save_interval = save_interval
        self.last_save_time = time.time()
        self.visited_urls = set()
        
        # Setup undetected-chromedriver
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        try:
            self.driver = uc.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("Undetected ChromeDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromeDriver: {e}")
            raise

    def get_soup(self, url, retries=2):
        """Get BeautifulSoup object from URL using undetected-chromedriver"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching URL: {url} (attempt {attempt + 1}/{retries})")
                self.driver.get(url)
                
                # Wait for content to load
                selectors = [
                    "div.restaurant-list",
                    "div.list-restaurant",
                    "div.restaurant-item",
                    "div.item",
                    "body"  # Fallback
                ]
                
                # Wait for page load
                self.driver.execute_script("return document.readyState") == "complete"
                time.sleep(3)  # Give JavaScript time to render
                
                # Try to find content with different selectors
                content_found = False
                for selector in selectors:
                    try:
                        element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        if element:
                            logger.info(f"Found content with selector: {selector}")
                            content_found = True
                            break
                    except TimeoutException:
                        continue
                
                if not content_found:
                    logger.warning("No content found with any selector")
                    if attempt < retries - 1:
                        continue
                    else:
                        return None
                
                # Get page source and create soup
                page_source = self.driver.page_source
                
                # Print first part of HTML for debugging
                print("=== HTML Content ===")
                print(page_source[:2000])
                print("===================")
                
                soup = BeautifulSoup(page_source, 'html.parser')
                return soup
                
            except Exception as e:
                logger.error(f"Error fetching URL {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                else:
                    return None

    def get_restaurant_listings(self, page=1):
        """Get restaurant listings from a page"""
        self._random_delay()
        
        url = f"{self.base_url}?page={page-1}" if page > 1 else self.base_url
        soup = self.get_soup(url)
        if not soup:
            return [], False

        restaurants = []
        
        # Try different selectors for listings
        selectors = [
            "div.restaurant-list .restaurant-item",
            "div.list-restaurant .item",
            "article.restaurant",
            ".restaurant-box",
            ".restaurant-info"
        ]
        
        listings = None
        for selector in selectors:
            listings = soup.select(selector)
            if listings:
                logger.info(f"Found {len(listings)} listings with selector: {selector}")
                break
                
        if not listings:
            logger.warning("No listings found with any selector")
            return [], False

        for listing in listings:
            try:
                # Try different name selectors
                name_selectors = [
                    'h3.item-child-headline',
                    'h3.title',
                    'h3 a',
                    '.restaurant-name',
                    '.title a',
                    'h3'
                ]
                
                name = None
                for selector in name_selectors:
                    name_tag = listing.select_one(selector)
                    if name_tag:
                        name = name_tag.text.strip()
                        logger.info(f"Found name with selector {selector}: {name}")
                        break
                
                # Try different URL selectors
                url_selectors = [
                    'a.item-link-desc',
                    'a[href*="/nha-hang/"]',
                    'h3 a[href]',
                    '.title a[href]',
                    'a'
                ]
                
                url = None
                for selector in url_selectors:
                    url_tag = listing.select_one(selector)
                    if url_tag and url_tag.has_attr('href'):
                        url = url_tag['href']
                        logger.info(f"Found URL with selector {selector}: {url}")
                        break
                
                if not name or not url:
                    logger.warning(f"Skipping listing - missing name or url: name={name}, url={url}")
                    continue
                    
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
        next_page_selectors = [
            'a.next',
            '.pagination .next',
            'a[rel="next"]',
            '.next-page'
        ]
        
        has_next_page = False
        for selector in next_page_selectors:
            if soup.select_one(selector):
                has_next_page = True
                logger.info(f"Found next page with selector: {selector}")
                break
        
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
            name = soup.select_one('h1.restaurant-title')
            if name:
                details["name"] = name.text.strip()
            
            # Extract address
            address = soup.select_one('div.restaurant-address')
            if address:
                details["address"] = address.text.strip()
            
            # Extract description
            description = soup.select_one('div.restaurant-description')
            if description:
                details["description"] = description.text.strip()
            
            # Extract opening hours
            hours = soup.select_one('div.opening-hours')
            if hours:
                details["opening_hours"] = hours.text.strip()
            
            # Extract price range
            price = soup.select_one('div.price-range')
            if price:
                details["price_range"] = price.text.strip()
            
            # Extract rating
            rating = soup.select_one('div.rating')
            if rating:
                details["rating"] = rating.text.strip()
            
            # Extract images
            images = []
            for img in soup.select('div.restaurant-images img'):
                if img.get('src'):
                    img_url = img['src']
                    if not img_url.startswith('http'):
                        img_url = urljoin("https://pasgo.vn", img_url)
                    images.append(img_url)
            
            if images:
                details["image_urls"] = images
                details["main_image"] = images[0]
            
            # Extract cuisine type
            cuisine = soup.select_one('div.cuisine-type')
            if cuisine:
                details["cuisine"] = cuisine.text.strip()
            
            # Extract features/amenities
            features = []
            for feature in soup.select('div.features li'):
                features.append(feature.text.strip())
            if features:
                details["features"] = features
            
        except Exception as e:
            logger.error(f"Error parsing restaurant details for {restaurant_url}: {e}")
            details["error"] = str(e)
            
        return details

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

        location_dir = os.path.join(output_dir, location)
        os.makedirs(location_dir, exist_ok=True)

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
            error_backup = f"error_backup_{int(time.time())}.json"
            try:
                with open(error_backup, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Created error backup at {error_backup}")
            except Exception as backup_error:
                logger.error(f"Failed to create error backup: {str(backup_error)}")

    def crawl_restaurants(self, max_pages=3, max_restaurants=None, threads=4, start_page=1, output_dir="data_restaurants", location="hanoi"):
        """Crawl restaurant listings and details"""
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

    def __del__(self):
        """Clean up ChromeDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    parser = argparse.ArgumentParser(description='PasGo Restaurant Crawler')
    parser.add_argument('--max-pages', type=int, default=3,
                      help='Maximum number of pages to crawl')
    parser.add_argument('--start-page', type=int, default=1,
                      help='Page number to start crawling from')
    parser.add_argument('--max-restaurants', type=int,
                      help='Maximum number of restaurants to crawl')
    parser.add_argument('--delay', type=float, default=1.0,
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