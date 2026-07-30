"""Combined master dashboard card generator.

Generates `dashboard.svg` by assembling individual card contents into a single,
unified master card container with tight panel spacing and zero clipping/stripping.
"""

from __future__ import annotations

import re

from ..models.combined import LeetCodeData
from ..render.svg import SVGRenderer
from ..render.themes import Theme
from .difficulty import generate_difficulty_card
from .heatmap import generate_heatmap_card
from .rating import generate_rating_card
from .stats import generate_stats_card
from .streak import generate_streak_card


def _extract_card_components(svg_str: str) -> tuple[str, str]:
    """Extract defs inner content and body content without outer card background rect.

    Args:
        svg_str: Complete standalone SVG string of a card.

    Returns:
        Tuple of (defs_content, body_content).
    """
    defs_content = ""
    if "<defs>" in svg_str and "</defs>" in svg_str:
        d_start = svg_str.find("<defs>") + 6
        d_end = svg_str.find("</defs>")
        defs_content = svg_str[d_start:d_end].strip()
        body_content = svg_str[d_end + 7 : svg_str.rfind("</svg>")].strip()
    else:
        body_start = svg_str.find(">") + 1
        body_end = svg_str.rfind("</svg>")
        body_content = svg_str[body_start:body_end].strip()

    # Strip outer background rectangle to merge into unified master card
    body_content = re.sub(
        r'<rect x="0\.5" y="0\.5"[^>]*filter="url\(#card_shadow\)"[^>]*/>',
        "",
        body_content,
    )

    return defs_content, body_content


def generate_dashboard_card(data: LeetCodeData, theme: Theme) -> str:
    """Generate the master composite dashboard card SVG.

    Assembles all cards into ONE unified master card with subtle section panels,
    tight 16px spacing, and zero right-edge clipping or stripping.

    Args:
        data: Complete LeetCode user data.
        theme: Color theme.

    Returns:
        Complete SVG string for the composite dashboard card.
    """
    renderer = SVGRenderer(theme)

    # Generate individual cards
    stats_svg = generate_stats_card(data, theme)
    streak_svg = generate_streak_card(data, theme)
    diff_svg = generate_difficulty_card(data, theme)
    rating_svg = generate_rating_card(data, theme)
    heatmap_svg = generate_heatmap_card(data, theme)

    # Section Panels (Master Card: 920 x 694)
    # Standalone Heatmap width is 825px. Scale: 888 / 825 = 1.07636
    # Top Left: Stats (16, 16, w=436, h=200)
    # Top Right: Contest Rating History (468, 16, w=436, h=200)
    # --- 16px Vertical Gap ---
    # Mid Left: Difficulty (16, 232, w=436, h=210)
    # Mid Right: Activity Streak (468, 232, w=436, h=210)
    # --- 16px Vertical Gap ---
    # Bottom: Heatmap (16, 458, w=888, h=220)
    cards = [
        ("stats", stats_svg, 16, 16, 436 / 450, 200 / 220),
        ("rating", rating_svg, 468, 16, 436 / 600, 200 / 300),
        ("diff", diff_svg, 16, 232, 436 / 450, 210 / 260),
        ("streak", streak_svg, 468, 232, 436 / 460, 210 / 295),
        ("heatmap", heatmap_svg, 16, 458, 888 / 825, 1.0),
    ]

    width = 920
    height = 694

    all_defs: list[str] = []
    svg_parts: list[str] = []

    # Master SVG header
    svg_parts.append(
        renderer.svg_header(
            width,
            height,
            title=f"{data.profile.username}'s LeetCode Unified Dashboard",
        )
    )

    # Defs collection
    all_defs.append(
        renderer.create_drop_shadow(
            "card_shadow", blur=8, offset_y=4, color=theme.shadow_color
        )
    )
    if theme.bg_gradient:
        all_defs.append(
            renderer.create_gradient(
                "bg_grad", theme.bg_gradient[0], theme.bg_gradient[1]
            )
        )

    # Collect defs and body content from each card
    body_groups: list[str] = []
    seen_def_ids: set[str] = {"card_shadow", "bg_grad"}

    for name, card_str, x, y, scale_x, scale_y in cards:
        defs_str, body_str = _extract_card_components(card_str)

        # Deduplicate defs
        if defs_str:
            for def_block in re.split(
                r"(?=<filter|<linearGradient|<radialGradient|<style|<clipPath)",
                defs_str,
            ):
                def_block = def_block.strip()
                if not def_block:
                    continue
                match = re.search(r'id="([^"]+)"', def_block)
                if match:
                    def_id = match.group(1)
                    if def_id not in seen_def_ids:
                        seen_def_ids.add(def_id)
                        all_defs.append(def_block)
                else:
                    if def_block not in all_defs:
                        all_defs.append(def_block)

        # Section background panel rect
        panel_w = 436 if name != "heatmap" else 888
        panel_h = (
            200
            if "stats" in name or "rating" in name
            else (210 if "diff" in name or "streak" in name else 220)
        )

        panel_rect = (
            f'<rect x="{x}" y="{y}" width="{panel_w}" height="{panel_h}" rx="10" '
            f'fill="{theme.separator_color}" fill-opacity="0.35" '
            f'stroke="{theme.border_color}" stroke-width="0.8"/>'
        )
        body_groups.append(panel_rect)

        # Wrap visual content in transform group
        transform_attr = (
            f'transform="translate({x}, {y}) scale({scale_x:.5f}, {scale_y:.5f})"'
        )
        body_groups.append(
            f'<g id="dash_section_{name}" {transform_attr}>\n{body_str}\n</g>'
        )

    # Combine master defs
    svg_parts.append("<defs>")
    svg_parts.extend(all_defs)
    svg_parts.append("</defs>")

    # Master Outer Card background
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

    # Add embedded card sections
    svg_parts.extend(body_groups)

    # Master SVG footer
    svg_parts.append(renderer.svg_footer())

    return "\n".join(svg_parts)
