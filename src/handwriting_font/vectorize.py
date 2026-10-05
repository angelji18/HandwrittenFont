"""Convert extracted glyph PNGs into black SVG outlines."""

import argparse
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image
import vtracer


def prepare_image(image, threshold):
    """Put transparency on white, then separate dark ink from the background."""
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, "white")
    grayscale = Image.alpha_composite(background, rgba).convert("L")
    return grayscale.point(lambda pixel: 0 if pixel < threshold else 255)


def trace_glyph(source_path, prepared_path, svg_path, threshold):
    """Save the black-and-white pixels and trace their outlines into an SVG."""
    with Image.open(source_path) as image:
        prepared = prepare_image(image, threshold)

    prepared_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    prepared.save(prepared_path)

    width, height = prepared.size
    if prepared.getextrema() == (255, 255):
        # A space has dimensions but no ink to trace.
        root = ElementTree.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(width),
            "height": str(height),
        })
    else:
        vtracer.convert_image_to_svg_py(
            str(prepared_path),
            str(svg_path),
            colormode="binary",
            mode="spline",
            filter_speckle=2,
        )
        root = ElementTree.parse(svg_path).getroot()

    # The viewBox lets a viewer scale the outline to different display sizes.
    root.set("viewBox", f"0 0 {width} {height}")
    ElementTree.register_namespace("", "http://www.w3.org/2000/svg")
    ElementTree.ElementTree(root).write(svg_path, encoding="utf-8", xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description="Trace glyph PNGs into SVG outlines.")
    parser.add_argument("--input", type=Path, default=Path("build/glyphs"))
    parser.add_argument("--prepared", type=Path, default=Path("build/monochrome"))
    parser.add_argument("--output", type=Path, default=Path("build/svg"))
    parser.add_argument("--threshold", type=int, default=180)
    args = parser.parse_args()
    if not 1 <= args.threshold <= 255:
        parser.error("--threshold must be between 1 and 255")

    # Only character folders are traced; colored underlines remain PNG assets.
    sources = []
    for section in ("thin", "bold", "punctuation"):
        sources.extend(sorted((args.input / section).rglob("*.png")))
    if not sources:
        parser.error("No glyph PNGs found. Run python -m handwriting_font first.")

    for source in sources:
        relative_path = source.relative_to(args.input)
        trace_glyph(
            source,
            args.prepared / relative_path,
            (args.output / relative_path).with_suffix(".svg"),
            args.threshold,
        )
    print(f"Saved {len(sources)} prepared PNGs to {args.prepared}")
    print(f"Saved {len(sources)} SVGs to {args.output}")


if __name__ == "__main__":
    main()
