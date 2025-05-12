import nest_asyncio
import asyncio
import re
import logging
import csv
import os
import argparse
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError

nest_asyncio.apply()

# Constants
BASE_URL = "https://pasgo.vn"
TIMEOUT = 30000  # Increased from 8000 to 30000 (30 seconds)
NAVIGATION_TIMEOUT = 60000  # 60 seconds for page navigation
SELECTOR_TIMEOUT = 30000  # 30 seconds for waiting selectors
RETRY_COUNT = 3  # Number of retries for failed requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def save_to_csv(data, filename):
    """Save data to CSV file"""
    if not data:
        logger.warning(f"No data to save to {filename}")
        return

    # Ensure directory exists
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    
    # Get all possible fields from all records
    fieldnames = set()
    for record in data:
        fieldnames.update(record.keys())
    fieldnames = sorted(list(fieldnames))

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Successfully saved {len(data)} records to {filepath}")
    except Exception as e:
        logger.error(f"Error saving to CSV: {str(e)}")

async def extract_price_range(page):
    """Extract price range from restaurant page"""
    try:
        info_span = await page.query_selector("span.pasgo-giatrungbinh")
        if not info_span:
            return {"price_range": ""}

        full_text = await info_span.inner_text()
        match = re.search(r"(\d{1,3}(?:\.\d{3})*)\s*-\s*(\d{1,3}(?:\.\d{3})*)", full_text)
        price_range = f"{match.group(1)} - {match.group(2)} đ/người" if match else ""
        return {"price_range": price_range}
    except Exception as e:
        logger.error(f"Error extracting price range: {str(e)}")
        return {"price_range": ""}
async def extract_detail_info(article):
    ps = await article.query_selector_all("p")
    detail_texts = []
    for p in ps:
        text = await p.inner_text()
        detail_texts.append(text.strip())

    full_text = "\n\n".join(detail_texts)  # cách dòng cho dễ đọc
    return {"reviews": full_text}

def slug_to_name(slug):
    """Convert URL slug to readable name"""
    return " ".join(slug.split("-"))

async def extract_summary(article):
    """Extract restaurant summary information"""
    result = {"description": "", "cuisines": ""}
    
    for title in await article.query_selector_all(".txt-title"):
        title_text = (await title.inner_text()).strip().replace(":", "").upper()
        
        if "MÓN ĐẶC SẮC" in title_text:
            span = await article.query_selector("span")
            result['cuisines'] = (await span.inner_text()).strip() if span else ""
            
        elif "ĐIỂM ĐẶC TRƯNG" in title_text:
            ps_texts = []
            sibling = await title.evaluate_handle("el => el.nextElementSibling")
            while sibling:
                if await sibling.evaluate("el => el === null"):
                    break
                    
                tag_name = await sibling.evaluate("el => el.tagName")
                if tag_name == "DIV" and await sibling.get_attribute("class") == "txt-title":
                    break
                    
                if tag_name == "P":
                    ps_texts.append((await sibling.inner_text()).strip())
                sibling = await sibling.evaluate_handle("el => el.nextElementSibling")
                
            result['description'] += "\n".join(ps_texts)
            
        else:
            sibling = await title.evaluate_handle("el => el.nextElementSibling")
            if sibling and not await sibling.evaluate("el => el === null"):
                tag_name = await sibling.evaluate("el => el.tagName")
                if tag_name in ["DIV", "P"] and (tag_name == "P" or await sibling.get_attribute("class") == "text-description"):
                    result['description'] += (await sibling.inner_text()).strip()

    return result

async def extract_image_gallery(article):
    """Extract all image URLs from article"""
    image_urls = []
    for image in await article.query_selector_all("img"):
        src = await image.get_attribute("src")
        if src:
            if src.startswith("/"):
                src = f"{BASE_URL}{src}"
            image_urls.append(src)
    return image_urls

async def get_detail_data(page, detail_link):
    """Get detailed restaurant information"""
    await page.goto(detail_link)
    await page.wait_for_load_state("domcontentloaded")

    result = {"photo_url": []}
    for article in await page.query_selector_all("article"):
        article_id = await article.get_attribute("id")
        
        if article_id == "NH-TOMTAT":
            result.update(await extract_summary(article))
        elif article_id == "info-booth":
            result.update(await extract_price_range(article))
        elif article_id == "NH-ANH":
            result['photo_url'].extend(await extract_image_gallery(article))
        elif article_id == "NH-CHITIET":
            result.update(await extract_detail_info(article))
    return result

