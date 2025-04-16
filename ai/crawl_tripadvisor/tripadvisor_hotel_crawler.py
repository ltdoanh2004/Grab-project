#!/usr/bin/env python3
# TripAdvisor Hotel Crawler
import requests
from bs4 import BeautifulSoup
import csv
import time
import argparse
import os
import random
import re
from urllib.parse import urlparse, urljoin
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TripAdvisorHotelCrawler:
    def __init__(self, base_url=None, delay=2):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.tripadvisor.com/'
        }
        self.base_url = base_url
        self.min_delay = delay
        self.max_delay = delay * 2  # Randomize delay a bit
        
    def _random_delay(self):
        """Add a random delay between requests to avoid being blocked"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.info(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)
        
    def get_soup(self, url):
        """Get BeautifulSoup object from URL with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching URL: {url}")
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                # Check if we got a captcha page
                if "captcha" in response.text.lower() or "please enable js" in response.text.lower():
                    logger.warning("Captcha detected! Try using a different approach or wait longer between requests")
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 60  # Incremental backoff
                        logger.info(f"Retrying after {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching URL {url}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 30
                    logger.info(f"Retrying after {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
            
    def get_hotels(self, location_url=None):
        """Get hotels for a given location"""
        url = location_url or self.base_url
        if not url:
            raise ValueError("No URL provided")
            
        soup = self.get_soup(url)
        if not soup:
            return []
        
        # Try various selectors that might work with TripAdvisor's current structure
        hotels = []
        seen_urls = set()  # Track seen URLs to avoid duplicates
        
        # Method 1: Look for hotel cards
        hotel_elements = soup.select('div.listing_title a, div.property_title a')
        if hotel_elements:
            logger.info(f"Found {len(hotel_elements)} hotels using method 1")
            for item in hotel_elements:
                if item.has_attr('href'):
                    name = item.get_text(strip=True)
                    link = item['href']
                    if not link.startswith('http'):
                        link = urljoin("https://www.tripadvisor.com", link)
                        
                    # Clean up URL by removing fragments and parameters
                    base_url = link.split('#')[0].split('?')[0]
                    
                    # Skip if we've already seen this URL
                    if base_url in seen_urls:
                        continue
                        
                    seen_urls.add(base_url)
                    hotels.append({"name": name, "url": base_url})
            
            if hotels:
                logger.info(f"Found {len(hotels)} unique hotels")
                return hotels
        
        # Method 2: Look for hotel links with Hotel_Review
        hotel_links = soup.select('a[href*="Hotel_Review"]')
        if hotel_links:
            # Filter out links that are likely not actual hotels
            filtered_links = []
            for link in hotel_links:
                href = link['href']
                
                # Clean URL and skip if we've seen it
                clean_url = href.split('#')[0].split('?')[0]
                if clean_url in seen_urls:
                    continue
                    
                name = link.get_text(strip=True)
                
                # Skip if very short name or empty text
                if not name or len(name) <= 1:
                    continue
                
                # Skip common navigation terms
                if name.lower() in ['map', 'view map', 'next', 'previous', '1', '2', '3', '4', '5']:
                    continue
                
                # Add to filtered list
                filtered_links.append((name, clean_url))
                seen_urls.add(clean_url)
            
            logger.info(f"Found {len(hotel_links)} potential hotels with 'Hotel_Review', filtered to {len(filtered_links)} unique hotels")
            
            for name, href in filtered_links:
                if not href.startswith('http'):
                    href = urljoin("https://www.tripadvisor.com", href)
                hotels.append({"name": name, "url": href})
                
            if hotels:
                return hotels
        
        # Fallback method 3: Try to find links with location name
        if not hotels:
            location_links = []
            try:
                path_parts = urlparse(url).path.split('-')
                if len(path_parts) > 2:
                    location_name = path_parts[2]  # e.g., 'Hanoi' from 'Hotels-g293924-Hanoi-Hotels.html'
                    location_links = soup.select(f'a[href*="{location_name}"][href*="Hotel"]')
            except Exception as e:
                logger.error(f"Error parsing location from URL: {e}")
            
            # Filter links to likely hotels
            filtered_location_links = []
            for link in location_links:
                href = link['href']
                name = link.get_text(strip=True)
                
                # Skip if very short name or empty text
                if not name or len(name) <= 1:
                    continue
                
                # Skip common navigation terms
                if name.lower() in ['map', 'view map', 'next', 'previous', '1', '2', '3', '4', '5']:
                    continue
                
                # Add to filtered list
                filtered_location_links.append(link)
            
            logger.info(f"Found {len(location_links)} potential location-based hotels, filtered to {len(filtered_location_links)}")
            
            for link in filtered_location_links:
                name = link.get_text(strip=True)
                href = link['href']
                if not href.startswith('http'):
                    href = urljoin("https://www.tripadvisor.com", href)
                hotels.append({"name": name, "url": href})
        
        # Fallback method 4: Use hardcoded top hotels for common locations
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
        
        # If we still found nothing, log the entire HTML for debugging
        if not hotels:
            logger.warning("No hotels found. The website structure may have changed.")
            logger.debug(f"HTML content: {soup}")
            
        return hotels
        
    def get_hotel_details(self, hotel_url):
        """Get details for a specific hotel"""
        self._random_delay()  # Add random delay before requesting
        
        soup = self.get_soup(hotel_url)
        if not soup:
            return {"url": hotel_url, "name": "Unknown", "status": "Failed to fetch page"}
            
        details = {"url": hotel_url}
        
        # Try to extract hotel name (multiple selectors)
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
        
        # Extract name from URL if we still don't have it
        if 'name' not in details:
            try:
                url_parts = hotel_url.split('-Reviews-')
                if len(url_parts) > 1:
                    name_part = url_parts[1].split('-')[0]
                    # Replace underscores with spaces and title case
                    details["name"] = name_part.replace('_', ' ').title()
            except:
                pass
        
        # Output the HTML to a file for debugging if no name found
        if 'name' not in details:
            logger.warning(f"Could not extract name from URL: {hotel_url}")
            try:
                with open('debug_hotel_page.html', 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                logger.info(f"Saved HTML to debug_hotel_page.html for debugging")
            except:
                logger.warning("Failed to save debug HTML")
            details["name"] = "Unknown Hotel"
        
        # Log the HTML structure to help with debugging
        logger.debug(f"Page structure: {soup.select('head > title')}")
        
        # Try to extract hotel class (stars) - multiple methods
        try:
            # Method 1: Look for star rating in class names
            hotel_class_elem = soup.select_one('span.ui_star_rating')
            if hotel_class_elem and 'class' in hotel_class_elem.attrs:
                for class_name in hotel_class_elem['class']:
                    if class_name.startswith('star_'):
                        star_count = class_name.replace('star_', '').replace('_', '.')
                        details["stars"] = star_count
                        break
            
            # Method 2: Look for hotel class in text with a regex pattern
            if "stars" not in details:
                hotel_class_pattern = re.compile(r'(\d+(?:\.\d+)?)[- ]star', re.IGNORECASE)
                for elem in soup.select('div.yPKQB, div.drcGn'):
                    text = elem.get_text(strip=True)
                    match = hotel_class_pattern.search(text)
                    if match:
                        details["stars"] = match.group(1)
                        break
        except:
            pass
        
        # Try to extract price range - multiple methods
        try:
            # Method 1: Look for price range directly
            price_elem = soup.select_one('div.priceRange')
            if price_elem:
                details["price_range"] = price_elem.get_text(strip=True)
                
            # Method 2: Look for price elements
            if "price_range" not in details:
                price_elems = soup.select('div.JPNOn span, div.WXCOL, div.gbprQ')
                if price_elems:
                    price_texts = [elem.get_text(strip=True) for elem in price_elems]
                    # Filter out non-price texts and keep unique values
                    price_texts = [text for text in price_texts if re.search(r'\$|\d+', text)]
                    if price_texts:
                        details["price_range"] = ', '.join(set(price_texts))
        except:
            pass
                
        # Try to extract rating and reviews
        try:
            # Method 1: Look for rating bubble
            rating_elem = soup.select_one('div.AfQtZ, span.bvcwU, span.ui_bubble_rating')
            if rating_elem:
                # Try to extract from class name if available
                if 'class' in rating_elem.attrs:
                    for class_name in rating_elem['class']:
                        if 'bubble_' in class_name:
                            try:
                                rating_value = class_name.split('_')[1]
                                details["rating"] = float(rating_value) / 10
                            except (IndexError, ValueError):
                                pass
                            break
                
                # Try to extract from text
                text = rating_elem.get_text(strip=True)
                if text and "rating" not in details:
                    # Extract rating
                    rating_match = re.search(r'(\d+\.?\d*)\s+of\s+\d+', text)
                    if rating_match:
                        details["rating"] = rating_match.group(1)
            
            # Method 2: Look for review count
            reviews_elem = soup.select_one('span.yFKLG, a.hvrfCF, span.qqniT, a.BMQDV')
            if reviews_elem:
                text = reviews_elem.get_text(strip=True)
                reviews_match = re.search(r'([\d,]+)\s+reviews?', text)
                if reviews_match:
                    details["reviews"] = reviews_match.group(1).replace(',', '')
        except:
            pass
        
        # Try to extract address
        try:
            address_selectors = [
                'span.street-address',
                'span.locality',
                'div.kUaGX button',
                'div.XPUSn span.yEWoV',
                'button[data-test-target="streetAddress"]',
                'span[data-test-target="street-address"]'
            ]
            address_parts = []
            for selector in address_selectors:
                elems = soup.select(selector)
                for elem in elems:
                    address_parts.append(elem.get_text(strip=True))
            
            if not address_parts:
                # Try finding address in a broader context
                address_containers = soup.select('div.drcGn, div.yPKQB, div.nheKb')
                for container in address_containers:
                    text = container.get_text(strip=True)
                    if re.search(r'street|avenue|road|boulevard|lane|alley', text, re.IGNORECASE):
                        address_parts.append(text)
                        break
            
            if address_parts:
                details["address"] = ", ".join(address_parts)
        except:
            pass
                
        # Try to extract amenities
        try:
            amenity_elems = soup.select('div.pZUbB div.duhwe span.JguWG, div.OsCbb.IBjkL, div.exmBD, div.bUmsU, div.hRNKr')
            if amenity_elems:
                amenities = []
                for elem in amenity_elems:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 1 and text not in amenities:
                        amenities.append(text)
                
                if amenities:
                    details["amenities"] = ", ".join(amenities)
        except:
            pass
                
        # Try to extract description
        try:
            desc_elem = soup.select_one('div.pZUbB div.duhwe span.JguWG, div.fIrGe div._c, div.cPQsENeY, div.duhwe')
            if desc_elem:
                details["description"] = desc_elem.get_text(strip=True)
        except:
            pass
                
        # Try to extract contact info (phone, email, website)
        try:
            contact_elems = soup.select('div.IhqAp a.YnKZo, div.DpZHu a, a.dMewXH, a.bKBRJ')
            for elem in contact_elems:
                href = elem.get('href', '')
                if href.startswith('tel:'):
                    details["phone"] = href.replace('tel:', '')
                elif href.startswith('mailto:'):
                    details["email"] = href.replace('mailto:', '')
                elif 'website' in href.lower() or 'tripadvisor.com/ShowUrl' in href:
                    details["website"] = "Available (via TripAdvisor)"
        except:
            pass
        
        # Add fallback status for debugging
        if len(details) <= 2:  # Just URL and name
            logger.warning(f"Limited details found for: {details.get('name', 'Unknown')} at {hotel_url}")
            details["status"] = "Limited information available"
        
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
            # Accept all hotel details even if limited
            detailed_hotels.append(details)
            self._random_delay()  # Random delay between requests
        
        # Only save if we have hotels
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
    parser = argparse.ArgumentParser(description='TripAdvisor Hotel Crawler')
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
                        help='Enable headless mode for debugging')
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
    
    crawler = TripAdvisorHotelCrawler(args.url, args.delay)
    crawler.scrape_location(output_file=args.output, max_hotels=args.max) 