#!/usr/bin/env python3
"""
Job Fit Analysis System using Gemini 2.0 Flash
Analyzes job matches against a resume and filters for good matches (score >= 50)
"""

import json
import os
import sys
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JobFitAnalyzer:
    def __init__(self, api_key: str = None):
        """Initialize the Job Fit Analyzer with Gemini API key"""
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY environment variable or pass it as parameter.")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def load_resume(self, resume_path: str) -> str:
        """Load resume text from file"""
        try:
            with open(resume_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Resume file not found: {resume_path}")
        except Exception as e:
            raise Exception(f"Error reading resume file: {e}")
    
    def load_jobs(self, jobs_path: str) -> List[Dict[str, Any]]:
        """Load jobs data from JSON file"""
        try:
            with open(jobs_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Jobs file not found: {jobs_path}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing jobs JSON: {e}")
        except Exception as e:
            raise Exception(f"Error reading jobs file: {e}")
    
    def create_prompt(self, resume_text: str, job_description: str) -> str:
        """Create the analysis prompt for Gemini"""
        prompt = f"""
You are a job application evaluator specializing in the technology industry.

Analyze how well the following resume matches the provided job description.

Return **only** a valid JSON object using the exact structure below — no code fences or additional commentary.

{{
  "matchScore": number (e.g. 75),
  "strengths": [string, string, ...],
  "gaps": [string, string, ...],
  "suggestions": [string, string, ...],
  "summary": string
}}

---

Resume:
{resume_text}

---

Job Description:
{job_description}
        """.strip()
        
        return prompt
    
    def analyze_job_fit(self, resume_text: str, job: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze job fit using Gemini and return the match score"""
        try:
            # Extract job description
            job_description = job.get('description', '')
            job_title = job.get('title', 'Unknown')
            company = job.get('company', 'Unknown')
            
            print(f"Analyzing: {job_title} at {company}...")
            
            # Create prompt
            prompt = self.create_prompt(resume_text, job_description)
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response
            response_text = response.text.strip()
            
            # Remove any markdown code fences if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON response
            try:
                analysis_result = json.loads(response_text)
                match_score = analysis_result.get('matchScore', 0)
                
                return {
                    'job': job,
                    'matchScore': match_score,
                    'analysis': analysis_result,
                    'status': 'success'
                }
                
            except json.JSONDecodeError as e:
                print(f"Error parsing Gemini response as JSON: {e}")
                print(f"Raw response: {response_text}")
                return {
                    'job': job,
                    'matchScore': 0,
                    'analysis': None,
                    'status': 'error',
                    'error': f"Failed to parse response: {e}"
                }
                
        except Exception as e:
            print(f"Error analyzing job: {e}")
            return {
                'job': job,
                'matchScore': 0,
                'analysis': None,
                'status': 'error',
                'error': str(e)
            }
    
    def analyze_all_jobs(self, resume_path: str, jobs_path: str) -> List[Dict[str, Any]]:
        """Analyze all jobs and return results"""
        # Load resume and jobs
        resume_text = self.load_resume(resume_path)
        jobs = self.load_jobs(jobs_path)
        
        print(f"Loaded {len(jobs)} jobs to analyze...")
        print(f"Resume loaded from: {resume_path}")
        print("-" * 50)
        
        results = []
        for i, job in enumerate(jobs, 1):
            print(f"[{i}/{len(jobs)}] Processing job...")
            result = self.analyze_job_fit(resume_text, job)
            results.append(result)
            
            # Print the match score for this job
            if result['status'] == 'success':
                print(f"Match Score: {result['matchScore']}/100")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
            print("-" * 30)
        
        return results
    
    def filter_good_matches(self, results: List[Dict[str, Any]], min_score: int = 67) -> List[Dict[str, Any]]:
        """Filter jobs with match score >= min_score"""
        good_matches = []
        for result in results:
            if result['status'] == 'success' and result['matchScore'] >= min_score:
                good_matches.append(result)
        
        return good_matches
    
    def save_good_matches(self, good_matches: List[Dict[str, Any]], output_path: str = "good_score_jobs.json"):
        """Save good matches to JSON file"""
        # Prepare data for output (include original job data plus analysis)
        output_data = []
        for match in good_matches:
            output_data.append({
                'job': match['job'],
                'matchScore': match['matchScore'],
                'analysis': match['analysis']
            })
        
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(output_data, file, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(output_data)} good matches to {output_path}")


def main():
    """Main function to run the job fit analysis"""
    try:
        # Initialize analyzer
        analyzer = JobFitAnalyzer()
        
        # File paths
        resume_path = "./resume.txt"
        jobs_path = "./linkedin_jobs.json"
        output_path = "./good_score_jobs.json"
        
        # Check if files exist
        if not os.path.exists(resume_path):
            print(f"Error: Resume file not found: {resume_path}")
            sys.exit(1)
        
        if not os.path.exists(jobs_path):
            print(f"Error: Jobs file not found: {jobs_path}")
            sys.exit(1)
        
        # Analyze all jobs
        print("Starting job fit analysis...")
        results = analyzer.analyze_all_jobs(resume_path, jobs_path)
        
        # Filter good matches
        print("\nFiltering good matches (score >= 50)...")
        good_matches = analyzer.filter_good_matches(results, min_score=50)
        
        # Save results
        if good_matches:
            analyzer.save_good_matches(good_matches, output_path)
            print(f"\n✅ Found {len(good_matches)} jobs with good match scores (>= 50)")
        else:
            print("\n❌ No jobs found with match scores >= 50")
            # Still save empty results
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump([], file, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("ANALYSIS SUMMARY")
        print("="*50)
        print(f"Total jobs analyzed: {len(results)}")
        print(f"Successful analyses: {len([r for r in results if r['status'] == 'success'])}")
        print(f"Failed analyses: {len([r for r in results if r['status'] == 'error'])}")
        print(f"Good matches (score >= 50): {len(good_matches)}")
        
        if good_matches:
            print("\nGood matches:")
            for match in good_matches:
                job = match['job']
                score = match['matchScore']
                print(f"  • {job['title']} at {job['company']} - Score: {score}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
