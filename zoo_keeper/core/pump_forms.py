"""A 1997 two-sided mechanical gas pump: two atlases, two draws.

Zoo 1.36.0, species `pump`. The walker, 2026-09-30, after cold run 9120's
FLAPPAHS walk found the forecourt's six pumps were the 2026-09-12 placeholder
box: "pumps first". Until this the species was one grey box.

THE REFERENCE (docs/proposals/GAS_STATION_SHOP.md, the walker's close-up):
"three grades in separate colour-coded bodies (silver, red, gold), each with
a MECHANICAL PRICE WHEEL showing dollars-per-gallon to the nine-tenths ...
above a smaller wheel for the sale. Coiled black hose, nozzle in a holster
on the face, a stencilled 'UNLEADED GASOLINE' plate, grade buttons along the
front". A digital display would date the forecourt a decade wrong; the 9/10
is the detail that reads as 1997.

WHAT IS BUILT (metres, Z up, origin at the floor's centre). A pump is
two-sided -- a car fuels at either lane -- so its FACES ARE ITS TWO LONG
SIDES, whichever axis that is: DC's gas stations author the slot 1.0 x 1.2
(the island runs along Y, the lanes either side in X) and Lot's rotated
sites hand Zoo the same pump as 1.2 x 1.0. Both put the faces on the lanes.
From the bottom:

  base     a dark steel base frame, the slot's full footprint;
  body     three grade PANELS a face, silver / red / gold, each with a
           recessed window on its price wheels, the grade's name, the
           stencilled plate, the grade button and a louvred door;
  nozzle   a holster boot on each panel, the nozzle in it, and a black hose
           hung in a loop from the nozzle's butt back into the body;
  header   the store's name, FLAPPAHS, lit on both faces.

Both faces are built once and turned 180 degrees, so each viewer reads
REGULAR, PLUS, SUPER left to right and no text is mirrored.

TWO ATLASES, TWO MATERIALS, TWO DRAWS (CLAUDE.md: colour-only variation is
texture, never material). PAINT -- the panels, the base, the hose, the
nozzles -- is lit by the scene. GLOW -- the price windows and the header,
backlit as a 1997 pump's computer face and canopy-height header were -- is
its own light (`materials.make_backlit_material`), named `_Face` so Lux's
power cut takes it.

THE PRICES ARE THE PYLON'S. Grades, colours, brand and price sets come from
`price_pylon_forms`, by the same variant, so the pump a driver pulls up to
agrees with the sign that brought them in.
"""
from __future__ import annotations

import math

from . import prims as P
from . import price_pylon_forms as PY
from .vending_forms import Canvas

#: Heights as fractions of the slot's, from a 1.4 m unit.
BASE = 0.06
HEADER = 0.80              # the header's underside
#: The window on the price wheels, as fractions of a panel (its width; its
#: height from the panel's foot).
WIN_W = 0.78
WIN_Z = (0.64, 0.94)
WELL = 0.015               # the window's recess behind its panel
#: The holster, from the panel's foot (fractions of its height), and its
#: size in metres. Low enough that the nozzle in it stands below the plate.
HOLSTER_Z = (0.22, 0.37)
HOLSTER_W, HOLSTER_D = 0.09, 0.07
NOZZLE_W, NOZZLE_H = 0.056, 0.06
REACH_MAX = 0.24           # how far a nozzle stands out of its face
HOSE_R = 0.016             # half the hose's square section
HOSE_N = 14                # segments in one hose, evenly spaced along it
OUTLET_W = 0.044           # the fitting the hose goes into, square, on the face
OUTLET_D = 0.05
HOSE_LANE = 0.16           # the panel's outer strip the hose climbs, of its width
#: The body's thickness between its faces: half the slot's short side,
#: within what a dispenser is.
BODY_T = (0.25, 0.6)
BODY = (214, 214, 206)     # the body's ends, a cream enamel
BASE_RGB = (96, 98, 100)   # the base frame: galvanised, not a black slab
TRIM = (34, 34, 38)
HOSE = (16, 16, 18)
STEEL = (150, 152, 156)
#: The sale wheel, by grade: what the last customer bought.
SALES = ("12.40", "07.15", "20.00")
PLATE = ("UNLEADED", "GASOLINE")
BUTTON = "PUSH"
#: The backlit glow: emission and the diffuse copy, as the ATM's.
GLOW_EMISSION = 1.0
GLOW_ALBEDO = 0.6
TEXEL = 256


