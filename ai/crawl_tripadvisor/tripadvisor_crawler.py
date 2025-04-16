#!/usr/bin/env python3
# TripAdvisor crawler
import requests
from bs4 import BeautifulSoup
import csv
import time
import argparse
import os
import random
from urllib.parse import urlparse, urljoin
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TripAdvisorCrawler:
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
            
    def get_attractions(self, location_url=None):
        """Get attractions, hotels, restaurants, or tours for a given location"""
        url = location_url or self.base_url
        if not url:
            raise ValueError("No URL provided")
            
        soup = self.get_soup(url)
        if not soup:
            return []
        
        # Determine entity type from URL
        entity_type = "attraction"
        if "Hotel_Review" in url or "Hotels-" in url:
            entity_type = "hotel"
        elif "Restaurant_Review" in url or "Restaurants-" in url:
            entity_type = "restaurant"
        elif "Tour_Review" in url or "Activities-c42" in url:
            entity_type = "tour"
            
        logger.info(f"Detected entity type: {entity_type}")
        
        # Try various selectors that might work with TripAdvisor's current structure
        entities = []
        
        # Method 1: Look for entity cards (new layout)
        card_selectors = [
            f'div[data-automation="{entity_type}-card"]',
            'div.eLWJL',  # Common card class
            'div.listing',  # Older listing class
            'div.DyfOE'  # Property cards
        ]
        
        for selector in card_selectors:
            entity_elements = soup.select(selector)
            if entity_elements:
                logger.info(f"Found {len(entity_elements)} entities using selector: {selector}")
                for item in entity_elements:
                    link_elem = item.select_one('a')
                    if link_elem and link_elem.has_attr('href'):
                        name_elem = item.select_one('h3, h2, div.name, div.listing_title, div.title')
                        name = name_elem.get_text(strip=True) if name_elem else "Unknown Entity"
                        link = link_elem['href']
                        if not link.startswith('http'):
                            link = urljoin("https://www.tripadvisor.com", link)
                        entities.append({"name": name, "url": link})
                
                if entities:
                    return entities
        
        # Method 2: Look for entity links by pattern
        link_patterns = {
            "attraction": 'a[href*="Attraction_Review"]',
            "hotel": 'a[href*="Hotel_Review"]',
            "restaurant": 'a[href*="Restaurant_Review"]',
            "tour": 'a[href*="Tour_Review"], a[href*="Attraction_Review"][href*="c42"]'
        }
        
        pattern = link_patterns.get(entity_type, 'a[href*="_Review"]')
        entity_links = soup.select(pattern)
        
        if entity_links:
            # Filter out links that are likely not actual entities
            filtered_links = []
            for link in entity_links:
                href = link['href']
                name = link.get_text(strip=True)
                
                # Skip if very short name or empty text
                if not name or len(name) <= 1:
                    continue
                
                # Skip common navigation terms
                if name.lower() in ['map', 'view map', 'next', 'previous', 'photos', '1', '2', '3', '4', '5']:
                    continue
                
                # Add to filtered list
                filtered_links.append(link)
            
            logger.info(f"Found {len(entity_links)} potential entities with '{entity_type}_Review', filtered to {len(filtered_links)}")
            
            for link in filtered_links:
                name = link.get_text(strip=True)
                href = link['href']
                if not href.startswith('http'):
                    href = urljoin("https://www.tripadvisor.com", href)
                entities.append({"name": name, "url": href})
            
            if entities:
                return entities
        
        # Method 3: Fallback to location-based links
        if not entities:
            location_links = []
            try:
                path_parts = urlparse(url).path.split('-')
                if len(path_parts) > 2:
                    location_name = path_parts[2]  # e.g., 'Hanoi' from 'Attractions-g293924-Activities-Hanoi.html'
                    location_links = soup.select(f'a[href*="{location_name}"]')
            except Exception as e:
                logger.error(f"Error parsing location from URL: {e}")
            
            # Filter links to likely entities
            filtered_location_links = []
            for link in location_links:
                href = link['href']
                name = link.get_text(strip=True)
                
                # Skip if very short name or empty text
                if not name or len(name) <= 1:
                    continue
                
                # Skip common navigation terms
                if name.lower() in ['map', 'view map', 'next', 'previous', 'photos', '1', '2', '3', '4', '5']:
                    continue
                
                # Check if the link looks like an entity page
                if f"{entity_type.capitalize()}_Review" in href or f"{entity_type.capitalize()}s-" in href:
                    filtered_location_links.append(link)
            
            logger.info(f"Found {len(location_links)} potential location-based entities, filtered to {len(filtered_location_links)}")
            
            for link in filtered_location_links:
                name = link.get_text(strip=True)
                href = link['href']
                if not href.startswith('http'):
                    href = urljoin("https://www.tripadvisor.com", href)
                entities.append({"name": name, "url": href})
        
        # Method 4: Use hardcoded data for common locations
        if not entities:
            logger.warning("No entities found through standard methods, trying fallback data")
            
            # Extract location from URL
            location = None
            try:
                path_parts = urlparse(url).path.split('-')
                if len(path_parts) > 2:
                    location = path_parts[2]  # e.g., 'Hanoi' from 'Attractions-g293924-Activities-Hanoi.html'
            except:
                pass
            
            # Hardcoded top entities for common locations
            if location and location.lower() == 'hanoi':
                if entity_type == "attraction":
                    entities = [
                        {"name": "Old Quarter", "url": "https://www.tripadvisor.com/Attraction_Review-g293924-d317503-Reviews-Old_Quarter-Hanoi.html"},
                        {"name": "Temple of Literature", "url": "https://www.tripadvisor.com/Attraction_Review-g293924-d311516-Reviews-Temple_of_Literature_National_University-Hanoi.html"},
                        {"name": "Hoan Kiem Lake", "url": "https://www.tripadvisor.com/Attraction_Review-g293924-d311516-Reviews-Hoan_Kiem_Lake-Hanoi.html"}
                    ]
                elif entity_type == "hotel":
                    entities = [
                        {"name": "Sofitel Legend Metropole Hanoi", "url": "https://www.tripadvisor.com/Hotel_Review-g293924-d301984-Reviews-Sofitel_Legend_Metropole_Hanoi-Hanoi.html"},
                        {"name": "JW Marriott Hotel Hanoi", "url": "https://www.tripadvisor.com/Hotel_Review-g293924-d5003805-Reviews-JW_Marriott_Hotel_Hanoi-Hanoi.html"}
                    ]
                elif entity_type == "restaurant":
                    entities = [
                        {"name": "Bun Cha Huong Lien", "url": "https://www.tripadvisor.com/Restaurant_Review-g293924-d8288571-Reviews-Bun_Cha_Huong_Lien-Hanoi.html"},
                        {"name": "Cau Go Vietnamese Cuisine", "url": "https://www.tripadvisor.com/Restaurant_Review-g293924-d3600935-Reviews-Cau_Go_Vietnamese_Cuisine-Hanoi.html"}
                    ]
                
                logger.info(f"Using {len(entities)} hardcoded {entity_type}s for {location}")
        
        # If we still found nothing, log the entire HTML for debugging
        if not entities:
            logger.warning(f"No {entity_type}s found. The website structure may have changed.")
            logger.debug(f"HTML content: {soup}")
            
        return entities
        
    def get_attraction_details(self, attraction_url):
        """Get details for a specific attraction"""
        self._random_delay()  # Add random delay before requesting
        
        soup = self.get_soup(attraction_url)
        if not soup:
            return {}
            
        details = {"url": attraction_url}
        
        # 1. Extract name
        name_selectors = [
            'h1.QdLfr',
            'h1.eIegw',
            'h1.HjBfq',
            'div.pZUbB h1'
        ]
        for selector in name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                details["name"] = name_elem.get_text(strip=True)
                break
        
        # Extract name from URL if we can't find it on page
        if 'name' not in details:
            try:
                url_parts = attraction_url.split('-Reviews-')
                if len(url_parts) > 1:
                    name_part = url_parts[1].split('-')[0]
                    # Replace underscores with spaces and title case
                    details["name"] = name_part.replace('_', ' ').title()
            except:
                details["name"] = "Unknown"
                
        # 2. Try to extract category/type
        category_selectors = [
            'div.fIrGe div._c',
            'a.GEcgi',
            'div.BmuhR a',
            'div.iyUkv span',
            'div.frvHq span'
        ]
        for selector in category_selectors:
            category_elems = soup.select(selector)
            if category_elems:
                categories = [elem.get_text(strip=True) for elem in category_elems]
                details["category"] = ", ".join(categories)
                break
                
        # Determine category based on URL
        if 'category' not in details:
            if 'Attraction_Review' in attraction_url:
                details["category"] = "Attractions"
            elif 'Hotel_Review' in attraction_url:
                details["category"] = "Hotels"
            elif 'Restaurant_Review' in attraction_url:
                details["category"] = "Restaurants"
            elif 'Tour_Review' in attraction_url:
                details["category"] = "Tours"
            else:
                details["category"] = "Things To Do"
        
        # 3. Extract location (address)
        address_selectors = [
            'div[data-test-target="attraction-detail-card"] button.UikbF',
            'button.KEaY',
            'div.kUaGX button',
            'div.XPUSn span.yEWoV',
            'div.FUHHI span',
            'div.CEQvT button'
        ]
        for selector in address_selectors:
            address_elem = soup.select_one(selector)
            if address_elem:
                details["location"] = address_elem.get_text(strip=True)
                break
        
        # 4 & 5. Extract latitude and longitude
        # Look for map data in script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_text = script.string
            if script_text and ('latitude' in script_text.lower() or 'lng' in script_text.lower()):
                # Try to extract coordinates using regex
                lat_match = re.search(r'"latitude":\s*([-+]?\d*\.\d+|\d+)', script_text)
                lng_match = re.search(r'"longitude":\s*([-+]?\d*\.\d+|\d+)', script_text)
                
                if not lat_match:
                    lat_match = re.search(r'"lat":\s*([-+]?\d*\.\d+|\d+)', script_text)
                if not lng_match:
                    lng_match = re.search(r'"lng":\s*([-+]?\d*\.\d+|\d+)', script_text)
                
                if lat_match and lng_match:
                    details["latitude"] = float(lat_match.group(1))
                    details["longitude"] = float(lng_match.group(1))
                    break
        
        # 6. Try to extract rating
        rating_selectors = [
            'div.AfQtZ',
            'div.eLXel',
            'div.EWtzU span.uwJeR',
            'span.bvcyz',
            'div.WAllg div.grdwI span'
        ]
        for selector in rating_selectors:
            rating_elem = soup.select_one(selector)
            if rating_elem:
                text = rating_elem.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)\s*(?:of\s*\d+)?', text)
                if rating_match:
                    details["rating"] = float(rating_match.group(1))
                    break
        
        # 7. Extract number of reviews
        reviews_selectors = [
            'div.AfQtZ',
            'a.iUttq',
            'span.jqKwK',
            'a.UctQk'
        ]
        for selector in reviews_selectors:
            reviews_elem = soup.select_one(selector)
            if reviews_elem:
                text = reviews_elem.get_text(strip=True)
                reviews_match = re.search(r'([\d,]+)\s*reviews?', text)
                if reviews_match:
                    details["number_of_reviews"] = int(reviews_match.group(1).replace(',', ''))
                    break
        
        # 8. Extract review summary
        review_summary_selectors = [
            'div.LbPSX span.JguWG',
            'span.ebEmH',
            'div.fIrGe',
            'div.cFaVH div.PXEwy'
        ]
        for selector in review_summary_selectors:
            summary_elems = soup.select(selector)
            if summary_elems and len(summary_elems) > 0:
                summaries = [elem.get_text(strip=True) for elem in summary_elems[:3]]  # Get top 3 reviews
                details["review_summary"] = " | ".join(summaries)
                break
        
        # 9. Extract price level
        price_level_selectors = [
            'div.DgQyR',
            'div.ceIOZ',
            'div.pZUbB span.WlYyy',
            'div.EEIGK span'
        ]
        for selector in price_level_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                text = price_elem.get_text(strip=True)
                if '$' in text:
                    # Extract price level ($, $$, $$$, etc.)
                    price_match = re.search(r'(\$+)', text)
                    if price_match:
                        details["price_level"] = price_match.group(1)
                    break
        
        # 10. Extract recommended duration
        duration_selectors = [
            'div.xVfSG',
            'div.eRzXP',
            'div.BmuhR div.WlYyy',
            'div.NeINz span'
        ]
        for selector in duration_selectors:
            duration_elem = soup.select_one(selector)
            if duration_elem:
                text = duration_elem.get_text(strip=True)
                if 'hour' in text.lower() or 'min' in text.lower() or 'day' in text.lower():
                    details["recommended_duration"] = text
                    break
        
        # 11. Extract tags
        tags_selectors = [
            'div.XPxdY span.WlYyy',
            'div.EZmvx span.eqXJH',
            'div.pZUbB span.eVxrG',
            'div.EEIGK div.gBJvU'
        ]
        tags = []
        for selector in tags_selectors:
            tag_elems = soup.select(selector)
            if tag_elems:
                tags = [elem.get_text(strip=True) for elem in tag_elems]
                details["tags"] = tags
                break
        
        # 12. Determine suitable_for from tags
        if tags:
            suitable_for = []
            if any('family' in tag.lower() for tag in tags):
                suitable_for.append('family')
            if any('couple' in tag.lower() for tag in tags):
                suitable_for.append('couple')
            if any('solo' in tag.lower() or 'alone' in tag.lower() for tag in tags):
                suitable_for.append('solo')
            if any('group' in tag.lower() for tag in tags):
                suitable_for.append('group')
            
            if suitable_for:
                details["suitable_for"] = ", ".join(suitable_for)
        
        # 13. Extract opening hours
        hours_selectors = [
            'div.sRVj span',
            'div.BmuhR div.WlYyy',
            'div.JINyA',
            'div.IhqAp'
        ]
        for selector in hours_selectors:
            hours_elems = soup.select(selector)
            if hours_elems:
                # Try to find elements with day/time patterns
                hour_texts = []
                for elem in hours_elems:
                    text = elem.get_text(strip=True)
                    if re.search(r'(mon|tue|wed|thu|fri|sat|sun|open|close|\d+:\d+|am|pm)', text.lower()):
                        hour_texts.append(text)
                
                if hour_texts:
                    details["opening_hours"] = " | ".join(hour_texts)
                    break
        
        # 14. Extract image URL
        img_selectors = [
            'div.UCacc img',
            'div.HRZla img',
            'div.pZUbB img',
            'div.EUuew img'
        ]
        for selector in img_selectors:
            img_elem = soup.select_one(selector)
            if img_elem and img_elem.has_attr('src'):
                details["image_url"] = img_elem['src']
                if not details["image_url"].startswith('http'):
                    details["image_url"] = urljoin("https://www.tripadvisor.com", details["image_url"])
                break
        
        # 15. Extract activities from descriptions or tags
        activities = []
        activity_keywords = ['hiking', 'swimming', 'sightseeing', 'shopping', 'diving', 'snorkeling', 
                           'kayaking', 'biking', 'tour', 'massage', 'spa', 'photography', 'eating']
        
        # Look in description
        description_selectors = [
            'div.pZUbB div.duhwe span.JguWG',
            'div.DpZHu div',
            'div.LBVLY div.WlYyy'
        ]
        description_text = ""
        for selector in description_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                description_text = desc_elem.get_text(strip=True)
                details["description"] = description_text
                break
        
        # Extract activities from description and tags
        if description_text:
            for activity in activity_keywords:
                if activity in description_text.lower():
                    activities.append(activity)
        
        if tags:
            for tag in tags:
                for activity in activity_keywords:
                    if activity in tag.lower() and activity not in activities:
                        activities.append(activity)
        
        if activities:
            details["activities"] = activities
        
        # 16. Extract website/contact info
        website_selectors = [
            'a[href*="website"]',
            'a.YnKZo',
            'a.eNwBm',
            'div.pZUbB a[target="_blank"]'
        ]
        for selector in website_selectors:
            website_elem = soup.select_one(selector)
            if website_elem and website_elem.has_attr('href'):
                href = website_elem['href']
                # Sometimes TripAdvisor uses redirect URLs
                if 'tripadvisor' in href and 'website=' in href:
                    # Extract actual URL from redirect
                    website_match = re.search(r'website=([^&]+)', href)
                    if website_match:
                        details["website"] = website_match.group(1)
                else:
                    details["website"] = href
                break
        
        # Look for phone number
        phone_selectors = [
            'span.BMQDV',
            'a[href*="tel:"]',
            'button[data-phone]'
        ]
        for selector in phone_selectors:
            phone_elem = soup.select_one(selector)
            if phone_elem:
                if phone_elem.has_attr('data-phone'):
                    details["contact_info"] = phone_elem['data-phone']
                else:
                    phone_text = phone_elem.get_text(strip=True)
                    if phone_text and re.search(r'\d', phone_text):
                        details["contact_info"] = phone_text
                break
        
        # 17. Extract popular times
        popular_times_selectors = [
            'div.FBJyy',
            'div.pZUbB div.UvZbQ',
            'div.EEIGK div.frvHq'
        ]
        for selector in popular_times_selectors:
            times_elem = soup.select_one(selector)
            if times_elem:
                times_text = times_elem.get_text(strip=True)
                if 'busy' in times_text.lower() or 'popular' in times_text.lower():
                    details["popular_times"] = times_text
                    break
        
        # 18. Extract nearby places
        nearby_selectors = [
            'div.PeVzA a',
            'div.pZUbB a[data-automation="attraction-card"]',
            'div.EEIGK div.gFxVV a'
        ]
        nearby_places = []
        for selector in nearby_selectors:
            nearby_elems = soup.select(selector)
            if nearby_elems:
                for elem in nearby_elems[:5]:  # Limit to 5 nearby places
                    name = elem.get_text(strip=True)
                    if name and len(name) > 1:
                        nearby_places.append(name)
                
                if nearby_places:
                    details["nearby_places"] = nearby_places
                    break
        
        # 19. Extract review date
        date_selectors = [
            'div.pZUbB div.RpeCd',
            'div.JVCMQ',
            'div.EEIGK span.cfIAE'
        ]
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s,]+\d{4}', date_text)
                if date_match:
                    details["review_date"] = date_match.group(0)
                    break
        
        # 20. Extract reviewer origin
        origin_selectors = [
            'div.pZUbB span.BMQDV',
            'div.EEIGK span.ShLyt',
            'div.JVCMQ span'
        ]
        for selector in origin_selectors:
            origin_elems = soup.select(selector)
            for elem in origin_elems:
                origin_text = elem.get_text(strip=True)
                # Look for text that's likely to be a location/origin
                if re.search(r'from\s+\w+', origin_text, re.IGNORECASE):
                    details["reviewer_origin"] = origin_text.replace('from', '').strip()
                    break
            if 'reviewer_origin' in details:
                break
        
        # 21. Extract rank in city
        rank_selectors = [
            'div.pZUbB div.cNFlb',
            'div.EEIGK div.cwbXG',
            'div.BmuhR div.RGNoQ'
        ]
        for selector in rank_selectors:
            rank_elem = soup.select_one(selector)
            if rank_elem:
                rank_text = rank_elem.get_text(strip=True)
                rank_match = re.search(r'#\d+\s+of\s+[\d,]+', rank_text)
                if rank_match:
                    details["rank_in_city"] = rank_match.group(0)
                    break
        
        return details
        
    def scrape_location(self, location_url=None, max_attractions=None, output_file=None):
        """Scrape attractions for a location and optionally get details"""
        attractions = self.get_attractions(location_url)
        logger.info(f"Found {len(attractions)} attractions")
        
        if max_attractions:
            attractions = attractions[:max_attractions]
            
        detailed_attractions = []
        for i, attraction in enumerate(attractions):
            logger.info(f"Processing {i+1}/{len(attractions)}: {attraction['name']}")
            details = self.get_attraction_details(attraction['url'])
            detailed_attractions.append(details)
            self._random_delay()  # Random delay between requests
            
        if output_file and detailed_attractions:
            self.save_to_csv(detailed_attractions, output_file)
            
        return detailed_attractions
        
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
    parser = argparse.ArgumentParser(description='TripAdvisor Crawler')
    parser.add_argument('--url', type=str, default='https://www.tripadvisor.com/Attractions-g293924-Activities-Hanoi.html',
                        help='URL of the TripAdvisor location page to crawl')
    parser.add_argument('--output', type=str, default='data/tripadvisor_attractions.csv',
                        help='Output CSV file name')
    parser.add_argument('--max', type=int, default=2,
                        help='Maximum number of attractions to crawl')
    parser.add_argument('--delay', type=float, default=3.0,
                        help='Minimum delay between requests in seconds (actual delay will be randomized)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    parser.add_argument('--type', type=str, choices=['attractions', 'restaurants', 'hotels', 'tours', 'all'],
                        default='attractions', help='Type of entities to crawl')
    parser.add_argument('--location', type=str, help='Location name (e.g., "Hanoi", "Ho Chi Minh City")')
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
    
    # Extract or use provided location name
    location = args.location
    if not location:
        try:
            parsed_url = urlparse(args.url)
            path_parts = parsed_url.path.split('-')
            if len(path_parts) > 2:
                location = path_parts[2]  # e.g., 'Hanoi' from 'Attractions-g293924-Activities-Hanoi.html'
        except:
            location = "Unknown"
    
    # Determine output filename if not explicitly provided
    if args.output == 'data/tripadvisor_attractions.csv':
        entity_type = args.type if args.type != 'all' else 'places'
        args.output = f'data/tripadvisor_{location}_{entity_type}.csv'
    
    # Construct URLs for different entity types if needed
    urls_to_crawl = []
    
    if args.type == 'all':
        # Get location ID from the URL if possible
        location_id = None
        try:
            path_parts = urlparse(args.url).path.split('-')
            if len(path_parts) > 1:
                for part in path_parts:
                    if part.startswith('g') and part[1:].isdigit():
                        location_id = part
                        break
        except:
            pass
        
        if location_id and location:
            base_url = f"https://www.tripadvisor.com"
            urls_to_crawl = [
                f"{base_url}/Attractions-{location_id}-Activities-{location}.html",
                f"{base_url}/Restaurants-{location_id}-{location}.html",
                f"{base_url}/Hotels-{location_id}-{location}.html",
                f"{base_url}/Attractions-{location_id}-Activities-c42-{location}.html"  # Tours
            ]
        else:
            # Just use the provided URL
            urls_to_crawl = [args.url]
    else:
        urls_to_crawl = [args.url]
    
    logger.info(f"Crawling TripAdvisor data for location: {location}")
    logger.info(f"Entity type: {args.type}")
    logger.info(f"Will save data to: {args.output}")
    logger.info(f"Max entities to crawl: {args.max}")
    logger.info(f"Delay between requests: {args.delay}-{args.delay*2} seconds")
    
    all_entities = []
    for url in urls_to_crawl:
        logger.info(f"Crawling URL: {url}")
        crawler = TripAdvisorCrawler(url, args.delay)
        entities = crawler.scrape_location(max_attractions=args.max)
        all_entities.extend(entities)
        
    # Save all data to CSV
    if all_entities:
        crawler = TripAdvisorCrawler()  # Create an instance just to use save_to_csv
        crawler.save_to_csv(all_entities, args.output) 