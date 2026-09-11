#!/usr/bin/env python3
"""Draw the Gossans aperture, the master visual asset.

Six blades opening around a hexagonal pupil. The theme is hidden value
becoming visible, so the geometry is parameterised on how far the aperture is
open: `stop` runs from 0, shut, to 1, wide. That one number gives the identity
a state rather than a picture, which is what makes it usable as a system --
shut on the cover, open on the answer.

Two decisions worth stating, because they depart from the supplied artwork:

  flat, not gradient   A gradient cannot emboss, cannot print in one ink, and
                       shifts between reproductions. Every brand named in the
                       brief -- BlackRock, Bloomberg, Palantir, McKinsey --
                       uses flat colour for exactly that reason. The two-tone
                       variant recovers the depth in a way that survives.

  gaps at the corners  The blade separations sit on the hexagon's vertices
                       rather than mid-edge, so the six straight edges stay
                       unbroken and the silhouette still reads as a hexagon
                       when the gaps themselves are below a pixel.

    python tools/make-mark.py

Writes into public/. Run tools/make-assets.py afterwards to rebuild the raster
icons and the social card from this same geometry.
"""

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"

# Copper primary, sandstone secondary, slate accent. Charcoal is typography
# only under the brand brief, so it does not appear in the mark at all.
COPPER = "#B7532E"
COPPER_GOLD = "#D18A4D"
SANDSTONE = "#D9C4A0"
SLATE = "#54606B"
PAPER = "#FBFAF7"

SIDES = 6
CX = CY = 32.0
R = 28.0

# How far open at rest. Chosen so the pupil is legible at 16 px but the blades
# still carry enough mass to hold colour.
STOP = 0.68


def _polar(r, deg):
    a = math.radians(deg)
    return (CX + r * math.cos(a), CY + r * math.sin(a))


def _offset(p, q, d):
    """The line p->q pushed d units to its right, as a point pair.

    Right, not left, because the y axis points down in SVG and in Pillow.
    """
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(dx, dy)
    nx, ny = -dy / n, dx / n
    return ((p[0] + nx * d, p[1] + ny * d), (q[0] + nx * d, q[1] + ny * d))


def _meet(a, b):
    """Where two infinite lines cross. Both are given as point pairs."""
    (x1, y1), (x2, y2) = a
    (x3, y3), (x4, y4) = b
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        raise ValueError("parallel edges: check twist and stop")
    p = x1 * y2 - y1 * x2
    q = x3 * y4 - y3 * x4
    return ((p * (x3 - x4) - (x1 - x2) * q) / den,
            (p * (y3 - y4) - (y1 - y2) * q) / den)


def blades(stop=STOP, twist=13.0, gap=2.4, r_outer=R):
    """One polygon per blade, as plain point lists.

    The blade is the quadrilateral between an outer hexagon edge and an inner
    hexagon edge, with its two radial sides pushed inward by half the gap. Two
    consequences are the point of doing it this way: the slits come out a
    constant width in real units rather than a constant angle, so they do not
    vanish as they approach the pupil; and the outer hexagon edges keep their
    full length, so the silhouette still reads as a hexagon once the slits are
    below a pixel.

    stop    0 shut, 1 wide. Sets the pupil radius.
    twist   degrees the inner hexagon lags the outer. This is the pinwheel.
    gap     slit width, in the mark's own 64-unit frame.
    """
    r_inner = r_outer * (0.15 + 0.44 * stop)
    step = 360.0 / SIDES
    outer = [_polar(r_outer, -90.0 + step * k) for k in range(SIDES)]
    inner = [_polar(r_inner, -90.0 + step * k + twist) for k in range(SIDES)]

    out = []
    for k in range(SIDES):
        v0, v1 = outer[k], outer[(k + 1) % SIDES]
        w0, w1 = inner[k], inner[(k + 1) % SIDES]
        # Walking w0 -> v0 puts the blade on the left, so a positive offset
        # eats into the blade; the far side is walked the other way round.
        side_a = _offset(w0, v0, gap / 2.0)
        side_b = _offset(v1, w1, gap / 2.0)
        top = (v0, v1)
        bottom = (w1, w0)
        out.append([_meet(side_a, top), _meet(top, side_b),
                    _meet(side_b, bottom), _meet(bottom, side_a)])
    return out


def _path(points):
    d = "M%.2f %.2f" % points[0]
    d += "".join("L%.2f %.2f" % p for p in points[1:])
    return d + "Z"


HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" '
        'role="img" aria-label="Gossans">')


def aperture(fill=COPPER, second=None, stop=STOP, gap=2.4,
             background=None):
    """The mark. `second` alternates blades, for the two-tone variant."""
    parts = [HEAD]
    if background:
        parts.append('<rect width="64" height="64" fill="%s"/>' % background)
    for k, blade in enumerate(blades(stop=stop, gap=gap)):
        colour = second if (second is not None and k % 2) else fill
        parts.append('<path d="%s" fill="%s"/>' % (_path(blade), colour))
    parts.append("</svg>")
    return "".join(parts)


def lockup(fill=COPPER, stop=STOP):
    """Mark and wordmark on one line, for the header and for email.

    The wordmark is set as text rather than outlines so it stays selectable
    and stays one file; anything going to a printer should use the SVG with
    the face embedded instead.
    """
    blade_paths = "".join('<path d="%s" fill="%s"/>' % (_path(b), fill)
                          for b in blades(stop=stop))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 64" '
        'role="img" aria-label="Gossans">'
        + blade_paths
        + '<text x="80" y="43" font-family="Archivo, Helvetica, Arial, '
          'sans-serif" font-size="34" font-weight="600" letter-spacing="-0.5" '
          'fill="#1E2327">Gossans</text>'
        + "</svg>"
    )


def sequence(steps=5, fill=COPPER):
    """The mark opening. Hidden value becoming visible, said once, literally."""
    return [aperture(fill=fill, stop=0.10 + (0.82 * i / (steps - 1)))
            for i in range(steps)]


# --------------------------------------------------------------------------
# One geometry, two renderers
# --------------------------------------------------------------------------
# make-assets.py rasterises from these same point lists, so the PNG icons and
# the SVG cannot drift apart.

def shapes(stop=STOP, gap=2.4):
    """Blades as flattened polygons in the 0..64 frame, for a raster renderer."""
    return blades(stop=stop, gap=gap)


def scaled(points, scale, dx=0.0, dy=0.0):
    return [(x * scale + dx, y * scale + dy) for x, y in points]


def write(name, body):
    (PUBLIC / name).write_text(body, encoding="utf-8")
    return "%-24s %5d bytes" % (name, len(body))


if __name__ == "__main__":
    outputs = [
        write("mark.svg", aperture()),
        write("mark-two-tone.svg", aperture(second=COPPER_GOLD)),
        write("mark-mono.svg", aperture(fill="currentColor")),
        write("mark-slate.svg", aperture(fill=SLATE)),
        write("mark-sand.svg", aperture(fill=SANDSTONE)),
        # Small sizes: wider gaps and a wider pupil, or both close up.
        write("mark-simple.svg", aperture(stop=0.84, gap=3.2)),
        # Transparent, no container: the favicon is the aperture and
        # nothing else, so it sits on whatever the browser chrome is.
        write("favicon.svg", aperture(stop=0.84, gap=3.2)),
        write("mark-shut.svg", aperture(stop=0.08)),
        write("mark-open.svg", aperture(stop=0.92)),
        write("lockup.svg", lockup()),
    ]
    for line in outputs:
        print(line)
    print()
    print("Run tools/make-assets.py next to rebuild the raster icons.")