def _quad(part, mat, tile, verts, uv=(0.0, 1.0, 0.0, 1.0)):
    """One textured quad, corners bottom-left, bottom-right, top-right,
    top-left as its viewer sees it (so it faces the viewer); ``uv`` the part
    of its tile it shows."""
    p = P.mesh(part, mat, verts, [(0, 1, 2, 3)])
    u0, u1, v0, v1 = uv
    p["tile"] = tile
    p["uvs"] = [((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
    return p


def _box(part, mat, tile, lo, hi, skip=()):
    """A box whose faces all show ``tile`` whole; ``skip`` names faces that
    something else covers, so none is doubled."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    faces = {
        "front": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        "back": [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
        "left": [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
        "right": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        "top": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        "bottom": [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
    }
    return [_quad(f"{part}_{k}", mat, tile, v) for k, v in faces.items() if k not in skip]


def resample(path, n):
    """``n + 1`` points on the polyline ``path``, EVENLY SPACED ALONG IT."""
    run = [0.0]
    for q, r in zip(path, path[1:]):
        run.append(run[-1] + math.dist(q, r))
    out, j = [], 0
    for i in range(n + 1):
        want = run[-1] * i / n
        while j < len(run) - 2 and run[j + 1] < want:
            j += 1
        f = 0.0 if run[j + 1] == run[j] else min(1.0, (want - run[j]) / (run[j + 1] - run[j]))
        out.append(tuple(path[j][k] + f * (path[j + 1][k] - path[j][k]) for k in range(3)))
    return out


def hang(x0, x1, z_top0, z_low, z_top1, p0, p1, fy, steps=64):
    """The hose's path on a -Y face: down from (x0, z_top0), round a
    semicircle at ``z_low`` to x1, and up to z_top1; standing out of the face
    by p0 at the start and p1 at the end, linearly along it.

    A single cubic was the first cut and it was wrong twice: sampled evenly in
    its parameter, the loop's bottom drew a 3.5 cm segment turning 69 degrees
    -- a tube's width -- and folded the tube through itself; resampled evenly
    along it, the same curve had a CUSP (121 degrees in one ring), which no
    sampling mends. A hanging hose is a U: two legs and the bend between."""
    R = (x1 - x0) / 2.0
    cx, cz = x0 + R, z_low + R
    xz = [(x0, z_top0 + (cz - z_top0) * i / steps) for i in range(steps)]
    xz += [(cx + R * math.cos(math.pi + math.pi * i / steps), cz + R * math.sin(math.pi + math.pi * i / steps))
           for i in range(steps + 1)]
    xz += [(x1, cz + (z_top1 - cz) * i / steps) for i in range(1, steps + 1)]
    run = [0.0]
    for q, r in zip(xz, xz[1:]):
        run.append(run[-1] + math.dist(q, r))
    return [(x, fy - (p0 + (p1 - p0) * L / run[-1]), z) for (x, z), L in zip(xz, run)]


def _norm(v):
    L = math.sqrt(sum(c * c for c in v))
    return tuple(c / L for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def tube(part, mat, tile, pts, r):
    """A square-section tube along ``pts``, capped at both ends, its sides
    facing out. The section is kept square to the path's tangent, one pair
    of sides facing along X. ``pts`` must never run along X."""
    rings = []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        t = _norm(tuple(b[k] - a[k] for k in range(3)))
        # the section's side: X with the tangent taken out. `t x X` was the
        # first cut, and it flips sign where the loop turns from falling to
        # rising, so the tube twisted shut at the bottom of the loop (caught
        # by `test_every_face_points_out_of_its_part`). A path that never
        # runs along X cannot flip this one.
        s = _norm(tuple((1.0 if k == 0 else 0.0) - t[0] * t[k] for k in range(3)))
        u = _cross(s, t)
        rings.append([tuple(p[k] + r * (cs * s[k] + cu * u[k]) for k in range(3))
                      for cs, cu in ((1, 1), (-1, 1), (-1, -1), (1, -1))])
    verts = [v for ring in rings for v in ring]
    faces, uvs = [], []
    n = len(rings)
    for i in range(n - 1):
        for k in range(4):
            a, b = i * 4 + k, i * 4 + (k + 1) % 4
            faces.append((a, b, b + 4, a + 4))
            uvs.append(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)))
    faces.append((3, 2, 1, 0))
    faces.append(tuple((n - 1) * 4 + k for k in range(4)))
    uvs += [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))] * 2
    # the winding above faces each side INTO the tube or out depending on
    # the ring's handedness; settle it on the first side and flip all if in
    c = rings[0]
    mid = tuple(sum(v[k] for v in c) / 4 for k in range(3))
    f = faces[0]
    v0, v1, v2 = verts[f[0]], verts[f[1]], verts[f[2]]
    nrm = _cross(tuple(v1[k] - v0[k] for k in range(3)), tuple(v2[k] - v0[k] for k in range(3)))
    fc = tuple((v0[k] + verts[f[2]][k]) / 2 for k in range(3))
    if sum(nrm[k] * (fc[k] - mid[k]) for k in range(3)) < 0:
        faces = [tuple(reversed(f)) for f in faces]
        uvs = [tuple(reversed(q)) for q in uvs]
    p = P.mesh(part, mat, verts, faces)
    p["tile"] = tile
    p["uvs"] = uvs
    return p


def _turn(p, quarter):
    """``p`` turned ``quarter`` x 90 degrees about Z (a rotation: windings,
    and so normals and which way a face's art reads, are kept)."""
    q = dict(p)
    vs = p["verts"]
    for _ in range(quarter % 4):
        vs = [(-y, x, z) for x, y, z in vs]
    q["verts"] = vs
    return q


def lane_at(pw):
    """The hose's centre in from its panel's outer edge: half the lane, and
    never so near the edge that the hose meets the body's end (the first cut
    put it there at a 0.6 m slot: a face shared with the body)."""
    return max(pw * HOSE_LANE / 2.0, OUTLET_W / 2 + 0.008)


def _face(W, TB, T, H, zb, zh, prices, side):
    """Everything on one face, built on the -Y face: the viewer stands at
    -Y and reads left to right along +X."""
    fy = -TB / 2.0
    reach = max(0.05, min(REACH_MAX, (T - TB) / 2.0 - 0.01))
    ph = zh - zb
    pw = W / len(PY.GRADES)
    out = []
    for i, (grade, _rgb) in enumerate(PY.GRADES):
        g = f"Pump_{side}{i}"
        ax0, ax1 = -W / 2.0 + i * pw, -W / 2.0 + (i + 1) * pw
        ac = (ax0 + ax1) / 2.0
        wx0, wx1 = ac - pw * WIN_W / 2.0, ac + pw * WIN_W / 2.0
        wz0, wz1 = zb + ph * WIN_Z[0], zb + ph * WIN_Z[1]
        tile = f"panel{i}"
        uw0, uw1 = (wx0 - ax0) / pw, (wx1 - ax0) / pw
        # the panel, cut round its window: four strips, each showing its
        # part of the panel's tile
        out += [
            _quad(f"{g}_PanelB", "paint", tile, [(ax0, fy, zb), (ax1, fy, zb), (ax1, fy, wz0), (ax0, fy, wz0)],
                  (0.0, 1.0, 0.0, WIN_Z[0])),
            _quad(f"{g}_PanelT", "paint", tile, [(ax0, fy, wz1), (ax1, fy, wz1), (ax1, fy, zh), (ax0, fy, zh)],
                  (0.0, 1.0, WIN_Z[1], 1.0)),
            _quad(f"{g}_PanelL", "paint", tile, [(ax0, fy, wz0), (wx0, fy, wz0), (wx0, fy, wz1), (ax0, fy, wz1)],
                  (0.0, uw0, WIN_Z[0], WIN_Z[1])),
            _quad(f"{g}_PanelR", "paint", tile, [(wx1, fy, wz0), (ax1, fy, wz0), (ax1, fy, wz1), (wx1, fy, wz1)],
                  (uw1, 1.0, WIN_Z[0], WIN_Z[1])),
        ]
        yi = fy + WELL
        # the window's walls face INTO the hole (the ATM's first cut wound
        # them out), and the wheels behind it glow
        out += [
            _quad(f"{g}_Well_B", "paint", "trim", [(wx0, fy, wz0), (wx1, fy, wz0), (wx1, yi, wz0), (wx0, yi, wz0)]),
            _quad(f"{g}_Well_T", "paint", "trim", [(wx0, yi, wz1), (wx1, yi, wz1), (wx1, fy, wz1), (wx0, fy, wz1)]),
            _quad(f"{g}_Well_L", "paint", "trim", [(wx0, fy, wz0), (wx0, yi, wz0), (wx0, yi, wz1), (wx0, fy, wz1)]),
            _quad(f"{g}_Well_R", "paint", "trim", [(wx1, yi, wz0), (wx1, fy, wz0), (wx1, fy, wz1), (wx1, yi, wz1)]),
            _quad(f"{g}_Dial", "glow", f"dial{i}", [(wx0, yi, wz0), (wx1, yi, wz0), (wx1, yi, wz1), (wx0, yi, wz1)]),
        ]
        # the holster boot, open to the face behind it
        hz0, hz1 = zb + ph * HOLSTER_Z[0], zb + ph * HOLSTER_Z[1]
        hd = min(HOLSTER_D, reach * 0.5)
        out += _box(f"{g}_Holster", "paint", "trim", (ac - HOLSTER_W / 2, fy - hd, hz0),
                    (ac + HOLSTER_W / 2, fy, hz1), skip=("back",))
        # the nozzle: its spout down in the boot, its body standing out of
        # the face, the trigger guard under the body's outer half
        nz0 = hz1 + 0.01
        nz1 = nz0 + NOZZLE_H
        ny1 = fy - reach                             # the butt, where the hose goes in
        out += _box(f"{g}_Spout", "paint", "steel", (ac - 0.015, fy - hd * 0.75, hz1 - 0.06),
                    (ac + 0.015, fy - hd * 0.30, nz0 + 0.02))
        out += _box(f"{g}_Nozzle", "paint", "steel", (ac - NOZZLE_W / 2, ny1, nz0),
                    (ac + NOZZLE_W / 2, fy - hd * 0.15, nz1))
        out += _box(f"{g}_Guard", "paint", "trim", (ac - 0.02, ny1 + reach * 0.2, nz0 - 0.045),
                    (ac + 0.02, fy - reach * 0.55, nz0 + 0.02), skip=("top",))
        # the hose: out of the nozzle's butt, down, round a U at the island
        # and back up the panel's outer edge (`HOSE_LANE`: the art keeps its
        # words out of that strip) into its fitting under the window, which
        # hides its end. It stands no further out than the butt, so the loop
        # keeps inside the slot, and comes in to just off the face.
        xo, zo = ax1 - lane_at(pw), wz0 - OUTLET_W / 2 - 0.02
        low = zb + max(0.06, ph * 0.06)
        pts = resample(hang(ac, xo, (nz0 + nz1) / 2, low, zo, reach - 0.012, HOSE_R + 0.012, fy), HOSE_N)
        out.append(tube(f"{g}_Hose", "paint", "hose", pts, HOSE_R))
        out += _box(f"{g}_Outlet", "paint", "steel", (xo - OUTLET_W / 2, fy - OUTLET_D, zo - OUTLET_W / 2),
                    (xo + OUTLET_W / 2, fy, zo + OUTLET_W / 2), skip=("back",))
    # the header's face: the store's name, lit
    out.append(_quad(f"Pump_{side}_Header", "glow", "header",
                     [(-W / 2, fy, zh), (W / 2, fy, zh), (W / 2, fy, H), (-W / 2, fy, H)]))
    return out


def plan(w, d, h, variant=0):
    """``{"prims", "tiles", "collision", "facts"}``: prims carry ``mat``
    "paint" or "glow" and a ``tile``; ``tiles`` maps each tile to its
    ``(atlas, spec)``. The faces are the two long sides."""
    v = int(variant) % len(PY.PRICE_SETS)
    turned = d > w                                   # the faces on +-X
    W, T, H = (d, w, h) if turned else (w, d, h)
    TB = max(BODY_T[0], min(BODY_T[1], T * 0.5, T - 0.1))
    zb, zh = h * BASE, h * HEADER
    prices = PY.PRICE_SETS[v]
    prims = []
    prims += _box("Pump_Base", "paint", "base", (-W / 2, -T / 2, 0.0), (W / 2, T / 2, zb), skip=("bottom",))
    prims += _box("Pump_Body", "paint", "body", (-W / 2, -TB / 2, zb), (W / 2, TB / 2, zh),
                  skip=("front", "back", "bottom", "top"))
    prims += _box("Pump_HeaderBox", "paint", "trim", (-W / 2, -TB / 2, zh), (W / 2, TB / 2, H),
                  skip=("front", "back", "bottom"))
    front = _face(W, TB, T, H, zb, zh, prices, "A")
    prims += front + [_turn(p, 2) | {"part": p["part"].replace("Pump_A", "Pump_B", 1)} for p in front]
    if turned:
        prims = [_turn(p, 1) for p in prims]
    pw = W / len(PY.GRADES)
    ph = zh - zb
    tiles = {
        "body": ("paint", {"kind": "pump_flat", "rgb": BODY, "w_m": 0.08, "h_m": 0.08}),
        "trim": ("paint", {"kind": "pump_flat", "rgb": TRIM, "w_m": 0.08, "h_m": 0.08}),
        "base": ("paint", {"kind": "pump_flat", "rgb": BASE_RGB, "w_m": 0.08, "h_m": 0.08}),
        "hose": ("paint", {"kind": "pump_flat", "rgb": HOSE, "w_m": 0.04, "h_m": 0.04}),
        "steel": ("paint", {"kind": "pump_flat", "rgb": STEEL, "w_m": 0.04, "h_m": 0.04}),
        "header": ("glow", {"kind": "pump_header", "w_m": W, "h_m": h - zh, "variant": v}),
    }
    for i in range(len(PY.GRADES)):
        tiles[f"panel{i}"] = ("paint", {"kind": "pump_panel", "w_m": pw, "h_m": ph, "grade": i,
                                        "lane": (lane_at(pw) + OUTLET_W / 2) / pw})
        tiles[f"dial{i}"] = ("glow", {"kind": "pump_dial", "w_m": pw * WIN_W,
                                      "h_m": ph * (WIN_Z[1] - WIN_Z[0]), "grade": i, "price": prices[i]})
    lo = (-T / 2, -W / 2) if turned else (-W / 2, -T / 2)
    hb = (-TB / 2, -W / 2) if turned else (-W / 2, -TB / 2)
    collision = [((lo[0], lo[1], 0.0), (-lo[0], -lo[1], zb)),
                 ((hb[0], hb[1], zb), (-hb[0], -hb[1], h))]
    return {"prims": prims, "tiles": tiles, "collision": collision,
            "facts": {"variant": v, "prices": prices, "faces": "x" if turned else "y",
                      "body_t": TB, "tris": P.tri_count(prims), "materials": 2}}


# --- the art -----------------------------------------------------------------------------


def _px(m):
    return max(4, int(round(m * TEXEL)))


def _shade(rgb, k):
    return tuple(max(0, min(255, int(c * k))) for c in rgb)


def paint(spec):
    """One tile as a Canvas; ``c.unset`` lists every line that did not set."""
    from .poster_art import fit_text
    w, h = _px(spec["w_m"]), _px(spec["h_m"])
    kind = spec["kind"]
    if kind == "pump_flat":
        return Canvas(w, h, spec["rgb"])
    if kind == "pump_panel":
        grade, rgb = PY.GRADES[spec["grade"]]
        c = Canvas(w, h, rgb)
        dark = _shade(rgb, 0.55)
        c.rect(0, 0, w, 2, TRIM)
        c.rect(0, h - 2, w, h, TRIM)
        c.rect(0, 0, 2, h, TRIM)
        c.rect(w - 2, 0, w, h, TRIM)
        # row 0 is the panel's top: the window sits in its top third (cut
        # out of the mesh, so nothing painted there is seen)
        def band(f0, f1):
            return int(h * f0), int(h * f1)
        unset = []
        xl = int(w * (1 - spec.get("lane", HOSE_LANE)))   # the words stop at the hose's lane
        y0, y1 = band(1 - WIN_Z[0] + 0.02, 1 - WIN_Z[0] + 0.10)       # the grade's name
        c.rect(4, y0, xl, y1, TRIM)
        # ONE scale for every grade's name, as the pylon's (fitted each on
        # its own, REGULAR set at half PLUS's size in the first render)
        gs = min(PY._scale(g, xl - 8, y1 - y0 - 2, "m5x7", 2) for g, _c in PY.GRADES)
        if gs < 1 or fit_text(c, grade, (6, y0 + 1, xl - 2, y1 - 1), (250, 250, 244), face="m5x7",
                              cap=gs) is None:
            unset.append(grade)
        # the stencilled plate, down to the nozzle's top (it stands over the
        # holster, `NOZZLE_H` and a centimetre above it)
        top = HOLSTER_Z[1] + (0.01 + NOZZLE_H) / spec["h_m"]
        y0, y1 = band(1 - WIN_Z[0] + 0.11, 1 - top - 0.005)
        c.rect(4, y0, xl, y1, (236, 232, 218))
        if fit_text(c, " ".join(PLATE), (5, y0 + 1, xl - 1, y1 - 1), TRIM, face="m5x7", cap=1) is None:
            unset.append(" ".join(PLATE))
        y0, y1 = band(1 - HOLSTER_Z[0] + 0.02, 1 - HOLSTER_Z[0] + 0.09)   # the grade button
        bx0, bx1 = int(w * 0.30), int(w * 0.70)
        c.rect(bx0 - 1, y0 - 1, bx1 + 1, y1 + 1, TRIM)
        c.rect(bx0, y0, bx1, y1, _shade(rgb, 1.15))
        if fit_text(c, BUTTON, (bx0 + 1, y0 + 1, bx1 - 1, y1 - 1), TRIM, face="m5x7", cap=1) is None:
            unset.append(BUTTON)
        y0, y1 = band(1 - HOLSTER_Z[0] + 0.10, 0.97)                  # the louvred door
        c.rect(6, y0, w - 6, y1, dark)
        for y in range(y0 + 3, y1 - 2, 4):
            c.rect(10, y, w - 10, y + 2, _shade(rgb, 0.35))
        c.unset = unset
        return c
    if kind == "pump_dial":
        c = Canvas(w, h, (238, 232, 212))                # the lens, lit from behind
        unset = []
        # the price wheel: dollars on black drums, the 9/10 after them
        y0, y1 = int(h * 0.08), int(h * 0.50)
        dx1 = int(w * 0.70)
        c.rect(3, y0, dx1, y1, TRIM)
        dollars, tenths = PY.price_text(spec["price"])
        if fit_text(c, dollars, (4, y0 + 1, dx1 - 1, y1 - 1), (250, 250, 244), face="m5x7", cap=3) is None:
            unset.append(dollars)
        # the nine-tenths, stacked as the wheel's face prints it: 9 over 10
        num, den = tenths.split("/")
        fx0, fx1, ym = dx1 + 2, w - 1, (y0 + y1) // 2
        c.rect(fx0 + 1, ym, fx1 - 1, ym + 1, TRIM)
        if (fit_text(c, num, (fx0, y0, fx1, ym), TRIM, face="m5x7", cap=1) is None
                or fit_text(c, den, (fx0, ym + 1, fx1, y1), TRIM, face="m5x7", cap=1) is None):
            unset.append(tenths)
        # the smaller sale wheel under it
        y0, y1 = int(h * 0.58), int(h * 0.92)
        sx0 = int(w * 0.28)
        if fit_text(c, "$", (2, y0, sx0 - 2, y1), TRIM, face="m5x7", cap=2) is None:
            unset.append("$")
        c.rect(sx0, y0, w - 4, y1, TRIM)
        sale = SALES[spec["grade"] % len(SALES)]
        if fit_text(c, sale, (sx0 + 1, y0 + 1, w - 5, y1 - 1), (250, 250, 244), face="m5x7", cap=2) is None:
            unset.append(sale)
        c.unset = unset
        return c
    if kind == "pump_header":
        field, rule, ink = PY.COLOURWAYS[int(spec.get("variant", 0)) % len(PY.COLOURWAYS)]
        c = Canvas(w, h, field)
        c.rect(0, 2, w, 5, rule)
        c.rect(0, h - 5, w, h - 2, rule)
        c.unset = [] if fit_text(c, PY.STORE, (6, 7, w - 6, h - 7), ink, face=PY.HEAD_FACE, cap=6,
                                 outline=rule) is not None else [PY.STORE]
        return c
    raise ValueError(f"pump: no tile kind {kind!r}")


def all_strings():
    out = [g for g, _rgb in PY.GRADES] + list(PLATE) + [" ".join(PLATE), BUTTON, PY.STORE]
    return out + list(SALES)
