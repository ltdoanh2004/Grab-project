#!/usr/bin/env python3
"""
Hanoi TripAdvisor Attractions Crawler - Fixed Version
A specialized crawler that extracts attraction details from TripAdvisor.
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

class ImprovedAttractionsCrawler:
    """Fixed crawler for TripAdvisor attractions in Hanoi"""
    
    def __init__(self, delay=3.0):
        self.min_delay = delay
        self.max_delay = delay * 2  # Randomize delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.tripadvisor.com/'
        }
        
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
    
    def get_attraction_details(self, attraction_url):
        """Get detailed information about an attraction"""
        soup = self.get_soup(attraction_url)
        if not soup:
            return {"url": attraction_url, "error": "Failed to fetch attraction page"}
            
        # Initialize the attraction details
        details = {
            "url": attraction_url,
            "type": "Attraction"
        }
        
        # 1. Extract name
        name_selectors = [
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
                details["name"] = name_elem.get_text(strip=True)
                break
        
        # 2. Extract address
        address_selectors = [
            'div[data-test-target="attraction-detail-card"] button.UikbF',
            'button.KEaY',
            'div.kUaGX button',
            'div.XPUSn span.yEWoV',
            'div.FUHHI span',
            'div.CEQvT button',
            'button[data-automation="searchFilters_filterGroup_address"]',
            'div.NXSyd',
            'a[href*="maps"]',
            'address',
            'div.euDRl',
            'div[data-automation="WebPresentation_POIInfoSection"] div.euDRl'
        ]
        for selector in address_selectors:
            address_elem = soup.select_one(selector)
            if address_elem:
                address_text = address_elem.get_text(strip=True)
                if address_text and len(address_text) > 5:  # Ensure it's a meaningful address
                    details["address"] = address_text
                    break
        
        # If address not found, try directly accessing the structured text
        if 'address' not in details:
            address_area = soup.find(string=re.compile('The area', re.IGNORECASE))
            if address_area:
                parent = address_area.parent
                if parent:
                    next_sibling = parent.next_sibling
                    if next_sibling:
                        address_text = next_sibling.get_text(strip=True)
                        details["address"] = address_text
        
        # Try looking for location within a section
        if 'address' not in details:
            location_sections = soup.find_all(['div', 'section'], string=lambda t: t and 'location' in t.lower())
            for section in location_sections:
                # Look for nearby content that might contain the address
                address_text = section.get_text(strip=True)
                if address_text and len(address_text) > 10:
                    details["address"] = address_text
                    break
        
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
        
        # 4. Extract opening hours
        hours_selectors = [
            'div.eRsNA',
            'div[data-automation="WebPresentation_POIOpeningHoursSection"]',
            'div.MWPpe',
            'div.wgNTK',
            'button.iGCTW',
            'div.QvzAT',
            'div[data-section-id="HoursSection"]'
        ]
        for selector in hours_selectors:
            hours_elem = soup.select_one(selector)
            if hours_elem:
                hours_text = hours_elem.get_text(strip=True)
                if hours_text and ('open' in hours_text.lower() or 'hour' in hours_text.lower() or 'am' in hours_text.lower() or 'pm' in hours_text.lower()):
                    details["opening_hours"] = hours_text.replace('Closed now', 'Currently closed')
                    break
        
        # Try looking for time directly
        if 'opening_hours' not in details:
            time_patterns = soup.find_all(string=re.compile(r'\d{1,2}:\d{2}\s*[AP]M\s*-\s*\d{1,2}:\d{2}\s*[AP]M'))
            if time_patterns:
                details["opening_hours"] = time_patterns[0].strip()
        
        # 5. Extract "Duration" information
        duration_selectors = [
            'div[data-section-id="DetailSection"] div:contains("Duration")',
            'div.NXSyd span:contains("Duration")',
            'div:contains("Duration")',
            'svg[aria-label="Duration"]'
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
                        duration_match = re.search(r'duration[:\s]*([^,;]+)', duration_text, re.IGNORECASE)
                        if duration_match:
                            details["duration"] = duration_match.group(1).strip()
                        else:
                            details["duration"] = duration_text
                        break
            else:
                duration_elem = soup.select_one(selector)
                if duration_elem:
                    parent_elem = duration_elem.parent
                    duration_text = parent_elem.get_text(strip=True) if parent_elem else duration_elem.get_text(strip=True)
                    if 'hour' in duration_text.lower():
                        details["duration"] = duration_text
                        break
        
        # 6. Extract images
        image_urls = []
        
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
        
        # Add images to details
        if image_urls:
            details["image_urls"] = image_urls
            details["main_image"] = image_urls[0]  # Main image
        
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
            'div.AfQtZ',
            'div.eLXel',
            'div.EWtzU span.uwJeR',
            'span.bvcyz',
            'div.WAllg div.grdwI span',
            'div.fiohW div.biGQs',
            'span.UctUV',
            'div.biGQs > span',
            'span[data-automation="WebPresentation_AttractionRating"]',
            'div[data-automation="WebPresentation_AttractionRating"]',
            'div.fjdOS'
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
        
        # 9. Extract type/category
        type_selectors = [
            'div.aSJLV a',
            'div.EEIGK a',
            'div.CskSA a',
            'div.xkSty a',
            'div.IKxsX a',
            'div.dyezQ a'
        ]
        types = []
        for selector in type_selectors:
            type_elems = soup.select(selector)
            for elem in type_elems:
                type_text = elem.get_text(strip=True)
                if type_text and len(type_text) > 1 and type_text.lower() not in ['hanoi', 'vietnam', 'asia']:
                    types.append(type_text)
        
        if types:
            details["types"] = ", ".join(types)
        
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

def main():
    """Main function to test the crawler with La Spa Hang Be URL"""
    crawler = ImprovedAttractionsCrawler(delay=4.0)
    url = "https://www.tripadvisor.com/Attraction_Review-g293924-d17707099-Reviews-La_Spa_Hang_Be-Hanoi.html"
    
    print(f"Fetching details for La Spa Hang Be...")
    details = crawler.get_attraction_details(url)
    
    # Print the results in a formatted way
    print("\nResults:")
    print(json.dumps(details, indent=2, ensure_ascii=False))
    
    # Save the results to file
    with open("la_spa_hang_be.json", "w", encoding="utf-8") as f:
        json.dump(details, f, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to la_spa_hang_be.json")

if __name__ == "__main__":
    main() 