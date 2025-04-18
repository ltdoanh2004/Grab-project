#!/usr/bin/env python3
"""
TripAdvisor Hanoi Attractions Crawler – **Playwright v1.43 + Stealth**
====================================================================
A fully‑asynchronous headless crawler that renders JavaScript with
Playwright, cloaks itself with *playwright‑stealth* **and** rotates
residential proxies & realistic browser fingerprints to dodge the
TripAdvisor antibot / CAPTCHA wall.

✨  **What’s new in this patch 18‑Apr‑2025**
------------------------------------------------
*   ✅ *No more AttributeErrors* – correct async shutdown, use
    `browser.is_connected()`.
*   ✅ Built‑in **proxy rotation** (HTTP/SOCKS) – pass list via
    `--proxies` or `$TA_PROXIES`.
*   ✅ Automatic **cookie‑consent** click & gentle scrolling to make the
    page load dynamic content.
*   ✅ Retry logic: if CAPTCHA detected → new proxy & context → retry
    up to *N* times before bailing.
*   ✅ Clean project layout, type‑hints everywhere, single entry‑point,
    280 LoC (replaced the legacy 800‑line script).

📦 Requirements
--------------
```bash
pip install playwright playwright‑stealth beautifulsoup4 tqdm python‑dotenv
# one‑time
playwright install chromium
```
If you want to use proxies, create a **.env** or export
`TA_PROXIES="http://user:pass@host1:port, socks5://host2:1080"`.

"""
#!/usr/bin/env python3
"""
TripAdvisor Hanoi Attractions Crawler – **Playwright v1.43 + Stealth**
====================================================================
A fully‑asynchronous headless crawler that renders JavaScript with
Playwright, cloaks itself with *playwright‑stealth* **and** rotates
residential proxies & realistic browser fingerprints to dodge the
TripAdvisor antibot / CAPTCHA wall.

✨  **What’s new in this patch 18‑Apr‑2025**
------------------------------------------------
*   ✅ *No more AttributeErrors* – correct async shutdown, use
    `browser.is_connected()`.
*   ✅ Built‑in **proxy rotation** (HTTP/SOCKS) – pass list via
    `--proxies` or `$TA_PROXIES`.
*   ✅ Automatic **cookie‑consent** click & gentle scrolling to make the
    page load dynamic content.
*   ✅ Retry logic: if CAPTCHA detected → new proxy & context → retry
    up to *N* times before bailing.
*   ✅ Clean project layout, type‑hints everywhere, single entry‑point,
    280 LoC (replaced the legacy 800‑line script).

📦 Requirements
--------------
```bash
pip install playwright playwright‑stealth beautifulsoup4 tqdm python‑dotenv
# one‑time
playwright install chromium
```
If you want to use proxies, create a **.env** or export
`TA_PROXIES="http://user:pass@host1:port, socks5://host2:1080"`.

"""
import os, asyncio, json, re, random, time, logging, argparse
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Dict, Sequence, Optional

from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm_asyncio
from playwright.async_api import (
    async_playwright, Browser, BrowserContext, Page, Error as PWError
)
from playwright_stealth import stealth_async
from dotenv import load_dotenv

load_dotenv()

# ───────────────────────── LOGGING ────────────────────────── #
FMT = "%(asctime)s %(levelname)7s – %(message)s"
logging.basicConfig(level=logging.INFO, format=FMT)
log = logging.getLogger("ta‑crawler")

# ───────────────────────── UTILITIES ───────────────────────── #
CAPTCHA_RE = re.compile(r"captcha|are you a human", re.I)
VALID_NAME_RE = re.compile(r"[^\W\d_]", re.UNICODE)  # at least one unicode letter



def random_delay(min_s: float, max_s: float) -> None:
    time.sleep(random.uniform(min_s, max_s))


def valid_name(txt: str) -> bool:
    if not txt or len(txt) < 3:
        return False
    bad_kw = ("see tickets", "reviews", "review of", "tickets")
    if any(b in txt.lower() for b in bad_kw):
        return False
    return bool(VALID_NAME_RE.search(txt))


