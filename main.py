#!/usr/bin/env python3
"""
Main Job Automation Orchestrator
This script runs the complete job automation workflow:
1. Run job scraper
2. Run job fit analysis
3. Process each good-scoring job sequentially
4. Copy job data to job_description.txt
5. Run test.py for each job
"""

import os
import sys
import json
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path

class JobAutomationOrchestrator:
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.job_description_path = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/job_description.txt"
        self.good_jobs_path = self.project_root / "job_fit_analysis" / "good_score_jobs.json"
        venv_dir = self.project_root / "venv"
        if sys.platform.startswith("win"):
            self.root_python = venv_dir / "Scripts" / "python.exe"
        else:
            self.root_python = venv_dir / "bin" / "python"
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def run_subprocess(self, command, cwd=None, description=""):
        """Run a subprocess and handle errors"""
        self.log(f"Starting: {description}")
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            self.log(f"✅ Completed: {description}")
            if result.stdout:
                print("STDOUT:", result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Failed: {description}")
            print(f"Error: {e}")
            if e.stdout:
                print("STDOUT:", e.stdout)
            if e.stderr:
                print("STDERR:", e.stderr)
            raise
        except Exception as e:
            self.log(f"❌ Unexpected error in {description}: {e}")
            raise
    
    # ---------------------------------------------------
    #  STEP 1: Job Scraper
    # ---------------------------------------------------
    def run_scraper(self):
        """Run the LinkedIn job scraper"""
        self.log("=" * 60)
        self.log("STEP 1: Running LinkedIn Job Scraper")
        self.log("=" * 60)
        
        scraper_path = self.project_root / "job_scrape" / "run_scraper.py"
        
        if not scraper_path.exists():
            raise FileNotFoundError(f"Scraper not found: {scraper_path}")
        if not self.root_python.exists():
            raise FileNotFoundError(f"Root virtual environment Python not found: {self.root_python}")
            
        command = f"\"{self.root_python}\" \"{scraper_path}\""
        self.run_subprocess(
            command, 
            cwd=str(scraper_path.parent),
            description="Running LinkedIn Job Scraper"
        )

    # ---------------------------------------------------
    #  STEP 2: Job Fit Analyzer
    # ---------------------------------------------------
    def run_analyzer(self):
        """Run the job fit analyzer"""
        self.log("=" * 60)
        self.log("STEP 2: Running Job Fit Analyzer")
        self.log("=" * 60)
        
        analyzer_path = self.project_root / "job_fit_analysis" / "job_fit_analyzer.py"
        
        if not analyzer_path.exists():
            raise FileNotFoundError(f"Analyzer not found: {analyzer_path}")
        if not self.root_python.exists():
            raise FileNotFoundError(f"Root virtual environment Python not found: {self.root_python}")
            
        command = f"\"{self.root_python}\" \"{analyzer_path}\""
        
        # Run analyzer in project root so relative paths (./job_scrape/...) resolve correctly
        self.run_subprocess(
            command,
            cwd=str(analyzer_path.parent),  # runs inside job_fit_analysis/
            description="Running Job Fit Analyzer"
        )
            
    # ---------------------------------------------------
    #  STEP 3: Process good-scoring jobs
    # ---------------------------------------------------
    def load_good_jobs(self):
        """Load the good scoring jobs from JSON file"""
        if not self.good_jobs_path.exists():
            raise FileNotFoundError(f"Good jobs file not found: {self.good_jobs_path}")
            
        with open(self.good_jobs_path, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
            
        self.log(f"Loaded {len(jobs)} good-scoring jobs from {self.good_jobs_path}")
        return jobs
        
    def write_job_description(self, job_data):
        """Write job data to the job_description.txt file"""
        company = job_data['job'].get('company', 'Unknown Company')
        title = job_data['job'].get('title', 'Unknown Title')
        description = job_data['job'].get('description', 'No description available')
        
        content = f"""COMPANY: {company}
TITLE: {title}

DESCRIPTION:
{description}

---
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        with open(self.job_description_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self.log(f"✅ Written job data to {self.job_description_path}")
        self.log(f"   Company: {company}")
        self.log(f"   Title: {title}")
    
    def process_title_or_company_name(self, name):
        """Replace invalid characters in title/company name"""
        return name.replace("/", "_")
        
    def run_test_script(self, job_index, total_jobs, company, title, easy_apply, location, job_category="sde"):
        """Run the test.py script"""
        self.log("=" * 60)
        self.log(f"STEP 4: Running test.py (Job {job_index + 1}/{total_jobs})")
        self.log("=" * 60)
        
        test_path = self.project_root / "test.py"
        
        if not test_path.exists():
            raise FileNotFoundError(f"Test script not found: {test_path}")
        if not self.root_python.exists():
            raise FileNotFoundError(f"Root virtual environment Python not found: {self.root_python}")
        
        company = self.process_title_or_company_name(company)
        title = self.process_title_or_company_name(title)
        easy_apply = "true" if easy_apply else "false"
        
        command = f"\"{self.root_python}\" test.py \"{company}\" \"{title}\" \"{easy_apply}\" \"{location}\" \"{job_category}\""
        self.run_subprocess(
            command, 
            cwd=str(test_path.parent),
            description="Running test.py"
        )
        
    async def process_all_jobs(self):
        """Process all good-scoring jobs sequentially"""
        self.log("=" * 60)
        self.log("STEP 3: Processing Good-Scoring Jobs")
        self.log("=" * 60)
        
        jobs = self.load_good_jobs()
        
        if not jobs:
            self.log("⚠️ No good-scoring jobs found. Exiting.")
            return
            
        self.log(f"Found {len(jobs)} jobs to process")
        
        for i, job_data in enumerate(jobs):
            self.log("=" * 60)
            self.log(f"PROCESSING JOB {i + 1}/{len(jobs)}")
            self.log("=" * 60)
            
            company = job_data['job'].get('company', 'Unknown')
            title = job_data['job'].get('title', 'Unknown')
            easy_apply = job_data['job'].get('easy_apply', False)
            job_category = job_data.get('job_category', 'sde')  # Get job_category from job_data
            location = job_data['job'].get('location', '')
            self.log(f"Processing: {title} at {company} (category: {job_category})")
            
            # Step 1: Write job description
            self.write_job_description(job_data)
            
            # Step 2: Run test.py
            self.run_test_script(i, len(jobs), company, title, easy_apply, location, job_category)
            
            self.log(f"✅ Completed processing job {i + 1}/{len(jobs)}")
            
    # ---------------------------------------------------
    #  MAIN WORKFLOW
    # ---------------------------------------------------
    async def run_complete_workflow(self):
        """Run the complete job automation workflow"""
        try:
            self.log("🚀 Starting Job Automation Workflow")
            self.log("=" * 80)

            # # Step 1: Run job scraper
            self.run_scraper()

            # Step 2: Run job fit analyzer
            # self.run_analyzer()

            # # Step 3: Process all good jobs
            # await self.process_all_jobs()

            self.log("=" * 80)
            self.log("🎉 Job Automation Workflow Completed Successfully!")

        except KeyboardInterrupt:
            self.log("\n⚠️ Workflow interrupted by user")
            sys.exit(0)
        except Exception as e:
            self.log(f"❌ Workflow failed with error: {e}")
            sys.exit(1)

# ---------------------------------------------------
#  ENTRY POINT
# ---------------------------------------------------
async def main():
    orchestrator = JobAutomationOrchestrator()
    await orchestrator.run_complete_workflow()

if __name__ == "__main__":
    asyncio.run(main())
