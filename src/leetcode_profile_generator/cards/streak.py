"""Streak card generator.

Generates `streak.svg` featuring the longest streak card,
vibrant flame graphics, and a smooth monthly activity area graph.
"""

from __future__ import annotations

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.fonts import FONT_FAMILY
from ..utils.icons import render_icon
from ..utils.math import (
    Point,
    format_number,
    points_to_area_path,
    points_to_svg_path,
    scale_value,
)

# Month label mapping
_MONTH_NAMES = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}


def generate_streak_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the streak card SVG.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme.

    Returns:
        Complete SVG string for the streak card.
    """
    renderer = SVGRenderer(theme)

    padding = 22
    width = 460
    height = 295

    orange_accent = "#ffa116"

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(
        renderer.svg_header(
            width,
            height,
            title=f"{data.profile.username}'s Activity Streak",
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

    # Flame linear gradient
    svg_parts.append(
        f'<linearGradient id="flame_grad" x1="0%" y1="100%" x2="0%" y2="0%">'
        f'<stop offset="0%" stop-color="#ff5500"/>'
        f'<stop offset="100%" stop-color="{orange_accent}"/>'
        f'</linearGradient>'
    )

    # Monthly chart area fill gradient
    svg_parts.append(
        f'<linearGradient id="monthly_chart_grad" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" stop-color="{orange_accent}" stop-opacity="0.35"/>'
        f'<stop offset="100%" stop-color="{orange_accent}" stop-opacity="0.0"/>'
        f'</linearGradient>'
    )

    svg_parts.append(
        renderer.create_glow("dot_glow", orange_accent, 3)
    )

    svg_parts.append("<style>")
    svg_parts.append("""
      @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
      .streak-content { animation: fadeIn 0.4s ease-out; }
      @media (prefers-reduced-motion: reduce) { .streak-content { animation: none; } }
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

    svg_parts.append('<g class="streak-content">')

    # ── Header Title ──
    svg_parts.append(render_icon("fire", padding, padding + 2, 20, "url(#flame_grad)"))
    svg_parts.append(
        renderer.text(
            padding + 26,
            padding + 16,
            "Activity Streak",
            font_size=16,
            fill=theme.title_color,
            weight="bold",
        )
    )

    # Top Right: Total Active Days
    active_days_str = format_number(data.activity.total_active_days)
    svg_parts.append(
        f'<text x="{width - padding}" y="{padding + 16}" font-family="{FONT_FAMILY}" font-size="11" text-anchor="end">'
        f'<tspan fill="{theme.text_secondary}">Total Active Days: </tspan>'
        f'<tspan fill="{theme.title_color}" font-weight="bold">{active_days_str}</tspan>'
        f'</text>'
    )

    # ── Row 1: Longest Streak Card (Full Width, Centered) ──
    card_y = padding + 34
    card_w = width - padding * 2
    card_h = 60

    svg_parts.append(
        f'<rect x="{padding}" y="{card_y}" width="{card_w}" height="{card_h}" rx="10" '
        f'fill="{theme.separator_color}" fill-opacity="0.5" '
        f'stroke="{theme.border_color}" stroke-width="0.8"/>'
    )

    # Flame icon centered-left
    icon_x = padding + 16
    svg_parts.append(
        render_icon("fire", icon_x, card_y + 14, 28, "url(#flame_grad)")
    )

    # Streak value
    svg_parts.append(
        renderer.text(
            icon_x + 42,
            card_y + 28,
            f"{data.activity.longest_streak} Days",
            font_size=18,
            fill=orange_accent,
            weight="bold",
        )
    )
    svg_parts.append(
        renderer.text(
            icon_x + 42,
            card_y + 44,
            "Longest Streak",
            font_size=11,
            fill=theme.text_secondary,
        )
    )

    # Lightning icon on right side
    svg_parts.append(
        render_icon("lightning", width - padding - 44, card_y + 16, 24, orange_accent)
    )

    # ── Separator Line ──
    sep_y = card_y + card_h + 14
    svg_parts.append(
        f'<line x1="{padding}" y1="{sep_y}" x2="{width - padding}" y2="{sep_y}" '
        f'stroke="{theme.separator_color}" stroke-width="1"/>'
    )

    # ── Monthly Activity Graph Section ──
    graph_y = sep_y + 12
    svg_parts.append(
        renderer.text(
            padding,
            graph_y + 12,
            "Monthly Activity",
            font_size=13,
            fill=theme.title_color,
            weight="bold",
        )
    )

    monthly = data.activity.monthly_activity
    months = list(monthly.items())

    chart_left = padding + 15
    chart_right = width - padding - 15
    chart_top = graph_y + 30
    chart_bottom = height - padding - 22

    if months:
        counts = [c for _, c in months]
        max_count = max(counts) if counts else 1
        nice_max = max(10, max_count)

        # Build chart points
        chart_points: list[Point] = []
        for i, (_, count) in enumerate(months):
            x = (
                scale_value(i, 0, len(months) - 1, chart_left, chart_right)
                if len(months) > 1
                else (chart_left + chart_right) / 2
            )
            y = scale_value(count, 0, nice_max, chart_bottom, chart_top)
            chart_points.append(Point(x, y))

        # Horizontal grid line
        grid_mid_y = (chart_top + chart_bottom) / 2
        svg_parts.append(
            f'<line x1="{chart_left}" y1="{grid_mid_y:.1f}" x2="{chart_right}" y2="{grid_mid_y:.1f}" '
            f'stroke="{theme.chart_grid_color}" stroke-width="0.5" stroke-dasharray="4,4"/>'
        )

        # Smooth Area Fill Path
        if len(chart_points) >= 2:
            area_path = points_to_area_path(chart_points, chart_bottom)
            svg_parts.append(
                f'<path d="{area_path}" fill="url(#monthly_chart_grad)"/>'
            )

        # Smooth Bézier Line Curve
        if len(chart_points) >= 2:
            line_path = points_to_svg_path(chart_points)
            svg_parts.append(
                f'<path d="{line_path}" fill="none" stroke="{orange_accent}" '
                f'stroke-width="2.5" stroke-linecap="round"/>'
            )

        # Data dots & X-axis month labels
        peak_count = max(counts) if counts else 0
        for i, (month_key, count) in enumerate(months):
            pt = chart_points[i]
            parts = month_key.split("-")
            m_code = parts[1] if len(parts) == 2 else month_key
            month_label = _MONTH_NAMES.get(m_code, m_code)

            # X-axis Label
            svg_parts.append(
                renderer.text(
                    pt.x,
                    chart_bottom + 16,
                    month_label,
                    font_size=10,
                    fill=theme.text_secondary,
                    anchor="middle",
                )
            )

            # Data Point Dot
            is_peak = count > 0 and count == peak_count
            dot_r = 4.5 if is_peak else 3.0
            dot_color = orange_accent if is_peak else theme.title_color
            glow_attr = ' filter="url(#dot_glow)"' if is_peak else ""

            tooltip = f"{month_label}: {count} submission{'s' if count != 1 else ''}"
            svg_parts.append(
                f'<circle cx="{pt.x:.1f}" cy="{pt.y:.1f}" r="{dot_r}" '
                f'fill="{dot_color}"{glow_attr}><title>{tooltip}</title></circle>'
            )

            # Display submission count number above each month vertex
            num_fill = orange_accent if is_peak else theme.text_color
            num_weight = "bold" if is_peak else "500"
            num_size = 10 if is_peak else 9
            num_y = pt.y - (9 if is_peak else 7)
            svg_parts.append(
                renderer.text(
                    pt.x,
                    num_y,
                    str(count),
                    font_size=num_size,
                    fill=num_fill,
                    weight=num_weight,
                    anchor="middle",
                )
            )

    else:
        # Fallback if no monthly activity data
        svg_parts.append(
            renderer.text(
                width / 2,
                chart_bottom - 20,
                "No monthly activity data available",
                font_size=12,
                fill=theme.text_secondary,
                anchor="middle",
            )
        )

    svg_parts.append("</g>")
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)
