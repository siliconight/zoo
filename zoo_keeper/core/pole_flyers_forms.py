"""Flyers on a pole as ONE module: a sleeve of paper, one atlas, one draw.

Zoo 1.34.0, species `pole_flyers`. The walker, 2026-09-30, after cold run 9118
stood a single flat 0.30 m bill on each 0.12 m pole -- which read as a small
sign -- sent six photographs of real poles: a festival bill pasted twice, one
above the other; a single gig bill on a wooden pole; columns of flyers up one
side; poles wrapped from knee to head height in layered, torn paper with the
shreds bunched at the foot; and a plywood board. Their placement guide names
the same shape: "Loose vertical stack: flyers were added over time to a pole
or narrow wall", "one or two overlaps where the newer sheet covers part of an
older one", "a pole may have stacked handbills". This draws that.

WHAT IS BUILT, in the recipe frame (metres, Z up, the pole's axis on Z at the
slot's centre, its FRONT toward -Y as every Zoo prop's): sheets of alley
handbill (`poster_art`'s `alley` family) CURVED ROUND THE POLE, each a strip
of flat facets on a circle, in layers a paper's thickness apart. Three forms,
from the photographs:

  pair   two sheets up the front, the lower pasted a little over the upper
         -- often the same bill twice, a campaign (the festival photo);
  stack  a column of three up the front, a step round the pole each, over an
         older sheet and a scrap;
  wrap   courses all the way round, layered, the oldest under the newest,
         and torn shreds at the foot.

HISTORY, AND THE WALKER'S "TEMPER THIS". The faded-'80s palette guide is
applied where age is the story and nowhere else: the NEWEST layer is printed
as `poster_art` paints it, day-glo; each older layer fades toward cheap
newsprint (`fade`: bright inks go first, dark ink holds -- "a softened yellow
field but a still-readable dark title"); scraps are partial sheets of the
oldest. Nothing fades the club's or the store's posters.

THE SLOT IS FILLED BY CONSTRUCTION. Width and depth are the sleeve's outer
diameter; every form keeps paper at the four cardinal angles at the outer
layer's radius, within Zoo's 2 cm fit (a pair on the front alone left the back
of the slot empty -- a scrap or an older sheet stands there, as one does on a
real pole), and its sheets reach the band's top and foot. Overlapping sheets
stand `LAYER` apart. No collision: paper does not stop a body.
"""
from __future__ import annotations

import math
import zlib

from . import poster_art as PA
from . import poster_copy as PC
from . import prims as P
from .flat_forms import ART

FORMS = ("pair", "stack", "wrap")
#: A paper's thickness between layers, as `poster_wall_forms.LAYER`.
LAYER = 0.004
#: Layers in the sleeve, innermost (oldest) first.
LAYERS = 4
#: Zoo's slot-fit tolerance.
FIT_TOL = 0.02
#: How far each layer has faded toward newsprint, oldest first: the newest is
#: fresh (the walker's "temper this").
FADE = (0.62, 0.38, 0.0, 0.0)
#: The facet grid round the pole: a vertex every this many degrees (and at an
#: arc's ends), so a sheet's outline is a circle's and its bounds reach the
#: cardinal angles.
STEP_DEG = 15.0
#: The front, in the recipe frame.
FRONT = -90.0
#: A course overlaps the one below it by this much of a sheet.
OVERLAP = 0.12
#: The default height of each form's band, metres: two sheets, three, a pole
#: wrapped from knee height to above the head.
HEIGHT = {"pair": 0.78, "stack": 1.12, "wrap": 1.9}


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def _u(*k):
    return (_h(*k) % 10000) / 10000.0


def sheet_size():
    return PA.SIZES_M["alley"]


def _radius(layer, r_out):
    return r_out - (LAYERS - 1 - layer) * LAYER


