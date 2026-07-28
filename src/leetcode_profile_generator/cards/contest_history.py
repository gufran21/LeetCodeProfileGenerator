"""Contest history table card generator.

Generates `contest_history.svg` showing the latest 10 contests
with ratings, ranks, and delta changes.
"""

from __future__ import annotations

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.icons import render_icon
from ..utils.math import format_number


def generate_contest_history_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the contest history table card SVG.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme.

    Returns:
        Complete SVG string for the contest history table.
    """
    renderer = SVGRenderer(theme)

    # Get latest 10 contests (most recent first)
    records = list(reversed(data.contest_history[-10:]))

    if not records:
        return _placeholder(renderer, theme, data.profile.username)

    padding = 24
    width = 520
    row_h = 26
    header_h = 40
    table_header_h = 28
    rows = len(records)
    height = padding + header_h + table_header_h + rows * row_h + padding + 8

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(renderer.svg_header(
        width, height,
        title=f"{data.profile.username}'s Recent Contests",
    ))

    # ── Defs ──
    svg_parts.append("<defs>")
    if theme.bg_gradient:
        svg_parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    svg_parts.append(renderer.create_drop_shadow("card_shadow", blur=8, offset_y=4, color=theme.shadow_color))
    svg_parts.append("<style>")
    svg_parts.append("""
      @keyframes fadeIn { from { opacity: 0; transform: translateY(3px); } to { opacity: 1; transform: translateY(0); } }
      .table-content { animation: fadeIn 0.4s ease-out; }
      @media (prefers-reduced-motion: reduce) { .table-content { animation: none; } }
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

    svg_parts.append('<g class="table-content">')

    # ── Title ──
    svg_parts.append(render_icon("medal", padding, padding + 2, 16, theme.icon_color))
    svg_parts.append(renderer.text(
        padding + 22, padding + 15, "Recent Contests",
        font_size=16, fill=theme.title_color, weight="bold",
    ))

    # ── Table header ──
    y = padding + header_h
    col_contest = padding
    col_rating = 280
    col_rank = 360
    col_delta = 445

    svg_parts.append(renderer.text(col_contest, y + 12, "Contest", font_size=11, fill=theme.text_secondary, weight="600"))
    svg_parts.append(renderer.text(col_rating, y + 12, "Rating", font_size=11, fill=theme.text_secondary, weight="600"))
    svg_parts.append(renderer.text(col_rank, y + 12, "Rank", font_size=11, fill=theme.text_secondary, weight="600"))
    svg_parts.append(renderer.text(col_delta, y + 12, "Δ", font_size=11, fill=theme.text_secondary, weight="600"))

    # Header separator
    y += table_header_h - 4
    svg_parts.append(
        f'<line x1="{padding}" y1="{y}" x2="{width - padding}" y2="{y}" '
        f'stroke="{theme.separator_color}" stroke-width="1"/>'
    )

    # ── Table rows ──
    for i, record in enumerate(records):
        row_y = y + 4 + i * row_h

        # Alternating row background
        if i % 2 == 0:
            svg_parts.append(
                f'<rect x="{padding - 4}" y="{row_y}" width="{width - padding * 2 + 8}" '
                f'height="{row_h}" rx="4" fill="{theme.separator_color}" opacity="0.3"/>'
            )

        text_y = row_y + 17

        # Contest name (truncate if too long)
        contest_name = record.title
        if len(contest_name) > 28:
            contest_name = contest_name[:25] + "…"
        svg_parts.append(renderer.text(
            col_contest, text_y, contest_name,
            font_size=11, fill=theme.text_color,
        ))

        # Rating
        svg_parts.append(renderer.text(
            col_rating, text_y, f"{record.rating:.0f}",
            font_size=11, fill=theme.text_color, weight="600",
        ))

        # Rank
        svg_parts.append(renderer.text(
            col_rank, text_y, f"#{format_number(record.ranking)}",
            font_size=11, fill=theme.text_secondary,
        ))

        # Delta with color and arrow
        if record.delta_rating > 0:
            delta_color = theme.easy_color
            arrow = "▲"
        elif record.delta_rating < 0:
            delta_color = theme.hard_color
            arrow = "▼"
        else:
            delta_color = theme.text_secondary
            arrow = ""

        delta_text = f"{arrow} {record.formatted_delta}" if arrow else "—"
        svg_parts.append(renderer.text(
            col_delta, text_y, delta_text,
            font_size=11, fill=delta_color, weight="600",
        ))

    svg_parts.append("</g>")
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)


def _placeholder(renderer: SVGRenderer, theme: Theme, username: str) -> str:
    """Generate a placeholder when no contest history exists."""
    width, height = 520, 120
    parts: list[str] = []
    parts.append(renderer.svg_header(width, height, title=f"No contests for {username}"))
    parts.append("<defs>")
    if theme.bg_gradient:
        parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    parts.append("</defs>")
    fill = "url(#bg_grad)" if theme.bg_gradient else theme.bg_color
    parts.append(renderer.rounded_rect(0.5, 0.5, width - 1, height - 1, rx=theme.border_radius, fill=fill, stroke=theme.border_color))
    parts.append(render_icon("medal", 24, 24, 16, theme.icon_color))
    parts.append(renderer.text(46, 38, "Recent Contests", font_size=16, fill=theme.title_color, weight="bold"))
    parts.append(renderer.text(width / 2, 75, "No contest history available", font_size=13, fill=theme.text_secondary, anchor="middle"))
    parts.append(renderer.text(width / 2, 95, "Participate in LeetCode contests to track your progress!", font_size=11, fill=theme.text_secondary, anchor="middle"))
    parts.append(renderer.svg_footer())
    return "\n".join(parts)
