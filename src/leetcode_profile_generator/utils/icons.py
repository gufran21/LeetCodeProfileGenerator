"""Inline SVG icon paths for use in card rendering.

All icons are designed for a 24×24 viewBox and specified as SVG path data.
They are rendered inline within the SVG output — no external assets needed.
"""

from __future__ import annotations

# Each icon is a dict with 'path' (SVG path data) and 'viewbox' (original viewbox)
# All icons use a 24×24 coordinate system

ICONS: dict[str, str] = {
    # Trophy — contest/ranking achievement
    "trophy": (
        "M7 4V2h10v2h3v4c0 1.1-.9 2-2 2h-1.16A5.98 5.98 0 0 1 12 16a5.98 5.98 0 0 1-4.84-6H6c-1.1 "
        "0-2-.9-2-2V4h3Zm-1 2H5v2h1V6Zm12 0h-1v2h1V6ZM12 18l-3 3h6l-3-3Z"
    ),

    # Fire — streak
    "fire": (
        "M12 23c-4.97 0-8-3.58-8-8 0-3.07 2.17-6.09 4-7.87.43-.42 1.14-.09 1.08.5-.13 1.3.19 2.4 "
        "1.42 3.19C11.2 8.55 12 6 12 3c0-.55.47-.94.97-.72C16.03 3.81 20 7.58 20 15c0 4.42-3.03 "
        "8-8 8Zm0-2c2.76 0 5-2.24 5-5 0-2.28-1.11-4.55-2.7-6.14-.41.78-.97 1.63-1.72 2.43a1 1 0 "
        "0 1-1.58-.11c-.78-1.17-1.06-2.5-.98-3.74C8.72 10.6 7 13.18 7 15c0 2.76 2.24 5 5 5Z"
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
