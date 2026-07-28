"""Combined dashboard card generator.

Generates `dashboard.svg` — a single, all-in-one card combining
compact versions of stats, difficulty, and activity data.
"""

from __future__ import annotations

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.date import format_relative
from ..utils.icons import render_icon
from ..utils.math import format_number


def generate_dashboard_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the combined dashboard card SVG.

    A single card that includes a compact version of stats,
    difficulty breakdown, rating summary, and streak info.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme.

    Returns:
        Complete SVG string for the dashboard card.
    """
    renderer = SVGRenderer(theme)

    width = 800
    height = 380
    padding = 24
    col_mid = width / 2

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(renderer.svg_header(
        width, height,
        title=f"{data.profile.username}'s LeetCode Dashboard",
    ))

    # ── Defs ──
    svg_parts.append("<defs>")
    if theme.bg_gradient:
        svg_parts.append(renderer.create_gradient("bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]))
    svg_parts.append(renderer.create_drop_shadow("card_shadow", blur=8, offset_y=4, color=theme.shadow_color))
    svg_parts.append("<style>")
    svg_parts.append("""
      @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      @keyframes growBar { from { width: 0; } }
      .dash-content { animation: fadeIn 0.4s ease-out; }
      .progress-fill { animation: growBar 0.8s ease-out; }
      @media (prefers-reduced-motion: reduce) {
        .dash-content { animation: none; }
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

    svg_parts.append('<g class="dash-content">')

    # ── Header: Username + Avatar ──
    avatar_size = 36
    if data.avatar_b64:
        clip_id = "dash_avatar_clip"
        cx = padding + avatar_size / 2
        cy = padding + avatar_size / 2
        svg_parts.append(f'<clipPath id="{clip_id}"><circle cx="{cx}" cy="{cy}" r="{avatar_size / 2}"/></clipPath>')
        svg_parts.append(
            f'<image x="{padding}" y="{padding}" width="{avatar_size}" height="{avatar_size}" '
            f'href="{data.avatar_b64}" clip-path="url(#{clip_id})" preserveAspectRatio="xMidYMid slice"/>'
        )
    else:
        cx = padding + avatar_size / 2
        cy = padding + avatar_size / 2
        svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{avatar_size / 2}" fill="{theme.separator_color}"/>')
        svg_parts.append(render_icon("user", padding + 6, padding + 6, 24, theme.text_secondary))

    text_x = padding + avatar_size + 12
    svg_parts.append(renderer.text(
        text_x, padding + 16, data.profile.username,
        font_size=20, fill=theme.title_color, weight="bold",
    ))
    if data.profile.real_name and data.profile.real_name != data.profile.username:
        svg_parts.append(renderer.text(
            text_x, padding + 34, data.profile.real_name,
            font_size=12, fill=theme.text_secondary,
        ))

    # Updated timestamp on right
    svg_parts.append(renderer.text(
        width - padding, padding + 16, f"Updated {format_relative(data.fetched_at)}",
        font_size=10, fill=theme.text_secondary, anchor="end",
    ))

    # ── Divider ──
    divider_y = padding + avatar_size + 16
    svg_parts.append(
        f'<line x1="{padding}" y1="{divider_y}" x2="{width - padding}" y2="{divider_y}" '
        f'stroke="{theme.separator_color}" stroke-width="1"/>'
    )

    # ═══════════════ LEFT COLUMN ═══════════════
    left_x = padding
    y = divider_y + 18
    section_w = col_mid - padding - 12

    # ── Stats Summary ──
    stat_col1_x = left_x
    stat_col2_x = left_x + section_w / 2
    stats_row_h = 22

    stats = []
    if data.contest and data.contest.has_competed:
        stats.extend([
            ("trophy", "Rating", f"{data.contest.rating:.0f}", stat_col1_x),
            ("globe", "Rank", f"#{format_number(data.contest.global_ranking)}", stat_col2_x),
            ("chart", "Top", f"{data.contest.top_percentage:.1f}%", stat_col1_x),
            ("medal", "Contests", str(data.contest.attended_count), stat_col2_x),
        ])
    else:
        stats.extend([
            ("globe", "Ranking", f"#{format_number(data.profile.ranking)}" if data.profile.ranking else "N/A", stat_col1_x),
            ("target", "Acceptance", f"{data.solved.acceptance_rate}%", stat_col2_x),
        ])

    for row_idx, (icon_name, label, value, sx) in enumerate(stats):
        row = row_idx // 2
        sy = y + row * stats_row_h
        svg_parts.append(render_icon(icon_name, sx, sy - 1, 13, theme.icon_color))
        svg_parts.append(renderer.text(sx + 18, sy + 10, f"{label}:", font_size=11, fill=theme.text_secondary))
        svg_parts.append(renderer.text(sx + 80, sy + 10, value, font_size=11, fill=theme.text_color, weight="600"))

    # ── Difficulty Bars ──
    y += (len(stats) // 2 + 1) * stats_row_h + 8
    bar_h = 8
    label_w = 55
    bar_w = section_w - label_w - 75

    difficulties = [
        ("Easy", data.solved.easy_solved, data.solved.easy_total, data.solved.easy_percentage, theme.easy_color),
        ("Medium", data.solved.medium_solved, data.solved.medium_total, data.solved.medium_percentage, theme.medium_color),
        ("Hard", data.solved.hard_solved, data.solved.hard_total, data.solved.hard_percentage, theme.hard_color),
    ]

    for label, solved, total, pct, color in difficulties:
        svg_parts.append(renderer.text(left_x, y + 9, label, font_size=11, fill=color, weight="600"))
        svg_parts.append(renderer.progress_bar(left_x + label_w, y + 1, bar_w, bar_h, pct, color, theme.progress_bg, theme.progress_radius))
        svg_parts.append(renderer.text(left_x + label_w + bar_w + 6, y + 9, f"{solved}/{total}", font_size=10, fill=theme.text_secondary))
        y += 22

    # Total
    svg_parts.append(renderer.text(
        left_x, y + 8, f"Total: {format_number(data.solved.total_solved)} / {format_number(data.solved.total_total)}",
        font_size=11, fill=theme.text_color, weight="600",
    ))

    # ═══════════════ VERTICAL DIVIDER ═══════════════
    svg_parts.append(
        f'<line x1="{col_mid}" y1="{divider_y + 8}" x2="{col_mid}" y2="{height - padding}" '
        f'stroke="{theme.separator_color}" stroke-width="1" stroke-dasharray="4,4"/>'
    )

    # ═══════════════ RIGHT COLUMN ═══════════════
    right_x = col_mid + 20
    right_w = width - right_x - padding
    y = divider_y + 18

    # ── Streak Info ──
    svg_parts.append(render_icon("fire", right_x, y - 1, 14, theme.hard_color))
    svg_parts.append(renderer.text(right_x + 20, y + 10, "Streak", font_size=13, fill=theme.title_color, weight="bold"))

    y += 26
    svg_parts.append(render_icon("fire", right_x, y - 1, 16, theme.hard_color))
    svg_parts.append(renderer.text(right_x + 22, y + 11, f"{data.activity.current_streak} days", font_size=13, fill=theme.text_color, weight="600"))
    svg_parts.append(renderer.text(right_x + 100, y + 11, "current", font_size=10, fill=theme.text_secondary))

    y += 22
    svg_parts.append(render_icon("lightning", right_x, y - 1, 16, theme.accent_color))
    svg_parts.append(renderer.text(right_x + 22, y + 11, f"{data.activity.longest_streak} days", font_size=13, fill=theme.text_color, weight="600"))
    svg_parts.append(renderer.text(right_x + 100, y + 11, "longest", font_size=10, fill=theme.text_secondary))

    y += 22
    svg_parts.append(renderer.text(right_x, y + 11, f"Active Days: {format_number(data.activity.total_active_days)}", font_size=11, fill=theme.text_secondary))

    # ── Recent Contests (mini table) ──
    y += 30
    if data.has_contests and data.contest_history:
        svg_parts.append(render_icon("medal", right_x, y - 1, 14, theme.icon_color))
        svg_parts.append(renderer.text(right_x + 20, y + 10, "Recent Contests", font_size=13, fill=theme.title_color, weight="bold"))

        y += 22
        recent = list(reversed(data.contest_history[-5:]))
        for record in recent:
            name = record.title
            if len(name) > 22:
                name = name[:19] + "…"
            svg_parts.append(renderer.text(right_x, y + 10, name, font_size=10, fill=theme.text_color))

            # Delta
            if record.delta_rating > 0:
                delta_color = theme.easy_color
                delta_text = f"▲{record.formatted_delta}"
            elif record.delta_rating < 0:
                delta_color = theme.hard_color
                delta_text = f"▼{record.formatted_delta}"
            else:
                delta_color = theme.text_secondary
                delta_text = "—"

            svg_parts.append(renderer.text(
                right_x + right_w, y + 10, delta_text,
                font_size=10, fill=delta_color, weight="600", anchor="end",
            ))

            y += 20

    # ── Badges count ──
    if data.has_badges:
        svg_parts.append(render_icon("shield", right_x, y - 1, 14, theme.icon_color))
        svg_parts.append(renderer.text(right_x + 20, y + 10, f"{len(data.badges)} badges earned", font_size=11, fill=theme.text_color))

    svg_parts.append("</g>")
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)
