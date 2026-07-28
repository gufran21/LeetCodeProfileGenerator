"""Math utilities for SVG chart rendering.

Includes Catmull-Rom to cubic Bézier conversion for smooth rating curves,
linear value scaling, and number formatting.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Point:
    """A 2D point."""

    x: float
    y: float


@dataclass
class BezierSegment:
    """A cubic Bézier curve segment defined by start, two control points, and end."""

    start: Point
    cp1: Point
    cp2: Point
    end: Point

    def to_svg(self) -> str:
        """Convert to SVG path 'C' command (control points + end point only)."""
        return f"C {self.cp1.x:.1f},{self.cp1.y:.1f} {self.cp2.x:.1f},{self.cp2.y:.1f} {self.end.x:.1f},{self.end.y:.1f}"


def catmull_rom_to_bezier(
    points: list[Point],
    tension: float = 0.5,
) -> list[BezierSegment]:
    """Convert a series of points to smooth cubic Bézier segments using Catmull-Rom interpolation.

    This creates the smooth curved line used in the rating history graph.
    Catmull-Rom splines pass through all data points while maintaining
    C1 continuity (smooth tangents).

    Args:
        points: List of data points to interpolate.
        tension: Tension parameter (0.0 = sharp, 0.5 = standard Catmull-Rom, 1.0 = very loose).

    Returns:
        List of BezierSegment objects that can be rendered as SVG path commands.
    """
    if len(points) < 2:
        return []

    segments: list[BezierSegment] = []
    n = len(points)

    for i in range(n - 1):
        # Get surrounding points (with clamping at boundaries)
        p0 = points[max(0, i - 1)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(n - 1, i + 2)]

        # Calculate control points
        d1x = (p2.x - p0.x) * tension / 3
        d1y = (p2.y - p0.y) * tension / 3
        d2x = (p3.x - p1.x) * tension / 3
        d2y = (p3.y - p1.y) * tension / 3

        cp1 = Point(p1.x + d1x, p1.y + d1y)
        cp2 = Point(p2.x - d2x, p2.y - d2y)

        segments.append(BezierSegment(start=p1, cp1=cp1, cp2=cp2, end=p2))

    return segments


def points_to_svg_path(points: list[Point], tension: float = 0.5) -> str:
    """Convert a list of points to a smooth SVG path string.

    Args:
        points: List of data points.
        tension: Catmull-Rom tension parameter.

    Returns:
        SVG path 'd' attribute value (e.g., 'M 0,100 C 10,90 20,80 30,70 C ...')
    """
    if not points:
        return ""

    if len(points) == 1:
        return f"M {points[0].x:.1f},{points[0].y:.1f}"

    segments = catmull_rom_to_bezier(points, tension)
    if not segments:
        return ""

    # Start with moveto
    path = f"M {segments[0].start.x:.1f},{segments[0].start.y:.1f}"

    # Add all curve segments
    for segment in segments:
        path += " " + segment.to_svg()

    return path


def points_to_area_path(
    points: list[Point],
    baseline_y: float,
    tension: float = 0.5,
) -> str:
    """Convert points to a closed SVG path for an area fill under the curve.

    Args:
        points: List of data points.
        baseline_y: The Y coordinate of the bottom of the area (chart baseline).
        tension: Catmull-Rom tension parameter.

    Returns:
        SVG path 'd' attribute for a closed area shape.
    """
    if len(points) < 2:
        return ""

    # Get the curve path
    line_path = points_to_svg_path(points, tension)

    # Close the area: line down to baseline, across, and back up
    first = points[0]
    last = points[-1]
    area_path = (
        f"{line_path} "
        f"L {last.x:.1f},{baseline_y:.1f} "
        f"L {first.x:.1f},{baseline_y:.1f} "
        f"Z"
    )

    return area_path


def scale_value(
    val: float,
    min_val: float,
    max_val: float,
    min_out: float,
    max_out: float,
) -> float:
    """Linearly map a value from one range to another.

    Args:
        val: Input value.
        min_val: Input range minimum.
        max_val: Input range maximum.
        min_out: Output range minimum.
        max_out: Output range maximum.

    Returns:
        The mapped value in the output range.
    """
    if max_val == min_val:
        return (min_out + max_out) / 2
    t = (val - min_val) / (max_val - min_val)
    return min_out + t * (max_out - min_out)


def format_number(n: int | float) -> str:
    """Format a number with comma separators.

    Args:
        n: The number to format.

    Returns:
        Formatted string like '42,156'.
    """
    if isinstance(n, float):
        if n == int(n):
            return f"{int(n):,}"
        return f"{n:,.1f}"
    return f"{n:,}"


def clamp(val: float, min_val: float, max_val: float) -> float:
    """Clamp a value to a range.

    Args:
        val: The value to clamp.
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.

    Returns:
        The clamped value.
    """
    return max(min_val, min(max_val, val))


def nice_axis_bounds(
    min_val: float, max_val: float, target_steps: int = 5
) -> tuple[float, float, float]:
    """Calculate nice axis bounds and step size for chart axes.

    Produces human-readable round numbers for axis labels.

    Args:
        min_val: Data minimum.
        max_val: Data maximum.
        target_steps: Desired number of axis steps.

    Returns:
        Tuple of (nice_min, nice_max, step_size).
    """
    if min_val == max_val:
        return (min_val - 100, max_val + 100, 50)

    data_range = max_val - min_val
    raw_step = data_range / target_steps

    # Find the magnitude
    magnitude = 1.0
    if raw_step > 0:
        while magnitude * 10 <= raw_step:
            magnitude *= 10
        while magnitude > raw_step:
            magnitude /= 10

    # Choose the nicest step
    nice_steps = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000]
    step = magnitude
    for ns in nice_steps:
        candidate = magnitude * ns
        if candidate >= raw_step:
            step = candidate
            break

    nice_min = (min_val // step) * step
    nice_max = ((max_val // step) + 1) * step

    # Add some padding
    if nice_min == min_val:
        nice_min -= step
    if nice_max == max_val:
        nice_max += step

    return (nice_min, nice_max, step)
