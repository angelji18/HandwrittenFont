"""Build a simple TrueType font from the traced character SVGs."""

import argparse
import json
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import SVGPath

from handwriting_font.__main__ import glyph_path


def svg_to_glyph(path, character, settings):
    """Scale an outline, position it on the baseline, and set its spacing."""
    svg = SVGPath(str(path))
    # VTracer writes translate(x, y); fontTools reads the equivalent matrix.
    for element in svg.root.iter():
        transform = element.get("transform", "")
        if transform.startswith("translate("):
            x, y = transform[10:-1].replace(",", " ").split()
            element.set("transform", f"matrix(1,0,0,1,{x},{y})")
    bounds_pen = BoundsPen(None)
    svg.draw(bounds_pen)
    pen = TTGlyphPen(None)
    if bounds_pen.bounds is None:
        return pen.glyph(), (settings["space_width"], 0)

    left, _, _, bottom = bounds_pen.bounds
    scale = settings["scale"]
    margin = settings["side_bearing"]
    offset = settings["baseline_offsets"].get(character, 0)
    # SVG y increases downward; font y increases upward from the baseline.
    svg.transform = (scale, 0, 0, -scale, margin - left * scale, (bottom - offset) * scale)
    # TrueType uses quadratic curves; SVG tracing produces cubic curves.
    svg.draw(Cu2QuPen(pen, max_err=1))
    # Measure the final rounded outline so spacing matches the stored points.
    glyph = pen.glyph()
    glyph.recalcBounds(None)
    return glyph, (glyph.xMax + margin, glyph.xMin)


def missing_glyph():
    """Draw the box displayed when a character is missing from the font."""
    pen = TTGlyphPen(None)
    for points in (
        [(50, 0), (50, 700), (550, 700), (550, 0)],
        [(100, 50), (500, 50), (500, 650), (100, 650)],
    ):
        pen.moveTo(points[0])
        for point in points[1:]:
            pen.lineTo(point)
        pen.closePath()
    return pen.glyph()


def build_font(svg_directory, sections, settings, output_path, style="Regular"):
    """Map configured characters to glyphs and package the required TTF tables."""
    glyphs = {".notdef": missing_glyph()}
    metrics = {".notdef": (600, 50)}
    character_map = {}
    for section in sections:
        characters = "".join(section["rows"])
        if section.get("include_space", False):
            characters += " "
        for character in characters:
            if ord(character) in character_map:
                raise ValueError(f"Duplicate character in font configuration: {character!r}")
            path = glyph_path(svg_directory / section["name"], character).with_suffix(".svg")
            if not path.is_file():
                raise FileNotFoundError(f"Missing {path}. Run python -m handwriting_font.vectorize first.")
            name = f"uni{ord(character):04X}"
            glyphs[name], metrics[name] = svg_to_glyph(path, character, settings)
            character_map[ord(character)] = name

    font = FontBuilder(settings["units_per_em"], isTTF=True)
    font.setupGlyphOrder(list(glyphs))
    font.setupCharacterMap(character_map)
    font.setupGlyf(glyphs)
    font.setupHorizontalMetrics(metrics)
    ascent, descent = settings["ascent"], settings["descent"]
    font.setupHorizontalHeader(ascent=ascent, descent=-descent)
    family = settings["family_name"]
    is_bold = style == "Bold"
    font.setupNameTable({
        "familyName": family,
        "styleName": style,
        "uniqueFontIdentifier": f"{family}-{style}-0.1",
        "fullName": f"{family} {style}",
        "psName": f"{family.replace(' ', '')}-{style}",
        "version": "Version 0.1",
    })
    font.setupOS2(
        sTypoAscender=ascent, sTypoDescender=-descent, sTypoLineGap=0,
        usWinAscent=ascent, usWinDescent=descent,
        usWeightClass=700 if is_bold else 400,
        fsSelection=0x20 if is_bold else 0x40,
    )
    font.font["head"].macStyle = 1 if is_bold else 0
    font.setupPost()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    font.save(output_path)
    print(f"Saved {output_path} with {len(character_map)} characters.")


def main():
    parser = argparse.ArgumentParser(description="Build a Regular or Bold handwriting TTF.")
    parser.add_argument("--style", choices=("regular", "bold"), default="regular")
    parser.add_argument("--input", type=Path, default=Path("build/svg"))
    parser.add_argument("--grid", type=Path, default=Path("config/grid.json"))
    parser.add_argument("--settings", type=Path, default=Path("config/font.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with args.grid.open(encoding="utf-8") as file:
        grid = json.load(file)
    with args.settings.open(encoding="utf-8") as file:
        settings = json.load(file)
    by_name = {section["name"]: section for section in grid["sections"]}
    letter_section = "bold" if args.style == "bold" else "thin"
    for name in (letter_section, "thin", "punctuation"):
        if name not in by_name:
            parser.error(f"Grid configuration is missing the {name} section.")
    sections = [by_name[letter_section], by_name["punctuation"]]
    if args.style == "bold":
        # The sheet has no bold digits, so reuse only the thin digit outlines.
        digits = "".join(character for row in by_name["thin"]["rows"]
                         for character in row if character in "0123456789")
        sections.append({"name": "thin", "rows": [digits]})
    style = args.style.title()
    output = args.output or Path(f"build/fonts/MyHandwriting-{style}.ttf")
    build_font(args.input, sections, settings, output, style)


if __name__ == "__main__":
    main()
