"""Stats card generator — the primary profile overview card.

Generates `leetcode_stats.svg` with profile info, contest ranking,
and difficulty breakdown with progress bars.
"""

from __future__ import annotations

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.date import format_relative
from ..utils.icons import render_icon
from ..utils.math import format_number


def generate_stats_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the stats overview card SVG.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme for rendering.

    Returns:
        Complete SVG string for the stats card.
    """
    renderer = SVGRenderer(theme)

    width = 495
    height = 258
    padding = 24
    inner_w = width - padding * 2

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(renderer.svg_header(
        width, height,
        title=f"{data.profile.username}'s LeetCode Stats",
        desc=f"LeetCode profile stats for {data.profile.username}",
    ))

    # ── Defs: gradient, shadow, glow ──
    svg_parts.append("<defs>")
    if theme.bg_gradient:
        svg_parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    svg_parts.append(renderer.create_drop_shadow("card_shadow", blur=8, offset_y=4, color=theme.shadow_color))
    svg_parts.append(renderer.create_glow("bar_glow", theme.accent_color, 2))

    # Animated style
    svg_parts.append("<style>")
    svg_parts.append("""
      @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes growBar { from { width: 0; } }
      .card-content { animation: fadeIn 0.4s ease-out; }
      .progress-fill { animation: growBar 0.8s ease-out; }
      @media (prefers-reduced-motion: reduce) {
        .card-content { animation: none; }
        .progress-fill { animation: none; }
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

    # ── Row 1: Avatar + Username + Rating Badge ──
    y = padding
    avatar_size = 40

    # Avatar (circular clip)
    if data.avatar_b64:
        clip_id = "avatar_clip"
        cx = padding + avatar_size / 2
        cy = y + avatar_size / 2
        svg_parts.append(f'<clipPath id="{clip_id}"><circle cx="{cx}" cy="{cy}" r="{avatar_size / 2}"/></clipPath>')
        svg_parts.append(
            f'<image x="{padding}" y="{y}" width="{avatar_size}" height="{avatar_size}" '
            f'href="{data.avatar_b64}" clip-path="url(#{clip_id})" preserveAspectRatio="xMidYMid slice"/>'
        )
    else:
        # Placeholder circle with user icon
        cx = padding + avatar_size / 2
        cy = y + avatar_size / 2
        svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{avatar_size / 2}" fill="{theme.separator_color}"/>')
        svg_parts.append(render_icon("user", padding + 8, y + 8, 24, theme.text_secondary))

    text_x = padding + avatar_size + 12
    svg_parts.append(renderer.text(
        text_x, y + 18, data.profile.username,
        font_size=18, fill=theme.title_color, weight="bold",
    ))

    if data.profile.real_name and data.profile.real_name != data.profile.username:
        svg_parts.append(renderer.text(
            text_x, y + 36, data.profile.real_name,
            font_size=12, fill=theme.text_secondary,
        ))

    # Lightning icon + rating badge on the right
    if data.contest and data.contest.has_competed:
        rating_text = f"{data.contest.rating:.0f}"
        badge_x = width - padding - 60
        svg_parts.append(render_icon("lightning", badge_x, y + 4, 16, theme.accent_color))
        svg_parts.append(renderer.text(
            badge_x + 20, y + 18, rating_text,
            font_size=16, fill=theme.accent_color, weight="bold",
        ))

    # ── Separator ──
    y += avatar_size + 16
    svg_parts.append(
        f'<line x1="{padding}" y1="{y}" x2="{width - padding}" y2="{y}" '
        f'stroke="{theme.separator_color}" stroke-width="1" stroke-dasharray="4,4"/>'
    )

    # ── Row 2: Stats Grid (2 columns × 3 rows) ──
    y += 14
    col1_x = padding
    col2_x = width / 2 + 10
    row_h = 22
    icon_size = 14
    label_size = 12
    value_size = 13

    stats_items: list[tuple[str, str, str, float, float]] = []

    if data.contest and data.contest.has_competed:
        stats_items.extend([
            ("trophy", "Rating", f"{data.contest.rating:.0f}", col1_x, y),
            ("globe", "Global Rank", f"#{format_number(data.contest.global_ranking)}", col2_x, y),
            ("chart", "Top", f"{data.contest.top_percentage:.1f}%", col1_x, y + row_h),
            ("medal", "Contests", str(data.contest.attended_count), col2_x, y + row_h),
            ("target", "Acceptance", f"{data.solved.acceptance_rate}%", col1_x, y + row_h * 2),
        ])
        y += row_h * 3 + 4
    else:
        stats_items.extend([
            ("target", "Acceptance", f"{data.solved.acceptance_rate}%", col1_x, y),
            ("globe", "Ranking", f"#{format_number(data.profile.ranking)}" if data.profile.ranking > 0 else "N/A", col2_x, y),
        ])
        y += row_h + 8

    for icon_name, label, value, sx, sy in stats_items:
        svg_parts.append(render_icon(icon_name, sx, sy - 2, icon_size, theme.icon_color))
        svg_parts.append(renderer.text(
            sx + icon_size + 6, sy + 10, f"{label}:",
            font_size=label_size, fill=theme.text_secondary,
        ))
        svg_parts.append(renderer.text(
            sx + icon_size + 6 + 85, sy + 10, value,
            font_size=value_size, fill=theme.text_color, weight="600",
        ))

    # ── Separator ──
    svg_parts.append(
        f'<line x1="{padding}" y1="{y}" x2="{width - padding}" y2="{y}" '
        f'stroke="{theme.separator_color}" stroke-width="1" stroke-dasharray="4,4"/>'
    )

    # ── Row 3: Difficulty Progress Bars ──
    y += 12
    bar_h = 8
    bar_w = inner_w - 155
    bar_x = padding + 58
    difficulties = [
        ("Easy", data.solved.easy_solved, data.solved.easy_total, data.solved.easy_percentage, theme.easy_color),
        ("Medium", data.solved.medium_solved, data.solved.medium_total, data.solved.medium_percentage, theme.medium_color),
        ("Hard", data.solved.hard_solved, data.solved.hard_total, data.solved.hard_percentage, theme.hard_color),
    ]

    for label, solved, total, pct, color in difficulties:
        # Label
        svg_parts.append(renderer.text(
            padding, y + 9, label,
            font_size=12, fill=color, weight="600",
        ))

        # Progress bar
        svg_parts.append(renderer.progress_bar(
            bar_x, y + 1, bar_w, bar_h, pct, color, theme.progress_bg, theme.progress_radius,
        ))

        # Count
        count_text = f"{solved}/{total}"
        svg_parts.append(renderer.text(
            bar_x + bar_w + 8, y + 9, count_text,
            font_size=11, fill=theme.text_secondary,
        ))

        y += 24

    # ── Footer: Total + Updated ──
    y += 2
    svg_parts.append(renderer.text(
        padding, y + 4, f"Total: {format_number(data.solved.total_solved)} / {format_number(data.solved.total_total)} solved",
        font_size=11, fill=theme.text_secondary,
    ))

    updated_text = f"Updated {format_relative(data.fetched_at)}"
    svg_parts.append(renderer.text(
        width - padding, y + 4, updated_text,
        font_size=10, fill=theme.text_secondary, anchor="end",
    ))

    svg_parts.append("</g>")
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)
