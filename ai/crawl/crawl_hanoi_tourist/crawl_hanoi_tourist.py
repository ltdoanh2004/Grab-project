import argparse
import logging
import time
import random
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urljoin
import urllib3
import cloudscraper

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        
        # Setup session with cloudscraper
        self.session = cloudscraper.create_scraper(
            delay=10,
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        # Update headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9',
            'Referer': 'https://dulichviet.com.vn/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

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

    def get_page_content(self, url: str, retries: int = 3) -> BeautifulSoup:
        """Get page content with retries"""
        for attempt in range(retries):
            try:
                # Add random delay between requests
                time.sleep(random.uniform(2, 5))
                
                # Make request
                response = self.session.get(
                    url, 
                    timeout=30,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # Check if we got a valid response
                if 'text/html' not in response.headers.get('Content-Type', ''):
                    raise Exception("Invalid content type received")
                
                return BeautifulSoup(response.text, 'html.parser')
                
            except Exception as e:
                logger.error(f"Error fetching {url} (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    # Increase delay for each retry
                    time.sleep(random.uniform(5, 10))
                    continue
                raise

    def extract_tours(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract tour information from page"""
        tours = []
        try:
            # Try multiple selectors for tour items
            selectors = [
                ".item-tour",
                ".tour-item",
                ".tour-box",
                ".tour-list .item",
                ".list-tour .item",
                "div[class*='tour']",
                ".product-list .item",
                ".tour-content .item"
            ]
            
            tour_items = []
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    tour_items = items
                    logger.info(f"Found {len(items)} tour items using selector: {selector}")
                    break
            
            if not tour_items:
                logger.error("No tour items found with any selector")
                return []
            
            for item in tour_items:
                try:
                    # Try to get tour link
                    link_selectors = [
                        "a.title",
                        ".tour-name a",
                        ".tour-link",
                        "a[href*='tour']",
                        "a"
                    ]
                    
                    tour_link = None
                    for selector in link_selectors:
                        link = item.select_one(selector)
                        if link and link.get('href'):
                            tour_link = link
                            break
                    
                    if not tour_link:
                        continue
                    
                    tour_url = urljoin(self.base_url, tour_link['href'])
                    
                    # Skip if already crawled
                    if tour_url in self.visited_urls:
                        continue
                    
                    # Extract basic info
                    tour = {
                        'url': tour_url,
                        'name': tour_link.get_text(strip=True),
                        'crawled_at': datetime.now().isoformat()
                    }
                    
                    # Try to get image
                    img = item.select_one("img")
                    if img:
                        tour['image'] = urljoin(self.base_url, img.get('src', img.get('data-src', '')))
                    
                    # Try to get price
                    price_elem = item.select_one(".tour-price, .price, .tour-cost, [class*='price'], [class*='cost']")
                    if price_elem:
                        tour['price'] = price_elem.get_text(strip=True)
                    
                    # Try to get duration
                    duration_elem = item.select_one(".tour-duration, .duration, .tour-time, [class*='duration'], [class*='time']")
                    if duration_elem:
                        tour['duration'] = duration_elem.get_text(strip=True)
                    
                    # Get detailed information
                    detailed_info = self.get_tour_details(tour_url)
                    tour.update(detailed_info)
                    
                    tours.append(tour)
                    self.visited_urls.add(tour_url)
                    logger.info(f"Extracted tour: {tour['name']}")
                    
                except Exception as e:
                    logger.error(f"Error extracting tour data: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error finding tour items: {e}")
            
        return tours

    def get_tour_details(self, url: str) -> Dict:
        """Get detailed information from tour page"""
        try:
            soup = self.get_page_content(url)
            
            details = {
                'description': self._get_text(soup, ".tour-description, .description, .tour-desc"),
                'highlights': self._get_list_items(soup, ".tour-highlights li, .highlights li, .tour-feature li"),
                'includes': self._get_list_items(soup, ".tour-includes li, .includes li, .tour-include li"),
                'excludes': self._get_list_items(soup, ".tour-excludes li, .excludes li, .tour-exclude li"),
                'itinerary': self.extract_itinerary(soup),
                'departure_dates': self._get_list_items(soup, ".departure-dates .date, .tour-dates .date, .schedule-date"),
                'notes': self._get_text(soup, ".tour-notes, .notes, .tour-note"),
                'policies': self._get_text(soup, ".tour-policies, .policies, .tour-policy")
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting tour details from {url}: {e}")
            return {}

    def _get_text(self, soup: BeautifulSoup, selector: str) -> str:
        """Get text from an element with multiple possible selectors"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None

    def _get_list_items(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """Get list items with multiple possible selectors"""
        elements = soup.select(selector)
        return [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]

    def extract_itinerary(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract detailed itinerary from tour page"""
        itinerary = []
        try:
            days = soup.select(".itinerary .day, .schedule-detail .day, .tour-schedule .day")
            for day in days:
                try:
                    day_info = {
                        'title': day.select_one(".day-title, .schedule-title").get_text(strip=True),
                        'description': day.select_one(".day-content, .schedule-content").get_text(strip=True)
                    }
                    itinerary.append(day_info)
                except Exception as e:
                    logger.error(f"Error extracting itinerary day: {e}")
        except Exception:
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
        try:
            logger.info(f"Starting crawler, targeting {total_items} items")
            all_tours = []
            page = 1
            
            while len(all_tours) < total_items:
                try:
                    # Construct URL for current page
                    url = f"{self.base_url}?page={page}" if page > 1 else self.base_url
                    logger.info(f"Crawling page {page}: {url}")
                    
                    # Get page content
                    soup = self.get_page_content(url)
                    
                    # Extract tours from current page
                    new_tours = self.extract_tours(soup)
                    if not new_tours:
                        logger.info("No more tours found")
                        break
                    
                    all_tours.extend(new_tours)
                    logger.info(f"Collected {len(all_tours)} tours so far")
                    
                    # Save progress
                    self.save_progress()
                    self.save_data(all_tours)
                    
                    # Move to next page
                    page += 1
                    
                    # Random delay between pages
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"Error processing page {page}: {e}")
                    break
            
            logger.info(f"Crawling completed. Total tours collected: {len(all_tours)}")
            
        except Exception as e:
            logger.error(f"Error in crawler execution: {e}")
        finally:
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