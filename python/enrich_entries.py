#!/usr/bin/env python3
"""
Enrich existing real_all_entries.csv with engagement data from the Contra API.

Strategy: Load the 276 known post URLs from real_all_entries.csv.
Extract UIDs from the URLs. Paginate the Contra GraphQL API for each
edition tag and match returned nodes to the known UIDs.
Stop paginating once all known UIDs for an edition are found
(or after a max page limit).

Outputs: data/enriched_entries.csv
"""
import csv, json, re
from pathlib import Path
from datetime import datetime, timezone
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
        "start": datetime(2025, 9, 3,  tzinfo=timezone.utc),
        "end":   datetime(2025, 9, 10, tzinfo=timezone.utc),
        "winners": [
            {"project": "web poetry",        "creator": "cara ellis",        "place": "1st ($50K)"},
            {"project": "plan that trip",     "creator": "johannes specht",   "place": "3rd ($7.5K)"},
            {"project": "package customizer", "creator": "daniella marynova", "place": "Most Innovative"},
            {"project": "package customizer", "creator": "max pradella",      "place": "Most Innovative"},
        ],
    },
    {
        "name": "Figma Makeathon March 2026",
        "slug": "figmamakeathonmarch2026",
        "start": datetime(2026, 2, 1,  tzinfo=timezone.utc),
        "end":   datetime(2026, 3, 16, tzinfo=timezone.utc),
        "winners": [
            {"project": "common thread",  "creator": "charlota blunárová",  "place": "Best Overall"},
            {"project": "tokyo",          "creator": "kiel cole",            "place": "Excellence in Craft"},
            {"project": "pucker",         "creator": "aleyna catak",         "place": "New Interaction"},
            {"project": "pucker",         "creator": "aleyna çatak",         "place": "New Interaction"},
            {"project": "airwwave",       "creator": "lee black",            "place": "Boundary Pushing"},
            {"project": "duet booth",     "creator": "paige latimer",        "place": "Reimagining Iconic Interactions"},
            {"project": "reframe it",     "creator": "dann petty",           "place": "Fan Favorite on Social"},
        ],
    },
    {
        "name": "Config Makeathon 2026",
        "slug": "configmakeathon",
        "start": datetime(2026, 6, 4,  tzinfo=timezone.utc),
        "end":   datetime(2026, 6, 18, tzinfo=timezone.utc),
        "winners": [],
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

def extract_uid_from_url(url: str) -> str:
    """Extract the 8-char UID prefix from a Contra community URL."""
    # e.g. https://contra.com/community/kNlMQlrl-transforming-sketches-...
    m = re.search(r"/community/([A-Za-z0-9]+)", url)
    return m.group(1) if m else ""


def text_from_blocks(blocks) -> str:
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
            parts.append(text_from_blocks([child]))
    return " ".join(filter(None, parts))


def social_flags(t: str) -> dict:
    tl = t.lower()
    return {p: any(re.search(pat, tl) for pat in pats) for p, pats in SOCIAL.items()}


def check_winner(body: str, author: str, edition: dict) -> tuple[bool, str]:
    bl, al = body.lower(), author.lower()
    for w in edition["winners"]:
        if w["project"] and w["project"] in bl:
            return True, w["place"]
        if w["creator"] and w["creator"] in al:
            return True, w["place"]
    return False, ""


def build_row(node: dict, orig_row: dict, edition: dict) -> dict:
    """Merge API node data with existing CSV row."""
    ao = node.get("author") or {}
    author_name = f"{ao.get('firstName','') or ''} {ao.get('lastName','') or ''}".strip()
    username    = ao.get("displayUsername", "") or ""

    likes_l  = node.get("likes") or []
    likes    = likes_l[0]["count"] if likes_l else 0
    comments = node.get("repliesAllLevelsCount", 0) or 0

    body_text  = text_from_blocks(node.get("body") or [])
    # Fall back to existing body snippet if API body is empty
    if not body_text.strip():
        body_text = orig_row.get("body", "")

    sf = social_flags(body_text)

    created_raw = node.get("createdAt") or orig_row.get("created_at", "")
    try:
        ca = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        if ca.tzinfo is None:
            ca = ca.replace(tzinfo=timezone.utc)
        days_in     = max(1, (ca - edition["start"]).days + 1)
        days_before = max(0, (edition["end"] - ca).days)
    except Exception:
        days_in, days_before = None, None

    is_w, w_cat = check_winner(body_text + " " + author_name, author_name, edition)

    return {
        "edition":               edition["name"],
        "id":                    node.get("id", "") or orig_row.get("id", ""),
        "uid":                   node.get("uid", ""),
        "url":                   orig_row.get("url", ""),
        "author":                author_name,
        "username":              username,
        "created_at":            created_raw,
        "days_into_window":      days_in,
        "days_before_deadline":  days_before,
        "likes":                 likes,
        "comments":              comments,
        "engagement_score":      likes + (comments * 2),
        "has_video":             node.get("contentVideos") and len(node["contentVideos"]) > 0,
        "video_count":           len(node.get("contentVideos") or []),
        "cross_posted_x":        sf.get("x", False),
        "cross_posted_linkedin": sf.get("linkedin", False),
        "cross_posted_instagram":sf.get("instagram", False),
        "cross_posted_threads":  sf.get("threads", False),
        "cross_posted_bluesky":  sf.get("bluesky", False),
        "social_platforms_count":sum(sf.values()),
        "is_winner":             is_w,
        "winner_category":       w_cat,
        "is_reply":              node.get("isReply", False),
        "is_pinned":             node.get("isPinned", False),
        "body_snippet":          body_text[:400],
    }


# ── Core logic ───────────────────────────────────────────────────────────────

def load_known_uids(csv_path: Path) -> dict[str, dict]:
    """
    Read existing CSV and return {uid: row_dict} for each entry.
    """
    uid_map = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            uid = extract_uid_from_url(row.get("url", ""))
            if uid:
                uid_map[uid] = row
    return uid_map


def paginate_and_match(
    client: httpx.Client,
    edition: dict,
    known_uids: set[str],
    max_pages: int = 120,
) -> dict[str, dict]:
    """
    Paginate the API and return {uid: node} for all nodes matching known_uids.
    Stops early once all known_uids are found or max_pages is reached.
    """
    found = {}
    after = None
    remaining = set(known_uids)

    for pg in range(1, max_pages + 1):
        payload = {
            "doc_id":        DOC_ID,
            "operationName": "SocialPosts_socialPostsPaginationQuery",
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
            uid = node.get("uid", "")
            if uid in remaining:
                found[uid] = node
                remaining.discard(uid)

        pi = sp.get("pageInfo", {})
        if pg % 20 == 0:
            print(f"    page {pg}: found {len(found)}/{len(known_uids)}, {len(remaining)} remaining")

        if not remaining:
            print(f"    All {len(known_uids)} UIDs found at page {pg}")
            break

        if not pi.get("hasNextPage"):
            print(f"    API exhausted at page {pg}, found {len(found)}/{len(known_uids)}")
            break

        after = pi.get("endCursor")

    return found


def main():
    base = Path(__file__).parent.parent
    data_dir = base / "data"
    csv_in   = data_dir / "real_all_entries.csv"

    # Load all 276 known entries grouped by edition
    print("Loading existing entries...")
    all_orig: dict[str, dict] = {}  # uid -> row
    edition_uid_map: dict[str, dict[str, dict]] = {}  # edition_name -> {uid: row}

    with open(csv_in, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            uid = extract_uid_from_url(row.get("url", ""))
            if not uid:
                continue
            ed_name = row.get("edition", "")
            all_orig[uid] = row
            edition_uid_map.setdefault(ed_name, {})[uid] = row

    print(f"  Loaded {len(all_orig)} entries across {len(edition_uid_map)} editions")
    for en, rows in edition_uid_map.items():
        print(f"    {en}: {len(rows)} entries")

    # Paginate the API for each edition and match known UIDs
    all_rows = []
    edition_by_name = {ed["name"]: ed for ed in EDITIONS}

    with httpx.Client(headers=HDRS, follow_redirects=True) as client:
        for ed_name, orig_rows in edition_uid_map.items():
            edition = edition_by_name.get(ed_name)
            if not edition:
                print(f"  WARNING: No config for edition '{ed_name}', skipping")
                continue

            print(f"\n[{ed_name}] — {len(orig_rows)} known entries")
            known_uids = set(orig_rows.keys())
            matched_nodes = paginate_and_match(client, edition, known_uids)

            # Build enriched rows
            matched_count = 0
            for uid, orig_row in orig_rows.items():
                node = matched_nodes.get(uid)
                if node:
                    row = build_row(node, orig_row, edition)
                    matched_count += 1
                else:
                    # Not found in API — keep original data with zeroed engagement
                    body_text = orig_row.get("body", "")
                    sf = social_flags(body_text)
                    is_w, w_cat = check_winner(body_text, "", edition)
                    created_raw = orig_row.get("created_at", "")
                    try:
                        ca = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                        if ca.tzinfo is None:
                            ca = ca.replace(tzinfo=timezone.utc)
                        days_in     = max(1, (ca - edition["start"]).days + 1)
                        days_before = max(0, (edition["end"] - ca).days)
                    except Exception:
                        days_in, days_before = None, None

                    row = {
                        "edition":               ed_name,
                        "id":                    orig_row.get("id", ""),
                        "uid":                   uid,
                        "url":                   orig_row.get("url", ""),
                        "author":                "",
                        "username":              "",
                        "created_at":            created_raw,
                        "days_into_window":      days_in,
                        "days_before_deadline":  days_before,
                        "likes":                 0,
                        "comments":              0,
                        "engagement_score":      0,
                        "has_video":             orig_row.get("has_video", "False") == "True",
                        "video_count":           int(orig_row.get("video_count", 0) or 0),
                        "cross_posted_x":        sf.get("x", False),
                        "cross_posted_linkedin": sf.get("linkedin", False),
                        "cross_posted_instagram":sf.get("instagram", False),
                        "cross_posted_threads":  sf.get("threads", False),
                        "cross_posted_bluesky":  sf.get("bluesky", False),
                        "social_platforms_count":sum(sf.values()),
                        "is_winner":             is_w,
                        "winner_category":       w_cat,
                        "is_reply":              False,
                        "is_pinned":             False,
                        "body_snippet":          body_text[:400],
                    }
                all_rows.append(row)

            print(f"  Matched: {matched_count}/{len(orig_rows)} entries enriched from API")
            winners = [r for r in all_rows if r["edition"] == ed_name and r["is_winner"]]
            print(f"  Winners identified: {len(winners)}")
            top = sorted([r for r in all_rows if r["edition"] == ed_name],
                         key=lambda r: r["likes"], reverse=True)[:5]
            for r in top:
                flag = " [WINNER]" if r["is_winner"] else ""
                print(f"    {r['likes']:4d} likes  {r['comments']:3d} cmt  {r['author'][:30]}{flag}")

    # Save
    out = data_dir / "enriched_entries.csv"
    fields = list(all_rows[0].keys())
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nSaved {len(all_rows)} rows -> {out}")

    # Final summary
    print("\n=== Final Summary ===")
    from collections import Counter
    for ed in EDITIONS:
        subset = [r for r in all_rows if r["edition"] == ed["name"]]
        wins   = [r for r in subset if r["is_winner"]]
        matched = [r for r in subset if r["likes"] > 0 or r["author"]]
        print(f"  {ed['name']}: {len(subset)} posts, {len(matched)} enriched, {len(wins)} winners")
    print(f"  TOTAL: {len(all_rows)} posts, {sum(1 for r in all_rows if r['is_winner'])} winners")


if __name__ == "__main__":
    main()