# ──────────────────────── CRAWLER CLASS ──────────────────────── #
class TAPlaywrightCrawler:
    BASE_URL = (
        "https://www.tripadvisor.com/Attractions-g293924-Activities-oa0-Hanoi.html"
    )

    def __init__(
        self,
        base_url: str | None = None,
        *,
        delay: float = 2.5,
        proxies: Optional[Sequence[str]] = None,
    ) -> None:
        self.base_url = base_url or self.BASE_URL
        self.delay_min = delay
        self.delay_max = delay * 2
        self.proxies = list(proxies or os.getenv("TA_PROXIES", "").split(","))
        self._proxy_idx = 0

        # runtime
        self._pw = None  # type: ignore
        self.browser: Browser | None = None
        self.ctx: BrowserContext | None = None
        self.page: Page | None = None
        self.visited_urls: set[str] = set()

    # ────────────── Playwright bootstrap / teardown ────────────── #
    async def _new_context(self) -> BrowserContext:
        """Create a fresh incognito context (optionally through next proxy)."""
        proxy_arg: dict | None = None
        if self.proxies:
            proxy_raw = self.proxies[self._proxy_idx % len(self.proxies)].strip()
            self._proxy_idx += 1
            if proxy_raw:
                proxy_arg = {"server": proxy_raw}
                log.debug(f"use proxy → {proxy_raw}")
        return await self.browser.new_context(
            **(proxy_arg or {}),
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{random.randint(120,124)}.0.{random.randint(1000,5000)}.0 "
                "Safari/537.36"
            ),
            viewport={"width": random.randint(1280, 1600), "height": 900},
            locale=random.choice(["en-US", "en-GB", "en"]),
        )

    async def _launch(self) -> None:
        if self.browser:
            return  # already launched
        self._pw = await async_playwright().start()
        self.browser = await self._pw.chromium.launch(headless=True)
        self.ctx = await self._new_context()
        self.page = await self.ctx.new_page()
        await stealth_async(self.page)

    async def _rotate_context(self) -> None:
        """Drop current context/page, open a fresh one (optionally new proxy)."""
        try:
            if self.ctx:
                await self.ctx.close()
        except Exception:
            pass
        self.ctx = await self._new_context()
        self.page = await self.ctx.new_page()
        await stealth_async(self.page)

    async def _shutdown(self) -> None:
        if self.ctx:
            try:
                await self.ctx.close()
            except Exception:
                pass
        if self.browser and self.browser.is_connected():
            try:
                await self.browser.close()
            except Exception:
                pass
        if self._pw:
            await self._pw.stop()

    # ──────────────── Core helpers ──────────────── #
    async def _goto(self, url: str, retries: int = 3) -> str | None:
        for attempt in range(1, retries + 1):
            try:
                assert self.page is not None
                log.info(f"GET {url} (try {attempt})")
                await self.page.goto(url, timeout=30000)
                # accept cookies if banner displayed
                try:
                    await self.page.click("#onetrust-accept-btn-handler", timeout=3000)
                except PWError:
                    pass
                # gentle scroll to trigger lazy‑load
                await self.page.mouse.wheel(0, 1000)
                await self.page.wait_for_timeout(1500)
                html = await self.page.content()
                if CAPTCHA_RE.search(html):
                    raise RuntimeError("captcha page")
                return html
            except Exception as e:
                log.warning(f"{e} – rotating context & retry…")
                await self._rotate_context()
        log.error("✗ too many captcha/timeout – skip url")
        return None

    # ──────────── Listing extraction ──────────── #
    async def _parse_listing(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        items: list[dict] = []
        seen: set[str] = set()
        for a in soup.select('a[href^="/Attraction_Review"]'):
            href = a.get("href")
            name = a.get_text(strip=True)
            if not href or not valid_name(name):
                continue
            if not href.startswith("http"):
                href = urljoin("https://www.tripadvisor.com", href)
            if href in seen:
                continue
            seen.add(href)
            items.append({"name": name, "url": href})
        return items

    async def collect_listings(self, max_pages: int, max_items: int | None) -> list[dict]:
        assert self.page is not None
        url = self.base_url
        page_idx, collected = 1, []
        while page_idx <= max_pages:
            html = await self._goto(url)
            if not html:
                break
            batch = await self._parse_listing(html)
            collected.extend(batch)
            if max_items and len(collected) >= max_items:
                return collected[:max_items]
            # find next‑page link
            soup = BeautifulSoup(html, "html.parser")
            nxt = soup.select_one('a[aria-label*="Next"][href*="oa"]')
            if not nxt:
                break
            href = nxt.get("href")
            url = urljoin("https://www.tripadvisor.com", href)
            page_idx += 1
            random_delay(self.delay_min, self.delay_max)
        return collected

    # ──────────── Detail extraction ──────────── #
    async def _detail(self, item: dict) -> dict | None:
        html = await self._goto(item["url"])
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        out: Dict = {
            "url": item["url"],
            "name": item["name"],
        }
        # title override
        title = soup.select_one('h1')
        if title:
            out["name"] = title.get_text(strip=True)
        # rating
        rat = soup.select_one('[data-automation="bubbleRatingValue"]')
        if rat and (m := re.search(r"(\d+(?:\.\d+)?)", rat.text)):
            out["rating"] = float(m.group(1))
        addr = soup.select_one('span.DsyBj')
        if addr:
            out["address"] = addr.get_text(strip=True)
        hero = soup.select_one('meta[property="og:image"]')
        if hero and hero.has_attr('content'):
            out["image"] = hero['content']
        return out

    # ──────────── Public API ──────────── #
    async def run(self, *, max_pages: int, max_items: int | None, threads: int):
        await self._launch()
        listings = await self.collect_listings(max_pages, max_items)
        log.info(f"listings → {len(listings)}")
        if not listings:
            return []
        results: list[dict] = []
        sem = asyncio.Semaphore(threads)

        async def worker(it: dict):
            async with sem:
                if it["url"] in self.visited_urls:
                    return
                self.visited_urls.add(it["url"])
                det = await self._detail(it)
                if det:
                    results.append(det)
                    log.info("✓ " + det.get("name", "?"))

        await tqdm_asyncio.gather(*[worker(it) for it in listings])
        await self._shutdown()
        return results


# ──────────────────────────── CLI ──────────────────────────── #

def cli() -> None:
    ap = argparse.ArgumentParser(description="TripAdvisor Hanoi crawler (Playwright stealth)")
    ap.add_argument("--max-pages", type=int, default=3)
    ap.add_argument("--max-attractions", type=int)
    ap.add_argument("--delay", type=float, default=2.5, help="base random delay seconds")
    ap.add_argument("--threads", type=int, default=5)
    ap.add_argument("--proxies", help="comma‑separated proxy list, overrides $TA_PROXIES")
    ap.add_argument("--output", default="hanoi_attractions.json")
    args = ap.parse_args()

    proxies = args.proxies.split(",") if args.proxies else None
    crawler = TAPlaywrightCrawler(delay=args.delay, proxies=proxies)
    data = asyncio.run(
        crawler.run(
            max_pages=args.max_pages,
            max_items=args.max_attractions,
            threads=args.threads,
        )
    )
    if data:
        Path(args.output).write_text(json.dumps(data, indent=2, ensure_ascii=False))
        log.info(f"saved → {args.output}")
    else:
        log.warning("no data scraped 😢 – try proxies or fewer pages")


if __name__ == "__main__":
    cli()
