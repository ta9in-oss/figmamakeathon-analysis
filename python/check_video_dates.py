#!/usr/bin/env python3
"""Analyze winner video upload dates vs challenge start dates.

Checks the PRD's hypothesis: did winners start working before the challenge?
Extracts video links from winner project pages, fetches upload dates,
and compares against edition start dates.
"""

import re
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import httpx
from playwright.sync_api import sync_playwright

from src.config import EDITIONS

OUTPUT_DIR = Path("output")


@dataclass
class VideoAnalysis:
    project_name: str
    creator: str
    edition: str
    edition_start: datetime
    project_url: str
    video_url: Optional[str] = None
    video_platform: str = ""
    video_upload_date: Optional[datetime] = None
    days_before_start: Optional[int] = None
    started_before: Optional[bool] = None
    notes: str = ""


def extract_video_from_page(project_url: str, headless: bool = True) -> list[dict]:
    """Use Playwright to find video embeds on a project page."""
    videos = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ))
        page = ctx.new_page()
        page.set_default_timeout(30_000)

        try:
            print(f"  Visiting {project_url}")
            page.goto(project_url, wait_until="networkidle", timeout=20_000)
            time.sleep(3)  # Let JS finish rendering

            # Look for video elements
            for selector in ["video", "iframe[src*='youtube']", "iframe[src*='vimeo']",
                             "iframe[src*='loom']", "iframe[src*='embed']",
                             "a[href*='youtube.com']", "a[href*='youtu.be']",
                             "a[href*='vimeo.com']", "a[href*='loom.com']"]:
                elements = page.query_selector_all(selector)
                for el in elements:
                    if selector.startswith("iframe"):
                        src = el.get_attribute("src") or ""
                    elif selector.startswith("video"):
                        src_el = el.query_selector("source")
                        src = src_el.get_attribute("src") if src_el else ""
                    else:
                        src = el.get_attribute("href") or ""
                    if src and ("youtube" in src or "youtu.be" in src or
                               "vimeo" in src or "loom" in src):
                        videos.append({"url": src, "type": "embed"})

            # Check for video element with poster
            video_els = page.query_selector_all("video")
            for el in video_els:
                poster = el.get_attribute("poster")
                if poster:
                    videos.append({"url": poster, "type": "poster"})

            # Scan page HTML for video URLs
            html = page.content()
            yt_patterns = [
                r'(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+)',
                r'(https?://youtu\.be/[\w-]+)',
                r'(https?://(?:www\.)?youtube\.com/embed/[\w-]+)',
            ]
            for pattern in yt_patterns:
                for match in re.finditer(pattern, html):
                    videos.append({"url": match.group(1), "type": "html"})

            vimeo_pattern = r'(https?://(?:player\.)?vimeo\.com/(?:video/)?[\d]+)'
            for match in re.finditer(vimeo_pattern, html):
                videos.append({"url": match.group(1), "type": "html"})

            loom_pattern = r'(https?://(?:www\.)?loom\.com/share/[\w-]+)'
            for match in re.finditer(loom_pattern, html):
                videos.append({"url": match.group(1), "type": "html"})

        except Exception as e:
            print(f"    Error: {e}")
        finally:
            browser.close()

    # Deduplicate
    seen = set()
    unique = []
    for v in videos:
        if v["url"] not in seen:
            seen.add(v["url"])
            unique.append(v)
    return unique


