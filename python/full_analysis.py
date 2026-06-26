#!/usr/bin/env python3
"""
Full analysis from scraped_all_6030.csv — real data, all 3 editions.
Outputs:
  data/analysis_results.json          — stats for the report
  astro/public/data/all_entries.csv   — chart-ready CSV
"""
import csv, json, re, statistics
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone

BASE = Path(__file__).parent.parent
DATA = BASE / "data"
SRC  = DATA / "scraped_all_6030.csv"
OUT_JSON = DATA / "analysis_results.json"
OUT_CSV  = BASE / "astro" / "public" / "data" / "all_entries.csv"

# ── Contest windows ────────────────────────────────────────────────────────────
EDITIONS = {
    "Figma Make-a-thon (Sep 2025)": {
        "start": datetime(2025, 9, 3,  tzinfo=timezone.utc),
        "end":   datetime(2025, 9, 10, tzinfo=timezone.utc),
        "max_day": 8,   # inclusive
    },
    "Figma Makeathon March 2026": {
        "start": datetime(2026, 2, 1,  tzinfo=timezone.utc),
        "end":   datetime(2026, 3, 16, tzinfo=timezone.utc),
        "max_day": 44,
    },
    "Config Makeathon 2026": {
        "start": datetime(2026, 6, 4,  tzinfo=timezone.utc),
        "end":   datetime(2026, 6, 18, tzinfo=timezone.utc),
        "max_day": 15,
    },
}

# ── Known winners ─────────────────────────────────────────────────────────────
# Sep 2025
SEP_WINNERS = [
    {"project": "web poetry",        "creator": "cara ellis",       "place": "1st ($50K)"},
    {"project": "plan that trip",    "creator": "johannes specht",  "place": "3rd ($7.5K)"},
    {"project": "package customizer","creator": "daniella marynova","place": "Most Innovative"},
    {"project": "package customizer","creator": "max pradella",     "place": "Most Innovative"},
]
# March 2026
MAR_WINNERS = [
    {"project": "common thread",    "creator": "charlota blunárová","place": "Best Overall"},
    {"project": "common thread",    "creator": "charlota blunarova","place": "Best Overall"},
    {"project": "tokyo",            "creator": "kiel cole",         "place": "Excellence in Craft"},
    {"project": "pucker",           "creator": "aleyna",            "place": "New Interaction"},
    {"project": "airwwave",         "creator": "lee black",         "place": "Boundary Pushing"},
    {"project": "duet booth",       "creator": "paige latimer",     "place": "Reimagining"},
    {"project": "reframe it",       "creator": "dann petty",        "place": "Fan Favorite"},
]
# Config 2026
CONFIG_WINNERS = [
    {"project": "visual atlas",        "creator": "bene brandhofer",   "place": "Grand Prize ($50K)"},
    {"project": "doodle fonts",        "creator": "carlos fernandez",  "place": "2nd Overall ($15K)"},
    {"project": "your eyes can speak", "creator": "nigar naghdaliyeva","place": "Build With Purpose"},
    {"project": "eyetext",             "creator": "nigar naghdaliyeva","place": "Build With Purpose"},
    {"project": "connected earth",     "creator": "lee black",         "place": "Innovative Workflow"},
    {"project": "still here",          "creator": "halle clark",       "place": "Build In Public"},
    {"project": "soundcheck",          "creator": "case ronquillo",    "place": "Community Favorite"},
    {"project": "sound check",         "creator": "case ronquillo",    "place": "Community Favorite"},
]

WINNER_MAP = {
    "Figma Make-a-thon (Sep 2025)": SEP_WINNERS,
    "Figma Makeathon March 2026":   MAR_WINNERS,
    "Config Makeathon 2026":        CONFIG_WINNERS,
}

# Official / announcement posts to exclude
EXCLUDE_AUTHORS = {
    "galaxia wu",     # Contra CEO — announcement posts
    "sabrina polanco",# Contra team
}
EXCLUDE_KEYWORDS = [
    "welcome to the first ever", "the figma make-a-thon is officially",
    "the figma makeathon is officially", "config makeathon is officially",
    "announcing the winners", "meet the winners", "celebrating",
    "judges for the", "join us for",
]

def is_excluded(row):
    author = row["author"].lower()
    body   = row["body"].lower()[:200]
    if author in EXCLUDE_AUTHORS:
        return True
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
        return f if f == f else None  # NaN guard
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

# ── Load data ─────────────────────────────────────────────────────────────────
with open(SRC, newline="", encoding="utf-8") as f:
    raw = list(csv.DictReader(f))

print(f"Loaded {len(raw)} raw rows")

# ── Filter: contest window + non-excluded ─────────────────────────────────────
rows = []
skipped_date = 0
skipped_excl = 0
for r in raw:
    ed = r["edition"]
    cfg = EDITIONS.get(ed)
    if not cfg:
        continue
    day = safe_int(r.get("days_into_window"))
    if day < 1 or day > cfg["max_day"]:
        skipped_date += 1
        continue
    if is_excluded(r):
        skipped_excl += 1
        continue
    # Tag winner
    body   = r.get("body", "")
    author = r.get("author", "")
    is_w, w_cat = check_winner(body, author, ed)
    r["is_winner"]       = is_w
    r["winner_category"] = w_cat
    rows.append(r)

