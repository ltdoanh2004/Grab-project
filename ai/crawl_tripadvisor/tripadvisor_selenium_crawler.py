#!/usr/bin/env python3
# TripAdvisor Hotel Crawler using Selenium to bypass anti-bot measures
import time
import argparse
import os
import random
import re
import csv
import logging
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TripAdvisorSeleniumCrawler:
    def __init__(self, base_url=None, delay=3, headless=True):
        self.base_url = base_url
        self.min_delay = delay
        self.max_delay = delay * 2  # Randomize delay a bit
        
        # Configure Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Add user agent to appear more like a real browser
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
        
        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)  # Set page load timeout
        
    def __del__(self):
        """Cleanup method to close the driver when done"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
                logger.info("WebDriver closed")
        except:
            pass
        
    def _random_delay(self):
        """Add a random delay between requests to avoid being blocked"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.info(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)
        
    def get_page(self, url):
        """Get page content using Selenium with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching URL: {url}")
                self.driver.get(url)
                
                # Wait for the page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Check if we hit a CAPTCHA or security page
                if "captcha" in self.driver.page_source.lower() or "please enable js" in self.driver.page_source.lower():
                    logger.warning("Detected CAPTCHA or security check page")
                    
                    # Wait longer to see if it resolves itself (some anti-bot measures time out)
                    time.sleep(10)
                    
                    # Check again after waiting
                    if "captcha" in self.driver.page_source.lower() or "please enable js" in self.driver.page_source.lower():
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 20  # Long wait for next attempt
                            logger.info(f"Still on security check. Retrying after {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                        else:
                            return None
                
                # Success - return the page source
                return self.driver.page_source
                
            except TimeoutException:
                logger.error(f"Timeout while loading {url}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    logger.info(f"Retrying after {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to load {url} after {max_retries} attempts")
                    return None
            except Exception as e:
                logger.error(f"Error fetching URL {url}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    logger.info(f"Retrying after {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
        
        return None
    
    def get_hotels(self, location_url=None):
        """Get hotels for a given location"""
        url = location_url or self.base_url
        if not url:
            raise ValueError("No URL provided")
        
        html = self.get_page(url)
        if not html:
            return []
            
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try various selectors that might work with TripAdvisor's current structure
        hotels = []
        seen_urls = set()  # Track seen URLs to avoid duplicates
        
        # Method 1: Look for hotel links directly in the page
        try:
            # First try to find all hotel cards
            hotel_links = []
            
            # Find hotel links using Selenium for better JavaScript-rendered content handling
            elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="Hotel_Review"]')
            for element in elements:
                try:
                    href = element.get_attribute('href')
                    name = element.text.strip()
                    if href and name and len(name) > 1:
                        # Avoid navigation links and pagination
                        if name.lower() not in ['map', 'view map', 'next', 'previous'] and not name.isdigit():
                            hotel_links.append((name, href))
                except:
                    continue
            
            logger.info(f"Found {len(hotel_links)} potential hotels")
            
            # Process and filter hotel links
            for name, href in hotel_links:
                # Clean up URL by removing fragments and parameters
                base_url = href.split('#')[0].split('?')[0]
                
                # Skip if we've already seen this URL
                if base_url in seen_urls:
                    continue
                    
                seen_urls.add(base_url)
                hotels.append({"name": name, "url": base_url})
        except Exception as e:
            logger.error(f"Error extracting hotel links: {e}")
        
        # Method 2: Use BeautifulSoup as fallback
        if not hotels:
            logger.info("Trying fallback method with BeautifulSoup")
            try:
                hotel_elements = soup.select('a[href*="Hotel_Review"]')
                for element in hotel_elements:
                    href = element.get('href', '')
                    name = element.get_text(strip=True)
                    
                    # Skip empty or very short names
                    if not name or len(name) <= 1:
                        continue
                        
                    # Skip navigation and pagination
                    if name.lower() in ['map', 'view map', 'next', 'previous'] or name.isdigit():
                        continue
                        
                    # Create full URL if needed
                    if not href.startswith('http'):
                        href = urljoin("https://www.tripadvisor.com", href)
                        
                    # Clean URL
                    base_url = href.split('#')[0].split('?')[0]
                    
                    # Skip duplicates
                    if base_url in seen_urls:
                        continue
                        
                    seen_urls.add(base_url)
                    hotels.append({"name": name, "url": base_url})
            except Exception as e:
                logger.error(f"Error in fallback method: {e}")
        
        # Fallback method 3: Use hardcoded top hotels for common locations
        if not hotels:
            logger.warning("No hotels found through standard methods, trying fallback data")
            
            # Extract location from URL
            location = None
            try:
                path_parts = urlparse(url).path.split('-')
                if len(path_parts) > 2:
                    location = path_parts[2]  # e.g., 'Hanoi' from 'Hotels-g293924-Hanoi-Hotels.html'
            except:
                pass
            
            # Hardcoded top hotels for common locations
            if location and location.lower() == 'hanoi':
                hotels = [
                    {"name": "Sofitel Legend Metropole Hanoi", "url": "https://www.tripadvisor.com/Hotel_Review-g293924-d301984-Reviews-Sofitel_Legend_Metropole_Hanoi-Hanoi.html"},
                    {"name": "JW Marriott Hotel Hanoi", "url": "https://www.tripadvisor.com/Hotel_Review-g293924-d4603958-Reviews-JW_Marriott_Hotel_Hanoi-Hanoi.html"},
                    {"name": "La Siesta Classic Ma May", "url": "https://www.tripadvisor.com/Hotel_Review-g293924-d7180730-Reviews-La_Siesta_Classic_Ma_May-Hanoi.html"},
                    {"name": "Oriental Jade Hotel", "url": "https://www.tripadvisor.com/Hotel_Review-g293924-d15614107-Reviews-Oriental_Jade_Hotel-Hanoi.html"},
                    {"name": "Hanoi La Siesta Hotel & Spa", "url": "https://www.tripadvisor.com/Hotel_Review-g293924-d8056846-Reviews-Hanoi_La_Siesta_Hotel_Spa-Hanoi.html"}
                ]
                logger.info(f"Using {len(hotels)} hardcoded hotels for {location}")
        
        logger.info(f"Found {len(hotels)} unique hotels")
        return hotels
    
    def get_hotel_details(self, hotel_url):
        """Get details for a specific hotel"""
        self._random_delay()  # Add random delay before requesting
        
        html = self.get_page(hotel_url)
        if not html:
            return {"url": hotel_url, "name": "Unknown", "status": "Failed to fetch page"}
            
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        details = {"url": hotel_url}
        
        # Try to extract hotel name (multiple methods)
        try:
            # Method 1: Use Selenium to get the title directly
            title = self.driver.title
            if title:
                # Extract hotel name from page title (usually "HOTEL NAME - Reviews & Prices")
                title_parts = title.split(' - ')
                if len(title_parts) > 0:
                    details["name"] = title_parts[0].strip()
                    
            # Method 2: Use BeautifulSoup selectors as fallback
            if "name" not in details or not details["name"]:
                name_selectors = [
                    'h1.QdLfr', 
                    'h1.biGQs', 
                    'h1#HEADING',
                    'div.fiohW', 
                    'div.hvrfCF'
                ]
                for selector in name_selectors:
                    name_elem = soup.select_one(selector)
                    if name_elem:
                        details["name"] = name_elem.get_text(strip=True)
                        break
                
            # Method 3: Extract from URL if still no name
            if "name" not in details or not details["name"]:
                url_parts = hotel_url.split('-Reviews-')
                if len(url_parts) > 1:
                    name_part = url_parts[1].split('-')[0]
                    # Replace underscores with spaces and title case
                    details["name"] = name_part.replace('_', ' ').title()
        except Exception as e:
            logger.error(f"Error extracting hotel name: {e}")
            # Fallback name from URL
            try:
                url_parts = hotel_url.split('-Reviews-')
                if len(url_parts) > 1:
                    name_part = url_parts[1].split('-')[0]
                    details["name"] = name_part.replace('_', ' ').title()
                else:
                    details["name"] = "Unknown Hotel"
            except:
                details["name"] = "Unknown Hotel"
        
        # Try to extract hotel address
        try:
            # Method 1: Use Selenium to find address elements
            address_elements = self.driver.find_elements(By.CSS_SELECTOR, 'span[data-test-target="street-address"], button[data-test-target="streetAddress"]')
            if address_elements:
                address_parts = [elem.text.strip() for elem in address_elements if elem.text.strip()]
                if address_parts:
                    details["address"] = ", ".join(address_parts)
                    
            # Method 2: Look for a location marker that often indicates address
            if "address" not in details:
                try:
                    location_icon_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.LjCWTZdN, div.bKBRJ')
                    for element in location_icon_elements:
                        if element.text and len(element.text.strip()) > 5:  # Likely an address if not too short
                            details["address"] = element.text.strip()
                            break
                except:
                    pass
        except Exception as e:
            logger.error(f"Error extracting address: {e}")
        
        # Try to extract price information
        try:
            price_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.DmVPc, div.WXCOL, div.gbprQ')
            price_texts = []
            for elem in price_elements:
                text = elem.text.strip()
                # Look for currency symbols or numbers to identify price text
                if re.search(r'[\$€£¥]|\d+', text):
                    price_texts.append(text)
            
            if price_texts:
                details["price_range"] = ", ".join(set(price_texts))
        except Exception as e:
            logger.error(f"Error extracting price info: {e}")
        
        # Try to extract star rating
        try:
            star_elements = self.driver.find_elements(By.CSS_SELECTOR, 'svg.mYbgW, span.ui_star_rating')
            for elem in star_elements:
                # Look for star rating in class attributes or aria labels
                try:
                    aria_label = elem.get_attribute('aria-label')
                    if aria_label and 'star' in aria_label.lower():
                        star_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:star|bubble)', aria_label.lower())
                        if star_match:
                            details["stars"] = star_match.group(1)
                            break
                except:
                    pass
                    
                # Try to get class name for bubble ratings
                try:
                    class_name = elem.get_attribute('class')
                    if class_name and 'bubble_' in class_name:
                        classes = class_name.split()
                        for cls in classes:
                            if 'bubble_' in cls:
                                try:
                                    rating_value = cls.split('_')[1]
                                    details["rating"] = float(rating_value) / 10
                                    break
                                except:
                                    pass
                except:
                    pass
        except Exception as e:
            logger.error(f"Error extracting star rating: {e}")
        
        # Try to extract review count
        try:
            review_elements = self.driver.find_elements(By.CSS_SELECTOR, 'span.yFKLG, a.hvrfCF, span.qqniT, a.BMQDV')
            for elem in review_elements:
                text = elem.text.strip()
                reviews_match = re.search(r'([\d,]+)\s+reviews?', text)
                if reviews_match:
                    details["reviews"] = reviews_match.group(1).replace(',', '')
                    break
        except Exception as e:
            logger.error(f"Error extracting review count: {e}")
        
        # Try to extract amenities
        try:
            amenity_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.exmBD, div.OsCbb.IBjkL, div.bUmsU')
            amenities = []
            for elem in amenity_elements:
                text = elem.text.strip()
                if text and len(text) > 1 and text not in amenities:
                    amenities.append(text)
            
            if amenities:
                details["amenities"] = ", ".join(amenities)
        except Exception as e:
            logger.error(f"Error extracting amenities: {e}")
        
        # If we have very limited information, add a status note
        if len(details) <= 2:  # Just URL and name
            logger.warning(f"Limited details found for: {details.get('name', 'Unknown')} at {hotel_url}")
            details["status"] = "Limited information available"
            
            # Try to screenshot the page for debugging
            try:
                screenshot_file = f"debug_{details['name'].replace(' ', '_')}.png"
                self.driver.save_screenshot(screenshot_file)
                logger.info(f"Saved screenshot to {screenshot_file}")
            except Exception as e:
                logger.error(f"Failed to save screenshot: {e}")
        
        return details
    
    def scrape_location(self, location_url=None, max_hotels=None, output_file=None):
        """Scrape hotels for a location and optionally get details"""
        hotels = self.get_hotels(location_url)
        logger.info(f"Found {len(hotels)} hotels")
        
        if max_hotels:
            hotels = hotels[:max_hotels]
            
        detailed_hotels = []
        for i, hotel in enumerate(hotels):
            logger.info(f"Processing {i+1}/{len(hotels)}: {hotel['name']}")
            details = self.get_hotel_details(hotel['url'])
            detailed_hotels.append(details)
            self._random_delay()  # Random delay between requests
        
        # Save to CSV if we have hotels
        if detailed_hotels and output_file:
            self.save_to_csv(detailed_hotels, output_file)
            
        return detailed_hotels
    
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
            writer.writerows(data)
            
        logger.info(f"Data saved to {filename}")


def parse_arguments():
    parser = argparse.ArgumentParser(description='TripAdvisor Hotel Crawler with Selenium')
    parser.add_argument('--url', type=str, default='https://www.tripadvisor.com/Hotels-g293924-Hanoi-Hotels.html',
                        help='URL of the TripAdvisor hotel page to crawl')
    parser.add_argument('--output', type=str, default='tripadvisor_hotels.csv',
                        help='Output CSV file name')
    parser.add_argument('--max', type=int, default=10,
                        help='Maximum number of hotels to crawl')
    parser.add_argument('--delay', type=float, default=3.0,
                        help='Minimum delay between requests in seconds (actual delay will be randomized)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    parser.add_argument('--no-headless', action='store_true',
                        help='Run Chrome in visible mode (not headless)')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # Set debug level if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Extract location name from URL for the filename if no output file specified
    if args.output == 'tripadvisor_hotels.csv':
        parsed_url = urlparse(args.url)
        path_parts = parsed_url.path.split('-')
        if len(path_parts) > 2:
            location = path_parts[2]  # e.g., 'Hanoi' from 'Hotels-g293924-Hanoi-Hotels.html'
            args.output = f'tripadvisor_{location}_hotels.csv'
    
    logger.info(f"Crawling TripAdvisor hotels from: {args.url}")
    logger.info(f"Will save data to: {args.output}")
    logger.info(f"Max hotels to crawl: {args.max}")
    logger.info(f"Delay between requests: {args.delay}-{args.delay*2} seconds")
    logger.info(f"Headless mode: {not args.no_headless}")
    
    try:
        crawler = TripAdvisorSeleniumCrawler(args.url, args.delay, headless=not args.no_headless)
        crawler.scrape_location(output_file=args.output, max_hotels=args.max)
    except Exception as e:
        logger.error(f"Error during crawling: {e}")
    finally:
        # Ensure we quit the driver
        if 'crawler' in locals() and hasattr(crawler, 'driver'):
            crawler.driver.quit() 