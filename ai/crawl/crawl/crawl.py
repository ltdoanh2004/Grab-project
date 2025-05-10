import nest_asyncio
import asyncio
import re
from playwright.async_api import async_playwright

nest_asyncio.apply()

# Constants
BASE_URL = "https://pasgo.vn"
TIMEOUT = 8000

async def extract_price_range(page):
    """Extract price range from restaurant page"""
    info_span = await page.query_selector("span.pasgo-giatrungbinh")
    if not info_span:
        return {"price_range": ""}

    full_text = await info_span.inner_text()
    match = re.search(r"(\d{1,3}(?:\.\d{3})*)\s*-\s*(\d{1,3}(?:\.\d{3})*)", full_text)
    price_range = f"{match.group(1)} - {match.group(2)} đ/người" if match else ""
    return {"price_range": price_range}

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
            
    return result

async def crawl_pasgo_by_page(category_slug, city, max_pages=5):
    """Crawl restaurant data from Pasgo website"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        all_results = []

        for page_num in range(1, max_pages + 1):
            url = f"{BASE_URL}/{city}/nha-hang{category_slug}?page={page_num}"
            print(f"🔎 Crawling page {page_num}: {url}")
            
            try:
                await page.goto(url)
                await page.wait_for_selector("div.wapitem a", timeout=TIMEOUT)
            except:
                print(f"⛔ No data found on page {page_num}")
                continue

            for item in await page.query_selector_all("div.wapitem"):
                result = {}
                main = await item.query_selector("div.waptop-main")
                desc = await item.query_selector("div.waptop-desc")
                
                # Get detail page data
                link = await (await item.query_selector("a.waptop")).get_attribute("href")
                full_link = f"{BASE_URL}{link}" if link.startswith("/") else link
                detail_page = await browser.new_page()
                result.update(await get_detail_data(detail_page, full_link))
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
                    "city": slug_to_name(city)
                })
                
                all_results.append(result)

        await browser.close()
        return all_results

if __name__ == "__main__":
    categories = ["","/lau-27", "/buffet-29", "/hai-san-28", "/lau-and-nuong-91", 
                 "/quan-nhau-165", "/mon-chay-44", "/dat-tiec-224", "/han-quoc-16", 
                 "/nhat-ban-15", "/mon-au-23", "/mon-viet-21", "/mon-thai-18", 
                 "/mon-trung-hoa-126", "/tiec-cuoi-143"]
                 
    cities = ["ha-noi", "ho-chi-minh", "hai-phong", "da-nang", "khanh-hoa", 
             "can-tho", "vung-tau", "bac-giang", "bac-ninh", "binh-duong", 
             "binh-dinh", "binh-thuan", "hung-yen", "kien-giang", "lam-dong", 
             "nghe-an", "quang-nam", "quang-ninh", "thanh-hoa", "thua-thien-hue"]

    for city in cities:
        for cat in categories:
            asyncio.run(crawl_pasgo_by_page(cat, city, max_pages=5))
