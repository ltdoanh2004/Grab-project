#!/usr/bin/env python3
"""
Enhanced Hanoi TripAdvisor Attractions Crawler
A specialized crawler that extracts clean, structured attraction details from TripAdvisor.

⚠️ 17‑04‑2025 – minimal patches:
   • Không đánh dấu URL là visited ngay ở bước listing  (# PATCH 1)
   • Thêm hàm _valid_name() lọc chuỗi rác                 (# PATCH 2)
   • Thêm selector mới  a[data-automation="poiTitleLink"] (# PATCH 3)
   • Sau khi crawl chi tiết thành công mới add visited    (# PATCH 4)
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
from get_image import crawl_tripadvisor_carousel_images
import asyncio
from datetime import datetime

import nest_asyncio
nest_asyncio.apply()
# --------------------------- LOGGING --------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("attractions_crawler.log")
    ]
)
logger = logging.getLogger(__name__)


class EnhancedAttractionsCrawler:
    """Enhanced crawler for TripAdvisor attractions in Hanoi with better data extraction"""

    # -------------------- INIT -------------------- #
    def __init__(self, base_url=None, delay=3.0, custom_type=None, save_interval=15):
        self.base_url = base_url or "https://www.tripadvisor.com/Attractions-g293924-Activities-oa0-Hanoi.html"
        self.min_delay = delay
        self.max_delay = delay * 2
        self.save_interval = save_interval  # Minutes between saves
        self.last_save_time = time.time()
        self.headers = {
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/123.0.0.0 Safari/537.36'),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.tripadvisor.com/'
        }
        self.visited_urls = set()
        self.visited_attractions = set()
        self.custom_type = custom_type
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _random_delay(self):
        """Add a random delay between requests to avoid being blocked"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.info(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)

    def _should_save(self):
        """Check if it's time to save data"""
        minutes_since_last_save = (time.time() - self.last_save_time) / 60
        return minutes_since_last_save >= self.save_interval

    def save_data(self, data, output_dir, location):
        """Save data to a new file with timestamp and index"""
        if not data:
            logger.warning("No data to save")
            return

        # Create location-specific directory
        location_dir = os.path.join(output_dir, location)
        os.makedirs(location_dir, exist_ok=True)

        # Find the next available index
        index = 0
        while True:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(location_dir, f'attractions_{timestamp}_index_{index}.json')
            if not os.path.exists(filename):
                break
            index += 1

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(data)} attractions to {filename}")
            self.last_save_time = time.time()
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {str(e)}")
            # Create error backup
            error_backup = f"error_backup_{int(time.time())}.json"
            try:
                with open(error_backup, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Created error backup at {error_backup}")
            except Exception as backup_error:
                logger.error(f"Failed to create error backup: {str(backup_error)}")

    def crawl_attractions(self, max_pages=3, max_attractions=None, threads=4, start_page=1, output_dir="data_attractions", location="hanoi"):
        all_listings, page, more = [], start_page, True
        detailed = []
        
        logger.info(f"Starting crawl from page {start_page} with max_pages={max_pages}, max_attractions={max_attractions}")
        
        while more and (page - start_page + 1) <= max_pages:
            logger.info(f"Crawling page {page}")
            lst, more = self.get_attraction_listings(page=page)
            logger.info(f"Found {len(lst)} attractions on page {page}")
            
            all_listings.extend(lst)
            if max_attractions and len(all_listings) >= max_attractions:
                logger.info(f"Reached max_attractions limit ({max_attractions})")
                all_listings = all_listings[:max_attractions]
                break
            page += 1
            self._random_delay()

            # Save periodically
            if self._should_save() and detailed:
                self.save_data(detailed, output_dir, location)

        if not all_listings:
            logger.warning("No attraction listings found.")
            return detailed

        logger.info(f"Starting to crawl details for {len(all_listings)} attractions")
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_map = {executor.submit(self.get_attraction_details, it["url"]): it for it in all_listings}
            for fut in as_completed(future_map):
                it = future_map[fut]
                try:
                    det = fut.result()
                    if "error" in det:
                        logger.warning(f"Error getting details for {it['url']}: {det['error']}")
                        continue
                    if det["url"] in self.visited_urls or det["name"].lower() in self.visited_attractions:
                        logger.info(f"Skipping duplicate: {det['name']}")
                        continue
                    self.visited_urls.add(det["url"])
                    self.visited_attractions.add(det["name"].lower())
                    detailed.append({**it, **det})
                    logger.info(f"✓ {det.get('name')}")
                    
                    # Save periodically
                    if self._should_save():
                        self.save_data(detailed, output_dir, location)
                        
                except Exception as e:
                    logger.error(f"{e} – {it['url']}")

        # Final save
        self.save_data(detailed, output_dir, location)
        logger.info(f"Found {len(detailed)} unique attractions")
        return detailed

    # -------------------- HELPERS -------------------- #
    def extract_images_with_playwright(self, attraction_url):
        try:
            image_urls = asyncio.run(crawl_tripadvisor_carousel_images(attraction_url, num_clicks=20))
            if image_urls:
                return {
                    "main_image": image_urls[0],
                    "image_urls": image_urls[:10]  # Limit to 10
                }
        except Exception as e:
            print(f"❌ Playwright error: {e}")
        return {}

    def get_soup(self, url, retries=3):
        """Get BeautifulSoup object from URL with retries"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching URL: {url}")
                response = self.session.get(url, timeout=30)
                # response = requests.get(url, headers=self.headers, timeout=30)
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

    # -----------  PATCH 2: small utility to filter bad names ----------- #
    def _valid_name(self, txt: str) -> bool:
        if not txt or len(txt) < 3:
            return False
        bad = ["see tickets", "reviews", "review of", "tickets"]
        if any(k in txt.lower() for k in bad):
            return False
        if re.fullmatch(r"[\d\W_]+", txt):
            return False
        return True

    # -------------------- LISTING PAGE -------------------- #
    def get_attraction_listings(self, url=None, page=1):
        current_url = url or self.base_url
        if page > 1:
            if "oa" in current_url:
                current_url = re.sub(r'oa\d+', f'oa{(page-1)*30}', current_url)
            else:
                current_url = current_url.replace('.html', f'-oa{(page-1)*30}.html')

        soup = self.get_soup(current_url)
        if not soup:
            return [], False

        attractions = []
        local_seen = set()             # PATCH 1a: track inside this call only

        selectors = [
            'a[data-automation="poiTitleLink"]',           # PATCH 3
            'div[data-automation="attraction"] a[href^="/Attraction_Review"]',
            'a[href^="/Attraction_Review"]'
        ]

        for sel in selectors:
            for a in soup.select(sel):
                href = a.get('href')
                name = a.get_text(strip=True)
                if not href or not self._valid_name(name):  # PATCH 2
                    continue
                if not href.startswith('http'):
                    href = urljoin("https://www.tripadvisor.com", href)
                if href in local_seen:                      # PATCH 1b
                    continue
                local_seen.add(href)
                # ❌ KHÔNG thêm vào self.visited_urls ở đây nữa  (# PATCH 1c)
                attractions.append({"name": name, "url": href})

        logger.info(f"Found {len(attractions)} attractions on page {page}")
        has_next_page = bool(soup.select_one('a[href*="oa"][aria-label*="Next"]'))
        return attractions, has_next_page

    # -------------------- DETAILS PAGE (unchanged) -------------------- #
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
    
    



    
    def _extract_clean_duration(self, soup: BeautifulSoup):
        """Extract cleaned duration text from a BeautifulSoup soup."""
        duration = None

        # ✅ 1. Duyệt theo các selector cố định
        duration_selectors = [
            'svg[aria-label="Duration"] + div',
            '[data-automation="WebPresentation_PoiDetailsTags"] span',  # TripAdvisor tags
            'div.eYKGZ',
        ]

        for selector in duration_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True).lower()
                if "duration" in text or "hour" in text or "min" in text:
                    # Ưu tiên trích xuất chuỗi như "1–2 hours", "30 minutes"
                    match = re.search(r'(\d+-\d+|\d+)\s*(hours?|minutes?|mins?)', text)
                    if match:
                        duration = match.group(0).strip()
                        return duration
                    else:
                        # fallback nếu chứa từ khóa
                        duration = text
                        return duration

        # ✅ 2. Duyệt toàn bộ DOM để tìm "duration" hợp lệ
        if not duration:
            pattern = re.compile(r'(\d+-\d+\s*hours?|\d+\s*hours?|\d+-\d+\s*min|\d+\s*min)', re.IGNORECASE)
            for div in soup.find_all('div'):
                text = div.get_text(strip=True)
                if len(text) < 100 and ('hour' in text.lower() or 'min' in text.lower()):
                    match = pattern.search(text)
                    if match:
                        duration = match.group(1).strip()
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
        print(opening_hours)
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
            'div.ITQHd img',
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
        
        # Replace old image extraction logic with:
        image_data = self.extract_images_with_playwright(attraction_url)
        if image_data:
            details.update(image_data)

        # Get gallery images
        gallery_selectors = [
            'div[data-testid="carousel-with-strip"] img',
            'div[data-testid="media-strip"] img',
            'div.PKDJv img',
            'div.AKIQt img',
            'button.BUTbe img',
            'picture.NhVvC img',
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
            '[data-automation="bubbleRatingValue"]', 
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
            '[data-automation="bubbleReviewCount"]', 
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

# ----------------------------- CLI ----------------------------- #
def main():
    parser = argparse.ArgumentParser(description='TripAdvisor Attractions Crawler')
    parser.add_argument('--url', type=str, required=True,
                      help='URL to crawl')
    parser.add_argument('--max-pages', type=int, default=3,
                      help='Maximum number of pages to crawl')
    parser.add_argument('--start-page', type=int, default=1,
                      help='Page number to start crawling from')
    parser.add_argument('--max-attractions', type=int,
                      help='Maximum number of attractions to crawl')
    parser.add_argument('--delay', type=float, default=4.0,
                      help='Delay between requests in seconds')
    parser.add_argument('--threads', type=int, default=4,
                      help='Number of concurrent threads')
    parser.add_argument('--custom-type',
                      help='Custom type to assign to all attractions')
    parser.add_argument('--output-dir', default='data_attractions',
                      help='Output directory for JSON files')
    parser.add_argument('--location', default='hanoi',
                      help='Location name for organizing files')
    parser.add_argument('--save-interval', type=int, default=15,
                      help='Minutes between periodic saves (default: 15)')
    args = parser.parse_args()

    crawler = EnhancedAttractionsCrawler(
        base_url=args.url,
        delay=args.delay,
        custom_type=args.custom_type,
        save_interval=args.save_interval
    )
    
    crawler.crawl_attractions(
        max_pages=args.max_pages,
        start_page=args.start_page,
        max_attractions=args.max_attractions,
        threads=args.threads,
        output_dir=args.output_dir,
        location=args.location
    )

if __name__ == "__main__":
    main() 