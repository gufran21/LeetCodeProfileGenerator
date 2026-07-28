"""CLI interface for the LeetCode Profile Generator.

Usage:
    leetcode-profile --username gufran21 --theme github_dark --output ./assets
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

import click

from . import __version__
from .cards import (
    generate_badges_card,
    generate_contest_history_card,
    generate_dashboard_card,
    generate_difficulty_card,
    generate_heatmap_card,
    generate_rating_card,
    generate_stats_card,
    generate_streak_card,
)
from .render.themes import Theme, get_theme, list_themes, load_custom_theme
from .services.data_service import LeetCodeDataService


def _setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def _resolve_theme(theme_name: str) -> Theme:
    """Resolve a theme name or JSON path to a Theme object."""
    # Check if it's a file path
    if theme_name.endswith(".json") or os.path.sep in theme_name:
        return load_custom_theme(theme_name)
    return get_theme(theme_name)


def _print_success(label: str, path: str) -> None:
    """Print a success message for a generated card."""
    click.echo(f"  ✓ {label:.<30s} {path}")


def _print_skip(label: str, reason: str) -> None:
    """Print a skip message when a card can't be generated."""
    click.echo(click.style(f"  ⊘ {label:.<30s} {reason}", fg="yellow"))


async def _run(
    username: str,
    theme: Theme,
    output_dir: str,
    generate_stats: bool,
    generate_rating: bool,
    generate_difficulty: bool,
    generate_heatmap: bool,
    generate_streak: bool,
    generate_contest_hist: bool,
    generate_badges: bool,
    generate_dash: bool,
    no_cache: bool,
    cache_ttl: int,
    no_avatar: bool,
    verbose: bool,
) -> int:
    """Main async execution function.

    Returns:
        Exit code (0=success, 1=user not found, 2=API error, 3=rate limited).
    """
    from .api.graphql import APIError, RateLimitError, UserNotFoundError

    _setup_logging(verbose)

    click.echo(f"\n  LeetCode Profile Generator v{__version__}")
    click.echo(f"  Theme: {theme.name}")
    click.echo(f"  User:  {username}\n")

    # Create output directory
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Fetch data
    click.echo("  ⏳ Fetching LeetCode data...")
    start = time.monotonic()

    try:
        service = LeetCodeDataService(
            use_cache=not no_cache,
            cache_ttl=cache_ttl,
            fetch_avatar=not no_avatar,
        )
        data = await service.fetch_user_data(username)
    except UserNotFoundError:
        click.echo(click.style(f"\n  ✗ User '{username}' not found on LeetCode.", fg="red"))
        return 1
    except RateLimitError:
        click.echo(click.style("\n  ✗ Rate limited by LeetCode. Please wait and try again.", fg="red"))
        return 3
    except APIError as e:
        click.echo(click.style(f"\n  ✗ API error: {e}", fg="red"))
        return 2

    elapsed = time.monotonic() - start
    click.echo(f"  ✓ Data fetched in {elapsed:.1f}s\n")

    # Generate cards
    click.echo("  Generating cards:")

    if generate_stats:
        svg = generate_stats_card(data, theme)
        path = str(out_path / "leetcode_stats.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        _print_success("Stats Card", path)

    if generate_rating:
        if data.has_contests:
            svg = generate_rating_card(data, theme)
            path = str(out_path / "rating_history.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            _print_success("Rating History", path)
        else:
            # Still generate placeholder
            svg = generate_rating_card(data, theme)
            path = str(out_path / "rating_history.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            _print_skip("Rating History", "no contest data (placeholder)")

    if generate_difficulty:
        svg = generate_difficulty_card(data, theme)
        path = str(out_path / "difficulty.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        _print_success("Difficulty Chart", path)

    if generate_heatmap:
        svg = generate_heatmap_card(data, theme)
        path = str(out_path / "heatmap.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        _print_success("Submission Heatmap", path)

    if generate_streak:
        svg = generate_streak_card(data, theme)
        path = str(out_path / "streak.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        _print_success("Streak Card", path)

    if generate_contest_hist:
        svg = generate_contest_history_card(data, theme)
        path = str(out_path / "contest_history.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        if data.has_contests:
            _print_success("Contest History", path)
        else:
            _print_skip("Contest History", "no contest data (placeholder)")

    if generate_badges:
        svg = generate_badges_card(data, theme)
        path = str(out_path / "badges.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        if data.has_badges:
            _print_success("Badges Card", path)
        else:
            _print_skip("Badges Card", "no badges (placeholder)")

    if generate_dash:
        svg = generate_dashboard_card(data, theme)
        path = str(out_path / "dashboard.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        _print_success("Dashboard", path)

    total = time.monotonic() - start
    click.echo(f"\n  Done in {total:.1f}s ⚡\n")

    return 0


@click.command("leetcode-profile")
@click.option("--username", "-u", default=None, help="LeetCode username")
@click.option("--theme", "-t", default="github_dark", help="Theme name or path to custom JSON")
@click.option("--output", "-o", default="./assets", help="Output directory for SVG files")
@click.option("--stats/--no-stats", default=True, help="Generate stats card")
@click.option("--rating/--no-rating", default=True, help="Generate rating history graph")
@click.option("--difficulty/--no-difficulty", default=True, help="Generate difficulty distribution")
@click.option("--heatmap/--no-heatmap", default=True, help="Generate submission heatmap")
@click.option("--streak/--no-streak", default=True, help="Generate streak card")
@click.option("--contest-history/--no-contest-history", default=True, help="Generate contest history table")
@click.option("--badges/--no-badges", default=True, help="Generate badges card")
@click.option("--dashboard/--no-dashboard", default=False, help="Generate combined dashboard")
@click.option("--no-cache", is_flag=True, default=False, help="Skip filesystem cache")
@click.option("--cache-ttl", default=86400, type=int, help="Cache TTL in seconds (default: 24h)")
@click.option("--no-avatar", is_flag=True, default=False, help="Skip avatar fetch (pure vector)")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Enable debug logging")
@click.option("--list-themes", is_flag=True, default=False, help="List available themes and exit")
@click.version_option(__version__, prog_name="leetcode-profile")
def main(
    username: str | None,
    theme: str,
    output: str,
    stats: bool,
    rating: bool,
    difficulty: bool,
    heatmap: bool,
    streak: bool,
    contest_history: bool,
    badges: bool,
    dashboard: bool,
    no_cache: bool,
    cache_ttl: int,
    no_avatar: bool,
    verbose: bool,
    list_themes: bool,
) -> None:
    """Generate beautiful SVG dashboards from your LeetCode profile."""
    if list_themes:
        click.echo("\n  Available themes:\n")
        for name in list_themes_fn():
            click.echo(f"    • {name}")
        click.echo()
        return

    if not username:
        click.echo(click.style("\n  ✗ Error: Missing required option '--username' / '-u'.\n", fg="red"))
        sys.exit(1)

    # Resolve theme
    try:
        resolved_theme = _resolve_theme(theme)
    except (ValueError, FileNotFoundError) as e:
        click.echo(click.style(f"\n  ✗ {e}", fg="red"))
        sys.exit(1)

    # Run the async pipeline
    exit_code = asyncio.run(_run(
        username=username,
        theme=resolved_theme,
        output_dir=output,
        generate_stats=stats,
        generate_rating=rating,
        generate_difficulty=difficulty,
        generate_heatmap=heatmap,
        generate_streak=streak,
        generate_contest_hist=contest_history,
        generate_badges=badges,
        generate_dash=dashboard,
        no_cache=no_cache,
        cache_ttl=cache_ttl,
        no_avatar=no_avatar,
        verbose=verbose,
    ))

    sys.exit(exit_code)


# Store reference for --list-themes
list_themes_fn = list_themes


if __name__ == "__main__":
    main()
