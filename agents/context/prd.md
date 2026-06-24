PROJECT SPEC: Figma x Contra Makeathon Analysis
Project Goal
Scrape, aggregate, and analyze all publicly available data across every Figma x Contra makeathon edition to answer one core question: What separates winners from everyone else — and is early posting the dominant variable?
The output is a data-backed community report published as a web page or interactive article.

Known Editions
There are 3 editions to cover:
EditionDatesPrize PoolPlatformFigma Make-a-thon (1st)Sep 3–10, 2025$100Kcontra.com/community/topic/figmamakeathonFigma Makeathon March 2026~Feb–Mar 16, 2026$100Kcontra.com/community/topic/figmamakeathonmarch2026Config Makeathon 2026Jun 4–18, 2026$100Kcontra.com/community/topic/configmakeathon

Known Winners (seed data — agent must complete and verify)
Sep 2025 Make-a-thon:

1st ($50K): "Web Poetry" — Cara Ellis
2nd ($15K): unknown
3rd ($7.5K): "Plan That Trip. Now" — Johannes Specht
Most Creative: unknown
Most Innovative: "Package Customizer" — Daniella Marynova & Max Pradella
Best Prompt: unknown

March 2026 Makeathon:

Best Overall: "Common Thread" — Charlota Blunárová → figma.bot/476bnit
Excellence in Craft: "TOKYO" — Kiel Cole → figma.bot/479fyKm
New Interaction: "Pucker" — Aleyna Çatak → figma.bot/417D3jl
Boundary Pushing: "Airwwave" — Lee Black → figma.bot/4lyJSnm
Reimagining Iconic Interactions: "Duet Booth" — Paige Latimer → figma.bot/4bpSesV
Fan Favorite on Social: "Reframe It" — Dann Petty → figma.bot/4lzmkyJ

Config Makeathon 2026 (Jun 4–18):

Winners announced live at Config June 23 at 2PM PDT at Moscone — agent must scrape the announcement post-event from contra.com/community/topic/configmakeathon and Figma/Contra social channels.


Data Collection Tasks
Phase 1 — Winners Deep Dive
For each winner across all editions:

Contra post data:

Post URL
Post timestamp (date + time posted)
Day relative to submission window open (Day 1 = first day of submission period)
Likes / hearts count
Comments count
Profile of submitter (Contra follower count, account age, prior makeathon participation)


Submission content:

Live URL (figma.site or external)
Figma community file link (if any)
Video/YouTube preview link (if any) — check video upload date metadata
Social links posted (X/Twitter, Instagram, Threads, LinkedIn, Bluesky)
Number of social platforms cross-posted to


Social traction:

X/Twitter post date, likes, retweets, impressions (public)
LinkedIn post date + engagement
Instagram/Threads if available
Was it included in an official Contra/Figma recap or pinned post? Y/N


Recap inclusion:

Was the project featured in Contra's community recap post?
Was it in the official Figma blog post post-event?
Announcement source URLs



Phase 2 — All Entries
For each edition, scrape all posts from the community topic page:

Contra post URL
Post timestamp
Day relative to window open
Likes + comments
Whether winner: Y/N / which category
Whether cross-posted socially: Y/N (check if social links present in post body)
Submitter follower count on Contra

Phase 3 — Computed Analysis Fields
For each entry, compute:

days_before_deadline: how many days before close they posted
engagement_score: likes + (comments × 2)
social_coverage: number of platforms linked
winner: boolean

Cross-entry analysis to run:

Distribution of post timing (Day 1–N) for winners vs non-winners
Correlation between posting day and engagement score
Correlation between posting day and winning
Average Contra follower count — winners vs non-winners
Cross-platform social presence — winners vs non-winners
% of winners that were in official recap posts
% of winners that posted social links in their submission
Video presence — winners vs non-winners


Data Sources & Scraping Strategy
Primary sources (agent must fetch):
# Contra community topic pages (paginate through all posts)
https://contra.com/community/topic/figmamakeathon
https://contra.com/community/topic/figmamakeathonmarch2026
https://contra.com/community/topic/configmakeathon

# Figma blog winner posts
https://www.figma.com/blog/6-winning-figma-makes-and-what-you-can-learn-from-them/
https://contra.com/community/neIDybLs-explore-the-innovative-winners-of-figmas
https://contra.com/community/6OZFlCWv-explore-projects-from-figma-makeathon-challenges

# Winner project links (fetch each for metadata)
https://figma.bot/476bnit  # Common Thread
https://figma.bot/479fyKm  # TOKYO
https://figma.bot/417D3jl  # Pucker
https://figma.bot/4lyJSnm  # Airwwave
https://figma.bot/4bpSesV  # Duet Booth
https://figma.bot/4lzmkyJ  # Reframe It

# Announcement references
https://config.figma.com/san-francisco/event/52f50783-e30a-4a98-9039-fab3d9f04fa4/
https://luma.com/z3s4o6g8   # Sep 2025 winners announcement event
https://x.com/figma/status/1968007805203517458  # Sep 2025 winners tweet
Social scraping:

Search X for #figmamakeathon, #figmamakeathonmarch2026, #configmakeathon — collect posts, sort by date, note engagement
Search for each winner's name / project name on X and LinkedIn for cross-post data


Output Format
1. Raw data — CSV files

winners.csv — all winners across editions, all fields
all_entries.csv — every scraped entry, all fields
social_posts.csv — linked social posts per entry

2. Analysis notebook / script

Python (pandas + matplotlib/seaborn or plotly)
Charts: posting day distribution, engagement vs timing scatter, winner vs non-winner box plots

3. Report — publishable article (Markdown → web)
Sections:

The Pattern — executive summary of what the data shows
Edition-by-Edition Breakdown — timeline + winner table per edition
The Timing Effect — chart: when did winners post vs everyone else?
The Social Multiplier — did cross-posting correlate with winning?
The Recap Game — were recaps decided early?
What This Means for You — actionable checklist for the next makeathon
Raw Data — link to CSV / GitHub


Agent Notes

Contra community pages are JavaScript-rendered. Use Playwright or Puppeteer for scraping, not plain HTTP fetch.
Timestamps on Contra posts are relative ("3 days ago") — resolve to absolute dates using the known submission window dates as anchor.
If video links are YouTube, fetch the video's uploadDate from the page <meta> or oEmbed API — this is key evidence for "was the idea already done."
For Config 2026 winners (just announced today June 23), the announcement may land on contra.com/community/topic/configmakeathon within hours — poll that page.
Rate-limit scraping, respect robots.txt, add delays between requests.
If Contra blocks scraping, fall back to manual extraction of visible post data + browser automation with human-in-the-loop confirmation.


Stack Suggestion (just a suggestion use what helps)
Python
├── playwright (Contra page scraping)
├── httpx (static fetches)
├── pandas (data wrangling)
├── plotly (interactive charts)
└── jinja2 or mdx (report generation)
