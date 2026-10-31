#!/usr/bin/env python3
"""Generate a PNG bifurcation diagram for the logistic map."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


R_MIN = 0.0
R_MAX = 4.0
R_SAMPLES = 2400
TRANSIENT_ITERATIONS = 1000
PLOTTED_ITERATIONS = 300


def _format_tick_values(values: list[float]) -> list[str]:
    """Keep neighboring axis labels distinct for narrow parameter ranges."""
    spacings = [
        abs(right - left)
        for left, right in zip(values, values[1:])
        if right != left
    ]
    if not spacings:
        return [f"{value:.3g}" for value in values]

    magnitude = max(1.0, *(abs(value) for value in values))
    precision = min(15, max(3, math.ceil(math.log10(magnitude / min(spacings))) + 1))
    return [f"{value:.{precision}g}" for value in values]


def generate_diagram(
    r_start: float,
    r_end: float,
    stretching_factor: float,
    output_path: Path,
    show_x_axis: bool = True,
    width: int = 800,
    height: int = 600,
) -> None:
    """Generate and save the logistic-map bifurcation diagram."""
    if not math.isfinite(r_start) or not math.isfinite(r_end):
        raise ValueError("r-start and r-end must be finite numbers")
    if not R_MIN <= r_start < r_end <= R_MAX:
        raise ValueError("r-start and r-end must satisfy 0 <= r-start < r-end <= 4")
    if not math.isfinite(stretching_factor) or stretching_factor <= 0:
        raise ValueError("stretching factor must be a finite positive number")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive integers")

    x_positions = np.linspace(0.0, 1.0, R_SAMPLES)
    r_values = r_start + (r_end - r_start) * np.power(
        x_positions, 1.0 / stretching_factor
    )
    states = np.full(R_SAMPLES, 0.5)

    for _ in range(TRANSIENT_ITERATIONS):
        states = r_values * states * (1.0 - states)

    plotted_states = np.empty((PLOTTED_ITERATIONS, R_SAMPLES))
    for iteration in range(PLOTTED_ITERATIONS):
        states = r_values * states * (1.0 - states)
        plotted_states[iteration] = states

    figure, axis = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    axis.plot(
        np.tile(x_positions, PLOTTED_ITERATIONS),
        plotted_states.ravel(),
        ",k",
        rasterized=True,
    )
    tick_positions = [index / 8 for index in range(9)]
    tick_values = [
        r_start + (r_end - r_start) * position ** (1.0 / stretching_factor)
        for position in tick_positions
    ]
    axis.set_xticks(tick_positions, _format_tick_values(tick_values))
    axis.set_xlim(0.0, 1.0)
    axis.set_ylim(0.0, 1.0)
    axis.set_xlabel("Growth factor r")
    axis.xaxis.set_visible(show_x_axis)
    axis.yaxis.set_visible(False)
    for spine in ("left", "right", "top"):
        axis.spines[spine].set_visible(False)
    axis.spines["bottom"].set_visible(show_x_axis)
    figure.tight_layout()
    figure.savefig(output_path, dpi=100)
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a logistic-map bifurcation diagram. A stretching factor of 1 "
            "is linear; larger values allocate more horizontal space near r-end."
        )
    )
    parser.add_argument("r_start", type=float, help="first growth factor (0 to 4)")
    parser.add_argument(
        "r_end",
        type=float,
        help="last growth factor (greater than r-start, up to 4)",
    )
    parser.add_argument(
        "stretching_factor",
        type=float,
        help="positive power-law stretching factor (1 is linear; greater than 1 stretches toward r-end)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("logistic_bifurcation.png"),
        help="output PNG path (default: logistic_bifurcation.png)",
    )
    parser.add_argument(
        "--x-axis",
        choices=("show", "hide"),
        default="show",
        help="show or hide the x-axis (default: show)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=800,
        help="output image width in pixels (default: 800)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=600,
        help="output image height in pixels (default: 600)",
    )
    arguments = parser.parse_args()

    try:
        generate_diagram(
            arguments.r_start,
            arguments.r_end,
            arguments.stretching_factor,
            arguments.output,
            arguments.x_axis == "show",
            arguments.width,
            arguments.height,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
