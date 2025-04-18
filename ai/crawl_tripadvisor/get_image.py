import nest_asyncio
nest_asyncio.apply()
# 6. Extract images - IMPROVED IMPLEMENTATION using Playwright
async def crawl_tripadvisor_carousel_images(url, num_clicks=10):
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup
    import re
    from urllib.parse import urljoin

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Debug bằng browser thật
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)

        # Scroll để hiện carousel
        await page.evaluate("window.scrollBy(0, 1000)")
        await page.wait_for_timeout(2000)

        # Click mũi tên phải nhiều lần
        for i in range(num_clicks):
            try:
                next_btn = page.locator('button.pWJww')
                if await next_btn.is_visible():
                    await next_btn.click()
                    await page.wait_for_timeout(800)
                else:
                    print(f"[{i}] Không thấy nút next.")
            except Exception as e:
                print(f"[{i}] ❌ Không bấm được: {e}")
                break

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        image_urls = set()

        # ✅ Quét tất cả div chứa ảnh: ZGLUM là container
        for container in soup.select("div.ZGLUM"):
            for img in container.select("img"):
                src = img.get("src") or img.get("data-src") or ""
                if not src:
                    continue
                src = re.sub(r"-s\\d+x\\d+", "-s1600x1200", src).split("?")[0]
                if not src.startswith("http"):
                    src = urljoin("https://www.tripadvisor.com", src)
                if "icons" in src.lower():
                    continue
                image_urls.add(src)

            # ✅ Nếu có thẻ <source> (ảnh responsive)
            for source in container.select("source"):
                srcset = source.get("srcset", "")
                for part in srcset.split(","):
                    candidate = part.strip().split(" ")[0]
                    candidate = re.sub(r"-s\\d+x\\d+", "-s1600x1200", candidate).split("?")[0]
                    if candidate.startswith("http"):
                        image_urls.add(candidate)

        await browser.close()
        return list(image_urls)
