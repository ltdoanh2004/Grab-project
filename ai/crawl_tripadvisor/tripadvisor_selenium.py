#!/usr/bin/env python3
"""
TripAdvisor Crawler using Selenium for handling dynamic content
This is a simplified example focusing on extracting key attributes
"""

import time
import re
import csv
import os
import argparse
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TripAdvisorSeleniumCrawler:
    def __init__(self, delay=2, headless=True):
        self.min_delay = delay
        self.max_delay = delay * 2
        self.headless = headless
        self.driver = None
        
    def _setup_driver(self):
        """Set up the Selenium WebDriver"""
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add realistic user agent
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=options)
        # Set page load timeout
        self.driver.set_page_load_timeout(30)
        
    def _random_delay(self):
        """Add a random delay between requests to avoid being blocked"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.info(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)
    
    def _ensure_driver(self):
        """Ensure driver is initialized"""
        if self.driver is None:
            self._setup_driver()
    
    def _quit_driver(self):
        """Quit the driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def get_entity_details(self, url):
        """Get details for a specific entity using Selenium"""
        try:
            self._ensure_driver()
            self._random_delay()
            
            logger.info(f"Fetching URL: {url}")
            self.driver.get(url)
            
            # Wait for the page to load (look for the title element)
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
            except TimeoutException:
                logger.error(f"Timeout waiting for page to load: {url}")
                # Take a screenshot for debugging
                self.driver.save_screenshot("timeout_error.png")
                return {"url": url, "error": "Timeout waiting for page to load"}
            
            # Get entity type from URL
            entity_type = "attraction"
            if "Hotel_Review" in url:
                entity_type = "hotel"
            elif "Restaurant_Review" in url:
                entity_type = "restaurant"
            elif "Tour_Review" in url:
                entity_type = "tour"
                
            # Check for captcha or bot detection page
            if "captcha" in self.driver.page_source.lower() or "robot" in self.driver.title.lower():
                logger.error("Captcha or bot detection encountered!")
                self.driver.save_screenshot("captcha_detected.png")
                return {"url": url, "error": "Captcha detected"}
            
            # Extract details using various methods
            details = {"url": url, "entity_type": entity_type}
            
            # Extract name
            try:
                name_elem = self.driver.find_element(By.TAG_NAME, "h1")
                details["name"] = name_elem.text.strip()
            except NoSuchElementException:
                logger.warning("Could not find name element")
            
            # Extract category (could be derived from URL or page elements)
            category_mapping = {
                "attraction": "Attractions",
                "hotel": "Hotels",
                "restaurant": "Restaurants",
                "tour": "Tours"
            }
            details["category"] = category_mapping.get(entity_type, "Things To Do")
            
            # Extract location/address
            address_selectors = [
                "button.CEQvT",  # Common address button
                "div.FUHHI span",  # Address in div
                "div.kUaGX button",  # Another address format
                "//button[contains(@data-tab, 'address')]"  # XPath for address tab
            ]
            
            for selector in address_selectors:
                try:
                    if selector.startswith("//"):
                        # This is an XPath selector
                        address_elem = self.driver.find_element(By.XPATH, selector)
                    else:
                        # This is a CSS selector
                        address_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    details["location"] = address_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract coordinates from page source
            page_source = self.driver.page_source
            lat_match = re.search(r'"latitude"\s*:\s*(-?\d+\.\d+)', page_source)
            lng_match = re.search(r'"longitude"\s*:\s*(-?\d+\.\d+)', page_source)
            
            if lat_match and lng_match:
                details["latitude"] = float(lat_match.group(1))
                details["longitude"] = float(lng_match.group(1))
            
            # Extract rating
            try:
                # Look for the bubble rating element
                rating_elem = self.driver.find_element(By.CSS_SELECTOR, "span.ui_bubble_rating")
                rating_class = rating_elem.get_attribute("class")
                rating_match = re.search(r'bubble_(\d+)', rating_class)
                if rating_match:
                    details["rating"] = float(rating_match.group(1)) / 10
            except NoSuchElementException:
                # Try alternative methods
                try:
                    rating_text = self.driver.find_element(By.CSS_SELECTOR, "div.AfQtZ, span.bvcyz").text
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        details["rating"] = float(rating_match.group(1))
                except:
                    pass
            
            # Extract number of reviews
            reviews_selectors = [
                "a.iUttq", "span.jqKwK", "a.UctQk",
                "//a[contains(@href, 'Reviews') and contains(text(), 'review')]"
            ]
            
            for selector in reviews_selectors:
                try:
                    if selector.startswith("//"):
                        reviews_elem = self.driver.find_element(By.XPATH, selector)
                    else:
                        reviews_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    reviews_text = reviews_elem.text
                    reviews_match = re.search(r'([\d,]+)\s*reviews?', reviews_text)
                    if reviews_match:
                        details["number_of_reviews"] = int(reviews_match.group(1).replace(',', ''))
                        break
                except:
                    continue
            
            # Extract price level (for hotels, restaurants)
            if entity_type in ["hotel", "restaurant"]:
                price_selectors = [
                    "div.DgQyR", "div.ceIOZ",  # Price range selectors
                    "//div[contains(@class, 'priceRange')]"  # XPath for price range
                ]
                
                for selector in price_selectors:
                    try:
                        if selector.startswith("//"):
                            price_elem = self.driver.find_element(By.XPATH, selector)
                        else:
                            price_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        price_text = price_elem.text
                        if '$' in price_text:
                            price_match = re.search(r'(\$+)', price_text)
                            if price_match:
                                details["price_level"] = price_match.group(1)
                            break
                    except:
                        continue
            
            # Extract image URL
            try:
                img_elem = self.driver.find_element(By.CSS_SELECTOR, "div.UCacc img, div.HRZla img, div.pZUbB img")
                if img_elem.get_attribute("src"):
                    details["image_url"] = img_elem.get_attribute("src")
            except:
                # Try another approach - look at all images and find one that looks like a main image
                try:
                    # Get images with certain size characteristics or specific classes
                    images = self.driver.find_elements(By.CSS_SELECTOR, "img[width='550'], img.BRCHW, img.gQaWW")
                    if images:
                        details["image_url"] = images[0].get_attribute("src")
                except:
                    pass
            
            # Extract tags and make them a list
            tags = []
            tag_selectors = [
                "div.XPxdY span.WlYyy", "div.EZmvx span.eqXJH",
                "//div[contains(@class, 'tagCloud')]//span"
            ]
            
            for selector in tag_selectors:
                try:
                    if selector.startswith("//"):
                        tag_elems = self.driver.find_elements(By.XPATH, selector)
                    else:
                        tag_elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if tag_elems:
                        tags = [elem.text.strip() for elem in tag_elems if elem.text.strip()]
                        if tags:
                            details["tags"] = tags
                        break
                except:
                    continue
            
            # Based on tags, determine suitable_for
            if tags:
                suitable_for = []
                for tag in tags:
                    tag = tag.lower()
                    if 'family' in tag:
                        suitable_for.append('family')
                    if 'couple' in tag:
                        suitable_for.append('couple')
                    if 'solo' in tag or 'alone' in tag:
                        suitable_for.append('solo')
                    if 'group' in tag:
                        suitable_for.append('group')
                
                if suitable_for:
                    details["suitable_for"] = suitable_for
            
            # Extract rank in city
            rank_selectors = [
                "div.pZUbB div.cNFlb", "div.EEIGK div.cwbXG",
                "//div[contains(text(), '#') and contains(text(), 'of')]"
            ]
            
            for selector in rank_selectors:
                try:
                    if selector.startswith("//"):
                        rank_elem = self.driver.find_element(By.XPATH, selector)
                    else:
                        rank_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    rank_text = rank_elem.text
                    rank_match = re.search(r'#\d+\s+of\s+[\d,]+', rank_text)
                    if rank_match:
                        details["rank_in_city"] = rank_match.group(0)
                        break
                except:
                    continue
            
            # Extract website/contact info
            try:
                website_elem = self.driver.find_element(By.CSS_SELECTOR, "a[href*='website'], a.YnKZo")
                if website_elem:
                    details["website"] = website_elem.get_attribute("href")
            except:
                pass
            
            # Extract opening hours
            try:
                hours_selector = "div.sRVj span, div.JINyA, div.IhqAp"
                hours_elems = self.driver.find_elements(By.CSS_SELECTOR, hours_selector)
                if hours_elems:
                    hours = []
                    for elem in hours_elems:
                        text = elem.text.strip()
                        if re.search(r'(mon|tue|wed|thu|fri|sat|sun|open|close|\d+:\d+|am|pm)', text.lower()):
                            hours.append(text)
                    
                    if hours:
                        details["opening_hours"] = " | ".join(hours)
            except:
                pass
                
            return details
            
        except Exception as e:
            logger.error(f"Error extracting details: {e}")
            return {"url": url, "error": str(e)}
        
    def scrape_entities(self, urls, output_file=None):
        """Scrape multiple entities"""
        results = []
        
        try:
            self._ensure_driver()
            
            for i, url in enumerate(urls):
                logger.info(f"Processing {i+1}/{len(urls)}: {url}")
                entity_details = self.get_entity_details(url)
                results.append(entity_details)
            
            if output_file and results:
                self.save_to_csv(results, output_file)
                
            return results
            
        finally:
            self._quit_driver()
    
    def save_to_csv(self, data, filename):
        """Save data to CSV file"""
        if not data:
            logger.warning("No data to save")
            return
            
        # Get all possible keys from all dictionaries
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
            
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
            writer.writeheader()
            
            # Process special fields like lists before writing
            processed_data = []
            for item in data:
                processed_item = {}
                for key, value in item.items():
                    if isinstance(value, list):
                        processed_item[key] = ", ".join(str(v) for v in value)
                    else:
                        processed_item[key] = value
                processed_data.append(processed_item)
                
            writer.writerows(processed_data)
            
        logger.info(f"Data saved to {filename}")

