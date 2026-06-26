#!/usr/bin/env python3
"""
Direct GraphQL API scraper using Contra's persisted query doc_id.
No browser needed — paginates all posts for each edition via httpx.
"""

import json
import time
import re
import csv
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

import httpx


# ── Contra API constants ────────────────────────────────────────────────────

API_URL = "https://contra.com/api/"
DOC_ID = "739d146d0e461458db0934fae52eeeb9"  # SocialPosts_socialPostsPaginationQuery
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Origin": "https://contra.com",
    "Referer": "https://contra.com/community/topic/figmamakeathon",
}


# ── Edition config ──────────────────────────────────────────────────────────

EDITIONS = [
    {
        "name": "Figma Make-a-thon (Sep 2025)",
        "slug": "figmamakeathon",
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
        "start": datetime(2026, 6, 4, tzinfo=timezone.utc),
        "end": datetime(2026, 6, 18, tzinfo=timezone.utc),
        "winners": [],  # To be filled after announcement
    },
]

SOCIAL_PATTERNS = {
    "x": [r"x\.com/", r"twitter\.com/"],
    "linkedin": [r"linkedin\.com/"],
    "instagram": [r"instagram\.com/"],
    "threads": [r"threads\.net/"],
    "bluesky": [r"bsky\.app/"],
}


# ── Text utilities ──────────────────────────────────────────────────────────

def extract_text(body_blocks) -> str:
    """Flatten Contra's block-based rich text to plain string."""
    if not isinstance(body_blocks, list):
        return str(body_blocks or "")
    parts = []
    for block in body_blocks:
        if not isinstance(block, dict):
            continue
        for item in block.get("content", []):
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
        for child in block.get("children", []):
            parts.append(extract_text([child]))
    return " ".join(filter(None, parts))


def social_flags(text: str) -> dict:
    text_l = text.lower()
    return {p: any(re.search(pat, text_l) for pat in pats)
            for p, pats in SOCIAL_PATTERNS.items()}


def check_winner(title: str, author: str, edition: dict) -> tuple[bool, str]:
    tl, al = title.lower(), author.lower()
    for w in edition["winners"]:
        if w["project"] and w["project"] in tl:
            return True, w["place"]
        if w["creator"] and w["creator"] in al:
            return True, w["place"]
    return False, ""


# ── API pagination ──────────────────────────────────────────────────────────

def fetch_page(client: httpx.Client, tag_slug: str, after: str | None, sort: str = "ENGAGEMENT") -> dict:
    variables = {
        "after": after,
        "filter": {"tagSlug": tag_slug},
        "first": 5,
        "includeFeaturedReply": True,
        "initialReplyCount": 1,
        "route": None,
        "skip": False,
        "sort": {"field": sort},
    }
    payload = {
        "doc_id": DOC_ID,
        "operationName": "SocialPosts_socialPostsPaginationQuery",
        "variables": variables,
    }
    resp = client.post(
        f"{API_URL}?operationName=SocialPosts_socialPostsPaginationQuery",
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def scrape_all_pages(client: httpx.Client, tag_slug: str, sort: str = "ENGAGEMENT") -> list[dict]:
    """Paginate through all posts for a topic tag."""
    nodes = {}
    after = None
    page_num = 0

    while True:
        page_num += 1
        try:
            data = fetch_page(client, tag_slug, after, sort)
        except httpx.HTTPStatusError as e:
            print(f"    HTTP {e.response.status_code} on page {page_num}, stopping")
            break
        except Exception as e:
            print(f"    Error on page {page_num}: {e}")
            break

        sp = (data.get("data") or {}).get("socialPosts", {})
        edges = sp.get("edges", [])
        page_info = sp.get("pageInfo", {})

        for edge in edges:
            node = edge.get("node")
            if node:
                uid = node.get("uid") or node.get("id")
                if uid not in nodes:
                    nodes[uid] = node

        if page_num % 10 == 0:
            print(f"    Page {page_num}: {len(nodes)} unique posts so far")

        if not page_info.get("hasNextPage"):
            break

        after = page_info.get("endCursor")
        time.sleep(0.5)

    return list(nodes.values())


# ── Node → row ──────────────────────────────────────────────────────────────

def parse_node(node: dict, edition: dict) -> dict:
    author_obj = node.get("author") or {}
    first = author_obj.get("firstName", "") or ""
    last = author_obj.get("lastName", "") or ""
    author_name = f"{first} {last}".strip()
    username = author_obj.get("displayUsername", "") or ""

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
    body_text = extract_text(body_blocks)

    socials = social_flags(body_text)
    social_count = sum(socials.values())

    has_video = bool(node.get("contentVideos"))
    video_count = len(node.get("contentVideos") or [])

    days_into_window = None
    days_before_deadline = None
    if created_at:
        start = edition["start"]
        end = edition["end"]
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        days_into_window = max(1, (created_at - start).days + 1)
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
        "is_reply": node.get("isReply", False),
        "is_pinned": node.get("isPinned", False),
        "is_not_challenge_submission": node.get("isNotChallengeSubmission", False),
        "body_snippet": body_text[:400],
    }


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    all_rows = []

    with httpx.Client(headers=HEADERS, follow_redirects=True) as client:
        for edition in EDITIONS:
            print(f"\n[{edition['name']}] tag={edition['slug']}")
            nodes = scrape_all_pages(client, edition["slug"])
            print(f"  Total API nodes: {len(nodes)}")
            rows = [parse_node(n, edition) for n in nodes]
            all_rows.extend(rows)

            # Quick stats
            winners = [r for r in rows if r["is_winner"]]
            replies = [r for r in rows if r["is_reply"]]
            print(f"  Winners identified: {len(winners)}")
            print(f"  Replies: {len(replies)}, Top-level: {len(rows) - len(replies)}")
            top_likes = sorted(rows, key=lambda r: r["likes"], reverse=True)[:3]
            for r in top_likes:
                print(f"    #{r['likes']} likes — {r['author']} — {r['url']}")

    # Save
    if all_rows:
        fieldnames = list(all_rows[0].keys())
        out_path = data_dir / "enriched_entries.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\nSaved {len(all_rows)} rows -> {out_path}")

    print("\n=== Final Summary ===")
    by_ed = Counter(r["edition"] for r in all_rows)
    for ed, cnt in by_ed.items():
        w = sum(1 for r in all_rows if r["edition"] == ed and r["is_winner"])
        print(f"  {ed}: {cnt} posts, {w} winners")

    total_w = sum(1 for r in all_rows if r["is_winner"])
    print(f"\nTotal: {len(all_rows)} posts, {total_w} winners flagged")


if __name__ == "__main__":
    main()
