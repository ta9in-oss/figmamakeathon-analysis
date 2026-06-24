"""Playwright-based scraper for Contra community pages and winner metadata."""

import time
import re
from datetime import datetime, timedelta
from typing import Optional

from playwright.sync_api import sync_playwright, Page, Browser

from src.config import (
    EDITIONS,
    Edition,
    REQUEST_DELAY_SECONDS,
    PLAYWRIGHT_TIMEOUT_MS,
    PAGE_LOAD_WAIT_MS,
)
from src.models import Entry, SocialPost


class ContraScraper:
    """Scraper for Contra community topic pages and linked content."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        return self

    def __exit__(self, *args):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def new_page(self) -> Page:
        ctx = self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        )
        self.page = ctx.new_page()
        self.page.set_default_timeout(PLAYWRIGHT_TIMEOUT_MS)
        return self.page

    def scrape_edition_topic(self, edition: Edition) -> list[Entry]:
        """Scrape all entries from an edition's Contra community topic page."""
        entries = []
        page = self.new_page()

        print(f"  Navigating to {edition.topic_url}")
        page.goto(edition.topic_url, wait_until="networkidle")
        time.sleep(PAGE_LOAD_WAIT_MS / 1000)

        # Scroll to load all posts (Contra lazy-loads content)
        self._scroll_to_load(page, max_scrolls=30)

        # Extract post cards
        post_cards = page.query_selector_all('[data-testid="community-post-card"], article, .post-card, [class*="PostCard"]')
        if not post_cards:
            # Fallback: try generic card selectors
            post_cards = page.query_selector_all("a[href*='/community/']")

        print(f"  Found {len(post_cards)} potential post elements")

        for i, card in enumerate(post_cards):
            try:
                entry = self._parse_post_card(card, edition)
                if entry and entry.contra_url:
                    entries.append(entry)
            except Exception as e:
                print(f"    Skipping card {i}: {e}")

            if (i + 1) % 10 == 0:
                print(f"    Processed {i + 1}/{len(post_cards)} cards...")

        return entries

    def scrape_winner_details(self, entry: Entry, edition: Edition) -> Entry:
        """Enrich a winner entry with detailed metadata from its Contra post page."""
        if not entry.contra_url:
            return entry

        page = self.new_page()
        try:
            page.goto(entry.contra_url, wait_until="networkidle")
            time.sleep(REQUEST_DELAY_SECONDS)

            # Project links
            live_link = page.query_selector('a[href*="figma.site"], a[href*="figma.bot"]')
            if live_link:
                entry.live_url = live_link.get_attribute("href")

            figma_link = page.query_selector('a[href*="figma.com/community"]')
            if figma_link:
                entry.figma_community_url = figma_link.get_attribute("href")

            # Video link
            video_link = page.query_selector('a[href*="youtube.com"], a[href*="youtu.be"], a[href*="vimeo.com"]')
            if video_link:
                entry.video_url = video_link.get_attribute("href")

            # Engagement
            likes_el = page.query_selector('[data-testid="like-count"], [class*="like"], [aria-label*="like" i]')
            if likes_el:
                try:
                    entry.likes = int(re.sub(r"\D", "", likes_el.inner_text() or "0"))
                except ValueError:
                    pass

            # Creator profile
            creator_link = page.query_selector('a[href*="/hire/"], a[href*="/profile/"]')
            if creator_link:
                href = creator_link.get_attribute("href") or ""
                entry.creator_name = href.rstrip("/").split("/")[-1] or entry.creator_name

            # Social links in post body
            body = page.inner_text("body").lower()
            if "twitter.com" in body or "x.com" in body:
                entry.cross_posted_x = True
            if "linkedin.com" in body:
                entry.cross_posted_linkedin = True
            if "instagram.com" in body:
                entry.cross_posted_instagram = True
            if "threads.net" in body:
                entry.cross_posted_threads = True
            if "bsky.app" in body:
                entry.cross_posted_bluesky = True

            entry.social_platforms_count = sum([
                entry.cross_posted_x,
                entry.cross_posted_linkedin,
                entry.cross_posted_instagram,
                entry.cross_posted_threads,
                entry.cross_posted_bluesky,
            ])

        except Exception as e:
            print(f"    Error scraping winner details for {entry.contra_url}: {e}")
        finally:
            page.close()

        return entry

    def _parse_post_card(self, card, edition: Edition) -> Optional[Entry]:
        """Parse a single post card element into an Entry."""
        entry = Entry(edition=edition.name)

        # URL
        link = card.query_selector("a[href*='/community/']")
        if not link:
            link = card if card.evaluate("el => el.tagName") == "A" else None
        if link:
            href = link.get_attribute("href") or ""
            if href and not href.startswith("http"):
                href = f"https://contra.com{href}"
            entry.contra_url = href

        if not entry.contra_url:
            return None

        # Title
        title_el = card.query_selector("h1, h2, h3, h4, [class*='title'], [class*='heading']")
        if title_el:
            entry.project_title = title_el.inner_text().strip()

        # Timestamp (resolve relative "X days ago" to absolute)
        time_el = card.query_selector("time, [datetime], [class*='time'], [class*='date'], [class*='ago']")
        if time_el:
            raw_time = time_el.inner_text().strip()
            entry.posted_at = self._resolve_relative_date(raw_time, edition)
            if entry.posted_at:
                entry.day_relative_to_open = (entry.posted_at - edition.start_date).days + 1
                entry.days_before_deadline = (edition.end_date - entry.posted_at).days

        # Likes
        likes_el = card.query_selector('[class*="like"], [class*="heart"], [class*="reaction"]')
        if likes_el:
            try:
                entry.likes = int(re.sub(r"\D", "", likes_el.inner_text() or "0"))
            except ValueError:
                pass

        # Comments
        comments_el = card.query_selector('[class*="comment"], [class*="reply"]')
        if comments_el:
            try:
                entry.comments = int(re.sub(r"\D", "", comments_el.inner_text() or "0"))
            except ValueError:
                pass

        entry.engagement_score = entry.likes + (entry.comments * 2)

        # Winner check
        entry.winner = self._check_winner(entry.project_title, entry.creator_name, edition)
        if entry.winner:
            entry.winner_category = self._get_winner_category(entry.project_title, entry.creator_name, edition)

        return entry

    def _resolve_relative_date(self, text: str, edition: Edition) -> Optional[datetime]:
        """Convert relative date strings like '3 days ago' to absolute datetime."""
        text = text.lower().strip()

        # Check for ISO format first
        iso_match = re.match(r"(\d{4}-\d{2}-\d{2})", text)
        if iso_match:
            return datetime.fromisoformat(iso_match.group(1))

        # Relative patterns
        patterns = [
            (r"(\d+)\s*day", "days"),
            (r"(\d+)\s*week", "weeks"),
            (r"(\d+)\s*month", "days"),  # approximate
            (r"(\d+)\s*hour", "hours"),
            (r"(\d+)\s*minute", "minutes"),
            (r"just now|a moment ago", "now"),
            (r"yesterday", "yesterday"),
            (r"today", "now"),
        ]

        for pattern, unit in patterns:
            m = re.search(pattern, text)
            if m:
                if unit == "now":
                    return datetime.now()
                if unit == "yesterday":
                    return datetime.now() - timedelta(days=1)
                num = int(m.group(1))
                if unit == "days":
                    return datetime.now() - timedelta(days=num)
                if unit == "weeks":
                    return datetime.now() - timedelta(weeks=num)
                if unit == "hours":
                    return datetime.now() - timedelta(hours=num)
                if unit == "minutes":
                    return datetime.now() - timedelta(minutes=num)

        return None

    def _check_winner(self, title: str, creator: str, edition: Edition) -> bool:
        """Check if an entry matches a known winner."""
        title_lower = title.lower().strip()
        creator_lower = creator.lower().strip()
        for w in edition.winner_seed:
            w_title = (w.get("project") or "").lower().strip()
            w_creator = (w.get("creator") or "").lower().strip()
            if w_title and w_title in title_lower:
                return True
            if w_creator and w_creator in creator_lower:
                return True
        return False

    def _get_winner_category(self, title: str, creator: str, edition: Edition) -> str:
        """Get the winner category for a matching entry."""
        title_lower = title.lower().strip()
        creator_lower = creator.lower().strip()
        for w in edition.winner_seed:
            w_title = (w.get("project") or "").lower().strip()
            w_creator = (w.get("creator") or "").lower().strip()
            if (w_title and w_title in title_lower) or (w_creator and w_creator in creator_lower):
                return w.get("place", "")
        return ""

    def _scroll_to_load(self, page: Page, max_scrolls: int = 30):
        """Scroll the page to trigger lazy loading of content."""
        last_height = page.evaluate("document.body.scrollHeight")
        scrolls = 0
        while scrolls < max_scrolls:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(REQUEST_DELAY_SECONDS)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls += 1


def scrape_youtube_metadata(video_url: str) -> Optional[datetime]:
    """Fetch YouTube video upload date via oEmbed."""
    import httpx
    oembed_url = f"https://www.youtube.com/oembed?url={video_url}&format=json"
    try:
        resp = httpx.get(oembed_url, timeout=10)
        if resp.status_code == 200:
            # oEmbed doesn't include upload date directly — use page meta fallback
            pass
    except Exception:
        pass
    return None
