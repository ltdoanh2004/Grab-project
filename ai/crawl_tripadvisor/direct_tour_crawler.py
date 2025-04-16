#!/usr/bin/env python3
"""
TripAdvisor Direct Tour Crawler - Scrapes specific tour URLs directly
"""

import time
import re
import csv
import os
import json
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectTourCrawler:
    def __init__(self, delay=3, headless=True):
        self.min_delay = delay
        self.max_delay = delay * 2
        self.headless = headless
        self.driver = None
        
    def _setup_driver(self):
        """Set up the Selenium WebDriver"""
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
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
            
    def get_tour_details(self, tour_url):
        """Get detailed information about a tour from its URL"""
        try:
            self._ensure_driver()
            self._random_delay()
            
            logger.info(f"Fetching tour details from: {tour_url}")
            self.driver.get(tour_url)
            
            # Wait for page to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
            except TimeoutException:
                logger.error(f"Timeout waiting for page to load: {tour_url}")
                self.driver.save_screenshot("timeout.png")
                return {"url": tour_url, "error": "Timeout loading page"}
            
            # Check for captcha
            if "captcha" in self.driver.page_source.lower() or "robot" in self.driver.title.lower():
                logger.error("Captcha detected!")
                self.driver.save_screenshot("captcha.png")
                return {"url": tour_url, "error": "Captcha detected"}
            
            # Initialize tour details
            tour_details = {"url": tour_url}
            
            # Extract name
            try:
                tour_details["name"] = self.driver.find_element(By.TAG_NAME, "h1").text.strip()
            except:
                logger.warning("Could not extract tour name")
            
            # Extract rating
            try:
                # First try bubble rating
                rating_elem = self.driver.find_element(By.CSS_SELECTOR, "div.kGXli span.dLNKG, div.pZUbB span.ui_bubble_rating")
                rating_class = rating_elem.get_attribute("class")
                rating_match = re.search(r'bubble_(\d+)', rating_class)
                if rating_match:
                    tour_details["rating"] = float(rating_match.group(1)) / 10
                else:
                    # Try alternative rating format
                    rating_text = self.driver.find_element(By.CSS_SELECTOR, "div.pZUbB div.fiUbA").text.strip()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        tour_details["rating"] = float(rating_match.group(1))
            except:
                logger.warning("Could not extract rating")
                
                # Try to extract from the page source
                rating_match = re.search(r'"rating"\s*:\s*"?(\d+\.?\d*)"?', self.driver.page_source)
                if rating_match:
                    tour_details["rating"] = float(rating_match.group(1))
            
            # Extract review count
            try:
                reviews_elem = self.driver.find_element(By.CSS_SELECTOR, "div.pZUbB span.JXHJF, div.pZUbB div.AfQtZ, div.pZUbB a.erVKP")
                reviews_text = reviews_elem.text.strip()
                reviews_match = re.search(r'([\d,]+)\s*reviews?', reviews_text)
                if reviews_match:
                    tour_details["number_of_reviews"] = int(reviews_match.group(1).replace(',', ''))
            except:
                logger.warning("Could not extract review count")
                
                # Try to extract from the page source
                reviews_match = re.search(r'"reviewCount"\s*:\s*"?(\d+)"?', self.driver.page_source)
                if reviews_match:
                    tour_details["number_of_reviews"] = int(reviews_match.group(1))
            
            # Extract price information
            try:
                price_elem = self.driver.find_element(By.CSS_SELECTOR, "div.xucHU, div.JWWVK, div.D4eLa")
                price_text = price_elem.text.strip()
                price_match = re.search(r'[$€£¥](\d+(?:,\d+)*(?:\.\d+)?)', price_text)
                if price_match:
                    tour_details["price"] = price_match.group(1).replace(',', '')
                    tour_details["currency"] = price_text[0]  # First character is the currency symbol
                    tour_details["price_level"] = "$" * (1 + int(float(tour_details["price"]) / 50))  # Estimate price level
            except:
                logger.warning("Could not extract price")
                
                # Try to extract from the page source
                price_match = re.search(r'"price"\s*:\s*"?[$€£¥]?(\d+(?:,\d+)*(?:\.\d+)?)"?', self.driver.page_source)
                if price_match:
                    tour_details["price"] = price_match.group(1).replace(',', '')
                    
                    # Try to find currency
                    currency_match = re.search(r'"currencySymbol"\s*:\s*"([$€£¥])"', self.driver.page_source)
                    if currency_match:
                        tour_details["currency"] = currency_match.group(1)
            
            # Extract duration
            try:
                duration_elem = self.driver.find_element(By.CSS_SELECTOR, "div.GEcgY, div.duration, div.eZrke")
                tour_details["recommended_duration"] = duration_elem.text.strip()
            except:
                logger.warning("Could not extract duration")
                
                # Try to extract from the page source
                duration_match = re.search(r'"duration"\s*:\s*"([^"]+)"', self.driver.page_source)
                if duration_match:
                    tour_details["recommended_duration"] = duration_match.group(1)
            
            # Extract cancellation policy
            try:
                cancellation_elem = self.driver.find_element(By.CSS_SELECTOR, "div.EFVJP, div[data-automation='cancellationSummary']")
                tour_details["cancellation_policy"] = cancellation_elem.text.strip()
            except:
                logger.warning("Could not extract cancellation policy")
            
            # Extract location/addresses
            try:
                location_elem = self.driver.find_element(By.CSS_SELECTOR, "div.XPUSn, div.eLcJE button")
                tour_details["location"] = location_elem.text.strip()
            except:
                logger.warning("Could not extract location information")
            
            # Extract coordinates (from page source)
            lat_match = re.search(r'"latitude"\s*:\s*(-?\d+\.\d+)', self.driver.page_source)
            lng_match = re.search(r'"longitude"\s*:\s*(-?\d+\.\d+)', self.driver.page_source)
            
            if lat_match and lng_match:
                tour_details["latitude"] = float(lat_match.group(1))
                tour_details["longitude"] = float(lng_match.group(1))
            
            # Extract description
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, "div.TnInx, div.LbOUx, div.JYHYH")
                tour_details["description"] = desc_elem.text.strip()
            except:
                logger.warning("Could not extract description")
            
            # Extract image URL
            try:
                img_elem = self.driver.find_element(By.CSS_SELECTOR, "div.UCacc img, div.HRZla img, img.MVYCC, picture img")
                tour_details["image_url"] = img_elem.get_attribute("src")
            except:
                logger.warning("Could not extract image URL")
                
                # Try to extract from the page source
                img_match = re.search(r'"image"\s*:\s*"([^"]+)"', self.driver.page_source)
                if img_match:
                    tour_details["image_url"] = img_match.group(1)
            
            # Extract tour operator info
            try:
                operator_elem = self.driver.find_element(By.CSS_SELECTOR, "div.SFCLR, div.cQdcY, div.cNFlb")
                tour_details["operator"] = operator_elem.text.strip()
            except:
                logger.warning("Could not extract tour operator information")
            
            # Extract languages
            try:
                language_section = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Languages Offered')]/following-sibling::div")
                languages = language_section.text.strip().split(',')
                tour_details["languages_offered"] = [lang.strip() for lang in languages if lang.strip()]
            except:
                logger.warning("Could not extract languages offered")
            
            # Extract tour highlights
            try:
                highlight_elems = self.driver.find_elements(By.CSS_SELECTOR, "div.WdBcE, div.JXkIz li")
                if highlight_elems:
                    tour_details["highlights"] = [elem.text.strip() for elem in highlight_elems if elem.text.strip()]
            except:
                logger.warning("Could not extract tour highlights")
            
            # Extract "Includes" section
            try:
                includes_elems = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Includes') or contains(text(), 'included')]/following-sibling::ul/li")
                if includes_elems:
                    tour_details["includes"] = [elem.text.strip() for elem in includes_elems if elem.text.strip()]
            except:
                logger.warning("Could not extract includes information")
            
            # Extract "Excludes" section
            try:
                excludes_elems = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Excludes') or contains(text(), 'Not included')]/following-sibling::ul/li")
                if excludes_elems:
                    tour_details["excludes"] = [elem.text.strip() for elem in excludes_elems if elem.text.strip()]
            except:
                logger.warning("Could not extract excludes information")
            
            # Set category
            tour_details["category"] = "Tours"
            
            # Extract additional details that might be useful
            try:
                additional_details = {}
                detail_elems = self.driver.find_elements(By.CSS_SELECTOR, "div.jemSU div.keSJe, div.pZUbB div.hpZJn")
                
                for elem in detail_elems:
                    text = elem.text.strip()
                    if ":" in text:
                        key, value = text.split(":", 1)
                        additional_details[key.strip().lower().replace(" ", "_")] = value.strip()
                
                # Add valid additional details
                for key, value in additional_details.items():
                    if value and key not in tour_details:
                        tour_details[key] = value
            except:
                logger.warning("Could not extract additional details")
            
            # Extract review quotes
            try:
                review_elems = self.driver.find_elements(By.CSS_SELECTOR, "div.review-container p.partial_entry, div.KOcvS div.NejBf")[:3]
                if review_elems:
                    tour_details["review_summary"] = " | ".join([elem.text.strip() for elem in review_elems if elem.text.strip()])
            except:
                logger.warning("Could not extract review summaries")
            
            return tour_details
            
        except Exception as e:
            logger.error(f"Error extracting tour details: {e}")
            return {"url": tour_url, "error": str(e)}
    
    def scrape_specific_tours(self, urls, output_file=None, output_json=None):
        """Scrape specific tour URLs"""
        try:
            self._ensure_driver()
            
            # List of tour details
            tour_details = []
            
            # Process each URL
            for i, url in enumerate(urls):
                logger.info(f"Processing tour {i+1}/{len(urls)}")
                details = self.get_tour_details(url)
                tour_details.append(details)
            
            # Save to CSV if requested
            if output_file:
                self.save_to_csv(tour_details, output_file)
                
            # Save to JSON if requested
            if output_json:
                self.save_to_json(tour_details, output_json)
                
            return tour_details
            
        finally:
            self._quit_driver()
    
    def save_to_csv(self, data, filename):
        """Save data to CSV file"""
        if not data:
            logger.warning("No data to save")
            return
            
        # Get all possible keys
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
            
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
            writer.writeheader()
            
            # Process data (convert lists to strings)
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
    
    def save_to_json(self, data, filename):
        """Save data to JSON file"""
        if not data:
            logger.warning("No data to save")
            return
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Data saved to {filename}")
            
