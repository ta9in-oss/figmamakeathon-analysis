#!/usr/bin/env python3
"""
Build the final enriched dataset for analysis.

Combines:
1. enriched_entries.csv (March 2026 + Config 2026 with real engagement)
2. Sep 2025 reply data from the submission threads
3. Sep 2025 non-reply entries from real_all_entries.csv (timing + video only)

Outputs: data/final_entries.csv
"""
import csv, json, re
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).parent.parent
DATA = BASE / "data"

# ── Sep 2025 winner seed (now complete) ──────────────────────────────────────

SEP_WINNERS = [
    {"project": "web poetry",        "creator": "cara ellis",        "place": "1st ($50K)"},
    {"project": "plan that trip",     "creator": "johannes specht",   "place": "3rd ($7.5K)"},
    {"project": "package customizer", "creator": "daniella marynova", "place": "Most Innovative"},
    {"project": "package customizer", "creator": "max pradella",      "place": "Most Innovative"},
]

MAR_WINNERS = [
    {"project": "common thread",  "creator": "charlota blunárová", "place": "Best Overall"},
    {"project": "tokyo",          "creator": "kiel cole",          "place": "Excellence in Craft"},
    {"project": "pucker",         "creator": "aleyna catak",       "place": "New Interaction"},
    {"project": "pucker",         "creator": "aleyna çatak",       "place": "New Interaction"},
    {"project": "airwwave",       "creator": "lee black",          "place": "Boundary Pushing"},
    {"project": "duet booth",     "creator": "paige latimer",      "place": "Reimagining Iconic Interactions"},
    {"project": "reframe it",     "creator": "dann petty",         "place": "Fan Favorite on Social"},
]

CONFIG_WINNERS = [
    {"project": "visual atlas",         "creator": "bene brandhofer",      "place": "Grand Prize ($50K)"},
    {"project": "doodle fonts",         "creator": "carlos fernandez",     "place": "2nd Overall ($15K)"},
    {"project": "your eyes can speak",  "creator": "nigar naghdaliyeva",   "place": "Build With Purpose ($10K)"},
    {"project": "connected earth",      "creator": "lee black",            "place": "Innovative Workflow ($10K)"},
    {"project": "still here focus",     "creator": "halle clark",          "place": "Build In Public ($10K)"},
    {"project": "sound check",          "creator": "case ronquillo",       "place": "Community Favorite ($5K)"},
]

EDITION_WINNERS = {
    "Figma Make-a-thon (Sep 2025)": SEP_WINNERS,
    "Figma Makeathon March 2026": MAR_WINNERS,
    "Config Makeathon 2026": CONFIG_WINNERS,
}

EDITION_DATES = {
    "Figma Make-a-thon (Sep 2025)": {
        "start": datetime(2025, 9, 3,  tzinfo=timezone.utc),
        "end":   datetime(2025, 9, 10, tzinfo=timezone.utc),
    },
    "Figma Makeathon March 2026": {
        "start": datetime(2026, 2, 1,  tzinfo=timezone.utc),
        "end":   datetime(2026, 3, 16, tzinfo=timezone.utc),
    },
    "Config Makeathon 2026": {
        "start": datetime(2026, 6, 4,  tzinfo=timezone.utc),
        "end":   datetime(2026, 6, 18, tzinfo=timezone.utc),
    },
}

SOCIAL = {
    "x":         [r"x\.com/", r"twitter\.com/"],
    "linkedin":  [r"linkedin\.com/"],
    "instagram": [r"instagram\.com/"],
    "threads":   [r"threads\.net/"],
    "bluesky":   [r"bsky\.app/"],
}


def social_flags(t: str) -> dict:
    tl = t.lower()
    return {p: any(re.search(pat, tl) for pat in pats) for p, pats in SOCIAL.items()}


def check_winner(body: str, author: str, edition: str) -> tuple[bool, str]:
    bl, al = body.lower(), author.lower()
    for w in EDITION_WINNERS.get(edition, []):
        if w["project"] and w["project"] in bl:
            return True, w["place"]
        if w["creator"] and w["creator"] in al:
            return True, w["place"]
    return False, ""


def parse_timing(created_at: str, edition: str) -> tuple:
    dates = EDITION_DATES.get(edition, {})
    if not dates or not created_at:
        return None, None
    try:
        ca = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if ca.tzinfo is None:
            ca = ca.replace(tzinfo=timezone.utc)
        days_in     = max(1, (ca - dates["start"]).days + 1)
        days_before = max(0, (dates["end"] - ca).days)
        return days_in, days_before
    except Exception:
        return None, None


