"""Badges card generator.

Generates `badges.svg` showing earned LeetCode badges in a grid layout
with upcoming badge progress.
"""

from __future__ import annotations

import math

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.icons import render_icon

# SVG badge icon shapes — vector representations since we can't use raster LeetCode icons
_BADGE_ICONS: dict[str, str] = {
    "medal": "shield",
    "star": "star",
    "trophy": "trophy",
    "fire": "fire",
    "check": "check",
    "code": "code",
    "default": "medal",
}


def _get_badge_icon(category: str) -> str:
    """Map a badge category to an icon name."""
    cat = category.lower()
    if "solving" in cat or "problem" in cat:
        return "star"
    elif "contest" in cat or "ranking" in cat:
        return "trophy"
    elif "streak" in cat or "daily" in cat:
        return "fire"
    elif "study" in cat or "plan" in cat:
        return "code"
    return "medal"


def generate_badges_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the badges card SVG.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme.

    Returns:
        Complete SVG string for the badges card.
    """
    renderer = SVGRenderer(theme)

    padding = 24
    badge_w = 85
    badge_h = 72
    badge_gap = 12
    cols = 4

    badges = data.badges
    upcoming = data.upcoming_badges

    if not badges and not upcoming:
        return _placeholder(renderer, theme, data.profile.username)

    badge_rows = math.ceil(len(badges) / cols) if badges else 0
    header_h = 40
    grid_h = badge_rows * (badge_h + badge_gap) if badge_rows else 0
    upcoming_h = 45 if upcoming else 0

    width = padding * 2 + cols * badge_w + (cols - 1) * badge_gap
    height = padding + header_h + grid_h + upcoming_h + padding

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(renderer.svg_header(
        width, height,
        title=f"{data.profile.username}'s Badges",
    ))

    # ── Defs ──
    svg_parts.append("<defs>")
    if theme.bg_gradient:
        svg_parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    svg_parts.append(renderer.create_drop_shadow("card_shadow", blur=8, offset_y=4, color=theme.shadow_color))
    svg_parts.append("<style>")
    svg_parts.append("""
      @keyframes fadeIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
      .badge-item { animation: fadeIn 0.4s ease-out backwards; }
      @media (prefers-reduced-motion: reduce) { .badge-item { animation: none; } }
    """)
    svg_parts.append("</style>")
    svg_parts.append("</defs>")

    # ── Card background ──
    fill = "url(#bg_grad)" if theme.bg_gradient else theme.bg_color
    svg_parts.append(renderer.rounded_rect(
        0.5, 0.5, width - 1, height - 1,
        rx=theme.border_radius, fill=fill,
        stroke=theme.border_color, stroke_width=1,
        filter_id="card_shadow",
    ))

    # ── Title ──
    svg_parts.append(render_icon("shield", padding, padding + 2, 16, theme.icon_color))
    badge_count_text = f"Badges ({len(badges)} earned)" if badges else "Badges"
    svg_parts.append(renderer.text(
        padding + 22, padding + 15, badge_count_text,
        font_size=16, fill=theme.title_color, weight="bold",
    ))

    # ── Badge grid ──
    grid_y = padding + header_h

    for i, badge in enumerate(badges):
        col = i % cols
        row = i // cols

        x = padding + col * (badge_w + badge_gap)
        y = grid_y + row * (badge_h + badge_gap)

        delay = i * 0.05

        svg_parts.append(f'<g class="badge-item" style="animation-delay: {delay:.2f}s">')

        # Badge card background
        svg_parts.append(renderer.rounded_rect(
            x, y, badge_w, badge_h, rx=8,
            fill=theme.separator_color, stroke=theme.border_color, stroke_width=0.5,
        ))

        # Badge icon
        icon_name = _get_badge_icon(badge.category)
        icon_x = x + (badge_w - 20) / 2
        svg_parts.append(render_icon(icon_name, icon_x, y + 10, 20, theme.accent_color))

        # Badge name (truncate if needed)
        name = badge.short_label
        if len(name) > 10:
            name = name[:9] + "…"
        svg_parts.append(renderer.text(
            x + badge_w / 2, y + 46, name,
            font_size=10, fill=theme.text_color, anchor="middle", weight="600",
        ))

        # Badge date
        if badge.creation_date:
            date_str = badge.creation_date[:10] if len(badge.creation_date) >= 10 else badge.creation_date
            svg_parts.append(renderer.text(
                x + badge_w / 2, y + 60, date_str,
                font_size=8, fill=theme.text_secondary, anchor="middle",
            ))

        svg_parts.append("</g>")

    # ── Upcoming badges ──
    if upcoming:
        upcoming_y = grid_y + grid_h + 8
        up_badge = upcoming[0]  # Show the first upcoming badge

        svg_parts.append(render_icon("chart", padding, upcoming_y + 2, 14, theme.icon_color))
        svg_parts.append(renderer.text(
            padding + 20, upcoming_y + 12,
            f"Upcoming: {up_badge.name} ({up_badge.progress_percentage}%)",
            font_size=11, fill=theme.text_color,
        ))

        # Progress bar
        bar_x = padding + 20
        bar_y = upcoming_y + 22
        bar_w = width - padding * 2 - 20
        svg_parts.append(renderer.progress_bar(
            bar_x, bar_y, bar_w, 8, up_badge.progress_percentage,
            theme.accent_color, theme.progress_bg, theme.progress_radius,
        ))

    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)


def _placeholder(renderer: SVGRenderer, theme: Theme, username: str) -> str:
    """Generate a placeholder when no badges are earned."""
    width, height = 460, 120
    parts: list[str] = []
    parts.append(renderer.svg_header(width, height, title=f"No badges for {username}"))
    parts.append("<defs>")
    if theme.bg_gradient:
        parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    parts.append("</defs>")
    fill = "url(#bg_grad)" if theme.bg_gradient else theme.bg_color
    parts.append(renderer.rounded_rect(0.5, 0.5, width - 1, height - 1, rx=theme.border_radius, fill=fill, stroke=theme.border_color))
    parts.append(render_icon("shield", 24, 24, 16, theme.icon_color))
    parts.append(renderer.text(46, 38, "Badges", font_size=16, fill=theme.title_color, weight="bold"))
    parts.append(renderer.text(width / 2, 75, "No badges earned yet", font_size=13, fill=theme.text_secondary, anchor="middle"))
    parts.append(renderer.text(width / 2, 95, "Keep solving problems to earn badges!", font_size=11, fill=theme.text_secondary, anchor="middle"))
    parts.append(renderer.svg_footer())
    return "\n".join(parts)
