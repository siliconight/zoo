"""A run of wall posters as ONE module: one atlas, one mesh, one draw.

Zoo 1.30.0, species `poster_wall`. The walker, 2026-09-29: posters to fill
walls in strip clubs, bars, alleys and stores; the plan they approved, and
the reason for the shape: "A shared atlas saves texture binds and almost no
memory, and in Godot every separate mesh is still its own draw" -- so the
posters that hang together are built together. A card-shop `poster` is up
to four draws (frame, mat, plate, art) and one texture EACH; a poster wall of
eight is one. The system guide says the same: "a collage sheet can be a
single atlas texture mapped to a wall panel".

WHAT IS BUILT, in the recipe frame (metres, Z up, x along the run, the posters
facing -Y, the wall at +Y): `n` sheets of the family's size (`poster_art.
SIZES_M`) across the run, each its own tile in the module's atlas -- so no
two in a run repeat (the card shop hung identical pairs side by side, because
its art was keyed per size and variant) -- laid out by the family's rule:

  club   a neat row, tops level, even gaps: posters in a club are put up;
  store  the same, a little tighter: a window of deals;
  bar    a row with tops that wander and sheets that tilt a few degrees,
         pinned up by whoever was closing;
  alley  a collage: two courses, overlapping, tilted, pasted over each other.

THE SLOT IS FILLED, AND NOTHING IS STRETCHED. The first and last sheets stand
at the run's ends and the band's top and foot are reached by construction,
so the bounds are the slot's to Zoo's 2 cm fit tolerance; `fit_exact` is not
used, because a stack of paper a few millimetres deep would be stretched to
the slot's depth (Zoo 1.27.0 recorded that exact failure on the window
neon). Overlapping sheets stand `LAYER` apart, past `prims.coincident_pairs`'
2 mm plane tolerance.

THE SLOT IS SHALLOW, AND MUST BE: a run is paper on a wall, a few
millimetres deep at most (`LAYER` times its layers), and Zoo's fit check
holds its depth to the slot's within `FIT_TOL` -- so a slot deeper than
2 cm fails the build (the first built test used 3 cm and did). The genome's
depth range is 4 mm to 2 cm.

No collision: a sheet of paper does not stop a body.
"""
from __future__ import annotations

import math
import zlib

from . import poster_art as PA
from . import poster_copy as PC
from . import prims as P
from .flat_forms import _quad

