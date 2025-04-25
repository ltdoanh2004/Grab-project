import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
from urllib.parse import urljoin
import argparse

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
                'rooms': rooms
            }
        except Exception as e:
            self.log(f"Error getting hotel detail: {e}", always=True)
            return None

    def save_checkpoint(self, hotels, output_base, current_page):
        """Save data checkpoint with timestamp"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        checkpoint_base = f"{output_base}_page{current_page}_{timestamp}"
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
                response = requests.get(page_url, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                hotel_elements = soup.find_all('div', {'data-testid': 'property-card'})
                
                if not hotel_elements:
                    self.log("No more hotels found.", always=True)
                    break
                
                self.log(f"Found {len(hotel_elements)} hotels on page {current_page}")
                
                for idx, hotel in enumerate(hotel_elements, 1):
                    try:
                        detail_link = None
                        title_link = hotel.find('a', {'data-testid': 'title-link'})
                        if title_link and 'href' in title_link.attrs:
                            detail_link = urljoin(self.base_url, title_link['href'])
                            self.log(f"\nProcessing hotel {idx}/{len(hotel_elements)} on page {current_page}")
                            self.log(f"Detail link: {detail_link}")
                            
                            hotel_details = self.get_hotel_detail(detail_link)
                            if hotel_details:
                                name_div = hotel.find('div', {'data-testid': 'title'})
                                name = name_div.text.strip() if name_div else 'N/A'
                                
                                price_elem = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
                                price = price_elem.text.strip() if price_elem else 'N/A'
                                
                                # Get original price if available
                                original_price_elem = hotel.find('span', {'data-testid': 'price-for-x-nights'})
                                original_price = original_price_elem.text.strip() if original_price_elem else 'N/A'

                                # Get discounted price if available
                                discounted_price_elem = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
                                discounted_price = discounted_price_elem.text.strip() if discounted_price_elem else 'N/A'

                                # Get tax information
                                tax_info_elem = hotel.find('div', {'data-testid': 'taxes-and-charges'})
                                tax_info = tax_info_elem.text.strip() if tax_info_elem else 'N/A'
                                
                                rating_elem = hotel.find('div', {'data-testid': 'review-score'})
                                rating = rating_elem.text.strip() if rating_elem else 'N/A'
                                
                                location_elem = hotel.find('span', {'data-testid': 'address'})
                                location = location_elem.text.strip() if location_elem else 'N/A'
                                
                                hotel_data = {
                                    'name': name,
                                    'link': detail_link,
                                    'price': price,
                                    'original_price': original_price,
                                    'discounted_price': discounted_price,
                                    'tax_info': tax_info,
                                    'rating': rating,
                                    'location': location,
                                    'facilities': hotel_details['facilities'],
                                    'description': hotel_details['description'],
                                    'images': hotel_details['images'],
                                    'room_types': hotel_details['rooms']
                                }
                                
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