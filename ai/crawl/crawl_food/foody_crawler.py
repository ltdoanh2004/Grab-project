import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import logging
import random
import time
import re
from typing import List, Dict, Any, Optional, Tuple
import os
import math
import argparse
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('foody_crawler.log'),
        logging.StreamHandler()
    ]
)

# Predefined locations
LOCATIONS = {
    "hanoi": {"lat": 21.033333, "lon": 105.85, "name": "Hà Nội", "path": "ha-noi"},
    "hochiminh": {"lat": 10.762622, "lon": 106.660172, "name": "Hồ Chí Minh", "path": "ho-chi-minh"},
    "danang": {"lat": 16.047079, "lon": 108.206230, "name": "Đà Nẵng", "path": "da-nang"},
    "haiphong": {"lat": 20.844912, "lon": 106.688084, "name": "Hải Phòng", "path": "hai-phong"},
    "nhatrang": {"lat": 12.238791, "lon": 109.196749, "name": "Nha Trang", "path": "nha-trang"},
    "cantho": {"lat": 10.045162, "lon": 105.746857, "name": "Cần Thơ", "path": "can-tho"},
    "khanhhoa": {"lat": 12.239507, "lon": 109.196717, "name": "Khánh Hòa", "path": "khanh-hoa"},
    "vungtau": {"lat": 10.346616, "lon": 107.084419, "name": "Vũng Tàu", "path": "vung-tau"},
    "binhthuan": {"lat": 10.933009, "lon": 108.102547, "name": "Bình Thuận", "path": "binh-thuan"},
    "lamdong": {"lat": 11.940419, "lon": 108.458313, "name": "Lâm Đồng", "path": "lam-dong"},
}

