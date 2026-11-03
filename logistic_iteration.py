#!/usr/bin/env python3
"""Generate a PNG plot of a fixed-parameter logistic-map orbit."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def generate_plot(
    r: float,
    iterations_per_step: int,
    initial_value: float,
    output_path: Path,
    show_x_axis: bool = True,
    width: int = 800,
    height: int = 600,
) -> None:
    """Generate and save every value from one logistic-map orbit."""
    if not math.isfinite(r) or not 0 <= r <= 4:
        raise ValueError("r must be a finite number between 0 and 4")
    if iterations_per_step <= 0:
        raise ValueError("iterations per step must be a positive integer")
    if not math.isfinite(initial_value) or not 0 <= initial_value <= 1:
        raise ValueError("initial value must be a finite number between 0 and 1")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive integers")

    iterations = width * iterations_per_step
    states: list[float] = []
    positions: list[float] = []
    state = initial_value
    for iteration in range(1, iterations + 1):
        state = r * state * (1.0 - state)
        positions.append(iteration / iterations_per_step)
        states.append(state)

    figure, axis = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    axis.plot(positions, states, ",k", rasterized=True)
    axis.set_xlim(0, width)
    axis.set_ylim(0, 1)
    axis.set_xlabel(f"Iterations ({iterations_per_step} per x-axis unit)")
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
        description="Plot a logistic-map orbit for a fixed growth factor r."
    )
    parser.add_argument("r", type=float, help="growth factor (0 to 4)")
    parser.add_argument(
        "--iterations-per-step",
        type=int,
        default=100,
        help="iterations per x-axis unit (default: 100)",
    )
    parser.add_argument(
        "--initial-value",
        type=float,
        default=0.5,
        help="initial population x0 (0 to 1; default: 0.5)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("logistic_iteration.png"),
        help="output PNG path (default: logistic_iteration.png)",
    )
    parser.add_argument(
        "--x-axis",
        choices=("show", "hide"),
        default="hide",
        help="show or hide the x-axis (default: hide)",
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
        generate_plot(
            arguments.r,
            arguments.iterations_per_step,
            arguments.initial_value,
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
