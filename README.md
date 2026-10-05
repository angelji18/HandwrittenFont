# Handwriting Font

A small Python project that crops handwritten characters and colored underline
strokes from a PNG using Pillow. Character labels and crop positions are
configured manually; the code does not recognize characters or detect styles.

## Setup

Requires Python 3.9 or newer. Run from the project directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Extract

```sh
source .venv/bin/activate
python -m handwriting_font
```

Reads `assets/sources/Font.png` using `config/grid.json` and saves to
`build/glyphs/`. The current configuration produces:

- 63 thin glyphs: uppercase, lowercase, digits, and a blank space.
- 53 bold glyphs: uppercase, lowercase, and a blank space.
- 40 punctuation and symbol glyphs.
- 8 colored underline images.

Uppercase and lowercase use separate folders. Symbols use Unicode filenames
such as `U+002F.png` for `/`. Underlines are saved in `underlines/`.
Images keep their original pixels and backgrounds. Rerunning overwrites
matching files. Generated output under `build/` is ignored by Git.

## Configuration

Edit `config/grid.json` when the source image or layout changes. It specifies
character rows, grid positions, cell sizes, optional crop overrides, blank
spaces, and named underline rectangles. Rectangles use
`[left, top, right, bottom]` in pixels, with right and bottom excluded.
The current coordinates are for the included 2500 x 3000 PNG.

Use `--image`, `--config`, and `--output` to select different paths.

Vector conversion and font generation are not implemented yet.