def fetch_youtube_upload_date(video_url: str) -> Optional[datetime]:
    """Fetch YouTube video upload date via oEmbed and page metadata."""
    video_id = None
    # Extract video ID
    for pattern in [
        r'(?:v=|/embed/|youtu\.be/)([\w-]{11})',
        r'youtube\.com/watch\?v=([\w-]{11})',
    ]:
        m = re.search(pattern, video_url)
        if m:
            video_id = m.group(1)
            break

    if not video_id:
        return None

    # Try oEmbed first
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        resp = httpx.get(oembed_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # oEmbed includes author info but NOT upload date directly
            # We need the page for that
    except Exception:
        pass

    # Try page scraping for meta tags
    try:
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        resp = httpx.get(watch_url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)",
        })
        if resp.status_code == 200:
            # Search for uploadDate in meta/JSON-LD
            html = resp.text
            # Pattern 1: JSON-LD
            json_match = re.search(
                r'"uploadDate"\s*:\s*"([^"]+)"',
                html,
            )
            if json_match:
                try:
                    return datetime.fromisoformat(json_match.group(1))
                except ValueError:
                    pass

            # Pattern 2: meta tag
            meta_match = re.search(
                r'<meta\s+itemprop="uploadDate"\s+content="([^"]+)"',
                html,
            )
            if meta_match:
                try:
                    return datetime.fromisoformat(meta_match.group(1))
                except ValueError:
                    pass

            # Pattern 3: dateText in ytInitialData
            date_match = re.search(r'"dateText"\s*:\s*\{\s*"simpleText"\s*:\s*"([^"]+)"', html)
            if date_match:
                date_str = date_match.group(1)
                print(f"    Found dateText: {date_str}")
                # e.g., "Premiered Jun 5, 2026" or "Jun 5, 2026"
                try:
                    for fmt in ["Premiered %b %d, %Y", "%b %d, %Y", "%B %d, %Y"]:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    pass

    except Exception as e:
        print(f"    Error fetching YouTube page: {e}")

    return None


