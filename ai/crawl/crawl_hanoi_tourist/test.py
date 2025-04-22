import argparse
import logging
import time
import random
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hanoi_tourist_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HanoiTouristCrawler:
    def __init__(self):
        self.base_url = "https://dulichviet.com.vn/du-lich-ha-noi"
        self.output_dir = "data_attractions"
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize progress tracking
        self.progress_file = os.path.join(self.output_dir, "progress.json")
        self.visited_urls = set()
        self.load_progress()
        
        # Setup Chrome options
        self.chrome_options = self._setup_chrome_options()

    def _setup_chrome_options(self) -> Options:
        """Setup Chrome options based on platform and requirements"""
        chrome_options = Options()
        
        # Common options
        chrome_options.add_argument("--headless=new")  # Use new headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Add user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Additional options for stability
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Platform specific options
        system = platform.system().lower()
        if system == "linux":
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-dev-shm-usage")
        elif system == "darwin":  # macOS
            chrome_options.add_argument("--disable-gpu-sandbox")
        
        return chrome_options

    def init_driver(self):
        """Initialize and return a new Chrome driver with error handling"""
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to initialize Chrome driver (attempt {attempt + 1}/{max_retries})")
                
                # Get the latest driver
                driver_path = ChromeDriverManager().install()
                service = Service(driver_path)
                
                # Create driver with extended page load timeout
                driver = webdriver.Chrome(service=service, options=self.chrome_options)
                driver.set_page_load_timeout(30)
                driver.implicitly_wait(20)  # Increased wait time
                
                # Test the driver
                driver.get("https://www.google.com")
                logger.info("Chrome driver initialized successfully")
                return driver
                
            except WebDriverException as e:
                logger.error(f"Failed to initialize Chrome driver (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise Exception(f"Failed to initialize Chrome driver after {max_retries} attempts: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error initializing Chrome driver: {str(e)}")
                raise

    def load_progress(self):
        """Load previous crawling progress"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    self.visited_urls = set(progress.get('visited_urls', []))
                    logger.info(f"Loaded progress: {len(self.visited_urls)} URLs visited")
        except Exception as e:
            logger.error(f"Error loading progress: {e}")

    def save_progress(self):
        """Save current crawling progress"""
        try:
            progress = {
                'visited_urls': list(self.visited_urls),
                'last_update': datetime.now().isoformat()
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2)
            logger.info("Progress saved")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")

    def click_load_more(self, driver: webdriver.Chrome, max_retries: int = 3) -> bool:
        """Click on load more button and wait for new content"""
        for attempt in range(max_retries):
            try:
                # Wait for the "Xem thêm" button to be clickable
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-more, .load-more, #loadMore, .btn-loadmore"))
                )
                
                # Scroll to button
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(1)  # Wait for scroll
                
                # Click using JavaScript
                driver.execute_script("arguments[0].click();", load_more_button)
                
                # Wait for new content to load
                time.sleep(3)  # Wait for content load
                return True
                
            except TimeoutException:
                logger.info("No more content to load (button not found)")
                return False
            except Exception as e:
                logger.warning(f"Error clicking load more (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return False
                time.sleep(2)
        return False

    def wait_for_page_load(self, driver: webdriver.Chrome):
        """Wait for page to load completely"""
        try:
            # Wait for document ready state
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Scroll to load lazy content
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
                "window.scrollTo(0, 0);"
            )
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error waiting for page load: {e}")

    def extract_tours(self, driver: webdriver.Chrome) -> List[Dict]:
        """Extract tour information from current page"""
        tours = []
        try:
            # Wait for page to load completely
            self.wait_for_page_load(driver)
            
            # Log page source for debugging
            logger.debug("Page source before extraction: " + driver.page_source[:500] + "...")
            
            # Try multiple selectors for tour items
            selectors = [
                ".item-tour",
                ".tour-item",
                ".tour-box",
                ".tour-list .item",
                ".list-tour .item",
                "div[class*='tour']",
                ".product-list .item"
            ]
            
            tour_items = []
            for selector in selectors:
                try:
                    items = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    if items:
                        tour_items = items
                        logger.info(f"Found {len(items)} tour items using selector: {selector}")
                        break
                except:
                    continue
            
            if not tour_items:
                logger.error("No tour items found with any selector")
                # Try to get page title and URL for debugging
                logger.debug(f"Current URL: {driver.current_url}")
                logger.debug(f"Page title: {driver.title}")
                return []
            
            for item in tour_items:
                try:
                    # Try multiple selectors for links
                    link_selectors = [
                        "a.title",
                        ".tour-name a",
                        ".tour-link",
                        "a[href*='tour']",
                        "a"
                    ]
                    
                    tour_link = None
                    for selector in link_selectors:
                        try:
                            tour_link = item.find_element(By.CSS_SELECTOR, selector)
                            break
                        except:
                            continue
                    
                    if not tour_link:
                        logger.warning("Could not find tour link, skipping item")
                        continue
                    
                    tour_url = tour_link.get_attribute("href")
                    if not tour_url:
                        logger.warning("Tour URL is empty, skipping item")
                        continue
                    
                    # Skip if already crawled
                    if tour_url in self.visited_urls:
                        continue
                    
                    # Extract basic info
                    tour = {
                        'url': tour_url,
                        'name': tour_link.text.strip(),
                        'crawled_at': datetime.now().isoformat()
                    }
                    
                    # Try to get image with multiple selectors
                    image_selectors = ["img", ".tour-image img", ".image img"]
                    for selector in image_selectors:
                        try:
                            img = item.find_element(By.CSS_SELECTOR, selector)
                            tour['image'] = img.get_attribute("src") or img.get_attribute("data-src")
                            if tour['image']:
                                break
                        except:
                            continue
                    
                    # Try to get price with multiple selectors
                    price_selectors = [
                        ".tour-price",
                        ".price",
                        ".tour-cost",
                        "*[class*='price']",
                        "*[class*='cost']"
                    ]
                    for selector in price_selectors:
                        try:
                            price_elem = item.find_element(By.CSS_SELECTOR, selector)
                            tour['price'] = price_elem.text.strip()
                            if tour['price']:
                                break
                        except:
                            continue
                    
                    # Try to get duration with multiple selectors
                    duration_selectors = [
                        ".tour-duration",
                        ".duration",
                        ".tour-time",
                        "*[class*='duration']",
                        "*[class*='time']"
                    ]
                    for selector in duration_selectors:
                        try:
                            duration_elem = item.find_element(By.CSS_SELECTOR, selector)
                            tour['duration'] = duration_elem.text.strip()
                            if tour['duration']:
                                break
                        except:
                            continue
                    
                    # Get detailed information
                    detailed_info = self.get_tour_details(driver, tour_url)
                    tour.update(detailed_info)
                    
                    tours.append(tour)
                    self.visited_urls.add(tour_url)
                    logger.info(f"Extracted tour: {tour['name']}")
                    
                except Exception as e:
                    logger.error(f"Error extracting tour data: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error finding tour items: {e}")
            logger.debug(f"Current URL: {driver.current_url}")
            logger.debug(f"Page title: {driver.title}")
            
        return tours

    def get_tour_details(self, driver: webdriver.Chrome, url: str) -> Dict:
        """Get detailed information from tour page"""
        try:
            # Store current window handle
            main_window = driver.current_window_handle
            
            # Open new tab
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            
            try:
                # Navigate to tour page
                driver.get(url)
                time.sleep(2)  # Wait for page load
                
                # Extract details
                details = {
                    'description': self._get_element_text(driver, ".tour-description, .description, .tour-desc"),
                    'highlights': self._get_list_items(driver, ".tour-highlights li, .highlights li, .tour-feature li"),
                    'includes': self._get_list_items(driver, ".tour-includes li, .includes li, .tour-include li"),
                    'excludes': self._get_list_items(driver, ".tour-excludes li, .excludes li, .tour-exclude li"),
                    'itinerary': self.extract_itinerary(driver),
                    'departure_dates': self._get_list_items(driver, ".departure-dates .date, .tour-dates .date, .schedule-date"),
                    'notes': self._get_element_text(driver, ".tour-notes, .notes, .tour-note"),
                    'policies': self._get_element_text(driver, ".tour-policies, .policies, .tour-policy")
                }
                
                return details
                
            finally:
                # Always close tab and switch back
                driver.close()
                driver.switch_to.window(main_window)
            
        except Exception as e:
            logger.error(f"Error getting tour details from {url}: {e}")
            # Make sure we're back on the main window
            try:
                driver.switch_to.window(main_window)
            except:
                pass
            return {}

    def _get_element_text(self, driver: webdriver.Chrome, selector: str) -> str:
        """Get text from an element with multiple possible selectors"""
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            return None

    def _get_list_items(self, driver: webdriver.Chrome, selector: str) -> List[str]:
        """Get list items with multiple possible selectors"""
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            return [elem.text.strip() for elem in elements if elem.text.strip()]
        except NoSuchElementException:
            return []

    def extract_itinerary(self, driver: webdriver.Chrome) -> List[Dict]:
        """Extract detailed itinerary from tour page"""
        itinerary = []
        try:
            days = driver.find_elements(By.CSS_SELECTOR, ".itinerary .day, .schedule-detail .day, .tour-schedule .day")
            for day in days:
                try:
                    day_info = {
                        'title': day.find_element(By.CSS_SELECTOR, ".day-title, .schedule-title").text.strip(),
                        'description': day.find_element(By.CSS_SELECTOR, ".day-content, .schedule-content").text.strip()
                    }
                    itinerary.append(day_info)
                except Exception as e:
                    logger.error(f"Error extracting itinerary day: {e}")
        except NoSuchElementException:
            pass
        return itinerary

    def save_data(self, data: List[Dict]):
        """Save crawled data to JSON file"""
        if not data:
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(self.output_dir, f'hanoi_tours_{timestamp}.json')
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(data)} tours to {filename}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def run(self, total_items: int = 100):
        """Run the crawler"""
        driver = None
        try:
            logger.info(f"Starting crawler, targeting {total_items} items")
            
            # Initialize driver
            driver = self.init_driver()
            all_tours = []
            
            # Load initial page
            logger.info("Loading initial page...")
            driver.get(self.base_url)
            
            # Wait for page to load completely
            self.wait_for_page_load(driver)
            
            # Keep clicking "Load More" until we have enough items or no more content
            max_attempts = 10  # Maximum number of attempts to find tours
            attempts = 0
            
            while len(all_tours) < total_items and attempts < max_attempts:
                attempts += 1
                
                # Extract current page tours
                new_tours = self.extract_tours(driver)
                if new_tours:
                    all_tours.extend(new_tours)
                    logger.info(f"Collected {len(all_tours)} tours so far")
                    
                    # Save progress
                    self.save_progress()
                    self.save_data(all_tours)
                    
                    # Try to load more
                    if not self.click_load_more(driver):
                        logger.info("No more tours to load")
                        break
                    
                    # Random delay between loads
                    time.sleep(random.uniform(2, 4))
                else:
                    logger.warning(f"No tours found on attempt {attempts}/{max_attempts}")
                    if attempts >= max_attempts:
                        logger.error("Max attempts reached without finding tours")
                        break
                    time.sleep(5)  # Wait before retrying
            
            logger.info(f"Crawling completed. Total tours collected: {len(all_tours)}")
            
        except Exception as e:
            logger.error(f"Error in crawler execution: {e}")
        finally:
            # Cleanup
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            # Final save
            self.save_progress()

def main():
    parser = argparse.ArgumentParser(description="Hanoi Tourist Crawler")
    parser.add_argument("--total-items", type=int, default=100,
                      help="Total number of items to crawl")
    args = parser.parse_args()

    crawler = HanoiTouristCrawler()
    crawler.run(args.total_items)

if __name__ == "__main__":
    main()