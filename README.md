# Margortceps

Margortceps converts a PNG image into a mono WAV file. Each image column maps
to a point in time from left to right, and each row maps to a frequency from
the minimum frequency at the bottom to the maximum frequency at the top.
Non-background pixels contribute sound. In short, it does the opposite of what a spectrogram does.

## Convert an image to sound

Install the converter dependency:

```sh
python3 -m pip install Pillow
```

Run the converter with an input PNG, output WAV, frequency range in Hz, and
duration in seconds:

```sh
python3 margortceps.py input.png output.wav 200 2000 10
```

The converter uses a minimum 10 ms fade at the start and end of each sound
segment to reduce clicks. It warns when this fade is longer than one-fifth of
the time represented by an image column. In that case, neighboring sounds may
overlap more than intended. Increase the sound duration (the final positional
argument) or use an image with fewer columns. For example, if the image comes
from the bifurcation program, reduce its `--width`. A narrower image has less
horizontal detail.

The sample rate defaults to 44100 Hz. Use `--sample-rate` to change it.
`--amplitude-mode` controls how the output volume is normalized:

- `global` (default) normalizes the entire sound together. Relative loudness
  between image columns is preserved, so columns with more overlapping pixels
  can sound louder.
- `column` normalizes each time slice (image column) independently. This makes
  active columns similarly loud, but reduces volume differences between them.

For example, add `--amplitude-mode column` to the conversion command to use
per-column normalization.

## Example: logistic-map bifurcation image

[`logistic_bifurcation.py`](./logistic_bifurcation.py) is a separate example
program that generates an image; its output can then be used as input to
Margortceps. It is not required by the converter.

Install its dependencies:

```sh
python3 -m pip install matplotlib numpy
```

Generate a diagram and convert it to sound:

```sh
python3 logistic_bifurcation.py 1.5 4 3 --output media/bifurcation.png
python3 margortceps.py media/bifurcation.png media/bifurcation.wav 200 2000 10
```

The diagram command takes the starting and ending logistic-map growth factors
(`r-start` and `r-end`, between 0 and 4) and a positive stretching factor.
Stretching factor `1` spaces the range linearly; larger values give more
horizontal space near `r-end`. The output path defaults to
`logistic_bifurcation.png`, and the default image resolution is 800x600 pixels.
Choose another resolution with `--width` and `--height`, for example:

```sh
python3 logistic_bifurcation.py 1.5 4 3 --width 1200 --height 800
```

Use `--x-axis hide` to omit the x-axis.
