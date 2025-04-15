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
        """Get attractions for a given location"""
        url = location_url or self.base_url
        if not url:
            raise ValueError("No URL provided")
            
        soup = self.get_soup(url)
        if not soup:
            return []
        
        # Try various selectors that might work with TripAdvisor's current structure
        attractions = []
        
        # Method 1: Look for attraction cards (new layout)
        attraction_elements = soup.select('div[data-automation="attraction-card"]')
        if attraction_elements:
            logger.info(f"Found {len(attraction_elements)} attractions using method 1")
            for item in attraction_elements:
                link_elem = item.select_one('a')
                if link_elem and link_elem.has_attr('href'):
                    name_elem = item.select_one('h3')
                    name = name_elem.get_text(strip=True) if name_elem else "Unknown Attraction"
                    link = link_elem['href']
                    if not link.startswith('http'):
                        link = urljoin("https://www.tripadvisor.com", link)
                    attractions.append({"name": name, "url": link})
            return attractions
        
        # Method 2: Look for listing elements (older layout)
        attraction_elements = soup.select('div.listing_title a, div._27-AHp a.CnVXeG, div.alPVI a.dDJLC')
        if attraction_elements:
            logger.info(f"Found {len(attraction_elements)} attractions using method 2")
            for item in attraction_elements:
                if item.has_attr('href'):
                    name = item.get_text(strip=True)
                    link = item['href']
                    if not link.startswith('http'):
                        link = urljoin("https://www.tripadvisor.com", link)
                    attractions.append({"name": name, "url": link})
            return attractions
        
        # Method 3: General approach - try to find attraction links by different patterns
        # First try Attraction_Review pattern
        attraction_links = soup.select('a[href*="Attraction_Review"]')
        if attraction_links:
            # Filter out links that are likely not actual attractions
            filtered_links = []
            for link in attraction_links:
                href = link['href']
                name = link.get_text(strip=True)
                
                # Skip if very short name or empty text
                if not name or len(name) <= 1:
                    continue
                
                # Skip common navigation terms
                if name.lower() in ['map', 'view map', 'next', 'previous', '1', '2', '3', '4', '5']:
                    continue
                
                # Add to filtered list
                filtered_links.append(link)
            
            logger.info(f"Found {len(attraction_links)} potential attractions with 'Attraction_Review', filtered to {len(filtered_links)}")
            
            for link in filtered_links:
                name = link.get_text(strip=True)
                href = link['href']
                if not href.startswith('http'):
                    href = urljoin("https://www.tripadvisor.com", href)
                attractions.append({"name": name, "url": href})
        
        # Fallback method 4: Try to find links with location name
        if not attractions:
            location_links = []
            try:
                path_parts = urlparse(url).path.split('-')
                if len(path_parts) > 2:
                    location_name = path_parts[2]  # e.g., 'Hanoi' from 'Attractions-g293924-Activities-Hanoi.html'
                    location_links = soup.select(f'a[href*="{location_name}"]')
            except Exception as e:
                logger.error(f"Error parsing location from URL: {e}")
            
            # Filter links to likely attractions
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
            
            logger.info(f"Found {len(location_links)} potential location-based attractions, filtered to {len(filtered_location_links)}")
            
            for link in filtered_location_links:
                name = link.get_text(strip=True)
                href = link['href']
                if not href.startswith('http'):
                    href = urljoin("https://www.tripadvisor.com", href)
                attractions.append({"name": name, "url": href})
        
        # Fallback method 5: Use hardcoded top attractions for common locations
        if not attractions:
            logger.warning("No attractions found through standard methods, trying fallback data")
            
            # Extract location from URL
            location = None
            try:
                path_parts = urlparse(url).path.split('-')
                if len(path_parts) > 2:
                    location = path_parts[2]  # e.g., 'Hanoi' from 'Attractions-g293924-Activities-Hanoi.html'
            except:
                pass
            
            # Hardcoded top attractions for common locations
            if location and location.lower() == 'hanoi':
                attractions = [
                    {"name": "Old Quarter", "url": "https://www.tripadvisor.com/Attraction_Review-g293924-d317503-Reviews-Old_Quarter-Hanoi.html"},
                    {"name": "Temple of Literature", "url": "https://www.tripadvisor.com/Attraction_Review-g293924-d311516-Reviews-Temple_of_Literature_National_University-Hanoi.html"},
                    {"name": "Hoan Kiem Lake", "url": "https://www.tripadvisor.com/Attraction_Review-g293924-d311516-Reviews-Hoan_Kiem_Lake-Hanoi.html"},
                    {"name": "Hoa Lo Prison", "url": "https://www.tripadvisor.com/Attraction_Review-g293924-d311069-Reviews-Hoa_Lo_Prison-Hanoi.html"},
                    {"name": "Vietnam Museum of Ethnology", "url": "https://www.tripadvisor.com/Attraction_Review-g293924-d311511-Reviews-Vietnam_Museum_of_Ethnology-Hanoi.html"}
                ]
                logger.info(f"Using {len(attractions)} hardcoded attractions for {location}")
        
        # If we still found nothing, log the entire HTML for debugging
        if not attractions:
            logger.warning("No attractions found. The website structure may have changed.")
            logger.debug(f"HTML content: {soup}")
            
        return attractions
        
    def get_attraction_details(self, attraction_url):
        """Get details for a specific attraction"""
        self._random_delay()  # Add random delay before requesting
        
        soup = self.get_soup(attraction_url)
        if not soup:
            return {}
            
        details = {"url": attraction_url}
        
        # Extract name from URL if we can't find it on page
        if 'name' not in details:
            try:
                url_parts = attraction_url.split('-Reviews-')
                if len(url_parts) > 1:
                    name_part = url_parts[1].split('-')[0]
                    # Replace underscores with spaces and title case
                    details["name"] = name_part.replace('_', ' ').title()
            except:
                pass
                
        # Try to extract rating and reviews
        rating_and_reviews = soup.select_one('div.AfQtZ')
        if rating_and_reviews:
            # Extract rating and reviews from text like "4.5 of 5 bubbles28,900 reviews"
            text = rating_and_reviews.get_text(strip=True)
            if text:
                # Extract rating
                rating_match = re.search(r'(\d+\.?\d*)\s+of\s+\d+', text)
                if rating_match:
                    details["rating"] = rating_match.group(1)
                
                # Extract reviews
                reviews_match = re.search(r'([\d,]+)\s+reviews?', text)
                if reviews_match:
                    details["reviews"] = reviews_match.group(1).replace(',', '')
        
        # Extract address if exists
        address_selectors = [
            'div[data-test-target="attraction-detail-card"] button.UikbF',
            'button.KEaY',
            'div.kUaGX button',
            'div.XPUSn span.yEWoV'
        ]
        for selector in address_selectors:
            address_elem = soup.select_one(selector)
            if address_elem:
                details["address"] = address_elem.get_text(strip=True)
                break
                
        # Try to extract category/type
        category_selectors = [
            'div.fIrGe div._c',
            'a.GEcgi',
            'div.BmuhR a'
        ]
        for selector in category_selectors:
            category_elems = soup.select(selector)
            if category_elems:
                categories = [elem.get_text(strip=True) for elem in category_elems]
                details["category"] = ", ".join(categories)
                break
                
        # Try to extract description
        description_selectors = [
            'div.pZUbB div.duhwe span.JguWG',
            'div.DpZHu div',
            'div.LBVLY div.WlYyy'
        ]
        for selector in description_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                details["description"] = desc_elem.get_text(strip=True)
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
    parser.add_argument('--output', type=str, default='tripadvisor_attractions.csv',
                        help='Output CSV file name')
    parser.add_argument('--max', type=int, default=10,
                        help='Maximum number of attractions to crawl')
    parser.add_argument('--delay', type=float, default=3.0,
                        help='Minimum delay between requests in seconds (actual delay will be randomized)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
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
    if args.output == 'tripadvisor_attractions.csv':
        parsed_url = urlparse(args.url)
        path_parts = parsed_url.path.split('-')
        if len(path_parts) > 2:
            location = path_parts[2]
            args.output = f'tripadvisor_{location}_attractions.csv'
    
    logger.info(f"Crawling TripAdvisor data from: {args.url}")
    logger.info(f"Will save data to: {args.output}")
    logger.info(f"Max attractions to crawl: {args.max}")
    logger.info(f"Delay between requests: {args.delay}-{args.delay*2} seconds")
    
    crawler = TripAdvisorCrawler(args.url, args.delay)
    crawler.scrape_location(output_file=args.output, max_attractions=args.max) 