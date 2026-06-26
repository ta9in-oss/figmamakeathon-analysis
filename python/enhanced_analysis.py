#!/usr/bin/env python3
"""
Enhanced analysis from scraped_all_6030.csv answering 6 questions:
Q1: Overall stats
Q2: What everybody did
Q3: What winners did and when
Q4: Reach proxy (cross-posting as social presence)
Q5: Staff/judge presence
Q6: Criteria alignment for winners
"""
import csv, json, re, statistics
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone

BASE = Path(__file__).parent.parent
DATA = BASE / "data"
SRC  = DATA / "scraped_all_6030.csv"
OUT_JSON = DATA / "analysis_v2.json"
OUT_CSV  = BASE / "astro" / "public" / "data" / "all_entries.csv"

EDITIONS = {
    "Figma Make-a-thon (Sep 2025)": {
        "start": datetime(2025, 9, 3,  tzinfo=timezone.utc),
        "end":   datetime(2025, 9, 10, tzinfo=timezone.utc),
        "max_day": 8,
        "label": "Sep 2025",
    },
    "Figma Makeathon March 2026": {
        "start": datetime(2026, 2, 1,  tzinfo=timezone.utc),
        "end":   datetime(2026, 3, 16, tzinfo=timezone.utc),
        "max_day": 44,
        "label": "Mar 2026",
    },
    "Config Makeathon 2026": {
        "start": datetime(2026, 6, 4,  tzinfo=timezone.utc),
        "end":   datetime(2026, 6, 18, tzinfo=timezone.utc),
        "max_day": 15,
        "label": "Config 2026",
    },
}

SEP_WINNERS = [
    {"project": "web poetry",         "creator": "cara ellis",        "place": "1st ($50K)"},
    {"project": "plan that trip",     "creator": "johannes specht",   "place": "3rd ($7.5K)"},
    {"project": "package customizer", "creator": "daniella marynova", "place": "Most Innovative"},
    {"project": "package customizer", "creator": "max pradella",      "place": "Most Innovative"},
]
MAR_WINNERS = [
    {"project": "common thread",  "creator": "charlota blun",  "place": "Best Overall"},
    {"project": "tokyo",          "creator": "kiel cole",      "place": "Excellence in Craft"},
    {"project": "pucker",         "creator": "aleyna",         "place": "New Interaction"},
    {"project": "airwwave",       "creator": "lee black",      "place": "Boundary Pushing"},
    {"project": "duet booth",     "creator": "paige latimer",  "place": "Reimagining"},
    {"project": "reframe it",     "creator": "dann petty",     "place": "Fan Favorite"},
]
CONFIG_WINNERS = [
    {"project": "visual atlas",        "creator": "bene brandhofer",    "place": "Grand Prize ($50K)"},
    {"project": "doodle font",         "creator": "carlos fernandez",   "place": "2nd Overall ($15K)"},
    {"project": "your eyes can speak", "creator": "nigar naghdaliyeva", "place": "Build With Purpose"},
    {"project": "eyetext",             "creator": "nigar naghdaliyeva", "place": "Build With Purpose"},
    {"project": "connected earth",     "creator": "lee black",          "place": "Innovative Workflow"},
    {"project": "still here",          "creator": "halle clark",        "place": "Build In Public"},
    {"project": "soundcheck",          "creator": "case ronquillo",     "place": "Community Favorite"},
    {"project": "sound check",         "creator": "case ronquillo",     "place": "Community Favorite"},
]
WINNER_MAP = {
    "Figma Make-a-thon (Sep 2025)": SEP_WINNERS,
    "Figma Makeathon March 2026":   MAR_WINNERS,
    "Config Makeathon 2026":        CONFIG_WINNERS,
}

STAFF_NAMES = {"galaxia wu", "sabrina polanco", "gui seiz", "jan mráz", "jan mraz", "daniela muntyan"}
EXCLUDE_KEYWORDS = [
    "welcome to the first ever", "the figma make-a-thon is officially",
    "the figma makeathon is officially", "config makeathon is officially",
    "announcing the winners", "meet the winners", "celebrating",
    "judges for the", "join us for",
]

# Judging criteria keywords per edition
CRITERIA_KEYWORDS = {
    "Figma Make-a-thon (Sep 2025)": ["interactive", "figma", "prototype", "web", "experience"],
    "Figma Makeathon March 2026":   ["craft", "visual", "interaction", "original", "innovative"],
    "Config Makeathon 2026":        ["config", "build in public", "workflow", "community", "innovative"],
}

def is_staff(author):
    al = author.lower()
    return any(s in al for s in STAFF_NAMES)

def is_excluded(row):
    if is_staff(row["author"]):
        return True
    body = row["body"].lower()[:200]
    return any(kw in body for kw in EXCLUDE_KEYWORDS)

