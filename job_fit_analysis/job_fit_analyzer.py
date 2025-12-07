#!/usr/bin/env python3
"""
Job Fit Analysis System using Gemini 2.5 Flash live
Analyzes job matches against multiple resume templates and assigns a category
based on fit scores + thresholds.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import google.generativeai as genai
from dotenv import load_dotenv
from decide_category import decide_category

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from job_fit_analysis.applied_tracker import (
    AppliedTracker,
    DEFAULT_TRACKER_PATH,
    DEFAULT_SHEET_NAME,
)

# Load environment variables
load_dotenv()


class JobFitAnalyzer:
    def process_title_or_company_name(self, name: str) -> str:
        """Replace invalid characters in title/company name"""
        return name.replace("/", "_")

    def __init__(self, api_key: str | None = None):
        """Initialize the Job Fit Analyzer with Gemini API key"""
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "Gemini API key not found. Please set GEMINI_API_KEY environment "
                "variable or pass it as parameter."
            )

        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        tracker_path = os.getenv("JOB_TRACKER_PATH", str(DEFAULT_TRACKER_PATH))
        tracker_sheet = os.getenv("JOB_TRACKER_SHEET", DEFAULT_SHEET_NAME)
        self.applied_tracker = AppliedTracker(tracker_path, tracker_sheet)

    def load_resume(self, resume_path: str) -> str:
        """Load resume text from file"""
        try:
            with open(resume_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Resume file not found: {resume_path}")
        except Exception as e:
            raise Exception(f"Error reading resume file: {e}")

    def load_jobs(self, jobs_path: str) -> List[Dict[str, Any]]:
        """Load jobs data from JSON file"""
        try:
            with open(jobs_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Jobs file not found: {jobs_path}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing jobs JSON: {e}")
        except Exception as e:
            raise Exception(f"Error reading jobs file: {e}")

    def create_prompt(
        self, resume_text_collection: Dict[str, str], job_description: str
    ) -> str:
        """Create the analysis prompt for Gemini"""
        prompt = f"""
You are an expert job-to-resume matcher.

Task:
Given a job description and four resume templates (SDE, Cloud Support, SharePoint/PowerApps Support, Application Support),
score how well the job description matches each template from 0 to 100.

Output STRICTLY a valid JSON object using the extracted structure below - no code fences or additional commentary:
{{
  "sde_fit": <0-100> (e.g. 75),
  "cloud_support_fit": <0-100>,
  "sharepoint_support_fit": <0-100>,
  "application_support_fit": <0-100>
}}

Scoring guideline:
- Consider responsibilities, required skills, tech stack, and seniority.
- 90-100: Extremely strong match (almost written for this profile)
- 80-89: Strong match (clearly fits)
- 70-79: Good match (reasonable fit, some gaps)
- 60-69: Partial match
- Below 60: Weak or poor match
- Do NOT hallucinate; if the role is pure customer service or unrelated, all fits should be low.

Now here is the job description:

{job_description}

Here are the four resume templates (summarized profiles):

[SDE TEMPLATE]
{resume_text_collection['sde']}

[CLOUD SUPPORT TEMPLATE]
{resume_text_collection['cloud_support']}

[SHAREPOINT SUPPORT TEMPLATE]
{resume_text_collection['sharepoint_support']}

[APPLICATION SUPPORT TEMPLATE]
{resume_text_collection['application_support']}

