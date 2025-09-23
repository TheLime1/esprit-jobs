# Esprit Jobs RSS Feed

An automated web scraper for job postings from EspritConnect that generates RSS feeds and JSON data, deployed via GitHub Pages.

## 📡 Live Feeds

- **RSS Feed**: [https://thelime1.github.io/esprit-jobs/data/feed.xml](https://thelime1.github.io/esprit-jobs/data/feed.xml)
- **JSON Feed**: [https://thelime1.github.io/esprit-jobs/data/jobs.json](https://thelime1.github.io/esprit-jobs/data/jobs.json)
- **Web Interface**: [https://thelime1.github.io/esprit-jobs/data/](https://thelime1.github.io/esprit-jobs/data/)

## 🚀 Features

### **Authenticated Scraping**
- Secure login to EspritConnect using credentials
- Automatic cookie consent handling
- Access to protected job listings

### **Smart Job Detection**
- Sequential job ID scanning starting from job 795
- Automatic detection of non-existent jobs via redirect
- State persistence - remembers last scraped position
- Duplicate prevention with safety checks

### **Rich Data Extraction**
- Complete job details: title, company, location, description
- Requirements, employment type, industry information
- Posted dates, closing dates, and contact information
- Company logos and job images
- Direct links to original postings

### **Multiple Output Formats**
- **RSS 2.0**: Full-featured feed with images and metadata
- **JSON**: Structured data for API consumption
- **HTML**: Human-friendly web interface with statistics

## ⚙️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

**For local development**, create `config/secrets.py`:
```python
ESPRIT_EMAIL = "your.email@esprit.tn"
ESPRIT_PASSWORD = "your_password"
```

**For GitHub Actions**, add repository secrets:
1. Go to Settings → Secrets and variables → Actions
2. Add `ESPRIT_EMAIL` and `ESPRIT_PASSWORD`

### 3. Browser Requirements

The scraper uses **Chrome with Selenium 4.15+** which automatically manages ChromeDriver - no manual driver installation needed!

## 🎯 Usage

### Local Testing

```bash
# Run the main scraper
python esprit_job_scraper.py

# Run with the complete workflow
python run_scraper.py

# Generate feeds from existing data
python generate_feeds.py
```

### Automated Runs

The scraper runs automatically via GitHub Actions:
- **Daily at 9 AM UTC**
- **On code changes to main branch**
- **Manual trigger available**

Results are automatically deployed to GitHub Pages.

## 🏗️ Project Structure

```
esprit-jobs/
├── esprit_job_scraper.py    # Main scraper with authentication
├── generate_feeds.py        # RSS/JSON/HTML generator
├── run_scraper.py           # Complete workflow runner
├── scraper_state.json       # Persistent state tracking
├── config/
│   ├── secrets.py          # Local credentials (git-ignored)
│   └── secrets_template.py # Template for credentials
├── data/                   # Generated output files
│   ├── jobs.json          # Structured job data
│   ├── jobs_raw.json      # Raw scraped data
│   ├── feed.xml           # RSS 2.0 feed
│   ├── index.html         # Web interface
│   └── summary.json       # Scraping statistics
├── .github/workflows/
│   └── scrape-jobs.yml    # GitHub Actions automation
└── requirements.txt       # Python dependencies
```

## 🔄 How It Works

1. **Authentication**: Logs into EspritConnect using provided credentials
2. **Job Discovery**: Scans job IDs sequentially starting from last position
3. **Data Extraction**: Extracts comprehensive job information including images
4. **Duplicate Detection**: Skips already-scraped jobs for efficiency
5. **Feed Generation**: Creates RSS, JSON, and HTML outputs
6. **State Management**: Saves progress for next run
7. **Deployment**: GitHub Actions publishes to GitHub Pages

## 🛠️ Technical Details

- **Language**: Python 3.11+
- **Web Driver**: Chrome with Selenium 4.15+ (auto-managed drivers)
- **Dependencies**: Selenium, BeautifulSoup4, Requests, LXML
- **Deployment**: GitHub Actions → GitHub Pages
- **State Persistence**: JSON-based state tracking
- **Error Handling**: Comprehensive logging and screenshot capture

## 📊 Output Data Structure

### RSS Feed
Standard RSS 2.0 format with:
- Job titles and descriptions
- Company information and locations
- Publication dates and links
- Embedded images and media

### JSON Feed
Structured job data including:
```json
{
  "job_id": 803,
  "title": "Software Developer",
  "company": "TechCorp",
  "location": "Tunis, Tunisia",
  "description": "Full job description...",
  "requirements": "Required skills...",
  "posted_date": "2025-09-20",
  "url": "https://espritconnect.com/jobs/803",
  "employment_type": "Full-time",
  "industry": "Technology"
}
```

## 🔐 Security

- Credentials stored securely in GitHub Secrets
- No hardcoded passwords in source code
- Environment variable fallback for local development
- Git-ignored local configuration files

## 📝 License

This project is for educational and informational purposes. Please respect EspritConnect's terms of service and implement appropriate rate limiting.