def main():
    rows_out = []

    # ── 1. Load enriched March 2026 + Config 2026 from enriched_entries.csv ──
    enriched_path = DATA / "enriched_entries.csv"
    if enriched_path.exists():
        with open(enriched_path, newline="", encoding="utf-8") as f:
            enriched = list(csv.DictReader(f))
        # Keep only March 2026 and Config 2026 (Sep 2025 had 0 matches)
        for row in enriched:
            ed = row["edition"]
            if "Sep 2025" in ed:
                continue
            body = row.get("body_snippet", "")
            author = row.get("author", "")
            is_w, w_cat = check_winner(body, author, ed)
            row["is_winner"] = str(is_w)
            row["winner_category"] = w_cat
            rows_out.append(row)
        print(f"Loaded {len(rows_out)} enriched March/Config rows")

    # ── 2. Load Sep 2025 reply data from /tmp ────────────────────────────────
    sep_json = Path("/tmp/sep2025_replies.json")
    sep_rows = []
    if sep_json.exists():
        with open(sep_json) as f:
            sep_data = json.load(f)
        for row in sep_data:
            # Re-check winner with full name
            body = row.get("body_snippet", "")
            author = row.get("author", "")
            is_w, w_cat = check_winner(body, author, "Figma Make-a-thon (Sep 2025)")
            # Force-check username too (Cara Ellis's username is onyourtiptoes)
            username = row.get("username", "")
            if not is_w:
                for w in SEP_WINNERS:
                    if w["creator"] and w["creator"] in (author + " " + username).lower():
                        is_w, w_cat = True, w["place"]
                        break
            row["is_winner"] = str(is_w)
            row["winner_category"] = w_cat
            # Ensure all expected keys present
            for k in ["cross_posted_x", "cross_posted_linkedin", "cross_posted_instagram",
                      "cross_posted_threads", "cross_posted_bluesky"]:
                if k not in row:
                    row[k] = False
            sep_rows.append(row)
        print(f"Loaded {len(sep_rows)} Sep 2025 reply rows")
        rows_out.extend(sep_rows)

    # ── 3. Supplement Sep 2025 with non-reply entries from real_all_entries ──
    real_path = DATA / "real_all_entries.csv"
    sep_reply_uids = {r["uid"] for r in sep_rows}
    extra_count = 0

    if real_path.exists():
        with open(real_path, newline="", encoding="utf-8") as f:
            orig = list(csv.DictReader(f))
        for row in orig:
            if "Sep 2025" not in row.get("edition", ""):
                continue
            # Extract UID from URL
            m = re.search(r"/community/([A-Za-z0-9]+)", row.get("url", ""))
            uid = m.group(1) if m else ""
            if uid in sep_reply_uids:
                continue  # already have it from replies
            # Build a row with limited data (no engagement)
            body = row.get("body", "")
            sf = social_flags(body)
            is_w, w_cat = check_winner(body, "", "Figma Make-a-thon (Sep 2025)")
            created_at = row.get("created_at", "")
            days_in, days_before = parse_timing(created_at, "Figma Make-a-thon (Sep 2025)")
            new_row = {
                "edition":               "Figma Make-a-thon (Sep 2025)",
                "id":                    row.get("id", ""),
                "uid":                   uid,
                "url":                   row.get("url", ""),
                "author":                "",
                "username":              "",
                "created_at":            created_at,
                "days_into_window":      days_in,
                "days_before_deadline":  days_before,
                "likes":                 0,
                "comments":              0,
                "engagement_score":      0,
                "has_video":             row.get("has_video", "False") == "True",
                "video_count":           int(row.get("video_count", 0) or 0),
                "cross_posted_x":        sf.get("x", False),
                "cross_posted_linkedin": sf.get("linkedin", False),
                "cross_posted_instagram":sf.get("instagram", False),
                "cross_posted_threads":  sf.get("threads", False),
                "cross_posted_bluesky":  sf.get("bluesky", False),
                "social_platforms_count":sum(sf.values()),
                "is_winner":             str(is_w),
                "winner_category":       w_cat,
                "is_reply":              False,
                "is_pinned":             False,
                "body_snippet":          body[:400],
            }
            rows_out.append(new_row)
            extra_count += 1

    print(f"Added {extra_count} extra Sep 2025 non-reply rows")

    # ── 4. Final winner re-scan (ensure all winners are flagged) ─────────────
    # Known winner UIDs from Sep 2025 reply data
    # Cara Ellis's submission: uid oYE6LLP7
    known_winners = {
        "oYE6LLP7": ("1st ($50K)", "Figma Make-a-thon (Sep 2025)"),
    }
    for row in rows_out:
        uid = row.get("uid", "")
        if uid in known_winners:
            row["is_winner"] = "True"
            row["winner_category"] = known_winners[uid][0]

    # ── 5. Save ──────────────────────────────────────────────────────────────
    out = DATA / "final_entries.csv"
    fieldnames = [
        "edition", "id", "uid", "url", "author", "username", "created_at",
        "days_into_window", "days_before_deadline", "likes", "comments",
        "engagement_score", "has_video", "video_count",
        "cross_posted_x", "cross_posted_linkedin", "cross_posted_instagram",
        "cross_posted_threads", "cross_posted_bluesky", "social_platforms_count",
        "is_winner", "winner_category", "is_reply", "is_pinned", "body_snippet",
    ]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows_out)

    print(f"\nSaved {len(rows_out)} rows -> {out}")

    # ── 6. Summary ───────────────────────────────────────────────────────────
    print("\n=== Final Dataset Summary ===")
    from collections import Counter
    by_ed = Counter(r["edition"] for r in rows_out)
    for ed, cnt in sorted(by_ed.items()):
        wins = sum(1 for r in rows_out if r["edition"] == ed and str(r.get("is_winner", "")).lower() == "true")
        enriched_count = sum(1 for r in rows_out if r["edition"] == ed and int(r.get("likes", 0) or 0) > 0)
        print(f"  {ed}: {cnt} entries, {wins} winners, {enriched_count} with engagement data")

    print()
    print("Config 2026 top entries by engagement:")
    config = sorted(
        [r for r in rows_out if "Config" in r.get("edition", "")],
        key=lambda r: int(r.get("engagement_score", 0) or 0), reverse=True
    )[:8]
    for r in config:
        flag = " [WINNER]" if str(r.get("is_winner", "")).lower() == "true" else ""
        print(f"  {int(r.get('engagement_score',0)):5d} | {int(r.get('likes',0)):4d} likes | {r.get('author','')[:25]:<25}{flag}")


if __name__ == "__main__":
    main()
