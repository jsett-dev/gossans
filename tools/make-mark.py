#!/usr/bin/env python3
"""Draw the Gossans mark as vector, at three levels of detail.

The supplied brand sheet is a raster with a mottled mineral texture through
the oxidised band. That is handsome at size and impossible below about sixty
pixels, impossible in one colour, and impossible to emboss. So the geometry is
rebuilt here from named curves: a ridge, the oxidised zone beneath it, and the
contours below that.

Three versions, because one drawing cannot do every job:

    full        ridge, oxidised band, five contours. Headers, cards, print.
    simple      ridge, band, two contours. Anything under about 48 px.
    icon        ridge and band only, on charcoal. Favicon and app icon.

    python tools/make-mark.py

Writes into public/. Run tools/make-assets.py afterwards to regenerate the
raster icons and the social card from whichever mark is current.
"""

import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"

# Sampled from the brand sheet's own swatch row.
CHARCOAL = "#1E2327"
COPPER = "#B7532E"
COPPER_GOLD = "#D18A4D"
SANDSTONE = "#E2D3B1"
SLATE = "#6C7580"
PAPER = "#F1F2EF"

# The ridge: asymmetric, summit left of centre, because a symmetrical peak
# reads as a logo of a mountain and an uneven one reads as ground.
RIDGE = (
    "M16 57 "
    "C37 55 50 51 63 42 "
    "C73 34 82 20 89 17 "
    "C96 19 104 30 114 39 "
    "C129 50 153 57 184 57 "
    "C162 63 121 65 91 63 "
    "C60 61 34 61 16 57 Z"
)

# The oxidised zone: wider than the ridge above it, tapering to points, which
# is the whole argument. What shows at surface is the smaller part.
BAND = (
    "M6 66 "
    "C40 59 71 64 101 68 "
    "C131 72 162 70 194 62 "
    "C167 84 131 89 99 86 "
    "C66 83 33 76 6 66 Z"
)

# Contours below, each shorter and fainter than the one above it.
CONTOURS = [
    ("M12 91 C46 85 78 93 110 95 C141 97 170 92 190 87", 1.6, 0.85),
    ("M19 98 C50 93 80 99 110 101 C139 103 164 99 182 94", 1.4, 0.64),
    ("M27 104 C55 100 82 105 110 107 C136 109 158 106 173 102", 1.25, 0.46),
    ("M35 110 C60 106 84 110 109 112 C132 114 150 111 164 108", 1.1, 0.31),
    ("M44 115 C65 112 86 115 108 117 C128 118 143 116 155 113", 1.0, 0.19),
]

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" '
        'role="img" aria-label="Gossans">')


def contours(count, colour=SLATE):
    out = []
    for d, width, opacity in CONTOURS[:count]:
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                   'stroke-linecap="round" opacity="%.2f"/>'
                   % (d, colour, width, opacity))
    return "".join(out)


def mark(count=5, ridge=CHARCOAL, band=COPPER, contour=SLATE, height=124):
    return (
        (HEAD % ("0 8 200 %d" % height))
        + '<path d="%s" fill="%s"/>' % (BAND, band)
        + '<path d="%s" fill="%s"/>' % (RIDGE, ridge)
        + contours(count, contour)
        + "</svg>"
    )


def icon(bg=CHARCOAL, ridge=PAPER, band=COPPER):
    """Square, for a favicon. No contours: they are gone by 32 px anyway."""
    return (
        (HEAD % "0 0 64 64")
        + '<rect width="64" height="64" fill="%s"/>' % bg
        + '<g transform="translate(-2 8) scale(0.34)">'
        + '<path d="%s" fill="%s"/>' % (BAND, band)
        + '<path d="%s" fill="%s"/>' % (RIDGE, ridge)
        + "</g></svg>"
    )


def single_colour(colour=CHARCOAL):
    """One ink, for embossing, stamps and faxes from 1994."""
    return (
        (HEAD % "0 8 200 92")
        + '<path d="%s" fill="%s" opacity="0.42"/>' % (BAND, colour)
        + '<path d="%s" fill="%s"/>' % (RIDGE, colour)
        + contours(3, colour)
        + "</svg>"
    )


# --------------------------------------------------------------------------
# One geometry, two renderers
# --------------------------------------------------------------------------

def _bezier(p0, p1, p2, p3, steps):
    out = []
    for i in range(1, steps + 1):
        t = i / steps
        u = 1 - t
        x = (u * u * u * p0[0] + 3 * u * u * t * p1[0]
             + 3 * u * t * t * p2[0] + t * t * t * p3[0])
        y = (u * u * u * p0[1] + 3 * u * u * t * p1[1]
             + 3 * u * t * t * p2[1] + t * t * t * p3[1])
        out.append((x, y))
    return out


def polygon(path, steps=24):
    """Flatten one of the M/C/Z paths above into points.

    Only the subset actually used here is handled, deliberately: a general SVG
    parser would be more code and more to get wrong, and the paths are written
    in this file.
    """
    # The paths are written as "M16 57 C37 55 ...", with no space after the
    # command letter, so splitting on whitespace is not enough.
    tokens = re.findall(r"[A-Za-z]|-?\d+(?:\.\d+)?", path)
    pts, cur, start, i = [], None, None, 0
    while i < len(tokens):
        cmd = tokens[i]
        if cmd == "M":
            cur = (float(tokens[i + 1]), float(tokens[i + 2]))
            start = cur
            pts.append(cur)
            i += 3
        elif cmd == "C":
            c1 = (float(tokens[i + 1]), float(tokens[i + 2]))
            c2 = (float(tokens[i + 3]), float(tokens[i + 4]))
            end = (float(tokens[i + 5]), float(tokens[i + 6]))
            pts.extend(_bezier(cur, c1, c2, end, steps))
            cur = end
            i += 7
        elif cmd in ("Z", "z"):
            if start:
                pts.append(start)
            i += 1
        else:
            raise ValueError("unsupported path command %r" % cmd)
    return pts


def scaled(points, scale, dx=0.0, dy=0.0):
    return [(x * scale + dx, y * scale + dy) for x, y in points]


RIDGE_POLY = None
BAND_POLY = None


def shapes():
    """Ridge and band as flattened polygons, for a raster renderer."""
    global RIDGE_POLY, BAND_POLY
    if RIDGE_POLY is None:
        RIDGE_POLY = polygon(RIDGE)
        BAND_POLY = polygon(BAND)
    return RIDGE_POLY, BAND_POLY


def write(name, body):
    path = PUBLIC / name
    path.write_text(body, encoding="utf-8")
    return "%-22s %5d bytes" % (name, len(body))


if __name__ == "__main__":
    outputs = [
        write("mark.svg", mark(5)),
        write("mark-simple.svg", mark(2, height=100)),
        write("mark-mono.svg", single_colour()),
        write("favicon.svg", icon()),
    ]
    for line in outputs:
        print(line)
    print()
    print("Run tools/make-assets.py next to rebuild the raster icons.")
