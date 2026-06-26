#!/usr/bin/env python3
"""
Scrape all Contra makeathon entries via GraphQL API interception.

Uses Playwright to navigate each topic page, intercepts SocialPosts API
responses, and collects complete post data including likes, comments, and author.
"""

import json
import time
import re
import csv
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from playwright.sync_api import sync_playwright, Route, Request


# ── Edition config ──────────────────────────────────────────────────────────

EDITIONS = [
    {
        "name": "Figma Make-a-thon (Sep 2025)",
        "slug": "figmamakeathon",
        "url": "https://contra.com/community/topic/figmamakeathon",
        "start": datetime(2025, 9, 3, tzinfo=timezone.utc),
        "end": datetime(2025, 9, 10, tzinfo=timezone.utc),
        "winners": [
            {"project": "web poetry", "creator": "cara ellis", "place": "1st ($50K)"},
            {"project": "plan that trip", "creator": "johannes specht", "place": "3rd ($7.5K)"},
            {"project": "package customizer", "creator": "daniella marynova", "place": "Most Innovative"},
            {"project": "package customizer", "creator": "max pradella", "place": "Most Innovative"},
        ],
    },
    {
        "name": "Figma Makeathon March 2026",
        "slug": "figmamakeathonmarch2026",
        "url": "https://contra.com/community/topic/figmamakeathonmarch2026",
        "start": datetime(2026, 2, 1, tzinfo=timezone.utc),
        "end": datetime(2026, 3, 16, tzinfo=timezone.utc),
        "winners": [
            {"project": "common thread", "creator": "charlota blunárová", "place": "Best Overall"},
            {"project": "tokyo", "creator": "kiel cole", "place": "Excellence in Craft"},
            {"project": "pucker", "creator": "aleyna çatak", "place": "New Interaction"},
            {"project": "airwwave", "creator": "lee black", "place": "Boundary Pushing"},
            {"project": "duet booth", "creator": "paige latimer", "place": "Reimagining Iconic Interactions"},
            {"project": "reframe it", "creator": "dann petty", "place": "Fan Favorite on Social"},
        ],
    },
    {
        "name": "Config Makeathon 2026",
        "slug": "configmakeathon",
        "url": "https://contra.com/community/topic/configmakeathon",
        "start": datetime(2026, 6, 4, tzinfo=timezone.utc),
        "end": datetime(2026, 6, 18, tzinfo=timezone.utc),
        "winners": [],  # Will be populated after scraping announcement
    },
]

SOCIAL_PATTERNS = {
    "x": [r"x\.com/", r"twitter\.com/"],
    "linkedin": [r"linkedin\.com/"],
    "instagram": [r"instagram\.com/"],
    "threads": [r"threads\.net/"],
    "bluesky": [r"bsky\.app/"],
}


def extract_text_from_body(body_blocks: list) -> str:
    """Recursively extract plain text from Contra's rich-text block format."""
    if not isinstance(body_blocks, list):
        return str(body_blocks)
    parts = []
    for block in body_blocks:
        if isinstance(block, dict):
            for content_item in block.get("content", []):
                if isinstance(content_item, dict):
                    parts.append(content_item.get("text", ""))
            for child in block.get("children", []):
                parts.append(extract_text_from_body([child]))
    return " ".join(parts)


def count_social_platforms(text: str) -> dict:
    """Count unique social platform mentions in post text."""
    counts = {}
    text_lower = text.lower()
    for platform, patterns in SOCIAL_PATTERNS.items():
        counts[platform] = any(re.search(p, text_lower) for p in patterns)
    return counts


def check_winner(title: str, author_name: str, edition: dict) -> tuple[bool, str]:
    """Return (is_winner, category) for an entry."""
    title_l = title.lower()
    author_l = author_name.lower()
    for w in edition["winners"]:
        if w["project"] and w["project"] in title_l:
            return True, w["place"]
        if w["creator"] and w["creator"] in author_l:
            return True, w["place"]
    return False, ""


def parse_node(node: dict, edition: dict) -> dict:
    """Transform a GraphQL node into a flat analysis-ready row."""
    author = node.get("author") or {}
    first = author.get("firstName", "") or ""
    last = author.get("lastName", "") or ""
    author_name = f"{first} {last}".strip()
    username = author.get("displayUsername", "") or ""

    uid = node.get("uid", "")
    slug = node.get("slug", uid)
    url = f"https://contra.com/community/{slug}" if slug else ""

    created_raw = node.get("createdAt", "")
    try:
        created_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        created_at = None

    likes_list = node.get("likes") or []
    likes = likes_list[0]["count"] if likes_list else 0
    comments = node.get("repliesAllLevelsCount", 0) or 0
    engagement_score = likes + (comments * 2)

    body_blocks = node.get("body") or []
    body_text = extract_text_from_body(body_blocks)

    socials = count_social_platforms(body_text)
    social_count = sum(socials.values())

    has_video = bool(node.get("contentVideos"))
    video_count = len(node.get("contentVideos") or [])

    # Timing relative to edition
    days_into_window = None
    days_before_deadline = None
    if created_at:
        start = edition["start"]
        end = edition["end"]
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        days_into_window = max(0, (created_at - start).days + 1)
        days_before_deadline = max(0, (end - created_at).days)

    is_winner, winner_category = check_winner(body_text + " " + author_name, author_name, edition)

    return {
        "edition": edition["name"],
        "id": node.get("id", ""),
        "uid": uid,
        "url": url,
        "author": author_name,
        "username": username,
        "created_at": created_raw,
        "days_into_window": days_into_window,
        "days_before_deadline": days_before_deadline,
        "likes": likes,
        "comments": comments,
        "engagement_score": engagement_score,
        "has_video": has_video,
        "video_count": video_count,
        "cross_posted_x": socials.get("x", False),
        "cross_posted_linkedin": socials.get("linkedin", False),
        "cross_posted_instagram": socials.get("instagram", False),
        "cross_posted_threads": socials.get("threads", False),
        "cross_posted_bluesky": socials.get("bluesky", False),
        "social_platforms_count": social_count,
        "is_winner": is_winner,
        "winner_category": winner_category,
        "is_not_challenge_submission": node.get("isNotChallengeSubmission", False),
        "body_snippet": body_text[:300],
    }


