# EspritConnect Jobs Scraper# Enhanced Esprit Jobs RSS Feed



A web scraper for job postings from EspritConnect.This repository automatically scrapes individual job postings from [EspritConnect](https://espritconnect.com/jobs) and generates comprehensive RSS and JSON feeds with images, deployed via GitHub Pages.



## Getting Started## 📡 Live Feeds



This repository has been reset and is ready for a fresh start.- **RSS Feed**: [https://thelime1.github.io/esprit-jobs/feed.xml](https://thelime1.github.io/esprit-jobs/feed.xml)

- **JSON Feed**: [https://thelime1.github.io/esprit-jobs/jobs.json](https://thelime1.github.io/esprit-jobs/jobs.json)

## Next Steps- **GitHub Pages**: [https://thelime1.github.io/esprit-jobs/](https://thelime1.github.io/esprit-jobs/)



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