LAYER = 0.004
#: Zoo's slot-fit tolerance (`core/validate.py`, `tol`), which a run's
#: bounds must meet in every axis.
FIT_TOL = 0.02
#: The family's spacing along the run, metres, and its tilt range, degrees.
LAYOUT = {"club": (0.22, 0.0), "store": (0.08, 0.0), "bar": (0.05, 3.0), "alley": (-0.06, 5.0)}
#: How far a bar or alley sheet's top may wander below the band's top.
WANDER = {"club": 0.0, "store": 0.0, "bar": 0.06, "alley": 0.10}
#: THE CLUB'S BLACKLIGHT (1.33.0): ``(emission, albedo)`` for
#: `materials.make_backlit_material`, by family; a family not here is paper,
#: lit by the room. The walker, 2026-09-30, choosing among three after cold
#: run 9115 showed the club's dim coloured light take the sheets' whites to
#: 92-127 luma: "blacklight treatment for the club posters" -- the club's
#: posters are printed in inks that glow under its UV tubes. The artwork is
#: its own emission, so dark ink stays dark and the bright inks glow; the same
#: atlas and the same one material a run, so no texture and no draw is added.
#: Named `_Face`, so Lux's power cut takes the blacklight with the lights.
#: Albedo 1.0: the paper still takes the room's light. The emission is a
#: starting point, judged on the walk (the cooler's glow began at 1.0, the
#: cigarette rack's header read faint at 0.5).
BLACKLIGHT = {"club": (0.6, 1.0)}


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def loud_sheets(n, key, variant):
    """Which of a run's ``n`` sheets are on loud paper (1.41.0): one; two
    from six sheets; three from sixteen -- spread evenly along the run from
    a start the run's own name picks. The rest are plain."""
    count = 1 if n < 6 else (2 if n < 16 else 3)
    start = _h(key, variant, "loud") % max(1, n)
    return {(start + k * n // count) % n for k in range(count)} if n else set()


def band_height(family, rows=1):
    """The band a run of ``family`` fills: its sheet height, plus the wander,
    plus a second course for an alley collage."""
    ph = PA.SIZES_M[family][1]
    if family == "alley" and rows > 1:
        return round(ph * 1.7 + WANDER[family], 3)
    return round(ph + WANDER[family], 3)


def _order(family, key, variant, n):
    """``n`` rows of the family's copy, no two alike while the table lasts."""
    rows = sorted(range(len(PC.COPY[family])), key=lambda r: _h(family, key, variant, r))
    return [rows[i % len(rows)] for i in range(n)]


def plan(w, d, h, family="club", variant=0, key="poster_wall"):
    """``{"prims", "tiles", "collision", "facts"}`` for one run of posters."""
    if family not in PA.SIZES_M:
        raise ValueError(f"poster_wall: no family {family!r}; the families are {', '.join(PC.FAMILIES)}")
    pw, ph = PA.SIZES_M[family]
    gap, tilt_max = LAYOUT[family]
    wander = WANDER[family]
    courses = 2 if family == "alley" and h >= ph * 1.6 else 1
    # a sheet never grows past its size; a band lower than it scales it down
    k = min(1.0, (h - wander - (ph * 0.7 if courses == 2 else 0.0)) / ph, w / pw)
    sw, sh = pw * k, ph * k
    n = max(1, int((w + gap) // (sw + gap)))
    # a run the one sheet cannot fill gets two, one at each end, overlapping
    # if they must: a 1.0 m club run built one 0.46 m sheet and filled 46% of
    # its slot (Zoo's fit check allows 2 cm)
    if n == 1 and w - sw > FIT_TOL:
        n = 2
    if n == 1:
        sw = min(w, sw)
    xs = [0.0] if n == 1 else [-w / 2.0 + sw / 2.0 + i * (w - sw) / (n - 1) for i in range(n)]
    places = []
    for c in range(courses):
        for i, x in enumerate(xs):
            if courses == 2 and c == 1:
                x = x + (sw * 0.45 if i < n - 1 else -sw * 0.45)
            # the top: level for a club or a store; wandering for the others,
            # with the first sheet of the run pinned to the band's top and the
            # last to its foot, so the band is filled by construction
            # a collage's second course hangs from the foot up: its tops wander
            # in [sh, sh + wander], its feet in [0, wander]
            u = (_h(key, variant, "top", c, i) % 1000) / 1000.0
            if wander == 0.0 or (c, i) == (0, 0):
                top = h
            elif (c, i) == (courses - 1, n - 1):
                top = sh
            elif c == 1:
                top = sh + u * wander
            else:
                top = h - u * wander
            places.append((c, i, x, top))
    rows = _order(family, key, variant, len(places))
    loud = loud_sheets(len(places), key, variant)
    prims, tiles = [], {}
    tilts = []
    for j, ((c, i, x, top), row) in enumerate(zip(places, rows)):
        tile = f"p{j}"
        tiles[tile] = {"kind": "wallposter", "family": family, "row": row,
                       "w_m": round(sw, 4), "h_m": round(sh, 4), "key": f"{key}|{variant}|{j}"}
        # the club's sheets are one stock: its colour and blacklight stay
        if family != "club":
            tiles[tile]["stock"] = "loud" if j in loud else "plain"
        # LAYERS ALTERNATE, THEY DO NOT ACCUMULATE: a sheet need only stand
        # off the ones it overlaps -- its neighbours in its course, and the
        # other course. Stepped by index, a 32-sheet collage stood 12 cm off
        # the wall; this is five layers at most, 16 mm.
        # (the second course cycles THREE: its last sheet is pulled back over
        # the one two places along to reach the run's end, and by parity the
        # two shared a plane)
        y = -d / 2.0 + ((i % 2) if c == 0 else 2 + (i % 3)) * LAYER
        z0, z1 = top - sh, top
        x0, x1 = x - sw / 2.0, x + sw / 2.0
        q = _quad("PosterWall_Sheet", tile, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])
        a = 0.0
        ends = (c, i) in ((0, 0), (courses - 1, n - 1))
        if tilt_max and not ends:
            a = ((_h(key, variant, "tilt", j) % 2001) / 1000.0 - 1.0) * tilt_max
            r = P.rotate_y(q, math.radians(a), about=(x, (z0 + z1) / 2.0))
            lo, hi = P.bounds([r])
            if lo[0] >= -w / 2.0 and hi[0] <= w / 2.0 and lo[2] >= 0.0 and hi[2] <= h:
                q = r
            else:
                a = 0.0
        tilts.append(round(a, 2))
        prims.append(q)
    return {"prims": prims, "tiles": tiles, "collision": [],
            "facts": {"family": family, "sheets": len(prims), "courses": courses,
                      "sheet_m": (round(sw, 4), round(sh, 4)), "rows": rows, "tilts": tilts,
                      "loud": sorted(loud) if family != "club" else [],
                      "tris": P.tri_count(prims)}}
