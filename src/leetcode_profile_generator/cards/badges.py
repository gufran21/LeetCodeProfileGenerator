"""Badges card generator.

Generates modern `badges.svg` showing earned LeetCode badges and locked/upcoming
badge progress with SVG hexagon badges and circular progress rings.
"""

from __future__ import annotations

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.icons import render_icon

# SVG badge icon shapes mapping
_BADGE_ICONS: dict[str, str] = {
    "medal": "shield",
    "star": "star",
    "trophy": "trophy",
    "fire": "fire",
    "check": "check",
    "code": "code",
    "default": "medal",
}


def _get_badge_icon(category: str) -> str:
    """Map a badge category to an icon name."""
    cat = category.lower()
    if "solving" in cat or "problem" in cat:
        return "star"
    elif "contest" in cat or "ranking" in cat:
        return "trophy"
    elif "streak" in cat or "daily" in cat:
        return "fire"
    elif "study" in cat or "plan" in cat:
        return "code"
    return "medal"


def generate_badges_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the badges card SVG.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme.

    Returns:
        Complete SVG string for the badges card.
    """
    renderer = SVGRenderer(theme)

    badges = data.badges
    upcoming = data.upcoming_badges

    if not badges and not upcoming:
        return _placeholder(renderer, theme, data.profile.username)

    # Calculate layout dimensions targeting ~4:3 aspect ratio
    badge_count = len(badges)
    col_width = 100
    row_height = 110
    left_section_width = 150
    divider_x = left_section_width
    right_start_x = divider_x + 20
    h_pad = 10  # right-side padding
    v_header = 45  # top header space
    v_pad = 20  # bottom padding

    # Pick column count (1 to badge_count) that produces aspect ratio closest to 4:3
    target_ratio = 4.0 / 3.0
    best_cols = 1
    best_diff = float("inf")
    max_search_cols = max(1, badge_count)

    for c in range(1, max_search_cols + 1):
        r = max(1, -(-badge_count // c))  # ceil division
        w = right_start_x + c * col_width + h_pad
        h = max(175, v_header + r * row_height + v_pad)
        diff = abs((w / h) - target_ratio)
        if diff < best_diff:
            best_diff = diff
            best_cols = c

    cols = best_cols if badge_count else 3
    rows = max(1, -(-badge_count // cols))
    right_section_width = cols * col_width

    width = right_start_x + right_section_width + h_pad
    height = max(175, v_header + rows * row_height + v_pad)

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(
        renderer.svg_header(
            width,
            height,
            title=f"{data.profile.username}'s Badges",
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
      @keyframes badgeFade {
        from { opacity: 0; transform: scale(0.85); }
        to { opacity: 1; transform: scale(1); }
      }
      .badge-item { animation: badgeFade 0.3s cubic-bezier(0.16, 1, 0.3, 1) backwards; }
      @media (prefers-reduced-motion: reduce) { .badge-item { animation: none; } }
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
    svg_parts.append('<g class="badges-content">')
    gold_color = "#ffa116"

    # ── Section 1: Locked / Upcoming Badge (Left Column) ──
    svg_parts.append(
        render_icon("shield", 18, 18, 16, gold_color)
    )
    svg_parts.append(
        renderer.text(
            40,
            30,
            "Locked Badge",
            font_size=13,
            fill=theme.title_color,
            weight="600",
            anchor="start",
        )
    )

    up_badge = upcoming[0] if upcoming else None
    up_name = up_badge.name if up_badge else "Daily Challenge"
    up_pct = up_badge.progress_percentage if up_badge else 70.0

    if len(up_name) > 14:
        up_name_display = up_name[:13] + "…"
    else:
        up_name_display = up_name

    left_cx = left_section_width / 2
    left_cy = 82

    # Hexagon base for locked badge
    svg_parts.append(
        renderer.hexagon(
            left_cx,
            left_cy,
            r=26,
            fill=theme.separator_color,
            stroke=theme.border_color,
            stroke_width=1.5,
        )
    )

    # Circular Progress Ring
    svg_parts.append(
        renderer.progress_ring(
            left_cx,
            left_cy,
            r=32,
            percentage=up_pct,
            stroke=gold_color,
            stroke_bg=theme.separator_color,
            stroke_width=3,
        )
    )

    # Lock icon inside center
    svg_parts.append(
        render_icon("lock", left_cx - 8, left_cy - 8, 16, theme.icon_color)
    )

    # Locked Badge Name & Progress Percentage
    svg_parts.append(
        renderer.text(
            left_cx,
            left_cy + 48,
            up_name_display,
            font_size=11,
            fill=theme.text_color,
            anchor="middle",
            weight="bold",
        )
    )
    svg_parts.append(
        renderer.text(
            left_cx,
            left_cy + 63,
            f"{up_pct:.0f}%",
            font_size=10,
            fill=gold_color,
            anchor="middle",
            weight="bold",
        )
    )

    # ── Vertical Separator ──
    svg_parts.append(
        f'<line x1="{divider_x}" y1="20" x2="{divider_x}" y2="{height - 20}" '
        f'stroke="{theme.separator_color}" stroke-width="1"/>'
    )

    # ── Section 2: History Awards (Right Column, max 6 per row) ──
    history_title = (
        f"History Awards ({len(badges)} earned)" if badges else "History Awards"
    )
    svg_parts.append(
        render_icon("trophy", right_start_x, 18, 16, gold_color)
    )
    svg_parts.append(
        renderer.text(
            right_start_x + 22,
            30,
            history_title,
            font_size=13,
            fill=theme.title_color,
            weight="600",
            anchor="start",
        )
    )

    # Dynamic delay so ALL badges finish animating within max 1.0s total
    anim_dur = 0.3  # duration per badge animation
    max_total_window = 1.0  # target total animation window (1.0s max!)
    max_delay = max_total_window - anim_dur  # 0.70s max delay for the last badge
    per_delay = min(0.04, max_delay / max(1, badge_count - 1)) if badge_count > 1 else 0.0

    for i, badge in enumerate(badges):
        row = i // cols
        col = i % cols
        cx = right_start_x + col * col_width + col_width / 2
        cy = 82 + row * row_height
        delay = i * per_delay

        svg_parts.append(
            f'<g class="badge-item" style="animation-delay: {delay:.2f}s">'
        )

        is_active = i == (len(badges) - 1)  # Most recent badge is active
        border_stroke = (
            gold_color if is_active else theme.border_color
        )

        # Hexagon badge frame
        svg_parts.append(
            renderer.hexagon(
                cx,
                cy,
                r=26,
                fill=theme.separator_color,
                stroke=border_stroke,
                stroke_width=1.5,
            )
        )

        # Badge category icon inside
        icon_name = _get_badge_icon(badge.category)
        icon_color = gold_color if is_active else theme.text_color
        svg_parts.append(
            render_icon(icon_name, cx - 10, cy - 10, 20, icon_color)
        )

        # Badge short name
        name = badge.short_label
        if len(name) > 11:
            name = name[:10] + "…"
        svg_parts.append(
            renderer.text(
                cx,
                cy + 48,
                name,
                font_size=11,
                fill=theme.text_color,
                anchor="middle",
                weight="bold",
            )
        )

        # Status or Creation Date
        if is_active:
            # Active indicator tag
            svg_parts.append(
                renderer.text(
                    cx,
                    cy + 63,
                    "✔ Active",
                    font_size=10,
                    fill=gold_color,
                    anchor="middle",
                    weight="600",
                )
            )
        elif badge.creation_date:
            date_str = (
                badge.creation_date[:10]
                if len(badge.creation_date) >= 10
                else badge.creation_date
            )
            svg_parts.append(
                renderer.text(
                    cx,
                    cy + 63,
                    date_str,
                    font_size=10,
                    fill=theme.text_secondary,
                    anchor="middle",
                )
            )

        svg_parts.append("</g>")

    svg_parts.append("</g>")
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)


def _placeholder(renderer: SVGRenderer, theme: Theme, username: str) -> str:
    """Generate a placeholder when no badges are earned."""
    width, height = 400, 300
    parts: list[str] = []
    parts.append(
        renderer.svg_header(width, height, title=f"No badges for {username}")
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
    parts.append(render_icon("shield", 24, 24, 16, theme.icon_color))
    parts.append(
        renderer.text(
            46, 38, "Badges", font_size=16, fill=theme.title_color, weight="bold"
        )
    )
    parts.append(
        renderer.text(
            width / 2,
            140,
            "No badges earned yet",
            font_size=14,
            fill=theme.text_secondary,
            anchor="middle",
        )
    )
    parts.append(
        renderer.text(
            width / 2,
            165,
            "Keep solving problems to earn badges!",
            font_size=12,
            fill=theme.text_secondary,
            anchor="middle",
        )
    )
    parts.append(renderer.svg_footer())
    return "\n".join(parts)
