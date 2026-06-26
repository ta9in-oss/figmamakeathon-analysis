#!/usr/bin/env python3
"""
Final scraper: paginates Contra GraphQL API for all 3 editions.
Gets all posts with engagement data, filters to contest window, marks winners.
Outputs: data/enriched_entries.csv
"""
import json, re, csv
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import httpx

# ── API ─────────────────────────────────────────────────────────────────────

API = "https://contra.com/api/"
DOC_ID = "739d146d0e461458db0934fae52eeeb9"
HDRS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Origin": "https://contra.com",
}

# ── Editions ─────────────────────────────────────────────────────────────────

EDITIONS = [
    {
        "name": "Figma Make-a-thon (Sep 2025)",
        "slug": "figmamakeathon",
        # Widen window slightly to catch late posts that are still part of the event
        "window_start": datetime(2025, 9, 1, tzinfo=timezone.utc),
        "window_end":   datetime(2025, 9, 15, tzinfo=timezone.utc),
        "start": datetime(2025, 9, 3, tzinfo=timezone.utc),
        "end":   datetime(2025, 9, 10, tzinfo=timezone.utc),
        "winners": [
            {"project": "web poetry",         "creator": "cara ellis",             "place": "1st ($50K)"},
            {"project": "plan that trip",      "creator": "johannes specht",        "place": "3rd ($7.5K)"},
            {"project": "package customizer",  "creator": "daniella marynova",      "place": "Most Innovative"},
            {"project": "package customizer",  "creator": "max pradella",           "place": "Most Innovative"},
        ],
    },
    {
        "name": "Figma Makeathon March 2026",
        "slug": "figmamakeathonmarch2026",
        "window_start": datetime(2026, 1, 28, tzinfo=timezone.utc),
        "window_end":   datetime(2026, 3, 20, tzinfo=timezone.utc),
        "start": datetime(2026, 2, 1,  tzinfo=timezone.utc),
        "end":   datetime(2026, 3, 16, tzinfo=timezone.utc),
        "winners": [
            {"project": "common thread",  "creator": "charlota blunárová", "place": "Best Overall"},
            {"project": "tokyo",          "creator": "kiel cole",          "place": "Excellence in Craft"},
            {"project": "pucker",         "creator": "aleyna catak",       "place": "New Interaction"},
            {"project": "pucker",         "creator": "aleyna çatak",       "place": "New Interaction"},
            {"project": "airwwave",       "creator": "lee black",          "place": "Boundary Pushing"},
            {"project": "duet booth",     "creator": "paige latimer",      "place": "Reimagining Iconic Interactions"},
            {"project": "reframe it",     "creator": "dann petty",         "place": "Fan Favorite on Social"},
        ],
    },
    {
        "name": "Config Makeathon 2026",
        "slug": "configmakeathon",
        "window_start": datetime(2026, 6, 1, tzinfo=timezone.utc),
        "window_end":   datetime(2026, 6, 25, tzinfo=timezone.utc),
        "start": datetime(2026, 6, 4,  tzinfo=timezone.utc),
        "end":   datetime(2026, 6, 18, tzinfo=timezone.utc),
        "winners": [],  # Config 2026 winners TBD — will be identified from post content
    },
]

