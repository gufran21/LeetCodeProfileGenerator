"""Tests for utility modules."""


from leetcode_profile_generator.utils.colors import (
    darken,
    heatmap_color,
    hex_to_rgb,
    hex_with_alpha,
    interpolate,
    lighten,
    rgb_to_hex,
    with_opacity,
)
from leetcode_profile_generator.utils.date import get_month_labels, get_week_grid, timestamp_to_date
from leetcode_profile_generator.utils.fonts import measure_text, measure_text_mono, truncate_text
from leetcode_profile_generator.utils.icons import render_icon
from leetcode_profile_generator.utils.math import (
    Point,
    catmull_rom_to_bezier,
    clamp,
    format_number,
    nice_axis_bounds,
    points_to_svg_path,
    scale_value,
)


class TestColors:
    def test_hex_to_rgb(self):
        assert hex_to_rgb("#ff5500") == (255, 85, 0)

    def test_hex_to_rgb_short(self):
        assert hex_to_rgb("#f50") == (255, 85, 0)

    def test_rgb_to_hex(self):
        assert rgb_to_hex(255, 85, 0) == "#ff5500"

    def test_rgb_to_hex_clamped(self):
        assert rgb_to_hex(300, -10, 128) == "#ff0080"

    def test_lighten(self):
        result = lighten("#000000", 0.5)
        r, g, b = hex_to_rgb(result)
        assert r > 0 and g > 0 and b > 0

    def test_darken(self):
        result = darken("#ffffff", 0.5)
        r, g, b = hex_to_rgb(result)
        assert r < 255 and g < 255 and b < 255

    def test_with_opacity(self):
        result = with_opacity("#ff0000", 0.5)
        assert result == "rgba(255,0,0,0.50)"

    def test_hex_with_alpha(self):
        result = hex_with_alpha("#ff0000", 0.5)
        assert result.startswith("#ff0000")
        assert len(result) == 9

    def test_interpolate_start(self):
        assert interpolate("#000000", "#ffffff", 0.0) == "#000000"

    def test_interpolate_end(self):
        assert interpolate("#000000", "#ffffff", 1.0) == "#ffffff"

    def test_heatmap_color_zero(self):
        levels = ["#empty", "#l1", "#l2", "#l3", "#l4"]
        assert heatmap_color(0, levels) == "#empty"

    def test_heatmap_color_high(self):
        levels = ["#empty", "#l1", "#l2", "#l3", "#l4"]
        assert heatmap_color(15, levels) == "#l4"


class TestFonts:
    def test_measure_text_returns_positive(self):
        width = measure_text("Hello World", 14)
        assert width > 0

    def test_measure_text_bold_wider(self):
        normal = measure_text("Hello", 14)
        bold = measure_text("Hello", 14, weight="bold")
        assert bold > normal

    def test_measure_text_mono(self):
        width = measure_text_mono("Hello", 14)
        assert width > 0

    def test_truncate_text_fits(self):
        result = truncate_text("Hi", 1000, 14)
        assert result == "Hi"

    def test_truncate_text_truncates(self):
        result = truncate_text("This is a very long string that should be truncated", 100, 14)
        assert result.endswith("…")
        assert len(result) < 52


class TestDate:
    def test_timestamp_to_date(self):
        d = timestamp_to_date(1718524800)
        assert d.year >= 2024

    def test_timestamp_to_date_string(self):
        d = timestamp_to_date("1718524800")
        assert d.year >= 2024

    def test_get_week_grid_shape(self):
        grid = get_week_grid()
        assert len(grid) == 53
        for week in grid:
            assert len(week) == 7

    def test_get_month_labels(self):
        grid = get_week_grid()
        labels = get_month_labels(grid)
        assert len(labels) > 0
        for col_idx, name in labels:
            assert isinstance(col_idx, int)
            assert isinstance(name, str)


class TestMath:
    def test_scale_value(self):
        assert scale_value(50, 0, 100, 0, 200) == 100.0

    def test_scale_value_equal_range(self):
        result = scale_value(50, 50, 50, 0, 200)
        assert result == 100.0  # midpoint

    def test_format_number_int(self):
        assert format_number(42156) == "42,156"

    def test_format_number_float(self):
        assert format_number(1847.0) == "1,847"

    def test_clamp(self):
        assert clamp(5, 0, 10) == 5
        assert clamp(-5, 0, 10) == 0
        assert clamp(15, 0, 10) == 10

    def test_nice_axis_bounds(self):
        nice_min, nice_max, step = nice_axis_bounds(1500, 2100)
        assert nice_min <= 1500
        assert nice_max >= 2100
        assert step > 0

    def test_catmull_rom_empty(self):
        assert catmull_rom_to_bezier([]) == []

    def test_catmull_rom_single(self):
        assert catmull_rom_to_bezier([Point(0, 0)]) == []

    def test_catmull_rom_two_points(self):
        segments = catmull_rom_to_bezier([Point(0, 0), Point(100, 50)])
        assert len(segments) == 1

    def test_points_to_svg_path(self):
        points = [Point(0, 100), Point(50, 50), Point(100, 75)]
        path = points_to_svg_path(points)
        assert path.startswith("M ")
        assert "C " in path


class TestIcons:
    def test_render_known_icon(self):
        svg = render_icon("trophy", 10, 20, 16, "#ffffff")
        assert "<g" in svg
        assert "<path" in svg

    def test_render_unknown_icon(self):
        svg = render_icon("nonexistent_icon", 10, 20, 16, "#ffffff")
        assert svg == ""
