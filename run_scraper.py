#!/usr/bin/env python3
"""
Complete workflow runner for Esprit job scraping

This script demonstrates the full scraping process:
1. Login to Esprit Connect
2. Scrape jobs starting from ID 785
3. Generate RSS, JSON, and HTML feeds
"""

import sys
import os
import argparse
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description='Esprit Jobs Scraper')
    parser.add_argument('--max-jobs', type=int, default=200,
                        help='Maximum jobs to scrape (default: 200)')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')
    parser.add_argument('--test-only', action='store_true',
                        help='Run test mode only')
    parser.add_argument('--reset', action='store_true',
                        help='Reset scraper state to start from job 785')

    args = parser.parse_args()

    print("🚀 Esprit Connect Job Scraper")
    print("=" * 50)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.test_only:
        print("🧪 Running in test mode...")
        try:
            from test_scraper import main as test_main
            return test_main()
        except ImportError:
            print("❌ Test module not found")
            return 1

    # Reset state if requested
    if args.reset:
        import os
        state_file = "scraper_state.json"
        if os.path.exists(state_file):
            os.remove(state_file)
            print("🔄 Reset scraper state - will start from job 785")
        else:
            print("ℹ️ No state file found - will start from job 785")

    # Check credentials
    try:
        from config.secrets import ESPRIT_EMAIL, ESPRIT_PASSWORD
        print("✅ Local credentials loaded")
    except ImportError:
        if os.getenv('ESPRIT_EMAIL') and os.getenv('ESPRIT_PASSWORD'):
            print("✅ Environment credentials loaded")
        else:
            print("❌ No credentials found!")
            print("\nPlease either:")
            print("1. Create config/secrets.py with ESPRIT_EMAIL and ESPRIT_PASSWORD")
            print("2. Set environment variables ESPRIT_EMAIL and ESPRIT_PASSWORD")
            return 1

    # Run the scraper
    print(f"\n Maximum jobs to scrape: {args.max_jobs}")
    print(f"🖥️ Headless mode: {args.headless}")

    try:
        from esprit_job_scraper import EspritJobScraper

        with EspritJobScraper(headless=args.headless) as scraper:
            print(f"🔍 Starting scrape from job ID {scraper.current_job_id}")
            jobs = scraper.scrape_jobs(max_jobs=args.max_jobs)

            if jobs:
                print(f"\n✅ Successfully scraped {len(jobs)} jobs")
                scraper.save_results()
                print(
                    f"📊 Next run will start from job ID {scraper.current_job_id}")

                # Show sample of scraped jobs
                print("\n📋 Sample of scraped jobs:")
                for i, job in enumerate(jobs[:3]):
                    print(
                        f"  {i+1}. Job {job.job_id}: {job.title} @ {job.company}")

                if len(jobs) > 3:
                    print(f"  ... and {len(jobs) - 3} more jobs")

                return 0
            else:
                print("⚠️ No jobs were scraped")
                return 1

    except Exception as e:
        print(f"💥 Scraper failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(exit_code)