def _arc(tile, layer, r_out, centre_deg, arc_m, z0, z1, uv=(0.0, 1.0, 0.0, 1.0)):
    """A sheet's facets: ``arc_m`` metres of paper round the circle of
    ``layer``, centred on ``centre_deg``, from ``z0`` to ``z1``; ``uv`` the
    part of its tile it shows (u0, u1, v0, v1) -- a torn scrap is a sheet's
    corner. Wound so each facet faces out, U increasing with the angle (left
    to right for a viewer outside)."""
    r = _radius(layer, r_out)
    span = min(math.degrees(arc_m / r), 350.0)
    a0, a1 = centre_deg - span / 2.0, centre_deg + span / 2.0
    grid = [a0] + [k * STEP_DEG for k in range(math.ceil(a0 / STEP_DEG), math.floor(a1 / STEP_DEG) + 1)
                   if a0 < k * STEP_DEG < a1] + [a1]
    verts, faces, uvs = [], [], []
    u0, u1, v0, v1 = uv
    for a in grid:
        t = math.radians(a)
        x, y = r * math.cos(t), r * math.sin(t)
        verts += [(x, y, z0), (x, y, z1)]
    for j in range(len(grid) - 1):
        b0, t0, b1, t1 = 2 * j, 2 * j + 1, 2 * j + 2, 2 * j + 3
        faces.append((b0, b1, t1, t0))
        ua = u0 + (u1 - u0) * (grid[j] - a0) / (a1 - a0)
        ub = u0 + (u1 - u0) * (grid[j + 1] - a0) / (a1 - a0)
        uvs.append(((ua, v0), (ub, v0), (ub, v1), (ua, v1)))
    p = P.mesh("PoleFlyers_Sheet", ART, verts, faces)
    p["tile"] = tile
    p["uvs"] = uvs
    return p


def fade(canvas, amount, paper=(189, 179, 154)):
    """In place: ``canvas`` faded toward ``paper`` (the palette guide's
    dusty newsprint, #BDB39A) by ``amount``, bright inks more than dark --
    `amount` scaled by the pixel's own value, so a title in dark ink stays
    readable while the day-glo field goes to paper first."""
    if amount <= 0.0:
        return canvas
    b = canvas.buf
    pr, pg, pb = paper
    for i in range(0, len(b), 3):
        r, g, bl = b[i], b[i + 1], b[i + 2]
        lum = (0.299 * r + 0.587 * g + 0.114 * bl) / 255.0
        k = amount * (0.35 + 0.65 * lum)
        b[i] = int(r + (pr - r) * k)
        b[i + 1] = int(g + (pg - g) * k)
        b[i + 2] = int(bl + (pb - bl) * k)
    return canvas


