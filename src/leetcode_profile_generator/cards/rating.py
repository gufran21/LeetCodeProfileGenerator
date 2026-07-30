"""Rating history graph card generator.

Generates `rating_history.svg` with a smooth Bézier curve showing
contest rating progression over time.
"""

from __future__ import annotations

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.date import format_date
from ..utils.fonts import FONT_FAMILY
from ..utils.icons import render_icon
from ..utils.math import (
    Point,
    format_number,
    nice_axis_bounds,
    points_to_area_path,
    points_to_svg_path,
    scale_value,
)


def generate_rating_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the rating history graph SVG.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme.

    Returns:
        Complete SVG string, or a placeholder if no contest data.
    """
    renderer = SVGRenderer(theme)
    width = 600
    height = 300
    padding = 24

    # If no contest data, return a placeholder card
    if not data.has_contests or len(data.contest_history) < 1:
        return _placeholder_card(renderer, theme, width, height, data.profile.username)

    records = data.contest_history

    # ── Chart geometry ──
    chart_left = padding + 45  # space for Y-axis labels
    chart_right = width - padding - 10
    chart_top = padding + 45
    chart_bottom = height - padding - 55  # space for X-axis labels + footer

    # ── Scale data ──
    ratings = [r.rating for r in records]
    min_rating = min(ratings)
    max_rating = max(ratings)
    nice_min, nice_max, step = nice_axis_bounds(min_rating, max_rating)

    # Map data points to chart coordinates
    chart_points: list[Point] = []
    for i, record in enumerate(records):
        x = scale_value(i, 0, len(records) - 1, chart_left, chart_right) if len(records) > 1 else (chart_left + chart_right) / 2
        y = scale_value(record.rating, nice_min, nice_max, chart_bottom, chart_top)
        chart_points.append(Point(x, y))

    # Find peak and latest
    peak_idx = ratings.index(max_rating)
    latest_idx = len(records) - 1

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(renderer.svg_header(
        width, height,
        title=f"{data.profile.username}'s Rating History",
    ))

    yellow_accent = "#ffa116"

    # ── Defs ──
    svg_parts.append("<defs>")
    if theme.bg_gradient:
        svg_parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    svg_parts.append(renderer.create_drop_shadow("card_shadow", blur=8, offset_y=4, color=theme.shadow_color))
    svg_parts.append(
        f'<linearGradient id="area_fill" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" stop-color="{yellow_accent}" stop-opacity="0.35"/>'
        f'<stop offset="100%" stop-color="{yellow_accent}" stop-opacity="0.0"/>'
        f'</linearGradient>'
    )
    svg_parts.append(renderer.create_glow("dot_glow", yellow_accent, 3))

    svg_parts.append("<style>")
    svg_parts.append("""
      @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      @keyframes drawLine { from { stroke-dashoffset: 2000; } to { stroke-dashoffset: 0; } }
      .chart-content { animation: fadeIn 0.5s ease-out; }
      @media (prefers-reduced-motion: reduce) { .chart-content { animation: none; } }
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

    svg_parts.append('<g class="chart-content">')

    # ── Title ──
    svg_parts.append(render_icon("chart", padding, padding + 2, 16, yellow_accent))
    svg_parts.append(renderer.text(
        padding + 22, padding + 15, "Contest Rating History",
        font_size=16, fill=theme.title_color, weight="bold",
    ))

    # ── Grid lines + Y-axis labels ──
    y_val = nice_min
    while y_val <= nice_max:
        y_pos = scale_value(y_val, nice_min, nice_max, chart_bottom, chart_top)

        # Grid line
        svg_parts.append(
            f'<line x1="{chart_left}" y1="{y_pos:.1f}" x2="{chart_right}" y2="{y_pos:.1f}" '
            f'stroke="{theme.chart_grid_color}" stroke-width="0.5" stroke-dasharray="4,4"/>'
        )

        # Y-axis label
        svg_parts.append(renderer.text(
            chart_left - 8, y_pos + 4, f"{int(y_val)}",
            font_size=10, fill=theme.text_secondary, anchor="end",
        ))

        y_val += step

    # ── X-axis labels (auto-sampled) ──
    max_labels = 8
    if len(records) <= max_labels:
        label_indices = list(range(len(records)))
    else:
        step_size = (len(records) - 1) / (max_labels - 1)
        label_indices = [int(i * step_size) for i in range(max_labels)]

    for idx in label_indices:
        x = chart_points[idx].x
        label = format_date(records[idx].timestamp, "%b %Y")
        svg_parts.append(renderer.text(
            x, chart_bottom + 16, label,
            font_size=9, fill=theme.text_secondary, anchor="middle",
        ))

    # ── Area fill under curve ──
    if len(chart_points) >= 2:
        area_path = points_to_area_path(chart_points, chart_bottom)
        svg_parts.append(
            f'<path d="{area_path}" fill="url(#area_fill)"/>'
        )

    # ── Smooth curve line (Yellow #ffa116) ──
    if len(chart_points) >= 2:
        line_path = points_to_svg_path(chart_points)
        svg_parts.append(
            f'<path d="{line_path}" fill="none" '
            f'stroke="{yellow_accent}" stroke-width="2.5" stroke-linecap="round"/>'
        )

    # ── Data point dots with tooltips ──
    for i, (point, record) in enumerate(zip(chart_points, records, strict=False)):
        tooltip = f"{record.title} — Rating: {record.rating:.0f}, Rank: #{format_number(record.ranking)}"

        if i == peak_idx:
            # Peak: star marker in yellow #ffa116
            dot_r = 5
            svg_parts.append(f'<circle cx="{point.x:.1f}" cy="{point.y:.1f}" r="{dot_r}" '
                             f'fill="{yellow_accent}" filter="url(#dot_glow)"><title>{tooltip}</title></circle>')
            svg_parts.append(render_icon("star", point.x - 6, point.y - 20, 12, yellow_accent))
        else:
            # All other dots are white
            dot_r = 4 if i == latest_idx else 3
            dot_color = theme.title_color
            opacity = "1.0" if i == latest_idx else "0.8"
            if i == latest_idx or len(records) <= 30 or i % max(1, len(records) // 20) == 0:
                svg_parts.append(f'<circle cx="{point.x:.1f}" cy="{point.y:.1f}" r="{dot_r}" '
                                 f'fill="{dot_color}" opacity="{opacity}"><title>{tooltip}</title></circle>')

    # ── Peak rating dashed line (#ffa116) ──
    peak_y = scale_value(max_rating, nice_min, nice_max, chart_bottom, chart_top)
    svg_parts.append(
        f'<line x1="{chart_left}" y1="{peak_y:.1f}" x2="{chart_right}" y2="{peak_y:.1f}" '
        f'stroke="{yellow_accent}" stroke-width="0.8" stroke-dasharray="6,4" opacity="0.6"/>'
    )

    # ── Footer: Current / Peak / Contests ──
    footer_y = height - padding - 5
    current_rating = records[-1].rating

    svg_parts.append(f'<circle cx="{padding + 4}" cy="{footer_y - 4}" r="4" fill="{theme.title_color}"/>')
    svg_parts.append(
        f'<text x="{padding + 14}" y="{footer_y}" font-family="{FONT_FAMILY}" font-size="11">'
        f'<tspan fill="{theme.text_secondary}">Current: </tspan>'
        f'<tspan fill="{theme.title_color}" font-weight="bold">{current_rating:.0f}</tspan>'
        f'</text>'
    )

    sep1_x = padding + 130
    svg_parts.append(renderer.text(sep1_x, footer_y, "│", font_size=11, fill=theme.separator_color))

    svg_parts.append(render_icon("star", sep1_x + 14, footer_y - 10, 12, yellow_accent))
    svg_parts.append(
        f'<text x="{sep1_x + 30}" y="{footer_y}" font-family="{FONT_FAMILY}" font-size="11">'
        f'<tspan fill="{theme.text_secondary}">Peak: </tspan>'
        f'<tspan fill="{yellow_accent}" font-weight="bold">{max_rating:.0f}</tspan>'
        f'</text>'
    )

    sep2_x = sep1_x + 130
    svg_parts.append(renderer.text(sep2_x, footer_y, "│", font_size=11, fill=theme.separator_color))

    contest_count = data.contest.attended_count if data.contest else len(records)
    svg_parts.append(renderer.text(
        sep2_x + 14, footer_y, f"{contest_count} contests",
        font_size=11, fill=theme.text_color,
    ))

    svg_parts.append("</g>")
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)


def _placeholder_card(
    renderer: SVGRenderer, theme: Theme, width: int, height: int, username: str
) -> str:
    """Generate a placeholder card when no contest data is available."""
    parts: list[str] = []
    parts.append(renderer.svg_header(width, 120, title=f"No contest data for {username}"))
    parts.append("<defs>")
    if theme.bg_gradient:
        parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    parts.append("</defs>")
    fill = "url(#bg_grad)" if theme.bg_gradient else theme.bg_color
    parts.append(renderer.rounded_rect(0.5, 0.5, width - 1, 119, rx=theme.border_radius, fill=fill, stroke=theme.border_color))
    parts.append(render_icon("chart", 24, 24, 16, theme.icon_color))
    parts.append(renderer.text(46, 38, "Contest Rating History", font_size=16, fill=theme.title_color, weight="bold"))
    parts.append(renderer.text(width / 2, 75, "No contest data available yet", font_size=13, fill=theme.text_secondary, anchor="middle"))
    parts.append(renderer.text(width / 2, 95, "Participate in a LeetCode contest to see your rating graph!", font_size=11, fill=theme.text_secondary, anchor="middle"))
    parts.append(renderer.svg_footer())
    return "\n".join(parts)
