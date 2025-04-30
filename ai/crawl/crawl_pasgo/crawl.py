#!/usr/bin/env python3
"""
PasGo Restaurant Crawler
A specialized crawler that extracts clean, structured restaurant details from PasGo using undetected-chromedriver.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
    """Crawler for PasGo restaurants with data extraction using undetected-chromedriver"""

    def __init__(self, base_url=None, delay=1.0, save_interval=15):
        self.base_url = base_url or "https://pasgo.vn/ha-noi/nha-hang"
        self.min_delay = delay
        self.max_delay = delay * 1.5
        self.save_interval = save_interval
        self.last_save_time = time.time()
        self.visited_urls = set()
        
        # Initialize Chrome options
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Initialize the driver
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass

    def get_soup(self, url, retries=2):
        """Get BeautifulSoup object from URL using undetected-chromedriver"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching URL: {url} (attempt {attempt + 1}/{retries})")
                
                # Load the page
                self.driver.get(url)
                
                # Wait for the main content to load
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.restaurant-item, .item, .boxed-main-items')))
                except TimeoutException:
                    logger.warning(f"Timeout waiting for content on {url}")
                
                # Get the rendered page source
                page_source = self.driver.page_source
                
                # Print first part of HTML for debugging
                print("=== HTML Content ===")
                print(page_source[:2000])
                print("===================")
                
                return BeautifulSoup(page_source, 'html.parser')
                
            except Exception as e:
                logger.error(f"Error fetching URL {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                else:
                    return None

    def get_restaurant_listings(self, page=1):
        """Get restaurant listings from a page"""
        self._random_delay()
        
        # Use the correct pagination format
        url = f"{self.base_url}?page={page-1}" if page > 1 else self.base_url
        soup = self.get_soup(url)
        if not soup:
            return [], False

        restaurants = []
        
        # Try different selectors for listings
        selectors = [
            ".restaurant-item",                # Main listing selector
            ".item",                          # Alternative listing selector
            ".boxed-main-items .items",       # Another possible selector
            ".list-restaurant .item",         # Backup selector
            ".restaurant-list .item"          # Last resort selector
        ]
        
        # Wait for listings to be visible in the browser
        listings = None
        for selector in selectors:
            try:
                elements = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                if elements:
                    listings = [BeautifulSoup(el.get_attribute('outerHTML'), 'html.parser') for el in elements]
                    logger.info(f"Found {len(listings)} listings with selector: {selector}")
                    break
            except TimeoutException:
                continue
                
        if not listings:
            logger.warning("No listings found with any selector")
            return [], False

        for listing in listings:
            try:
                # Try different name selectors
                name_selectors = [
                    '.item-child-headline',    # Main name selector
                    '.title',                  # Alternative name selector
                    'h3',                      # Another name selector
                    'h3 a',                    # Backup name selector
                    'a[title]'                 # Last resort name selector
                ]
                
                name = None
                for selector in name_selectors:
                    name_tag = listing.select_one(selector)
                    if name_tag:
                        name = name_tag.text.strip()
                        if not name and name_tag.has_attr('title'):
                            name = name_tag['title'].strip()
                        if name:
                            logger.info(f"Found name with selector {selector}: {name}")
                            break
                
                # Try different URL selectors
                url_selectors = [
                    'a[href*="/nha-hang/"]',   # Main URL selector
                    '.item-link-desc',         # Alternative URL selector
                    'h3 a[href]',              # Another URL selector
                    'a[href]',                 # Backup URL selector
                    'a'                        # Last resort URL selector
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
                    
                # Extract additional information
                try:
                    # Get restaurant image
                    img_tag = listing.select_one('img[src*="restaurant"], img[data-src*="restaurant"], img.lazy')
                    image_url = None
                    if img_tag:
                        image_url = img_tag.get('data-src') or img_tag.get('src')
                        if image_url and not image_url.startswith('http'):
                            image_url = urljoin("https://pasgo.vn", image_url)
                    
                    # Get restaurant address
                    address_tag = listing.select_one('.address, .item-address, .restaurant-address')
                    address = address_tag.text.strip() if address_tag else None
                    
                    # Get rating if available
                    rating_tag = listing.select_one('.rating, .rating-score, .score')
                    rating = rating_tag.text.strip() if rating_tag else None
                    
                    # Get price range if available
                    price_tag = listing.select_one('.price, .price-range, .item-price')
                    price_range = price_tag.text.strip() if price_tag else None
                    
                except Exception as e:
                    logger.warning(f"Error extracting additional details: {e}")
                    image_url = address = rating = price_range = None
                
                restaurants.append({
                    "name": name,
                    "url": url,
                    "image_url": image_url,
                    "address": address,
                    "rating": rating,
                    "price_range": price_range
                })
                
            except Exception as e:
                logger.error(f"Error parsing restaurant listing: {e}")
                continue

        # Check for next page
        next_page_selectors = [
            '.pagination .next',           # Main next page selector
            'a.next',                      # Alternative next page selector
            '.pagination a[rel="next"]'    # Another next page selector
        ]
        
        has_next = False
        for selector in next_page_selectors:
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                has_next = next_button.is_displayed()
                if has_next:
                    break
            except NoSuchElementException:
                continue

        return restaurants, has_next

    def get_restaurant_details(self, restaurant_url):
        """Get detailed information about a restaurant"""
        self._random_delay()
        
        soup = self.get_soup(restaurant_url)
        if not soup:
            return None
            
        try:
            # Wait for main content to load
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.restaurant-detail, .restaurant-info')))
            except TimeoutException:
                logger.warning(f"Timeout waiting for restaurant details on {restaurant_url}")
            
            # Extract restaurant details
            details = {}
            
            # Basic information
            name_tag = soup.select_one('.restaurant-name, h1.name, .detail-name')
            details['name'] = name_tag.text.strip() if name_tag else None
            
            address_tag = soup.select_one('.restaurant-address, .detail-address, .address')
            details['address'] = address_tag.text.strip() if address_tag else None
            
            # Contact information
            phone_tag = soup.select_one('.phone, .contact-phone, .restaurant-phone')
            details['phone'] = phone_tag.text.strip() if phone_tag else None
            
            # Opening hours
            hours_tag = soup.select_one('.opening-hours, .business-hours, .restaurant-hours')
            details['opening_hours'] = hours_tag.text.strip() if hours_tag else None
            
            # Price range
            price_tag = soup.select_one('.price-range, .restaurant-price, .price')
            details['price_range'] = price_tag.text.strip() if price_tag else None
            
            # Cuisine types
            cuisine_tags = soup.select('.cuisine-type, .restaurant-cuisine, .cuisine')
            details['cuisines'] = [tag.text.strip() for tag in cuisine_tags] if cuisine_tags else []
            
            # Features/Facilities
            feature_tags = soup.select('.features span, .facilities span, .amenities span')
            details['features'] = [tag.text.strip() for tag in feature_tags] if feature_tags else []
            
            # Images
            image_tags = soup.select('img.restaurant-image, .gallery img, .restaurant-photos img')
            details['images'] = []
            for img in image_tags:
                src = img.get('data-src') or img.get('src')
                if src:
                    if not src.startswith('http'):
                        src = urljoin("https://pasgo.vn", src)
                    details['images'].append(src)
            
            # Description
            desc_tag = soup.select_one('.restaurant-description, .detail-description, .description')
            details['description'] = desc_tag.text.strip() if desc_tag else None
            
            # Rating information
            rating_tag = soup.select_one('.rating-score, .restaurant-rating, .rating')
            details['rating'] = rating_tag.text.strip() if rating_tag else None
            
            # Number of reviews
            reviews_tag = soup.select_one('.review-count, .total-reviews, .reviews-count')
            details['review_count'] = reviews_tag.text.strip() if reviews_tag else None
            
            # Location coordinates (if available)
            map_div = soup.select_one('#restaurant-map, .restaurant-map, .map-container')
            if map_div:
                lat = map_div.get('data-lat') or map_div.get('data-latitude')
                lng = map_div.get('data-lng') or map_div.get('data-longitude')
                if lat and lng:
                    details['location'] = {'latitude': lat, 'longitude': lng}
            
            return details
            
        except Exception as e:
            logger.error(f"Error extracting restaurant details from {restaurant_url}: {e}")
            return None

    def _random_delay(self):
        """Add a random delay between requests"""
        delay = random.uniform(self.min_delay, self.max_delay)
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

    def crawl_restaurants(self, max_pages=None, threads=4):
        """Crawl restaurant listings and details with multi-threading"""
        all_restaurants = []
        current_page = 1
        
        try:
            while max_pages is None or current_page <= max_pages:
                logger.info(f"Processing page {current_page}")
                
                restaurants, has_next = self.get_restaurant_listings(current_page)
                
                if not restaurants:
                    logger.warning(f"No restaurants found on page {current_page}. Stopping listing collection.")
                    break
                
                logger.info(f"Found {len(restaurants)} restaurants on page {current_page}")
                
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    future_to_url = {
                        executor.submit(self.get_restaurant_details, restaurant['url']): restaurant
                        for restaurant in restaurants
                    }
                    
                    for future in as_completed(future_to_url):
                        restaurant = future_to_url[future]
                        try:
                            details = future.result()
                            if details:
                                restaurant.update(details)
                                all_restaurants.append(restaurant)
                                self.visited_urls.add(restaurant['url'])
                                
                                if time.time() - self.last_save_time > self.save_interval:
                                    self.save_data(all_restaurants, "data_restaurants", "hanoi")
                                    
                        except Exception as e:
                            logger.error(f"Error processing restaurant {restaurant['url']}: {e}")
                
                if not has_next:
                    logger.info("No more pages available")
                    break
                    
                current_page += 1
                
        except KeyboardInterrupt:
            logger.info("Crawling interrupted by user")
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
        finally:
            # Save final results
            if all_restaurants:
                self.save_data(all_restaurants, "data_restaurants", "hanoi")
            
            # Cleanup
            if hasattr(self, 'driver'):
                self.driver.quit()

def main():
    parser = argparse.ArgumentParser(description='PasGo Restaurant Crawler')
    parser.add_argument('--url', help='Base URL to start crawling from', default="https://pasgo.vn/ha-noi/nha-hang")
    parser.add_argument('--max-pages', type=int, help='Maximum number of pages to crawl (default: unlimited)', default=None)
    parser.add_argument('--threads', type=int, help='Number of threads for parallel processing', default=4)
    parser.add_argument('--delay', type=float, help='Minimum delay between requests in seconds', default=1.0)
    args = parser.parse_args()

    crawler = PasGoCrawler(base_url=args.url, delay=args.delay)
    crawler.crawl_restaurants(max_pages=args.max_pages, threads=args.threads)

if __name__ == "__main__":
    main()