def plan(w, d, h, form="stack", variant=0, key="pole_flyers"):
    """``{"prims", "tiles", "collision", "facts"}`` for one pole's flyers."""
    if form not in FORMS:
        raise ValueError(f"pole_flyers: no form {form!r}; the forms are {', '.join(FORMS)}")
    r_out = min(w, d) / 2.0
    sw, sh = sheet_size()
    # a band lower than a sheet scales the sheets down, never up
    k = min(1.0, h / sh)
    sw, sh = sw * k, sh * k
    rows = sorted(range(len(PC.COPY["alley"])), key=lambda r: _h(key, variant, form, r))
    tiles, prims, pieces = {}, [], []
    taken = {layer: [] for layer in range(LAYERS)}      # (a0, a1, z0, z1), degrees

    def _span(layer, centre, arc_m):
        half = min(math.degrees(arc_m / _radius(layer, r_out)), 350.0) / 2.0
        return centre - half, centre + half

    def _clear(layer, a0, a1, z0, z1):
        for b0, b1, y0, y1 in taken[layer]:
            if z0 >= y1 - 1e-6 or y0 >= z1 - 1e-6:
                continue
            # angular overlap, round the circle
            for shift in (-360.0, 0.0, 360.0):
                if a0 < b1 + shift - 1e-6 and b0 + shift < a1 - 1e-6:
                    return False
        return True

    def sheet(prefer, centre, z0, z1, uv=(0.0, 1.0, 0.0, 1.0), row_i=None):
        """Paper at the first layer in ``prefer`` where it overlaps nothing
        already on that layer -- two sheets sharing a plane would z-fight --
        faded by the layer it lands on. None when every layer is taken there."""
        arc_m = sw * (uv[1] - uv[0])
        for layer in prefer:
            a0, a1 = _span(layer, centre, arc_m)
            if _clear(layer, a0, a1, z0, z1):
                break
        else:
            return None
        taken[layer].append((a0, a1, z0, z1))
        j = len(prims)
        row = rows[(j if row_i is None else row_i) % len(rows)]
        tile = f"s{j}"
        tiles[tile] = {"kind": "wallposter", "family": "alley", "row": row,
                       "w_m": round(sw, 4), "h_m": round(sh, 4),
                       "key": f"{key}|{variant}|{row}", "fade": FADE[layer]}
        prims.append(_arc(tile, layer, r_out, centre, arc_m, z0, z1, uv))
        pieces.append({"layer": layer, "centre": round(centre, 2), "z": (round(z0, 3), round(z1, 3)),
                       "row": row, "scrap": uv != (0.0, 1.0, 0.0, 1.0)})
        return layer

    NEW, OLD = (3, 2, 1, 0), (1, 0, 2, 3)
    jitter = lambda *k_: (_u(key, variant, *k_) - 0.5)
    if form == "pair":
        # the festival photo: two sheets up the front; half the time the
        # same bill twice
        same = _u(key, variant, "same") < 0.5
        # the back first: an older sheet, torn to half its width
        sheet((0, 1), -FRONT, h * 0.2, h * 0.2 + sh * 0.8, uv=(0.2, 0.7, 0.1, 0.9), row_i=2)
        sheet(NEW, FRONT + 8 * jitter("a"), h - sh, h, row_i=0)
        sheet(NEW, FRONT + 8 * jitter("b"), 0.0, sh, row_i=0 if same else 1)
    elif form == "stack":
        n = 3
        step = (h - sh) / (n - 1)
        # older first: one sheet a quarter turn round, and a scrap on the back
        # (inside the band: at a low band a sheet starting 30% up overshot it)
        z1 = min(h, h * 0.3 + sh)
        sheet(OLD, FRONT + 100, max(0.0, z1 - sh), z1, row_i=n)
        sheet(OLD, -FRONT, h * 0.05, h * 0.05 + sh * 0.55, uv=(0.3, 0.8, 0.0, 0.55), row_i=n + 1)
        for i in range(n):
            z0 = i * step
            sheet(NEW, FRONT + (i - 1) * 18 + 6 * jitter("s", i), z0, z0 + sh, row_i=i)
    else:
        # courses all the way round, the oldest under the newest; the top
        # course and the bottom reach the band's ends
        circ = 2 * math.pi * _radius(2, r_out)
        per = max(2, math.ceil(circ / (sw * 0.8)))
        courses = max(2, math.ceil((h - sh) / (sh * (1 - OVERLAP))) + 1)
        step = (h - sh) / (courses - 1)
        # the shreds at the foot first: the oldest paper, torn to scraps
        for s_ in range(per + 2):
            u0 = 0.1 * (s_ % 5)
            hh = sh * (0.25 + 0.3 * _u(key, variant, "shred", s_))
            sheet((0,), FRONT + s_ * 360.0 / (per + 2) + 20 * jitter("f", s_), 0.0, hh,
                  uv=(u0, u0 + 0.45, 0.0, hh / sh), row_i=s_)
        # then the courses, bottom up: each lands on the oldest free layer
        # it can, so what went up last sits on top
        for c in range(courses):
            z0 = c * step
            for i in range(per):
                centre = FRONT + i * 360.0 / per + (c % 2) * 180.0 / per + 10 * jitter("w", c, i)
                sheet((1, 2, 3, 0) if c < courses - 1 else NEW, centre, z0, z0 + sh,
                      row_i=c * per + i)
    # EVERY SIDE CARRIES PAPER. The slot's width and depth are the sleeve's
    # diameter, and a form that leaves a cardinal side bare falls short of it:
    # a pair on a 0.30 m wooden pole covered 118 degrees of it and built 0.258
    # m against a 0.30 m slot. Old paper goes there -- a faded scrap, as on
    # any pole anybody has ever papered -- on the oldest layer free there
    # ABOVE THE INNERMOST: that one sits `(LAYERS - 1) * LAYER` inside the
    # sleeve, and paper there on both ends of an axis fell 24 mm short of the
    # slot against Zoo's 20 mm (measured over the genome's range).
    for s_, card in enumerate((0.0, 90.0, 180.0, -90.0)):
        covered = any(
            any(b0 + shift <= card <= b1 + shift for shift in (-360.0, 0.0, 360.0))
            for layer in taken if layer >= 1 for b0, b1, _z0, _z1 in taken[layer])
        if not covered:
            zc = h * (0.3 + 0.4 * _u(key, variant, "side", s_))
            sheet((1, 2, 3), card, max(0.0, zc - sh * 0.3), min(h, zc + sh * 0.3),
                  uv=(0.25, 0.75, 0.2, 0.8), row_i=len(prims) + s_)
    return {"prims": prims, "tiles": tiles, "collision": [],
            "facts": {"form": form, "sheets": len(prims), "radius": round(r_out, 4),
                      "sheet_m": (round(sw, 4), round(sh, 4)), "pieces": pieces,
                      "tris": P.tri_count(prims)}}