def scrape_edition(page, edition: dict, max_scroll_rounds: int = 60) -> list[dict]:
    """
    Navigate to a topic page, intercept all paginated API responses,
    and return a list of parsed post rows.
    """
    captured_nodes: dict[str, dict] = {}  # uid -> node, deduped
    all_api_responses = []

    def handle_response(response):
        url = response.url
        if "operationName=SocialPosts_socialPostsPaginationQuery" in url:
            try:
                body = response.json()
                all_api_responses.append(body)
                edges = (body.get("data") or {}).get("socialPosts", {}).get("edges", [])
                for edge in edges:
                    node = edge.get("node")
                    if node:
                        uid = node.get("uid") or node.get("id")
                        captured_nodes[uid] = node
            except Exception as e:
                print(f"    [warn] Failed to parse response: {e}")

    page.on("response", handle_response)
    print(f"  -> {edition['url']}")
    page.goto(edition["url"], wait_until="networkidle", timeout=60_000)
    time.sleep(4)

    last_count = 0
    stable_rounds = 0

    for i in range(max_scroll_rounds):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2.5)

        current_count = len(captured_nodes)
        if current_count == last_count:
            stable_rounds += 1
            if stable_rounds >= 4:
                print(f"    Stable at {current_count} nodes after {i+1} scrolls")
                break
        else:
            stable_rounds = 0
            last_count = current_count
            print(f"    Scroll {i+1}: {current_count} nodes captured")

    page.remove_listener("response", handle_response)

    rows = [parse_node(node, edition) for node in captured_nodes.values()]
    print(f"  Total: {len(rows)} unique posts")
    return rows, all_api_responses


def scrape_config_winners(page) -> list[dict]:
    """
    Scrape Config 2026 winner announcement from the Contra community topic.
    Returns list of winner dicts with project/creator/place.
    """
    print("\n  Looking for Config 2026 winner announcement...")
    winners = []

    # Known sources to check
    urls_to_check = [
        "https://contra.com/community/topic/configmakeathon",
        "https://contra.com/community/6OZFlCWv-explore-projects-from-figma-makeathon-challenges",
    ]

    captured = []

    def handle_response(response):
        url = response.url
        if "/api/" in url:
            try:
                body = response.json()
                captured.append({"url": url, "body": body})
            except Exception:
                pass

    page.on("response", handle_response)

    # Check the configmakeathon topic page for a pinned winner post
    page.goto("https://contra.com/community/topic/configmakeathon", wait_until="networkidle", timeout=60_000)
    time.sleep(3)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(2)

    page.remove_listener("response", handle_response)

    # Look for winner announcement posts in the captured data
    for item in captured:
        body = item.get("body", {})
        edges = (body.get("data") or {}).get("socialPosts", {}).get("edges", [])
        for edge in edges:
            node = edge.get("node") or {}
            if node.get("isPinned") or "winner" in str(node.get("body", "")).lower():
                body_text = extract_text_from_body(node.get("body", []))
                if "winner" in body_text.lower() or "config makeathon" in body_text.lower():
                    print(f"    Found potential winner post: {body_text[:200]}")

    return winners


def main():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    all_rows = []
    all_raw = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        )

        for edition in EDITIONS:
            print(f"\n[{edition['name']}]")
            page = ctx.new_page()
            rows, raw = scrape_edition(page, edition)
            all_rows.extend(rows)
            all_raw.extend(raw)
            page.close()
            time.sleep(2)

        browser.close()

    # Save complete enriched CSV
    if all_rows:
        fieldnames = list(all_rows[0].keys())
        out_path = data_dir / "enriched_entries.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\nSaved {len(all_rows)} rows -> {out_path}")

    # Save raw API responses
    raw_path = data_dir / "api_responses_full.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_raw, f, indent=2)
    print(f"Saved {len(all_raw)} API responses -> {raw_path}")

    # Summary
    print("\n=== Summary ===")
    from collections import Counter
    by_edition = Counter(r["edition"] for r in all_rows)
    for ed, count in by_edition.items():
        winners = sum(1 for r in all_rows if r["edition"] == ed and r["is_winner"])
        print(f"  {ed}: {count} entries, {winners} winners identified")

    total_winners = sum(1 for r in all_rows if r["is_winner"])
    print(f"\nTotal: {len(all_rows)} entries, {total_winners} winners")


if __name__ == "__main__":
    main()