async def crawl_pasgo_by_page(category_slug, city, max_pages=5):
    """Crawl restaurant data from Pasgo website"""
    logger.info(f"Starting crawl for city: {city}, category: {category_slug}")
    start_time = datetime.now()
    stats = {"total_restaurants": 0, "successful": 0, "failed": 0}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        all_results = []

        for page_num in range(1, max_pages + 1):
            url = f"{BASE_URL}/{city}/nha-hang{category_slug}?page={page_num}"
            logger.info(f"🔎 Crawling page {page_num}: {url}")
            
            for retry in range(RETRY_COUNT):
                try:
                    await page.goto(url, timeout=NAVIGATION_TIMEOUT)
                    await page.wait_for_selector("div.wapitem a", timeout=SELECTOR_TIMEOUT)
                    break
                except TimeoutError as e:
                    if retry == RETRY_COUNT - 1:
                        logger.error(f"⛔ Timeout after {RETRY_COUNT} retries on page {page_num}: {str(e)}")
                        continue
                    logger.warning(f"Retry {retry + 1}/{RETRY_COUNT} for page {page_num}")
                    await asyncio.sleep(2)  # Wait before retry
                except Exception as e:
                    logger.error(f"⛔ Error on page {page_num}: {str(e)}")
                    break

            items = await page.query_selector_all("div.wapitem")
            logger.info(f"Found {len(items)} restaurants on page {page_num}")
            stats["total_restaurants"] += len(items)

            for item in items:
                try:
                    result = {}
                    main = await item.query_selector("div.waptop-main")
                    desc = await item.query_selector("div.waptop-desc")
                    
                    # Get detail page data
                    link = await (await item.query_selector("a.waptop")).get_attribute("href")
                    full_link = f"{BASE_URL}{link}" if link.startswith("/") else link
                    detail_page = await context.new_page()
                    
                    # Add retry logic for detail page
                    for retry in range(RETRY_COUNT):
                        try:
                            await detail_page.goto(full_link, timeout=NAVIGATION_TIMEOUT)
                            await detail_page.wait_for_load_state("domcontentloaded", timeout=SELECTOR_TIMEOUT)
                            result.update(await get_detail_data(detail_page, full_link))
                            break
                        except TimeoutError as e:
                            if retry == RETRY_COUNT - 1:
                                logger.error(f"Timeout loading detail page after {RETRY_COUNT} retries: {full_link}")
                                break
                            logger.warning(f"Retry {retry + 1}/{RETRY_COUNT} for detail page: {full_link}")
                            await asyncio.sleep(2)
                    
                    await detail_page.close()

                    # Extract basic info
                    img = await main.query_selector("a.waptop img")
                    img_url = await img.get_attribute("src") if img else None
                    result['photo_url'].append(img_url)
                    
                    name = await main.query_selector("div.wapfooter h3")
                    address = await main.query_selector("p")
                    
                    result.update({
                        "img_url": img_url,
                        "name": (await name.inner_text()).strip() if name else "No name",
                        "address": (await address.inner_text()).strip() if address else "No address",
                        "link": full_link,
                        "city": slug_to_name(city),
                        "category": category_slug.replace("/", ""),
                        "crawl_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    all_results.append(result)
                    stats["successful"] += 1
                    logger.debug(f"Successfully crawled restaurant: {result['name']}")
                    
                except Exception as e:
                    stats["failed"] += 1
                    logger.error(f"Error processing restaurant: {str(e)}")

        await context.close()
        await browser.close()
        
        # Save results to CSV
        if all_results:
            filename = f"pasgo_{city}_{category_slug.replace('/', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            save_to_csv(all_results, filename)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"""
Crawl completed for {city} - {category_slug}:
- Duration: {duration:.2f} seconds
- Total restaurants found: {stats['total_restaurants']}
- Successfully crawled: {stats['successful']}
- Failed: {stats['failed']}
""")
        
        return all_results

async def crawl_city(city, categories, max_pages=5):
    """Crawl all categories for a specific city"""
    all_city_results = []
    for cat in categories:
        results = await crawl_pasgo_by_page(cat, city, max_pages)
        all_city_results.extend(results)
    return all_city_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl Pasgo restaurant data')
    parser.add_argument('--city', type=str, help='City to crawl (e.g., ha-noi)')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum number of pages to crawl per category')
    args = parser.parse_args()

    categories = ["","/lau-27", "/buffet-29", "/hai-san-28", "/lau-and-nuong-91", 
                 "/quan-nhau-165", "/mon-chay-44", "/dat-tiec-224", "/han-quoc-16", 
                 "/nhat-ban-15", "/mon-au-23", "/mon-viet-21", "/mon-thai-18", 
                 "/mon-trung-hoa-126", "/tiec-cuoi-143"]
                 
    cities = ["ha-noi", "ho-chi-minh", "hai-phong", "da-nang", "khanh-hoa", 
             "can-tho", "vung-tau", "bac-giang", "bac-ninh", "binh-duong", 
             "binh-dinh", "binh-thuan", "hung-yen", "kien-giang", "lam-dong", 
             "nghe-an", "quang-nam", "quang-ninh", "thanh-hoa", "thua-thien-hue"]

    if args.city:
        if args.city not in cities:
            logger.error(f"Invalid city: {args.city}")
            exit(1)
        logger.info(f"Running crawler for city: {args.city}")
        asyncio.run(crawl_city(args.city, categories, args.max_pages))
    else:
        logger.info("Running crawler for all cities")
        for city in cities:
            asyncio.run(crawl_city(city, categories, args.max_pages))
