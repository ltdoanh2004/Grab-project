#!/usr/bin/env python3
"""
Enhanced TripAdvisor Crawler using Selenium
Includes advanced anti-detection features and proxy support
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import json
import time
import random
import logging
import os
import argparse
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("selenium_crawler.log")
    ]
)
logger = logging.getLogger(__name__)

class SeleniumTripAdvisorCrawler:
    def __init__(self, base_url=None, delay=3.0, proxy=None, custom_type=None):
        self.base_url = base_url or "https://www.tripadvisor.com/Attractions-g293924-Activities-a_allAttractions.true-Hanoi.html"
        self.min_delay = delay
        self.max_delay = delay * 2
        self.proxy = proxy
        self.custom_type = custom_type
        self.visited_urls = set()
        self.visited_attractions = set()
        self.driver = None

    def init_driver(self):
        """Initialize undetected-chromedriver with anti-detection measures"""
        try:
            options = uc.ChromeOptions()
            
            # Add proxy if specified
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')

            # Add anti-detection measures
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--disable-gpu')
            options.add_argument(f'--window-size={random.randint(1200, 1920)},{random.randint(800, 1080)}')
            
            # Random user agent
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            ]
            options.add_argument(f'user-agent={random.choice(user_agents)}')

            # Initialize undetected-chromedriver
            self.driver = uc.Chrome(options=options)
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            # Execute stealth JavaScript
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = { runtime: {} };
            """)
            
            logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False

    def random_delay(self):
        """Add random delay between actions"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)

    def simulate_human_behavior(self):
        """Simulate random human-like behavior"""
        try:
            # Random mouse movements
            actions = ActionChains(self.driver)
            for _ in range(random.randint(2, 5)):
                actions.move_by_offset(
                    random.randint(-100, 100),
                    random.randint(-100, 100)
                ).perform()
                time.sleep(random.uniform(0.1, 0.3))

            # Random scrolling
            for _ in range(random.randint(3, 7)):
                scroll_amount = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.5, 1.5))

            # Sometimes move mouse to random element
            elements = self.driver.find_elements(By.TAG_NAME, 'a')
            if elements:
                random_element = random.choice(elements)
                try:
                    actions.move_to_element(random_element).perform()
                    time.sleep(random.uniform(0.2, 0.5))
                except:
                    pass

        except Exception as e:
            logger.warning(f"Error in human behavior simulation: {e}")

    def get_page_with_retry(self, url, max_retries=3):
        """Get page content with retry mechanism"""
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                self.random_delay()
                
                # Wait for main content to load
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Simulate human behavior
                self.simulate_human_behavior()
                
                # Check for captcha
                if "captcha" in self.driver.page_source.lower():
                    logger.warning("Captcha detected!")
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 30
                        logger.info(f"Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return None
                
                return BeautifulSoup(self.driver.page_source, 'html.parser')
                
            except TimeoutException:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except WebDriverException as e:
                logger.error(f"WebDriver error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
            
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 30
                logger.info(f"Retrying after {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                return None

    def get_attraction_listings(self, page=1):
        """Get attraction listings from a page"""
        current_url = self.base_url
        if page > 1:
            if "oa" in current_url:
                current_url = current_url.replace("oa0", f"oa{(page-1)*30}")
            else:
                current_url = current_url.replace(".html", f"-oa{(page-1)*30}.html")

        soup = self.get_page_with_retry(current_url)
        if not soup:
            return [], False

        attractions = []
        local_seen = set()

        # Find attraction links
        selectors = [
            'a[data-automation="poiTitleLink"]',
            'div[data-automation="attraction"] a[href^="/Attraction_Review"]',
            'a[href^="/Attraction_Review"]'
        ]

        for selector in selectors:
            for a in soup.select(selector):
                href = a.get('href')
                name = a.get_text(strip=True)
                
                if not href or not self._valid_name(name):
                    continue
                    
                if not href.startswith('http'):
                    href = urljoin("https://www.tripadvisor.com", href)
                    
                if href in local_seen:
                    continue
                    
                local_seen.add(href)
                attractions.append({"name": name, "url": href})

        logger.info(f"Found {len(attractions)} attractions on page {page}")
        
        # Check for next page
        next_button = soup.select_one('a[href*="oa"][aria-label*="Next"]')
        has_next = bool(next_button)

        return attractions, has_next

    def _valid_name(self, name):
        """Validate attraction name"""
        if not name or len(name) < 3:
            return False
        bad_words = ["see tickets", "reviews", "review of", "tickets"]
        return not any(word in name.lower() for word in bad_words)

    def crawl_attractions(self, max_pages=3, max_attractions=None):
        """Main crawling function"""
        if not self.init_driver():
            return []

        try:
            all_listings = []
            page = 1
            more = True
            retry_count = 0
            max_retries = 3

            while more and page <= max_pages:
                try:
                    lst, more = self.get_attraction_listings(page)
                    
                    if not lst and retry_count < max_retries:
                        retry_count += 1
                        wait_time = (2 ** retry_count) * 30
                        logger.info(f"No listings found, retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue

                    retry_count = 0
                    all_listings.extend(lst)
                    
                    if max_attractions and len(all_listings) >= max_attractions:
                        all_listings = all_listings[:max_attractions]
                        break

                    page += 1
                    self.random_delay()

                except Exception as e:
                    logger.error(f"Error on page {page}: {e}")
                    if retry_count < max_retries:
                        retry_count += 1
                        continue
                    break

            if not all_listings:
                logger.warning("No attractions found")
                return []

            # Process attraction details
            detailed = []
            for item in all_listings:
                try:
                    details = self.get_attraction_details(item["url"])
                    if details:
                        detailed.append({**item, **details})
                        logger.info(f"✓ {item['name']}")
                except Exception as e:
                    logger.error(f"Error processing {item['url']}: {e}")

            return detailed

        finally:
            if self.driver:
                self.driver.quit()

    def save_to_json(self, data, filename):
        """Save results to JSON file"""
        if not data:
            logger.warning("No data to save")
            return
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description='TripAdvisor Crawler using Selenium')
    parser.add_argument('--max-pages', type=int, default=3)
    parser.add_argument('--max-attractions', type=int)
    parser.add_argument('--delay', type=float, default=4.0)
    parser.add_argument('--proxy', help='Proxy server (e.g., socks5://127.0.0.1:9050)')
    parser.add_argument('--custom-type')
    parser.add_argument('--output', default='hanoi_attractions_selenium.json')
    args = parser.parse_args()

    crawler = SeleniumTripAdvisorCrawler(
        delay=args.delay,
        proxy=args.proxy,
        custom_type=args.custom_type
    )
    
    data = crawler.crawl_attractions(
        max_pages=args.max_pages,
        max_attractions=args.max_attractions
    )
    
    crawler.save_to_json(data, args.output)
    logger.info(f"Saved → {args.output}")

if __name__ == "__main__":
    main() 