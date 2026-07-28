"""Difficulty distribution card generator.

Generates `difficulty.svg` with horizontal progress bars showing
easy/medium/hard problem solving stats.
"""

from __future__ import annotations

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.icons import render_icon
from ..utils.math import format_number


def generate_difficulty_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the difficulty distribution card SVG.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme.

    Returns:
        Complete SVG string for the difficulty card.
    """
    renderer = SVGRenderer(theme)
    width = 420
    height = 230
    padding = 24
    inner_w = width - padding * 2

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(renderer.svg_header(
        width, height,
        title=f"{data.profile.username}'s Difficulty Breakdown",
    ))

    # ── Defs ──
    svg_parts.append("<defs>")
    if theme.bg_gradient:
        svg_parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    svg_parts.append(renderer.create_drop_shadow("card_shadow", blur=8, offset_y=4, color=theme.shadow_color))
    svg_parts.append("<style>")
    svg_parts.append("""
      @keyframes growBar { from { width: 0; } }
      @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
      .bar-fill { animation: growBar 0.8s ease-out; }
      .card-content { animation: fadeIn 0.4s ease-out; }
      @media (prefers-reduced-motion: reduce) {
        .bar-fill { animation: none; }
        .card-content { animation: none; }
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

    svg_parts.append('<g class="card-content">')

    # ── Title ──
    svg_parts.append(render_icon("chart", padding, padding + 2, 16, theme.icon_color))
    svg_parts.append(renderer.text(
        padding + 22, padding + 15, "Difficulty Breakdown",
        font_size=16, fill=theme.title_color, weight="bold",
    ))

    # ── Difficulty Bars ──
    y = padding + 40
    bar_h = 10
    bar_x = padding + 65
    bar_w = inner_w - 160
    row_gap = 50

    difficulties = [
        ("Easy", data.solved.easy_solved, data.solved.easy_total, data.solved.easy_percentage, theme.easy_color, data.solved.easy_beats),
        ("Medium", data.solved.medium_solved, data.solved.medium_total, data.solved.medium_percentage, theme.medium_color, data.solved.medium_beats),
        ("Hard", data.solved.hard_solved, data.solved.hard_total, data.solved.hard_percentage, theme.hard_color, data.solved.hard_beats),
    ]

    for label, solved, total, pct, color, beats in difficulties:
        # Label
        svg_parts.append(renderer.text(
            padding, y + 10, label,
            font_size=13, fill=color, weight="bold",
        ))

        # Progress bar
        svg_parts.append(renderer.progress_bar(
            bar_x, y + 2, bar_w, bar_h, pct, color, theme.progress_bg, theme.progress_radius,
        ))

        # Count
        count_text = f"{solved} / {total}"
        svg_parts.append(renderer.text(
            bar_x + bar_w + 10, y + 10, count_text,
            font_size=12, fill=theme.text_color,
        ))

        # Percentage below bar
        pct_text = f"{pct}%"
        if beats is not None:
            pct_text += f"  •  beats {beats:.1f}%"
        svg_parts.append(renderer.text(
            bar_x, y + 26, pct_text,
            font_size=10, fill=theme.text_secondary,
        ))

        y += row_gap

    # ── Footer: Total ──
    y += 5
    svg_parts.append(renderer.text(
        padding, y, f"Total Solved: {format_number(data.solved.total_solved)}",
        font_size=12, fill=theme.text_color, weight="600",
    ))

    svg_parts.append("</g>")
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)
