# Enhanced Esprit Jobs RSS Feed

A web scraper for job postings from EspritConnect with automated testing capabilities. This repository automatically scrapes individual job postings from [EspritConnect](https://espritconnect.com/jobs) and generates comprehensive RSS and JSON feeds with images, deployed via GitHub Pages.

## 📡 Live Feeds

- **RSS Feed**: [https://thelime1.github.io/esprit-jobs/feed.xml](https://thelime1.github.io/esprit-jobs/feed.xml)
- **JSON Feed**: [https://thelime1.github.io/esprit-jobs/jobs.json](https://thelime1.github.io/esprit-jobs/jobs.json)
- **GitHub Pages**: [https://thelime1.github.io/esprit-jobs/](https://thelime1.github.io/esprit-jobs/)

## 🧪 Testing Framework

This project includes comprehensive automated testing for the EspritConnect login functionality.

### Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Credentials**:
   Create a `config/secrets.py` file with your credentials:
   ```python
   ESPRIT_EMAIL = "your.email@esprit.tn"
   ESPRIT_PASSWORD = "your_password"
   ```
   
   Alternatively, set environment variables:
   ```bash
   export ESPRIT_EMAIL="your.email@esprit.tn"
   export ESPRIT_PASSWORD="your_password"
   ```

3. **Install Firefox WebDriver**:
   Download [geckodriver](https://github.com/mozilla/geckodriver/releases) and add it to your PATH.

### Running Tests

**Run all login tests**:
```bash
python run_tests.py
```

**Run specific test**:
```bash
python run_tests.py TestEspritLogin::test_esprit_login_to_jobs
```

**Using pytest directly**:
```bash
# Run all tests
pytest tests/test_esprit_login.py -v

# Run only login tests
pytest tests/test_esprit_login.py::TestEspritLogin::test_esprit_login_to_jobs -v

# Run with detailed output
pytest tests/test_esprit_login.py -v -s
```

### Test Features

- ✅ **Secure credential management** - No hardcoded passwords
- ✅ **Explicit waits** - Better reliability than implicit waits
- ✅ **Error handling** - Screenshots on failure for debugging
- ✅ **Cookie consent handling** - Automatically handles privacy banners
- ✅ **Clean code** - Removed unnecessary mouse movements from Selenium IDE
- ✅ **Multiple test scenarios** - Valid and invalid login testing
- ✅ **Cross-platform support** - Works on Windows, macOS, and Linux

### Project Structure

```
esprit-jobs/
├── config/
│   └── secrets.py          # Credentials (git-ignored)
├── tests/
│   └── test_esprit_login.py # Login test automation
├── recording/
│   └── test_loginonetojobs.py # Original Selenium IDE export
├── requirements.txt         # Python dependencies
├── pytest.ini             # Pytest configuration
├── run_tests.py            # Test runner script
└── README.md              # This file
```

## 🔄 Automation

The scraper includes GitHub Actions automation that:
- Runs daily at 9 AM UTC 
- Scrapes jobs starting from ID 785
- Stops when it hits non-existent jobs (redirected to home page)
- Generates RSS, JSON feeds, and HTML index
- Deploys results to GitHub Pages

### Setting up GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add these repository secrets:
   - `ESPRIT_EMAIL`: Your Esprit Connect email
   - `ESPRIT_PASSWORD`: Your Esprit Connect password

### Manual Run

You can trigger the scraper manually:

```bash
# Simple run (continues from last position)
python run_scraper.py

# Custom options
python run_scraper.py --max-jobs 100 --headless

# Reset to start from job 785 again
python run_scraper.py --reset

# Test mode
python run_scraper.py --test-only
```

### State Management

Control scraper state and progress:

```bash
# View current state
python state_manager.py view

# View last scraping summary  
python state_manager.py summary

# Reset to job 785
python state_manager.py reset

# Set specific starting job ID
python state_manager.py set --job-id 850
```

## 🏗️ Project Architecture

```
esprit-jobs/
├── esprit_job_scraper.py   # Main scraper with authentication
├── generate_feeds.py       # RSS/JSON/HTML feed generator
├── test_scraper.py         # Scraper test suite
├── .github/workflows/      # GitHub Actions automation
├── output/                 # Generated feeds and data
└── config/secrets.py       # Local credentials (git-ignored)
```

## 📊 Features

### **Authenticated Scraping**
- Logs into Esprit Connect with credentials
- Handles cookie consent automatically
- Scrapes protected job pages

### **Smart Job Detection**
- **Starts from job ID 785** on first run (hardcoded)
- **Remembers last position** - continues from where it left off
- Increments through job IDs (786, 787, 788...)
- Detects non-existent jobs via redirect to home page
- Stops automatically when no more jobs found
- **State persistence** - saves progress between runs

### **Rich Data Extraction**
- Job title, company, location
- Full job description and requirements
- Posted date and images
- Direct links to original postings

### **Multiple Output Formats**
- **JSON**: Machine-readable job data
- **RSS 2.0**: Subscribe in feed readers
- **HTML**: Human-friendly web interface
- **Summary**: Quick statistics and overview

## Next Steps
1. Define your project requirements## 🔄 Automation

2. Set up the development environment

3. Implement your scraperThe scraper runs automatically:

4. Configure automation- **Every 6 hours** via GitHub Actions schedule

- **On push to main branch**

## Backup- **Manual trigger** available in GitHub Actions



Your previous work has been backed up to: `C:\Users\everp\Documents\GitHub\esprit-jobs-backup\`## 🔧 Setup

### Required GitHub Secrets

Configure these secrets in your repository settings:

- `ESPRIT_EMAIL`: Your EspritConnect email address
- `ESPRIT_PASSWORD`: Your EspritConnect password

### Enable GitHub Pages

1. Go to repository Settings
2. Navigate to Pages section
3. Set Source to "GitHub Actions"

## � Enhanced Features

### **Sequential Job Scraping**
- Scrapes individual job posts starting from ID 795
- Continues sequentially (796, 797, 798...) until no more jobs found
- Detects when redirected to feed page (indicates end of available jobs)
- Extracts detailed information from each job posting

### **Image Handling**
- Downloads and stores job images locally
- Serves images via GitHub Pages for feed consumption
- Includes images in both RSS and JSON feeds
- Optimizes image handling (skips small icons)

### **Multiple Feed Formats**
- **RSS 2.0**: Full-featured feed with images and media elements
- **JSON Feed**: Modern format following jsonfeed.org standard
- **Enhanced HTML**: Beautiful landing page with statistics

### **Rich Content Extraction**
- Job title, company, location, description
- Publication dates and metadata
- Multiple images per job posting
- Direct links to original job posts

## 🏗️ Structure

```
esprit-jobs/
├── .github/workflows/
│   └── scrape-jobs.yml      # GitHub Actions workflow
├── docs/                    # GitHub Pages output
│   ├── index.html          # Landing page
│   └── jobs.xml            # Generated XML feed
├── scraper.py              # Main scraping script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔍 XML Format

The generated XML includes:
- Job title
- Company name
- Location
- Description
- Date posted
- Direct link to job posting

## 🚀 Manual Execution

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ESPRIT_EMAIL="your-email@esprit.tn"
export ESPRIT_PASSWORD="your-password"

# Run scraper
python scraper.py
```

## 📝 License

This project is for educational and informational purposes. Please respect EspritConnect's terms of service and rate limits.