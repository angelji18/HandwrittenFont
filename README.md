# Handwriting Font

A small Python project that crops handwritten characters and colored underline
strokes from a PNG using Pillow. Character labels and crop positions are
configured manually; the code does not recognize characters or detect styles.

## Setup

Requires Python 3.10 or newer. Run from the project directory (Python 3.12 shown):

```sh
python3.12 -m venv .venv
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

## Trace SVG outlines

After extracting glyphs, run:

```sh
python -m handwriting_font.vectorize
```

Pillow separates dark ink from the light background; [VTracer](https://pypi.org/project/vtracer/0.6.11/)
traces the black shapes into curves. Outputs are `build/monochrome/` (prepared
PNGs) and `build/svg/` (156 SVGs), with the same folder structure as the glyphs.
Spaces produce empty SVGs. Colored underlines remain PNG assets.

Open an SVG in a browser to inspect it. Use `--threshold 200` to include more
faint ink, or a lower value to include less (default: 180). Tracing approximates
the handwriting, so review outlines before building the font.

## Build the TTF

After tracing the SVGs, run:

```sh
python -m handwriting_font.build_font
python -m handwriting_font.build_font --style bold
```

Creates `build/fonts/MyHandwriting-Regular.ttf` and `MyHandwriting-Bold.ttf`,
each with 103 characters. Bold uses the thicker letters and shares the thin
digits and punctuation. Install both TTFs, then select **My Handwriting** and
choose Regular or Bold in an application that supports installed fonts.

`config/font.json` controls the font name, scale, spacing, and baseline offsets.
`side_bearing` sets the margin on each side of a character; `space_width` sets word spacing.
Positive offsets place strokes below the baseline; negative offsets raise
them. [fontTools](https://github.com/fonttools/fonttools) converts SVG curves
to TrueType curves and packages the character mappings and font information.
Both styles use simple spacing with no kerning (adjustments between pairs
of letters). Colored underlines remain separate image assets.

## From handwriting to a font

```text
PNG glyphs → trace outlines → SVG shapes → add character mapping and spacing → TTF font
```

- **PNG (Portable Network Graphics):** an image made of pixels, like our cropped letters.
- **SVG (Scalable Vector Graphics):** lines and curves describing each letter's shape, so it scales smoothly.
- **TTF (TrueType Font):** a font containing those outlines, character mappings, and spacing, so applications can use them when you type.

PNG cropping, SVG conversion, and Regular/Bold TTFs are complete. WOFF2 is not implemented yet.
