"""Analysis and visualization module — computes derived fields, runs statistical comparisons, and generates plotly charts."""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Optional

from src.models import Entry, AnalysisResult

OUTPUT_DIR = Path("output/figures")


def load_data(all_entries_path: str = "data/all_entries.csv") -> pd.DataFrame:
    """Load the scraped entries CSV into a DataFrame."""
    df = pd.read_csv(all_entries_path, parse_dates=["posted_at"])
    return df


def compute_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Compute derived analysis fields if not already present."""
    if "engagement_score" not in df.columns or df["engagement_score"].isna().all():
        df["engagement_score"] = df["likes"].fillna(0) + (df["comments"].fillna(0) * 2)

    if "social_coverage" not in df.columns or df.get("social_coverage").isna().all():
        social_cols = ["cross_posted_x", "cross_posted_linkedin", "cross_posted_instagram", "cross_posted_threads", "cross_posted_bluesky"]
        available = [c for c in social_cols if c in df.columns]
        if available:
            df["social_coverage"] = df[available].fillna(False).astype(int).sum(axis=1)
        else:
            df["social_coverage"] = df.get("social_platforms_count", 0)

    df["winner_bool"] = df["winner"].fillna(False).astype(bool)
    return df


def run_analysis(df: pd.DataFrame, edition_name: Optional[str] = None) -> AnalysisResult:
    """Run cross-entry statistical analysis."""
    subset = df[df["edition"] == edition_name] if edition_name else df

    winners = subset[subset["winner_bool"] == True]
    non_winners = subset[subset["winner_bool"] == False]

    def safe_mean(series):
        return series.dropna().mean() if len(series.dropna()) > 0 else 0

    return AnalysisResult(
        edition=edition_name or "All Editions",
        total_entries=len(subset),
        total_winners=len(winners),
        winner_avg_post_day=safe_mean(winners.get("day_relative_to_open")),
        non_winner_avg_post_day=safe_mean(non_winners.get("day_relative_to_open")),
        winner_avg_engagement=safe_mean(winners.get("engagement_score")),
        non_winner_avg_engagement=safe_mean(non_winners.get("engagement_score")),
        winner_avg_followers=safe_mean(winners.get("creator_followers")),
        non_winner_avg_followers=safe_mean(non_winners.get("creator_followers")),
        winner_avg_social_platforms=safe_mean(winners.get("social_coverage")),
        non_winner_avg_social_platforms=safe_mean(non_winners.get("social_coverage")),
        winner_recap_pct=safe_mean(winners.get("in_contra_recap").fillna(False).astype(float)) * 100,
        non_winner_recap_pct=safe_mean(non_winners.get("in_contra_recap").fillna(False).astype(float)) * 100,
        winner_video_pct=safe_mean(winners["video_url"].notna().fillna(False).astype(float)) * 100 if "video_url" in winners.columns else 0,
        non_winner_video_pct=safe_mean(non_winners["video_url"].notna().fillna(False).astype(float)) * 100 if "video_url" in non_winners.columns else 0,
    )


def create_timing_chart(df: pd.DataFrame, edition_name: Optional[str] = None) -> go.Figure:
    """Post timing distribution: winners vs non-winners (histogram)."""
    subset = df[df["edition"] == edition_name] if edition_name else df
    title_suffix = f" — {edition_name}" if edition_name else ""

    fig = go.Figure()
    for label, color, group in [("Winners", "#7C3AED", True), ("Non-Winners", "#94A3B8", False)]:
        data = subset[subset["winner_bool"] == group]["day_relative_to_open"].dropna()
        if len(data) > 0:
            fig.add_trace(go.Histogram(
                x=data, name=label, marker_color=color, opacity=0.75,
                xbins=dict(start=1, end=max(data.max(), 10), size=1),
            ))

    fig.update_layout(
        title=f"When Did Winners Post vs Everyone Else?{title_suffix}",
        xaxis_title="Day of Submission Window (Day 1 = window opened)",
        yaxis_title="Number of Entries",
        barmode="overlay",
        template="plotly_white",
        height=500,
    )
    return fig


def create_engagement_scatter(df: pd.DataFrame, edition_name: Optional[str] = None) -> go.Figure:
    """Engagement vs posting day scatter with winner highlighting."""
    subset = df[df["edition"] == edition_name] if edition_name else df
    title_suffix = f" — {edition_name}" if edition_name else ""

    fig = px.scatter(
        subset.dropna(subset=["day_relative_to_open", "engagement_score"]),
        x="day_relative_to_open",
        y="engagement_score",
        color="winner_bool",
        color_discrete_map={True: "#7C3AED", False: "#94A3B8"},
        labels={"winner_bool": "Winner"},
        hover_data=["project_title", "creator_name", "likes", "comments"],
        title=f"Engagement vs Posting Day{title_suffix}",
        template="plotly_white",
        height=500,
    )
    fig.update_traces(marker=dict(size=10, opacity=0.7))
    return fig


def create_comparison_boxplots(df: pd.DataFrame, edition_name: Optional[str] = None) -> go.Figure:
    """Side-by-side box plots comparing winners vs non-winners across key metrics."""
    subset = df[df["edition"] == edition_name] if edition_name else df
    title_suffix = f" — {edition_name}" if edition_name else ""

    metrics = [
        ("day_relative_to_open", "Posting Day"),
        ("engagement_score", "Engagement Score"),
        ("creator_followers", "Creator Followers"),
        ("social_coverage", "Social Platforms"),
    ]

    fig = make_subplots(rows=2, cols=2, subplot_titles=[m[1] for m in metrics])

    for i, (col, label) in enumerate(metrics):
        row, col_idx = i // 2 + 1, i % 2 + 1
        if col not in subset.columns:
            continue
        for winner_bool, name, color in [(True, "Winners", "#7C3AED"), (False, "Non-Winners", "#94A3B8")]:
            data = subset[subset["winner_bool"] == winner_bool][col].dropna()
            if len(data) > 0:
                fig.add_trace(
                    go.Box(y=data, name=name, marker_color=color, showlegend=(i == 0)),
                    row=row, col=col_idx,
                )

    fig.update_layout(
        title=f"Winners vs Non-Winners: Key Metrics{title_suffix}",
        template="plotly_white",
        height=700,
        showlegend=True,
    )
    return fig


def create_recap_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart showing recap inclusion rates."""
    metrics = {
        "In Contra Recap": "in_contra_recap",
        "In Figma Blog": "in_figma_blog",
    }
    categories = ["Winners", "Non-Winners"]
    winner_pcts = []
    non_winner_pcts = []

    for label, col in metrics.items():
        if col not in df.columns:
            continue
        w = df[df["winner_bool"] == True][col].fillna(False).astype(float).mean() * 100
        nw = df[df["winner_bool"] == False][col].fillna(False).astype(float).mean() * 100
        winner_pcts.append(w)
        non_winner_pcts.append(nw)

    fig = go.Figure(data=[
        go.Bar(name="Winners", x=list(metrics.keys()), y=winner_pcts, marker_color="#7C3AED"),
        go.Bar(name="Non-Winners", x=list(metrics.keys()), y=non_winner_pcts, marker_color="#94A3B8"),
    ])
    fig.update_layout(
        title="Recap & Blog Inclusion: Winners vs Non-Winners",
        yaxis_title="Percentage Included (%)",
        template="plotly_white",
        height=400,
        barmode="group",
    )
    return fig


