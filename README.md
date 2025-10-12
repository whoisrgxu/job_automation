# 🤖 Job Automation System

An intelligent job application automation system that scrapes LinkedIn jobs, analyzes job-resume fit using AI, and automatically customizes resumes and cover letters for each application.

## 🚀 Features

- **LinkedIn Job Scraping**: Automated scraping of job listings with filtering
- **AI-Powered Job Analysis**: Uses Gemini 2.0 Flash to analyze job-resume fit
- **Resume Customization**: Automatically tailors resume sections for each job
- **Cover Letter Generation**: Creates personalized cover letters using LLM
- **Application Tracking**: Logs all applications to prevent duplicates
- **Sequential Processing**: Processes jobs one by one for optimal results

## 📁 Project Structure

```
Job Automation/
├── main.py                          # Main orchestrator script
├── job_scrape/                      # LinkedIn job scraping module
│   ├── linkedin_scraper.py         # Core scraper implementation
│   ├── run_scraper.py              # Scraper entry point
│   ├── config.py                   # Scraper configuration
│   └── linkedin_jobs/              # Scraped job data
├── job_fit_analysis/               # AI job analysis module
│   ├── job_fit_analyzer.py         # Gemini-based analyzer
│   ├── good_score_jobs.json        # Filtered high-fit jobs
│   └── resume.txt                  # Your resume for analysis
├── LLMClients/                     # LLM integration layer
│   └── clients.py                  # OpenAI/Gemini client wrapper
├── job_description_cleaner/        # Job description processing
│   └── jd_cleaning.py              # LLM-based JD cleaning
├── test.py                         # Resume customization & application
├── coverletter_customizer.py       # Cover letter generation
├── customize_resume_sections_tex.py # Advanced resume customization
└── .env                            # Environment variables (ignored)
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- LinkedIn account (optional, for authenticated scraping)
- OpenAI API key
- Google Gemini API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "Job Automation"
   ```

2. **Create virtual environments**
   ```bash
   # Main project
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Job scraper
   cd job_scrape
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd ..

   # Job fit analysis
   cd job_fit_analysis
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd ..
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file in project root
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here

   # Create .env in job_scrape/ (optional for LinkedIn login)
   LINKEDIN_EMAIL=your_email@example.com
   LINKEDIN_PASSWORD=your_password

   # Create .env in job_fit_analysis/
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Update file paths** in `main.py`, `test.py`, and other scripts to match your system:
   ```python
   # Update these paths to your resume directory
   self.job_description_path = "/path/to/your/resume/folder/job_description.txt"
   ```

## 🎯 Usage

### Quick Start - Full Automation

Run the complete workflow with one command:

```bash
python main.py
```

This will:
1. Scrape LinkedIn jobs
2. Analyze job-resume fit
3. Process each high-scoring job
4. Customize resume and cover letter
5. Track applications

### Individual Components

#### 1. Job Scraping
```bash
cd job_scrape
source venv/bin/activate
python run_scraper.py
```

#### 2. Job Fit Analysis
```bash
cd job_fit_analysis
source venv/bin/activate
python job_fit_analyzer.py
```

#### 3. Resume Customization
```bash
python test.py "Company Name" "Position Title" "fullstack" "false"
```

## ⚙️ Configuration

### Search Parameters (job_scrape/config.py)

```python
KEYWORDS = [
    'react developer not senior',
    'next.js developer not senior',
]

LOCATIONS = [
    'Ontario, Canada',
]

TIME_FILTERS = [24]  # Last 24 hours
```

### Job Analysis Threshold (job_fit_analysis/job_fit_analyzer.py)

```python
MIN_SCORE = 50  # Minimum job fit score (0-100)
```

## 🔧 Customization

### Adding New Job Search Terms

Edit `job_scrape/config.py`:
```python
KEYWORDS = [
    'your new search term',
    'another search term',
]
```

### Modifying Resume Sections

Edit `customize_resume_sections_tex.py` to customize how resume sections are tailored:
```python
SECTION_RULES = {
    "SUMMARY": """
    Your custom rules for summary section
    """,
    "SKILLS": """
    Your custom rules for skills section
    """,
}
```

### Custom Cover Letter Prompts

Modify `coverletter_customizer.py` to change cover letter generation:
```python
# Customize the prompt in the script
prompt = f"""
Your custom cover letter prompt here...
"""
```

## 📊 Output Files

- `job_scrape/linkedin_jobs/` - Raw scraped job data
- `job_fit_analysis/good_score_jobs.json` - High-fit jobs only
- `job_fit_analysis/linkedin_jobs.json` - Processed job data
- Application logs in your resume tracking Excel file

## 🔒 Security

- All sensitive data (API keys, credentials) stored in `.env` files
- `.env` files are git-ignored and never committed
- Use environment variables for all API keys and passwords

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure you're using the correct virtual environment
   - Install requirements: `pip install -r requirements.txt`

2. **LinkedIn scraping fails**
   - Check if LinkedIn has changed their page structure
   - Try running without login (public jobs only)
   - Verify proxy settings if using proxies

3. **API rate limits**
   - Reduce batch sizes in configuration
   - Add delays between requests
   - Check API quota limits

4. **File path errors**
   - Update hardcoded paths in scripts to match your system
   - Ensure resume files exist at specified locations

### Debug Mode

Enable debug logging by modifying the scraper configuration:
```python
# In job_scrape/config.py
DEBUG = True
```

## 📈 Performance Tips

- Run scraping during off-peak hours
- Use smaller batch sizes for stability
- Monitor API usage and costs
- Keep resume files organized for faster processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for personal use. Please respect LinkedIn's terms of service and rate limits.

## ⚠️ Disclaimer

- Use responsibly and within LinkedIn's terms of service
- Monitor API usage to avoid unexpected costs
- Test thoroughly before running large batches
- Keep your credentials secure

## 🔗 Related Files

- [Job Scraper README](job_scrape/README.md)
- [Job Fit Analysis Setup](job_fit_analysis/SETUP_INSTRUCTIONS.md)

---

**Happy job hunting! 🎯**