def fetch_vimeo_upload_date(video_url: str) -> Optional[datetime]:
    """Fetch Vimeo video upload date via oEmbed or API."""
    video_id = None
    m = re.search(r'vimeo\.com/(?:video/)?(\d+)', video_url)
    if m:
        video_id = m.group(1)

    if not video_id:
        return None

    try:
        oembed_url = f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{video_id}"
        resp = httpx.get(oembed_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if "upload_date" in data:
                return datetime.fromisoformat(data["upload_date"])
    except Exception:
        pass

    return None


def main():
    print("=" * 70)
    print("  VIDEO UPLOAD DATE ANALYSIS")
    print("  Checking if winners started before the challenge")
    print("=" * 70)

    # ── Strategy 1: Search X/Twitter for winner posts with #figmamakeathon hashtags ──
    print("\n── Strategy 1: Searching social media for winner video posts ──\n")

    # Known winner search queries for X/Twitter
    winner_queries = [
        ("Common Thread", "Charlota Blunárová", "Figma Makeathon March 2026",
         "Common Thread OR Charlota Blunárová #figmamakeathonmarch2026"),
        ("TOKYO", "Kiel Cole", "Figma Makeathon March 2026",
         "TOKYO OR Kiel Cole #figmamakeathonmarch2026"),
        ("Pucker", "Aleyna Çatak", "Figma Makeathon March 2026",
         "Pucker OR Aleyna Çatak #figmamakeathonmarch2026"),
        ("Airwwave", "Lee Black", "Figma Makeathon March 2026",
         "Airwwave OR Lee Black #figmamakeathonmarch2026"),
        ("Duet Booth", "Paige Latimer", "Figma Makeathon March 2026",
         "Duet Booth OR Paige Latimer #figmamakeathonmarch2026"),
        ("Reframe It", "Dann Petty", "Figma Makeathon March 2026",
         "Reframe It OR Dann Petty #figmamakeathonmarch2026"),
        ("Web Poetry", "Cara Ellis", "Figma Make-a-thon (Sep 2025)",
         "Web Poetry OR Cara Ellis #figmamakeathon"),
        ("Plan That Trip. Now", "Johannes Specht", "Figma Make-a-thon (Sep 2025)",
         "Plan That Trip OR Johannes Specht #figmamakeathon"),
        ("Package Customizer", "Daniella Marynova", "Figma Make-a-thon (Sep 2025)",
         "Package Customizer OR Daniella Marynova OR Max Pradella #figmamakeathon"),
    ]

    edition_map = {e.name: e for e in EDITIONS}
    results: list[VideoAnalysis] = []

    # ── Strategy 2: Scrape Contra topic pages for winner submission posts ──
    print("\n── Strategy 2: Finding winner submission posts on Contra ──\n")
    winner_posts = find_winner_contra_posts()

    # ── Strategy 3: Try X/Twitter search via nitter or direct ──
    print("\n── Strategy 3: Checking X/Twitter for videos ──\n")
    for name, creator, edition_name, query in winner_queries:
        print(f"  Searching X for: {name} by {creator}")

        edition = edition_map.get(edition_name)
        start_date = edition.start_date if edition else datetime.now()
        analysis = VideoAnalysis(
            project_name=name, creator=creator,
            edition=edition_name, edition_start=start_date,
            project_url="",
        )

        # Try to find X posts with videos
        x_videos = search_x_for_videos(name, creator)
        if x_videos:
            analysis.video_url = x_videos[0]["url"]
            analysis.video_platform = "X/Twitter"
            analysis.notes = f"Found {len(x_videos)} X post(s) with video"
            # X video upload date is the post date
            if x_videos[0].get("date"):
                try:
                    analysis.video_upload_date = x_videos[0]["date"]
                    analysis.days_before_start = (start_date - x_videos[0]["date"]).days
                    analysis.started_before = analysis.days_before_start > 0
                    analysis.notes += f" — posted {analysis.days_before_start} days relative to start"
                except Exception:
                    pass
            print(f"    → {analysis.notes}")
        else:
            analysis.notes = "No video posts found on X"
            print(f"    → No videos found")

        results.append(analysis)
        time.sleep(1)

    # ── Strategy 4: Check known Contra winner posts for video links ──
    print("\n── Strategy 4: Scraping Contra winner posts for embeds ──\n")
    contra_results = scrape_contra_winner_posts_for_videos(winner_posts, edition_map)
    results.extend(contra_results)

    # ── Strategy 5: Search directly on YouTube ──
    print("\n── Strategy 5: Direct YouTube search for winner projects ──\n")
    for name, creator, edition_name, _ in winner_queries:
        edition = edition_map.get(edition_name)
        start_date = edition.start_date if edition else datetime.now()

        yt_url = search_youtube_for_project(name, creator)
        if yt_url:
            upload_date = fetch_youtube_upload_date(yt_url)
            analysis = VideoAnalysis(
                project_name=name, creator=creator,
                edition=edition_name, edition_start=start_date,
                project_url=yt_url, video_url=yt_url,
                video_platform="YouTube",
                video_upload_date=upload_date,
            )
            if upload_date:
                # Normalize timezone for comparison
                if hasattr(upload_date, 'tzinfo') and upload_date.tzinfo is not None:
                    upload_date = upload_date.replace(tzinfo=None)
                analysis.days_before_start = (start_date - upload_date).days
                analysis.started_before = analysis.days_before_start > 0
                if analysis.started_before:
                    analysis.notes = f"YouTube video uploaded {analysis.days_before_start} days BEFORE challenge start"
                else:
                    analysis.notes = f"YouTube video uploaded {-analysis.days_before_start} days AFTER challenge start"
                print(f"  {name}: {analysis.notes}")
            else:
                analysis.notes = f"YouTube video found but upload date not extracted"
                print(f"  {name}: video found, date unknown")
            results.append(analysis)
        else:
            print(f"  {name}: not found on YouTube")

    # ── Print summary ──────────────────────────────────────────────────
    print_summary_table(results)


def find_winner_contra_posts() -> dict:
    """Try to find the actual Contra submission posts for winners."""
    # These are known or guessed Contra post URLs based on the topic pages
    # The topic URLs typically have individual post pages we need to discover
    return {
        "Common Thread": None,
        "TOKYO": None,
        "Pucker": None,
        "Airwwave": None,
        "Duet Booth": None,
        "Reframe It": None,
    }


def scrape_contra_winner_posts_for_videos(
    winner_posts: dict,
    edition_map: dict,
) -> list[VideoAnalysis]:
    """For each winner with a known Contra post, scrape for video embeds."""
    results = []
    # Contra posts likely contain embedded YouTube/Vimeo iframes
    # or links to social media posts with videos
    for name, post_url in winner_posts.items():
        if not post_url:
            continue
        print(f"  Checking Contra post for {name}")
        videos = extract_video_from_page(post_url, headless=True)
        if videos:
            for v in videos:
                print(f"    Found video: {v['url']}")
                # Try to get upload date
                upload_date = None
                if "youtube" in v["url"] or "youtu.be" in v["url"]:
                    upload_date = fetch_youtube_upload_date(v["url"])
                elif "vimeo" in v["url"]:
                    upload_date = fetch_vimeo_upload_date(v["url"])
                if upload_date:
                    print(f"    Upload date: {upload_date.date()}")
    return results


def search_x_for_videos(name: str, creator: str) -> list[dict]:
    """Search X/Twitter for posts with videos from a winner."""
    # X API requires authentication. Try nitter or public search as fallback.
    # For now, use httpx to hit nitter.net search
    import urllib.parse
    query = f"{name} {creator}"
    encoded = urllib.parse.quote(query)

    for nitter_instance in [
        "https://nitter.net",
        "https://nitter.poast.org",
    ]:
        try:
            url = f"{nitter_instance}/search?f=tweets&q={encoded}"
            resp = httpx.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)",
            })
            if resp.status_code == 200 and "video" in resp.text.lower():
                # Extract video URLs from the search results page
                videos = []
                # Look for tweet links and video indicators
                vid_matches = re.findall(
                    r'(https?://video\.twimg\.com/[^\s"<>]+)',
                    resp.text,
                )
                for vm in vid_matches:
                    videos.append({"url": vm})
                if videos:
                    return videos
        except Exception:
            continue

    return []


