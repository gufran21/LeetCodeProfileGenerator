"""Theme engine with 9 built-in themes and custom theme support.

Each theme defines a complete color palette for rendering SVG cards.
Themes are designed to match popular editor/terminal color schemes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Theme:
    """A complete color theme for SVG card rendering.

    All color values are hex strings (e.g., '#0d1117').
    """

    name: str

    # Background
    bg_color: str
    bg_gradient: tuple[str, str] | None = None

    # Text
    title_color: str = "#ffffff"
    text_color: str = "#c9d1d9"
    text_secondary: str = "#8b949e"

    # Structure
    border_color: str = "#30363d"
    border_radius: int = 12
    shadow_color: str = "#00000040"
    separator_color: str = "#21262d"

    # Difficulty
    easy_color: str = "#00b8a3"
    medium_color: str = "#ffc01e"
    hard_color: str = "#ff375f"

    # Charts
    accent_color: str = "#58a6ff"
    chart_line_color: str = "#58a6ff"
    chart_fill_color: str = "#58a6ff26"
    chart_grid_color: str = "#21262d"
    chart_dot_color: str = "#58a6ff"

    # Heatmap
    heatmap_empty: str = "#161b22"
    heatmap_l1: str = "#0e4429"
    heatmap_l2: str = "#006d32"
    heatmap_l3: str = "#26a641"
    heatmap_l4: str = "#39d353"

    # Icons
    icon_color: str = "#8b949e"

    # Progress bars
    progress_bg: str = "#21262d"
    progress_radius: int = 4


# ────────────────────────────────────────────────────────────────────
# Built-in themes
# ────────────────────────────────────────────────────────────────────

GITHUB_DARK = Theme(
    name="github_dark",
    bg_color="#0d1117",
    bg_gradient=("#0d1117", "#161b22"),
    title_color="#e6edf3",
    text_color="#c9d1d9",
    text_secondary="#8b949e",
    border_color="#30363d",
    separator_color="#21262d",
    shadow_color="#00000060",
    easy_color="#00b8a3",
    medium_color="#ffc01e",
    hard_color="#ff375f",
    accent_color="#58a6ff",
    chart_line_color="#58a6ff",
    chart_fill_color="#58a6ff1a",
    chart_grid_color="#21262d",
    chart_dot_color="#58a6ff",
    heatmap_empty="#161b22",
    heatmap_l1="#0e4429",
    heatmap_l2="#006d32",
    heatmap_l3="#26a641",
    heatmap_l4="#39d353",
    icon_color="#8b949e",
    progress_bg="#21262d",
)

GITHUB_LIGHT = Theme(
    name="github_light",
    bg_color="#ffffff",
    bg_gradient=("#ffffff", "#f6f8fa"),
    title_color="#24292f",
    text_color="#1f2328",
    text_secondary="#656d76",
    border_color="#d0d7de",
    separator_color="#d8dee4",
    shadow_color="#00000015",
    easy_color="#1a7f37",
    medium_color="#bf8700",
    hard_color="#cf222e",
    accent_color="#0969da",
    chart_line_color="#0969da",
    chart_fill_color="#0969da15",
    chart_grid_color="#d0d7de",
    chart_dot_color="#0969da",
    heatmap_empty="#ebedf0",
    heatmap_l1="#9be9a8",
    heatmap_l2="#40c463",
    heatmap_l3="#30a14e",
    heatmap_l4="#216e39",
    icon_color="#656d76",
    progress_bg="#e1e4e8",
)

DRACULA = Theme(
    name="dracula",
    bg_color="#282a36",
    bg_gradient=("#282a36", "#21222c"),
    title_color="#f8f8f2",
    text_color="#f8f8f2",
    text_secondary="#6272a4",
    border_color="#44475a",
    separator_color="#44475a",
    shadow_color="#00000060",
    easy_color="#50fa7b",
    medium_color="#ffb86c",
    hard_color="#ff5555",
    accent_color="#bd93f9",
    chart_line_color="#bd93f9",
    chart_fill_color="#bd93f91a",
    chart_grid_color="#44475a",
    chart_dot_color="#bd93f9",
    heatmap_empty="#21222c",
    heatmap_l1="#2d4a22",
    heatmap_l2="#3a6b2f",
    heatmap_l3="#50fa7b80",
    heatmap_l4="#50fa7b",
    icon_color="#6272a4",
    progress_bg="#44475a",
)

NORD = Theme(
    name="nord",
    bg_color="#2e3440",
    bg_gradient=("#2e3440", "#3b4252"),
    title_color="#eceff4",
    text_color="#d8dee9",
    text_secondary="#7b88a1",
    border_color="#4c566a",
    separator_color="#434c5e",
    shadow_color="#00000050",
    easy_color="#a3be8c",
    medium_color="#ebcb8b",
    hard_color="#bf616a",
    accent_color="#88c0d0",
    chart_line_color="#88c0d0",
    chart_fill_color="#88c0d01a",
    chart_grid_color="#434c5e",
    chart_dot_color="#88c0d0",
    heatmap_empty="#3b4252",
    heatmap_l1="#4a5a3a",
    heatmap_l2="#6d8a5e",
    heatmap_l3="#8faa7e",
    heatmap_l4="#a3be8c",
    icon_color="#7b88a1",
    progress_bg="#434c5e",
)

CATPPUCCIN_MOCHA = Theme(
    name="catppuccin_mocha",
    bg_color="#1e1e2e",
    bg_gradient=("#1e1e2e", "#181825"),
    title_color="#cdd6f4",
    text_color="#cdd6f4",
    text_secondary="#6c7086",
    border_color="#313244",
    separator_color="#313244",
    shadow_color="#00000060",
    easy_color="#a6e3a1",
    medium_color="#f9e2af",
    hard_color="#f38ba8",
    accent_color="#89b4fa",
    chart_line_color="#89b4fa",
    chart_fill_color="#89b4fa1a",
    chart_grid_color="#313244",
    chart_dot_color="#89b4fa",
    heatmap_empty="#181825",
    heatmap_l1="#2d4033",
    heatmap_l2="#3d6044",
    heatmap_l3="#74c07a",
    heatmap_l4="#a6e3a1",
    icon_color="#6c7086",
    progress_bg="#313244",
)

CATPPUCCIN_LATTE = Theme(
    name="catppuccin_latte",
    bg_color="#eff1f5",
    bg_gradient=("#eff1f5", "#e6e9ef"),
    title_color="#4c4f69",
    text_color="#4c4f69",
    text_secondary="#7c7f93",
    border_color="#ccd0da",
    separator_color="#ccd0da",
    shadow_color="#00000012",
    easy_color="#40a02b",
    medium_color="#df8e1d",
    hard_color="#d20f39",
    accent_color="#1e66f5",
    chart_line_color="#1e66f5",
    chart_fill_color="#1e66f515",
    chart_grid_color="#ccd0da",
    chart_dot_color="#1e66f5",
    heatmap_empty="#dce0e8",
    heatmap_l1="#c6e6b8",
    heatmap_l2="#8cce7a",
    heatmap_l3="#5dae43",
    heatmap_l4="#40a02b",
    icon_color="#7c7f93",
    progress_bg="#ccd0da",
)

TOKYO_NIGHT = Theme(
    name="tokyo_night",
    bg_color="#1a1b26",
    bg_gradient=("#1a1b26", "#16161e"),
    title_color="#c0caf5",
    text_color="#a9b1d6",
    text_secondary="#565f89",
    border_color="#292e42",
    separator_color="#292e42",
    shadow_color="#00000060",
    easy_color="#9ece6a",
    medium_color="#e0af68",
    hard_color="#f7768e",
    accent_color="#7aa2f7",
    chart_line_color="#7aa2f7",
    chart_fill_color="#7aa2f71a",
    chart_grid_color="#292e42",
    chart_dot_color="#7aa2f7",
    heatmap_empty="#16161e",
    heatmap_l1="#2d4a2a",
    heatmap_l2="#4a7a3a",
    heatmap_l3="#73a854",
    heatmap_l4="#9ece6a",
    icon_color="#565f89",
    progress_bg="#292e42",
)

GRUVBOX_DARK = Theme(
    name="gruvbox_dark",
    bg_color="#282828",
    bg_gradient=("#282828", "#1d2021"),
    title_color="#ebdbb2",
    text_color="#ebdbb2",
    text_secondary="#928374",
    border_color="#3c3836",
    separator_color="#3c3836",
    shadow_color="#00000060",
    easy_color="#b8bb26",
    medium_color="#fabd2f",
    hard_color="#fb4934",
    accent_color="#83a598",
    chart_line_color="#83a598",
    chart_fill_color="#83a5981a",
    chart_grid_color="#3c3836",
    chart_dot_color="#83a598",
    heatmap_empty="#1d2021",
    heatmap_l1="#3d4220",
    heatmap_l2="#6b7a18",
    heatmap_l3="#98971a",
    heatmap_l4="#b8bb26",
    icon_color="#928374",
    progress_bg="#3c3836",
)

ONE_DARK = Theme(
    name="one_dark",
    bg_color="#282c34",
    bg_gradient=("#282c34", "#21252b"),
    title_color="#abb2bf",
    text_color="#abb2bf",
    text_secondary="#5c6370",
    border_color="#3e4451",
    separator_color="#3e4451",
    shadow_color="#00000060",
    easy_color="#98c379",
    medium_color="#e5c07b",
    hard_color="#e06c75",
    accent_color="#61afef",
    chart_line_color="#61afef",
    chart_fill_color="#61afef1a",
    chart_grid_color="#3e4451",
    chart_dot_color="#61afef",
    heatmap_empty="#21252b",
    heatmap_l1="#2d4a30",
    heatmap_l2="#4a7a40",
    heatmap_l3="#78a55c",
    heatmap_l4="#98c379",
    icon_color="#5c6370",
    progress_bg="#3e4451",
)

# ────────────────────────────────────────────────────────────────────
# Theme registry
# ────────────────────────────────────────────────────────────────────

_THEMES: dict[str, Theme] = {
    "github_dark": GITHUB_DARK,
    "github_light": GITHUB_LIGHT,
    "dracula": DRACULA,
    "nord": NORD,
    "catppuccin_mocha": CATPPUCCIN_MOCHA,
    "catppuccin_latte": CATPPUCCIN_LATTE,
    "tokyo_night": TOKYO_NIGHT,
    "gruvbox_dark": GRUVBOX_DARK,
    "one_dark": ONE_DARK,
}


def get_theme(name: str) -> Theme:
    """Get a built-in theme by name (case-insensitive).

    Args:
        name: Theme name (e.g., 'github_dark', 'dracula').

    Returns:
        The matching Theme object.

    Raises:
        ValueError: If the theme name is not recognized.
    """
    key = name.lower().strip()
    theme = _THEMES.get(key)
    if theme is None:
        available = ", ".join(sorted(_THEMES.keys()))
        raise ValueError(
            f"Unknown theme '{name}'. Available themes: {available}"
        )
    return theme


def list_themes() -> list[str]:
    """Return a sorted list of all built-in theme names."""
    return sorted(_THEMES.keys())


def load_custom_theme(path: str) -> Theme:
    """Load a custom theme from a JSON file.

    The JSON file should contain a flat object with theme field names as keys
    and color hex strings as values. The 'name' field is required.

    Example JSON:
    ```json
    {
        "name": "my_theme",
        "bg_color": "#1a1a2e",
        "title_color": "#e94560",
        "text_color": "#eaeaea",
        ...
    }
    ```

    Args:
        path: Path to the JSON theme file.

    Returns:
        A Theme object constructed from the JSON data.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If required fields are missing or invalid.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Theme file not found: {path}")

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Theme JSON must be a flat object")

    if "name" not in data:
        raise ValueError("Theme JSON must include a 'name' field")

    # Handle bg_gradient as a list → tuple
    if "bg_gradient" in data:
        grad = data["bg_gradient"]
        if isinstance(grad, list) and len(grad) == 2:
            data["bg_gradient"] = tuple(grad)
        elif grad is None:
            data["bg_gradient"] = None
        else:
            raise ValueError("bg_gradient must be a list of two hex color strings or null")

    # Construct the theme, filtering out unknown fields
    valid_fields = {f.name for f in Theme.__dataclass_fields__.values()}
    filtered = {k: v for k, v in data.items() if k in valid_fields}

    try:
        return Theme(**filtered)
    except TypeError as e:
        raise ValueError(f"Invalid theme data: {e}") from e