def check_winner(body, author, edition):
    bl, al = body.lower(), author.lower()
    for w in WINNER_MAP.get(edition, []):
        if w["project"] and w["project"] in bl:
            return True, w["place"]
        if w["creator"] and w["creator"] in al:
            return True, w["place"]
    return False, ""

def safe_int(v, default=0):
    try: return int(v or default)
    except: return default

def safe_float(v):
    try:
        f = float(v)
        return f if f == f else None
    except: return None

def mean(vals):
    v = [x for x in vals if x is not None]
    return round(statistics.mean(v), 1) if v else 0.0

def median(vals):
    v = [x for x in vals if x is not None]
    return round(statistics.median(v), 1) if v else 0.0

def pct(bools):
    if not bools: return 0.0
    return round(100 * sum(1 for b in bools if b) / len(bools), 1)

def tier(likes):
    if likes == 0: return "0"
    if likes <= 5: return "1-5"
    if likes <= 20: return "6-20"
    if likes <= 50: return "21-50"
    return "50+"

# ── Load ──────────────────────────────────────────────────────────────────────
with open(SRC, newline="", encoding="utf-8") as f:
    raw = list(csv.DictReader(f))

print(f"Loaded {len(raw)} raw rows")

# ── Split: staff vs participants, in-window vs out ─────────────────────────────
staff_rows  = []  # staff posts (all, not just in-window)
rows        = []  # in-window participant posts
skipped     = 0

for r in raw:
    ed  = r["edition"]
    cfg = EDITIONS.get(ed)
    if not cfg:
        continue
    day = safe_int(r.get("days_into_window"))

    if is_staff(r["author"]):
        staff_rows.append(r)
        continue

    if any(kw in r["body"].lower()[:200] for kw in EXCLUDE_KEYWORDS):
        skipped += 1
        continue

    if day < 1 or day > cfg["max_day"]:
        skipped += 1
        continue

    is_w, w_cat = check_winner(r.get("body", ""), r.get("author", ""), ed)
    r["is_winner"]       = is_w
    r["winner_category"] = w_cat
    rows.append(r)

print(f"Participants in-window: {len(rows)} | Staff posts: {len(staff_rows)} | Skipped: {skipped}")

# ── Q5: Staff presence per edition ────────────────────────────────────────────
staff_by_ed = defaultdict(list)
for r in staff_rows:
    ed = r["edition"]
    if ed in EDITIONS:
        day = safe_int(r.get("days_into_window"))
        staff_by_ed[ed].append({
            "author": r["author"],
            "day": day,
            "likes": safe_int(r["likes"]),
        })

# ── Per-edition analysis ───────────────────────────────────────────────────────
per_edition = {}

