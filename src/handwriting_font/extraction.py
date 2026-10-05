"""Crop configured grid cells and create blank spaces with Pillow."""

from PIL import Image

def extract_glyphs(image, rows, cell_width, cell_height, grid_left=0, grid_top=0):
    """Return a dictionary mapping characters to their grid crops."""
    glyphs = {}

    for row_index, characters in enumerate(rows):
        for column_index, character in enumerate(characters):
            left = grid_left + column_index * cell_width
            top = grid_top + row_index * cell_height
            right = left + cell_width
            bottom = top + cell_height

            glyphs[character] = image.crop((left, top, right, bottom))

    return glyphs


def extract_section(image, section):
    """Extract one alphabet or punctuation block from its configuration."""
    glyphs = extract_glyphs(
        image,
        rows=section["rows"],
        cell_width=section["cell_width"],
        cell_height=section["cell_height"],
        grid_left=section["grid_left"],
        grid_top=section["grid_top"],
    )
    # Some handwritten strokes extend beyond their regular cells.
    for character, box in section.get("crop_overrides", {}).items():
        glyphs[character] = image.crop(tuple(box))
    if section.get("include_space", False):
        size = (section["cell_width"], section["cell_height"])
        glyphs[" "] = Image.new(image.mode, size, "white")
    return glyphs
