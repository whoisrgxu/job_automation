#!/usr/bin/env python3
"""
Batch processing script for running multiple scraping sessions
with different configurations to avoid detection
"""
import asyncio
import time
from datetime import datetime
from typing import List, Dict
from linkedin_scraper import LinkedInJobScraper
from config import Config


class BatchScraper:
    def __init__(self):
        self.config = Config()
        self.session_count = 0
        self.total_jobs = []
    
    def create_session_config(self, keywords: List[str], locations: List[str]) -> Dict:
        """Create configuration for a single session"""
        return {
            'keywords': keywords,
            'locations': locations,
            'max_pages': 5,  # Reduced pages per session
            'delay_between_requests': (3, 7),  # Increased delays
            'delay_between_pages': (8, 15),
            'max_jobs_per_session': 50
        }
    
    async def run_session(self, session_config: Dict):
        """Run a single scraping session"""
        self.session_count += 1
        session_start = datetime.now()
        
        print(f"\n🔄 Starting Session {self.session_count}")
        print(f"⏰ Time: {session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 Keywords: {', '.join(session_config['keywords'])}")
        print(f"📍 Locations: {', '.join(session_config['locations'])}")
        print("-" * 60)
        
        # Temporarily modify config
        original_keywords = self.config.KEYWORDS
        original_locations = self.config.LOCATIONS
        original_max_pages = self.config.MAX_PAGES
        original_delays = self.config.DELAY_BETWEEN_REQUESTS
        original_page_delays = self.config.DELAY_BETWEEN_PAGES
        original_max_jobs = self.config.MAX_JOBS_PER_SESSION
        
        # Apply session config
        self.config.KEYWORDS = session_config['keywords']
        self.config.LOCATIONS = session_config['locations']
        self.config.MAX_PAGES = session_config['max_pages']
        self.config.DELAY_BETWEEN_REQUESTS = session_config['delay_between_requests']
        self.config.DELAY_BETWEEN_PAGES = session_config['delay_between_pages']
        self.config.MAX_JOBS_PER_SESSION = session_config['max_jobs_per_session']
        
        try:
            scraper = LinkedInJobScraper()
            await scraper.run_scraper()
            
            # Collect results
            session_jobs = scraper.jobs_data
            self.total_jobs.extend(session_jobs)
            
            print(f"✅ Session {self.session_count} completed")
            print(f"📊 Jobs found in this session: {len(session_jobs)}")
            print(f"📊 Total jobs collected: {len(self.total_jobs)}")
            
        except Exception as e:
            print(f"❌ Session {self.session_count} failed: {e}")
        
        finally:
            # Restore original config
            self.config.KEYWORDS = original_keywords
            self.config.LOCATIONS = original_locations
            self.config.MAX_PAGES = original_max_pages
            self.config.DELAY_BETWEEN_REQUESTS = original_delays
            self.config.DELAY_BETWEEN_PAGES = original_page_delays
            self.config.MAX_JOBS_PER_SESSION = original_max_jobs
        
        # Session cooldown
        if self.session_count < len(self.get_session_configs()):
            cooldown = self.config.SESSION_COOLDOWN
            print(f"⏳ Cooling down for {cooldown} seconds before next session...")
            await asyncio.sleep(cooldown)
    
    def get_session_configs(self) -> List[Dict]:
        """Get configurations for all sessions"""
        # Split keywords and locations into smaller batches
        keyword_batches = [
            ['python developer', 'software engineer'],
            ['data scientist', 'machine learning engineer'],
            ['web developer', 'full stack developer']
        ]
        
        location_batches = [
            ['United States', 'Remote'],
            ['New York, NY', 'San Francisco, CA'],
            ['Chicago, IL', 'Austin, TX']
        ]
        
        session_configs = []
        for i, keywords in enumerate(keyword_batches):
            for j, locations in enumerate(location_batches):
                session_configs.append(self.create_session_config(keywords, locations))
        
        return session_configs
    
    async def run_batch_scraping(self):
        """Run all scraping sessions"""
        print("🚀 Starting Batch LinkedIn Job Scraping")
        print("=" * 60)
        
        session_configs = self.get_session_configs()
        total_sessions = len(session_configs)
        
        print(f"📋 Total sessions planned: {total_sessions}")
        print(f"⏱️  Estimated time: {total_sessions * (self.config.SESSION_COOLDOWN + 300) / 60:.1f} minutes")
        print("=" * 60)
        
        start_time = datetime.now()
        
        for i, session_config in enumerate(session_configs, 1):
            print(f"\n📊 Progress: {i}/{total_sessions} sessions")
            await self.run_session(session_config)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 Batch scraping completed!")
        print(f"⏱️  Total duration: {duration}")
        print(f"📊 Total jobs collected: {len(self.total_jobs)}")
        print(f"📊 Unique jobs: {len(set(job['url'] for job in self.total_jobs))}")
        
        # Save final results
        await self.save_final_results()
    
    async def save_final_results(self):
        """Save all collected results"""
        if not self.total_jobs:
            print("❌ No jobs to save")
            return
        
        # Remove duplicates
        unique_jobs = []
        seen_urls = set()
        for job in self.total_jobs:
            if job['url'] not in seen_urls:
                unique_jobs.append(job)
                seen_urls.add(job['url'])
        
        print(f"💾 Saving {len(unique_jobs)} unique jobs...")
        
        # Save with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'linkedin_jobs_batch_{timestamp}.csv'
        
        import pandas as pd
        df = pd.DataFrame(unique_jobs)
        df.to_csv(filename, index=False)
        
        print(f"✅ Results saved to {filename}")


async def main():
    """Main function"""
    batch_scraper = BatchScraper()
    await batch_scraper.run_batch_scraping()


if __name__ == "__main__":
    asyncio.run(main())
