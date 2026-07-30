"""Stats card generator — profile overview card.

Generates modern `leetcode_stats.svg` featuring user avatar, username,
top-right rating & level badge, and a clean performance grid.
"""

from __future__ import annotations

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.icons import render_icon
from ..utils.math import format_number


def _determine_level(data: LeetCodeData) -> str:
    """Determine the user's LeetCode level title."""
    if data.contest and data.contest.badge_name:
        return data.contest.badge_name

    rating = data.contest.rating if data.contest else 0.0
    solved = data.solved.total_solved

    if rating >= 2200 or solved >= 1000:
        return "Guardian"
    elif rating >= 1600 or solved >= 500:
        return "Knight"
    elif solved >= 250:
        return "Advanced"
    elif solved >= 100:
        return "Intermediate"
    return "Novice"


def generate_stats_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the stats overview card SVG.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme for rendering.

    Returns:
        Complete SVG string for the stats card.
    """
    renderer = SVGRenderer(theme)

    width = 470
    height = 170
    padding = 22

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(
        renderer.svg_header(
            width,
            height,
            title=f"{data.profile.username}'s LeetCode Stats",
            desc=f"LeetCode profile stats for {data.profile.username}",
        )
    )

    # ── Defs ──
    svg_parts.append("<defs>")
    if theme.bg_gradient:
        svg_parts.append(
            renderer.create_gradient(
                "bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]
            )
        )
    svg_parts.append(
        renderer.create_drop_shadow(
            "card_shadow", blur=8, offset_y=4, color=theme.shadow_color
        )
    )

    svg_parts.append("<style>")
    svg_parts.append("""
      @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
      .card-content { animation: fadeIn 0.4s ease-out; }
      @media (prefers-reduced-motion: reduce) {
        .card-content { animation: none; }
      }
    """)
    svg_parts.append("</style>")
    svg_parts.append("</defs>")

    # ── Card background ──
    fill = "url(#bg_grad)" if theme.bg_gradient else theme.bg_color
    svg_parts.append(
        renderer.rounded_rect(
            0.5,
            0.5,
            width - 1,
            height - 1,
            rx=theme.border_radius,
            fill=fill,
            stroke=theme.border_color,
            stroke_width=1,
            filter_id="card_shadow",
        )
    )

    svg_parts.append('<g class="card-content">')

    # ── Row 1: Profile Info (Left: Avatar + Name, Right: Rating + Level Badge) ──
    y = padding
    avatar_size = 42

    # Avatar (circular clip for base64 image, fallback to SVG placeholder icon)
    if data.avatar_b64:
        clip_id = "avatar_clip"
        cx = padding + avatar_size / 2
        cy = y + avatar_size / 2
        svg_parts.append(
            f'<clipPath id="{clip_id}"><circle cx="{cx}" cy="{cy}" r="{avatar_size / 2}"/></clipPath>'
        )
        svg_parts.append(
            f'<image x="{padding}" y="{y}" width="{avatar_size}" height="{avatar_size}" '
            f'href="{data.avatar_b64}" clip-path="url(#{clip_id})" preserveAspectRatio="xMidYMid slice"/>'
        )
    else:
        cx = padding + avatar_size / 2
        cy = y + avatar_size / 2
        svg_parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{avatar_size / 2}" fill="{theme.separator_color}" stroke="{theme.border_color}" stroke-width="1"/>'
        )
        svg_parts.append(
            render_icon("user", padding + 9, y + 9, 24, theme.text_secondary)
        )

    text_x = padding + avatar_size + 12

    # Swap hierarchy: Real Name is Primary (top, 18px), Username is Secondary (bottom, 11px)
    real_name = data.profile.real_name
    has_real_name = bool(real_name and real_name != data.profile.username)
    primary_name: str = real_name if (has_real_name and real_name is not None) else data.profile.username
    secondary_name: str | None = f"@{data.profile.username}" if has_real_name else None

    # Primary Name (18px, bold)
    svg_parts.append(
        renderer.text(
            text_x,
            y + 18,
            primary_name,
            font_size=18,
            fill=theme.title_color,
            weight="bold",
        )
    )

    # Level Pill Badge directly beside Primary Name
    level_title = _determine_level(data)
    level_text = f"Level: {level_title}"
    approx_name_w = len(primary_name) * 10.2
    pill_x = text_x + approx_name_w + 10
    pill_y = y + 2
    pill_w = len(level_text) * 6.8 + 22
    gold_accent = "#ffa116"

    svg_parts.append(
        f'<rect x="{pill_x}" y="{pill_y}" width="{pill_w}" height="20" rx="10" '
        f'fill="{theme.separator_color}" fill-opacity="0.6" '
        f'stroke="{gold_accent}" stroke-width="0.8"/>'
    )
    svg_parts.append(
        render_icon("shield", pill_x + 6, pill_y + 4, 12, gold_accent)
    )
    svg_parts.append(
        renderer.text(
            pill_x + 21,
            pill_y + 14,
            level_text,
            font_size=10,
            fill=gold_accent,
            weight="bold",
        )
    )

    # Secondary Name / Username (11px)
    if secondary_name:
        svg_parts.append(
            renderer.text(
                text_x,
                y + 36,
                secondary_name,
                font_size=11,
                fill=theme.text_secondary,
            )
        )

    # Right side of Row 1: Rating lightning badge in #ffa116 color
    right_x = width - padding

    if data.contest and data.contest.has_competed:
        rating_val = f"{data.contest.rating:.0f}"
        rating_yellow = "#ffa116"
        svg_parts.append(
            render_icon("lightning", right_x - 68, y + 10, 18, rating_yellow)
        )
        svg_parts.append(
            renderer.text(
                right_x - 46,
                y + 26,
                rating_val,
                font_size=18,
                fill=rating_yellow,
                weight="bold",
                anchor="start",
            )
        )

    # ── Separator ──
    sep_y = y + avatar_size + 14
    svg_parts.append(
        f'<line x1="{padding}" y1="{sep_y}" x2="{width - padding}" y2="{sep_y}" '
        f'stroke="{theme.separator_color}" stroke-width="1"/>'
    )

    # ── Row 2: Stats Grid (2 columns × 3 items) ──
    grid_y = sep_y + 16
    col1_x = padding
    col2_x = width / 2 + 10
    row_h = 24
    icon_size = 14
    label_size = 11
    value_size = 12

    stats_items: list[tuple[str, str, str, float, float]] = []

    if data.contest and data.contest.has_competed:
        stats_items.extend([
            ("globe", "Global Rank", f"#{format_number(data.contest.global_ranking)}", col1_x, grid_y),
            ("chart", "Top", f"{data.contest.top_percentage:.1f}%", col2_x, grid_y),
            ("check", "Total Solved", f"{format_number(data.solved.total_solved)}", col1_x, grid_y + row_h),
            ("target", "Acceptance", f"{data.solved.acceptance_rate:.1f}%", col2_x, grid_y + row_h),
            ("medal", "Contests", str(data.contest.attended_count), col1_x, grid_y + row_h * 2),
            ("fire", "Max Streak", str(data.activity.longest_streak), col2_x, grid_y + row_h * 2),
        ])
    else:
        stats_items.extend([
            ("globe", "Global Rank", f"#{format_number(data.profile.ranking)}" if data.profile.ranking > 0 else "N/A", col1_x, grid_y),
            ("check", "Total Solved", f"{format_number(data.solved.total_solved)}", col2_x, grid_y),
            ("target", "Acceptance", f"{data.solved.acceptance_rate:.1f}%", col1_x, grid_y + row_h),
            ("fire", "Max Streak", str(data.activity.longest_streak), col2_x, grid_y + row_h),
        ])

    for icon_name, label, value, sx, sy in stats_items:
        svg_parts.append(
            render_icon(icon_name, sx, sy - 2, icon_size, theme.icon_color)
        )
        svg_parts.append(
            renderer.text(
                sx + icon_size + 6,
                sy + 10,
                f"{label}:",
                font_size=label_size,
                fill=theme.text_secondary,
            )
        )
        svg_parts.append(
            renderer.text(
                sx + icon_size + 6 + 82,
                sy + 10,
                value,
                font_size=value_size,
                fill=theme.text_color,
                weight="bold",
            )
        )

    svg_parts.append("</g>")
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)
