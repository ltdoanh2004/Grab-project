import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
from urllib.parse import urljoin
import argparse
import os

class AttractionCrawler:
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
        self.attractions_since_last_save = 0
        self.debug = debug
        
    def log(self, message, always=False):
        """Log message if in debug mode or if always=True"""
        if self.debug or always:
            print(message)

    def get_attraction_detail(self, url):
        """Get detailed information from attraction page"""
        try:
            self.log(f"\nFetching details from: {url}")
            time.sleep(random.uniform(2, 4))
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Get main title
            title = 'N/A'
            title_elem = soup.find('h1', {'class': 'e1jpltd20'})
            if title_elem:
                title = title_elem.text.strip()
            
            # Get description
            description = 'N/A'
            description_elem = soup.find('div', {'data-testid': 'attraction-content-description'})
            if description_elem:
                description = description_elem.text.strip()
                self.log(f"\nFound description: {description[:100]}...")
            
            # Get details sections
            details = {}
            details_sections = soup.find_all('div', {'class': ['a830e55bb0', 'bcb64e9a27']})
            for section in details_sections:
                section_title_elem = section.find('h3')
                if section_title_elem:
                    section_title = section_title_elem.text.strip()
                    section_content = []
                    content_elements = section.find_all('div', {'class': 'c5b9b723db'})
                    for element in content_elements:
                        section_content.append(element.text.strip())
                    details[section_title] = section_content
            
            # Get ticket options
            ticket_options = []
            ticket_elements = soup.find_all('div', {'data-testid': 'product-card'})
            for ticket in ticket_elements:
                ticket_data = {}
                
                # Get ticket name
                name_elem = ticket.find('div', {'data-testid': 'product-card-name'})
                if name_elem:
                    ticket_data['name'] = name_elem.text.strip()
                
                # Get ticket price
                price_elem = ticket.find('span', {'data-testid': 'product-card-price'})
                if price_elem:
                    ticket_data['price'] = price_elem.text.strip()
                
                # Get benefits
                benefits = []
                benefits_elems = ticket.find_all('li', {'data-testid': 'usp-box'})
                for benefit in benefits_elems:
                    benefits.append(benefit.text.strip())
                ticket_data['benefits'] = benefits
                
                ticket_options.append(ticket_data)
            
            # Get all images
            images = []
            image_elements = soup.find_all('img', {'class': 'e562ed37d1'})
            for img in image_elements:
                if img.get('src'):
                    image_url = img['src']
                    # Clean URL by removing query params
                    if '?' in image_url:
                        image_url = image_url.split('?')[0]
                    images.append({
                        'url': image_url,
                        'alt': img.get('alt', '')
                    })
            self.log(f"\nFound {len(images)} images")
            
            # Get reviews if available
            reviews = []
            review_elements = soup.find_all('div', {'class': 'review_item'})
            for review in review_elements:
                review_data = {}
                
                # Get review title
                title_elem = review.find('div', {'class': 'review_item_header'})
                if title_elem:
                    review_data['title'] = title_elem.text.strip()
                
                # Get review score
                score_elem = review.find('span', {'class': 'review-score-badge'})
                if score_elem:
                    review_data['score'] = score_elem.text.strip()
                
                # Get review text
                text_elem = review.find('div', {'class': 'review_item_review_content'})
                if text_elem:
                    review_data['text'] = text_elem.text.strip()
                
                reviews.append(review_data)
            
            # Get location information
            location = {}
            location_elem = soup.find('div', {'data-testid': 'attraction-content-location'})
            if location_elem:
                location_title = location_elem.find('h3')
                location['title'] = location_title.text.strip() if location_title else 'N/A'
                
                address_elem = location_elem.find('span', {'data-testid': 'address'})
                location['address'] = address_elem.text.strip() if address_elem else 'N/A'
                
                # Try to get coordinates from map if available
                map_elem = soup.find('div', {'class': 'map_static_container'})
                if map_elem and 'data-atlas-latlng' in map_elem.attrs:
                    location['coordinates'] = map_elem['data-atlas-latlng']

            return {
                'title': title,
                'description': description,
                'details': details,
                'ticket_options': ticket_options,
                'images': images,
                'reviews': reviews,
                'location': location
            }
        except Exception as e:
            self.log(f"Error getting attraction detail: {e}", always=True)
            return None

    def save_checkpoint(self, attractions, output_base, current_page):
        """Save data checkpoint with timestamp"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        checkpoint_base = f"{output_base}_page{current_page}_{timestamp}"
        self.save_to_csv(attractions, filename=f'{checkpoint_base}.csv')
        self.last_save_time = time.time()
        self.attractions_since_last_save = 0
        self.log(f"Saved checkpoint: {checkpoint_base}", always=True)
        return checkpoint_base

    def get_attraction_data(self, url, start_page=1, end_page=5, output_base='attractions', save_interval_mins=30, save_interval_attractions=50):
        all_attractions = []
        current_page = start_page
        
        self.log(f"\nStarting crawl from page {start_page} to page {end_page}", always=True)
        self.log(f"Auto-save settings: Every {save_interval_mins} mins or {save_interval_attractions} attractions")
        
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
                
                self.log(f"Page URL: {page_url}")
                time.sleep(random.uniform(1, 3))
                response = requests.get(page_url, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Print HTML structure for debugging
                with open(f"page_{current_page}_debug.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())
                self.log(f"HTML structure saved to page_{current_page}_debug.html")
                
                # Try different selectors for attraction elements
                attraction_elements = soup.find_all('li', {'class': ['css-1wts3mx', 'b817090550', 'b736e9e3f4']})
                
                self.log(f"Found {len(attraction_elements)} attractions on page {current_page}")
                
                if not attraction_elements:
                    # Try to find any links that might contain attractions
                    all_links = soup.find_all('a')
                    potential_attractions = [link for link in all_links if 'attraction' in link.get('href', '')]
                    self.log(f"Found {len(potential_attractions)} potential attraction links")
                    
                    if not potential_attractions:
                        self.log("No attractions found on this page.", always=True)
                        break
                    
                    # Use these links instead
                    for idx, link in enumerate(potential_attractions[:10], 1):  # Limit to 10 for testing
                        try:
                            detail_link = urljoin(self.base_url, link['href'])
                            name = link.text.strip() if link.text else f"Attraction {idx}"
                            
                            self.log(f"\nProcessing attraction {idx}/{len(potential_attractions[:10])} on page {current_page}")
                            self.log(f"Name: {name}")
                            self.log(f"Detail link: {detail_link}")
                            
                            # Get detailed information if we have a link
                            attraction_details = self.get_attraction_detail(detail_link)
                            
                            # Build attraction data structure
                            attraction_data = {
                                'name': name,
                                'link': detail_link,
                            }
                            
                            # Add detailed information if available
                            if attraction_details:
                                attraction_data.update({
                                    'description': attraction_details.get('description', 'N/A'),
                                    'details': attraction_details.get('details', {}),
                                    'ticket_options': attraction_details.get('ticket_options', []),
                                    'images': attraction_details.get('images', []),
                                    'reviews': attraction_details.get('reviews', []),
                                    'location': attraction_details.get('location', {})
                                })
                            
                            all_attractions.append(attraction_data)
                            self.attractions_since_last_save += 1
                            self.log(f"Successfully crawled: {name}")
                            
                            time_since_last_save = time.time() - self.last_save_time
                            if time_since_last_save >= save_interval_mins * 60 or self.attractions_since_last_save >= save_interval_attractions:
                                self.log(f"\nAuto-saving checkpoint...", always=True)
                                self.save_checkpoint(all_attractions, output_base, current_page)
                            
                            time.sleep(random.uniform(2, 4))
                        except Exception as e:
                            self.log(f"Error parsing attraction data: {e}", always=True)
                            continue
                else:
                    # Process normally found attraction elements
                    for idx, attraction in enumerate(attraction_elements, 1):
                        try:
                            # Get attraction name and link from the card-title element
                            card_title = attraction.find('h3', {'data-testid': 'card-title'})
                            if card_title:
                                link_elem = card_title.find('a', {'data-link-type': 'title'})
                                print(f"Found link element: {link_elem}")
                                print('doanh')
                                
                                if link_elem:
                                    name = link_elem.text.strip()
                                    detail_link = urljoin(self.base_url, link_elem['href'])
                                    self.log(f"\nProcessing attraction {idx}/{len(attraction_elements)} on page {current_page}")
                                    self.log(f"Name: {name}")
                                    self.log(f"Detail link: {detail_link}")
                                    
                                    # Get attraction price
                                    price = 'N/A'
                                    price_elem = attraction.find(['span', 'div'], {'data-testid': 'card-price'})
                                    if not price_elem:
                                        price_elem = attraction.find(['span', 'div'], {'class': 'bui-card__price'})
                                    if price_elem:
                                        price = price_elem.text.strip()
                                    
                                    # Get attraction rating
                                    rating = 'N/A'
                                    rating_elem = attraction.find(['div', 'span'], {'data-testid': 'card-rating'})
                                    if not rating_elem:
                                        rating_elem = attraction.find(['div', 'span'], {'class': 'bui-review-score__badge'})
                                    if rating_elem:
                                        rating = rating_elem.text.strip()
                                    
                                    # Get attraction image
                                    image_url = 'N/A'
                                    image_elem = attraction.find('img')
                                    if image_elem and 'src' in image_elem.attrs:
                                        image_url = image_elem['src']
                                        if '?' in image_url:
                                            image_url = image_url.split('?')[0]
                                    
                                    # Get detailed information if we have a link
                                    attraction_details = None
                                    if detail_link:
                                        attraction_details = self.get_attraction_detail(detail_link)
                                    
                                    # Build attraction data structure
                                    attraction_data = {
                                        'name': name,
                                        'link': detail_link,
                                        'price': price,
                                        'rating': rating,
                                        'thumbnail': image_url
                                    }
                                    
                                    # Add detailed information if available
                                    if attraction_details:
                                        attraction_data.update({
                                            'description': attraction_details.get('description', 'N/A'),
                                            'details': attraction_details.get('details', {}),
                                            'ticket_options': attraction_details.get('ticket_options', []),
                                            'images': attraction_details.get('images', []),
                                            'reviews': attraction_details.get('reviews', []),
                                            'location': attraction_details.get('location', {})
                                        })
                                    
                                    all_attractions.append(attraction_data)
                                    self.attractions_since_last_save += 1
                                    self.log(f"Successfully crawled: {name}")
                                    
                                    time_since_last_save = time.time() - self.last_save_time
                                    if time_since_last_save >= save_interval_mins * 60 or self.attractions_since_last_save >= save_interval_attractions:
                                        self.log(f"\nAuto-saving checkpoint...", always=True)
                                        self.save_checkpoint(all_attractions, output_base, current_page)
                                    
                                    time.sleep(random.uniform(2, 4))
                                    
                        except Exception as e:
                            self.log(f"Error parsing attraction data: {e}", always=True)
                            continue
                
                current_page += 1
                
            except Exception as e:
                self.log(f"Error fetching page {current_page}: {e}", always=True)
                if all_attractions:
                    self.log("\nSaving checkpoint due to error...", always=True)
                    self.save_checkpoint(all_attractions, output_base, current_page-1)
                break
        
        self.log(f"\nCrawl completed. Total attractions collected: {len(all_attractions)}", always=True)
        if all_attractions:
            final_base = f"{output_base}_final"
            self.save_to_csv(all_attractions, filename=f'{final_base}.csv')
        return all_attractions

    def save_to_csv(self, attractions, filename='attractions.csv'):
        if attractions:
            # Flatten the complex data structure for CSV
            flattened_attractions = []
            for attraction in attractions:
                attraction_copy = attraction.copy()
                
                # Handle nested structures
                # Flatten details dictionary
                if 'details' in attraction_copy:
                    details_dict = attraction_copy.pop('details')
                    for key, value in details_dict.items():
                        safe_key = key.replace(' ', '_').lower()
                        attraction_copy[f'details_{safe_key}'] = ' | '.join(value) if isinstance(value, list) else value
                
                # Handle ticket options
                if 'ticket_options' in attraction_copy:
                    ticket_options = attraction_copy.pop('ticket_options')
                    for i, ticket in enumerate(ticket_options[:5]):  # Limit to 5 tickets to avoid too many columns
                        attraction_copy[f'ticket_{i+1}_name'] = ticket.get('name', 'N/A')
                        attraction_copy[f'ticket_{i+1}_price'] = ticket.get('price', 'N/A')
                        attraction_copy[f'ticket_{i+1}_benefits'] = ' | '.join(ticket.get('benefits', []))
                
                # Handle images - just keep count and first 5 URLs
                if 'images' in attraction_copy:
                    images = attraction_copy.pop('images')
                    attraction_copy['image_count'] = len(images)
                    for i, img in enumerate(images[:5]):  # Limit to 5 images
                        attraction_copy[f'image_{i+1}_url'] = img.get('url', 'N/A')
                
                # Handle reviews - just keep count and a sample
                if 'reviews' in attraction_copy:
                    reviews = attraction_copy.pop('reviews')
                    attraction_copy['review_count'] = len(reviews)
                    for i, review in enumerate(reviews[:3]):  # Limit to 3 reviews
                        attraction_copy[f'review_{i+1}_text'] = review.get('text', 'N/A')
                        attraction_copy[f'review_{i+1}_score'] = review.get('score', 'N/A')
                
                # Handle location
                if 'location' in attraction_copy:
                    location = attraction_copy.pop('location')
                    attraction_copy['location_address'] = location.get('address', 'N/A')
                    attraction_copy['location_coordinates'] = location.get('coordinates', 'N/A')
                
                flattened_attractions.append(attraction_copy)
            
            # Create dataframe and save to CSV
            df = pd.DataFrame(flattened_attractions)
            df.to_csv(filename, index=False, encoding='utf-8')
            self.log(f"\nData saved to {filename}")
            
            # Save raw JSON data
            json_filename = filename.replace('.csv', '.json')
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(attractions, f, ensure_ascii=False, indent=2)
            self.log(f"Raw data saved to {json_filename}")
        else:
            self.log("No data to save")

def main():
    parser = argparse.ArgumentParser(description='Crawl attraction data from Booking.com')
    parser.add_argument('--url', type=str, default="https://www.booking.com/attractions/searchresults/vn/hanoi.vi.html?adplat=www-searcx%C6%B0hresults_irene-web_shell_header-attraction-missing_creative-5TtbVuFeaoBZHhexOcvJ8A&aid=304142&label=gen173nr-1FCAQoggJCEHNlYXJjaF9ow6AgbuG7mWlIKlgEaPQBiAEBmAEquAEHyAEM2AEB6AEB-AEDiAIBqAIDuAKV75HABsACAdICJDJjNTc3NTFlLTBkZjctNGFiOC05MjlhLTk3ZTJlYzBhMmE2ZtgCBeACAQ&client_name=b-web-shell-bff&distribution_id=5TtbVuFeaoBZHhexOcvJ8A&source=attractions_index_open_shop",
                        help='URL to crawl')
    parser.add_argument('--start-page', type=int, default=1,
                        help='Starting page number (default: 1)')
    parser.add_argument('--end-page', type=int, default=5,
                        help='Ending page number (default: 5)')
    parser.add_argument('--output', type=str, default='data_attractions/attractions',
                        help='Output filename without extension (default: data_attractions/attractions)')
    parser.add_argument('--save-interval-mins', type=int, default=15,
                        help='Save checkpoint every N minutes (default: 15)')
    parser.add_argument('--save-interval-attractions', type=int, default=10,
                        help='Save checkpoint every N attractions (default: 10)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    crawler = AttractionCrawler(debug=args.debug)
    attractions = crawler.get_attraction_data(
        args.url, 
        start_page=args.start_page, 
        end_page=args.end_page,
        output_base=args.output,
        save_interval_mins=args.save_interval_mins,
        save_interval_attractions=args.save_interval_attractions
    )

if __name__ == "__main__":
    main() 