#!/usr/bin/env python3
"""
RSS and JSON feed generator for scraped Esprit jobs
"""

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring


def smart_truncate(text: str, max_length: int = 1000) -> str:
    """Truncate text at word boundary and add ellipsis if needed"""
    if len(text) <= max_length:
        return text

    # Find the last space before max_length to avoid cutting words
    last_space = text.rfind(" ", 0, max_length)
    if last_space > max_length * 0.8:  # Only use word boundary if it's not too far back
        return text[:last_space] + "..."
    else:
        return text[:max_length] + "..."


def create_rss_feed(jobs_data: List[Dict[str, Any]], output_file: str) -> None:
    """Create RSS 2.0 feed from jobs data"""

    # Create RSS root element
    rss = Element("rss", version="2.0")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

    # Create channel
    channel = SubElement(rss, "channel")

    # Channel metadata
    title = SubElement(channel, "title")
    title.text = "Esprit Connect Jobs Feed"

    link = SubElement(channel, "link")
    link.text = "https://espritconnect.com/jobs"

    description = SubElement(channel, "description")
    description.text = "Latest job postings from Esprit Connect"

    language = SubElement(channel, "language")
    language.text = "en-us"

    last_build_date = SubElement(channel, "lastBuildDate")
    last_build_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    generator = SubElement(channel, "generator")
    generator.text = "Esprit Jobs Scraper v1.0"

    # Self-reference link
    atom_link = SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", "https://thelime1.github.io/esprit-jobs/data/feed.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    # Add job items
    for job in jobs_data:
        item = SubElement(channel, "item")

        # Job title
        item_title = SubElement(item, "title")
        item_title.text = (
            f"{job.get('title', 'Unknown')} - {job.get('company', 'Unknown Company')}"
        )

        # Job URL
        item_link = SubElement(item, "link")
        item_link.text = job.get("url", "")

        # Job description with enhanced metadata
        item_description = SubElement(item, "description")

        # Build comprehensive description with company logo
        description_parts = []

        # Company logo if available
        if job.get("company_logo_url"):
            description_parts.append(
                f'<img src="{job.get("company_logo_url")}" alt="{job.get("company", "Company")} Logo" style="max-width: 200px; height: auto; margin-bottom: 10px;"/>'
            )

        description_parts.extend(
            [
                f"<p>Company: {job.get('company', 'N/A')}</p>",
                f"<p>Location: {job.get('location', 'N/A')}</p>",
            ]
        )

        # Add new metadata fields
        if job.get("employment_type"):
            description_parts.append(
                f"<p>Employment Type: {job.get('employment_type')}</p>"
            )

        if job.get("industry"):
            description_parts.append(f"<p>Industry: {job.get('industry')}</p>")

        if job.get("job_function"):
            description_parts.append(f"<p>Job Function: {job.get('job_function')}</p>")

        if job.get("closing_date"):
            # Extract just the date part from "Closing date for applications: 31/10/2025"
            closing_text = job.get("closing_date")
            if ":" in closing_text:
                date_part = closing_text.split(":", 1)[1].strip()
                description_parts.append(
                    f"<p>Closing Date: Closing date for applications: <strong>{date_part}</strong></p>"
                )
            else:
                description_parts.append(
                    f"<p>Closing Date: <strong>{closing_text}</strong></p>"
                )

        # Added by information
        if job.get("added_by_name") or job.get("added_by_company"):
            added_by_info = []
            if job.get("added_by_name"):
                added_by_info.append(f"<strong>{job.get('added_by_name')}</strong>")
            if job.get("added_by_company"):
                added_by_info.append(f"({job.get('added_by_company')})")
            description_parts.append(f"<p>Added by: {' '.join(added_by_info)}</p>")

        description_parts.extend(
            [
                "<p>Description:</p>",
                f"<p>{job.get('description', 'No description available')}</p>",
                "<p>Requirements:</p>",
                f"<p>{job.get('requirements', 'No requirements specified')}</p>",
            ]
        )

        description_text = "\n        ".join(description_parts)
        item_description.text = description_text

        # Content (full HTML)
        content = SubElement(item, "{http://purl.org/rss/1.0/modules/content/}encoded")
        content.text = description_text

        # Publication date
        pub_date = SubElement(item, "pubDate")
        try:
            scraped_date = datetime.fromisoformat(job.get("scraped_at", ""))
            pub_date.text = scraped_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        except:
            pub_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

        # Unique identifier
        guid = SubElement(item, "guid")
        guid.set("isPermaLink", "true")
        guid.text = job.get("url", f"job-{job.get('job_id', 'unknown')}")

        # Categories
        category = SubElement(item, "category")
        category.text = "Jobs"

        # Image enclosure if available (prefer company logo)
        image_url = job.get("company_logo_url") or job.get("image_url")
        if image_url:
            enclosure = SubElement(item, "enclosure")
            enclosure.set("url", image_url)
            enclosure.set("type", "image/jpeg")
            enclosure.set("length", "0")

    # Pretty print and save
    rough_string = tostring(rss, "utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

    with open(output_file, "wb") as f:
        f.write(pretty_xml)

    print(f"✅ RSS feed created: {output_file}")


def create_json_feed(jobs_data: List[Dict[str, Any]], output_file: str) -> None:
    """Create JSON feed from jobs data"""

    feed_data = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "Esprit Connect Jobs Feed",
        "home_page_url": "https://espritconnect.com/jobs",
        "feed_url": "https://thelime1.github.io/esprit-jobs/data/jobs.json",
        "description": "Latest job postings from Esprit Connect",
        "language": "en",
        "items": [],
    }

    for job in jobs_data:
        # Build comprehensive content HTML with company logo
        content_parts = []

        # Company logo if available
        if job.get("company_logo_url"):
            content_parts.append(
                f'<img src="{job.get("company_logo_url")}" alt="{job.get("company", "Company")} Logo" style="max-width: 200px; height: auto; margin-bottom: 10px;"/>'
            )

        content_parts.extend(
            [
                f"<p>Company: {job.get('company', 'N/A')}</p>",
                f"<p>Location: {job.get('location', 'N/A')}</p>",
            ]
        )

        # Add new metadata fields
        if job.get("employment_type"):
            content_parts.append(
                f"<p>Employment Type: {job.get('employment_type')}</p>"
            )

        if job.get("industry"):
            content_parts.append(f"<p>Industry: {job.get('industry')}</p>")

        if job.get("job_function"):
            content_parts.append(f"<p>Job Function: {job.get('job_function')}</p>")

        if job.get("closing_date"):
            # Extract just the date part from "Closing date for applications: 31/10/2025"
            closing_text = job.get("closing_date")
            if ":" in closing_text:
                date_part = closing_text.split(":", 1)[1].strip()
                content_parts.append(
                    f"<p>Closing Date: Closing date for applications: <strong>{date_part}</strong></p>"
                )
            else:
                content_parts.append(
                    f"<p>Closing Date: <strong>{closing_text}</strong></p>"
                )

        # Added by information
        if job.get("added_by_name") or job.get("added_by_company"):
            added_by_info = []
            if job.get("added_by_name"):
                added_by_info.append(f"<strong>{job.get('added_by_name')}</strong>")
            if job.get("added_by_company"):
                added_by_info.append(f"({job.get('added_by_company')})")
            content_parts.append(f"<p>Added by: {' '.join(added_by_info)}</p>")

        content_parts.extend(
            [
                "<p>Description:</p>",
                f"<p>{job.get('description', 'No description available')}</p>",
                "<p>Requirements:</p>",
                f"<p>{job.get('requirements', 'No requirements specified')}</p>",
            ]
        )

        content_html = "\n            ".join(content_parts)

        # Create summary with target of 1000 characters (no truncation)
        description = job.get("description", "")
        requirements = job.get("requirements", "")

        # Combine description and requirements to try to reach 1000 chars
        combined_text = description
        if (
            len(combined_text) < 1000
            and requirements
            and requirements != "No requirements specified"
        ):
            combined_text += f"\n\nRequirements: {requirements}"

        # Use all available content, aim for 1000 but don't cut words
        if len(combined_text) <= 1000:
            summary = combined_text  # Use all content if 1000 chars or less
        else:
            summary = smart_truncate(combined_text, 1000)

        item = {
            "id": str(job.get("job_id", "")),
            "url": job.get("url", ""),
            "title": f"{job.get('title', 'Unknown')} - {job.get('company', 'Unknown Company')}",
            "content_html": content_html,
            "summary": summary,
            "date_published": job.get("scraped_at", ""),
            "tags": ["jobs", "esprit", job.get("company", "").lower()],
            "external_url": job.get("url", ""),
        }

        # Prefer company logo, fallback to job image
        if job.get("company_logo_url"):
            item["image"] = job["company_logo_url"]
        elif job.get("image_url"):
            item["image"] = job["image_url"]

        feed_data["items"].append(item)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(feed_data, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON feed created: {output_file}")


def _extract_closing_date(raw: str) -> str:
    """Extract DD/MM/YYYY from a scraper closing-date string."""
    if not raw:
        return ""
    match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", raw)
    return match.group(0) if match else raw.strip()


def _parse_closing_date(value: str) -> Optional[datetime]:
    try:
        return datetime.strptime(value, "%d/%m/%Y")
    except Exception:
        return None


def _is_closed(closing_date: str) -> bool:
    parsed = _parse_closing_date(closing_date)
    if parsed is None:
        return False
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return parsed < today


def _classify_job_type(job: Dict[str, Any]) -> str:
    haystack = " ".join(
        str(job.get(key, ""))
        for key in ("title", "employment_type", "job_function", "location", "industry")
    ).lower()

    if "internship" in haystack or "stage" in haystack or "pfe" in haystack:
        return "Internship"
    if "contract" in haystack or "cdd" in haystack:
        return "Contract"
    if "permanent" in haystack or "full-time" in haystack or "emploi" in haystack:
        return "Permanent"
    return "Job"


def create_portal_internships_json(
    jobs_data: List[Dict[str, Any]], output_file: str
) -> None:
    """Create a lightweight JSON payload consumed directly by esprit-portal-v2."""
    items = []

    for job in jobs_data:
        closing_date = _extract_closing_date(str(job.get("closing_date", "")))
        if _is_closed(closing_date):
            continue

        description = str(job.get("description", "") or "").strip()
        item = {
            "id": str(job.get("job_id", "")),
            "title": str(job.get("title", "Unknown")).strip(),
            "company": str(job.get("company", "")).strip(),
            "location": str(job.get("location", "")).strip(),
            "type": _classify_job_type(job),
            "closingDate": closing_date,
            "link": str(job.get("url", "")).strip(),
            "description": smart_truncate(description, 300),
            "imageUrl": str(
                job.get("company_logo_url") or job.get("image_url") or ""
            ).strip(),
            "pubDate": str(job.get("scraped_at", "")).strip(),
            "addedBy": str(
                job.get("added_by_name") or job.get("added_by_company") or ""
            ).strip(),
        }
        items.append(item)

    payload = {
        "success": True,
        "items": items,
        "total": len(items),
        "lastUpdated": datetime.now().isoformat(),
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"✅ Portal internships JSON created: {output_file}")


def create_html_index(jobs_data: List[Dict[str, Any]], output_file: str) -> None:
    """Create HTML index page for the jobs"""

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Esprit Connect Jobs</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .feeds {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .feeds a {{
            display: inline-block;
            margin: 0 10px;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }}
        .job-card {{
            background: white;
            margin-bottom: 20px;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }}
        .job-title {{
            color: #333;
            margin-bottom: 10px;
            margin-right: 160px; /* Make space for logo */
        }}
        .job-meta {{
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
            line-height: 1.8;
            margin-right: 160px; /* Make space for logo */
        }}
        .job-description {{
            color: #333;
            line-height: 1.6;
            margin-right: 160px; /* Make space for logo */
        }}
        .stats {{
            text-align: center;
            margin-bottom: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Esprit Connect Jobs</h1>
        <p>Automatically scraped job postings from Esprit Connect</p>
        <p>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}</p>
    </div>

    <div class="stats">
        <p><strong>Total Jobs Found:</strong> {len(jobs_data)}</p>
    </div>

    <div class="feeds">
        <a href="feed.xml">📡 RSS Feed</a>
        <a href="jobs.json">📄 JSON Feed</a>
        <a href="summary.json">📊 Summary</a>
    </div>

    <div class="jobs">
"""

    for job in jobs_data:
        # Build enhanced job card with company logo and all metadata
        job_meta_parts = []

        # Company logo if available
        logo_html = ""
        if job.get("company_logo_url"):
            logo_html = f'<img src="{job.get("company_logo_url")}" alt="{job.get("company", "Company")} Logo" style="max-width: 150px; height: auto; float: right; margin-left: 15px; border-radius: 4px;"/>'

        # Build comprehensive metadata
        job_meta_parts.append(f"Company: {job.get('company', 'Unknown')}")
        job_meta_parts.append(f"Location: {job.get('location', 'Unknown')}")

        if job.get("employment_type"):
            job_meta_parts.append(f"Employment Type: {job.get('employment_type')}")

        if job.get("industry"):
            job_meta_parts.append(f"Industry: {job.get('industry')}")

        if job.get("job_function"):
            job_meta_parts.append(f"Job Function: {job.get('job_function')}")

        if job.get("closing_date"):
            # Extract just the date part from "Closing date for applications: 31/10/2025"
            closing_text = job.get("closing_date")
            if ":" in closing_text:
                date_part = closing_text.split(":", 1)[1].strip()
                job_meta_parts.append(
                    f"Closing Date: Closing date for applications: <strong>{date_part}</strong>"
                )
            else:
                job_meta_parts.append(f"Closing Date: <strong>{closing_text}</strong>")

        # Added by information
        if job.get("added_by_name") or job.get("added_by_company"):
            added_by_info = []
            if job.get("added_by_name"):
                added_by_info.append(f"<strong>{job.get('added_by_name')}</strong>")
            if job.get("added_by_company"):
                added_by_info.append(f"({job.get('added_by_company')})")
            job_meta_parts.append(f"Added by: {' '.join(added_by_info)}")

        job_meta_html = " | ".join(job_meta_parts)
        job_url = job.get("url", "#")
        job_title = job.get("title", "Unknown Title")
        job_description = smart_truncate(
            job.get("description", "No description available"),
            1000,
        )

        html_content += f"""
        <div class="job-card">
            {logo_html}
            <h2 class="job-title">
                <a href="{job_url}" target="_blank">
                    {job_title}
                </a>
            </h2>
            <div class="job-meta">
                {job_meta_html}
            </div>
            <div class="job-description">
                <p>{job_description}</p>
            </div>
            <div style="clear: both;"></div>
        </div>
"""

    html_content += """
    </div>

    <footer style="text-align: center; margin-top: 40px; color: #666;">
        <p>Generated by Esprit Jobs Scraper |
        <a href="https://github.com/thelime1/esprit-jobs">GitHub</a></p>
    </footer>
</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ HTML index created: {output_file}")


def generate_all_feeds(json_file: str, output_dir: str) -> None:
    """Generate all feed formats from jobs JSON file"""

    if not os.path.exists(json_file):
        print(f"❌ Jobs file not found: {json_file}")
        return

    # Load jobs data
    with open(json_file, "r", encoding="utf-8") as f:
        jobs_data = json.load(f)

    # Sort jobs by job_id in descending order (newest first)
    jobs_data.sort(key=lambda job: job.get("job_id", 0), reverse=True)

    print(f"📊 Generating feeds for {len(jobs_data)} jobs...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate feeds
    create_rss_feed(jobs_data, os.path.join(output_dir, "feed.xml"))
    create_json_feed(jobs_data, os.path.join(output_dir, "jobs.json"))
    create_portal_internships_json(
        jobs_data, os.path.join(output_dir, "internships.json")
    )
    create_html_index(jobs_data, os.path.join(output_dir, "index.html"))

    print("🎉 All feeds generated successfully!")


if __name__ == "__main__":
    # Generate feeds from default location
    input_file = "data/jobs_raw.json"
    output_dir = "data"

    if os.path.exists(input_file):
        generate_all_feeds(input_file, output_dir)
    else:
        print(f"❌ No jobs file found at {input_file}")
        print("Run the scraper first: python esprit_job_scraper.py")