def parse_arguments():
    parser = argparse.ArgumentParser(description='TripAdvisor Selenium Crawler')
    parser.add_argument('--urls', type=str, nargs='+', 
                        help='URLs of TripAdvisor pages to crawl')
    parser.add_argument('--output', type=str, default='data/tripadvisor_selenium_results.csv',
                        help='Output CSV file name')
    parser.add_argument('--delay', type=float, default=3.0,
                        help='Minimum delay between requests in seconds')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    parser.add_argument('--visible', action='store_true',
                        help='Make browser visible (non-headless mode)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Set debug level if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Default URLs if none provided
    if not args.urls:
        args.urls = [
            "https://www.tripadvisor.com/Attraction_Review-g293924-d317503-Reviews-Old_Quarter-Hanoi.html",
            "https://www.tripadvisor.com/Hotel_Review-g293924-d301984-Reviews-Sofitel_Legend_Metropole_Hanoi-Hanoi.html",
            "https://www.tripadvisor.com/Restaurant_Review-g293925-d7153258-Reviews-Hum_Vegetarian_Lounge_Restaurant-Ho_Chi_Minh_City.html"
        ]
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    logger.info(f"Crawling {len(args.urls)} TripAdvisor URLs")
    logger.info(f"Will save data to: {args.output}")
    logger.info(f"Delay between requests: {args.delay}-{args.delay*2} seconds")
    logger.info(f"Browser visible: {args.visible}")
    
    # Initialize crawler
    crawler = TripAdvisorSeleniumCrawler(delay=args.delay, headless=not args.visible)
    
    # Start scraping
    results = crawler.scrape_entities(args.urls, output_file=args.output) 