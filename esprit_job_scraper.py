#!/usr/bin/env python3
"""
Esprit Connect Job Scraper

Authenticates to Esprit Connect and scrapes job postings starting from job ID 785
until it encounters a non-existent job (which redirects to home page).
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Union
from urllib.parse import urljoin, urlparse
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load credentials


def load_credentials():
    """Load credentials from config file or environment variables"""
    try:
        # Try to import from config directory relative to this script
        config_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'config')
        if config_dir not in sys.path:
            sys.path.insert(0, config_dir)

        from secrets import ESPRIT_EMAIL, ESPRIT_PASSWORD
        logger.info("Loaded credentials from config/secrets.py")
        return ESPRIT_EMAIL, ESPRIT_PASSWORD
    except ImportError:
        # Fallback to environment variables
        email = os.getenv('ESPRIT_EMAIL', '')
        password = os.getenv('ESPRIT_PASSWORD', '')
        if email and password:
            logger.info("Loaded credentials from environment variables")
            return email, password
        else:
            logger.error(
                "No credentials found in config file or environment variables")
            raise ValueError(
                "Please set ESPRIT_EMAIL and ESPRIT_PASSWORD environment variables or create config/secrets.py")


# Load credentials at module level
ESPRIT_EMAIL, ESPRIT_PASSWORD = load_credentials()


@dataclass
class JobPosting:
    """Data structure for a job posting"""
    job_id: int
    title: str
    company: str
    location: str
    description: str
    requirements: str
    posted_date: str
    url: str
    image_url: Optional[str] = None
    company_logo_url: Optional[str] = None
    employment_type: Optional[str] = None
    industry: Optional[str] = None
    job_function: Optional[str] = None
    closing_date: Optional[str] = None
    added_by_name: Optional[str] = None
    added_by_company: Optional[str] = None
    scraped_at: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()


class EspritJobScraper:
    """Main scraper class for Esprit Connect jobs"""

    def __init__(self, headless: bool = True, state_file: str = "scraper_state.json"):
        # Start from job 795 for production testing
        self.initial_job_id = 795
        self.state_file = state_file
        self.current_job_id = self.load_last_job_id()
        self.base_url = "https://espritconnect.com"
        self.jobs_scraped: List[JobPosting] = []
        self.session = requests.Session()

        # Load existing job IDs for duplicate detection (EXTRA SAFETY)
        self.existing_job_ids = self.load_existing_job_ids()

        # Start from current_job_id - 1 for extra safety against duplicates
        if self.current_job_id > self.initial_job_id:
            self.current_job_id = self.current_job_id - 1
            logger.info(
                f"🔄 Starting from job ID {self.current_job_id} (current-1) for duplicate safety")

        # Configure Chrome options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')

        self.driver = None
        self.wait = None

    def load_last_job_id(self) -> int:
        """Load the last scraped job ID from state file, or return initial ID"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    last_id = state.get('last_job_id', self.initial_job_id)
                    logger.info(
                        f"Resuming from job ID {last_id} (loaded from {self.state_file})")
                    return last_id
            else:
                logger.info(
                    f"No state file found, starting from initial job ID {self.initial_job_id}")
                return self.initial_job_id
        except Exception as e:
            logger.warning(
                f"Error loading state file: {e}, starting from initial job ID {self.initial_job_id}")
            return self.initial_job_id

    def load_existing_job_ids(self) -> set:
        """Load existing job IDs from data files for duplicate detection"""
        existing_ids = set()

        # Check multiple possible locations for existing job data
        data_files = [
            "data/jobs_raw.json",
            "jobs_raw.json"
        ]

        for data_file in data_files:
            if os.path.exists(data_file):
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        jobs = json.load(f)

                    if jobs:
                        job_ids = {job['job_id']
                                   for job in jobs if 'job_id' in job}
                        existing_ids.update(job_ids)
                        logger.info(
                            f"🔍 Loaded {len(job_ids)} existing job IDs from {data_file}")
                        break  # Use the first file found

                except Exception as e:
                    logger.warning(
                        f"Error loading existing job data from {data_file}: {e}")

        if existing_ids:
            logger.info(
                f"🛡️ Duplicate detection active - will skip {len(existing_ids)} existing jobs")
        else:
            logger.info("🆕 No existing job data found - starting fresh")

        return existing_ids

    def save_last_job_id(self, job_id: int) -> None:
        """Save the last processed job ID to state file"""
        try:
            state = {
                'last_job_id': job_id,
                'last_updated': datetime.now().isoformat(),
                'total_runs': 1
            }

            # If state file exists, preserve run count
            if os.path.exists(self.state_file):
                try:
                    with open(self.state_file, 'r') as f:
                        existing_state = json.load(f)
                        state['total_runs'] = existing_state.get(
                            'total_runs', 0) + 1
                except Exception:
                    pass

            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)

            logger.info(
                f"Saved state: next run will start from job ID {job_id + 1}")
        except Exception as e:
            logger.error(f"Error saving state file: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.driver:
            self.driver.quit()

    def login(self) -> bool:
        """Authenticate to Esprit Connect"""
        try:
            logger.info("Starting login process...")

            # Navigate to login page
            self.driver.get(f"{self.base_url}/")
            self.driver.set_window_size(1550, 830)

            # Handle cookie consent with more robust approach
            try:
                cookie_reject_btn = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.ID, "onetrust-reject-all-handler"))
                )
                cookie_reject_btn.click()
                logger.info("Cookie consent rejected")

                # Wait for cookie banner to disappear
                self.wait.until(
                    EC.invisibility_of_element_located(
                        (By.ID, "onetrust-button-group"))
                )
                logger.info("Cookie banner disappeared")
            except TimeoutException:
                logger.info("No cookie consent dialog found")

            # Wait a moment for page to settle
            import time
            time.sleep(2)

            # Click sign in button with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    sign_in_btn = self.wait.until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, ".gw-sign-in .material-icons"))
                    )
                    sign_in_btn.click()
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.info(
                            f"Sign-in click attempt {attempt + 1} failed, retrying...")
                        time.sleep(2)
                    else:
                        raise e

            # Enter credentials
            email_field = self.wait.until(
                EC.element_to_be_clickable((By.ID, "mat-input-0")))
            email_field.clear()
            email_field.send_keys(ESPRIT_EMAIL)

            password_field = self.wait.until(
                EC.element_to_be_clickable((By.ID, "mat-input-1")))
            password_field.clear()
            password_field.send_keys(ESPRIT_PASSWORD)

            # Submit login
            login_btn = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".gw-btn-sign-in")))
            login_btn.click()

            # Verify successful login
            try:
                self.wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "#gw-parent-menu-link-jobs > .item-title"))
                )
                logger.info("✅ Login successful")
                return True
            except TimeoutException:
                logger.error("❌ Login failed - expected elements not found")
                return False

        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False

    def is_redirected_to_home(self) -> bool:
        """Check if we've been redirected to home page (indicating non-existent job)"""
        current_url = self.driver.current_url

        # More robust redirect detection
        redirected = (
            current_url.endswith('/feed') or
            current_url.endswith('/') or
            current_url.endswith('/jobs') or  # Redirected to jobs list
            '/jobs/' not in current_url or
            current_url == self.base_url or
            current_url == f"{self.base_url}/" or
            current_url == f"{self.base_url}/feed"
        )

        if redirected:
            logger.info(f"Detected redirect: {current_url}")

        return redirected

    def extract_job_data(self, job_id: int) -> Optional[Union[JobPosting, str]]:
        """Extract job data from a job page"""
        try:
            job_url = f"{self.base_url}/jobs/{job_id}"
            logger.info(f"Scraping job {job_id}: {job_url}")

            self.driver.get(job_url)
            time.sleep(2)  # Allow page to load

            # Check if redirected (job doesn't exist)
            if self.is_redirected_to_home():
                logger.info(
                    f"Job {job_id} doesn't exist - redirected to home page")
                # Wait 3 seconds to ensure redirect is complete
                logger.info(
                    "Waiting 3 seconds to ensure redirect is complete...")
                time.sleep(3)
                return None

            # Extract job information
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Try to find job title - Updated for Angular components
            title_selectors = [
                '#jobPageJobTitle',  # Angular-specific ID
                'h2#jobPageJobTitle',
                'h1.job-title',
                '.job-header h1',
                '.job-details h1',
                'h1',
                'h2',
                '.title'
            ]
            title = self._extract_text_by_selectors(
                soup, title_selectors, "Unknown Title")

            # Try to find company - Updated for Angular components
            company_selectors = [
                '#jobPageOrganization_0',  # Angular-specific ID
                'p#jobPageOrganization_0',
                '.company-name',
                '.job-company',
                '.employer',
                '.company'
            ]
            company = self._extract_text_by_selectors(
                soup, company_selectors, "Unknown Company")

            # Try to find location/employment type - Updated for Angular components
            location_selectors = [
                # Angular-specific ID (employment type)
                '#jobPageJobFunction_0',
                'p#jobPageJobFunction_0',
                '.job-location',
                '.location',
                '.job-address'
            ]
            location = self._extract_text_by_selectors(
                soup, location_selectors, "Unknown Location")

            # Try to find description - Updated for Angular components
            description_selectors = [
                '#jobPageDescription',  # Angular-specific ID
                'div#jobPageDescription',
                '.job-description',
                '.description',
                '.job-content',
                '.content'
            ]
            description = self._extract_text_by_selectors(
                soup, description_selectors, "No description available")

            # Try to find requirements
            requirements_selectors = [
                '.job-requirements',
                '.requirements',
                '.job-qualifications',
                '.qualifications'
            ]
            requirements = self._extract_text_by_selectors(
                soup, requirements_selectors, "No requirements specified")

            # Try to find posted date
            date_selectors = [
                '.posted-date',
                '.job-date',
                '.publication-date'
            ]
            posted_date = self._extract_text_by_selectors(
                soup, date_selectors, "Unknown Date")

            # Try to find image
            image_selectors = [
                '.job-image img',
                '.company-logo img',
                '.job-header img'
            ]
            image_url = self._extract_image_url(soup, image_selectors)

            # Extract new fields for improved feed

            # Company logo
            company_logo_selectors = [
                '.gw-company-logo img',
                '.company-logo-position'
            ]
            company_logo_url = self._extract_image_url(
                soup, company_logo_selectors)

            # Employment type (different from job function)
            employment_type_selectors = [
                '#jobPageOrganization_2',  # Angular-specific ID for employment type
                'p#jobPageOrganization_2'
            ]
            employment_type = self._extract_text_by_selectors(
                soup, employment_type_selectors, None)

            # Industry
            industry_selectors = [
                '#jobPageJobFunction_2',  # Angular-specific ID for industry
                'p#jobPageJobFunction_2'
            ]
            industry = self._extract_text_by_selectors(
                soup, industry_selectors, None)

            # Actual location (from location text)
            actual_location_selectors = [
                '.location-address',
                '.location-icon-text'
            ]
            actual_location = self._extract_text_by_selectors(
                soup, actual_location_selectors, None)

            # Closing date
            closing_date = None
            try:
                # Look for "Closing date for applications:" text
                closing_text = soup.find(
                    text=lambda t: t and "Closing date for applications:" in t)
                if closing_text:
                    closing_date = closing_text.strip()
            except:
                pass

            # Added by information
            added_by_name = None
            added_by_company = None
            try:
                # Find the "Added by" section
                added_by_section = soup.find(
                    'h4', class_='gw-section-caption', string='Added by')
                if added_by_section:
                    parent = added_by_section.find_parent()
                    if parent:
                        # Find name
                        name_elem = parent.select_one('.gw-name')
                        if name_elem:
                            added_by_name = name_elem.get_text(strip=True)

                        # Find company description
                        desc_elem = parent.select_one('.gw-descr')
                        if desc_elem:
                            added_by_company = desc_elem.get_text(strip=True)
            except:
                pass

            job = JobPosting(
                job_id=job_id,
                title=title.strip(),
                company=company.strip(),
                location=actual_location or location.strip(),  # Use actual location if found
                # Limit description length
                description=description.strip()[:1000],
                # Limit requirements length
                requirements=requirements.strip()[:500],
                posted_date=posted_date.strip(),
                url=job_url,
                image_url=image_url,
                company_logo_url=company_logo_url,
                employment_type=employment_type,
                industry=industry,
                # Original location becomes job function
                job_function=location if actual_location else None,
                closing_date=closing_date,
                added_by_name=added_by_name,
                added_by_company=added_by_company
            )

            # Validate job is not empty (failsafe mechanism)
            if self._is_empty_job(job):
                logger.warning(
                    f"⚠️ Job {job_id} appears to be empty - stopping scraper as failsafe")
                logger.info(
                    "This may indicate a redirect that wasn't caught or incomplete page load")
                # Save current state so next run starts from this ID
                self.save_last_job_id(job_id)
                return "EMPTY_JOB_STOP"  # Special return value to signal stop

            logger.info(f"✅ Successfully scraped job {job_id}: {title}")
            return job

        except Exception as e:
            logger.error(f"❌ Error scraping job {job_id}: {e}")
            return None

    def _extract_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str], default: str) -> str:
        """Try multiple CSS selectors to extract text"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        return default

    def _extract_image_url(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Try to extract image URL"""
        for selector in selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                src = img.get('src')
                if src.startswith('http'):
                    return src
                else:
                    return urljoin(self.base_url, src)
        return None

    def _is_empty_job(self, job: JobPosting) -> bool:
        """Check if a job is effectively empty (failsafe for missed redirects)"""
        # A job is considered empty if it has no meaningful content
        empty_indicators = [
            not job.title or job.title.strip() == "" or job.title.lower() in [
                "unknown", "no title", "unknown title"],
            not job.company or job.company.strip() == "" or job.company.lower() in [
                "unknown", "unknown company", "no company"],
            not job.description or job.description.strip() == "" or job.description.lower() in [
                "no description available", "no description", "unknown description"] or len(job.description.strip()) < 20,
        ]

        # If 2 or more indicators are true, consider it empty
        return sum(empty_indicators) >= 2

    def scrape_jobs(self, max_jobs: int = 500) -> List[JobPosting]:
        """Main scraping loop"""
        if not self.login():
            logger.error("Failed to login - aborting scrape")
            return []

        start_id = self.current_job_id
        logger.info(f"Starting job scraping from ID {start_id}")

        jobs_scraped = 0

        while jobs_scraped < max_jobs:
            job = self.extract_job_data(self.current_job_id)

            if job is None:
                logger.info(
                    f"No job found at ID {self.current_job_id} - reached end of available jobs")
                logger.info("🎯 Saving progress and generating feeds...")

                # Save results immediately when we hit the first missing job
                if self.jobs_scraped:
                    self.save_results()
                    logger.info(
                        f"✅ Successfully saved {len(self.jobs_scraped)} jobs")

                    # Generate feeds
                    from generate_feeds import generate_all_feeds
                    generate_all_feeds("data/jobs_raw.json", "data")
                    logger.info("📰 Feeds generated successfully")

                break
            elif job == "EMPTY_JOB_STOP":
                logger.warning(
                    "🛑 Empty job detected - stopping as failsafe mechanism")
                logger.info("🎯 Saving progress before stopping...")

                # Save results immediately when we detect empty job
                if self.jobs_scraped:
                    self.save_results()
                    logger.info(
                        f"✅ Successfully saved {len(self.jobs_scraped)} jobs")

                    # Generate feeds
                    from generate_feeds import generate_all_feeds
                    generate_all_feeds("data/jobs_raw.json", "data")
                    logger.info("📰 Feeds generated successfully")

                break
            else:
                # Check for duplicates (EXTRA EXTRA SAFETY)
                if job.job_id in self.existing_job_ids:
                    logger.warning(
                        f"🔄 Duplicate detected: Job {job.job_id} already exists - skipping")
                else:
                    self.jobs_scraped.append(job)
                    # Add to existing IDs set to prevent duplicates within this session
                    self.existing_job_ids.add(job.job_id)
                    jobs_scraped += 1
                    logger.info(f"Jobs scraped: {jobs_scraped}")

            self.current_job_id += 1
            time.sleep(1)  # Be respectful to the server

        # Save the last processed job ID for next run
        if self.current_job_id > start_id:
            self.save_last_job_id(self.current_job_id - 1)

        logger.info(
            f"Scraping completed. Total jobs scraped: {len(self.jobs_scraped)}")
        return self.jobs_scraped

    def save_results(self, output_dir: str = "data") -> None:
        """Save scraped results to JSON and other formats"""
        os.makedirs(output_dir, exist_ok=True)

        # Save as raw JSON for feed generation
        raw_json_file = os.path.join(output_dir, "jobs_raw.json")
        with open(raw_json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(job) for job in self.jobs_scraped],
                      f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.jobs_scraped)} jobs to {raw_json_file}")

        # Save summary with state information
        start_id = self.load_last_job_id() if hasattr(self, 'initial_job_id') else 785
        summary = {
            "total_jobs": len(self.jobs_scraped),
            "session_start_job_id": start_id,
            "session_end_job_id": self.current_job_id - 1,
            "next_job_id": self.current_job_id,
            "scraped_at": datetime.now().isoformat(),
            "jobs": [{"id": job.job_id, "title": job.title, "company": job.company} for job in self.jobs_scraped]
        }

        summary_file = os.path.join(output_dir, "summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved summary to {summary_file}")

        # Generate RSS and other feeds
        try:
            from generate_feeds import generate_all_feeds
            generate_all_feeds(raw_json_file, output_dir)
        except ImportError as e:
            logger.warning(f"Could not generate feeds: {e}")
        except Exception as e:
            logger.error(f"Error generating feeds: {e}")


