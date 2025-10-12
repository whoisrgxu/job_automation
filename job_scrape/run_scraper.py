#!/usr/bin/env python3
"""
Simple runner script for LinkedIn job scraper
"""
import asyncio
import sys
from linkedin_scraper import LinkedInJobScraper


async def main():
    """Run the scraper with error handling"""
    try:
        print("Starting LinkedIn Job Scraper...")
        print("=" * 50)
        
        scraper = LinkedInJobScraper()
        await scraper.run_scraper()
        
        print("=" * 50)
        print("Scraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