def search_youtube_for_project(name: str, creator: str) -> Optional[str]:
    """Search YouTube for a project/creator and return the most relevant video URL."""
    import urllib.parse
    query = f"{name} {creator} figma makeathon"
    encoded = urllib.parse.quote(query)

    try:
        # Use YouTube search page
        url = f"https://www.youtube.com/results?search_query={encoded}"
        resp = httpx.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        if resp.status_code == 200:
            # Extract first video ID from search results
            match = re.search(r'"/watch\?v=([\w-]{11})"', resp.text)
            if match:
                return f"https://www.youtube.com/watch?v={match.group(1)}"
    except Exception:
        pass

    return None


def print_summary_table(results: list[VideoAnalysis]):
    """Print formatted summary table."""
    print(f"\n{'='*70}")
    print("  VIDEO UPLOAD DATE ANALYSIS — FINAL SUMMARY")
    print(f"{'='*70}")

    before = [r for r in results if r.started_before is True]
    during = [r for r in results if r.started_before is False]
    unknown = [r for r in results if r.started_before is None]

    if before:
        print(f"\n  ⚠️  Started BEFORE challenge ({len(before)}):")
        for r in before:
            print(f"    • {r.project_name} ({r.creator})")
            print(f"      Uploaded {r.days_before_start} days before {r.edition_start.date()}")
            print(f"      {r.video_url}")

    if during:
        print(f"\n  ✅ Started DURING challenge ({len(during)}):")
        for r in during:
            print(f"    • {r.project_name} ({r.creator}) — {r.notes}")

    if unknown:
        print(f"\n  ❓ Could not determine ({len(unknown)}):")
        for r in unknown:
            print(f"    • {r.project_name} ({r.creator})")

    # Save
    OUTPUT_DIR.mkdir(exist_ok=True)
    import csv
    csv_path = OUTPUT_DIR / "video_analysis.csv"
    fieldnames = [
        "project_name", "creator", "edition", "edition_start",
        "project_url", "video_url", "video_platform",
        "video_upload_date", "days_before_start", "started_before", "notes",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "project_name": r.project_name, "creator": r.creator,
                "edition": r.edition, "edition_start": r.edition_start.isoformat()[:10],
                "project_url": r.project_url, "video_url": r.video_url or "",
                "video_platform": r.video_platform,
                "video_upload_date": r.video_upload_date.isoformat()[:10] if r.video_upload_date else "",
                "days_before_start": r.days_before_start if r.days_before_start is not None else "",
                "started_before": r.started_before if r.started_before is not None else "",
                "notes": r.notes,
            })

    print(f"\n  Results saved to {csv_path}")


if __name__ == "__main__":
    main()
