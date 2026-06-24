"""Data models for the makeathon analysis project."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Entry:
    """A single makeathon submission entry."""

    # Identity
    edition: str = ""
    entry_id: str = ""
    contra_url: str = ""

    # Timing
    posted_at: Optional[datetime] = None
    day_relative_to_open: Optional[int] = None
    days_before_deadline: Optional[int] = None

    # Project info
    project_title: str = ""
    creator_name: str = ""
    live_url: Optional[str] = None
    figma_community_url: Optional[str] = None
    video_url: Optional[str] = None
    video_upload_date: Optional[datetime] = None

    # Engagement
    likes: int = 0
    comments: int = 0
    engagement_score: float = 0.0

    # Winner
    winner: bool = False
    winner_category: str = ""

    # Creator profile
    creator_followers: int = 0
    creator_prior_participation: bool = False

    # Social
    social_platforms_count: int = 0
    cross_posted_x: bool = False
    cross_posted_linkedin: bool = False
    cross_posted_instagram: bool = False
    cross_posted_threads: bool = False
    cross_posted_bluesky: bool = False

    # Recap
    in_contra_recap: bool = False
    in_figma_blog: bool = False

    def to_dict(self) -> dict:
        d = asdict(self)
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        return d


@dataclass
class SocialPost:
    """A social media post linked to an entry."""

    entry_id: str = ""
    platform: str = ""  # x, linkedin, instagram, threads, bluesky
    post_url: str = ""
    posted_at: Optional[datetime] = None
    likes: int = 0
    retweets: int = 0
    impressions: int = 0
    comments: int = 0

    def to_dict(self) -> dict:
        d = asdict(self)
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        return d


@dataclass
class AnalysisResult:
    """Summary statistics for the analysis phase."""

    edition: str
    total_entries: int
    total_winners: int
    winner_avg_post_day: float
    non_winner_avg_post_day: float
    winner_avg_engagement: float
    non_winner_avg_engagement: float
    winner_avg_followers: float
    non_winner_avg_followers: float
    winner_avg_social_platforms: float
    non_winner_avg_social_platforms: float
    winner_recap_pct: float
    non_winner_recap_pct: float
    winner_video_pct: float
    non_winner_video_pct: float

    def to_dict(self) -> dict:
        return asdict(self)