print(f"After filtering: {len(rows)} rows (skipped {skipped_date} out-of-window, {skipped_excl} excluded)")

# ── Per-edition analysis ───────────────────────────────────────────────────────
def edition_stats(subset):
    wins = [r for r in subset if r["is_winner"]]
    nw   = [r for r in subset if not r["is_winner"]]

    def stats_group(group):
        likes   = [safe_int(r["likes"]) for r in group]
        eng     = [safe_int(r["engagement"]) for r in group]
        days    = [safe_float(r["days_into_window"]) for r in group]
        soc     = [safe_int(r["social_count"]) for r in group]
        video   = [r["has_video"] == "true" for r in group]
        return {
            "n":            len(group),
            "avg_likes":    mean(likes),
            "med_likes":    median(likes),
            "avg_eng":      mean(eng),
            "avg_day":      mean(days),
            "med_day":      median(days),
            "avg_social":   mean(soc),
            "video_pct":    pct(video),
            "top_likes":    max(likes) if likes else 0,
        }

    return {
        "total":    len(subset),
        "winners":  stats_group(wins),
        "non_winners": stats_group(nw),
        "top_posts": [
            {"author": r["author"], "likes": safe_int(r["likes"]),
             "day": r["days_into_window"], "is_winner": r["is_winner"],
             "category": r["winner_category"], "body": r["body"][:120]}
            for r in sorted(subset, key=lambda x: safe_int(x["likes"]), reverse=True)[:10]
        ],
    }

results = {}
for ed_name in EDITIONS:
    subset = [r for r in rows if r["edition"] == ed_name]
    results[ed_name] = edition_stats(subset)
    s = results[ed_name]
    w = s["winners"]
    nw = s["non_winners"]
    print(f"\n[{ed_name}]")
    print(f"  Total in window: {s['total']}, winners: {w['n']}, non-winners: {nw['n']}")
    print(f"  Avg likes — winners: {w['avg_likes']}, non-winners: {nw['avg_likes']}")
    print(f"  Avg day — winners: {w['avg_day']}, non-winners: {nw['avg_day']}")
    print(f"  Avg social — winners: {w['avg_social']}, non-winners: {nw['avg_social']}")
    print(f"  Video pct — winners: {w['video_pct']}%, non-winners: {nw['video_pct']}%")
    print(f"  Top by likes:")
    for p in s["top_posts"][:5]:
        flag = " [W]" if p["is_winner"] else ""
        print(f"    {p['likes']:4d} lk | day {p['day']:>2} | {p['author'][:25]:<25}{flag}")

# ── Cross-edition summary ─────────────────────────────────────────────────────
all_wins = [r for r in rows if r["is_winner"]]
all_nw   = [r for r in rows if not r["is_winner"]]

def group_likes(group): return [safe_int(r["likes"]) for r in group]
def group_eng(group):   return [safe_int(r["engagement"]) for r in group]
def group_day(group):   return [safe_float(r["days_into_window"]) for r in group]
def group_soc(group):   return [safe_int(r["social_count"]) for r in group]

total_likes_winners = sum(group_likes(all_wins))
total_likes_nw      = sum(group_likes(all_nw))
avg_w  = mean(group_likes(all_wins))
avg_nw = mean(group_likes(all_nw))
ratio  = round(avg_w / avg_nw, 1) if avg_nw else 0

summary = {
    "total_in_window":  len(rows),
    "total_winners":    len(all_wins),
    "total_non_winners":len(all_nw),
    "winner_avg_likes":  avg_w,
    "non_winner_avg_likes": avg_nw,
    "engagement_ratio":  ratio,
    "winner_avg_day":    mean(group_day(all_wins)),
    "non_winner_avg_day":mean(group_day(all_nw)),
    "winner_avg_social": mean(group_soc(all_wins)),
    "non_winner_avg_social": mean(group_soc(all_nw)),
    "winner_video_pct":  pct([r["has_video"] == "true" for r in all_wins]),
    "non_winner_video_pct": pct([r["has_video"] == "true" for r in all_nw]),
    "editions": results,
}

print(f"\n=== Cross-Edition Summary ===")
print(f"Total in-window posts: {len(rows)}")
print(f"Winners: {len(all_wins)}, Non-winners: {len(all_nw)}")
print(f"Avg likes — winners: {avg_w}, non-winners: {avg_nw}, ratio: {ratio}x")
print(f"Avg post day — winners: {summary['winner_avg_day']}, non-winners: {summary['non_winner_avg_day']}")
print(f"Avg social platforms — winners: {summary['winner_avg_social']}, non-winners: {summary['non_winner_avg_social']}")

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
print(f"\nSaved -> {OUT_JSON}")

# ── Export chart CSV ──────────────────────────────────────────────────────────
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
        })

print(f"Saved -> {OUT_CSV} ({len(rows)} rows)")
