import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import logging
import random
import time
import re
from typing import List, Dict, Any
import os
import math
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('foody_crawler.log'),
        logging.StreamHandler()
    ]
)

class FoodyCrawler:
    def __init__(self, start_page=1):
        self.api_url = "https://www.foody.vn/__get/Place/HomeListPlace"
        self.output_dir = "data"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://www.foody.vn/ha-noi",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        # Hanoi coordinates
        self.lat = 21.033333
        self.lon = 105.85
        self.items_per_page = 12  # Default items per page from API
        self.start_page = start_page
        
        os.makedirs(self.output_dir, exist_ok=True)

        # Create progress tracking file
        self.progress_file = os.path.join(self.output_dir, "crawl_progress.json")
        self.load_progress()

    def load_progress(self):
        """Load previous crawling progress if exists"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    self.start_page = progress.get('last_page', self.start_page)
                    logging.info(f"Loaded previous progress: last page was {self.start_page}")
        except Exception as e:
            logging.error(f"Error loading progress: {str(e)}")

    def save_progress(self, current_page: int, items_collected: int):
        """Save current crawling progress"""
        try:
            progress = {
                'last_page': current_page,
                'items_collected': items_collected,
                'last_update': datetime.now().isoformat()
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2)
            logging.info(f"Saved progress: page {current_page}, items {items_collected}")
        except Exception as e:
            logging.error(f"Error saving progress: {str(e)}")

    def get_page_data(self, page: int = 1) -> List[Dict]:
        """Fetch restaurant data from a specific page"""
        try:
            params = {
                "t": str(int(time.time() * 1000)),  # Current timestamp
                "page": page,
                "lat": self.lat,
                "lon": self.lon,
                "count": self.items_per_page,
                "type": 1
            }
            
            logging.info(f"Fetching page {page}")
            response = requests.get(
                self.api_url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get("Items", [])
            
            if not items:
                logging.warning(f"No items found on page {page}")
                return []
                
            restaurants = []
            for item in items:
                try:
                    # Extract reviews
                    reviews = []
                    if item.get("LstReview"):
                        for review in item["LstReview"]:
                            reviews.append({
                                "user": review.get("reviewUserDisplayName"),
                                "rating": review.get("AvgRating"),
                                "comment": review.get("Comment"),
                                "date": review.get("CreatedOn"),
                                "user_avatar": review.get("reviewUserAvatar")
                            })
                    
                    # Extract services
                    services = []
                    if item.get("Services"):
                        for service in item["Services"]:
                            services.append({
                                "name": service.get("Title"),
                                "url": service.get("Url"),
                                "type": service.get("Type")
                            })
                    
                    # Create restaurant object with API data
                    restaurant = {
                        "id": item.get("Id"),
                        "name": item.get("Name"),
                        "address": item.get("Address"),
                        "rating": item.get("AvgRating"),
                        "total_reviews": item.get("TotalReviews"),
                        "total_pictures": item.get("TotalPictures"),
                        "phone": item.get("Phone"),
                        "photo_url": item.get("PhotoUrl"),
                        "url": "https://www.foody.vn" + item.get("Url", ""),
                        "location": {
                            "lat": item.get("Latitude"),
                            "lon": item.get("Longitude")
                        },
                        "reviews": reviews,
                        "services": services,
                        "is_delivery": item.get("IsDelivery", False),
                        "is_booking": item.get("IsBooking", False),
                        "is_opening": item.get("IsOpening", True),
                        "price_range": {
                            "min": item.get("PriceMin"),
                            "max": item.get("PriceMax")
                        },
                        "crawled_at": datetime.now().isoformat()
                    }
                    
                    restaurants.append(restaurant)
                    logging.info(f"Extracted data for restaurant: {restaurant['name']}")
                    
                    # Add small delay between requests
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logging.error(f"Error processing restaurant item: {str(e)}")
                    continue
                    
            return restaurants
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page {page}: {str(e)}")
            if hasattr(e.response, 'text'):
                logging.error(f"API Response: {e.response.text[:500]}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error fetching page {page}: {str(e)}")
            return []

    def save_data(self, data: Dict[str, Any]):
        """Save restaurant data to JSON file"""
        if not data or not data.get('name'):
            logging.error("Cannot save data: missing restaurant name")
            return
            
        safe_name = re.sub(r'[^\w\s-]', '', data['name'].lower())
        safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Saved data to {filepath}")
        except Exception as e:
            logging.error(f"Error saving data to {filepath}: {str(e)}")

    def run(self, total_items: int = 100):
        """
        Run the crawler to get the specified number of restaurants
        Args:
            total_items: Total number of restaurants to crawl
        """
        try:
            logging.info(f"Starting crawler from page {self.start_page}, targeting {total_items} items")
            
            # Calculate number of pages needed
            total_pages = math.ceil(total_items / self.items_per_page)
            items_collected = 0
            current_page = self.start_page
            
            while items_collected < total_items and current_page <= (self.start_page + total_pages - 1):
                # Get restaurants from current page
                restaurants = self.get_page_data(current_page)
                
                # Process each restaurant
                for restaurant in restaurants:
                    if items_collected >= total_items:
                        break
                        
                    try:
                        # Save the data
                        self.save_data(restaurant)
                        items_collected += 1
                        
                        # Progress update
                        logging.info(f"Progress: {items_collected}/{total_items} restaurants processed")
                        
                    except Exception as e:
                        logging.error(f"Error processing restaurant: {str(e)}")
                        continue
                
                # Save progress after each page
                self.save_progress(current_page, items_collected)
                
                # Move to next page
                current_page += 1
                
                # Random delay between pages
                if current_page <= (self.start_page + total_pages - 1):
                    delay = random.uniform(1, 3)
                    logging.info(f"Waiting {delay:.2f} seconds before next page...")
                    time.sleep(delay)
            
            logging.info(f"Crawling completed. Processed {items_collected} restaurants")
            
        except Exception as e:
            logging.error(f"Error in main crawler loop: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Foody.vn Restaurant Crawler')
    parser.add_argument('--total-items', type=int, default=100,
                      help='Total number of restaurants to crawl')
    parser.add_argument('--start-page', type=int, default=1,
                      help='Page number to start crawling from')
    args = parser.parse_args()

    try:
        crawler = FoodyCrawler(start_page=args.start_page)
        crawler.run(args.total_items)
    except Exception as e:
        logging.error(f"Critical error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 