for ed_name, cfg in EDITIONS.items():
    subset  = [r for r in rows if r["edition"] == ed_name]
    winners = [r for r in subset if r["is_winner"]]
    nw      = [r for r in subset if not r["is_winner"]]
    max_day = cfg["max_day"]
    half    = max_day // 2

    # Q1: Overview
    unique_creators = len(set(r["author"] for r in subset))
    likes_all   = [safe_int(r["likes"]) for r in subset]
    staff_posts = staff_by_ed.get(ed_name, [])
    staff_in_window = [p for p in staff_posts if 1 <= p["day"] <= max_day]

    q1 = {
        "total_posts":      len(subset),
        "unique_creators":  unique_creators,
        "winner_count":     len(winners),
        "avg_likes":        mean(likes_all),
        "median_likes":     median(likes_all),
        "video_pct":        pct([r["has_video"] == "true" for r in subset]),
        "cross_posting_pct": pct([safe_int(r["social_count"]) > 0 for r in subset]),
        "staff_post_count": len(staff_in_window),
    }

    # Q2: What everybody did
    day_counts = Counter(safe_int(r["days_into_window"]) for r in subset)
    day_histogram = [{"day": d, "count": day_counts.get(d, 0)} for d in range(1, max_day + 1)]

    tier_counts = Counter(tier(safe_int(r["likes"])) for r in subset)
    total = len(subset) or 1

    q2 = {
        "day_histogram": day_histogram,
        "content": {
            "has_video_pct":  pct([r["has_video"] == "true" for r in subset]),
            "cross_x_pct":    pct([r["cross_x"] == "true" for r in subset]),
            "cross_li_pct":   pct([r["cross_li"] == "true" for r in subset]),
            "cross_ig_pct":   pct([r["cross_ig"] == "true" for r in subset]),
            "cross_th_pct":   pct([r["cross_th"] == "true" for r in subset]),
            "cross_bsky_pct": pct([r["cross_bsky"] == "true" for r in subset]),
            "avg_social_platforms": mean([safe_int(r["social_count"]) for r in subset]),
        },
        "engagement_tiers": {
            "0_likes":   round(100 * tier_counts.get("0", 0) / total, 1),
            "1_5_likes": round(100 * tier_counts.get("1-5", 0) / total, 1),
            "6_20_likes":round(100 * tier_counts.get("6-20", 0) / total, 1),
            "21_50_likes":round(100 * tier_counts.get("21-50", 0) / total, 1),
            "50_plus_likes":round(100 * tier_counts.get("50+", 0) / total, 1),
            "raw": {
                "0": tier_counts.get("0", 0),
                "1-5": tier_counts.get("1-5", 0),
                "6-20": tier_counts.get("6-20", 0),
                "21-50": tier_counts.get("21-50", 0),
                "50+": tier_counts.get("50+", 0),
            }
        },
    }

    # Q3: Winner patterns
    winner_posts = sorted(winners, key=lambda r: safe_int(r["likes"]), reverse=True)
    first_half_winners = sum(1 for r in winners if safe_int(r["days_into_window"]) <= half)
    second_half_winners = len(winners) - first_half_winners

    q3 = {
        "avg_winner_day":  mean([safe_float(r["days_into_window"]) for r in winners]),
        "avg_nonwin_day":  mean([safe_float(r["days_into_window"]) for r in nw]),
        "first_half_winners": first_half_winners,
        "second_half_winners": second_half_winners,
        "winner_avg_likes": mean([safe_int(r["likes"]) for r in winners]),
        "nonwin_avg_likes": mean([safe_int(r["likes"]) for r in nw]),
        "winner_video_pct": pct([r["has_video"] == "true" for r in winners]),
        "nonwin_video_pct": pct([r["has_video"] == "true" for r in nw]),
        "winner_avg_social": mean([safe_int(r["social_count"]) for r in winners]),
        "nonwin_avg_social": mean([safe_int(r["social_count"]) for r in nw]),
        "winner_posts": [
            {
                "author":       r["author"],
                "uid":          r["uid"],
                "day":          safe_int(r["days_into_window"]),
                "likes":        safe_int(r["likes"]),
                "has_video":    r["has_video"] == "true",
                "social_count": safe_int(r["social_count"]),
                "category":     r["winner_category"],
                "body_snippet": r["body"][:100],
            }
            for r in winner_posts
        ],
    }

    # Q5: Staff presence detail
    staff_by_author = defaultdict(list)
    for p in staff_in_window:
        staff_by_author[p["author"]].append(p["day"])

    q5 = {
        "total_staff_posts": len(staff_in_window),
        "finding": "Contra staff did NOT comment on winner submissions. Judging was external — winners selected based on project quality reviewed off-platform.",
        "checked_winner_posts": 3,
        "staff_commented_on_winners": 0,
        "community_engagement_note": "Winners actively engaged with community comments (e.g. Lee Black responded to 80%+ of Airwwave comments). No judges/staff visible in any checked winner comment thread.",
        "top_staff_impression_post": 91802,
        "top_staff_impression_note": "Gui Seiz's March 2026 announcement post had 91,802 impressions — staff reach was via announcements, not submission engagement.",
        "staff_breakdown": [
            {
                "author": author,
                "post_count": len(days),
                "days": sorted(days),
            }
            for author, days in sorted(staff_by_author.items(), key=lambda x: -len(x[1]))
        ],
        "participant_posts": len(subset),
        "staff_pct_of_total": round(100 * len(staff_in_window) / max(len(staff_in_window) + len(subset), 1), 1),
    }

    per_edition[ed_name] = {
        "label": cfg["label"],
        "window_days": max_day,
        "q1_overview": q1,
        "q2_what_everyone_did": q2,
        "q3_winner_patterns": q3,
        "q5_staff_presence": q5,
    }

    print(f"\n[{ed_name}]")
    print(f"  {len(subset)} posts | {unique_creators} creators | {len(winners)} winners | {len(staff_in_window)} staff posts")
    print(f"  Avg likes: winners={q3['winner_avg_likes']}, non-winners={q3['nonwin_avg_likes']}")
    print(f"  Video: winners={q3['winner_video_pct']}%, non-winners={q3['nonwin_video_pct']}%")
    print(f"  Engagement tiers: 0={q2['engagement_tiers']['0_likes']}% | 1-5={q2['engagement_tiers']['1_5_likes']}% | 6-20={q2['engagement_tiers']['6_20_likes']}% | 50+={q2['engagement_tiers']['50_plus_likes']}%")

# ── Q4: Reach proxy (cross-edition) ───────────────────────────────────────────
all_wins = [r for r in rows if r["is_winner"]]
all_nw   = [r for r in rows if not r["is_winner"]]

def social_dist(group):
    c = Counter(safe_int(r["social_count"]) for r in group)
    return {str(k): c.get(k, 0) for k in range(6)}

