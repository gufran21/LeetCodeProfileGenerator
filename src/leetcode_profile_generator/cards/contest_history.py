"""Contest history table card generator.

Generates modern `contest_history.svg` showing the latest contests
with pill-card rows, staggered entrance animations, and interactive hover states.
"""

from __future__ import annotations

from datetime import datetime, timezone

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

    padding = 20
    width = 600
    header_h = 44
    table_header_h = 24
    row_h = 36
    row_gap = 6
    rows_count = len(records)

    start_y = padding + header_h + table_header_h
    height = start_y + rows_count * (row_h + row_gap) + 14

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(
        renderer.svg_header(
            width,
            height,
            title=f"{data.profile.username}'s Recent Contests",
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
    svg_parts.append(f"""
      @keyframes rowSlide {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}
      .contest-row {{
        animation: rowSlide 0.35s ease-out backwards;
        transition: transform 0.2s ease;
      }}
      .contest-row:hover {{
        transform: translateY(-1.5px);
      }}
      .contest-row:hover .row-bg {{
        fill-opacity: 0.7;
        stroke: {theme.accent_color};
        stroke-width: 1px;
      }}
      @media (prefers-reduced-motion: reduce) {{
        .contest-row {{ animation: none; transition: none; }}
      }}
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

    # ── Header Title ──
    svg_parts.append(render_icon("trophy", padding + 4, padding + 4, 18, theme.icon_color))
    svg_parts.append(
        renderer.text(
            padding + 28,
            padding + 18,
            "Recent Contests",
            font_size=16,
            fill=theme.title_color,
            weight="bold",
        )
    )

    # ── Table Header Columns ──
    header_y = padding + header_h
    col_contest_x = padding + 12
    col_date_x = 280
    col_rating_x = 380
    col_rank_x = 490
    col_delta_x = 576

    svg_parts.append(
        renderer.text(
            col_contest_x,
            header_y,
            "Contest",
            font_size=11,
            fill=theme.text_secondary,
            weight="600",
            anchor="start",
        )
    )
    svg_parts.append(
        renderer.text(
            col_date_x,
            header_y,
            "Date",
            font_size=11,
            fill=theme.text_secondary,
            weight="600",
            anchor="end",
        )
    )
    svg_parts.append(
        renderer.text(
            col_rating_x,
            header_y,
            "Rating",
            font_size=11,
            fill=theme.text_secondary,
            weight="600",
            anchor="end",
        )
    )
    svg_parts.append(
        renderer.text(
            col_rank_x,
            header_y,
            "Rank",
            font_size=11,
            fill=theme.text_secondary,
            weight="600",
            anchor="end",
        )
    )
    svg_parts.append(
        renderer.text(
            col_delta_x,
            header_y,
            "Δ",
            font_size=11,
            fill=theme.text_secondary,
            weight="600",
            anchor="end",
        )
    )

    # ── Table Rows ──
    for i, record in enumerate(records):
        row_y = start_y + i * (row_h + row_gap)
        delay = i * 0.06

        svg_parts.append(
            f'<g class="contest-row" style="animation-delay: {delay:.2f}s">'
        )

        # Row Pill background
        svg_parts.append(
            f'<rect class="row-bg" x="{padding}" y="{row_y}" width="{width - padding * 2}" '
            f'height="{row_h}" rx="8" fill="{theme.separator_color}" fill-opacity="0.4" '
            f'stroke="{theme.border_color}" stroke-width="0.5"/>'
        )

        text_y = row_y + 23

        # Contest name (truncated if long)
        contest_name = record.title
        if len(contest_name) > 26:
            contest_name = contest_name[:24] + "…"
        svg_parts.append(
            renderer.text(
                col_contest_x,
                text_y,
                contest_name,
                font_size=12,
                fill=theme.text_color,
                weight="500",
                anchor="start",
            )
        )

        # Date
        try:
            dt = datetime.fromtimestamp(record.timestamp, tz=timezone.utc)
            date_str = dt.strftime("%b %d, %Y")
        except (ValueError, OSError):
            date_str = "—"
        svg_parts.append(
            renderer.text(
                col_date_x,
                text_y,
                date_str,
                font_size=11,
                fill=theme.text_secondary,
                anchor="end",
            )
        )

        # Rating
        svg_parts.append(
            renderer.text(
                col_rating_x,
                text_y,
                f"{record.rating:.0f}",
                font_size=12,
                fill=theme.text_color,
                weight="bold",
                anchor="end",
            )
        )

        # Rank
        svg_parts.append(
            renderer.text(
                col_rank_x,
                text_y,
                f"#{format_number(record.ranking)}",
                font_size=12,
                fill=theme.text_secondary,
                anchor="end",
            )
        )

        # Delta rating with arrow & colors
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
        svg_parts.append(
            renderer.text(
                col_delta_x,
                text_y,
                delta_text,
                font_size=12,
                fill=delta_color,
                weight="bold",
                anchor="end",
            )
        )

        svg_parts.append("</g>")

    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)


def _placeholder(renderer: SVGRenderer, theme: Theme, username: str) -> str:
    """Generate a placeholder when no contest history exists."""
    width, height = 600, 120
    parts: list[str] = []
    parts.append(
        renderer.svg_header(width, height, title=f"No contests for {username}")
    )
    parts.append("<defs>")
    if theme.bg_gradient:
        parts.append(
            renderer.create_gradient(
                "bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]
            )
        )
    parts.append("</defs>")
    fill = "url(#bg_grad)" if theme.bg_gradient else theme.bg_color
    parts.append(
        renderer.rounded_rect(
            0.5,
            0.5,
            width - 1,
            height - 1,
            rx=theme.border_radius,
            fill=fill,
            stroke=theme.border_color,
        )
    )
    parts.append(render_icon("trophy", 24, 24, 18, theme.icon_color))
    parts.append(
        renderer.text(
            48, 38, "Recent Contests", font_size=16, fill=theme.title_color, weight="bold"
        )
    )
    parts.append(
        renderer.text(
            width / 2,
            75,
            "No contest history available",
            font_size=13,
            fill=theme.text_secondary,
            anchor="middle",
        )
    )
    parts.append(renderer.svg_footer())
    return "\n".join(parts)
