"""Inline SVG icon paths for use in card rendering.

All icons are designed for a 24×24 viewBox and specified as SVG path data.
They are rendered inline within the SVG output — no external assets needed.
"""

from __future__ import annotations

# Each icon is a dict with 'path' (SVG path data) and 'viewbox' (original viewbox)
# All icons use a 24×24 coordinate system

ICONS: dict[str, str] = {
    # LeetCode Logo
    "leetcode": (
        "M13.483 0a1.374 1.374 0 0 0-.961.438L7.17 5.79a1.374 1.374 0 0 0 0 1.941.97.97 0 0 0 1.37 0l5.353-5.352a.456.456 0 0 1 .645 0l2.368 2.368a.456.456 0 0 1 0 .645L11.554 10.74a.456.456 0 0 1-.645 0L8.54 8.373a.97.97 0 0 0-1.37 0 1.374 1.374 0 0 0 0 1.941l2.368 2.368a2.4 2.4 0 0 0 3.393 0l5.353-5.353a2.4 2.4 0 0 0 0-3.393L16.082.438A1.374 1.374 0 0 0 14.444 0zM7.17 12.353a1.374 1.374 0 0 0-.961.438L.857 18.143a2.4 2.4 0 0 0 0 3.393l2.368 2.368a2.4 2.4 0 0 0 3.393 0l5.353-5.353a1.374 1.374 0 0 0 0-1.941.97.97 0 0 0-1.37 0l-5.353 5.353a.456.456 0 0 1-.645 0L2.235 21.595a.456.456 0 0 1 0-.645l5.353-5.353a.456.456 0 0 1 .645 0 .97.97 0 0 0 1.37 0 1.374 1.374 0 0 0 0-1.941l-2.368-2.368a1.374 1.374 0 0 0-.065-.935z"
    ),

    # Trophy — contest/ranking achievement
    "trophy": (
        "M7 4V2h10v2h3v4c0 1.1-.9 2-2 2h-1.16A5.98 5.98 0 0 1 12 16a5.98 5.98 0 0 1-4.84-6H6c-1.1 "
        "0-2-.9-2-2V4h3Zm-1 2H5v2h1V6Zm12 0h-1v2h1V6ZM12 18l-3 3h6l-3-3Z"
    ),

    # Fire — streak flame
    "fire": (
        "M13.5 2C13.5 2 7 8.5 7 14C7 17.58 9.92 20.5 13.5 20.5C17.08 20.5 20 17.58 20 "
        "14C20 12.2 19.3 10.5 18.2 9.2C17.9 10.5 17 11.5 15.8 11.8C15.8 9.5 14.7 7 13.5 2Z"
    ),

    # Lightning bolt — rating/performance
    "lightning": "M13 2L3 14h9l-1 8 10-12h-9l1-8Z",

    # Chart line — graph/stats
    "chart": (
        "M3 13h2v8H3v-8Zm4-4h2v12H7V9Zm4-4h2v16h-2V5Zm4 8h2v8h-2v-8Zm4-6h2v14h-2V7Z"
    ),

    # Code brackets — programming
    "code": (
        "M8 5l-5 7 5 7 1.41-1.41L4.83 12l4.58-5.59L8 5Zm8 0l5 7-5 7-1.41-1.41L19.17 "
        "12l-4.58-5.59L16 5Z"
    ),

    # Star — highlight/peak
    "star": (
        "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 "
        "3.25L7 14.14 2 9.27l6.91-1.01L12 2Z"
    ),

    # Checkmark — solved/completed
    "check": "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17Z",

    # Globe — global ranking
    "globe": (
        "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2Zm-1 17.93c-3.95-.49-7-3.85"
        "-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93Zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1"
        "v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 "
        "7.41 0 2.08-.8 3.97-2.1 5.39Z"
    ),

    # Medal — contests/badges
    "medal": (
        "M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V21l4-2 4 2v-6.26c1.81-1.27 3-3.36 "
        "3-5.74 0-3.87-3.13-7-7-7Zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5Z"
    ),

    # Calendar — schedule/dates
    "calendar": (
        "M19 3h-1V1h-2v2H8V1H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 "
        "2-2V5c0-1.1-.9-2-2-2Zm0 16H5V8h14v11Z"
    ),

    # Arrow up — positive change
    "arrow_up": "M7 14l5-5 5 5H7Z",

    # Arrow down — negative change
    "arrow_down": "M7 10l5 5 5-5H7Z",

    # Shield — badge
    "shield": (
        "M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4Zm0 "
        "10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8Z"
    ),

    # User — profile
    "user": (
        "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4Zm0 2c-2.67 "
        "0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4Z"
    ),

    # Target/bullseye — acceptance rate
    "target": (
        "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2Zm0 18c-4.42 "
        "0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8Zm0-14c-3.31 0-6 2.69-6 6s2.69 6 6 "
        "6 6-2.69 6-6-2.69-6-6-6Zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 "
        "4-4 4Zm0-6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2Z"
    ),

    # Lock — locked badge
    "lock": (
        "M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 "
        "2-.9 2-2V10c0-1.1-.9-2-2-2ZM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6Zm9 14H6V10h12v10Z"
    ),
}

ICON_VIEWBOX = "0 0 24 24"


def render_icon(
    name: str,
    x: float,
    y: float,
    size: float = 16,
    fill: str = "#ffffff",
) -> str:
    """Render an inline SVG icon as a <g> element.

    Args:
        name: Icon name (key in ICONS dict).
        x: X position.
        y: Y position.
        size: Icon size in pixels (width and height).
        fill: Fill color.

    Returns:
        SVG markup string for the icon, or empty string if icon not found.
    """
    path_data = ICONS.get(name)
    if not path_data:
        return ""

    scale = size / 24.0
    return (
        f'<g transform="translate({x},{y}) scale({scale})">'
        f'<path d="{path_data}" fill="{fill}"/>'
        f"</g>"
    )