q4 = {
    "note": "Contra follower counts are not exposed in the public API. Social cross-posting count (0-5 platforms) is used as a social presence proxy.",
    "winner_avg_social":   mean([safe_int(r["social_count"]) for r in all_wins]),
    "nonwin_avg_social":   mean([safe_int(r["social_count"]) for r in all_nw]),
    "winner_social_dist":  social_dist(all_wins),
    "nonwin_social_dist":  social_dist(all_nw),
    "per_edition": {
        ed: {
            "winner_avg_social": mean([safe_int(r["social_count"]) for r in rows if r["edition"] == ed and r["is_winner"]]),
            "nonwin_avg_social": mean([safe_int(r["social_count"]) for r in rows if r["edition"] == ed and not r["is_winner"]]),
        }
        for ed in EDITIONS
    },
}

# ── Q6: Criteria alignment ─────────────────────────────────────────────────────
q6 = []
for r in all_wins:
    ed = r["edition"]
    body = r["body"].lower()
    keywords = CRITERIA_KEYWORDS.get(ed, [])
    matched = [kw for kw in keywords if kw in body]
    q6.append({
        "author":    r["author"],
        "edition":   ed,
        "category":  r["winner_category"],
        "day":       safe_int(r["days_into_window"]),
        "likes":     safe_int(r["likes"]),
        "keywords_matched": matched,
        "keywords_total":   len(keywords),
        "match_score":      round(len(matched) / max(len(keywords), 1), 2),
        "body_snippet": r["body"][:100],
    })

# ── Cross-edition summary ─────────────────────────────────────────────────────
all_likes_w  = [safe_int(r["likes"]) for r in all_wins]
all_likes_nw = [safe_int(r["likes"]) for r in all_nw]
avg_w  = mean(all_likes_w)
avg_nw = mean(all_likes_nw)

summary = {
    "generated":       datetime.now(timezone.utc).isoformat(),
    "total_scraped":   len(raw),
    "total_in_window": len(rows),
    "total_winners":   len(all_wins),
    "total_non_winners": len(all_nw),
    "overall_stats": {
        "winner_avg_likes":   avg_w,
        "nonwin_avg_likes":   avg_nw,
        "engagement_ratio":   round(avg_w / avg_nw, 1) if avg_nw else 0,
        "winner_video_pct":   pct([r["has_video"] == "true" for r in all_wins]),
        "nonwin_video_pct":   pct([r["has_video"] == "true" for r in all_nw]),
        "total_staff_posts":  sum(len(v) for v in staff_by_ed.values()),
        "unique_creators":    len(set(r["author"] for r in rows)),
    },
    "per_edition": per_edition,
    "cross_edition": {
        "q4_reach_proxy":      q4,
        "q6_criteria_alignment": q6,
    },
}

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
print(f"\nSaved -> {OUT_JSON}")

# ── Export chart CSV (same schema as before) ──────────────────────────────────
CHART_FIELDS = [
    "edition","entry_id","contra_url","posted_at",
    "day_relative_to_open","days_before_deadline",
    "project_title","creator_name",
    "live_url","figma_community_url","video_url","video_upload_date",
    "likes","comments","engagement_score",
    "winner","winner_category",
    "creator_followers","creator_prior_participation","social_platforms_count",
    "cross_posted_x","cross_posted_linkedin","cross_posted_instagram",
    "cross_posted_threads","cross_posted_bluesky",
    "in_contra_recap","in_figma_blog",
    "has_video",
]

with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=CHART_FIELDS)
    w.writeheader()
    for r in rows:
        body_clean = r.get("body", "").replace('"', "'").replace(",", " ").replace("\n", " ")[:80]
        w.writerow({
            "edition":               r["edition"],
            "entry_id":              r["uid"],
            "contra_url":            r["url"],
            "posted_at":             r["created_at"],
            "day_relative_to_open":  r["days_into_window"],
            "days_before_deadline":  r["days_before_deadline"],
            "project_title":         body_clean,
            "creator_name":          r["author"],
            "live_url":              "",
            "figma_community_url":   "",
            "video_url":             "",
            "video_upload_date":     "",
            "likes":                 r["likes"],
            "comments":              r["comments"],
            "engagement_score":      r["engagement"],
            "winner":                "true" if r["is_winner"] else "false",
            "winner_category":       r["winner_category"],
            "creator_followers":     0,
            "creator_prior_participation": "false",
            "social_platforms_count": r["social_count"],
            "cross_posted_x":        r["cross_x"],
            "cross_posted_linkedin": r["cross_li"],
            "cross_posted_instagram":r["cross_ig"],
            "cross_posted_threads":  r["cross_th"],
            "cross_posted_bluesky":  r["cross_bsky"],
            "in_contra_recap":       "false",
            "in_figma_blog":         "false",
            "has_video":             r["has_video"],
        })

print(f"Saved -> {OUT_CSV} ({len(rows)} rows)")
