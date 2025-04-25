import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
from urllib.parse import urljoin
import argparse
import re
from datetime import datetime, timedelta
import os

class HotelCrawler:
    def __init__(self, debug=False):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.base_url = "https://www.booking.com"
        self.last_save_time = time.time()
        self.hotels_since_last_save = 0
        self.debug = debug
        self.debug_counter = 0
        
    def log(self, message, always=False):
        """Log message if in debug mode or if always=True"""
        if self.debug or always:
            print(message)

    def get_hotel_detail(self, url):
        """Get detailed information from hotel page"""
        try:
            self.log(f"\nFetching details from: {url}")
            time.sleep(random.uniform(2, 4))
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Get facilities
            facilities = []
            facility_elements = soup.find_all('div', {'data-testid': 'facility-list-item'})
            for facility in facility_elements:
                facilities.append(facility.text.strip())
                
            # Get description
            description_text = 'N/A'
            description_elem = soup.find('p', {'data-testid': 'property-description'})
            if description_elem:
                description_text = description_elem.text.strip()
                self.log("\nFound description:", description_text)
            else:
                self.log("\nNo description element found")
            
            # Get price from detail page (useful when search page price isn't available)
            detail_price = None
            # Method 1: Check for price in multiple formats
            price_elements = soup.find_all('span', {'class': lambda x: x and (('price' in x.lower() or 'amount' in x.lower()) if x else False)})
            for elem in price_elements:
                if elem.text and any(char.isdigit() for char in elem.text):
                    detail_price = elem.text.strip()
                    self.log(f"\nFound price in detail page: {detail_price}")
                    break
                    
            # Method 2: Check for elements containing price with currency symbols
            if not detail_price:
                currency_elements = soup.find_all(['span', 'div'], text=lambda x: x and ('₫' in x or 'VND' in x or '$' in x or '€' in x))
                for elem in currency_elements:
                    if elem.text and any(char.isdigit() for char in elem.text):
                        detail_price = elem.text.strip()
                        self.log(f"\nFound price with currency symbol: {detail_price}")
                        break
            
            # Get images
            images = []
            image_elements = soup.find_all('img', {'class': ['e3fa9175ee', 'd354f8f44f', 'ba6d792fd4', 'b1a5e281e7']})
            for img in image_elements:
                if img.get('src') and 'hotel' in img.get('src'):
                    image_url = img['src']
                    if '?' in image_url:
                        image_url = image_url.split('?')[0]
                    images.append({
                        'url': image_url,
                        'alt': img.get('alt', '')
                    })
            self.log(f"\nFound {len(images)} images")
            
            # Get room types
            rooms = []
            # Find the table containing room information
            room_table = soup.find('table', {'id': 'hprt-table'})
            if room_table:
                room_rows = room_table.find_all('tr', {'class': 'js-rt-block-row'})
                for room in room_rows:
                    room_data = {}
                    
                    # Get room name
                    room_name = room.find('span', {'class': 'hprt-roomtype-icon-link'})
                    room_data['name'] = room_name.text.strip() if room_name else 'N/A'
                    
                    # Get bed type
                    bed_info = room.find('span', {'class': 'wholesalers_table__bed_options_text'})
                    room_data['bed_type'] = bed_info.text.strip() if bed_info else 'N/A'
                    
                    # Get price information
                    price_cell = room.find('td', {'class': 'hprt-table-cell-price'})
                    if price_cell:
                        # Get main price
                        price_display = price_cell.find('span', {'class': 'prco-valign-middle-helper'})
                        room_data['price'] = price_display.text.strip() if price_display else 'N/A'
                        
                        # Get taxes and fees
                        taxes = price_cell.find('div', {'class': 'prd-taxes-and-fees-under-price'})
                        if taxes:
                            room_data['taxes_and_fees'] = taxes.text.strip()
                            # Get raw charges
                            charges_raw = taxes.get('data-excl-charges-raw')
                            if charges_raw:
                                room_data['charges_raw'] = charges_raw
                    
                    # Get occupancy
                    occupancy_cell = room.find('td', {'class': 'hprt-table-cell-occupancy'})
                    if occupancy_cell:
                        room_data['occupancy'] = occupancy_cell.text.strip()
                    
                    # Get conditions/cancellation policy
                    conditions_cell = room.find('td', {'class': 'hprt-table-cell-conditions'})
                    if conditions_cell:
                        room_data['conditions'] = conditions_cell.text.strip()
                    
                    rooms.append(room_data)
                    self.log(f"\nRoom details: {room_data}")

            return {
                'facilities': facilities,
                'description': description_text,
                'images': images,
                'rooms': rooms,
                'detail_price': detail_price
            }
        except Exception as e:
            self.log(f"Error getting hotel detail: {e}", always=True)
            return None

    def save_checkpoint(self, hotels, output_base, current_page):
        """Save data checkpoint with timestamp"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        checkpoint_base = f"{output_base}_page{current_page}_{timestamp}"
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_base)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            self.log(f"Created directory: {output_dir}", always=True)
            
        self.save_to_csv(hotels, filename=f'{checkpoint_base}.csv')
        self.last_save_time = time.time()
        self.hotels_since_last_save = 0
        self.log(f"Saved checkpoint: {checkpoint_base}", always=True)
        return checkpoint_base

    def get_hotel_data(self, url, start_page=1, end_page=5, output_base='hotels', save_interval_mins=30, save_interval_hotels=50):
        all_hotels = []
        current_page = start_page
        
        self.log(f"\nStarting crawl from page {start_page} to page {end_page}", always=True)
        self.log(f"Auto-save settings: Every {save_interval_mins} mins or {save_interval_hotels} hotels")
        
        # Check if URL is a city page and convert to search results URL
        if '/city/' in url and 'searchresults' not in url:
            self.log("Detected city URL, converting to search results URL...", always=True)
            try:
                # Extract city name and country code from URL
                city_match = re.search(r'/city/([^/]+)/([^.]+)', url)
                if city_match:
                    country_code = city_match.group(1)
                    city_name = city_match.group(2)
                    self.log(f"Extracted country: {country_code}, city: {city_name}", always=True)
                    
                    # Replace hyphens with spaces for the search query
                    city_name_for_search = city_name.replace('-', ' ')
                    
                    # Get date parameters from current date if not in URL
                    today = datetime.now()
                    tomorrow = today + timedelta(days=1)
                    checkin_date = today.strftime('%Y-%m-%d')
                    checkout_date = tomorrow.strftime('%Y-%m-%d')
                    
                    # Construct search URL with destination
                    if '?' in url:
                        query_params = url.split('?')[1]
                        search_url = f"https://www.booking.com/searchresults.vi.html?ss={city_name_for_search}&dest_id=&dest_type=city&checkin={checkin_date}&checkout={checkout_date}&group_adults=2&no_rooms=1&group_children=0&{query_params}"
                    else:
                        search_url = f"https://www.booking.com/searchresults.vi.html?ss={city_name_for_search}&dest_id=&dest_type=city&checkin={checkin_date}&checkout={checkout_date}&group_adults=2&no_rooms=1&group_children=0"
                    
                    self.log(f"Redirecting to search URL: {search_url}", always=True)
                    url = search_url
                else:
                    self.log("Could not extract city name from URL", always=True)
            except Exception as e:
                self.log(f"Error converting city URL: {e}", always=True)
        
        while current_page <= end_page:
            try:
                self.log(f"\nCrawling page {current_page}...", always=True)
                if current_page > 1:
                    if '?' in url:
                        page_url = f"{url}&offset={25 * (current_page-1)}"
                    else:
                        page_url = f"{url}?offset={25 * (current_page-1)}"
                else:
                    page_url = url
                
                time.sleep(random.uniform(1, 3))
                try:
                    response = requests.get(page_url, headers=self.headers, timeout=30)
                    response.raise_for_status()
                    
                    # Save HTML for debugging if needed
                    if self.debug:
                        self.save_debug_html(response.text, prefix=f"page_{current_page}")
                    
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Try different selectors for hotel elements as Booking.com might change its layout
                    hotel_elements = soup.find_all('div', {'data-testid': 'property-card'})
                    
                    if not hotel_elements:
                        # Try alternative selectors
                        self.log("No property cards found with primary selector, trying alternatives...", always=True)
                        
                        # Alternative 1: Search for hotel cards by class
                        hotel_elements = soup.find_all('div', {'class': 'sr_property_block'})
                        
                        # Alternative 2: Search for hotel cards by id pattern
                        if not hotel_elements:
                            hotel_elements = soup.find_all('div', id=lambda x: x and x.startswith('hotel_'))
                            
                        # Alternative 3: Look for any div with hotel data
                        if not hotel_elements:
                            hotel_elements = soup.find_all('div', {'data-hotelid': True})
                    
                    if not hotel_elements:
                        # Check if we're redirected to another page by looking for common Booking.com elements
                        if soup.find('div', {'id': 'basiclayout'}) or soup.find('div', {'id': 'bodyconstraint'}):
                            self.log("Page seems to be a valid Booking.com page but no hotel elements found.", always=True)
                            self.log("The URL might be a city page or another non-search page.", always=True)
                            self.log("Trying to find search results link...", always=True)
                            
                            # Try to find search link
                            search_link = soup.find('a', {'data-testid': 'search-results-link'})
                            if search_link and 'href' in search_link.attrs:
                                next_url = urljoin(self.base_url, search_link['href'])
                                self.log(f"Found search link: {next_url}", always=True)
                                self.log("Please restart the crawler with this URL", always=True)
                                break
                        
                        self.log("No hotel elements found. The page structure might have changed or no results exist.", always=True)
                        break
                    
                    self.log(f"Found {len(hotel_elements)} hotels on page {current_page}")
                    
                    for idx, hotel in enumerate(hotel_elements, 1):
                        try:
                            detail_link = None
                            title_link = hotel.find('a', {'data-testid': 'title-link'})
                            if title_link and 'href' in title_link.attrs:
                                detail_link = urljoin(self.base_url, title_link['href'])
                            else:
                                self.log(f"Could not find hotel link for hotel {idx} on page {current_page}")
                                continue
                            
                            self.log(f"\nProcessing hotel {idx}/{len(hotel_elements)} on page {current_page}")
                            self.log(f"Detail link: {detail_link}")
                            
                            # Get basic info from search results page
                            name_div = hotel.find('div', {'data-testid': 'title'})
                            name = name_div.text.strip() if name_div else 'N/A'
                            
                            # Try multiple selectors for price in search results page
                            price = 'N/A'
                            original_price = 'N/A'
                            discounted_price = 'N/A'
                            
                            # Method 1: Look for price with class based on the screenshot
                            price_span = hotel.find('span', {'class': lambda x: x and ('d746e3a28e' in x if x else False)})
                            if price_span:
                                price = price_span.text.strip()
                                self.log(f"Found price using class selector: {price}")
                            
                            # Method 2: Look for price with data-testid
                            if price == 'N/A':
                                price_elem = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
                                if price_elem:
                                    price = price_elem.text.strip()
                                    self.log(f"Found price using data-testid: {price}")
                            
                            # Method 3: Look for any element with price in its class name
                            if price == 'N/A':
                                price_elems = hotel.find_all('span', {'class': lambda x: x and ('price' in x.lower() if x else False)})
                                if price_elems:
                                    price = price_elems[0].text.strip()
                                    self.log(f"Found price using general class search: {price}")
                            
                            # Get original price if available
                            original_price_elem = hotel.find('span', {'data-testid': 'price-for-x-nights'})
                            if original_price_elem:
                                original_price = original_price_elem.text.strip()
                            
                            # Get discounted price if available
                            discounted_price_elem = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
                            if discounted_price_elem:
                                discounted_price = discounted_price_elem.text.strip()
                            
                            # Get tax information
                            tax_info = 'N/A'
                            tax_info_elem = hotel.find('div', {'data-testid': 'taxes-and-charges'})
                            if tax_info_elem:
                                tax_info = tax_info_elem.text.strip()
                            
                            # Get room info from listing
                            room_info = 'N/A'
                            room_info_elem = hotel.find('div', text=lambda x: x and ('đêm' in x.lower() if x else False))
                            if room_info_elem:
                                room_info = room_info_elem.text.strip()
                                self.log(f"Found room info: {room_info}")
                            
                            # Get rating
                            rating = 'N/A'
                            rating_elem = hotel.find('div', {'data-testid': 'review-score'})
                            if rating_elem:
                                rating = rating_elem.text.strip()
                            
                            # Get location
                            location = 'N/A'
                            location_elem = hotel.find('span', {'data-testid': 'address'})
                            if location_elem:
                                location = location_elem.text.strip()
                            
                            # Now get detailed info only if needed
                            hotel_details = self.get_hotel_detail(detail_link)
                            
                            hotel_data = {
                                'name': name,
                                'link': detail_link,
                                'price': price,
                                'original_price': original_price,
                                'discounted_price': discounted_price,
                                'tax_info': tax_info,
                                'room_info': room_info,
                                'rating': rating,
                                'location': location,
                            }
                            
                            if hotel_details:
                                # Add detailed information
                                hotel_data.update({
                                    'facilities': hotel_details['facilities'],
                                    'description': hotel_details['description'],
                                    'images': hotel_details['images'],
                                    'room_types': hotel_details['rooms']
                                })
                                
                                # Use price from detail page if not found in search results
                                if (price == 'N/A' or not price) and hotel_details.get('detail_price'):
                                    hotel_data['price'] = hotel_details['detail_price']
                                    hotel_data['price_source'] = 'detail_page'
                                else:
                                    hotel_data['price_source'] = 'search_page'
                            else:
                                # Add default values if detailed info couldn't be fetched
                                hotel_data.update({
                                    'facilities': [],
                                    'description': 'N/A',
                                    'images': [],
                                    'room_types': []
                                })
                            
                            all_hotels.append(hotel_data)
                            self.hotels_since_last_save += 1
                            self.log(f"Successfully crawled: {name}")
                            
                            time_since_last_save = time.time() - self.last_save_time
                            if time_since_last_save >= save_interval_mins * 60 or self.hotels_since_last_save >= save_interval_hotels:
                                self.log(f"\nAuto-saving checkpoint...", always=True)
                                self.save_checkpoint(all_hotels, output_base, current_page)
                            
                            time.sleep(random.uniform(2, 4))
                            
                        except Exception as e:
                            self.log(f"Error parsing hotel data: {e}", always=True)
                            continue
                
                except requests.exceptions.RequestException as e:
                    self.log(f"Error making request: {e}", always=True)
                    time.sleep(5)  # Wait longer before retrying
                    continue
                except Exception as e:
                    self.log(f"Unexpected error: {e}", always=True)
                    time.sleep(5)
                    continue
                
                current_page += 1
                
            except Exception as e:
                self.log(f"Error fetching page {current_page}: {e}", always=True)
                if all_hotels:
                    self.log("\nSaving checkpoint due to error...", always=True)
                    self.save_checkpoint(all_hotels, output_base, current_page-1)
                break
        
        self.log(f"\nCrawl completed. Total hotels collected: {len(all_hotels)}", always=True)
        final_base = f"{output_base}_final"
        self.save_to_csv(all_hotels, filename=f'{final_base}.csv')
        return all_hotels

    def save_to_csv(self, hotels, filename='hotels.csv'):
        if hotels:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.log(f"Created directory: {output_dir}", always=True)
            
            # Flatten the facilities into a string
            flattened_hotels = []
            for hotel in hotels:
                hotel_copy = hotel.copy()
                
                # Convert facilities list to string
                hotel_copy['facilities'] = ' | '.join(hotel_copy['facilities'])
                
                # Remove rooms data
                if 'rooms' in hotel_copy:
                    del hotel_copy['rooms']
                
                flattened_hotels.append(hotel_copy)
            
            df = pd.DataFrame(flattened_hotels)
            df.to_csv(filename, index=False, encoding='utf-8')
            self.log(f"\nData saved to {filename}")
            
            # Save raw JSON data
            json_filename = filename.replace('.csv', '.json')
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(hotels, f, ensure_ascii=False, indent=2)
            self.log(f"Raw data saved to {json_filename}")
        else:
            self.log("No data to save")

    def save_debug_html(self, html_content, prefix="debug"):
        """Save HTML content to file for debugging"""
        if self.debug:
            self.debug_counter += 1
            
            # Create debug directory if it doesn't exist
            debug_dir = "debug_html"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir, exist_ok=True)
                self.log(f"Created debug directory: {debug_dir}", always=True)
            
            filename = os.path.join(debug_dir, f"{prefix}_{self.debug_counter}_{time.strftime('%Y%m%d_%H%M%S')}.html")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.log(f"Saved debug HTML to {filename}", always=True)

def main():
    parser = argparse.ArgumentParser(description='Crawl hotel data from Booking.com')
    parser.add_argument('--url', type=str, default="https://www.booking.com/searchresults.vi.html?aid=304142&label=gen173nr-1FCAQoggJCEHNlYXJjaF9ow6AgbuG7mWlIKlgEaPQBiAEBmAEquAEHyAEM2AEB6AEB-AEDiAIBqAIDuAKV75HABsACAdICJDJjNTc3NTFlLTBkZjctNGFiOC05MjlhLTk3ZTJlYzBhMmE2ZtgCBeACAQ&sid=7834fe4d42ec780609444a0dd3917e20&checkin=2025-04-22&checkout=2025-04-23&dest_id=-3714993&dest_type=city&srpvid=29061d4dc37a0049&",
                        help='URL to crawl')
    parser.add_argument('--start-page', type=int, default=1,
                        help='Starting page number (default: 1)')
    parser.add_argument('--end-page', type=int, default=100,
                        help='Ending page number (default: 100)')
    parser.add_argument('--output', type=str, default='data_hotels',
                        help='Output filename without extension (default: data_hotels)')
    parser.add_argument('--save-interval-mins', type=int, default=30,
                        help='Save checkpoint every N minutes (default: 30)')
    parser.add_argument('--save-interval-hotels', type=int, default=50,
                        help='Save checkpoint every N hotels (default: 50)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    
    args = parser.parse_args()
    
    crawler = HotelCrawler(debug=args.debug)
    hotels = crawler.get_hotel_data(
        args.url, 
        start_page=args.start_page, 
        end_page=args.end_page,
        output_base=args.output,
        save_interval_mins=args.save_interval_mins,
        save_interval_hotels=args.save_interval_hotels
    )

if __name__ == "__main__":
    main() 