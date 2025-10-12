#!/usr/bin/env python3
"""
Test script to verify LinkedIn login works
"""
import asyncio
from playwright.async_api import async_playwright
from config import Config

async def test_login():
    """Test LinkedIn login"""
    config = Config()
    
    print(f"Testing login with email: {config.LINKEDIN_EMAIL}")
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Go to LinkedIn login
            await page.goto('https://www.linkedin.com/login')
            await page.wait_for_selector('#username')
            
            # Fill credentials
            await page.fill('#username', config.LINKEDIN_EMAIL)
            await page.fill('#password', config.LINKEDIN_PASSWORD)
            
            # Click login
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)
            
            # Check if we're redirected to feed or jobs
            current_url = page.url
            print(f"Current URL after login: {current_url}")
            
            if 'feed' in current_url or 'jobs' in current_url:
                print("✅ Login successful!")
            else:
                print("❌ Login may have failed - check manually")
                
        except Exception as e:
            print(f"❌ Login test failed: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login())