class FoodyCrawler:
    def __init__(self, location="hanoi", start_page=1, output_dir=None):
        self.api_url = "https://www.foody.vn/__get/Place/HomeListPlace"
        self.base_url = "https://www.foody.vn"
        self.output_dir = output_dir or "data"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://www.foody.vn",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        # Set location coordinates
        if location in LOCATIONS:
            location_data = LOCATIONS[location]
            self.location = location
            self.lat = location_data["lat"]
            self.lon = location_data["lon"]
            self.location_name = location_data["name"]
            self.location_path = location_data["path"]
        else:
            # Default to Hanoi if invalid location
            self.location = "hanoi"
            self.lat = LOCATIONS["hanoi"]["lat"]
            self.lon = LOCATIONS["hanoi"]["lon"]
            self.location_name = LOCATIONS["hanoi"]["name"]
            self.location_path = LOCATIONS["hanoi"]["path"]
            logging.warning(f"Invalid location '{location}'. Using default location: {self.location_name}")
        
        self.items_per_page = 12  # Default items per page from API
        self.start_page = start_page
        
        # Setup output directory with location subfolder
        self.output_dir = os.path.join(self.output_dir, self.location)
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

    def get_location_url(self):
        """Get the base URL for the current location"""
        return f"{self.base_url}/{self.location_path}"
        
    def get_page_data(self, page: int = 1) -> List[Dict]:
        """Fetch restaurant data from a specific page"""
        try:
            # Add timestamp to avoid caching
            timestamp = str(int(time.time() * 1000))
            
            # API parameters - Điều chỉnh tham số API chính xác
            params = {
                "t": timestamp,
                "page": page,
                "lat": self.lat,
                "lon": self.lon,
                "count": self.items_per_page,
                "type": 1,
                "cityId": "",  # Không cần thiết lập cityId
                "districtId": "",
                "categoryId": "",
                "cuisineId": "",
                "isReputation": "false",
                "SortType": 1
            }
            
            logging.info(f"Fetching page {page} for location: {self.location_name}")
            
            # Sử dụng header phù hợp với trang foody
            headers = self.headers.copy()
            headers["Referer"] = self.get_location_url()
            
            response = requests.get(
                self.api_url,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            # Xử lý response
            data = response.json()
            items = data.get("Items", [])
            total_items = data.get("Total", 0)
            
            logging.info(f"API returned {len(items)} items out of {total_items} total for {self.location_name}")
            
            if not items:
                logging.warning(f"No items found on page {page} for {self.location_name}")
                return []
                
            restaurants = []
            for item in items:
                try:
                    restaurant = self._extract_restaurant_data(item)
                    restaurants.append(restaurant)
                    logging.info(f"Extracted data for restaurant: {restaurant['name']}")
                    
                    # Add small delay between requests
                    time.sleep(random.uniform(0.2, 0.5))
                    
                except Exception as e:
                    logging.error(f"Error processing restaurant item: {str(e)}")
                    continue
                    
            return restaurants
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page {page}: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logging.error(f"API Response: {e.response.status_code}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error fetching page {page}: {str(e)}")
            return []

    def _extract_restaurant_data(self, item: Dict) -> Dict:
        """Extract restaurant data from API response item"""
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
                "lon": item.get("Longitude"),
                "city": self.location_name,
                "path": self.location_path
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
        
        return restaurant

    def extract_restaurant_id_from_url(self, url: str) -> Optional[int]:
        """Extract restaurant ID from Foody URL"""
        try:
            # Try different URL patterns
            patterns = [
                r'\/(\d+)(-|_)', # Pattern like /123-restaurant-name
                r'Id=(\d+)',     # Pattern like ?Id=123
                r'id=(\d+)'      # Pattern like ?id=123
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return int(match.group(1))
                    
            logging.warning(f"Could not extract restaurant ID from URL: {url}")
            return None
            
        except Exception as e:
            logging.error(f"Error extracting restaurant ID from URL: {str(e)}")
            return None
            
    def get_restaurant_by_url(self, url: str) -> Optional[Dict]:
        """Fetch restaurant data by URL"""
        try:
            # Extract restaurant ID from URL
            restaurant_id = self.extract_restaurant_id_from_url(url)
            if not restaurant_id:
                logging.error(f"Failed to extract restaurant ID from URL: {url}")
                return None
                
            # Check if URL is relative or absolute
            if not url.startswith("http"):
                url = f"{self.base_url}{url}"
                
            logging.info(f"Fetching restaurant data for ID: {restaurant_id}, URL: {url}")
            
            # First, fetch the HTML page to get restaurant data
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info from the page
            name = soup.select_one('.main-h1')
            name = name.text.strip() if name else "Unknown Restaurant"
            
            address = soup.select_one('.res-common-add')
            address = address.text.strip() if address else ""
            
            rating_element = soup.select_one('.microsite-top-points')
            rating = float(rating_element.text.strip()) if rating_element else None
            
            # Get coordinates from script tag if available
            lat, lon = self._extract_coordinates_from_html(soup)
            
            # Create restaurant object
            restaurant = {
                "id": restaurant_id,
                "name": name,
                "address": address,
                "rating": rating,
                "url": url,
                "location": {
                    "lat": lat,
                    "lon": lon,
                    "city": self.location_name,
                    "path": self.location_path
                },
                "crawled_at": datetime.now().isoformat(),
                "crawled_from_url": True
            }
            
            # Try to extract more data like reviews, photos, etc.
            # This may require additional API calls based on restaurant ID
            
            return restaurant
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching restaurant from URL {url}: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error fetching restaurant from URL {url}: {str(e)}")
            return None
            
    def _extract_coordinates_from_html(self, soup: BeautifulSoup) -> Tuple[Optional[float], Optional[float]]:
        """Extract coordinates from HTML"""
        try:
            # Look for script tags that might contain coordinates
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('var markerlat' in script.string or 'var lng' in script.string):
                    lat_match = re.search(r'var\s+markerlat\s*=\s*([0-9.]+)', script.string)
                    lon_match = re.search(r'var\s+markerlng\s*=\s*([0-9.]+)', script.string)
                    
                    if lat_match and lon_match:
                        return float(lat_match.group(1)), float(lon_match.group(1))
                        
            return None, None
        except Exception as e:
            logging.error(f"Error extracting coordinates: {str(e)}")
            return None, None

    def save_data(self, data: Dict[str, Any]):
        """Save restaurant data to JSON file"""
        if not data or not data.get('name'):
            logging.error("Cannot save data: missing restaurant name")
            return
            
        safe_name = re.sub(r'[^\w\s-]', '', data['name'].lower())
        safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Include restaurant ID in filename if available
        restaurant_id = data.get('id', '')
        if restaurant_id:
            filename = f"{restaurant_id}_{safe_name}_{timestamp}.json"
        else:
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
            logging.info(f"Starting crawler for {self.location_name} from page {self.start_page}, targeting {total_items} items")
            
            # Calculate number of pages needed
            total_pages = math.ceil(total_items / self.items_per_page)
            items_collected = 0
            current_page = self.start_page
            max_empty_pages = 5  # Maximum consecutive empty pages before giving up
            empty_pages_count = 0
            
            while items_collected < total_items and current_page <= (self.start_page + total_pages - 1):
                # Get restaurants from current page
                restaurants = self.get_page_data(current_page)
                
                if not restaurants:
                    empty_pages_count += 1
                    logging.warning(f"Page {current_page} returned no restaurants. Empty page count: {empty_pages_count}/{max_empty_pages}")
                    
                    if empty_pages_count >= max_empty_pages:
                        logging.warning(f"Reached {max_empty_pages} consecutive empty pages. Stopping crawler.")
                        break
                else:
                    # Reset empty pages counter if we found restaurants
                    empty_pages_count = 0
                
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
    
    def crawl_from_urls(self, urls: List[str]):
        """
        Crawl restaurants from specific URLs
        Args:
            urls: List of Foody restaurant URLs to crawl
        """
        try:
            logging.info(f"Starting URL-based crawler for {len(urls)} URLs")
            
            items_collected = 0
            
            for url in urls:
                try:
                    # Get restaurant data from URL
                    restaurant = self.get_restaurant_by_url(url)
                    
                    if restaurant:
                        # Save the data
                        self.save_data(restaurant)
                        items_collected += 1
                        
                        # Progress update
                        logging.info(f"Progress: {items_collected}/{len(urls)} URLs processed")
                    else:
                        logging.warning(f"Failed to get data for URL: {url}")
                    
                    # Random delay between requests
                    delay = random.uniform(2, 4)
                    logging.info(f"Waiting {delay:.2f} seconds before next URL...")
                    time.sleep(delay)
                    
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {str(e)}")
                    continue
            
            logging.info(f"URL crawling completed. Processed {items_collected}/{len(urls)} URLs")
            
        except Exception as e:
            logging.error(f"Error in URL crawler loop: {str(e)}")

    def crawl_by_location_path(self, pages=5):
        """
        Crawl restaurants by directly scraping the location's page
        Args:
            pages: Number of pages to crawl
        """
        try:
            location_url = self.get_location_url()
            logging.info(f"Starting location-path based crawler for {self.location_name} at {location_url}")
            
            items_collected = 0
            
            for page in range(1, pages + 1):
                try:
                    # Build page URL
                    page_url = f"{location_url}?page={page}"
                    logging.info(f"Fetching page {page} at {page_url}")
                    
                    # Sử dụng User-Agent và header phù hợp
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Referer": self.base_url,
                        "Connection": "keep-alive"
                    }
                    
                    response = requests.get(
                        page_url,
                        headers=headers,
                        timeout=30
                    )
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Tìm kiếm các link nhà hàng dựa trên cấu trúc HTML của Foody
                    restaurant_links = []
                    
                    # Lấy tất cả các link chứa đường dẫn của tỉnh
                    location_path_pattern = f"/{self.location_path}/"
                    all_links = soup.find_all('a', href=lambda href: href and location_path_pattern in href)
                    
                    for link in all_links:
                        href = link.get('href')
                        if href and location_path_pattern in href:
                            # Bỏ qua các link không phải nhà hàng như Filter, Login, ...
                            skip_patterns = ['dang-nhap', 'filter', 'khuyen-mai', 'danh-sach', 'giao-hang', 'khach-hang']
                            if not any(pattern in href.lower() for pattern in skip_patterns):
                                # Make sure we have an absolute URL
                                if not href.startswith('http'):
                                    href = f"{self.base_url}{href}"
                                if href not in restaurant_links:  # Avoid duplicates
                                    restaurant_links.append(href)
                    
                    logging.info(f"Found {len(restaurant_links)} restaurant links on page {page}")
                    
                    # Nếu sử dụng API có hiệu quả hơn, hãy chuyển sang API
                    if len(restaurant_links) < 2:
                        logging.info(f"Few links found on page {page}, switching to API method")
                        api_restaurants = self.get_page_data(page)
                        for restaurant in api_restaurants:
                            self.save_data(restaurant)
                            items_collected += 1
                            logging.info(f"Progress (API): {items_collected} restaurants processed")
                        continue
                    
                    # Process each restaurant
                    for url in restaurant_links:
                        try:
                            restaurant = self.get_restaurant_by_url(url)
                            
                            if restaurant:
                                # Save the data
                                self.save_data(restaurant)
                                items_collected += 1
                                
                                # Progress update
                                logging.info(f"Progress: {items_collected} restaurants processed")
                            else:
                                logging.warning(f"Failed to get data for URL: {url}")
                            
                            # Random delay between requests
                            delay = random.uniform(1.0, 2.0)
                            logging.info(f"Waiting {delay:.2f} seconds before next restaurant...")
                            time.sleep(delay)
                            
                        except Exception as e:
                            logging.error(f"Error processing URL {url}: {str(e)}")
                            continue
                    
                    # Save progress after each page
                    self.save_progress(page, items_collected)
                    
                    # Random delay between pages
                    if page < pages:
                        delay = random.uniform(2, 3)
                        logging.info(f"Waiting {delay:.2f} seconds before next page...")
                        time.sleep(delay)
                    
                except Exception as e:
                    logging.error(f"Error processing page {page}: {str(e)}")
                    continue
            
            logging.info(f"Location-path crawling completed. Processed {items_collected} restaurants")
            
        except Exception as e:
            logging.error(f"Error in location path crawler: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Foody.vn Restaurant Crawler')
    parser.add_argument('--total-items', type=int, default=100,
                      help='Total number of restaurants to crawl')
    parser.add_argument('--start-page', type=int, default=1,
                      help='Page number to start crawling from')
    parser.add_argument('--location', type=str, default='hanoi',
                      help=f'Location to crawl. Options: {", ".join(LOCATIONS.keys())}')
    parser.add_argument('--output-dir', type=str, default='data',
                      help='Directory to save crawled data')
    parser.add_argument('--urls', type=str, default=None,
                      help='File containing list of URLs to crawl (one URL per line)')
    parser.add_argument('--url', type=str, default=None,
                      help='Single URL to crawl')
    parser.add_argument('--crawl-method', type=str, choices=['api', 'web'], default='api',
                      help='Method to use for crawling: api (using API) or web (using location URLs)')
    parser.add_argument('--pages', type=int, default=5,
                      help='Number of pages to crawl when using web crawling method')
    args = parser.parse_args()

    try:
        crawler = FoodyCrawler(
            location=args.location, 
            start_page=args.start_page,
            output_dir=args.output_dir
        )
        
        # URL-based crawling
        if args.url:
            crawler.crawl_from_urls([args.url])
        elif args.urls:
            try:
                with open(args.urls, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
                if urls:
                    crawler.crawl_from_urls(urls)
                else:
                    logging.error(f"No URLs found in file: {args.urls}")
            except Exception as e:
                logging.error(f"Error reading URLs from file {args.urls}: {str(e)}")
        else:
            # Choose crawling method
            if args.crawl_method == 'web':
                # Web-based crawling using location URL
                logging.info(f"Using web-based crawling for location: {args.location}")
                crawler.crawl_by_location_path(pages=args.pages)
            else:
                # Default API-based crawling
                logging.info(f"Using API-based crawling for location: {args.location}")
                crawler.run(args.total_items)
    except Exception as e:
        logging.error(f"Critical error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 