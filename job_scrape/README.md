# LinkedIn Job Scraper

A sophisticated LinkedIn job scraper built with Playwright that simulates human behavior and uses proxy rotation to avoid detection and IP bans.

## Features

- 🔍 **Keyword-based job search** with customizable keywords and locations
- ⏰ **Time-based filtering** (e.g., jobs posted within last 24 hours)
- 🤖 **Human-like behavior simulation** with random delays and mouse movements
- 🔄 **Proxy rotation** to prevent IP bans
- 🛡️ **Anti-detection measures** including user agent rotation and stealth scripts
- 📊 **Multiple output formats** (CSV, JSON)
- ⚙️ **Highly configurable** through config file

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables (optional):**
   ```bash
   cp env_example.txt .env
   # Edit .env with your LinkedIn credentials and proxy settings
   ```

## Configuration

Edit `config.py` to customize your scraping behavior:

### Search Parameters
```python
KEYWORDS = [
    'python developer',
    'software engineer',
    'data scientist'
]

LOCATIONS = [
    'United States',
    'Remote',
    'New York, NY'
]

TIME_LIMIT = 24  # hours
```

### Scraping Behavior
```python
MAX_PAGES = 10  # pages to scrape per keyword
DELAY_BETWEEN_REQUESTS = (2, 5)  # random delay in seconds
DELAY_BETWEEN_PAGES = (5, 10)
```

### Proxy Configuration
```python
USE_PROXIES = True
PROXY_LIST = [
    'http://proxy1:port',
    'http://username:password@proxy2:port'
]
```

## Usage

### Basic Usage
```bash
python run_scraper.py
```

### Advanced Usage
```python
from linkedin_scraper import LinkedInJobScraper
import asyncio

async def custom_scrape():
    scraper = LinkedInJobScraper()
    await scraper.run_scraper()

asyncio.run(custom_scrape())
```

## Output

The scraper saves results in your chosen format (default: CSV) with the following fields:
- `title`: Job title
- `company`: Company name
- `location`: Job location
- `url`: LinkedIn job URL
- `posted_date`: When the job was posted
- `scraped_at`: When the job was scraped

## Anti-Detection Features

1. **Human-like behavior simulation:**
   - Random mouse movements
   - Variable scrolling patterns
   - Random delays between actions

2. **Browser fingerprint masking:**
   - Random user agent rotation
   - Disabled automation indicators
   - Custom viewport settings

3. **Proxy rotation:**
   - Automatic proxy switching
   - Support for authenticated proxies

4. **Rate limiting:**
   - Configurable delays between requests
   - Session cooldown periods

## Important Notes

⚠️ **Legal and Ethical Considerations:**
- Respect LinkedIn's Terms of Service
- Use reasonable scraping rates
- Consider reaching out to LinkedIn for official API access
- Be mindful of rate limits to avoid IP bans

⚠️ **Proxy Requirements:**
- Use high-quality residential or datacenter proxies
- Rotate proxies regularly
- Test proxy functionality before scraping

⚠️ **LinkedIn Login:**
- Login is optional but may provide access to more jobs
- Use strong passwords and consider 2FA
- Monitor for any account restrictions

## Troubleshooting

### Common Issues

1. **"Playwright not found" error:**
   ```bash
   playwright install chromium
   ```

2. **Proxy connection errors:**
   - Verify proxy credentials and URLs
   - Test proxies independently
   - Consider using different proxy providers

3. **LinkedIn blocking requests:**
   - Increase delays between requests
   - Use more proxies
   - Consider using residential proxies

4. **Empty results:**
   - Check if LinkedIn's structure has changed
   - Verify keyword and location settings
   - Ensure time filter is not too restrictive

### Performance Tips

- Use headless mode for faster scraping (`HEADLESS = True`)
- Reduce `MAX_PAGES` for quicker results
- Use fewer keywords/locations for focused searches
- Monitor system resources during large scraping sessions

## License

This project is for educational purposes only. Please ensure compliance with LinkedIn's Terms of Service and applicable laws in your jurisdiction.