# List of specific tour URLs to scrape (from the image)
TOUR_URLS = [
    "https://www.tripadvisor.com/AttractionProductReview-g293924-d11988179-Ninh_Binh_Day_Tour_To_Visit_Hoa_Lu_Trang_An_Tam_Coc_Mua_Cave-Hanoi.html",
    "https://www.tripadvisor.com/AttractionProductReview-g293924-d14781418-Ninh_Binh_Full_Day_Tour_from_Hanoi_to_Hoa_Lu_Tam_Coc_Mua_Cave_Via_Boat_Bike-Hanoi.html"
]

if __name__ == "__main__":
    # Set up output directories
    os.makedirs('data', exist_ok=True)
    
    # Initialize the crawler
    crawler = DirectTourCrawler(delay=3, headless=False)
    
    # Scrape the tours
    logger.info(f"Starting to scrape {len(TOUR_URLS)} specific tours")
    tour_data = crawler.scrape_specific_tours(
        TOUR_URLS,
        output_file="data/ninh_binh_tours.csv",
        output_json="data/ninh_binh_tours.json"
    )
    
    logger.info(f"Completed scraping {len(tour_data)} tours")
    
    # Print out sample of the data
    if tour_data:
        logger.info("\nSample tour data:")
        sample_tour = tour_data[0]
        for key in ['name', 'rating', 'price', 'currency', 'recommended_duration', 'cancellation_policy']:
            if key in sample_tour:
                logger.info(f"{key}: {sample_tour[key]}")
                
        logger.info("\nAll extracted fields:")
        logger.info(", ".join(sorted(sample_tour.keys()))) 