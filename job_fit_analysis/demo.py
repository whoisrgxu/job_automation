#!/usr/bin/env python3
"""
Demo script showing how to use the Job Fit Analyzer
"""

import os
from job_fit_analyzer import JobFitAnalyzer

def main():
    """Demo function showing basic usage"""
    print("Job Fit Analysis Demo")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'test_key':
        print("❌ Please set your Gemini API key:")
        print("   export GEMINI_API_KEY='your_actual_api_key_here'")
        print("\n   Get your API key from: https://aistudio.google.com/")
        return
    
    try:
        # Initialize analyzer
        analyzer = JobFitAnalyzer(api_key)
        
        # Check if files exist
        if not os.path.exists('resume.txt'):
            print("❌ resume.txt not found. Please create your resume file.")
            return
            
        if not os.path.exists('jobs.json'):
            print("❌ jobs.json not found. Please create your jobs file.")
            return
        
        # Analyze jobs
        print("🚀 Starting analysis...")
        results = analyzer.analyze_all_jobs('resume.txt', 'jobs.json', industry="Technology")
        
        # Filter good matches
        good_matches = analyzer.filter_good_matches(results, min_score=50)
        
        # Save results
        analyzer.save_good_matches(good_matches, 'good_score_jobs.json')
        
        print(f"\n✅ Analysis complete!")
        print(f"📊 Found {len(good_matches)} jobs with good match scores (>= 50)")
        
        if good_matches:
            print("\n🎯 Good matches:")
            for match in good_matches:
                job = match['job']
                score = match['matchScore']
                print(f"   • {job['title']} at {job['company']} - Score: {score}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
