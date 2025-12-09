"""
LinkedIn Scraper Helper Utilities
Contains utility methods for browser automation, human-like behavior, and data processing
"""
import asyncio
import random
import os
import re
from datetime import datetime, timedelta
from typing import Optional
from playwright.async_api import BrowserContext, Page
from fake_useragent import UserAgent
from config import Config


class ScraperHelpers:
    """Helper class containing utility methods for LinkedIn scraping"""
    
    def __init__(self, config: Config):
        self.config = config
        self.ua = UserAgent()
        self.current_proxy_index = 0

    def get_random_user_agent(self) -> str:
        """Get a random user agent string"""
        return self.ua.random if self.config.USE_RANDOM_USER_AGENTS else self.ua.chrome

    def get_next_proxy(self) -> Optional[str]:
        """Get the next proxy from the proxy list (with rotation)"""
        if not self.config.USE_PROXIES or not self.config.PROXY_LIST:
            return None
        if self.current_proxy_index >= len(self.config.PROXY_LIST):
            self.current_proxy_index = 0
        proxy = self.config.PROXY_LIST[self.current_proxy_index]
        self.current_proxy_index += 1
        return proxy

    async def human_like_delay(self, min_delay: float = None, max_delay: float = None):
        """Add human-like delay between actions"""
        if min_delay is None:
            min_delay, max_delay = self.config.DELAY_BETWEEN_REQUESTS
        await asyncio.sleep(random.uniform(min_delay, max_delay))

    async def simulate_human_behavior(self, page: Page):
        """Simulate human-like mouse movements and scrolling"""
        viewport = page.viewport_size
        for _ in range(random.randint(2, 5)):
            x = random.randint(0, viewport["width"])
            y = random.randint(0, viewport["height"])
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))
        await page.evaluate(f"window.scrollBy(0, {random.randint(200,800)})")
        await asyncio.sleep(random.uniform(1, 3))

    async def create_browser_context(self, playwright) -> BrowserContext:
        """Create persistent browser context (reuses cookies & device)"""
        user_data_dir = os.path.expanduser("~/linkedin_playwright_profile")

        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=self.config.HEADLESS,
            slow_mo=500,
            channel="chrome",
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--no-first-run",
                "--disable-default-apps",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
            ],
        )
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """)
        return context

    def is_within_time_limit(self, job_date_str: str) -> bool:
        """Check if a job posting is within the specified time limit"""
        try:
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
                try:
                    job_date = datetime.strptime(job_date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                return False
            time_limit = datetime.now() - timedelta(hours=self.config.TIME_LIMIT)
            return job_date >= time_limit
        except Exception:
            return False
        
    def requires_5_or_more_years(self, description: str) -> bool:
        desc = description.lower()

        years = []

        # Case 1: expressions with YOE / yrs — safe to assume experience
        matches1 = re.findall(
            r"\b(\d+)\s*\+?\s*(?:yoe|yrs?|yr|year of experience|years of experience)\b",
            desc
        )
        years += [int(n) for n in matches1]

        # Case 2: numbers + years + "experience"/"exp"
        matches2 = re.findall(
            r"\b(\d+)\s*\+?\s*years?\s*(?:of\s*)?(?:experience|exp)\b",
            desc
        )
        years += [int(n) for n in matches2]

        # Case 3: natural language - "at least 5 years experience"
        matches3 = re.findall(
            r"(?:at\s+least|minimum\s+of)\s+(\d+)\s*years?\s*(?:of\s*)?(?:experience|exp)",
            desc
        )
        years += [int(n) for n in matches3]

        # Case 4: "5 or more years experience"
        matches4 = re.findall(
            r"(\d+)\s*(?:or\s+more)\s*years?\s*(?:of\s*)?(?:experience|exp)",
            desc
        )
        years += [int(n) for n in matches4]

        # Case 5: "over 5 years experience"
        matches5 = re.findall(
            r"over\s+(\d+)\s*years?\s*(?:of\s*)?(?:experience|exp)",
            desc
        )
        years += [int(n) for n in matches5]

        return any(y >= 5 for y in years)

    def extract_job_id(self, url: str) -> str:
        """Extract job ID from LinkedIn job URL"""
        return url.split("/")[-2]

    def has_french_words(self, text: str) -> bool:
        """Check if text contains at least 2 common French words"""
        if not text:
            return False
        
        # Just 4 very common French words
        french_words = ['nous', 'pour', 'avec', 'dans']
        
        text_lower = text.lower()
        
        # Count how many of these French words appear
        count = 0
        for word in french_words:
            if word in text_lower:
                count += 1
        
        # If 2 or more of these words appear, likely French
        return count >= 2
