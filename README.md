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

The sample rate defaults to 44100 Hz. Use `--sample-rate` to change it.
`--amplitude-mode` controls how the output volume is normalized:

- `global` (default) normalizes the entire sound together. Relative loudness
  between image columns is preserved, so columns with more overlapping pixels
  can sound louder.
- `column` normalizes each time slice (image column) independently. This makes
  active columns similarly loud, but reduces volume differences between them.

For example, add `--amplitude-mode column` to the conversion command to use
per-column normalization.

The converter uses a minimum 10 ms fade at the start and end of each sound
segment to reduce clicks. It warns when this fade is longer than one-fifth of
the time represented by an image column. In that case, neighboring sounds may
overlap more than intended. Increase the sound duration (the final positional
argument) or use an image with fewer columns. For example, if the image comes
from the bifurcation program, reduce its `--width`. A narrower image has less
horizontal detail.



## Example 1: Melody

Convert [`melody.png`](./melody.png) from this repository into a WAV file. Do you know the song?

```sh
python3 margortceps.py melody.png melody.wav 261.63 440 16.2338
```


## Example 2: Logistic map bifurcation diagrams

[`logistic_bifurcation.py`](./logistic_bifurcation.py) is a separate example
program that generates an image; its output can then be used as input to
Margortceps. It is not required by the converter.

Install its dependencies:

```sh
python3 -m pip install matplotlib numpy
```

Generate a diagram and convert it to sound:

```sh
python3 logistic_bifurcation.py 1.5 4 3 --output bifurcation.png
python3 margortceps.py bifurcation.png bifurcation.wav 200 2000 40
```

The diagram command takes the starting and ending logistic-map growth factors
(`r-start` and `r-end`, between 0 and 4) and a positive stretching factor.
Stretching factor `1` spaces the range linearly; larger values give more
horizontal space near `r-end`. If `r-start` is greater than `r-end`, the growth
factor decreases from the start value to the end value.

The output path defaults to
`logistic_bifurcation.png`, and the default image resolution is 800x600 pixels. The x-axis is hidden by default; use `--x-axis show` to display it. Choose another resolution with `--width` and `--height`, for example:

```sh
python3 logistic_bifurcation.py 1.5 4 3 --width 1200 --height 800 --x-axis show
```

The diagram plots 300 iterations per x-axis pixel after an initial transient
by default. Change that density with `--iterations-per-pixel`:

```sh
python3 logistic_bifurcation.py 1.5 4 3 --iterations-per-pixel 500
```

The bifurcation diagram has many interesting "regions". Try this for a complete different sound:

```sh
python3 logistic_bifurcation.py 3.82842635 3.8284266 0.15 --output bifurcation.png
python3 margortceps.py bifurcation.png bifurcation.wav 200 1000 60
```

This one travels from the period regime into intermittency and then chaos:

```sh
python3 logistic_bifurcation.py 3.828425 3.82000 0.1 --iterations-per-pixel 20 --width 1500 --output bifurcation.png
python3 margortceps.py bifurcation.png bifurcation.wav 200 1000 80
```
