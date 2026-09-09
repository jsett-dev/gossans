"""Generate the site's raster image assets from the brand tokens.

Run from the repository root:

    python tools/make-assets.py

Writes favicon.ico, apple-touch-icon.png and og-image.png. The SVG favicon is
hand-written and is not touched by this script; these are the raster fallbacks
that older browsers and every social platform still require.

Regenerate whenever the brand colours change, and commit the output. The files
are small enough that keeping them in the repository is simpler than adding a
build step to a site that otherwise has none.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Brand tokens, matching the :root block in index.html.
INK = (20, 24, 26)          # --ink / dark ground
PAPER = (241, 242, 239)     # --paper
RUST = (163, 48, 31)        # --redline, the gossan itself
RUST_DARK = (221, 115, 97)  # --redline on a dark ground
MUTED = (179, 186, 184)     # --ink-2 dark
DRAFT = (107, 163, 198)     # --draft dark
RULE = (45, 53, 56)         # --rule dark

ROOT = Path(__file__).resolve().parent.parent

#: Tried in order. Arial is on every Windows machine; the rest cover macOS and
#: Linux so the script is not silently Windows-only.
FONT_CANDIDATES = {
    "bold": [
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "regular": [
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "mono": [
        "C:/Windows/Fonts/consola.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ],
}


def load(weight: str, size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES[weight]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    raise SystemExit(
        f"No {weight} font found. Add a path for this machine to "
        "FONT_CANDIDATES in tools/make-assets.py."
    )


def tracked(draw: ImageDraw.ImageDraw, xy, text: str, font, fill,
            spacing: float = 0.0) -> float:
    """Draw text with manual letter-spacing, which Pillow does not support."""
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + spacing
    return x


def make_icon(size: int, pad_ratio: float = 0.22) -> Image.Image:
    """The mark: a rust square on ink, the same shape as favicon.svg."""
    image = Image.new("RGBA", (size, size), INK + (255,))
    draw = ImageDraw.Draw(image)
    pad = round(size * pad_ratio)
    draw.rectangle([pad, pad, size - pad - 1, size - pad - 1], fill=RUST + (255,))
    return image


def write_favicon() -> None:
    sizes = [16, 32, 48, 64]
    base = make_icon(256)
    base.save(ROOT / "favicon.ico", format="ICO",
              sizes=[(s, s) for s in sizes])
    print("favicon.ico", sizes)


def write_apple_touch() -> None:
    # Apple composites onto white if the icon is transparent, and does not
    # round the corners itself on modern iOS, so ship it opaque and square.
    icon = make_icon(180, pad_ratio=0.26).convert("RGB")
    icon.save(ROOT / "apple-touch-icon.png", format="PNG")
    print("apple-touch-icon.png 180x180")


def write_og_image() -> None:
    width, height = 1200, 630
    image = Image.new("RGB", (width, height), INK)
    draw = ImageDraw.Draw(image)

    left = 88
    # The mark, sized to sit on the cap height of the wordmark below it.
    draw.rectangle([left, 150, left + 46, 196], fill=RUST_DARK)

    name = load("bold", 128)
    label = load("mono", 25)
    line = load("regular", 34)

    draw.text((left, 232), "Gossans", font=name, fill=PAPER)

    draw.line([(left, 420), (width - left, 420)], fill=RULE, width=2)

    tracked(draw, (left, 452),
            "EXTRACTION ECONOMICS & PRODUCTION OPTIMISATION",
            label, DRAFT, spacing=2.4)

    draw.text((left, 508),
              "Your production data already holds the answer.",
              font=line, fill=MUTED)

    # A rust rule along the foot, so the mark reads even as a thumbnail.
    draw.rectangle([0, height - 10, width, height], fill=RUST_DARK)

    image.save(ROOT / "og-image.png", format="PNG", optimize=True)
    print(f"og-image.png {width}x{height}")


if __name__ == "__main__":
    write_favicon()
    write_apple_touch()
    write_og_image()
    print("\nDone. Commit the generated files.")
