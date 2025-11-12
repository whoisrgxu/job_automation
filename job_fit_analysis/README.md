# Job Fit Analysis System

This system uses Google's Gemini 2.0 Flash model to analyze job matches against your resume and filter for positions with good fit scores (>= 50).

## Setup

1. **Install dependencies (with the shared root venv activated):**
   ```bash
   cd ..
   source venv/bin/activate
   pip install -r job_fit_analysis/requirements.txt
   ```

2. **Get Gemini API Key:**
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Copy the API key

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

## Usage

1. **Prepare your files:**
   - `resume.txt` - Your resume in text format
   - `jobs.json` - JSON file containing job listings

2. **Run the analysis:**
   ```bash
   python job_fit_analyzer.py
   ```

3. **Results:**
   - The system will analyze each job against your resume
   - Jobs with match scores >= 50 will be saved to `good_score_jobs.json`
   - Console output shows progress and summary

## File Structure

```
job_fit_analysis/
├── job_fit_analyzer.py    # Main analysis script
├── resume.txt             # Your resume (text format)
├── jobs.json              # Job listings (JSON format)
├── good_score_jobs.json   # Output: jobs with good match scores
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Job JSON Format

The `jobs.json` file should contain an array of job objects with this structure:

```json
[
  {
    "title": "Software Developer",
    "company": "Company Name",
    "location": "Location",
    "url": "Job URL",
    "description": "Full job description text",
    "posted_date": "Date posted",
    "scraped_at": "Scraping timestamp"
  }
]
```

## Output Format

The `good_score_jobs.json` file contains jobs with match scores >= 50:

```json
[
  {
    "job": { /* original job object */ },
    "matchScore": 75,
    "analysis": {
      "matchScore": 75,
      "strengths": ["Strong React experience", "..."],
      "gaps": ["Missing Python experience", "..."],
      "suggestions": ["Learn Python", "..."],
      "summary": "Good match with room for improvement"
    }
  }
]
```

## Features

- ✅ Uses Gemini 2.0 Flash for accurate analysis
- ✅ Analyzes job-resume compatibility with detailed scoring
- ✅ Filters jobs with scores >= 50
- ✅ Provides detailed analysis including strengths, gaps, and suggestions
- ✅ Handles errors gracefully
- ✅ Progress tracking and detailed output
