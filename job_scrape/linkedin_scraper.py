    # async def create_browser_context(self, playwright) -> tuple[Browser, BrowserContext]:
    #     """Create browser + context with proxy and UA"""
    #     browser_type = playwright.chromium
    #     launch_options = {
    #         "headless": self.config.HEADLESS,
    #         "slow_mo": 500,  # 🐢 <— add this line for slow motion
    #         "args": [
    #             "--no-sandbox",
    #             "--disable-blink-features=AutomationControlled",
    #             "--disable-dev-shm-usage",
    #             "--disable-extensions",
    #             "--no-first-run",
    #             "--disable-default-apps",
    #             "--disable-features=TranslateUI",
    #             "--disable-ipc-flooding-protection",
    #         ],
    #     }
    #     proxy = self.get_next_proxy()
    #     if proxy:
    #         launch_options["proxy"] = {"server": proxy}

    #     browser = await browser_type.launch(**launch_options)
    #     context = await browser.new_context(
    #         user_agent=self.get_random_user_agent(),
    #         viewport={
    #             "width": self.config.VIEWPORT_WIDTH,
    #             "height": self.config.VIEWPORT_HEIGHT,
    #         },
    #         locale="en-US",
    #         timezone_id="America/New_York",
    #     )

    #     # Anti-detection script
    #     await context.add_init_script(
    #         """
    #         Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    #         Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    #         Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    #         """
    #     )
    #     return browser, context

"""
LinkedIn Job Scraper
- Excludes reposted jobs
- Scrapes job descriptions
- Uses Playwright async API, proxy rotation, and human-like behavior
"""
import asyncio
import random
import json
from datetime import datetime, timedelta, timezone
import shutil
import time
from typing import List, Dict, Optional
# import pandas as pd
from playwright.async_api import async_playwright, BrowserContext, Page
from fake_useragent import UserAgent
from config import Config
from scraper_helpers import ScraperHelpers
import os
from playwright.async_api import TimeoutError as PWTimeout