SOCIAL = {
    "x":         [r"x\.com/", r"twitter\.com/"],
    "linkedin":  [r"linkedin\.com/"],
    "instagram": [r"instagram\.com/"],
    "threads":   [r"threads\.net/"],
    "bluesky":   [r"bsky\.app/"],
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def text(blocks) -> str:
    if not isinstance(blocks, list):
        return str(blocks or "")
    parts = []
    for b in blocks:
        if not isinstance(b, dict):
            continue
        for item in b.get("content", []):
            if isinstance(item, dict):
                parts.append(item.get("text", "") or "")
        for child in b.get("children", []):
            parts.append(text([child]))
    return " ".join(filter(None, parts))


def social_flags(t: str) -> dict:
    tl = t.lower()
    return {p: any(re.search(pat, tl) for pat in pats) for p, pats in SOCIAL.items()}


def winner(body: str, author: str, edition: dict) -> tuple[bool, str]:
    bl, al = body.lower(), author.lower()
    for w in edition["winners"]:
        if w["project"] and w["project"] in bl:
            return True, w["place"]
        if w["creator"] and w["creator"] in al:
            return True, w["place"]
    return False, ""


def parse_node(node: dict, edition: dict) -> dict:
    ao = node.get("author") or {}
    author_name = f"{ao.get('firstName','') or ''} {ao.get('lastName','') or ''}".strip()
    username    = ao.get("displayUsername", "") or ""
    uid         = node.get("uid", "")
    slug        = node.get("slug", uid)
    url         = f"https://contra.com/community/{slug}" if slug else ""
    raw_ts      = node.get("createdAt", "")

    try:
        ca = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
    except Exception:
        ca = None

    likes_l    = node.get("likes") or []
    likes      = likes_l[0]["count"] if likes_l else 0
    comments   = node.get("repliesAllLevelsCount", 0) or 0
    body_text  = text(node.get("body") or [])
    sf         = social_flags(body_text)
    has_vid    = bool(node.get("contentVideos"))
    vid_count  = len(node.get("contentVideos") or [])

    days_in, days_before = None, None
    if ca:
        if ca.tzinfo is None:
            ca = ca.replace(tzinfo=timezone.utc)
        days_in     = max(1, (ca - edition["start"]).days + 1)
        days_before = max(0, (edition["end"] - ca).days)

    is_w, w_cat = winner(body_text + " " + author_name, author_name, edition)

    return {
        "edition":              edition["name"],
        "id":                   node.get("id", ""),
        "uid":                  uid,
        "url":                  url,
        "author":               author_name,
        "username":             username,
        "created_at":           raw_ts,
        "days_into_window":     days_in,
        "days_before_deadline": days_before,
        "likes":                likes,
        "comments":             comments,
        "engagement_score":     likes + (comments * 2),
        "has_video":            has_vid,
        "video_count":          vid_count,
        "cross_posted_x":       sf.get("x", False),
        "cross_posted_linkedin":sf.get("linkedin", False),
        "cross_posted_instagram":sf.get("instagram", False),
        "cross_posted_threads": sf.get("threads", False),
        "cross_posted_bluesky": sf.get("bluesky", False),
        "social_platforms_count": sum(sf.values()),
        "is_winner":            is_w,
        "winner_category":      w_cat,
        "is_reply":             node.get("isReply", False),
        "is_pinned":            node.get("isPinned", False),
        "body_snippet":         body_text[:400],
    }


def scrape_edition(client: httpx.Client, edition: dict) -> list[dict]:
    nodes = {}
    after = None
    pg    = 0

    ws = edition["window_start"]
    we = edition["window_end"]

    while True:
        pg += 1
        payload = {
            "doc_id":          DOC_ID,
            "operationName":   "SocialPosts_socialPostsPaginationQuery",
            "variables": {
                "after":              after,
                "filter":             {"tagSlug": edition["slug"]},
                "first":              20,
                "includeFeaturedReply": True,
                "initialReplyCount":  1,
                "route":              None,
                "skip":               False,
                "sort":               {"field": "ENGAGEMENT"},
            },
        }
        resp = client.post(
            f"{API}?operationName=SocialPosts_socialPostsPaginationQuery",
            json=payload, timeout=30,
        )
        resp.raise_for_status()
        sp = resp.json().get("data", {}).get("socialPosts", {})

        for edge in sp.get("edges", []):
            node = edge.get("node")
            if not node:
                continue
            uid = node.get("uid") or node.get("id")
            if uid in nodes:
                continue
            # Filter: only posts within the window
            raw = node.get("createdAt", "")
            try:
                ca = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                if ca.tzinfo is None:
                    ca = ca.replace(tzinfo=timezone.utc)
                if ws <= ca <= we:
                    nodes[uid] = node
            except Exception:
                pass

        pi = sp.get("pageInfo", {})
        if pg % 20 == 0:
            print(f"    page {pg}: {len(nodes)} in-window posts")

        if not pi.get("hasNextPage"):
            break
        after = pi.get("endCursor")

    return [parse_node(n, edition) for n in nodes.values()]


def main():
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    all_rows = []
    with httpx.Client(headers=HDRS, follow_redirects=True) as client:
        for ed in EDITIONS:
            print(f"\n[{ed['name']}]")
            rows = scrape_edition(client, ed)
            # Filter out replies (not direct submissions)
            top_level = [r for r in rows if not r["is_reply"]]
            print(f"  {len(rows)} in-window posts ({len(top_level)} top-level)")
            ws = [r for r in rows if r["is_winner"]]
            print(f"  Winners identified: {len(ws)}")
            top = sorted(rows, key=lambda r: r["likes"], reverse=True)[:5]
            for r in top:
                flag = " [WINNER]" if r["is_winner"] else ""
                print(f"    {r['likes']:4d} likes  {r['comments']:3d} cmt  {r['author'][:30]}{flag}")
            all_rows.extend(rows)

    # Save
    if all_rows:
        out = data_dir / "enriched_entries.csv"
        fields = list(all_rows[0].keys())
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(all_rows)
        print(f"\nSaved {len(all_rows)} rows -> {out}")

    # Summary
    print("\n=== Summary ===")
    for ed in EDITIONS:
        subset = [r for r in all_rows if r["edition"] == ed["name"]]
        wins   = [r for r in subset if r["is_winner"]]
        print(f"  {ed['name']}: {len(subset)} posts, {len(wins)} winners")
    total_w = sum(1 for r in all_rows if r["is_winner"])
    print(f"  TOTAL: {len(all_rows)} posts, {total_w} winners")


if __name__ == "__main__":
    main()
