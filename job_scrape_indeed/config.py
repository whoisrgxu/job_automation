"""
Configuration for Indeed job scraper.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_URL = os.getenv("INDEED_BASE_URL", "https://ca.indeed.com")

    # Keywords mapped to max pages (10 results per page on Indeed by default)
    KEYWORDS = {
        "junior software developer": 2,
        "python developer": 2,
        "full stack developer": 2,
    }

    LOCATIONS = [
        "Toronto, ON",
        "Mississauga, ON",
    ]

    # Time window: 1 => past 24 hours, 3 => past 3 days, etc.
    TIME_RANGE_DAYS = int(os.getenv("INDEED_TIME_RANGE_DAYS", "1"))

    MAX_RESULTS_PER_KEYWORD = int(os.getenv("INDEED_MAX_RESULTS_PER_KEYWORD", "50"))
    DELAY_BETWEEN_ACTIONS = (1.5, 3.5)
    DELAY_BETWEEN_PAGES = (3, 6)
    DELAY_BETWEEN_REQUESTS = DELAY_BETWEEN_ACTIONS

    BLACKLIST_COMPANIES = [
        "Adecco",
        "Randstad",
        "Affirm",
        "Dawn InfoTek"
    ]

    TITLE_KEYWORDS_BLACKLIST = [
        "senior",
        "principal",
        "manager",
    ]

    OUTPUT_FORMAT = "json"
    OUTPUT_DIR = "indeed_jobs"
    OUTPUT_FILE = "indeed_jobs.json"

    HEADLESS = False
    USE_RANDOM_USER_AGENTS = True
    USE_PROXIES = False
    PROXY_LIST = []
    TIME_LIMIT = TIME_RANGE_DAYS * 24

