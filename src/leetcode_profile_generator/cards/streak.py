"""Streak card generator.

Generates `streak.svg` showing current streak, longest streak,
monthly activity bars, and total active days.
"""

from __future__ import annotations

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.icons import render_icon
from ..utils.math import format_number


def generate_streak_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the streak card SVG.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme.

    Returns:
        Complete SVG string for the streak card.
    """
    renderer = SVGRenderer(theme)

    padding = 24
    width = 420
    header_h = 40
    streak_section_h = 60
    separator_h = 20
    monthly_header_h = 25

    monthly = data.activity.monthly_activity
    months = list(monthly.items())
    bar_row_h = 22
    monthly_section_h = len(months) * bar_row_h if months else 0
    footer_h = 30

    height = padding + header_h + streak_section_h + separator_h + monthly_header_h + monthly_section_h + footer_h + padding

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(renderer.svg_header(
        width, height,
        title=f"{data.profile.username}'s Activity Streak",
    ))

    # ── Defs ──
    svg_parts.append("<defs>")
    if theme.bg_gradient:
        svg_parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    svg_parts.append(renderer.create_drop_shadow("card_shadow", blur=8, offset_y=4, color=theme.shadow_color))
    svg_parts.append(renderer.create_glow("fire_glow", theme.hard_color, 3))
    svg_parts.append("<style>")
    svg_parts.append("""
      @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes growBar { from { width: 0; } }
      .streak-content { animation: fadeIn 0.4s ease-out; }
      .monthly-bar { animation: growBar 0.6s ease-out; }
      @media (prefers-reduced-motion: reduce) {
        .streak-content { animation: none; }
        .monthly-bar { animation: none; }
      }
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

    svg_parts.append('<g class="streak-content">')

    # ── Title ──
    svg_parts.append(render_icon("fire", padding, padding + 2, 16, theme.hard_color))
    svg_parts.append(renderer.text(
        padding + 22, padding + 15, "Activity Streak",
        font_size=16, fill=theme.title_color, weight="bold",
    ))

    # ── Streak numbers ──
    y = padding + header_h
    col_mid = width / 2

    # Current streak (left)
    svg_parts.append(render_icon("fire", padding + 30, y, 28, theme.hard_color))
    svg_parts.append(renderer.text(
        padding + 65, y + 24, str(data.activity.current_streak),
        font_size=28, fill=theme.title_color, weight="bold",
    ))
    svg_parts.append(renderer.text(
        padding + 50, y + 44, "Current Streak",
        font_size=11, fill=theme.text_secondary,
    ))

    # Longest streak (right)
    svg_parts.append(render_icon("lightning", col_mid + 30, y, 28, theme.accent_color))
    svg_parts.append(renderer.text(
        col_mid + 65, y + 24, str(data.activity.longest_streak),
        font_size=28, fill=theme.title_color, weight="bold",
    ))
    svg_parts.append(renderer.text(
        col_mid + 45, y + 44, "Longest Streak",
        font_size=11, fill=theme.text_secondary,
    ))

    # ── Separator ──
    y += streak_section_h
    svg_parts.append(
        f'<line x1="{padding}" y1="{y}" x2="{width - padding}" y2="{y}" '
        f'stroke="{theme.separator_color}" stroke-width="1" stroke-dasharray="4,4"/>'
    )

    # ── Monthly activity ──
    y += separator_h
    if months:
        svg_parts.append(renderer.text(
            padding, y + 4, f"Monthly Activity (last {len(months)} months)",
            font_size=12, fill=theme.text_secondary,
        ))
        y += monthly_header_h

        max_count = max(monthly.values()) if monthly.values() else 1
        bar_max_w = width - padding * 2 - 80  # space for label + count

        # Month name formatter
        month_names = {
            "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
            "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
            "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
        }

        for month_key, count in months:
            # Parse month label
            parts = month_key.split("-")
            month_label = month_names.get(parts[1], parts[1]) if len(parts) == 2 else month_key

            # Month label
            svg_parts.append(renderer.text(
                padding, y + 14, month_label,
                font_size=11, fill=theme.text_secondary,
            ))

            # Bar
            bar_x = padding + 36
            bar_w = (count / max_count) * bar_max_w if max_count > 0 else 0
            svg_parts.append(
                f'<rect class="monthly-bar" x="{bar_x}" y="{y + 5}" width="{bar_w:.1f}" height="{10}" '
                f'rx="{theme.progress_radius}" fill="{theme.accent_color}"/>'
            )

            # Count
            svg_parts.append(renderer.text(
                bar_x + bar_w + 8, y + 14, str(count),
                font_size=10, fill=theme.text_color, weight="600",
            ))

            y += bar_row_h

    # ── Footer: Total active days ──
    y += 8
    svg_parts.append(renderer.text(
        padding, y + 4, f"Total Active Days: {format_number(data.activity.total_active_days)}",
        font_size=12, fill=theme.text_color, weight="600",
    ))

    svg_parts.append("</g>")
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)
