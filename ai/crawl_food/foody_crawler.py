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
    def __init__(self):
        self.api_url = "https://www.foody.vn/__get/Place/HomeListPlace"
        self.menu_api_url = "https://gappapi.deliverynow.vn/api/dish/get_detail"
        self.output_dir = "data"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://www.foody.vn/ha-noi",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.deliverynow_headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,vi;q=0.8",
            "x-foody-access-token": "",
            "x-foody-api-version": "1",
            "x-foody-app-type": "1004",
            "x-foody-client-id": "",
            "x-foody-client-language": "vi",
            "x-foody-client-type": "1",
            "x-foody-client-version": "3.0.0",
            "x-sap-ri": "d19ba9d6-6485-4485-a3a5-2b01a0d6f1a0",
            "Referer": "https://shopeefood.vn/",
            "Origin": "https://shopeefood.vn"
        }
        # Hanoi coordinates
        self.lat = 21.033333
        self.lon = 105.85
        self.items_per_page = 12  # Default items per page from API
        
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_restaurant_menu(self, restaurant_url: str) -> Dict:
        """Fetch menu items by parsing the restaurant's HTML page"""
        try:
            logging.info(f"Fetching menu from URL: {restaurant_url}")
            
            response = requests.get(
                restaurant_url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            menu_items = []
            
            # Find menu container - try different possible class names
            menu_section = soup.find('div', class_='menu-restaurant') or \
                         soup.find('div', class_='delivery-menu-restaurant')
            
            if menu_section:
                # Process each menu category
                for category in menu_section.find_all(['div', 'li'], class_=['menu-group', 'menu-item']):
                    # Try to find category name
                    category_name = category.find(['div', 'h2', 'h3'], class_=['menu-group-name', 'title'])
                    category_name = category_name.text.strip() if category_name else "Uncategorized"
                    
                    # Find all dishes in this category
                    dishes = category.find_all(['div', 'li'], class_=['menu-item', 'item'])
                    for dish in dishes:
                        try:
                            # Try different possible class names for each element
                            name_elem = dish.find(['div', 'span', 'h2', 'h3'], 
                                               class_=['item-name', 'name', 'title'])
                            price_elem = dish.find(['div', 'span'], 
                                                class_=['item-price', 'price', 'current-price'])
                            photo_elem = dish.find('img')
                            desc_elem = dish.find(['div', 'span'], 
                                               class_=['item-description', 'description', 'desc'])
                            
                            if name_elem:  # Only add if we at least have a name
                                menu_items.append({
                                    "name": name_elem.text.strip(),
                                    "price": price_elem.text.strip() if price_elem else None,
                                    "description": desc_elem.text.strip() if desc_elem else None,
                                    "photo": photo_elem['src'] if photo_elem and 'src' in photo_elem.attrs else None,
                                    "category": category_name
                                })
                        except Exception as e:
                            logging.error(f"Error processing dish element: {str(e)}")
                            continue
            
            if not menu_items:
                logging.warning(f"No menu items found for URL: {restaurant_url}")
            
            return {
                "total_menu_items": len(menu_items),
                "menu_items": menu_items
            }
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching menu from URL {restaurant_url}: {str(e)}")
            return {}
        except Exception as e:
            logging.error(f"Unexpected error fetching menu: {str(e)}")
            return {}

    def get_restaurant_details(self, soup: BeautifulSoup) -> Dict:
        """Extract additional restaurant details from the HTML"""
        try:
            details = {}
            
            # Get restaurant name
            name_elem = soup.find('h1', class_='name-restaurant')
            if name_elem:
                details['name'] = name_elem.text.strip()
            
            # Get address
            address_elem = soup.find('div', class_='address-restaurant')
            if address_elem:
                details['address'] = address_elem.text.strip()
            
            # Get opening hours
            time_elem = soup.find('div', class_='time-restaurant')
            if time_elem:
                details['opening_hours'] = time_elem.text.strip()
            
            # Get rating information
            rating_elem = soup.find('div', class_='rating-restaurant')
            if rating_elem:
                details['rating'] = {
                    'score': rating_elem.find('span', class_='rating-score').text.strip() if rating_elem.find('span', class_='rating-score') else None,
                    'count': rating_elem.find('span', class_='rating-count').text.strip() if rating_elem.find('span', class_='rating-count') else None
                }
            
            # Get price range
            price_elem = soup.find('div', class_='price-restaurant')
            if price_elem:
                details['price_range'] = price_elem.text.strip()
            
            # Get categories/cuisines
            categories = soup.find_all('div', class_='category-restaurant')
            if categories:
                details['categories'] = [cat.text.strip() for cat in categories]
            
            return details
            
        except Exception as e:
            logging.error(f"Error extracting restaurant details: {str(e)}")
            return {}

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
                    
                    # Add menu information by parsing restaurant page
                    if restaurant["url"]:
                        menu_info = self.get_restaurant_menu(restaurant["url"])
                        restaurant["menu"] = menu_info
                        
                        # Add small delay between requests
                        time.sleep(random.uniform(1, 2))
                    
                    restaurants.append(restaurant)
                    logging.info(f"Extracted data for restaurant: {restaurant['name']}")
                    
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
            logging.info(f"Starting crawler, targeting {total_items} items")
            
            # Calculate number of pages needed
            total_pages = math.ceil(total_items / self.items_per_page)
            items_collected = 0
            current_page = 1
            
            while items_collected < total_items and current_page <= total_pages:
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
                
                # Move to next page
                current_page += 1
                
                # Random delay between pages
                if current_page <= total_pages:
                    delay = random.uniform(1, 3)
                    logging.info(f"Waiting {delay:.2f} seconds before next page...")
                    time.sleep(delay)
            
            logging.info(f"Crawling completed. Processed {items_collected} restaurants")
            
        except Exception as e:
            logging.error(f"Error in main crawler loop: {str(e)}")

    def test_api(self):
        """Test API response and print detailed information"""
        try:
            params = {
                "t": str(int(time.time() * 1000)),
                "page": 1,
                "lat": self.lat,
                "lon": self.lon,
                "count": self.items_per_page,
                "type": 1
            }
            
            logging.info("Testing API with parameters:")
            logging.info(json.dumps(params, indent=2))
            
            response = requests.get(
                self.api_url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            logging.info(f"Response Status Code: {response.status_code}")
            logging.info("Response Headers:")
            logging.info(json.dumps(dict(response.headers), indent=2))
            
            if response.status_code == 200:
                data = response.json()
                logging.info("\nAPI Response Data Structure:")
                logging.info(json.dumps(data, ensure_ascii=False, indent=2))
                
                if "Items" in data:
                    logging.info(f"\nTotal items in response: {len(data['Items'])}")
                    if data['Items']:
                        logging.info("\nExample of first item fields:")
                        logging.info(json.dumps(data['Items'][0], ensure_ascii=False, indent=2))
            else:
                logging.error(f"API returned error status: {response.status_code}")
                logging.error(f"Error response: {response.text[:500]}")
                
        except Exception as e:
            logging.error(f"Error testing API: {str(e)}")

if __name__ == "__main__":
    try:
        crawler = FoodyCrawler()
        # Test API first
        # crawler.test_api()
        crawler.run(100)  # Commented out for testing
    except Exception as e:
        logging.error(f"Critical error in main execution: {str(e)}") 