"""Core SVG rendering engine with shared utilities for all card generators.

Provides helper functions for creating SVG elements, gradients, filters,
and Jinja2 template rendering. All card generators build on this foundation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..utils.colors import darken, hex_with_alpha, lighten
from ..utils.fonts import FONT_FAMILY, FONT_FAMILY_MONO, measure_text
from ..utils.icons import render_icon
from ..utils.math import format_number
from .themes import Theme

# Template directory
TEMPLATES_DIR = Path(__file__).parent / "templates"


class SVGRenderer:
    """Core SVG rendering engine with Jinja2 template support.

    Provides shared utilities used by all card generators:
    - Jinja2 template rendering
    - SVG element helpers (gradients, shadows, rounded rects, etc.)
    - Layout calculation helpers
    """

    def __init__(self, theme: Theme) -> None:
        """Initialize the renderer with a theme.

        Args:
            theme: The color theme to use for rendering.
        """
        self.theme = theme
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(["svg", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters and globals
        self._env.filters["format_number"] = format_number
        self._env.filters["lighten"] = lighten
        self._env.filters["darken"] = darken

        self._env.globals["icon"] = render_icon
        self._env.globals["theme"] = theme
        self._env.globals["font_family"] = FONT_FAMILY
        self._env.globals["font_family_mono"] = FONT_FAMILY_MONO
        self._env.globals["measure_text"] = measure_text
        self._env.globals["hex_with_alpha"] = hex_with_alpha

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a Jinja2 SVG template with the given context.

        Args:
            template_name: Name of the template file (e.g., 'stats.svg').
            context: Template variables to inject.

        Returns:
            The rendered SVG string.
        """
        template = self._env.get_template(template_name)
        return template.render(**context)

    def render_string(self, template_str: str, context: dict[str, Any]) -> str:
        """Render an SVG template from a string.

        Args:
            template_str: The Jinja2 template string.
            context: Template variables.

        Returns:
            The rendered SVG string.
        """
        template = self._env.from_string(template_str)
        return template.render(**context)

    @staticmethod
    def svg_header(
        width: int,
        height: int,
        title: str = "",
        desc: str = "",
    ) -> str:
        """Generate an SVG opening tag with proper attributes.

        Args:
            width: SVG width in pixels.
            height: SVG height in pixels.
            title: Accessible title for the SVG.
            desc: Accessible description.

        Returns:
            SVG opening tag string.
        """
        parts = [
            f'<svg width="{width}" height="{height}"',
            f'  viewBox="0 0 {width} {height}"',
            '  xmlns="http://www.w3.org/2000/svg"',
            '  xmlns:xlink="http://www.w3.org/1999/xlink"',
            '  role="img"',
        ]
        if title:
            parts.append(f'  aria-label="{title}"')
        parts.append(">")

        svg = "\n".join(parts) + "\n"

        if title:
            svg += f"  <title>{title}</title>\n"
        if desc:
            svg += f"  <desc>{desc}</desc>\n"

        return svg

    @staticmethod
    def svg_footer() -> str:
        """Generate the SVG closing tag."""
        return "</svg>"

    @staticmethod
    def create_gradient(
        gradient_id: str,
        color1: str,
        color2: str,
        direction: str = "vertical",
    ) -> str:
        """Create a linear gradient definition.

        Args:
            gradient_id: Unique ID for the gradient.
            color1: Start color (hex).
            color2: End color (hex).
            direction: 'vertical', 'horizontal', or 'diagonal'.

        Returns:
            SVG <linearGradient> element string.
        """
        coords = {
            "vertical": ('x1="0%" y1="0%" x2="0%" y2="100%"'),
            "horizontal": ('x1="0%" y1="0%" x2="100%" y2="0%"'),
            "diagonal": ('x1="0%" y1="0%" x2="100%" y2="100%"'),
        }
        coord_str = coords.get(direction, coords["vertical"])

        return (
            f'<linearGradient id="{gradient_id}" {coord_str}>'
            f'<stop offset="0%" stop-color="{color1}"/>'
            f'<stop offset="100%" stop-color="{color2}"/>'
            f"</linearGradient>"
        )

    @staticmethod
    def create_drop_shadow(
        filter_id: str = "shadow",
        blur: float = 10,
        offset_x: float = 0,
        offset_y: float = 4,
        color: str = "#00000040",
    ) -> str:
        """Create a drop shadow filter definition.

        Args:
            filter_id: Unique ID for the filter.
            blur: Blur radius.
            offset_x: Horizontal offset.
            offset_y: Vertical offset.
            color: Shadow color (with alpha).

        Returns:
            SVG <filter> element string.
        """
        return (
            f'<filter id="{filter_id}" x="-5%" y="-5%" width="110%" height="115%">'
            f'<feDropShadow dx="{offset_x}" dy="{offset_y}" '
            f'stdDeviation="{blur}" flood-color="{color}" flood-opacity="0.4"/>'
            f"</filter>"
        )

    @staticmethod
    def create_glow(
        filter_id: str = "glow",
        color: str = "#58a6ff",
        intensity: float = 3,
    ) -> str:
        """Create a glow filter for highlighted elements.

        Args:
            filter_id: Unique ID for the filter.
            color: Glow color.
            intensity: Glow blur radius.

        Returns:
            SVG <filter> element string.
        """
        return (
            f'<filter id="{filter_id}">'
            f'<feGaussianBlur stdDeviation="{intensity}" result="blur"/>'
            f'<feFlood flood-color="{color}" flood-opacity="0.6" result="color"/>'
            f'<feComposite in="color" in2="blur" operator="in" result="glow"/>'
            f'<feMerge>'
            f'<feMergeNode in="glow"/>'
            f'<feMergeNode in="SourceGraphic"/>'
            f'</feMerge>'
            f"</filter>"
        )

    @staticmethod
    def rounded_rect(
        x: float,
        y: float,
        width: float,
        height: float,
        rx: float = 12,
        fill: str = "none",
        stroke: str = "none",
        stroke_width: float = 1,
        filter_id: str | None = None,
    ) -> str:
        """Create a rounded rectangle SVG element.

        Args:
            x: X position.
            y: Y position.
            width: Rectangle width.
            height: Rectangle height.
            rx: Corner radius.
            fill: Fill color or gradient reference.
            stroke: Stroke color.
            stroke_width: Stroke width.
            filter_id: Optional filter ID for effects like shadow.

        Returns:
            SVG <rect> element string.
        """
        attrs = [
            f'x="{x}" y="{y}"',
            f'width="{width}" height="{height}"',
            f'rx="{rx}"',
            f'fill="{fill}"',
        ]
        if stroke != "none":
            attrs.append(f'stroke="{stroke}" stroke-width="{stroke_width}"')
        if filter_id:
            attrs.append(f'filter="url(#{filter_id})"')

        return f"<rect {' '.join(attrs)}/>"

    @staticmethod
    def progress_bar(
        x: float,
        y: float,
        width: float,
        height: float,
        percentage: float,
        fill: str,
        bg: str = "#21262d",
        rx: float = 4,
    ) -> str:
        """Create a progress bar with background and fill.

        Args:
            x: X position.
            y: Y position.
            width: Total bar width.
            height: Bar height.
            percentage: Fill percentage (0-100).
            fill: Fill color for the progress portion.
            bg: Background color.
            rx: Corner radius.

        Returns:
            SVG markup for the progress bar (background + fill rects).
        """
        fill_width = max(0, min(width, (percentage / 100) * width))

        parts = [
            # Background
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{rx}" fill="{bg}"/>',
        ]

        if fill_width > 0:
            # Use clipPath to ensure rounded corners on the fill
            parts.append(
                f'<rect x="{x}" y="{y}" width="{fill_width:.1f}" height="{height}" '
                f'rx="{rx}" fill="{fill}"/>'
            )

        return "\n".join(parts)

    @staticmethod
    def text(
        x: float,
        y: float,
        content: str,
        font_size: float = 14,
        fill: str = "#c9d1d9",
        anchor: str = "start",
        weight: str = "normal",
        font_family: str = FONT_FAMILY,
        dominant_baseline: str = "auto",
    ) -> str:
        """Create a text SVG element.

        Args:
            x: X position.
            y: Y position.
            content: Text content.
            font_size: Font size in pixels.
            fill: Text fill color.
            anchor: Text anchor ('start', 'middle', 'end').
            weight: Font weight.
            font_family: Font family string.
            dominant_baseline: Vertical alignment.

        Returns:
            SVG <text> element string.
        """
        # Escape XML special characters
        safe_content = (
            content
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

        attrs = [
            f'x="{x}" y="{y}"',
            f'font-size="{font_size}"',
            f'fill="{fill}"',
            f'font-family="{font_family}"',
            f'font-weight="{weight}"',
        ]
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if dominant_baseline != "auto":
            attrs.append(f'dominant-baseline="{dominant_baseline}"')

        return f"<text {' '.join(attrs)}>{safe_content}</text>"

    @staticmethod
    def css_animation(
        name: str,
        property_name: str,
        from_val: str,
        to_val: str,
        duration: str = "0.6s",
        easing: str = "ease-out",
    ) -> str:
        """Generate a CSS @keyframes animation block for embedding in SVG.

        Args:
            name: Animation name.
            property_name: CSS property to animate.
            from_val: Starting value.
            to_val: Ending value.
            duration: Animation duration.
            easing: Timing function.

        Returns:
            CSS style block string.
        """
        return (
            f"@keyframes {name} {{"
            f" from {{ {property_name}: {from_val}; }}"
            f" to {{ {property_name}: {to_val}; }}"
            f" }}"
        )
