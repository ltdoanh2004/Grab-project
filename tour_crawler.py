#!/usr/bin/env python3
"""
Enhanced Hanoi TripAdvisor Attractions Crawler
A specialized crawler that extracts clean, structured attraction details from TripAdvisor.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
import random
import re
import logging
from urllib.parse import urljoin
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("hanoi_attractions_crawler.log")
    ]
)
logger = logging.getLogger(__name__)

class EnhancedAttractionsCrawler:
    """Enhanced crawler for TripAdvisor attractions in Hanoi with better data extraction"""
    
    def __init__(self, base_url=None, delay=3.0, custom_type=None):
        self.base_url = base_url or "https://www.tripadvisor.com/Attractions-g293924-Activities-a_allAttractions.true-Hanoi.html"
        self.min_delay = delay
        self.max_delay = delay * 2  # Randomize delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.tripadvisor.com/'
        }
        self.visited_urls = set()  # Track visited URLs to avoid duplicates
        self.visited_attractions = set()  # Track attraction names to avoid duplicates
        self.custom_type = custom_type  # User-specified attraction type
        
    def _random_delay(self):
        """Add a random delay between requests to avoid being blocked"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.info(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)
        
    def get_soup(self, url, retries=3):
        """Get BeautifulSoup object from URL with retries"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching URL: {url}")
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                # Check if we got a captcha page
                if "captcha" in response.text.lower() or "please enable js" in response.text.lower():
                    logger.warning("Captcha detected! Try using a different approach or wait longer between requests")
                    if attempt < retries - 1:
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
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 30
                    logger.info(f"Retrying after {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
        return None

    def get_attraction_listings(self, url=None, page=1):
        """Get attraction listings from the TripAdvisor page"""
        current_url = url or self.base_url
        
        # Add page parameter if not first page
        if page > 1:
            if "oa" in current_url:
                current_url = re.sub(r'oa\d+', f'oa{(page-1)*30}', current_url)
            else:
                # Insert before .html or add at the end
                if '.html' in current_url:
                    current_url = current_url.replace('.html', f'-oa{(page-1)*30}.html')
                else:
                    current_url = f"{current_url}-oa{(page-1)*30}"
                
        logger.info(f"Getting attraction listings from page {page}: {current_url}")
        
        soup = self.get_soup(current_url)
        if not soup:
            return [], False
            
        attractions = []
        
        # Various selectors to extract URLs from attraction cards
        attraction_url_selectors = [
            'a.WllYF',
            'a.BMQDV',
            'a.alPVI',
            'a.ZXsl',
            'a.property_title',
            'a.heading',
            'a[data-automation="photo-link"]',
            'div.BCRHq a',
            'div a.TZVMl',
            'a.gfCGZ',
            'a.dlMOJ',
            'a.kBmqM',
            'a.ZcNoO',
            'div.VQlbfs a',
            'a.rmyCe', # New selector for links
            'a.iPqaD', # New product link
            'a.JXbvE', # New listing link format
            'a.VLKGO', # Latest card link format
            'a.tRmNF', # Latest link class
            'article a',  # Fallback for article-based cards
            'a' # Fallback selector
        ]
        
        # Selectors for name when we have the card itself
        name_selectors = [
            'div.XfVdV h3.biGQs',
            'div.jemSU span',
            'div.YsYxh',
            'div.ZoUyE h3',
            'a.dOGcA h2',
            'a span.eQSJI',
            'span.FzRCx',
            'div.keSJH h2',
            'div.zNmOp div',
            'h3.mPZIx',
            'h3.cJhIa',
            'div.iBMJX h3',
            'h3.WlYyy',
            'div.aLfbo h3',
            'h3.biGQs',
            'div.vQlbfs div[data-automation="listing-title"] span',
            'h3.yZXYn', # New card title class
            'h3.JwvYK', # New title format
            'span.NhWcC', # Latest product name format
            'span.KqEEi', # Latest title class
            'h3.KegBk', # Alternative title class
            'div.qoizX span'  # New title container
        ]
        
        # Debug - print the entire HTML structure if needed
        # with open('debug_page.html', 'w', encoding='utf-8') as f:
        #     f.write(str(soup))
        
        found_attractions = False
        for selector in attraction_url_selectors:
            attraction_elements = soup.select(selector)
            if attraction_elements:
                logger.info(f"Found {len(attraction_elements)} attractions using selector: {selector}")
                found_attractions = True
                
                for item in attraction_elements:
                    # FIXED: Add a direct check for attraction links by looking for Attraction_Review
                    attraction_link = None
                    # First try links within the card
                    attraction_link = item.find('a', href=lambda href: href and ('Attraction_Review' in href or 'AttractionProductDetail' in href))
                    
                    # If nothing found, try looking at the parent container
                    if not attraction_link and item.parent:
                        attraction_link = item.parent.find('a', href=lambda href: href and ('Attraction_Review' in href or 'AttractionProductDetail' in href))
                    
                    if attraction_link and attraction_link.has_attr('href'):
                        href = attraction_link['href']
                        # Make sure it's an absolute URL
                        if not href.startswith('http'):
                            href = urljoin("https://www.tripadvisor.com", href)
                        
                        # Skip if we've already processed this URL
                        if href in self.visited_urls:
                            continue
                        
                        # Try to find the name
                        name = None
                        # First check if the link itself has text
                        if attraction_link.text and len(attraction_link.text.strip()) > 0:
                            name = attraction_link.text.strip()
                        else:
                            # Try to find a title/name element nearby
                            name_elements = item.select('h3, h2, div.biGQs, span.biGQs, div.name, div.listing_title, div.DTUQm, span.DTUQm, div.bAJzS, h1, a.xkSty, ' + 
                                                         'h3.yZXYn, h3.JwvYK, span.NhWcC, span.KqEEi, h3.KegBk, div.qoizX span')
                            for name_elem in name_elements:
                                if name_elem.text and len(name_elem.text.strip()) > 0:
                                    name = name_elem.text.strip()
                                    break
                        
                        # If still no name, use a default
                        if not name:
                            name = "Unknown Attraction"
                        
                        # Clean up the name
                        name = re.sub(r'\d+(\.\d+)?\s+of\s+5\s+bubbles', '', name)
                        name = re.sub(r'[\d,]+\s+reviews?', '', name)
                        name = name.strip()
                        
                        # Find image if available
                        image_url = None
                        img_elem = item.find('img')
                        if img_elem and img_elem.has_attr('src'):
                            image_url = img_elem['src']
                            # Check for data-src for lazy-loaded images
                            if img_elem.has_attr('data-src'):
                                image_url = img_elem['data-src']
                            
                            # Make image URL absolute
                            if not image_url.startswith('http'):
                                image_url = urljoin("https://www.tripadvisor.com", image_url)
                        
                        # Find rating if available
                        rating = None
                        rating_elem = item.select_one('span.ui_bubble_rating, svg.jWkzb, span.bvcyz, [data-automation="bubbleRatingValue"]')
                        if rating_elem:
                            # Try to extract from class
                            rating_class = rating_elem.get('class', [])
                            for cls in rating_class:
                                if 'bubble_' in cls:
                                    try:
                                        rating = float(rating_elem.get_text(strip=True))
                                        print(rating)
                                        break
                                    except (IndexError, ValueError):
                                        pass
                        
                        # Create the attraction object
                        attraction_data = {
                            "name": name,
                            "url": href
                        }
                        
                        if image_url:
                            attraction_data["thumbnail_url"] = image_url
                        
                        if rating is not None:
                            attraction_data["rating"] = rating
                        
                        attractions.append(attraction_data)
                        self.visited_urls.add(href)  # Mark as visited
                        
                        # Debug log for each attraction found
                        logger.info(f"Found attraction: {name} - {href}")
                
                if attractions:
                    break
        
        logger.info(f"Found {len(attractions)} attractions on page {page}")
        if not attractions and found_attractions:
            logger.warning("Found attraction elements but couldn't extract any valid attraction data.")
            logger.warning("Consider running with --debug flag to save the HTML for inspection.")
            
            # Add fallback method to extract any link that might be an attraction
            all_links = soup.select('a')
            attraction_links = []
            
            # First, gather meaningful links with proper URLs
            for link in all_links:
                if not link.has_attr('href'):
                    continue
                    
                href = link['href']
                # Only consider links that look like attraction links
                if 'Attraction_Review' in href and href not in self.visited_urls:
                    text = link.get_text(strip=True)
                    # Skip "Review of:" links that are duplicates
                    if text and text.startswith("Review of:"):
                        continue
                    # Skip very short texts, empty texts, ratings, and numbers
                    if not text or len(text) < 3 or re.match(r'^[\d.]+$', text):
                        continue
                    # Skip navigation links
                    if text in ['Next', 'Previous', '1', '2', '3', '4', '5']:
                        continue
                        
                    # Clean the name from ratings, reviews, etc.
                    name = re.sub(r'\d+(\.\d+)?\s+of\s+5\s+bubbles', '', text)
                    name = re.sub(r'[\d,]+\s+reviews?', '', name)
                    name = name.strip()
                    
                    # Make URL absolute
                    if not href.startswith('http'):
                        href = urljoin("https://www.tripadvisor.com", href)
                    
                    # Add to potential attractions list if it looks like a name    
                    if name and len(name) > 3 and not name.isdigit() and not re.match(r'^\d+\.\s*$', name):
                        attraction_links.append((name, href))
                        logger.info(f"Fallback found potential attraction: {name}")
            
            # Sort by name length (longer names are usually more meaningful) 
            # and deduplicate by URL
            seen_urls = set()
            for name, href in sorted(attraction_links, key=lambda x: len(x[0]), reverse=True):
                if href in seen_urls:
                    continue
                
                attractions.append({
                    "name": name,
                    "url": href
                })
                self.visited_urls.add(href)
                seen_urls.add(href)
                logger.info(f"Added fallback attraction: {name}")
                
                # Limit to 30 attractions per page to avoid excessive processing
                if len(attractions) >= 30:
                    break
        
        # Look for "Next" button to determine if there are more pages
        has_next_page = False
        next_selectors = [
            'a[data-smoke-attr="pagination-next-arrow"]',
            'a.nav.next', 
            'a.ui_button.nav.next', 
            'a[data-page-number="next"]', 
            'a.BrOJk[href*="oa"]',
            'a.JSRZY', 
            'button[data-automation="pagination-button-next"]'
        ]
        
        for selector in next_selectors:
            next_buttons = soup.select(selector)
            for btn in next_buttons:
                if ("next" in btn.get_text().lower() or 
                    "next" in str(btn.get('class', [])).lower() or 
                    "oa" in btn.get('href', '') or
                    "→" in btn.get_text() or
                    "pagination-next" in str(btn)):
                    has_next_page = True
                    break
            if has_next_page:
                break
        
        return attractions, has_next_page
    
    def _extract_clean_address(self, soup):
        """Extract just the address from the soup, using improved selectors"""
        address = None
        
        # Try to find address with various selectors
        address_selectors = [
            'span.DsyBj[data-test-target="detailsAddressInfo"]',
            'div[data-automation="location__address"]',
            'div.czkFU a',
            'button.KTXIj',
            'div.XQaIe',
            'div.euDRl > a',
            'div[data-automation="WebPresentation_LocalizationMapCard"] div.euDRl',
            'div[data-automation="WebPresentation_PoiLocationCard"] div.euDRl',
            'div.euDRl > div[data-automation="webPresentation"]'
        ]
        
        for selector in address_selectors:
            addr_elem = soup.select_one(selector)
            if addr_elem:
                address_text = addr_elem.get_text(strip=True)
                # Clean up any "Address" label
                address_text = re.sub(r'^Address\s*', '', address_text)
                # Check if we have a reasonable address
                if address_text and len(address_text) > 5 and len(address_text) < 200:
                    address = address_text
                    break
        
        # If not found, try looking for a specific pattern in the text
        if not address:
            # Look for a pattern like "27 Hang Be Hang Bac, Hoan Kiem, Hanoi 100000 Vietnam"
            addr_pattern = re.compile(r'(\d+\s+[\w\s]+,\s+[\w\s]+,\s+Hanoi\s+\d+\s+Vietnam)', re.IGNORECASE)
            for script in soup.find_all('script'):
                if script.string and addr_pattern.search(script.string):
                    address = addr_pattern.search(script.string).group(1)
                    break
            
            # Try to find it in any div text
            if not address:
                for div in soup.find_all('div'):
                    text = div.get_text(strip=True)
                    if addr_pattern.search(text):
                        address = addr_pattern.search(text).group(1)
                        break
        
        # One more method - check for "The area" text and extract what follows
        if not address:
            area_text = soup.find(string=re.compile(r'The\s+area', re.IGNORECASE))
            if area_text:
                parent = area_text.parent
                if parent:
                    next_elem = parent.next_sibling
                    if next_elem:
                        addr_text = next_elem.get_text(strip=True)
                        if addr_text and len(addr_text) > 5 and len(addr_text) < 200:
                            address = addr_text
        
        return address
    
    def _extract_clean_opening_hours(self, soup):
        """Extract just the opening hours from the soup"""
        hours = None
        
        # Try specific hours selectors
        hours_selectors = [
            'div[data-automation="WebPresentation_PoiOpenHours"]',
            'div.IMlHP',
            'div.QvzAT',
            'div.YbkpN',
            'div.JguWG:contains("Open now")',
            'div:contains("Open today")',
            'div:contains("Hours:")',
            'div[data-section-id="HoursSection"]'
        ]
        
        for selector in hours_selectors:
            if ':contains' in selector:
                base_selector, contains_text = selector.split(':contains(')
                contains_text = contains_text.rstrip(')')
                contains_text = contains_text.strip('"\'')
                
                elements = soup.select(base_selector)
                for elem in elements:
                    if contains_text in elem.get_text():
                        hours_text = elem.get_text(strip=True)
                        # Clean up to just get times
                        hours_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M\s*-\s*\d{1,2}:\d{2}\s*[AP]M)', hours_text)
                        if hours_match:
                            hours = hours_match.group(1)
                        else:
                            hours = hours_text
                        break
            else:
                hours_elem = soup.select_one(selector)
                if hours_elem:
                    hours_text = hours_elem.get_text(strip=True)
                    if hours_text and ('open' in hours_text.lower() or 'hour' in hours_text.lower() or 'am' in hours_text.lower() or 'pm' in hours_text.lower()):
                        # Clean up to just get times
                        hours_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M\s*-\s*\d{1,2}:\d{2}\s*[AP]M)', hours_text)
                        if hours_match:
                            hours = hours_match.group(1)
                        else:
                            # Limit to a reasonable length
                            if len(hours_text) < 50:
                                hours = hours_text
                        break
        
        # Try looking for time pattern directly
        if not hours:
            time_pattern = re.compile(r'\d{1,2}:\d{2}\s*[AP]M\s*-\s*\d{1,2}:\d{2}\s*[AP]M')
            time_elems = soup.find_all(string=time_pattern)
            if time_elems:
                for elem in time_elems:
                    match = time_pattern.search(elem)
                    if match:
                        hours = match.group(0)
                        break
        
        return hours
    
    def _extract_clean_duration(self, soup):
        """Extract just the duration from the soup"""
        duration = None
        
        # Try specific duration selectors
        duration_selectors = [
            'svg[aria-label="Duration"] + div',
            'div:contains("Duration:")',
            'div:contains("Suggested duration:")',
            'div[data-automation="WebPresentation_PoiDetailsTags"] span:contains("hour")',
            'div.eYKGZ:contains("Duration")'
        ]
        
        for selector in duration_selectors:
            if ':contains' in selector:
                base_selector, contains_text = selector.split(':contains(')
                contains_text = contains_text.rstrip(')')
                contains_text = contains_text.strip('"\'')
                
                elements = soup.select(base_selector)
                for elem in elements:
                    if contains_text in elem.get_text():
                        duration_text = elem.get_text(strip=True)
                        # Extract just the duration part (e.g., "1-2 hours")
                        duration_match = re.search(r'(?:duration|suggested duration)[:\s]*([^,;]+)', duration_text, re.IGNORECASE)
                        if duration_match:
                            duration = duration_match.group(1).strip()
                        elif 'hour' in duration_text.lower():
                            duration = duration_text
                        break
            else:
                duration_elem = soup.select_one(selector)
                if duration_elem:
                    duration_text = duration_elem.get_text(strip=True)
                    if 'hour' in duration_text.lower() or 'min' in duration_text.lower():
                        # Clean it up
                        duration_match = re.search(r'((?:\d+(?:-\d+)?\s+hours?)|(?:\d+(?:-\d+)?\s+minutes?))', duration_text)
                        if duration_match:
                            duration = duration_match.group(1)
                        else:
                            # Remove any irrelevant text
                            duration = re.sub(r'suggest.*?edit.*', '', duration_text)
                            duration = duration.strip()
                        break
        
        # If we didn't find it with selectors, look for text patterns
        if not duration:
            hour_pattern = re.compile(r'(\d+-\d+\s+hours?|\d+\s+hours?|\d+-\d+\s+min|\d+\s+min)')
            for div in soup.find_all('div'):
                text = div.get_text(strip=True)
                match = hour_pattern.search(text)
                if match and len(text) < 100:  # Ensure it's a reasonable string
                    duration = match.group(1)
                    break
        
        return duration
    
    def _clean_name(self, name):
        """Clean up the attraction name"""
        if not name:
            return "Unknown Attraction"
            
        # Remove claim/ownership text
        name = re.sub(r'If you own this business.*', '', name, flags=re.IGNORECASE)
        # Remove review counts
        name = re.sub(r'\d+(\.\d+)?\s+of\s+5\s+bubbles', '', name)
        name = re.sub(r'[\d,]+\s+reviews?', '', name)
        # Remove any trailing numbers or punctuation
        name = re.sub(r'\s*\(\d+\)\s*$', '', name)
        return name.strip()
    
    def get_attraction_details(self, attraction_url):
        """Get detailed information about an attraction"""
        self._random_delay()
        
        soup = self.get_soup(attraction_url)
        if not soup:
            return {"url": attraction_url, "error": "Failed to fetch attraction page"}
            
        # Initialize the attraction details
        details = {
            "url": attraction_url
        }
        
        # 1. Extract name with better cleaning
        name_selectors = [
            'div.MhXlV h1',  # New selector for attraction title
            'div.bFQvZ h1',   # New header container
            'h1.QdLfr',
            'h1.eIegw',
            'h1.HjBfq',
            'div.pZUbB h1',
            'div.aRRrc h1',
            'div.fiohW h1',
            'div.ITQHd h1',
            'div.vQlbfs h1',
            'h1',
            'div[data-automation="WebPresentation_AttractionTitle"] h1'
        ]
        for selector in name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                details["name"] = self._clean_name(name_elem.get_text(strip=True))
                break
        
        # Extract name from URL if not found on page
        if 'name' not in details or not details['name'] or details['name'] == "Unknown Attraction":
            try:
                if 'Attraction_Review' in attraction_url:
                    url_parts = attraction_url.split('-')
                    name_part = url_parts[-2] if len(url_parts) > 2 else ""
                    details["name"] = name_part.replace('_', ' ').title()
            except Exception as e:
                logger.error(f"Error extracting name from URL {attraction_url}: {e}")
                details["name"] = "Unknown Attraction"
        
        # 2. Extract address with better cleaning
        address = self._extract_clean_address(soup)
        if address:
            details["address"] = address
        
        # 3. Extract description (About section)
        description_selectors = [
            'div.pZUbB div.duhwe span.JguWG',
            'div.DpZHu div',
            'div.LBVLY div.WlYyy',
            'div[data-automation="WebPresentation_AttractionOverviewSection"]',
            'div.fIrGe',
            'div.TTTpR',
            'div.XfVdV div.JguWG',
            'div.pZUbB div.eSywT',
            'div.euDRl',
            'div.ecNAQ',
            'section[data-automation="WebPresentation_POIAboutSection"] div',
            'div[data-automation="WebPresentation_POIAboutSection"] div',
            'section[data-section-id="AboutSection"]',
            'div#ABOUT'
        ]
        for selector in description_selectors:
            desc_elems = soup.select(selector)
            if desc_elems:
                for desc_elem in desc_elems:
                    description_text = desc_elem.get_text(strip=True)
                    if description_text and len(description_text) > 20:  # Ensure it's a meaningful description
                        details["description"] = description_text
                        break
                if "description" in details:
                    break
        
        # Special check for "About" heading
        if 'description' not in details:
            about_headings = soup.find_all(['h2', 'h3'], string=lambda s: s and 'about' in s.lower())
            for heading in about_headings:
                desc_container = heading.find_next(['div', 'p'])
                if desc_container:
                    description_text = desc_container.get_text(strip=True)
                    if description_text and len(description_text) > 20:
                        details["description"] = description_text
                        break
        
        # 4. Extract opening hours - improved
        opening_hours = self._extract_clean_opening_hours(soup)
        if opening_hours:
            details["opening_hours"] = opening_hours
        
        # 5. Extract "Duration" information - improved
        duration = self._extract_clean_duration(soup)
        if duration:
            details["duration"] = duration
        
        # Apply custom type if provided, otherwise use extracted type
        if self.custom_type:
            details["type"] = self.custom_type
        else:
            # 9. Extract type/category - IMPROVED IMPLEMENTATION
            type_selectors = [
                'div.aSJLV a',
                'div.EEIGK a',
                'div.CskSA a',
                'div.xkSty a',
                'div.IKxsX a',
                'div.dyezQ a',
                'a.cMKgw',  # Additional selectors for type
                'a[href*="Attractions-g293924-Activities-c"]',  # Category links
                'div.bJQut span',  # Category bubbles/tags
                'div.KgSvs a',  # New selector for categories
                'div.VZeht a',  # Another category selector
                'div.fINpo a',  # Breadcrumb selectors that might contain type
                'div.fINpo span'
            ]
            
            attraction_type = "Attraction"  # Default type
            type_categories = []
            
            # First try to extract from breadcrumbs which often has the most specific type
            breadcrumb_selectors = [
                'div.fINpo a',
                'div.fINpo span',
                'div.drcGn a',
                'div.breadcrumb a',
                'div.TkWMV a',
                'ul.breadcrumbs li a',
                '.crumbs a'
            ]
            
            breadcrumb_types = []
            for selector in breadcrumb_selectors:
                breadcrumb_elems = soup.select(selector)
                for elem in breadcrumb_elems:
                    type_text = elem.get_text(strip=True)
                    # Skip general location breadcrumbs
                    if (type_text and len(type_text) > 1 and 
                        type_text.lower() not in ['hanoi', 'vietnam', 'asia', 'things to do', 'home']):
                        breadcrumb_types.append(type_text)
            
            # Look for the most specific type in the URL
            if 'Attractions-g293924-Activities-c' in attraction_url:
                category_match = re.search(r'Activities-c(\d+)', attraction_url)
                if category_match:
                    # Try to extract the category from the page content
                    activity_type_elems = soup.select('h2.RyMnA, h2.YzSip, h1 + div span')
                    for elem in activity_type_elems:
                        type_text = elem.get_text(strip=True)
                        if type_text and len(type_text) > 1 and type_text.lower() not in ['hanoi', 'vietnam', 'asia']:
                            type_categories.append(type_text)
                            # Update the main attraction type
                            attraction_type = type_text
                            break
            
            # If we found specific types in breadcrumbs, use them
            if breadcrumb_types:
                # Sort by length to get the most specific (usually longer) type
                sorted_types = sorted(breadcrumb_types, key=len, reverse=True)
                if sorted_types:
                    type_categories.extend(sorted_types)
                    # Update the main attraction type to the most specific one
                    attraction_type = sorted_types[0]
            
            # Use the regular type selectors as fallback
            if not type_categories:
                for selector in type_selectors:
                    type_elems = soup.select(selector)
                    for elem in type_elems:
                        type_text = elem.get_text(strip=True)
                        if type_text and len(type_text) > 1 and type_text.lower() not in ['hanoi', 'vietnam', 'asia']:
                            type_categories.append(type_text)
            
            # For specific known attraction types, check meta tags and descriptions
            spa_keywords = ['spa', 'massage', 'wellness']
            tour_keywords = ['tour', 'excursion', 'trip', 'journey']
            food_keywords = ['restaurant', 'dining', 'food', 'cuisine']
            
            for meta in soup.find_all('meta', {'name': ['description', 'keywords']}):
                if meta.has_attr('content'):
                    content = meta['content'].lower()
                    
                    # Check for specific attraction types
                    if any(keyword in content for keyword in spa_keywords) and "spa" not in attraction_type.lower():
                        attraction_type = "Spas"
                        type_categories.append("Spas")
                        
                    elif any(keyword in content for keyword in tour_keywords) and "tour" not in attraction_type.lower():
                        attraction_type = "Tours"
                        type_categories.append("Tours")
                        
                    elif any(keyword in content for keyword in food_keywords) and "restaurant" not in attraction_type.lower():
                        attraction_type = "Restaurants"
                        type_categories.append("Restaurants")
            
            # Set the primary type
            details["type"] = attraction_type
            
            # Instead of a long comma-separated string, store categories as a list
            if type_categories:
                details["categories"] = list(set(type_categories[:5]))  # Limit to 5 unique categories
        
        # 6. Extract images - IMPROVED IMPLEMENTATION to get more images
        image_urls = []
        
        # Find high-resolution images from PhotoViewer links
        photo_viewer_selectors = [
            'a.iTxXD',
            'a.IXaZR',
            'a.cWwQK',
            'a[href*="PhotoViewer"]',
            'a[data-automation="photo"]',
            'a[data-testid="photo-viewer"]',
            'div.pZUbB a.cWwQK'
        ]
        
        photo_ids = []
        for selector in photo_viewer_selectors:
            photo_links = soup.select(selector)
            for link in photo_links:
                if link.has_attr('href') and 'PhotoViewer' in link['href']:
                    # Extract all photo IDs from the link
                    photo_matches = re.findall(r'-i(\d+)-', link['href'])
                    photo_ids.extend(photo_matches)
        
        # Deduplicate photo IDs and construct high-quality image URLs
        for photo_id in set(photo_ids):
            hq_img_url = f"https://dynamic-media-cdn.tripadvisor.com/media/photo-o/{photo_id}.jpg?w=1200&h=-1&s=1"
            if hq_img_url not in image_urls:
                image_urls.append(hq_img_url)
        
        # Find the main hero image
        hero_img_selectors = [
            'picture.PpCRE img',
            'div.vwOfI img',
            'div.VQlbfs img',
            'div.ITQHd picture img',
            'div.HRZla img.dDwZr',
            'picture.MCCLx img',
            'div.zgdjX img',
            'div[data-automation="WebPresentation_PhotoCarousel"] img',
            'div.euDRl img',
            'img.eqVDQ',
            'div[data-automation="WebPresentation_SinglePhoto"] img',
            'div[data-automation="PhotoTile"] img'
        ]
        
        for selector in hero_img_selectors:
            hero_imgs = soup.select(selector)
            for hero_img in hero_imgs:
                if hero_img and hero_img.has_attr('src'):
                    img_url = hero_img['src']
                    # Check other attributes for higher quality image
                    for attr in ['data-src', 'data-lazy', 'data-srcset', 'data-lazyurl']:
                        if hero_img.has_attr(attr):
                            img_url = hero_img[attr]
                            break
                    
                    # Improve image quality by modifying URL parameters
                    img_url = re.sub(r'-s\d+x\d+', '-s1600x1200', img_url)
                    
                    # Make absolute URL
                    if not img_url.startswith('http'):
                        img_url = urljoin("https://www.tripadvisor.com", img_url)
                    
                    # Add to images list
                    if img_url not in image_urls:
                        image_urls.append(img_url)
        
        # Get gallery images
        gallery_selectors = [
            'div.MRIyS picture img',
            'div.UCacc img',
            'div.HRZla img',
            'div.pZUbB img',
            'div.EUuew img',
            'div[data-automation="WebPresentation_LargePhoto"] img',
            'div.IhqAp img',
            'div.JiEzc img',
            'div.NVVJp img',
            'div.euDRl img',
            'div.vQlbfs img',
            'div.fXMsMw img'
        ]
        
        for selector in gallery_selectors:
            img_elems = soup.select(selector)
            for img in img_elems:
                if img.has_attr('src'):
                    img_url = img['src']
                    # Check data-src attribute for lazy-loaded images
                    for attr in ['data-src', 'data-lazy', 'data-srcset', 'data-lazyurl']:
                        if img.has_attr(attr):
                            img_url = img[attr]
                            break
                    
                    # Improve image quality by modifying URL parameters
                    img_url = re.sub(r'-s\d+x\d+', '-s1600x1200', img_url)
                    
                    # Remove tracking parameters
                    img_url = img_url.split('?')[0]
                    
                    # Make sure the image URL is absolute
                    if not img_url.startswith('http'):
                        img_url = urljoin("https://www.tripadvisor.com", img_url)
                    
                    # Avoid duplicates and skip very small images
                    if img_url not in image_urls and 'icons' not in img_url.lower() and not re.search(r'-s\d+x\d+', img_url):
                        image_urls.append(img_url)
        
        # Add images to details - increased limit to collect more images
        if image_urls:
            # Remove duplicates but increase limit to 10 images
            unique_images = list(dict.fromkeys(image_urls))[:10]  # Increased from 5 to 10
            details["image_urls"] = unique_images
            details["main_image"] = unique_images[0]  # Main image
        
        # Add social media image URL as a fallback
        if 'main_image' not in details:
            og_image = soup.select_one('meta[property="og:image"]')
            if og_image and og_image.has_attr('content'):
                img_url = og_image['content']
                # Make sure the image URL is absolute
                if not img_url.startswith('http'):
                    img_url = urljoin("https://www.tripadvisor.com", img_url)
                
                details["main_image"] = img_url
                details["image_urls"] = [img_url]
        
        # 7. Extract price/admission fee
        fee_selectors = [
            'div.NXSyd:contains("Admission tickets")',
            'div[data-automation="WebPresentation_POIPricingSection"]',
            'div.CEQvT:contains("Price")',
            'div.XfVdV:contains("fees")',
            'div.euDRl:contains("Admission")',
            'div.euDRl:contains("Price")',
            'div.euDRl:contains("Ticket")',
            'div:contains("price")'
        ]
        
        for selector in fee_selectors:
            # For selectors with :contains, we need a different approach
            if ':contains' in selector:
                base_selector, contains_text = selector.split(':contains(')
                contains_text = contains_text.rstrip(')')
                contains_text = contains_text.strip('"\'')
                
                elements = soup.select(base_selector)
                for elem in elements:
                    if contains_text.lower() in elem.get_text().lower():
                        fee_text = elem.get_text(strip=True)
                        # Look for price patterns like $X, X USD, free, etc.
                        price_match = re.search(r'(\$[\d,.]+|[\d,.]+ VND|free|Free|included|Included)', fee_text)
                        if price_match:
                            details["price"] = price_match.group(1)
                        else:
                            # If there's no direct match but the section is about tickets, save the full text
                            if 'ticket' in fee_text.lower() or 'admission' in fee_text.lower() or 'price' in fee_text.lower() or 'fee' in fee_text.lower():
                                details["price"] = fee_text
                        break
            else:
                fee_elem = soup.select_one(selector)
                if fee_elem:
                    fee_text = fee_elem.get_text(strip=True)
                    price_match = re.search(r'(\$[\d,.]+|[\d,.]+ VND|free|Free|included|Included)', fee_text)
                    if price_match:
                        details["price"] = price_match.group(1)
                    else:
                        # If there's no direct match but the section is about tickets, save the full text
                        if 'ticket' in fee_text.lower() or 'admission' in fee_text.lower() or 'price' in fee_text.lower() or 'fee' in fee_text.lower():
                            details["price"] = fee_text
                    break
        
        # 8. Extract rating
        rating_selectors = [
            'span.UctUV',  # New rating selector
            'div.grdwI span.UctUV',  # Rating with container
            'div.xjlO span',  # New rating element
            'span.ui_bubble_rating',
            'div.rWAMq',
            'div.WdWxQ',
            'div.oETBb',
            'div.jT3cZ',
            'div.fwxfp',
            'span.bhvpg',
            'span.qMsuS',
            'div.jVDfQ span',
            'div.oETBb span'
        ]
        for selector in rating_selectors:
            rating_elem = soup.select_one(selector)
            if rating_elem:
                text = rating_elem.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)\s*(?:of\s*\d+)?', text)
                if rating_match:
                    try:
                        rating_val = float(rating_match.group(1))
                        # Validate rating - typically 0-5 scale
                        if 0 <= rating_val <= 5:
                            details["rating"] = rating_val
                            break
                    except ValueError:
                        pass
        
        # 10. Extract number of reviews
        reviews_selectors = [
            'a.iUttq',
            'span.jqKwK',
            'a.UctQk',
            'span.DJzgG',
            'span.fzleB',
            'a.CnVXp'
        ]
        for selector in reviews_selectors:
            reviews_elem = soup.select_one(selector)
            if reviews_elem:
                text = reviews_elem.get_text(strip=True)
                reviews_match = re.search(r'([\d,]+)\s*reviews?', text)
                if reviews_match:
                    details["reviews"] = reviews_match.group(1)
                    break
        
        return details
    
    def crawl_attractions(self, max_pages=3, max_attractions=None, threads=4):
        """Crawl attractions from TripAdvisor Hanoi attractions page with multithreading"""
        all_attraction_listings = []
        page = 1
        has_next_page = True
        
        # Get attraction listings from each page
        while page <= max_pages and has_next_page:
            page_listings, has_next_page = self.get_attraction_listings(page=page)
            if not page_listings:
                logger.warning(f"No attraction listings found on page {page}")
                break
                
            all_attraction_listings.extend(page_listings)
            logger.info(f"Collected {len(all_attraction_listings)} attraction listings so far")
            
            if max_attractions and len(all_attraction_listings) >= max_attractions:
                all_attraction_listings = all_attraction_listings[:max_attractions]
                break
                
            page += 1
            self._random_delay()
        
        # Exit early if no attractions were found
        if not all_attraction_listings:
            logger.warning("No attraction listings found on any page. Nothing to process.")
            return []
            
        # Get detailed information for each attraction using ThreadPoolExecutor
        detailed_attractions = []
        processed_urls = set()  # Track URLs we've already processed
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Create a map of future to attraction index
            future_to_index = {}
            futures = []
            
            for i, attraction in enumerate(all_attraction_listings):
                # Check that we have a valid URL
                if not attraction.get('url') or not attraction['url'].startswith('http'):
                    logger.warning(f"Skipping attraction with invalid URL: {attraction.get('url')}")
                    continue
                
                url = attraction['url']
                # Skip duplicates based on URL
                if url in self.visited_urls or url in processed_urls:
                    logger.info(f"Skipping already processed URL: {url}")
                    continue
                
                # Mark URL as being processed
                processed_urls.add(url)
                
                # Submit the task to the executor
                future = executor.submit(self.get_attraction_details, url)
                futures.append(future)
                future_to_index[future] = i
            
            # Process completed futures as they complete
            for future in as_completed(futures):
                try:
                    i = future_to_index[future]
                    attraction = all_attraction_listings[i]
                    details = future.result()
                    
                    # Skip if there was an error getting details
                    if 'error' in details and not details.get('name'):
                        logger.error(f"Error getting details for {attraction.get('url')}: {details.get('error')}")
                        continue
                    
                    # Merge the listing data with the details
                    merged_details = {**attraction, **details}
                    
                    # Ensure we have name from either source
                    if 'name' not in merged_details or not merged_details['name'] or merged_details['name'] == "Unknown Attraction":
                        if 'name' in attraction and attraction['name'] and attraction['name'] != "Unknown Attraction":
                            merged_details['name'] = attraction['name']
                    
                    # Skip duplicate attractions by name (case-insensitive)
                    attraction_name = merged_details.get('name', '').lower()
                    if attraction_name and attraction_name in self.visited_attractions:
                        logger.info(f"Skipping duplicate attraction: {merged_details.get('name')}")
                        continue
                    
                    # Keep thumbnail URL if we couldn't get full size images
                    if 'thumbnail_url' in attraction and ('main_image' not in merged_details or not merged_details.get('main_image')):
                        merged_details['main_image'] = attraction['thumbnail_url']
                        if 'image_urls' not in merged_details:
                            merged_details['image_urls'] = [attraction['thumbnail_url']]
                    
                    # Make sure we have a type
                    if 'type' not in merged_details or not merged_details['type']:
                        if self.custom_type:
                            merged_details['type'] = self.custom_type
                        else:
                            merged_details['type'] = "Attraction"
                    
                    # Add to the list of detailed attractions
                    detailed_attractions.append(merged_details)
                    
                    # Mark as visited
                    if attraction_name:
                        self.visited_attractions.add(attraction_name)
                    self.visited_urls.add(attraction['url'])
                    
                    logger.info(f"Processed attraction {i+1}/{len(all_attraction_listings)}: {merged_details.get('name', 'Unknown')}")
                    
                except Exception as e:
                    logger.error(f"Error processing attraction: {e}")
                    logger.debug(f"Exception details: {str(e)}", exc_info=True)
        
        logger.info(f"Found {len(detailed_attractions)} unique attractions")
        return detailed_attractions
    
    def save_to_json(self, data, filename):
        """Save attraction data to JSON file"""
        if not data:
            logger.warning("No data to save")
            return
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Main function to crawl all Hanoi attractions from the main page"""
    parser = argparse.ArgumentParser(description='TripAdvisor Hanoi Attractions Crawler')
    parser.add_argument('--max-pages', type=int, default=3, help='Maximum number of pages to crawl')
    parser.add_argument('--max-attractions', type=int, default=None, help='Maximum number of attractions to crawl')
    parser.add_argument('--delay', type=float, default=4.0, help='Delay between requests in seconds')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads for parallel processing')
    parser.add_argument('--output', type=str, default='hanoi_attractions.json', help='Output file name')
    parser.add_argument('--download-images', action='store_true', help='Download images locally')
    parser.add_argument('--url', type=str, default=None, help='Optional specific URL to crawl instead of main attractions page')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode to save HTML for inspection')
    parser.add_argument('--custom-type', type=str, default=None, help='Specify a custom type for all attractions (e.g., "Museum", "Temple")')
    
    args = parser.parse_args()
    
    # Initialize the crawler with optional custom type
    crawler = EnhancedAttractionsCrawler(delay=args.delay, custom_type=args.custom_type)
    
    if args.debug:
        # Set up additional logging for debugging
        logger.setLevel(logging.DEBUG)
        print("Debug mode enabled - will save HTML for inspection")
    
    if args.url:
        # If a specific URL is provided, just get details for that attraction
        print(f"Fetching details for {args.url}...")
        details = crawler.get_attraction_details(args.url)
        
        # Print the results in a formatted way
        print("\nResults:")
        print(json.dumps(details, indent=2, ensure_ascii=False))
        
        # Save the results to file
        output_file = f"{details.get('name', 'attraction').replace(' ', '_').lower()}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
        
        print(f"\nData saved to {output_file}")
    else:
        # Crawl all attractions from the main page
        print(f"Crawling up to {args.max_pages} pages of Hanoi attractions...")
        if args.custom_type:
            print(f"Using custom type for all attractions: {args.custom_type}")
        
        try:
            # Only for debugging - save the HTML of the first page
            if args.debug:
                current_url = crawler.base_url
                print(f"Saving HTML of the first page for debugging: {current_url}")
                
                try:
                    response = requests.get(current_url, headers=crawler.headers, timeout=30)
                    response.raise_for_status()
                    
                    with open("debug_first_page.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    
                    print("HTML saved to debug_first_page.html")
                except Exception as e:
                    print(f"Error saving debug HTML: {e}")
            
            # Start the crawling process
            attractions = crawler.crawl_attractions(
                max_pages=args.max_pages,
                max_attractions=args.max_attractions,
                threads=args.threads
            )
            
            if attractions:
                print(f"\nSuccessfully crawled {len(attractions)} unique attractions")
                
                # Save attractions to JSON file
                crawler.save_to_json(attractions, args.output)
                print(f"Data saved to {args.output}")
                
                # Print first 5 attractions for quick verification
                print("\nFirst 5 attractions:")
                for i, attraction in enumerate(attractions[:5]):
                    print(f"{i+1}. {attraction.get('name', 'Unknown')} - {attraction.get('type', 'Unknown Type')}")
                    print(f"   URL: {attraction.get('url', 'No URL')}")
                    if 'image_urls' in attraction:
                        print(f"   Images: {len(attraction.get('image_urls', []))} images found")
                    print()
                
                # Optionally download images
                if args.download_images and attractions:
                    download_dir = "attraction_images"
                    os.makedirs(download_dir, exist_ok=True)
                    
                    print(f"Downloading images to {download_dir}...")
                    for i, attraction in enumerate(attractions):
                        if 'image_urls' in attraction and attraction['image_urls']:
                            attraction_name = re.sub(r'[^\w\s-]', '', attraction.get('name', f'attraction_{i}'))
                            attraction_name = re.sub(r'[\s]+', '_', attraction_name).lower()
                            
                            for j, img_url in enumerate(attraction['image_urls']):
                                try:
                                    img_response = requests.get(img_url, stream=True, timeout=30)
                                    img_response.raise_for_status()
                                    
                                    img_path = os.path.join(download_dir, f"{attraction_name}_{j+1}.jpg")
                                    with open(img_path, 'wb') as img_file:
                                        for chunk in img_response.iter_content(1024):
                                            img_file.write(chunk)
                                    
                                    print(f"Downloaded image {j+1} for {attraction.get('name')}")
                                except Exception as e:
                                    print(f"Error downloading image {img_url}: {e}")
                    
                    print(f"Finished downloading images")
            else:
                print("\nNo attractions found. This could be due to:")
                print("1. TripAdvisor may have changed their website structure")
                print("2. TripAdvisor might be blocking the requests")
                print("3. There might be network issues")
                print("\nTry running with --debug flag for more detailed information")
        
        except Exception as e:
            print(f"\nAn error occurred during crawling: {e}")
            import traceback
            traceback.print_exc()
            print("\nTry running with --debug flag for more detailed information")

if __name__ == "__main__":
    main() 