def main():
    """Main execution function"""
    scraper = None
    try:
        logger.info("🚀 Starting Esprit Job Scraper")

        with EspritJobScraper(headless=True) as scraper:
            jobs = scraper.scrape_jobs(max_jobs=200)

            # Results are now saved automatically when scraping completes
            if jobs:
                logger.info(
                    f"📊 Next run will start from job ID {scraper.current_job_id}")
            else:
                logger.warning("⚠️ No jobs were scraped")

    except KeyboardInterrupt:
        logger.info("🛑 Scraping interrupted by user")
        if scraper and scraper.jobs_scraped:
            logger.info(
                f"💾 Saving {len(scraper.jobs_scraped)} jobs before exit...")
            scraper.save_results()
            logger.info(
                f"✅ Successfully saved {len(scraper.jobs_scraped)} jobs")
            logger.info(
                f"📊 Next run will start from job ID {scraper.current_job_id}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Scraper failed: {e}")
        if scraper and scraper.jobs_scraped:
            logger.info(
                f"💾 Saving {len(scraper.jobs_scraped)} jobs before exit...")
            scraper.save_results()
            logger.info(
                f"✅ Successfully saved {len(scraper.jobs_scraped)} jobs")
            logger.info(
                f"📊 Next run will start from job ID {scraper.current_job_id}")
        sys.exit(1)


if __name__ == "__main__":
    main()
