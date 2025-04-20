import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
from urllib.parse import urljoin

class HotelCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.base_url = "https://www.booking.com"
        
    def get_hotel_detail(self, url):
        """Get detailed information from hotel page"""
        try:
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
            description = soup.find('div', {'data-testid': 'property-description'})
            description_text = description.text.strip() if description else 'N/A'
            
            # Get room types
            rooms = []
            room_elements = soup.find_all('div', {'data-testid': 'room-item'})
            for room in room_elements:
                room_name = room.find('span', {'data-testid': 'room-name'})
                room_price = room.find('span', {'data-testid': 'price-and-discounted-price'})
                if room_name and room_price:
                    rooms.append({
                        'name': room_name.text.strip(),
                        'price': room_price.text.strip()
                    })
            
            return {
                'facilities': facilities,
                'description': description_text,
                'rooms': rooms
            }
        except Exception as e:
            print(f"Error getting hotel detail: {e}")
            return None

    def get_hotel_data(self, url, max_pages=5):
        all_hotels = []
        current_page = 1
        
        while current_page <= max_pages:
            try:
                print(f"\nCrawling page {current_page}...")
                # Add offset parameter for pagination
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
                    print("No more hotels found.")
                    break
                
                for hotel in hotel_elements:
                    try:
                        # Get basic hotel information
                        name_div = hotel.find('div', {'data-testid': 'title'})
                        name = name_div.text.strip() if name_div else 'N/A'
                        
                        link_elem = hotel.find('a', {'data-testid': 'title-link'})
                        link = urljoin(self.base_url, link_elem['href']) if link_elem else 'N/A'
                        
                        img_elem = hotel.find('img', {'data-testid': 'image'})
                        image_url = img_elem.get('src') if img_elem else 'N/A'
                        
                        price_elem = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
                        price = price_elem.text.strip() if price_elem else 'N/A'
                        
                        rating_elem = hotel.find('div', {'data-testid': 'review-score'})
                        rating = rating_elem.text.strip() if rating_elem else 'N/A'
                        
                        location_elem = hotel.find('span', {'data-testid': 'address'})
                        location = location_elem.text.strip() if location_elem else 'N/A'
                        
                        # Get detailed information if link is available
                        details = self.get_hotel_detail(link) if link != 'N/A' else None
                        
                        hotel_data = {
                            'name': name,
                            'link': link,
                            'image_url': image_url,
                            'price': price,
                            'rating': rating,
                            'location': location,
                            'facilities': details['facilities'] if details else [],
                            'description': details['description'] if details else 'N/A',
                            'room_types': details['rooms'] if details else []
                        }
                        
                        all_hotels.append(hotel_data)
                        print(f"Crawled hotel: {name}")
                        
                    except Exception as e:
                        print(f"Error parsing hotel data: {e}")
                        continue
                
                current_page += 1
                
            except Exception as e:
                print(f"Error fetching page {current_page}: {e}")
                break
        
        return all_hotels

    def save_to_csv(self, hotels, filename='hotels.csv'):
        if hotels:
            # Flatten the room types and facilities into separate columns
            flattened_hotels = []
            for hotel in hotels:
                hotel_copy = hotel.copy()
                
                # Convert facilities list to string
                hotel_copy['facilities'] = ' | '.join(hotel_copy['facilities'])
                
                # Convert room types to separate columns
                for i, room in enumerate(hotel_copy['room_types']):
                    hotel_copy[f'room_{i+1}_name'] = room['name']
                    hotel_copy[f'room_{i+1}_price'] = room['price']
                
                del hotel_copy['room_types']
                flattened_hotels.append(hotel_copy)
            
            df = pd.DataFrame(flattened_hotels)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"\nData saved to {filename}")
            
            # Save raw JSON data
            json_filename = filename.replace('.csv', '.json')
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(hotels, f, ensure_ascii=False, indent=2)
            print(f"Raw data saved to {json_filename}")
        else:
            print("No data to save")

def main():
    url = "https://www.booking.com/searchresults.vi.html?ss=H%C3%A0+N%E1%BB%99i"
    
    crawler = HotelCrawler()
    hotels = crawler.get_hotel_data(url, max_pages=3)  # Crawl 3 pages by default
    crawler.save_to_csv(hotels)

if __name__ == "__main__":
    main() 