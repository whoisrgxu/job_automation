"""
Indeed Job Scraper

- Navigates Indeed search results
- Extracts job metadata and descriptions
- Filters by blacklist and optional heuristics
- Stores results under job_scrape_indeed/indeed_jobs/
"""
import asyncio
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs, quote_plus

from playwright.async_api import BrowserContext, Page, async_playwright, TimeoutError as PWTimeout

from job_scrape.scraper_helpers import ScraperHelpers
from job_scrape_indeed.config import Config


class IndeedJobScraper:
    def __init__(self) -> None:
        self.config = Config()
        self.helpers = ScraperHelpers(self.config)
        self.jobs_data: List[Dict] = []
        self.project_root = Path(__file__).resolve().parent
        self.output_dir = self.project_root / self.config.OUTPUT_DIR

    # ------------------------- Utility methods -------------------------

    def build_search_url(self, keyword: str, location: str, start: int = 0) -> str:
        params = {
            "q": keyword,
            "l": location,
            "fromage": str(self.config.TIME_RANGE_DAYS),
            "start": str(start),
        }
        query = "&".join(f"{k}={quote_plus(v)}" for k, v in params.items())
        return f"{self.config.BASE_URL}/jobs?{query}"

    @staticmethod
    def extract_job_id(job_url: str) -> Optional[str]:
        parsed = urlparse(job_url)
        qs = parse_qs(parsed.query)
        for key in ("jk", "vjk"):
            if key in qs and qs[key]:
                return qs[key][0]
        # fallback: last segment
        return parsed.path.split("/")[-1] or None

    async def fetch_job_description(self, context: BrowserContext, job_url: str) -> str:
        detail_page = await context.new_page()
        try:
            await detail_page.goto(job_url, wait_until="domcontentloaded", timeout=30_000)
            await self.helpers.human_like_delay(*self.config.DELAY_BETWEEN_ACTIONS)
            description_el = await detail_page.query_selector("#jobDescriptionText, .jobsearch-jobDescriptionText")
            if description_el:
                return (await description_el.inner_text()).strip()
        except PWTimeout:
            print(f"⚠️ Timeout fetching description for {job_url}")
        except Exception as exc:
            print(f"⚠️ Error fetching description for {job_url}: {exc}")
        finally:
            await detail_page.close()
        return ""

    async def extract_job_cards(
        self,
        context: BrowserContext,
        page: Page,
        keyword: str,
        location: str,
        max_results: int,
    ) -> List[Dict]:
        collected: List[Dict] = []
        start = 0
        results_per_page = 15  # Indeed typically shows 15 results per page

        while start < max_results:
            search_url = self.build_search_url(keyword, location, start=start)
            print(f"🔍 Visiting search URL: {search_url}")
            await page.goto(search_url, wait_until="domcontentloaded")
            await self.helpers.human_like_delay(*self.config.DELAY_BETWEEN_PAGES)

            # Wait for job cards to load
            try:
                await page.wait_for_selector("ul.jobsearch-ResultsList, .job_seen_beacon", timeout=20_000)
            except PWTimeout:
                print("⚠️ No results container found – moving to next keyword.")
                break

            job_cards = await page.query_selector_all(".job_seen_beacon")
            if not job_cards:
                print("⚠️ No job cards found on this page.")
                break

            for card in job_cards:
                if len(collected) >= max_results:
                    break

                try:
                    title_el = await card.query_selector("h2.jobTitle span")
                    company_el = await card.query_selector(".companyName")
                    location_el = await card.query_selector(".companyLocation")
                    easy_apply_el = await card.query_selector("span:has-text('Easily apply')")
                    link_el = await card.query_selector("a")

                    title = (await title_el.inner_text()).strip() if title_el else "N/A"
                    company = (await company_el.inner_text()).strip() if company_el else "N/A"
                    location_text = (await location_el.inner_text()).strip() if location_el else "N/A"

                    if company in self.config.BLACKLIST_COMPANIES:
                        print(f"⏩ Skipping {title} at {company} – company blacklist")
                        continue

                    if any(keyword.lower() in title.lower() for keyword in self.config.TITLE_KEYWORDS_BLACKLIST):
                        print(f"⏩ Skipping {title} – title blacklist")
                        continue

                    if not link_el:
                        continue

                    partial_href = await link_el.get_attribute("href")
                    if not partial_href:
                        continue

                    job_url = urljoin(self.config.BASE_URL, partial_href)
                    job_id = self.extract_job_id(job_url)
                    if not job_id:
                        print(f"⚠️ Could not determine job ID for {job_url}, skipping.")
                        continue

                    description = await self.fetch_job_description(context, job_url)
                    if not description:
                        print(f"⚠️ Empty description for {job_url}, skipping.")
                        continue

                    if self.helpers.has_french_words(description):
                        print(f"⏩ Skipping {title} – French description detected.")
                        continue

                    job_data = {
                        "title": title,
                        "company": company,
                        "location": location_text,
                        "job_id": job_id,
                        "url": job_url,
                        "description": description,
                        "easy_apply": bool(easy_apply_el),
                        "posted_date": datetime.now(timezone.utc).isoformat(),
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    }

                    collected.append(job_data)
                    print(f"✅ Scraped: {title} | {company}")
                    await self.helpers.human_like_delay(*self.config.DELAY_BETWEEN_ACTIONS)
                except Exception as exc:
                    print(f"⚠️ Failed to process job card: {exc}")
                    continue

            if len(job_cards) < results_per_page:
                # no more pages
                break
            start += results_per_page

        return collected

    # ------------------------- Workflow methods -------------------------

    async def search_jobs(
        self,
        context: BrowserContext,
        keyword: str,
        location: str,
        max_pages: int,
    ) -> List[Dict]:
        max_results = max_pages * 15
        page = await context.new_page()
        try:
            return await self.extract_job_cards(context, page, keyword, location, max_results)
        finally:
            await page.close()

    async def run_scraper(self) -> None:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self.config.HEADLESS)
            context = await browser.new_context()

            try:
                for keyword, max_pages in self.config.KEYWORDS.items():
                    for location in self.config.LOCATIONS:
                        print("=" * 80)
                        print(f"🔍 Searching: {keyword} | {location}")
                        jobs = await self.search_jobs(context, keyword, location, max_pages)
                        self.jobs_data.extend(jobs)
                        await self.helpers.human_like_delay(*self.config.DELAY_BETWEEN_PAGES)
            finally:
                await context.close()
                await browser.close()

        await self.save_results()

    # ------------------------- Persistence -------------------------

    async def save_results(self) -> None:
        if not self.jobs_data:
            print("⚠️ No jobs scraped; nothing to save.")
            return

        unique = {}
        for job in self.jobs_data:
            unique[job["job_id"]] = job

        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"indeed_jobs_batch_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(list(unique.values()), f, ensure_ascii=False, indent=2)

        print(f"✅ Saved {len(unique)} unique jobs to {filename}")

        # Copy the latest batch to job_fit_analysis for downstream processing
        analysis_target = self.project_root.parent / "job_fit_analysis" / "indeed_jobs.json"
        with open(analysis_target, "w", encoding="utf-8") as f:
            json.dump(list(unique.values()), f, ensure_ascii=False, indent=2)
        print(f"📁 Copied results to {analysis_target}")


async def main():
    scraper = IndeedJobScraper()
    await scraper.run_scraper()


if __name__ == "__main__":
    asyncio.run(main())

