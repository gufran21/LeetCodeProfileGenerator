"""Difficulty distribution card generator.

Generates `difficulty.svg` featuring a modern circular donut gauge
with symmetrical 260° gauge arc (start and end terminals aligned on a flat horizontal line),
arc separator gaps, solved progress overlays, dedicated difficulty focus gauges,
and a 15-second looping multi-phase rising arc animation (Solved → Acceptance → Beats Easy → Beats Medium → Beats Hard).
"""

from __future__ import annotations

import math

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from ..utils.fonts import FONT_FAMILY
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
    width = 450
    height = 200

    svg_parts: list[str] = []

    # ── SVG Header ──
    svg_parts.append(
        renderer.svg_header(
            width,
            height,
            title=f"{data.profile.username}'s Difficulty Breakdown",
            desc="Easy, Medium, Hard problem solving statistics",
        )
    )

    # ── Symmetrical Circular Donut Gauge Math (260° Arc) ──
    # Arc geometry: 260° visible arc with 100° bottom gap centered at 6 o'clock.
    # rotate(140) places start at 140° and end at 40° (both at same y-coordinate).
    cx, cy, r = 135.0, 105.0, 65.0
    c_len = 2.0 * math.pi * r  # ~408.41px circumference
    arc_deg = 260.0
    arc_span = (arc_deg / 360.0) * c_len  # 260° arc (~294.95px)
    rot_angle = 140  # 270 - 260/2 = 140° → horizontal start/end alignment
    gap_len = 14.0   # Gap between arc segments

    solved = data.solved
    total_questions = max(1, solved.total_total)

    # ── Segment sizing: 2 gaps sit BETWEEN 3 segments ──
    # Usable arc = total arc - 2 gaps (no gap at the two outer terminals)
    usable_span = arc_span - 2.0 * gap_len

    easy_ratio = solved.easy_total / total_questions
    medium_ratio = solved.medium_total / total_questions
    hard_ratio = solved.hard_total / total_questions

    # Base segment lengths (light background arcs)
    easy_seg = max(0.1, easy_ratio * usable_span)
    medium_seg = max(0.1, medium_ratio * usable_span)
    hard_seg = max(0.1, hard_ratio * usable_span)

    # Segment start offsets along the arc
    easy_start = 0.0
    medium_start = easy_seg + gap_len
    hard_start = easy_seg + gap_len + medium_seg + gap_len

    # Solved progress segment lengths (proportional within usable_span)
    easy_solved_seg = max(0.0, (solved.easy_solved / total_questions) * usable_span)
    medium_solved_seg = max(0.0, (solved.medium_solved / total_questions) * usable_span)
    hard_solved_seg = max(0.0, (solved.hard_solved / total_questions) * usable_span)

    # Dedicated focus progress lengths (relative to individual difficulty total, using full arc)
    easy_focus_len = (solved.easy_solved / max(1, solved.easy_total)) * arc_span
    medium_focus_len = (solved.medium_solved / max(1, solved.medium_total)) * arc_span
    hard_focus_len = (solved.hard_solved / max(1, solved.hard_total)) * arc_span

    # ── Defs & Keyframes ──
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
      @keyframes phase1 {{
        0%, 18% {{ opacity: 1; transform: scale(1); }}
        20%, 98% {{ opacity: 0; transform: scale(0.96); }}
        100% {{ opacity: 1; transform: scale(1); }}
      }}
      @keyframes phase2 {{
        0%, 18% {{ opacity: 0; transform: scale(0.96); }}
        20%, 38% {{ opacity: 1; transform: scale(1); }}
        40%, 100% {{ opacity: 0; transform: scale(0.96); }}
      }}
      @keyframes phase3 {{
        0%, 38% {{ opacity: 0; transform: scale(0.96); }}
        40%, 58% {{ opacity: 1; transform: scale(1); }}
        60%, 100% {{ opacity: 0; transform: scale(0.96); }}
      }}
      @keyframes phase4 {{
        0%, 58% {{ opacity: 0; transform: scale(0.96); }}
        60%, 78% {{ opacity: 1; transform: scale(1); }}
        80%, 100% {{ opacity: 0; transform: scale(0.96); }}
      }}
      @keyframes phase5 {{
        0%, 78% {{ opacity: 0; transform: scale(0.96); }}
        80%, 98% {{ opacity: 1; transform: scale(1); }}
        100% {{ opacity: 0; transform: scale(0.96); }}
      }}

      /* Phase 1 Combined Solved Rising Arc Animations */
      @keyframes riseEasyComb {{
        0% {{ stroke-dasharray: 0 {c_len:.1f}; }}
        4%, 18% {{ stroke-dasharray: {easy_solved_seg:.1f} {c_len - easy_solved_seg:.1f}; }}
        20%, 100% {{ stroke-dasharray: {easy_solved_seg:.1f} {c_len - easy_solved_seg:.1f}; }}
      }}
      @keyframes riseMedComb {{
        0% {{ stroke-dasharray: 0 {c_len:.1f}; }}
        4%, 18% {{ stroke-dasharray: {medium_solved_seg:.1f} {c_len - medium_solved_seg:.1f}; }}
        20%, 100% {{ stroke-dasharray: {medium_solved_seg:.1f} {c_len - medium_solved_seg:.1f}; }}
      }}
      @keyframes riseHardComb {{
        0% {{ stroke-dasharray: 0 {c_len:.1f}; }}
        4%, 18% {{ stroke-dasharray: {hard_solved_seg:.1f} {c_len - hard_solved_seg:.1f}; }}
        20%, 100% {{ stroke-dasharray: {hard_solved_seg:.1f} {c_len - hard_solved_seg:.1f}; }}
      }}

      /* Dedicated Focus Rising Progress Arc Animations */
      @keyframes riseEasyArc {{
        0%, 39% {{ stroke-dasharray: 0 {c_len:.1f}; }}
        40% {{ stroke-dasharray: 0 {c_len:.1f}; }}
        44%, 58% {{ stroke-dasharray: {easy_focus_len:.1f} {c_len - easy_focus_len:.1f}; }}
        60%, 100% {{ stroke-dasharray: 0 {c_len:.1f}; }}
      }}
      @keyframes riseMedArc {{
        0%, 59% {{ stroke-dasharray: 0 {c_len:.1f}; }}
        60% {{ stroke-dasharray: 0 {c_len:.1f}; }}
        64%, 78% {{ stroke-dasharray: {medium_focus_len:.1f} {c_len - medium_focus_len:.1f}; }}
        80%, 100% {{ stroke-dasharray: 0 {c_len:.1f}; }}
      }}
      @keyframes riseHardArc {{
        0%, 79% {{ stroke-dasharray: 0 {c_len:.1f}; }}
        80% {{ stroke-dasharray: 0 {c_len:.1f}; }}
        84%, 98% {{ stroke-dasharray: {hard_focus_len:.1f} {c_len - hard_focus_len:.1f}; }}
        100% {{ stroke-dasharray: 0 {c_len:.1f}; }}
      }}

      .phase {{ transform-origin: {cx}px {cy}px; transition: all 0.4s ease; }}
      .p1 {{ animation: phase1 15s infinite ease-in-out; }}
      .p2 {{ animation: phase2 15s infinite ease-in-out; }}
      .p3 {{ animation: phase3 15s infinite ease-in-out; }}
      .p4 {{ animation: phase4 15s infinite ease-in-out; }}
      .p5 {{ animation: phase5 15s infinite ease-in-out; }}

      .rise-easy-comb {{ animation: riseEasyComb 15s infinite cubic-bezier(0.0, 0.7, 0.1, 1.0); }}
      .rise-med-comb {{ animation: riseMedComb 15s infinite cubic-bezier(0.0, 0.7, 0.1, 1.0); }}
      .rise-hard-comb {{ animation: riseHardComb 15s infinite cubic-bezier(0.0, 0.7, 0.1, 1.0); }}

      .rise-easy {{ animation: riseEasyArc 15s infinite cubic-bezier(0.0, 0.7, 0.1, 1.0); }}
      .rise-med {{ animation: riseMedArc 15s infinite cubic-bezier(0.0, 0.7, 0.1, 1.0); }}
      .rise-hard {{ animation: riseHardArc 15s infinite cubic-bezier(0.0, 0.7, 0.1, 1.0); }}

      @media (prefers-reduced-motion: reduce) {{
        .p1 {{ opacity: 1 !important; animation: none !important; }}
        .p2, .p3, .p4, .p5 {{ display: none !important; }}
        .rise-easy-comb, .rise-med-comb, .rise-hard-comb {{ animation: none !important; }}
        .rise-easy, .rise-med, .rise-hard {{ animation: none !important; }}
      }}
    """)
    svg_parts.append("</style>")
    svg_parts.append("</defs>")

    # ── Card Background ──
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

    # ── Helper: create a circle arc element ──
    def _arc(
        color: str,
        dash_len: float,
        offset: float,
        width_val: int = 8,
        opacity: float | None = None,
        css_class: str = "",
    ) -> str:
        """Build an SVG circle element for one donut arc segment."""
        cls = f'class="{css_class}" ' if css_class else ""
        opa = f'stroke-opacity="{opacity}" ' if opacity is not None else ""
        return (
            f'<circle {cls}cx="{cx}" cy="{cy}" r="{r}" fill="none" '
            f'stroke="{color}" {opa}stroke-width="{width_val}" '
            f'stroke-dasharray="{dash_len:.1f} {c_len - dash_len:.1f}" '
            f'stroke-dashoffset="{-offset:.1f}" stroke-linecap="round" '
            f'transform="rotate({rot_angle} {cx} {cy})"/>'
        )

    # ── Helper for Combined Arc Group (Phases 1 & 2) ──
    def _combined_gauge_base() -> list[str]:
        """Light translucent background arcs: Easy → gap → Medium → gap → Hard."""
        return [
            _arc(theme.easy_color, easy_seg, easy_start, opacity=0.22),
            _arc(theme.medium_color, medium_seg, medium_start, opacity=0.22),
            _arc(theme.hard_color, hard_seg, hard_start, opacity=0.22),
        ]

    # ── Phase 1: Solved Summary (3-Arc Simultaneous Rise Animation + tspan) ──
    svg_parts.append('<g class="phase p1">')
    svg_parts.extend(_combined_gauge_base())
    if easy_solved_seg > 0:
        svg_parts.append(
            _arc(theme.easy_color, 0, easy_start, css_class="rise-easy-comb")
        )
    if medium_solved_seg > 0:
        svg_parts.append(
            _arc(theme.medium_color, 0, medium_start, css_class="rise-med-comb")
        )
    if hard_solved_seg > 0:
        svg_parts.append(
            _arc(theme.hard_color, 0, hard_start, css_class="rise-hard-comb")
        )

    t_solved_str = format_number(solved.total_solved)
    t_total_str = f"/{format_number(solved.total_total)}"
    svg_parts.append(
        f'<text x="{cx}" y="{cy - 2}" font-family="{FONT_FAMILY}" text-anchor="middle">'
        f'<tspan font-size="22" font-weight="bold" fill="{theme.title_color}">{t_solved_str}</tspan>'
        f'<tspan font-size="14" font-weight="normal" fill="{theme.text_secondary}">{t_total_str}</tspan>'
        f'</text>'
    )
    svg_parts.append(
        renderer.text(
            cx,
            cy + 18,
            "✔ Solved",
            font_size=12,
            fill=theme.easy_color,
            weight="600",
            anchor="middle",
        )
    )
    svg_parts.append("</g>")

    # ── Phase 2: Acceptance Rate ──
    svg_parts.append('<g class="phase p2">')
    svg_parts.extend(_combined_gauge_base())
    if easy_solved_seg > 0:
        svg_parts.append(
            _arc(theme.easy_color, easy_solved_seg, easy_start)
        )
    if medium_solved_seg > 0:
        svg_parts.append(
            _arc(theme.medium_color, medium_solved_seg, medium_start)
        )
    if hard_solved_seg > 0:
        svg_parts.append(
            _arc(theme.hard_color, hard_solved_seg, hard_start)
        )
    svg_parts.append(
        renderer.text(
            cx,
            cy - 2,
            f"{solved.acceptance_rate:.1f}%",
            font_size=22,
            fill=theme.title_color,
            weight="bold",
            anchor="middle",
        )
    )
    svg_parts.append(
        renderer.text(
            cx,
            cy + 18,
            "Acceptance",
            font_size=12,
            fill=theme.text_secondary,
            weight="600",
            anchor="middle",
        )
    )
    svg_parts.append("</g>")

    # ── Phase 3: Beats Easy (Full 260° Easy Base + Rising Arc) ──
    easy_beats_val = (
        f"{solved.easy_beats:.1f}%"
        if solved.easy_beats is not None
        else f"{solved.easy_percentage:.1f}%"
    )
    svg_parts.append('<g class="phase p3">')
    svg_parts.append(_arc(theme.easy_color, arc_span, 0, opacity=0.22))
    if easy_focus_len > 0:
        svg_parts.append(
            _arc(theme.easy_color, 0, 0, width_val=9, css_class="rise-easy")
        )
    svg_parts.append(
        renderer.text(cx, cy - 16, "Beats", font_size=11,
                      fill=theme.text_secondary, anchor="middle")
    )
    svg_parts.append(
        renderer.text(cx, cy + 6, easy_beats_val, font_size=20,
                      fill=theme.easy_color, weight="bold", anchor="middle")
    )
    svg_parts.append(
        renderer.text(cx, cy + 22, "Easy", font_size=11,
                      fill=theme.easy_color, weight="bold", anchor="middle")
    )
    svg_parts.append("</g>")

    # ── Phase 4: Beats Medium (Full 260° Medium Base + Rising Arc) ──
    med_beats_val = (
        f"{solved.medium_beats:.1f}%"
        if solved.medium_beats is not None
        else f"{solved.medium_percentage:.1f}%"
    )
    svg_parts.append('<g class="phase p4">')
    svg_parts.append(_arc(theme.medium_color, arc_span, 0, opacity=0.22))
    if medium_focus_len > 0:
        svg_parts.append(
            _arc(theme.medium_color, 0, 0, width_val=9, css_class="rise-med")
        )
    svg_parts.append(
        renderer.text(cx, cy - 16, "Beats", font_size=11,
                      fill=theme.text_secondary, anchor="middle")
    )
    svg_parts.append(
        renderer.text(cx, cy + 6, med_beats_val, font_size=20,
                      fill=theme.medium_color, weight="bold", anchor="middle")
    )
    svg_parts.append(
        renderer.text(cx, cy + 22, "Med.", font_size=11,
                      fill=theme.medium_color, weight="bold", anchor="middle")
    )
    svg_parts.append("</g>")

    # ── Phase 5: Beats Hard (Full 260° Hard Base + Rising Arc) ──
    hard_beats_val = (
        f"{solved.hard_beats:.1f}%"
        if solved.hard_beats is not None
        else f"{solved.hard_percentage:.1f}%"
    )
    svg_parts.append('<g class="phase p5">')
    svg_parts.append(_arc(theme.hard_color, arc_span, 0, opacity=0.22))
    if hard_focus_len > 0:
        svg_parts.append(
            _arc(theme.hard_color, 0, 0, width_val=9, css_class="rise-hard")
        )
    svg_parts.append(
        renderer.text(cx, cy - 16, "Beats", font_size=11,
                      fill=theme.text_secondary, anchor="middle")
    )
    svg_parts.append(
        renderer.text(cx, cy + 6, hard_beats_val, font_size=20,
                      fill=theme.hard_color, weight="bold", anchor="middle")
    )
    svg_parts.append(
        renderer.text(cx, cy + 22, "Hard", font_size=11,
                      fill=theme.hard_color, weight="bold", anchor="middle")
    )
    svg_parts.append("</g>")

    # ── Right: Stacked Cards for Easy, Medium, Hard ──
    right_x = 265
    card_w = 160
    card_h = 44
    start_y = 30
    gap = 10

    cards_data = [
        ("Easy", solved.easy_solved, solved.easy_total, theme.easy_color),
        ("Med.", solved.medium_solved, solved.medium_total, theme.medium_color),
        ("Hard", solved.hard_solved, solved.hard_total, theme.hard_color),
    ]

    for i, (label, s_count, t_count, color) in enumerate(cards_data):
        y_pos = start_y + i * (card_h + gap)

        # Rounded pill card background
        svg_parts.append(
            f'<rect x="{right_x}" y="{y_pos}" width="{card_w}" height="{card_h}" '
            f'rx="8" fill="{theme.separator_color}" fill-opacity="0.5" '
            f'stroke="{theme.border_color}" stroke-width="0.5"/>'
        )

        # Label
        svg_parts.append(
            renderer.text(
                right_x + card_w / 2,
                y_pos + 16,
                label,
                font_size=12,
                fill=color,
                weight="bold",
                anchor="middle",
            )
        )

        # Count (Solved / Total)
        svg_parts.append(
            renderer.text(
                right_x + card_w / 2,
                y_pos + 33,
                f"{s_count}/{t_count}",
                font_size=12,
                fill=theme.text_color,
                weight="bold",
                anchor="middle",
            )
        )

    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)
