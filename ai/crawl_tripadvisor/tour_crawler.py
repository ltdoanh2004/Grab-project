#!/usr/bin/env python3
"""
TripAdvisor Tour Crawler - Specialized crawler for tour listings
"""

import time
import re
import csv
import os
import json
import argparse
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from urllib.parse import urlparse, urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TourCrawler:
    def __init__(self, delay=3, headless=True):
        self.min_delay = delay
        self.max_delay = delay * 2
        self.headless = headless
        self.driver = None
        self.base_url = "https://www.tripadvisor.com"
        
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
    
    def get_tour_listings(self, url, max_tours=None):
        """Scrape tour listings from a TripAdvisor tour category page"""
        try:
            self._ensure_driver()
            logger.info(f"Fetching tour listings from: {url}")
            self.driver.get(url)
            
            # Wait for listings to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.listing"))
                )
            except TimeoutException:
                logger.error("Timeout waiting for tour listings to load")
                self.driver.save_screenshot("tour_listings_timeout.png")
                return []
            
            # Check for captcha
            if "captcha" in self.driver.page_source.lower() or "robot" in self.driver.title.lower():
                logger.error("Captcha detected. Taking screenshot for debugging.")
                self.driver.save_screenshot("captcha_detected.png")
                return []
            
            # Try multiple selectors for tour listings
            tour_elements = []
            selectors = [
                "div.listing",
                "div.attraction_element",
                "div.attraction_clarity_cell",
                "div._c._s:not(.hidden)",  # Common tour card class
                "//div[contains(@class, 'attraction_element')]"  # XPath alternative
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        tour_elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        tour_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if tour_elements:
                        logger.info(f"Found {len(tour_elements)} tour elements using selector: {selector}")
                        break
                except Exception as e:
                    logger.error(f"Error finding tour elements with selector {selector}: {e}")
            
            if not tour_elements:
                logger.warning("No tour elements found. Taking screenshot for debugging.")
                self.driver.save_screenshot("no_tour_elements.png")
                
                # Try a more generic approach
                logger.info("Trying generic approach to find listings...")
                try:
                    # Look for any links that might be tour listings
                    tour_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='Attraction_Review']")
                    if tour_links:
                        logger.info(f"Found {len(tour_links)} potential tour links")
                        tour_data = []
                        for link in tour_links[:max_tours if max_tours else 10]:
                            href = link.get_attribute("href")
                            if href and "Attraction_Review" in href:
                                tour_data.append({"url": href, "name": link.text.strip() or "Unknown Tour"})
                        return tour_data
                except Exception as e:
                    logger.error(f"Error with generic approach: {e}")
                return []
            
            # Process tour elements to extract basic data
            tour_data = []
            count = 0
            
            for tour_elem in tour_elements:
                if max_tours and count >= max_tours:
                    break
                
                try:
                    # Find the tour link and extract URL
                    link_elem = tour_elem.find_element(By.CSS_SELECTOR, "a")
                    tour_url = link_elem.get_attribute("href")
                    
                    # Skip if this doesn't look like a tour URL
                    if not tour_url or "Attraction_Review" not in tour_url:
                        continue
                    
                    # Get basic tour info
                    tour_info = {"url": tour_url}
                    
                    # Try to get name
                    try:
                        name_elem = tour_elem.find_element(By.CSS_SELECTOR, "h2, h3, div.listing_title")
                        tour_info["name"] = name_elem.text.strip()
                    except NoSuchElementException:
                        # Try to extract from the link text if name element not found
                        tour_info["name"] = link_elem.text.strip() or "Unknown Tour"
                    
                    # Try to get rating
                    try:
                        rating_elem = tour_elem.find_element(By.CSS_SELECTOR, "span.ui_bubble_rating, div.prw_rup.prw_filters_star_rating")
                        bubble_class = rating_elem.get_attribute("class")
                        rating_match = re.search(r'bubble_(\d+)', bubble_class)
                        if rating_match:
                            tour_info["rating"] = float(rating_match.group(1)) / 10
                    except:
                        pass
                    
                    # Try to get review count
                    try:
                        reviews_elem = tour_elem.find_element(By.CSS_SELECTOR, "span.reviewCount, a.review_count")
                        reviews_text = reviews_elem.text.strip()
                        reviews_match = re.search(r'([\d,]+)', reviews_text)
                        if reviews_match:
                            tour_info["number_of_reviews"] = int(reviews_match.group(1).replace(',', ''))
                    except:
                        pass
                    
                    # Try to get price
                    try:
                        price_elem = tour_elem.find_element(By.CSS_SELECTOR, "span.price, div.price_wrap, div.price-wrap")
                        price_text = price_elem.text.strip()
                        price_match = re.search(r'[$€£¥](\d+(?:,\d+)*(?:\.\d+)?)', price_text)
                        if price_match:
                            tour_info["price"] = price_match.group(1).replace(',', '')
                            tour_info["currency"] = price_text[0]  # First character is the currency symbol
                    except:
                        pass
                        
                    # Only add tours with valid names
                    if tour_info.get("name") and tour_info["name"] != "Unknown Tour":
                        tour_data.append(tour_info)
                        count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing tour element: {e}")
                    continue
            
            logger.info(f"Successfully collected data for {len(tour_data)} tours")
            return tour_data
            
        except Exception as e:
            logger.error(f"Error fetching tour listings: {e}")
            return []
    
    def get_tour_details(self, tour_url):
        """Get detailed information about a tour from its page"""
        try:
            self._ensure_driver()
            self._random_delay()
            
            logger.info(f"Fetching tour details from: {tour_url}")
            self.driver.get(tour_url)
            
            # Wait for tour details to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
            except TimeoutException:
                logger.error(f"Timeout waiting for tour details page to load: {tour_url}")
                self.driver.save_screenshot("tour_details_timeout.png")
                return {"url": tour_url, "error": "Timeout loading tour details"}
            
            # Check for captcha
            if "captcha" in self.driver.page_source.lower() or "robot" in self.driver.title.lower():
                logger.error("Captcha detected on tour details page")
                self.driver.save_screenshot("tour_details_captcha.png")
                return {"url": tour_url, "error": "Captcha detected"}
            
            # Initialize tour details with URL
            details = {"url": tour_url}
            
            # Extract name
            try:
                name_elem = self.driver.find_element(By.TAG_NAME, "h1")
                details["name"] = name_elem.text.strip()
            except:
                logger.warning("Could not extract tour name")
            
            # Set category to Tours
            details["category"] = "Tours"
            
            # Extract rating
            try:
                rating_elem = self.driver.find_element(By.CSS_SELECTOR, 
                                                     "span.ui_bubble_rating, div.ratingContainer span[class*='ui_bubble_rating']")
                bubble_class = rating_elem.get_attribute("class")
                rating_match = re.search(r'bubble_(\d+)', bubble_class)
                if rating_match:
                    details["rating"] = float(rating_match.group(1)) / 10
            except:
                try:
                    # Try alternative selectors for rating
                    rating_text = self.driver.find_element(By.CSS_SELECTOR, 
                                                         "span.ratingValue, div.ratingValue").text.strip()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        details["rating"] = float(rating_match.group(1))
                except:
                    logger.warning("Could not extract tour rating")
            
            # Extract review count
            try:
                reviews_elem = self.driver.find_element(By.CSS_SELECTOR, 
                                                      "span.reviewCount, a.seeAllReviews, span.ratingInfo")
                reviews_text = reviews_elem.text.strip()
                reviews_match = re.search(r'([\d,]+)', reviews_text)
                if reviews_match:
                    details["number_of_reviews"] = int(reviews_match.group(1).replace(',', ''))
            except:
                logger.warning("Could not extract review count")
            
            # Extract price
            try:
                price_elem = self.driver.find_element(By.CSS_SELECTOR, 
                                                    "div.priceContainer, div.priceRange, span.price, div.price-wrap")
                price_text = price_elem.text.strip()
                price_match = re.search(r'[$€£¥](\d+(?:,\d+)*(?:\.\d+)?)', price_text)
                if price_match:
                    details["price"] = price_match.group(1).replace(',', '')
                    details["currency"] = price_text[0]  # First character is the currency symbol
                    details["price_level"] = "$" * (1 + int(float(details["price"]) / 50))  # Estimate price level
            except:
                logger.warning("Could not extract price information")
            
            # Extract duration
            try:
                duration_elem = self.driver.find_element(By.CSS_SELECTOR, 
                                                       "div.tourDuration, div.duration, span[data-test-target='tour-duration']")
                details["recommended_duration"] = duration_elem.text.strip()
            except:
                # Try looking for duration in the page source
                duration_match = re.search(r'duration["\':\s]+([^"\'<>]+)', self.driver.page_source, re.IGNORECASE)
                if duration_match:
                    details["recommended_duration"] = duration_match.group(1).strip()
                else:
                    logger.warning("Could not extract tour duration")
            
            # Extract location/addresses
            try:
                location_elem = self.driver.find_element(By.CSS_SELECTOR, 
                                                       "span.address, div.address, button[data-tab='address']")
                details["location"] = location_elem.text.strip()
            except:
                logger.warning("Could not extract location information")
            
            # Extract tour description
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, 
                                                   "div.description, div.listing_description, div[data-test-target='about-section']")
                details["description"] = desc_elem.text.strip()
            except:
                logger.warning("Could not extract tour description")
            
            # Extract coordinates (often in page source)
            lat_match = re.search(r'"latitude"\s*:\s*(-?\d+\.\d+)', self.driver.page_source)
            lng_match = re.search(r'"longitude"\s*:\s*(-?\d+\.\d+)', self.driver.page_source)
            
            if lat_match and lng_match:
                details["latitude"] = float(lat_match.group(1))
                details["longitude"] = float(lng_match.group(1))
            
            # Extract image URL
            try:
                img_elem = self.driver.find_element(By.CSS_SELECTOR, 
                                                  "div.heroPhotoWrapper img, div.prv_thumbs img, div.hero_image img")
                details["image_url"] = img_elem.get_attribute("src")
            except:
                logger.warning("Could not extract image URL")
            
            # Extract tour highlights/features
            try:
                highlight_elems = self.driver.find_elements(By.CSS_SELECTOR, 
                                                          "div.highlightItem, div.vr_points, li.plusItem")
                if highlight_elems:
                    details["highlights"] = [elem.text.strip() for elem in highlight_elems if elem.text.strip()]
            except:
                logger.warning("Could not extract tour highlights")
            
            # Extract "Includes" and "Excludes" sections if available
            try:
                includes_elems = self.driver.find_elements(By.XPATH, 
                                                         "//h3[contains(text(), 'Includes') or contains(text(), 'included')]/following-sibling::ul/li")
                if includes_elems:
                    details["includes"] = [elem.text.strip() for elem in includes_elems if elem.text.strip()]
                
                excludes_elems = self.driver.find_elements(By.XPATH, 
                                                         "//h3[contains(text(), 'Excludes') or contains(text(), 'Not included')]/following-sibling::ul/li")
                if excludes_elems:
                    details["excludes"] = [elem.text.strip() for elem in excludes_elems if elem.text.strip()]
            except:
                logger.warning("Could not extract includes/excludes information")
            
            # Extract cancellation policy
            try:
                cancellation_elem = self.driver.find_element(By.CSS_SELECTOR, 
                                                           "div.taCancellation, div.cancellation-policy, div[data-test-target='cancellation-policy']")
                details["cancellation_policy"] = cancellation_elem.text.strip()
            except:
                logger.warning("Could not extract cancellation policy")
            
            # Extract review summary
            try:
                review_elems = self.driver.find_elements(By.CSS_SELECTOR, 
                                                       "div.review-container p, div.reviewSelector p.partial_entry")[:3]
                if review_elems:
                    details["review_summary"] = " | ".join([elem.text.strip() for elem in review_elems if elem.text.strip()])
            except:
                logger.warning("Could not extract review summary")
            
            # Extract operator info
            try:
                operator_elem = self.driver.find_element(By.CSS_SELECTOR, 
                                                       "div.supplier, div.operatorInfo, a.productSupplierItemLink")
                details["operator"] = operator_elem.text.strip()
            except:
                logger.warning("Could not extract tour operator information")
            
            # Extract languages offered
            try:
                language_elems = self.driver.find_elements(By.XPATH, 
                                                         "//div[contains(text(), 'Languages Offered')]/following-sibling::div/span")
                if language_elems:
                    details["languages_offered"] = [elem.text.strip() for elem in language_elems if elem.text.strip()]
            except:
                logger.warning("Could not extract languages offered")
            
            # Extract activities/tags
            activities = []
            try:
                tag_elems = self.driver.find_elements(By.CSS_SELECTOR, 
                                                    "div.tagContent, span.tag, div.collapsedTagContent span")
                if tag_elems:
                    tags = [elem.text.strip() for elem in tag_elems if elem.text.strip()]
                    details["tags"] = tags
                    
                    # Derive activities from tags
                    activity_keywords = ['hiking', 'swimming', 'sightseeing', 'shopping', 'diving', 'snorkeling', 
                                       'kayaking', 'biking', 'tour', 'walking', 'boat', 'cruise', 'food', 'eating',
                                       'cultural', 'historical', 'adventure', 'nature', 'photography']
                    
                    for tag in tags:
                        for keyword in activity_keywords:
                            if keyword.lower() in tag.lower() and keyword not in activities:
                                activities.append(keyword)
            except:
                logger.warning("Could not extract tags/activities")
            
            if activities:
                details["activities"] = activities
            
            # Extract suitable_for information from tags
            if "tags" in details:
                suitable_for = []
                for tag in details["tags"]:
                    tag_lower = tag.lower()
                    if 'family' in tag_lower:
                        suitable_for.append('family')
                    if 'couple' in tag_lower:
                        suitable_for.append('couple')
                    if 'solo' in tag_lower or 'alone' in tag_lower:
                        suitable_for.append('solo')
                    if 'group' in tag_lower:
                        suitable_for.append('group')
                
                if suitable_for:
                    details["suitable_for"] = suitable_for
            
            # Extract popular destinations on this tour
            try:
                destination_elems = self.driver.find_elements(By.CSS_SELECTOR, 
                                                           "div.stops span, div.stopping span, div.attractionStop")
                if destination_elems:
                    details["destinations"] = [elem.text.strip() for elem in destination_elems if elem.text.strip()]
            except:
                logger.warning("Could not extract tour destinations")
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting tour details: {e}")
            return {"url": tour_url, "error": str(e)}
        
    def scrape_tours(self, url, max_tours=None, output_file=None):
        """Scrape tour listings and get details for each tour"""
        try:
            self._ensure_driver()
            
            # Get tour listings
            tours = self.get_tour_listings(url, max_tours)
            logger.info(f"Found {len(tours)} tour listings")
            
            # Get detailed info for each tour
            detailed_tours = []
            for i, tour in enumerate(tours):
                logger.info(f"Processing tour {i+1}/{len(tours)}: {tour.get('name', 'Unknown')}")
                tour_details = self.get_tour_details(tour["url"])
                detailed_tours.append(tour_details)
            
            # Save to file if requested
            if output_file and detailed_tours:
                self.save_to_csv(detailed_tours, output_file)
            
            return detailed_tours
            
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
        
    def save_to_json(self, data, filename):
        """Save data to JSON file"""
        if not data:
            logger.warning("No data to save")
            return
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Data saved to {filename}")

