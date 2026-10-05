"""Run with python -m handwriting_font from the project directory."""

import argparse
import json
from pathlib import Path

from PIL import Image

from handwriting_font.extraction import extract_section


def glyph_path(output_directory, character):
    """Keep letter case separate and use safe filenames for punctuation."""
    if character == " ":
        return output_directory / "space.png"
    if character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return output_directory / "uppercase" / f"{character}.png"
    if character in "abcdefghijklmnopqrstuvwxyz":
        return output_directory / "lowercase" / f"{character}.png"
    if character in "0123456789":
        return output_directory / "digits" / f"{character}.png"
    return output_directory / "symbols" / f"U+{ord(character):04X}.png"


def save_glyphs(glyphs, directory):
    """Save each character using a filename suitable for the filesystem."""
    for character, glyph in glyphs.items():
        path = glyph_path(directory, character)
        path.parent.mkdir(parents=True, exist_ok=True)
        glyph.save(path)


def save_underlines(image, underlines, directory):
    """Crop named colored strokes and save them as separate PNGs."""
    if not underlines:
        return
    directory.mkdir(parents=True, exist_ok=True)
    for name, box in underlines.items():
        image.crop(tuple(box)).save(directory / f"{name}.png")
    print(f"Saved {len(underlines)} underline images to {directory}")


def main():
    parser = argparse.ArgumentParser(description="Crop glyph PNGs from configured grids.")
    parser.add_argument("--image", type=Path, default=Path("assets/sources/Font.png"))
    parser.add_argument("--config", type=Path, default=Path("config/grid.json"))
    parser.add_argument("--output", type=Path, default=Path("build/glyphs"))
    args = parser.parse_args()

    with args.config.open(encoding="utf-8") as config_file:
        config = json.load(config_file)

    total = 0
    with Image.open(args.image) as image:
        for section in config["sections"]:
            glyphs = extract_section(image, section)
            directory = args.output / section["name"]
            save_glyphs(glyphs, directory)
            total += len(glyphs)
            print(f"Saved {len(glyphs)} glyphs to {directory}")
        save_underlines(image, config.get("underlines", {}), args.output / "underlines")
    print(f"Saved {total} glyphs in total.")


if __name__ == "__main__":
    main()
