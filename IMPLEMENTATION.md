# 🎉 Esprit Jobs Scraper - Complete Implementation

## ✅ What's Been Built

I've created a complete authenticated job scraper for Esprit Connect that:

### 🔐 **Authentication System**
- Logs into Esprit Connect with your credentials
- Handles cookie consent automatically
- Supports both local config files and GitHub secrets

### 🕷️ **Smart Scraping Engine**
- Starts from job ID 785 as requested
- Increments through jobs (786, 787, 788...)
- **Automatically detects when jobs don't exist** (redirect to home page)
- Stops scraping when hitting the redirect threshold
- Extracts: title, company, location, description, requirements, dates, images

### 📊 **Multiple Output Formats**
- **JSON** - Machine-readable job data
- **RSS 2.0** - Subscribe in feed readers  
- **HTML** - Beautiful web interface
- **Summary** - Quick statistics

### 🤖 **GitHub Actions Automation**
- Runs daily at 9 AM UTC
- Uses GitHub secrets for credentials
- Automatically deploys to GitHub Pages
- Artifact storage for debugging

## 🚀 Quick Start

### 1. Set up credentials (choose one):

**Option A: Local config (development)**
```python
# config/secrets.py
ESPRIT_EMAIL = "your.email@esprit.tn"
ESPRIT_PASSWORD = "your_password"
```

**Option B: GitHub Secrets (production)**
- Go to Settings → Secrets → Actions
- Add `ESPRIT_EMAIL` and `ESPRIT_PASSWORD`

### 2. Run the scraper:
```bash
# Simple run
python run_scraper.py

# Custom options
python run_scraper.py --start-id 785 --max-jobs 100 --headless

# Test mode
python run_scraper.py --test-only
```

### 3. View results:
- `output/jobs.json` - Raw job data
- `output/feed.xml` - RSS feed
- `output/index.html` - Web interface

## 📁 Files Created

| File                                | Purpose                          |
| ----------------------------------- | -------------------------------- |
| `esprit_job_scraper.py`             | Main scraper with authentication |
| `generate_feeds.py`                 | RSS/JSON/HTML feed generator     |
| `run_scraper.py`                    | Complete workflow runner         |
| `test_scraper.py`                   | Test suite                       |
| `.github/workflows/scrape-jobs.yml` | GitHub Actions automation        |

## 🎯 Key Features

✅ **Stops at non-existent jobs** - Detects redirect to home page  
✅ **GitHub secrets integration** - Secure credential management  
✅ **Automated daily runs** - Set and forget operation  
✅ **Multiple output formats** - RSS, JSON, HTML  
✅ **Error handling** - Screenshots on failure, logging  
✅ **Respectful scraping** - Delays between requests  

## 🔄 How it Works

1. **Authentication**: Logs into Esprit Connect using your credentials
2. **Job Discovery**: Starts at job ID 785, increments through IDs
3. **Termination Detection**: Stops when jobs redirect to home page (`/feed`)
4. **Data Extraction**: Pulls job details, company info, requirements
5. **Feed Generation**: Creates RSS, JSON, and HTML outputs
6. **Deployment**: GitHub Actions pushes to GitHub Pages

This is exactly what you requested - an authenticated scraper that starts at job 785 and stops when it hits non-existent jobs! 🎉