---
        """.strip()

        return prompt

    def analyze_job_fit(
        self, resume_text_collection: Dict[str, str], job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze job fit using Gemini and return the match scores + category"""
        try:
            # Extract job description
            job_description = job.get("description", "")
            job_title = job.get("title", "Unknown")
            company = job.get("company", "Unknown")

            print(f"Analyzing: {job_title} at {company}...")

            # Create prompt
            prompt = self.create_prompt(resume_text_collection, job_description)

            # Get response from Gemini
            response = self.model.generate_content(prompt)

            # Parse the response
            response_text = (response.text or "").strip()

            # Remove any markdown code fences if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON response
            try:
                fit_scores = json.loads(response_text)

                category = decide_category(fit_scores)

                if category != "skip":
                    return {
                        "job": job,
                        "category": category,
                        "fit_scores": fit_scores,
                        "status": "success",
                    }

                # skip 情况也带上 job 和 fit_scores，方便后续分析
                return {
                    "job": job,
                    "category": "skip",
                    "fit_scores": fit_scores,
                    "status": "success",
                }

            except json.JSONDecodeError as e:
                print(f"Error parsing Gemini response as JSON: {e}")
                print(f"Raw response: {response_text}")
                return {
                    "job": job,
                    "category": None,
                    "status": "error",
                    "error": f"Failed to parse job fit analysis response: {e}",
                }

        except Exception as e:
            msg = str(e)
            print(f"Error analyzing job: {msg}")

            # Treat 429 / RESOURCE_EXHAUSTED / quota messages as quota_exceeded
            lower = msg.lower()
            if "429" in lower or "resource_exhausted" in lower or "quota" in lower:
                status = "quota_exceeded"
            else:
                status = "error"

            return {
                "job": job,
                "category": None,
                "status": status,
                "error": msg,
            }

    def analyze_all_jobs(
        self, resume_paths: Dict[str, str], jobs_path: str
    ) -> List[Dict[str, Any]]:
        """Analyze all jobs with multi-template scoring and categorization"""
        # Load resumes and jobs
        resume_SDE_text = self.load_resume(resume_paths["sde"])
        resume_Application_Support_text = self.load_resume(
            resume_paths["application_support"]
        )
        resume_Cloud_Support_text = self.load_resume(resume_paths["cloud_support"])
        resume_SharePoint_Support_text = self.load_resume(
            resume_paths["sharepoint_support"]
        )

        resume_text_collection: Dict[str, str] = {
            "sde": resume_SDE_text,
            "application_support": resume_Application_Support_text,
            "cloud_support": resume_Cloud_Support_text,
            "sharepoint_support": resume_SharePoint_Support_text,
        }

        jobs = self.load_jobs(jobs_path)

        print(f"Loaded {len(jobs)} jobs to analyze...")
        print(f"SDE resume loaded from: {resume_paths['sde']}")
        print(
            f"Application Support resume loaded from: {resume_paths['application_support']}"
        )
        print(f"Cloud Support resume loaded from: {resume_paths['cloud_support']}")
        print(
            f"SharePoint Support resume loaded from: {resume_paths['sharepoint_support']}"
        )
        print("-" * 50)

        results: List[Dict[str, Any]] = []
        for i, job in enumerate(jobs, 1):
            print(f"[{i}/{len(jobs)}] Processing job...")

            # Delay to avoid rate limits if needed
            time.sleep(5)

            result = self.analyze_job_fit(resume_text_collection, job)
            status = result.get("status")

            if status == "quota_exceeded":
                print("🚫 Gemini quota exhausted. Stopping further analysis.")
                # We break here but still return whatever results we already collected
                break

            if status == "success" and result.get("category") != "skip":
                results.append(result)
                print(f"Match category: {result['category']}")
            else:
                if status == "success" and result.get("category") == "skip":
                    print("Job is not matched with any category, skip...")
                else:
                    print(f"Error: {result.get('error', 'Unknown error')}")

            print("-" * 30)

        return results

    def save_good_matches(
        self, good_matches: List[Dict[str, Any]], output_path: str = "good_score_jobs.json"
    ) -> None:
        """Save good matches to JSON file"""
        output_data = []
        for idx, match in enumerate(good_matches, 1):
            output_data.append(
                {
                    "id": idx,
                    "job": match["job"],
                    "job_category": match.get("category", "unknown"),
                    "fit_scores": match.get("fit_scores", {}),
                }
            )

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(output_data, file, indent=2, ensure_ascii=False)

        print(f"Saved {len(output_data)} good matches to {output_path}")

    def filter_already_applied(
        self, matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove matches that have already been applied to recently."""
        if not matches:
            return matches

        filtered: List[Dict[str, Any]] = []
        for match in matches:
            job = match.get("job", {})
            company = job.get("company", "")
            title = job.get("title", "")
            description = job.get("description", "")
            processed_company = self.process_title_or_company_name(company)
            processed_title = self.process_title_or_company_name(title)
            if self.applied_tracker.is_applied(
                processed_company, processed_title, job_description=description
            ):
                print(f"⏩ Skipping already applied job: {title} at {company}")
                continue

            filtered.append(match)
        return filtered


def main() -> None:
    """Main function to run the job fit analysis"""
    try:
        # Initialize analyzer
        analyzer = JobFitAnalyzer()

        # File paths
        resume_paths = {
            "sde": "./resume_SDE.txt",
            "application_support": "./resume_Application_Support.txt",
            "cloud_support": "./resume_Cloud_Support.txt",
            "sharepoint_support": "./resume_SharePoint_Support.txt",
        }
        jobs_path = "./linkedin_jobs.json"
        output_path = "./good_score_jobs.json"

        # Check if files exist
        if not os.path.exists(resume_paths["sde"]):
            print(f"Error: SDE Resume file not found: {resume_paths['sde']}")
            sys.exit(1)

        if not os.path.exists(resume_paths["application_support"]):
            print(
                f"Error: Application Support resume file not found: {resume_paths['application_support']}"
            )
            sys.exit(1)
        if not os.path.exists(resume_paths["cloud_support"]):
            print(
                f"Error: Cloud Support resume file not found: {resume_paths['cloud_support']}"
            )
            sys.exit(1)
        if not os.path.exists(resume_paths["sharepoint_support"]):
            print(
                f"Error: SharePoint Support resume file not found: {resume_paths['sharepoint_support']}"
            )
            sys.exit(1)

        if not os.path.exists(jobs_path):
            print(f"Error: Jobs file not found: {jobs_path}")
            sys.exit(1)

        # Analyze all jobs
        print("Starting job fit analysis...")
        results = analyzer.analyze_all_jobs(resume_paths, jobs_path)

        # Filter out already-applied jobs
        print("\nFiltering out already-applied jobs...")
        filtered_results = analyzer.filter_already_applied(results)

        # Save results
        if filtered_results:
            analyzer.save_good_matches(filtered_results, output_path)
            sde_count = len(
                [m for m in filtered_results if m.get("category") == "sde"]
            )
            application_support_count = len(
                [
                    m
                    for m in filtered_results
                    if m.get("category") == "application_support"
                ]
            )
            cloud_support_count = len(
                [
                    m
                    for m in filtered_results
                    if m.get("category") == "cloud_support"
                ]
            )
            sharepoint_support_count = len(
                [
                    m
                    for m in filtered_results
                    if m.get("category") == "sharepoint_support"
                ]
            )
            print(f"\n✅ Found {len(filtered_results)} jobs that you haven't applied to yet")
            print(f"   - SDE category: {sde_count} jobs")
            print(
                f"   - Application Support category: {application_support_count} jobs"
            )
            print(f"   - Cloud Support category: {cloud_support_count} jobs")
            print(
                f"   - SharePoint Support category: {sharepoint_support_count} jobs"
            )
        else:
            print("\n❌ No jobs found matching any category")
            # Still save empty results
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump([], file, indent=2)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