def parse_arguments():
    parser = argparse.ArgumentParser(description='TripAdvisor Tour Crawler')
    parser.add_argument('--url', type=str, 
                        default='https://www.tripadvisor.com/Attractions-g293924-Activities-c42-Hanoi.html',
                        help='URL of the TripAdvisor tour listings page')
    parser.add_argument('--output', type=str, default='data/hanoi_tours.csv',
                        help='Output CSV file name')
    parser.add_argument('--json', type=str, default='data/hanoi_tours.json',
                        help='Output JSON file name')
    parser.add_argument('--max', type=int, default=5,
                        help='Maximum number of tours to scrape')
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
    
    # Create output directory if it doesn't exist
    for filename in [args.output, args.json]:
        if filename:
            output_dir = os.path.dirname(filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
    
    logger.info(f"Starting tour crawler for: {args.url}")
    logger.info(f"Will save data to: {args.output} and {args.json}")
    logger.info(f"Max tours to scrape: {args.max}")
    logger.info(f"Delay between requests: {args.delay}-{args.delay*2} seconds")
    
    # Initialize crawler
    crawler = TourCrawler(delay=args.delay, headless=not args.visible)
    
    # Start scraping
    tour_data = crawler.scrape_tours(args.url, max_tours=args.max, output_file=args.output)
    
    # Save as JSON as well
    if args.json and tour_data:
        crawler.save_to_json(tour_data, args.json)
    
    logger.info(f"Completed crawling {len(tour_data)} tours") 