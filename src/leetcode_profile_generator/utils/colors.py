"""Color manipulation utilities for SVG generation."""

from __future__ import annotations


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple.

    Args:
        hex_color: A hex color string like '#ff5500' or 'ff5500'.

    Returns:
        A tuple of (red, green, blue) integers in the range 0-255.
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to a hex color string.

    Args:
        r: Red component (0-255).
        g: Green component (0-255).
        b: Blue component (0-255).

    Returns:
        A hex color string like '#ff5500'.
    """
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten(hex_color: str, amount: float = 0.2) -> str:
    """Lighten a hex color by the given amount.

    Args:
        hex_color: The hex color to lighten.
        amount: How much to lighten (0.0 = no change, 1.0 = white).

    Returns:
        The lightened hex color.
    """
    r, g, b = hex_to_rgb(hex_color)
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return rgb_to_hex(r, g, b)


def darken(hex_color: str, amount: float = 0.2) -> str:
    """Darken a hex color by the given amount.

    Args:
        hex_color: The hex color to darken.
        amount: How much to darken (0.0 = no change, 1.0 = black).

    Returns:
        The darkened hex color.
    """
    r, g, b = hex_to_rgb(hex_color)
    r = int(r * (1 - amount))
    g = int(g * (1 - amount))
    b = int(b * (1 - amount))
    return rgb_to_hex(r, g, b)


def with_opacity(hex_color: str, opacity: float) -> str:
    """Convert a hex color to an rgba() string with the given opacity.

    Args:
        hex_color: The hex color.
        opacity: Opacity value from 0.0 (transparent) to 1.0 (opaque).

    Returns:
        An rgba() CSS string.
    """
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r},{g},{b},{opacity:.2f})"


def hex_with_alpha(hex_color: str, opacity: float) -> str:
    """Convert a hex color to an 8-digit hex string with alpha.

    This format (#rrggbbaa) is supported in SVG and works better
    than rgba() in some SVG renderers including GitHub's.

    Args:
        hex_color: The hex color (6-digit).
        opacity: Opacity value from 0.0 to 1.0.

    Returns:
        An 8-digit hex color string like '#ff550080'.
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    alpha = int(max(0.0, min(1.0, opacity)) * 255)
    return f"#{hex_color}{alpha:02x}"


def interpolate(color1: str, color2: str, t: float) -> str:
    """Linearly interpolate between two hex colors.

    Args:
        color1: Start color (hex).
        color2: End color (hex).
        t: Interpolation factor (0.0 = color1, 1.0 = color2).

    Returns:
        The interpolated hex color.
    """
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return rgb_to_hex(r, g, b)


def heatmap_color(count: int, levels: list[str]) -> str:
    """Map a submission count to a heatmap color from the given level list.

    Args:
        count: Number of submissions for a day.
        levels: List of 5 colors [empty, l1, l2, l3, l4].

    Returns:
        The appropriate color for the given count.
    """
    if count == 0:
        return levels[0]
    elif count <= 3:
        return levels[1]
    elif count <= 6:
        return levels[2]
    elif count <= 9:
        return levels[3]
    else:
        return levels[4]