def generate_all_charts(df: pd.DataFrame, edition_name: Optional[str] = None) -> list[Path]:
    """Generate all charts and save to output/figures/."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prefix = edition_name.replace(" ", "_").replace("(", "").replace(")", "").lower() if edition_name else "all"
    paths = []

    charts = [
        ("timing_histogram", create_timing_chart(df, edition_name)),
        ("engagement_scatter", create_engagement_scatter(df, edition_name)),
        ("comparison_boxplots", create_comparison_boxplots(df, edition_name)),
        ("recap_inclusion", create_recap_chart(df)),
    ]

    for name, fig in charts:
        path = OUTPUT_DIR / f"{prefix}_{name}.html"
        fig.write_html(str(path))
        paths.append(path)

    return paths


def print_summary(result: AnalysisResult):
    """Print a formatted summary of the analysis."""
    print(f"\n{'='*60}")
    print(f"  ANALYSIS SUMMARY — {result.edition}")
    print(f"{'='*60}")
    print(f"  Total entries:          {result.total_entries}")
    print(f"  Total winners:          {result.total_winners}")
    print(f"  {'Metric':<35} {'Winners':>10} {'Non-Winners':>10}")
    print(f"  {'-'*55}")
    print(f"  {'Avg Post Day':<35} {result.winner_avg_post_day:>10.1f} {result.non_winner_avg_post_day:>10.1f}")
    print(f"  {'Avg Engagement Score':<35} {result.winner_avg_engagement:>10.1f} {result.non_winner_avg_engagement:>10.1f}")
    print(f"  {'Avg Creator Followers':<35} {result.winner_avg_followers:>10.1f} {result.non_winner_avg_followers:>10.1f}")
    print(f"  {'Avg Social Platforms':<35} {result.winner_avg_social_platforms:>10.1f} {result.non_winner_avg_social_platforms:>10.1f}")
    print(f"  {'Recap Inclusion %':<35} {result.winner_recap_pct:>10.1f} {result.non_winner_recap_pct:>10.1f}")
    print(f"  {'Video Presence %':<35} {result.winner_video_pct:>10.1f} {result.non_winner_video_pct:>10.1f}")
    print(f"{'='*60}\n")
