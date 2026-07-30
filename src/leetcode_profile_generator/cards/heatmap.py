"""Submission heatmap card generator.

Generates `heatmap.svg` with a GitHub-style contribution heatmap
showing daily submission activity over the past year.
"""

from __future__ import annotations

from datetime import date, timedelta

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.colors import heatmap_color
from ..utils.date import get_month_labels, get_week_grid, timestamp_to_date
from ..utils.fonts import FONT_FAMILY
from ..utils.icons import render_icon
from ..utils.math import format_number


def generate_heatmap_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the submission heatmap card SVG.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme.

    Returns:
        Complete SVG string for the heatmap card.
    """
    renderer = SVGRenderer(theme)

    cell_size = 11
    cell_gap = 3
    cell_stride = cell_size + cell_gap

    # Day labels on left
    day_label_w = 28
    # Month labels on top
    month_label_h = 18

    padding = 24
    header_h = 35  # title row

    # Grid dimensions
    grid_cols = 53
    grid_rows = 7
    grid_w = grid_cols * cell_stride - cell_gap
    grid_h = grid_rows * cell_stride - cell_gap

    # Legend at bottom
    legend_h = 30

    width = padding * 2 + day_label_w + grid_w + 10
    height = padding + header_h + month_label_h + grid_h + legend_h + padding

    # Build date → count lookup from submission calendar
    date_counts: dict[date, int] = {}
    for ts_str, count in data.activity.submission_calendar.items():
        try:
            d = timestamp_to_date(ts_str)
            date_counts[d] = date_counts.get(d, 0) + count
        except (ValueError, OSError):
            continue

    # Generate the week grid
    grid = get_week_grid()
    month_labels = get_month_labels(grid)

    # Count total submissions in the past year
    total_submissions = sum(
        count for d, count in date_counts.items()
        if d >= (date.today() - timedelta(days=365))
    )

    # Heatmap color levels
    levels = [
        theme.heatmap_empty,
        theme.heatmap_l1,
        theme.heatmap_l2,
        theme.heatmap_l3,
        theme.heatmap_l4,
    ]

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(renderer.svg_header(
        width, height,
        title=f"{data.profile.username}'s Submission Heatmap",
    ))

    # ── Defs ──
    svg_parts.append("<defs>")
    if theme.bg_gradient:
        svg_parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    svg_parts.append(renderer.create_drop_shadow("card_shadow", blur=8, offset_y=4, color=theme.shadow_color))
    svg_parts.append("<style>")
    svg_parts.append("""
      @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      .heatmap-content { animation: fadeIn 0.5s ease-out; }
      @media (prefers-reduced-motion: reduce) { .heatmap-content { animation: none; } }
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

    svg_parts.append('<g class="heatmap-content">')

    # ── Title ──
    svg_parts.append(render_icon("calendar", padding, padding + 2, 16, theme.icon_color))
    svg_parts.append(renderer.text(
        padding + 22, padding + 15,
        f"{format_number(total_submissions)} submissions in the past year",
        font_size=14, fill=theme.title_color, weight="bold",
    ))

    # ── Top Right Stats (Total Active Days & Max Streak) ──
    active_days_str = format_number(data.activity.total_active_days)
    max_streak_str = format_number(data.activity.longest_streak)
    svg_parts.append(
        f'<text x="{width - padding}" y="{padding + 15}" font-family="{FONT_FAMILY}" font-size="11" text-anchor="end">'
        f'<tspan fill="{theme.text_secondary}">Total active days: </tspan>'
        f'<tspan fill="{theme.title_color}" font-weight="bold">{active_days_str}</tspan>'
        f'<tspan fill="{theme.text_secondary}">   Max streak: </tspan>'
        f'<tspan fill="{theme.title_color}" font-weight="bold">{max_streak_str}</tspan>'
        f'</text>'
    )

    # ── Grid origin ──
    grid_x = padding + day_label_w
    grid_y = padding + header_h + month_label_h

    # ── Month labels ──
    for col_idx, month_name in month_labels:
        x = grid_x + col_idx * cell_stride
        y = grid_y - 6
        svg_parts.append(renderer.text(
            x, y, month_name,
            font_size=9, fill=theme.text_secondary,
        ))

    # ── Day labels (Mon, Wed, Fri) ──
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for row_idx in [1, 3, 5]:  # Mon, Wed, Fri
        y = grid_y + row_idx * cell_stride + cell_size - 2
        svg_parts.append(renderer.text(
            padding, y, day_names[row_idx],
            font_size=9, fill=theme.text_secondary,
        ))

    # ── Heatmap cells ──
    for col_idx, week in enumerate(grid):
        for row_idx, day_val in enumerate(week):
            if day_val is None:
                continue

            x = grid_x + col_idx * cell_stride
            y = grid_y + row_idx * cell_stride
            count = date_counts.get(day_val, 0)
            color = heatmap_color(count, levels)

            tooltip = f"{day_val.strftime('%b %d, %Y')}: {count} submission{'s' if count != 1 else ''}"

            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'rx="2" fill="{color}"><title>{tooltip}</title></rect>'
            )

    # ── Legend ──
    legend_y = grid_y + grid_h + 16
    legend_x = grid_x + grid_w - 130

    svg_parts.append(renderer.text(
        legend_x - 32, legend_y + 9, "Less",
        font_size=9, fill=theme.text_secondary,
    ))

    for i, level_color in enumerate(levels):
        lx = legend_x + i * (cell_size + 3)
        svg_parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="{cell_size}" height="{cell_size}" '
            f'rx="2" fill="{level_color}"/>'
        )

    svg_parts.append(renderer.text(
        legend_x + len(levels) * (cell_size + 3) + 4, legend_y + 9, "More",
        font_size=9, fill=theme.text_secondary,
    ))

    svg_parts.append("</g>")
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)
