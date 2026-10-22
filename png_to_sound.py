#!/usr/bin/env python3
"""Convert a PNG spectrogram image into a mono WAV file; install Pillow to run."""

from __future__ import annotations

import argparse
import math
import struct
import wave
from collections import Counter
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def image_to_samples(
    image_path: Path,
    minimum_frequency: float,
    maximum_frequency: float,
    duration: float,
    sample_rate: int,
) -> list[int]:
    """Synthesize a mono, 16-bit PCM signal from the non-background pixels."""
    if not math.isfinite(minimum_frequency) or minimum_frequency <= 0:
        raise ValueError("minimum frequency must be a finite positive number")
    if not math.isfinite(maximum_frequency) or maximum_frequency <= 0:
        raise ValueError("maximum frequency must be a finite positive number")
    if maximum_frequency < minimum_frequency:
        raise ValueError("maximum frequency must be greater than or equal to minimum frequency")
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("duration must be a finite positive number")
    if sample_rate <= 0:
        raise ValueError("sample rate must be a positive integer")
    if maximum_frequency > sample_rate / 2:
        raise ValueError("maximum frequency must not exceed the sample rate's Nyquist frequency")

    with Image.open(image_path) as source:
        if source.format != "PNG":
            raise ValueError("input image must be a PNG file")
        rgba_image = source.convert("RGBA")
        width, height = rgba_image.size
        pixels = list(rgba_image.getdata())

    if width == 0 or height == 0:
        raise ValueError("input image must not be empty")

    total_frames = round(duration * sample_rate)
    if total_frames < 1:
        raise ValueError("duration is too short to produce a sample at this sample rate")

    background = Counter(pixels).most_common(1)[0][0]
    samples = [0.0] * total_frames

    for y in range(height):
        if height == 1:
            frequency = (minimum_frequency + maximum_frequency) / 2
        else:
            frequency = maximum_frequency - y * (
                (maximum_frequency - minimum_frequency) / (height - 1)
            )

        row_offset = y * width
        x = 0
        while x < width:
            pixel = pixels[row_offset + x]
            if pixel == background or pixel[3] == 0:
                x += 1
                continue

            run_start = x
            x += 1
            while x < width:
                pixel = pixels[row_offset + x]
                if pixel == background or pixel[3] == 0:
                    break
                x += 1

            frame_start = run_start * total_frames // width
            frame_end = x * total_frames // width
            if frame_start == frame_end:
                continue

            phase_step = 2 * math.pi * frequency / sample_rate
            frame = frame_start
            while frame < frame_end:
                block_end = min(frame + 4096, frame_end)
                phase = phase_step * frame
                sine = math.sin(phase)
                cosine = math.cos(phase)
                step_sine = math.sin(phase_step)
                step_cosine = math.cos(phase_step)

                while frame < block_end:
                    samples[frame] += sine
                    sine, cosine = (
                        sine * step_cosine + cosine * step_sine,
                        cosine * step_cosine - sine * step_sine,
                    )
                    frame += 1

    peak = max((abs(sample) for sample in samples), default=0.0)
    if peak == 0:
        return [0] * total_frames

    scale = 32767 / peak
    return [max(-32768, min(32767, round(sample * scale))) for sample in samples]


def write_wav(output_path: Path, samples: list[int], sample_rate: int) -> None:
    with wave.open(str(output_path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a PNG spectrogram into a normalized mono WAV file."
    )
    parser.add_argument("input_png", type=Path, help="lossless PNG image to convert")
    parser.add_argument("output_wav", type=Path, help="path for the output WAV file")
    parser.add_argument("minimum_frequency", type=float, help="frequency for the bottom row, in Hz")
    parser.add_argument("maximum_frequency", type=float, help="frequency for the top row, in Hz")
    parser.add_argument("duration", type=float, help="total sound duration, in seconds")
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=44100,
        help="output sample rate in Hz (default: 44100)",
    )
    arguments = parser.parse_args()

    try:
        samples = image_to_samples(
            arguments.input_png,
            arguments.minimum_frequency,
            arguments.maximum_frequency,
            arguments.duration,
            arguments.sample_rate,
        )
        write_wav(arguments.output_wav, samples, arguments.sample_rate)
    except (OSError, UnidentifiedImageError, ValueError) as error:
        parser.error(str(error))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
