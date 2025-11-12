"""
Configuration file for LinkedIn job scraper
"""
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LinkedIn credentials (optional - can scrape without login for public jobs)
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')
    
    # Search parameters with keywords and pages needed
    KEYWORDS = {
        'developer not senior': 2,
        'Node.js developer not senior': 2,
        'typescript developer not senior': 2,
        'JavaScript developer not senior': 2,
        'react developer not senior': 2,
        # 'python developer not senior': 2,
        'software engineer not senior': 2,
        'next.js developer not senior': 2,
        'AWS developer not senior': 1,
        'engineer in test': 1,
    }

    # title keywords blacklist
    TITLE_KEYWORDS_BLACKLIST = [
        'Data Engineer',  
        'Data Science',
        'Machine Learning',
    ]
    # Blacklist companies
    BLACKLIST_COMPANIES = [
        'Jerry',
        'wanderlog',
        'Lumenalta',
        'Dawn InfoTeck',
        'J&M Group'
    ]
    # Location filters
    LOCATIONS = [
        'Ontario, Canada',
    ]
    
    # Time filters (in hours)
    TIME_LIMIT = 24  # jobs posted within last 24 hours
    
    # Scraping behavior
    MAX_PAGES = 10  # maximum pages to scrape per keyword
    DELAY_BETWEEN_REQUESTS = (2, 5)  # random delay range in seconds
    DELAY_BETWEEN_PAGES = (5, 10)  # delay between page loads
    
    # Proxy configuration
    USE_PROXIES = False
    PROXY_LIST = [
        # Add your proxy servers here
        # Format: 'http://username:password@ip:port' or 'http://ip:port'
    ]
    
    # User agents rotation
    USE_RANDOM_USER_AGENTS = True
    
    # Output settings
    OUTPUT_FORMAT = 'json'  # csv, json, excel
    OUTPUT_FILE = 'linkedin_jobs.json'
    
    # Browser settings
    HEADLESS = False  # Set to True for production
    VIEWPORT_WIDTH = 1920
    VIEWPORT_HEIGHT = 1080
    
    # Rate limiting
    MAX_JOBS_PER_SESSION = 100  # max jobs to scrape per session
    SESSION_COOLDOWN = 300  # 5 minutes between sessions
