"""Font metrics and text measurement utilities.

Since we generate pure SVG without a browser, we use approximate character
width tables to estimate text dimensions for layout calculations. These
values are calibrated against common system fonts at typical SVG sizes.
"""

from __future__ import annotations

# Primary font stack used in all SVG output
FONT_FAMILY = "'Segoe UI', Roboto, 'Helvetica Neue', Ubuntu, sans-serif"
FONT_FAMILY_MONO = "'SF Mono', 'Cascadia Code', 'Fira Code', Consolas, monospace"

# Average character widths at font-size 1.0 (multiply by actual font size)
# These are empirically measured averages for the Segoe UI / Roboto family
_PROPORTIONAL_AVG_WIDTH = 0.55  # average char width as fraction of font size
_MONOSPACE_AVG_WIDTH = 0.60

# Per-character width overrides for proportional fonts (relative to font size)
_CHAR_WIDTHS: dict[str, float] = {
    " ": 0.28, "!": 0.30, '"': 0.38, "#": 0.58, "$": 0.52, "%": 0.72,
    "&": 0.65, "'": 0.22, "(": 0.32, ")": 0.32, "*": 0.42, "+": 0.58,
    ",": 0.28, "-": 0.35, ".": 0.28, "/": 0.38, "0": 0.55, "1": 0.38,
    "2": 0.52, "3": 0.52, "4": 0.55, "5": 0.52, "6": 0.55, "7": 0.48,
    "8": 0.55, "9": 0.55, ":": 0.28, ";": 0.28, "<": 0.58, "=": 0.58,
    ">": 0.58, "?": 0.45, "@": 0.85, "A": 0.62, "B": 0.58, "C": 0.58,
    "D": 0.65, "E": 0.52, "F": 0.48, "G": 0.65, "H": 0.65, "I": 0.28,
    "J": 0.38, "K": 0.58, "L": 0.48, "M": 0.78, "N": 0.65, "O": 0.68,
    "P": 0.55, "Q": 0.68, "R": 0.58, "S": 0.52, "T": 0.52, "U": 0.65,
    "V": 0.58, "W": 0.82, "X": 0.55, "Y": 0.52, "Z": 0.55,
    "a": 0.50, "b": 0.55, "c": 0.45, "d": 0.55, "e": 0.50, "f": 0.32,
    "g": 0.55, "h": 0.55, "i": 0.25, "j": 0.25, "k": 0.50, "l": 0.25,
    "m": 0.82, "n": 0.55, "o": 0.55, "p": 0.55, "q": 0.55, "r": 0.35,
    "s": 0.42, "t": 0.35, "u": 0.55, "v": 0.48, "w": 0.72, "x": 0.48,
    "y": 0.48, "z": 0.45,
}


def measure_text(text: str, font_size: float, weight: str = "normal") -> float:
    """Estimate the rendered width of a text string in pixels.

    Args:
        text: The text string to measure.
        font_size: The font size in pixels.
        weight: Font weight ('normal' or 'bold'). Bold adds ~8% width.

    Returns:
        Estimated width in pixels.
    """
    width = 0.0
    for char in text:
        char_w = _CHAR_WIDTHS.get(char, _PROPORTIONAL_AVG_WIDTH)
        width += char_w * font_size

    # Bold text is typically ~8% wider
    if weight == "bold" or weight == "600" or weight == "700":
        width *= 1.08

    return width


def measure_text_mono(text: str, font_size: float) -> float:
    """Estimate the rendered width of monospaced text.

    Args:
        text: The text string to measure.
        font_size: The font size in pixels.

    Returns:
        Estimated width in pixels.
    """
    return len(text) * _MONOSPACE_AVG_WIDTH * font_size


def truncate_text(text: str, max_width: float, font_size: float, suffix: str = "…") -> str:
    """Truncate text to fit within a maximum width, adding an ellipsis.

    Args:
        text: The text to potentially truncate.
        max_width: Maximum allowed width in pixels.
        font_size: The font size in pixels.
        suffix: The truncation suffix (default: ellipsis).

    Returns:
        The original text if it fits, or truncated text with suffix.
    """
    if measure_text(text, font_size) <= max_width:
        return text

    suffix_width = measure_text(suffix, font_size)
    available = max_width - suffix_width

    result = ""
    current_width = 0.0
    for char in text:
        char_w = _CHAR_WIDTHS.get(char, _PROPORTIONAL_AVG_WIDTH) * font_size
        if current_width + char_w > available:
            break
        result += char
        current_width += char_w

    return result + suffix
