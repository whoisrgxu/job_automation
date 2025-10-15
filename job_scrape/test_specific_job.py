#!/usr/bin/env python3
"""
Test script for scraping a specific LinkedIn job page
Usage: python test_specific_job.py <job_url>
"""
import asyncio
import sys
import json
from linkedin_scraper import LinkedInJobScraper
from playwright.async_api import async_playwright

async def test_job_url(job_url: str):
    """Test scraping a specific job URL"""
    scraper = LinkedInJobScraper()
    
    async with async_playwright() as playwright:
        context = await scraper.helpers.create_browser_context(playwright)
        page = await context.new_page()
        
        try:
            # Test the specific job page
            job_data = await scraper.test_specific_job_page(page, job_url)
            
            if job_data:
                print("\n" + "="*60)
                print("📋 JOB DATA EXTRACTED:")
                print("="*60)
                print(json.dumps(job_data, indent=2))
                
                # Save to file
                output_file = "test_job_output.json"
                with open(output_file, "w") as f:
                    json.dump(job_data, f, indent=2)
                print(f"\n💾 Saved to: {output_file}")
            else:
                print("❌ Failed to extract job data")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await context.close()

async def main():
    if len(sys.argv) != 2:
        print("Usage: python test_specific_job.py <job_url>")
        print("Example: python test_specific_job.py 'https://www.linkedin.com/jobs/view/1234567890/'")
        sys.exit(1)
    
    job_url = sys.argv[1]
    await test_job_url(job_url)

if __name__ == "__main__":
    asyncio.run(main())
