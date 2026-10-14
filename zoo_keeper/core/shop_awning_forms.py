"""What a corner shop's awning is, in numbers: ONE place, no bpy (1.108.0, factory roadmap 241).

The urban comps (the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`): "Corners carry the life. The corner
building has the shop at grade (lit, awning), homes above", and "a lit restaurant at street level under an
awning -- the warm light the eye goes to first". The Empties comps (`docs/reference/EMPTIES_COMPS.md`) list the
awning as Zoo's to build. Deli Counter (>= 0.219.0) stands one over a corner block's shopfront, and this module
draws it from its slot's box alone, so an awning of any width, projection or drop is drawn without the module
knowing the building.

THE SHED: the common storefront awning, a canvas slope from the wall down to a valance along its front, closed at
each end by a triangular cheek. The canvas and the valance are thin boxes, not single faces, so the awning reads
from below as from the street.

THE FRAME is Zoo's: X along the facade; Y the projection, the WALL at +Y and the street at -Y, as every module faces
-Y; Z up. Centre pivot, and the extents are exactly the slot's (w, d, h): the slope's top meets the wall at the box's
top, the valance hangs to the box's bottom at its front.

THE FORMS are ``<shape>_<colour>``: one shape, ``shed``, in the canvas colours a 1990s Philadelphia corner shop wore
(`COLOURS`). The colour is the form's because it is the shop's: a deli's red, a grocery's green, a laundromat's
navy, a bar's black. Each colour is its own material, ONE a module and one module a building, so no merge is lost
by it.

NO FACE OF ONE PART LIES ON ANOTHER'S, so `prims.coincident_pairs` reads none before Blender does:
  * the slope stops `SINK` behind the valance's front face, inside the valance;
  * the slope stops `2 * NEST` short of either end, inside the cheeks, which stand `NEST` inside the ends;
  * a cheek's back stands `SINK` off the wall plane, and its bottom edge `NEST` over the valance's top.

COLLISION: none (the genome's `collision: false`). The awning hangs over a frontage nobody walks at its height, and
the building's own collider is the wall behind it.
"""
from __future__ import annotations

import math

from . import prims

#: the canvas's thickness, metres: a box this thin, not a face, so it reads from below
CANVAS = 0.02
#: the valance's drop along the front, metres -- a 10 in valance, the common size
VALANCE = round(10 * 0.0254, 4)       # 0.254 m
#: a part's end inside the one it runs into (Zoo's JOIN)
SINK = 0.004
#: how far, each side, a part stands inside the one it meets
NEST = 0.003
SHAPES = ("shed",)
#: the canvas colours, linear RGB, tinted onto Pixelcoat's achromatic `canvas_neutral`
COLOURS = {
    "red": (0.42, 0.04, 0.035),
    "green": (0.035, 0.20, 0.07),
    "navy": (0.03, 0.05, 0.16),
    "black": (0.025, 0.025, 0.028),
}
FORMS = tuple(f"{s}_{c}" for s in SHAPES for c in COLOURS)
MAT = "canvas"
PART = "ShopAwning_Canvas"


def form_of(form):
    """``(shape, colour)`` for a slot's ``form``: none or "auto" is ``shed_red``."""
    f = (str(form) if form not in (None, "") else "auto").lower()
    if f == "auto":
        f = FORMS[0]
    if f not in FORMS:
        raise ValueError("shop_awning has no form %r (it draws %s)" % (form, ", ".join(FORMS)))
    shape, colour = f.split("_", 1)
    return shape, colour


def _shed(w, d, h):
    x0, x1, y0, y1, z0, z1 = -w / 2.0, w / 2.0, -d / 2.0, d / 2.0, -h / 2.0, h / 2.0
    zv = z0 + min(VALANCE, h / 2.0)                # the valance's top
    out = [prims.box(PART, MAT, (x0, y0, z0), (x1, y0 + CANVAS, zv))]

    # the slope: its top surface from the wall's top (y1, z1) to the valance's top at the front, its front end
    # SINK behind the valance's front face, its ends 2 * NEST inside the box's ends
    def top_at(y):
        return zv + (z1 - zv) * (y - y0) / (y1 - y0)

    yf = y0 + SINK
    sx0, sx1 = x0 + 2 * NEST, x1 - 2 * NEST
    v = [(sx0, yf, top_at(yf) - CANVAS), (sx1, yf, top_at(yf) - CANVAS), (sx1, y1, z1 - CANVAS), (sx0, y1, z1 - CANVAS),
         (sx0, yf, top_at(yf)), (sx1, yf, top_at(yf)), (sx1, y1, z1), (sx0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    out.append(prims.mesh(PART, MAT, v, f))

    # the cheeks: a triangle under the slope at each end, from the wall to the valance, CANVAS thick
    yb = y1 - SINK                                 # off the wall plane
    zb = zv + NEST                                 # over the valance's top
    yc = y0 + CANVAS / 2.0                         # the front corner, inside the valance
    for side in (-1, 1):
        xo = side * (w / 2.0 - NEST)               # the outer face
        xi = side * (w / 2.0 - NEST - CANVAS)      # the inner face
        a, b = (xi, xo) if side > 0 else (xo, xi)  # a < b whichever end
        # the hypotenuse runs inside the slope's thickness: the back corner at its middle, the front corner at
        # its middle too, or on the bottom edge where a shallow awning brings the slope that low
        zc = max(zb, top_at(yc) - CANVAS / 2.0)
        tri = [(yb, top_at(yb) - CANVAS / 2.0), (yb, zb), (yc, zc)]
        v = [(a, y, z) for y, z in tri] + [(b, y, z) for y, z in tri]
        # wound outward, as `prims.box`'s faces are: -X, +X, the back (+Y), the bottom, the hypotenuse
        f = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
        out.append(prims.mesh(PART, MAT, v, f))
    pitch = math.degrees(math.atan2(z1 - zv, y1 - y0))
    return out, {"pitch_deg": round(pitch, 3), "valance_m": round(zv - z0, 4)}


def plan(w, d, h, form=None):
    """The awning for a slot of ``w`` x ``d`` x ``h`` (X along the facade, the wall at +Y): ``{prims, collision,
    form, colour, rgb, facts}``. ``collision`` is empty."""
    shape, colour = form_of(form)
    w, d, h = float(w), float(d), float(h)
    if min(w, d, h) <= 4 * CANVAS:
        raise ValueError("an awning %.3f x %.3f x %.3f m is too small to draw" % (w, d, h))
    out, facts = _shed(w, d, h)
    out, _boxes = prims.fit_exact(out, (-w / 2, -d / 2, -h / 2), (w / 2, d / 2, h / 2))
    facts["tris"] = prims.tri_count(out)
    return {"prims": out, "collision": [], "form": f"{shape}_{colour}", "colour": colour, "rgb": COLOURS[colour],
            "facts": facts}