class LinkedInJobScraper:
    def __init__(self):
        self.config = Config()
        self.helpers = ScraperHelpers(self.config)
        self.jobs_data = []

    # ------------------------- Utility helpers -------------------------
    async def scroll_visually_down(self, page: Page, selector: str, duration: float = 6.0, step: int = 220):
        print(f"🖱️ Moving mouse to first job card and scrolling {selector} down slowly...")
        await page.wait_for_selector(selector, timeout=20000)

        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < duration:
            await page.evaluate(f"document.querySelector('{selector}').scrollBy(0, {step})")
            await self.helpers.human_like_delay(0.3, 0.5)
        print("✅ Finished visual scroll.")


    # ------------------------- Core scraping logic -------------------------

    async def extract_job_data(self, page: Page, max_pages: int = 1) -> List[Dict]:
        """Extract job cards (title, company, location, description) from LinkedIn job search results (up to max_pages)."""
        jobs = []
        page_number = 1

        try:
            while page_number <= max_pages:
                print(f"\n📄 Scraping page {page_number}...")

                # 🔄 Scroll job list to ensure all lazy-loaded jobs appear
                await self.scroll_visually_down(page, selector=".semantic-search-results-list")

                # 🧭 Wait for visible job cards
                await page.wait_for_selector(
                    ".job-card-job-posting-card-wrapper, div[data-job-id], li[data-job-id]",
                    state="attached",
                    timeout=20000
                )

                job_elements = await page.query_selector_all(
                    ".job-card-job-posting-card-wrapper, div[data-job-id], li[data-job-id]"
                )
                print(f"✅ Found {len(job_elements)} job cards on page {page_number}")

                # 🧩 Extract job data from each card
                for job_element in job_elements:
                    try:
                        title_el = await job_element.query_selector(
                            '.artdeco-entity-lockup__title strong, .job-card-list__title, h3'
                        )
                        company_el = await job_element.query_selector(
                            '.artdeco-entity-lockup__subtitle div[dir="ltr"], .job-card-container__company-name, .job-card-list__company-name'
                        )
                        location_el = await job_element.query_selector(
                            '.artdeco-entity-lockup__caption div[dir="ltr"], .job-card-container__metadata-item, .job-card-list__location'
                        )
                        link_el = await job_element.query_selector(
                            "a[href*='/jobs/view/'], a[href*='/jobs/search-results/?currentJobId=']"
                        )

                        title = await title_el.inner_text() if title_el else "N/A"
                        company = await company_el.inner_text() if company_el else "N/A"

                        # continue if company is within a blacklist company list
                        if company in self.config.BLACKLIST_COMPANIES:
                            print(f"⏩ Skipping job: {title.strip()} - Company in blacklist")
                            continue

                        # continue if title contains any of the title keywords blacklist
                        if any(keyword in title for keyword in self.config.TITLE_KEYWORDS_BLACKLIST):
                            print(f"⏩ Skipping job: {title.strip()} - Title contains keyword in blacklist")
                            continue
                        
                        location = await location_el.inner_text() if location_el else "N/A"

                        # define what is GTA cities
                        GTA_CITIES = ['Toronto', 'Markham', 'Richmond Hill', 'Mississauga', 'Brampton', 'Vaughan', 'Oakville', 'Burlington', 'Hamilton', 'Oshawa', 'Pickering', 'Ajax', 'Whitchurch-Stouffville', 'Whitby', 'North York','Greater Toronto Area', 'Remote', 'GTA', 'Caledon', 'NewMarket', 'King', 'Uxbridge', 'Aurora', 'Scugog', 'East York']

                        # check across all the cities in GTA, ontario, canada. If the location doesn't include any of the GTA cities, skip
                        if not any(city in location for city in GTA_CITIES):
                            print(f"⏩ Skipping job: {title.strip()} - Location not in GTA")
                            continue

                        await link_el.get_attribute("href")

                        # Click job card (to load right panel)
                        await link_el.click()
                        print(f"🖱️ Clicked job: {title.strip()} — waiting for description...")
                        await page.wait_for_selector(
                            ".jobs-box__html-content, .show-more-less-html__markup",
                            timeout=20000
                        )
                        await self.helpers.human_like_delay(1, 2)

                        # Skip reposted jobs
                        repost_el = await page.query_selector('span:has-text("Reposted")')
                        if repost_el:
                            print(f"⏩ Skipping reposted job: {title.strip()}")
                            continue

                        # Skip closed jobs
                        closed_el = await page.query_selector('span.artdeco-inline-feedback__message:has-text("No longer accepting applications")')
                        if closed_el:
                            print(f"⏩ Skipping closed job: {title.strip()}")
                            continue

                        ifEasyApply = await page.query_selector('span.artdeco-button__text:has-text("Easy Apply")')
                        
                        # Extract description
                        desc_el = await page.query_selector(
                            ".jobs-box__html-content, .show-more-less-html__markup"
                        )
                        description = await desc_el.inner_text() if desc_el else ""

                        # Check if description has French words
                        if self.helpers.has_french_words(description):
                            print(f"⏩ Skipping job: {title.strip()} - French job description")
                            continue

                        # get the href of the job link
                        job_url = "https://www.linkedin.com" + await page.get_attribute(".job-details-jobs-unified-top-card__job-title h1 a", "href")
                        job_id = self.helpers.extract_job_id(job_url)
                        # Extract posted date
                        date_el = await page.query_selector(
                            ".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--positive strong span"
                        )
                        posted_date = await date_el.inner_text() if date_el else "N/A"
                        if posted_date == "N/A":
                            continue
                        easy_apply = True if ifEasyApply else False

                        gmt_minus_4 = timezone(timedelta(hours=-4))

                        # Save job data
                        job_data = {
                            "title": title.strip(),
                            "company": company.strip(),
                            "location": location.strip(),
                            "job_id": job_id,
                            "url": job_url,
                            "description": description.strip(),
                            "easy_apply": easy_apply,
                            "posted_date": posted_date.strip(),
                            # use gmt-4 timezone
                            "scraped_at": datetime.now(gmt_minus_4).isoformat(),
                        }
                        jobs.append(job_data)
                        print(f"✅ Scraped: {title[:60]} | {company}")
                        await self.helpers.human_like_delay(1, 2)

                    except Exception as e:
                        print(f"⚠️ Error extracting job card: {e}")
                        continue

                # 🔁 Pagination (stop if no Next or reached page limit)
                if page_number >= max_pages:
                    print(f"⏹️ Reached max page limit ({max_pages}). Stopping pagination.")
                    break

                next_button = await page.query_selector(
                    'button[aria-label="View next page"]'
                )
                if next_button:
                    is_disabled = await next_button.get_attribute("disabled")
                    if is_disabled:
                        print("⏹️ No more pages found.")
                        break

                    print("➡️ Clicking 'Next' for more results...")
                    await next_button.click()
                    page_number += 1
                    await self.helpers.human_like_delay(3, 5)

                    # Wait for job list refresh
                    await page.wait_for_selector(
                        ".job-card-job-posting-card-wrapper, div[data-job-id], li[data-job-id]",
                        timeout=20000
                    )
                else:
                    print("⏹️ No Next button detected.")
                    break

        except Exception as e:
            print(f"⚠️ Error parsing frame: {e}")

        return jobs

    LIST = ".scaffold-layout__list.jobs-semantic-search-list"
    IFRAME = 'iframe[data-testid="interop-iframe"]'

    async def get_results_surface(self,page):
        """Return (surface, LIST) where surface is either the page or the iframe's content_frame()."""
        # 1) Try iframe variant fast
        try:
            iframe_el = await page.wait_for_selector(self.IFRAME, timeout=5_000)  # pyright: ignore[reportUndefinedVariable]
            frame = await iframe_el.content_frame()
            await frame.wait_for_selector(self.LIST, state="attached", timeout=15_000)  # pyright: ignore[reportUndefinedVariable]
            return frame, ".scaffold-layout__list.jobs-semantic-search-list"
        except PWTimeout:  # pyright: ignore[reportUndefinedVariable]
            pass

        # 2) Fallback to top-level DOM variant
        await page.wait_for_selector(self.LIST, state="attached", timeout=30_000)  # pyright: ignore[reportUndefinedVariable]
        return page, self.LIST

    async def search_jobs(self, page: Page, context: BrowserContext, keyword: str, location: str = "", max_pages: int = 1) -> List[Dict]:
        """Search by keyword/location and paginate, including clicking 'Past 24 hours' filter."""
        all_jobs = []
        try:
            # --- Navigate to jobs homepage ---
            await page.goto("https://www.linkedin.com/jobs/", wait_until="domcontentloaded")
            await self.helpers.human_like_delay()
            await self.helpers.simulate_human_behavior(page)

            # --- Perform search ---
            search_input = await page.wait_for_selector('input[placeholder*="Describe the job"], input[aria-label*="Search jobs"]')
            await search_input.fill(keyword)
            await search_input.press("Enter")
            await self.helpers.human_like_delay(3, 5)

            # --- Wait for job search results container ---
            
            # await page.wait_for_selector(".scaffold-layout__list.jobs-semantic-search-list", state="attached", timeout=20000)
            surface, list_selector = await self.get_results_surface(page)
            print("✅ Found job search results container")

            # --- Click "Date Posted" filter and select "Past 24 hours" ---
            try:
                # Click the "Date posted" dropdown
                await surface.wait_for_selector('#searchFilter_timePostedRange', state="attached", timeout=30000)
                await surface.click('#searchFilter_timePostedRange')
                await self.helpers.human_like_delay(1, 2)

                # Select "Past 24 hours"
                await surface.wait_for_selector('label[for="timePostedRange-r86400"]', timeout=30000)
                await surface.click('label[for="timePostedRange-r86400"]')
                print("✅ Selected 'Past 24 hours' filter successfully")
                await self.helpers.human_like_delay(1, 2)

                # Click "Show results" to apply the filter
                await surface.wait_for_selector('button[aria-label*="Apply current filter"], button:has-text("Show results")', timeout=30000)
                await surface.click('button[aria-label*="Apply current filter"], button:has-text("Show results")')
                print("✅ Clicked 'Show results' to apply the filter")
                await self.helpers.human_like_delay(3, 5)
            except Exception as e:
                print(f"⚠️ Could not apply 'Past 24 hours' filter: {e}")

            # --- Extract job data from main DOM ---
            page_jobs = await self.extract_job_data(surface, max_pages)
            all_jobs.extend(page_jobs)

        except Exception as e:
            print(f"⚠️ Error searching jobs: {e}")

        return all_jobs


    # ------------------------- Runner and output -------------------------

    async def run_scraper(self):
        async with async_playwright() as playwright:
            context = await self.helpers.create_browser_context(playwright)
            try:
                page = await context.new_page()

                await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
                if "login" in page.url.lower():
                    print("🔐 Not logged in — performing login...")
                    if self.config.LINKEDIN_EMAIL and self.config.LINKEDIN_PASSWORD:
                        await self.login(page)
                else:
                    print("✅ Already logged in — skipping login")
                #now KEYWWORDS IS A DICT
                for keyword, max_pages in self.config.KEYWORDS.items():
                    for location in self.config.LOCATIONS:
                        print(f"\n🔍 Searching: {keyword} in {location}")
                        jobs = await self.search_jobs(page, context, keyword, location, max_pages)
                        self.jobs_data.extend(jobs)
                        await self.helpers.human_like_delay(5, 10)

                # Deduplicate within scraped jobs first
                self.jobs_data = self._deduplicate_current_session()
                
                await self.save_results()

            finally:
                await context.close()

    def _deduplicate_current_session(self) -> List[Dict]:
        """Deduplicate jobs within the current scraping session by job_id"""
        seen = set()
        unique_jobs = []
        for job in self.jobs_data:
            if job["job_id"] not in seen:
                seen.add(job["job_id"])
                unique_jobs.append(job)
        print(f"🔄 Deduplicated: {len(self.jobs_data)} -> {len(unique_jobs)} jobs (removed {len(self.jobs_data) - len(unique_jobs)} duplicates)")
        return unique_jobs

    def _get_yesterday_file_path(self) -> Optional[str]:
        """Get the path to yesterday's batch file if it exists"""
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_date_str = yesterday.strftime('%Y%m%d')
        
        linkedin_jobs_dir = 'linkedin_jobs'
        if not os.path.exists(linkedin_jobs_dir):
            return None
        
        # Find all files from yesterday
        yesterday_files = [
            f for f in os.listdir(linkedin_jobs_dir)
            if f.endswith('.json') and f.startswith(f'linkedin_jobs_batch_{yesterday_date_str}')
        ]
        
        if yesterday_files:
            # Return the most recent file from yesterday (if multiple exist)
            yesterday_files.sort(reverse=True)
            return os.path.join(linkedin_jobs_dir, yesterday_files[0])
        return None

    async def login(self, page: Page):
        try:
            await page.goto("https://www.linkedin.com/login")
            await self.helpers.human_like_delay(2, 4)
            await (await page.wait_for_selector("#username")).fill(self.config.LINKEDIN_EMAIL)
            await (await page.wait_for_selector("#password")).fill(self.config.LINKEDIN_PASSWORD)
            await page.click('button[type="submit"]')
            await self.helpers.human_like_delay(3, 5)
            print("✅ Logged in successfully")
        except Exception as e:
            print(f"⚠️ Login failed: {e}")

    async def save_results(self):
        if not self.jobs_data:
            print("No jobs found to save.")
            return
        
        seen = set()
        unique_jobs = []
        
        # Check against yesterday's file if it exists
        yesterday_file = self._get_yesterday_file_path()
        if yesterday_file:
            print(f"📂 Checking against yesterday's file: {yesterday_file}")
            try:
                with open(yesterday_file, 'r', encoding='utf-8') as f:
                    yesterday_jobs = json.load(f)
                    for job in yesterday_jobs:
                        seen.add(job["job_id"])
                print(f"   Found {len(seen)} job IDs from yesterday's file")
            except Exception as e:
                print(f"⚠️ Error reading yesterday's file: {e}")
        else:
            print("📂 No file from yesterday found, skipping duplicate check")
        
        # Filter out jobs that already exist in yesterday's file
        for job in self.jobs_data:
            if job["job_id"] not in seen:
                seen.add(job["job_id"])
                unique_jobs.append(job)
        
        print(f"\n💾 Saving {len(unique_jobs)} unique jobs (filtered {len(self.jobs_data) - len(unique_jobs)} duplicates from yesterday)")
        
        if self.config.OUTPUT_FORMAT.lower() == "csv":
            pd.DataFrame(unique_jobs).to_csv(self.config.OUTPUT_FILE, index=False)
        else:
            # file name is linkedin_jobs_batch_timestamp.json under a folder called linkedin_jobs
            os.makedirs('linkedin_jobs', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'linkedin_jobs/linkedin_jobs_batch_{timestamp}.json'
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(unique_jobs, f, ensure_ascii=False, indent=2)
        print("✅ Results saved successfully.")
        #copy the file to the job_fit_analysis folder
        shutil.copy(filename, '../job_fit_analysis/linkedin_jobs.json')

async def main():
    scraper = LinkedInJobScraper()
    await scraper.run_scraper()


if __name__ == "__main__":
    asyncio.run(main())

