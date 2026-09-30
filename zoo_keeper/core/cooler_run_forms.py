"""The convenience store's reach-in cooler wall, decided in pure Python: the
cabinet, the glass doors, the shelves, the fluorescent tubes, the sign band,
and every pixel of what glows behind the glass.

Zoo 1.12.0, species `cooler_run`. Asked for by name, 2026-09-28: "do the
cooler wall next", then "we also want glowing fridge lights". The reference
(docs/SET_DRESSING_REFERENCES.md, "The walker's convenience store
references", 2026-09-15): "a full back wall of glass-door reach-in coolers
(drinks, milk jugs, juice), lit from inside, with a sign band above ('ICE
COLD DRINKS' / 'BOTTLED DRINKS')".

WHERE IT STANDS. Deli Counter's `cooler_run` volume, 8.0 x 2.8 x 2.2 against
the stockroom partition in five store specs, which until this species
existed built as a plain box wearing glass; and, from Deli Counter 0.148.0,
a cooler wall on the walk-in cooler's front wall of the stores that have one.
The volume is deeper than a reach-in cabinet (2.8 m against ~0.9), so the
CABINET is the front `CAB_D` of the slot and the rest is the walk-in's plain
body behind it -- the slot is filled exactly and a body cannot walk into the
back of the doors.

WHAT IS BUILT, in the recipe frame (metres, Z up, floor 0, CENTRE pivot,
x along the run, the doors facing -Y, the wall behind at +Y):

  * the cabinet body and the walk-in body behind it, a black kick plate, a
    header box across the top;
  * DOORS, `n_doors` of them across the run: a black frame (two stiles, two
    rails), a glass pane, a vertical handle on the latch side;
  * behind each door, SHELVES in steel and a BACK PANEL whose face is the
    products, lit;
  * a FLUORESCENT TUBE down every mullion and both ends, just behind the
    glass, lit white;
  * the SIGN BAND on the header's face, one section a pair of doors
    ("ICE COLD DRINKS", "DAIRY", ...), lit.

GLOWING WITHOUT A LIGHT. The walker asked for glowing fridge lights. The
glow is emission, not light: the products, the tubes and the sign band are
ONE backlit material (`M_Cooler_<art>_Face`, so Lux's power cut takes it)
on ONE image, `glow_art`. It costs no light and nothing per mesh that the
eight-lights rule counts. Light that SPILLS onto the floor in front would
need real lights, which do cost; that is priced and offered separately, not
built here.

THREE SUBMISSIONS whatever the length: painted steel (every frame, shelf,
body and handle, colour in the `Wear` vertex colour), the glass, the glow.

NO TWO FACES SHARE A PLANE among these primitives (`prims.coincident_pairs`
is empty); every part meeting another is buried into it.
"""
from __future__ import annotations

import re
import zlib

from . import brands as BR
from . import club_names as CN
from . import pixel_type as pt
from . import prims as P
from .vending_forms import Canvas

#: Deli Counter's volume (long side first), then the genome's range.
DC_SIZES = ((8.0, 2.8, 2.2), (5.2, 0.9, 2.2))
RANGES = {"width": (1.6, 12.0), "depth": (0.7, 3.0), "height": (1.9, 2.6)}

BURY = 0.004
CAB_D = 0.90              # the reach-in cabinet's depth, at most the slot's
KICK_H = 0.12
HEADER_H = 0.30
END_POST = 0.06           # the cabinet's frame at each end of the run
DOOR_PITCH = 0.78         # a door and its share of a mullion
MULLION = 0.05
FRAME = 0.045             # a door frame's stile and rail
FRAME_T = 0.04            # a door frame's thickness
GLASS_T = 0.008
HANDLE_R = 0.012
HANDLE_OUT = 0.05         # the handle past the frame's face
INTERIOR = 0.55           # from the door plane back to the product panel
SHELVES = 5
SHELF_T = 0.018
TUBE_W = 0.024
TUBE_T = 0.014

#: Pixels a metre of the glow art: a door's panel is ~115 x ~270 px.
TEXEL = 160
SECTION_WORDS = ("ICE COLD DRINKS", "DAIRY", "BOTTLED WATER", "JUICE & TEA", "COLD SODA",
                 "COLD BEER")
DOOR_TYPES = ("soda", "cans", "milk", "juice", "beer", "water")
#: WHAT A RUN SELLS, IN ORDER (1.28.0). The walker, 2026-09-29: "there
#: should be fridges of cold sodas, beer, milk, etc, with glowing lights too".
#: Until this a section's word was drawn by hash and each door's stock by
#: another, independently, so a DAIRY sign stood over soda bottles and no
#: section sold beer. Now a run is sections of two doors, read left to right
#: off this list -- the walker's three first -- and every door carries its
#: section's stock. An 8 m run (ten doors) is soda, beer, dairy, water and
#: the canned drinks; a four-door run is soda and beer. A seed may choose among
#: approved options, never whether the sign says what is behind it.
LINEUP = ("COLD SODA", "COLD BEER", "DAIRY", "BOTTLED WATER", "ICE COLD DRINKS", "JUICE & TEA")
SECTION_STOCK = {"COLD SODA": "soda", "COLD BEER": "beer", "DAIRY": "milk",
                 "BOTTLED WATER": "water", "ICE COLD DRINKS": "cans", "JUICE & TEA": "juice"}
#: The beers are the window neon's (`club_names.WINDOW_NAMES`) -- one table
#: of invented beers, two places they are sold. (carton top, carton band)
BEER_COLOURS = {
    "WOODER ICE": ("#dff3ff", "#1b5fae"),
    "JAWN LITE": ("#f4d35e", "#ffffff"),
    "YOUSE BREW": ("#c1121f", "#1d1d1d"),
    "SHOOBIE SUDS": ("#2ec4b6", "#f7e1b5"),
    "SCRAPPLE STOUT": ("#4a2c1a", "#e9d8a6"),
    "COLD ONE HON": ("#c0c7cf", "#1f4e9c"),
}
assert set(BEER_COLOURS) == set(CN.WINDOW_NAMES), "every beer the window sells, and no other"

#: Colours (linear) and surface kind of every non-glowing part.
MATERIALS = {
    "cabinet": ((0.78, 0.79, 0.80), "metal_painted"),
    "body": ((0.60, 0.61, 0.62), "metal_painted"),
    "black": ((0.02, 0.02, 0.022), "metal_painted"),
    "shelf": ((0.70, 0.71, 0.72), "metal_painted"),
    "handle": ((0.62, 0.62, 0.63), "metal_painted"),
    "glass": ((0.80, 0.86, 0.88), "glass"),
}
KIND_BASE = {"metal_painted": (1.0, 1.0, 1.0), "glass": (0.80, 0.86, 0.88)}
GLASS_OPACITY = 0.22
#: The glow's emission and its dimmed diffuse copy
#: (`materials.make_backlit_material`). The cigarette rack's header measured
#: faint at 0.5; a cooler is lit from inside and the walker asked for it to
#: glow, so it starts at double. To be judged on the walk.
GLOW_EMISSION = 1.0
GLOW_ALBEDO = 0.6
_VARIANT = re.compile(r"_n\d+(?=_|$)")


def vertex_tint(mat_key):
    rgb, kind = MATERIALS[mat_key]
    return kind, tuple(c / b for c, b in zip(rgb, KIND_BASE[kind]))


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def resolve(plan_):
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    key = _VARIANT.sub("", module.get("stem") or "") or "cooler_run"
    return key, variant


def doors(w):
    """``(n, door_width)``: the doors across a run ``w`` wide."""
    run = w - 2.0 * END_POST
    n = max(1, int(round(run / DOOR_PITCH)))
    return n, (run - (n - 1) * MULLION) / n


def sections(n):
    """``[(word, span)]``: the run's sign sections, two doors each (a last
    odd door is its own), their words read off `LINEUP` in order."""
    out = []
    k = 0
    while k < n:
        span = 2 if k + 1 < n else 1
        out.append((LINEUP[len(out) % len(LINEUP)], span))
        k += span
    return out


def glow_face(part, x0, x1, y_front, y_back, z0, z1, region, uv_front=True):
    """A box whose -Y face maps edge to edge onto ``region`` of the glow
    image (``(region, u, v)`` corners) and whose other faces take the dark
    pixel. ``region`` names a rect in `glow_art`'s ``rects``."""
    p = P.box(part, "glow", (x0, y_front, z0), (x1, y_back, z1))

    def uv(i):
        x, _y, z = p["verts"][i]
        return (region, (x - x0) / (x1 - x0), (z - z0) / (z1 - z0))
    # P.box faces: 0 bottom, 1 top, 2 -Y, 3 +X, 4 +Y, 5 -X
    p["uvs"] = [tuple(uv(i) for i in f) if (k == 2 and uv_front) else tuple(("dark",) for _ in f)
                for k, f in enumerate(p["faces"])]
    return p


def layout(w, d, h, key="cooler_run", variant=0):
    """Every part at slot (w, d, h): ``(prims, facts)``. The module IS the
    slot's box (cabinet, walk-in body behind, header, kick)."""
    out = []
    yf = -d / 2.0                         # the slot's front plane
    cab = min(CAB_D, d)
    yb = yf + cab                         # the cabinet's back
    z_door0, z_door1 = KICK_H, h - HEADER_H
    n, dw = doors(w)
    # --- the carcass ------------------------------------------------------------
    # EVERY PART ENDS AT ITS OWN DEPTH. The first cut ran the kick, the header,
    # the end posts and the back wall all to the cabinet's back plane and the
    # header and end posts both to the front: 12-15 coincident pairs a build.
    # The header reaches the back (and the top, when there is no body behind);
    # the others stop 5, 10 and 15 mm short of it.
    body = d > cab + 1e-6
    # the kick and the header step 5 mm in from the run's ends and the body
    # 10: at the full width each shared the end posts' outer planes. The end
    # posts are what reach +/-w/2.
    out.append(P.box("Cooler_Kick", "black", (-w / 2.0 + 0.005, yf + 0.03, 0.0),
                     (w / 2.0 - 0.005, yb - 0.015, KICK_H + BURY)))
    out.append(P.box("Cooler_Header", "cabinet", (-w / 2.0 + 0.005, yf + 0.006, z_door1 - BURY),
                     (w / 2.0 - 0.005, yb, h - (0.006 if body else 0.0))))
    for s in (-1, 1):
        x0, x1 = sorted((s * w / 2.0, s * (w / 2.0 - END_POST)))
        # up 20 mm into the header: at +2 mm its top was a pair with the end stiles'
        out.append(P.box("Cooler_Cabinet", "cabinet", (x0, yf, KICK_H - BURY), (x1, yb - 0.005, z_door1 + 0.020)))
    # the cabinet's back wall, behind the product panels
    out.append(P.box("Cooler_Cabinet", "cabinet", (-w / 2.0 + END_POST - BURY, yf + INTERIOR + 0.03, KICK_H - 0.010),
                     (w / 2.0 - END_POST + BURY, yb - 0.010, z_door1 + 0.008)))
    if body:
        # the walk-in's body behind the cabinet, buried 20 mm into it; its
        # bottom 6 mm off the floor so it does not share the kick's plane
        out.append(P.box("Cooler_Body", "body", (-w / 2.0 + 0.010, yb - 0.020, 0.006), (w / 2.0 - 0.010, d / 2.0, h)))
    # --- the doors ------------------------------------------------------------------
    x = -w / 2.0 + END_POST
    # the frames' plane, set back so the HANDLES end exactly at the slot's
    # front: the first cut had them 5 cm proud of it, which fails a slot's fit
    fy0 = yf + 2.0 * HANDLE_R + HANDLE_OUT
    fy1 = fy0 + FRAME_T
    door_types = []
    # every door's stock is its section's (1.28.0)
    door_words = [w for w, span in sections(n) for _ in range(span)]
    for i in range(n):
        dx0, dx1 = x, x + dw
        # the mullion before this door (none before the first)
        if i:
            out.append(P.box("Cooler_Mullion", "black", (dx0 - MULLION - BURY, fy0 - 0.006, KICK_H - BURY),
                             (dx0 + BURY, yf + INTERIOR + 0.03 + BURY, z_door1 + 0.012)))
        # the frame: two stiles, two rails, one closed ring of four boxes
        # the run's first and last stiles bury 6 mm into the end posts rather
        # than meet them face to face
        out.append(P.box("Cooler_Door", "black", (dx0 - (0.006 if i == 0 else 0.0), fy0, z_door0),
                         (dx0 + FRAME, fy1, z_door1)))
        out.append(P.box("Cooler_Door", "black", (dx1 - FRAME, fy0, z_door0),
                         (dx1 + (0.006 if i == n - 1 else 0.0), fy1, z_door1)))
        # the rails 5 mm inside the stiles' faces: at 2 mm they were a pair
        # the rails 10 mm off the kick's top and the header's bottom
        out.append(P.box("Cooler_Door", "black", (dx0 + FRAME - BURY, fy0 + 0.005, z_door0 + 0.010),
                         (dx1 - FRAME + BURY, fy1 - 0.005, z_door0 + FRAME)))
        out.append(P.box("Cooler_Door", "black", (dx0 + FRAME - BURY, fy0 + 0.005, z_door1 - FRAME),
                         (dx1 - FRAME + BURY, fy1 - 0.005, z_door1 - 0.010)))
        # the glass, set into the frame
        gy = (fy0 + fy1) / 2.0
        out.append(P.box("Cooler_Glass", "glass", (dx0 + FRAME - 0.010, gy - GLASS_T / 2.0, z_door0 + FRAME - 0.010),
                         (dx1 - FRAME + 0.010, gy + GLASS_T / 2.0, z_door1 - FRAME + 0.010)))
        # the handle on the latch side, a bar standing off the stile
        hx = dx0 + FRAME / 2.0 if i % 2 else dx1 - FRAME / 2.0
        hz0, hz1 = z_door0 + 0.55, z_door0 + 1.15
        hy = yf + HANDLE_R                    # the bar's front touches the slot's front
        out.append(P.cyl("Cooler_Handle", "handle", (hx, hy), HANDLE_R, hz0, hz1, segments=6, phase=0.5236))
        for hz in (hz0 + 0.03, hz1 - 0.03):
            out.append(P.rod("Cooler_Handle", "handle", (hx, fy0 + 0.004, hz), (hx, hy, hz), 0.007, segments=5))
        # behind the glass: the product panel, lit, and the shelves in front of it
        py0 = yf + INTERIOR
        dt = SECTION_STOCK[door_words[i]]
        door_types.append(dt)
        # 12 mm in from each side: a mullion's face stands 4 mm past dx0
        out.append(glow_face("Cooler_Glow", dx0 + 0.012, dx1 - 0.012, py0, py0 + 0.02, z_door0 + 0.02,
                             z_door1 - 0.02, "door_" + dt))
        step = (z_door1 - z_door0 - 0.10) / SHELVES
        for k in range(SHELVES):
            sz = z_door0 + 0.06 + k * step
            out.append(P.box("Cooler_Shelf", "shelf", (dx0 + 0.02, fy1 + 0.03, sz),
                             (dx1 - 0.02, py0 + BURY, sz + SHELF_T)))
        # the tube down this door's left side, lit white (and the last one's right)
        for tx in ([dx0 + 0.010] + ([dx1 - TUBE_W - 0.010] if i == n - 1 else [])):
            out.append(glow_face("Cooler_Glow", tx, tx + TUBE_W, fy1 + 0.008, fy1 + 0.008 + TUBE_T,
                                 z_door0 + 0.03, z_door1 - 0.03, "tube"))
        x = dx1 + MULLION
    # --- the sign band: one section a pair of doors -------------------------------------
    said = []
    k = 0
    for word, span in sections(n):
        sx0 = -w / 2.0 + END_POST + k * (dw + MULLION)
        sx1 = sx0 + span * dw + (span - 1) * MULLION
        region = ("sign2_" if span == 2 else "sign1_") + str(SECTION_WORDS.index(word))
        out.append(glow_face("Cooler_Glow", sx0 + 0.01, sx1 - 0.01, yf, yf + 0.006 + BURY,
                             z_door1 + 0.04, h - 0.04, region))
        said.append((word, span))
        k += span
    facts = {"doors": n, "door_width": dw, "door_types": door_types, "sections": said,
             "cabinet_depth": cab, "collision": ((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h))}
    return out, facts


def plan(w, d, h, key="cooler_run", variant=0):
    """``{prims, facts, bounds}`` -- the slot filled exactly, the handles and
    the sign band's 6 mm proud of it at the front (recorded, not scaled)."""
    prims, facts = layout(w, d, h, key, variant)
    return {"prims": prims, "facts": facts}


def signed_volume(p):
    vs = p["verts"]
    tot = 0.0
    for f in p["faces"]:
        a = vs[f[0]]
        for k in range(1, len(f) - 1):
            b, c = vs[f[k]], vs[f[k + 1]]
            tot += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return tot / 6.0


# --- the glow ---------------------------------------------------------------------------

def _rgb(h):
    return BR.hex_rgb(h) if hasattr(BR, "hex_rgb") else tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def _shelf_row(c, x0, x1, y_top, y_bot, kind, key, row):
    """One shelf's products, faced out, standing on ``y_bot``."""
    drinks = [b for b in BR.BRANDS]
    x = x0 + 2
    i = 0
    while True:
        b = drinks[(_h(key, row, i) + i) % len(drinks)]
        top, bottom = _rgb(b["bg"][0]), _rgb(b["bg"][1])
        if kind == "soda":            # a 20 oz bottle: cap, neck, shoulder, label
            bw, bh = 9, min(34, y_bot - y_top - 3)
            if x + bw > x1 - 1: break
            c.rect(x + 3, y_bot - bh, x + 6, y_bot - bh + 3, (230, 230, 230))
            c.rect(x + 2, y_bot - bh + 3, x + 7, y_bot - bh + 8, bottom)
            c.rect(x, y_bot - bh + 8, x + bw, y_bot, bottom)
            c.rect(x, y_bot - bh + 16, x + bw, y_bot - 8, top)
            x += bw + 2
        elif kind == "cans":          # 12 oz cans, two high
            bw, bh = 8, 14
            if x + bw > x1 - 1: break
            for tier in (0, 1):
                yb = y_bot - tier * (bh + 1)
                c.rect(x, yb - bh, x + bw, yb, top)
                c.rect(x, yb - bh + 4, x + bw, yb - 4, bottom)
                c.rect(x, yb - bh, x + bw, yb - bh + 1, (210, 210, 214))
            x += bw + 1
        elif kind == "milk":          # gallon jugs: white, a coloured cap and label band
            bw, bh = 18, min(38, y_bot - y_top - 3)
            if x + bw > x1 - 1: break
            cap = ((200, 30, 30), (40, 90, 200), (230, 120, 170), (40, 150, 70))[(row + i) % 4]
            c.rect(x, y_bot - bh + 6, x + bw, y_bot, (238, 238, 232))
            c.rect(x + 11, y_bot - bh, x + 16, y_bot - bh + 6, (238, 238, 232))
            c.rect(x + 12, y_bot - bh - 2, x + 15, y_bot - bh, cap)
            c.rect(x + 1, y_bot - bh + 18, x + bw - 1, y_bot - bh + 24, cap)
            x += bw + 3
        elif kind == "beer":          # 12-pack cartons two high, then tallboys (1.28.0)
            name = CN.WINDOW_NAMES[(_h(key, "beer", row, i) + i) % len(CN.WINDOW_NAMES)]
            top, band = _rgb(BEER_COLOURS[name][0]), _rgb(BEER_COLOURS[name][1])
            if row % 2 == 0:
                bw, bh = 20, min(11, (y_bot - y_top - 3) // 2)
                if x + bw > x1 - 1: break
                for tier in (0, 1):
                    yb = y_bot - tier * (bh + 1)
                    c.rect(x, yb - bh, x + bw, yb, top)
                    c.rect(x, yb - bh + 3, x + bw, yb - bh + 6, band)
                x += bw + 2
            else:
                bw, bh = 7, min(19, y_bot - y_top - 3)
                if x + bw > x1 - 1: break
                c.rect(x, y_bot - bh, x + bw, y_bot, top)
                c.rect(x, y_bot - bh + 5, x + bw, y_bot - 5, band)
                c.rect(x, y_bot - bh, x + bw, y_bot - bh + 1, (210, 210, 214))
                x += bw + 1
        elif kind == "water":         # clear blue bottles, brand caps and labels (1.28.0)
            bw, bh = 8, min(30, y_bot - y_top - 3)
            if x + bw > x1 - 1: break
            # three brands a shelf, not one bottle stamped: `test_cooler_run`
            # read the first cut as four colours, a flat panel
            cap, band = (((30, 90, 200), (40, 110, 210)), ((236, 236, 240), (30, 150, 90)),
                         ((20, 160, 200), (220, 60, 50)))[(_h(key, "water", row, i) + i) % 3]
            c.rect(x + 2, y_bot - bh, x + 6, y_bot - bh + 3, cap)
            c.rect(x, y_bot - bh + 3, x + bw, y_bot, (170, 208, 236))
            c.rect(x, y_bot - bh + 12, x + bw, y_bot - bh + 18, (246, 248, 250))
            c.rect(x, y_bot - bh + 14, x + bw, y_bot - bh + 16, band)
            x += bw + 2
        else:                         # juice and tea: square cartons and tall bottles
            bw, bh = 11, min(30, y_bot - y_top - 3)
            if x + bw > x1 - 1: break
            c.rect(x, y_bot - bh, x + bw, y_bot, top)
            c.rect(x, y_bot - bh, x + bw, y_bot - bh + 5, bottom)
            c.rect(x + 2, y_bot - bh // 2, x + bw - 2, y_bot - bh // 2 + 4, (250, 246, 230))
            x += bw + 2
        i += 1
    # the shelf's price strip, lit from above
    c.rect(x0, y_bot, x1, y_bot + 2, (250, 250, 244))


def glow_art(door_w, door_h, key="cooler_run", variant=0):
    """ONE image for everything that glows: a panel per door type (`door_*`),
    each sign-band section at one and two doors wide (`sign1_*`, `sign2_*`),
    a white tube block, and a dark block. ``{canvas, size, rects, name,
    said}``; rects are pixel boxes, row 0 at the top."""
    DW = max(40, int(round(door_w * TEXEL)))
    DH = max(80, int(round(door_h * TEXEL)))
    S2 = int(round((2 * door_w + MULLION) * TEXEL))
    SH = int(round((HEADER_H - 0.08) * TEXEL))
    W = max(len(DOOR_TYPES) * DW, S2 + DW)
    H = DH + len(SECTION_WORDS) * SH + 8
    c = Canvas(W, H, (18, 22, 26))
    rects = {}
    said = []
    # door panels: a cold white-blue back, five shelves of product
    for j, dt in enumerate(DOOR_TYPES):
        x0 = j * DW
        c.rect(x0, 0, x0 + DW, DH, (206, 222, 236))
        step = DH / float(SHELVES)
        for k in range(SHELVES):
            y_top = int(k * step) + 2
            y_bot = int((k + 1) * step) - 4
            _shelf_row(c, x0 + 1, x0 + DW - 1, y_top, y_bot, dt, key, k)
        rects["door_" + dt] = (x0, 0, x0 + DW, DH)
    # sign sections: white letters on a coloured band, one row per word
    band_cols = ((20, 70, 160), (190, 30, 40), (20, 120, 170), (230, 120, 20), (40, 140, 60),
                 (150, 100, 20))
    for j, word in enumerate(SECTION_WORDS):
        y0 = DH + j * SH
        for span, sx0, sw in ((2, 0, S2), (1, S2, DW)):
            c.rect(sx0, y0, sx0 + sw, y0 + SH, band_cols[j])
            text = word if span == 2 or pt.ink_width(word, 1, "small_caps_bold") <= sw - 6 else word.split()[0]
            scale = 2 if pt.ink_width(text, 2, "small_caps_bold") <= sw - 8 and pt.line("small_caps_bold") * 2 <= SH - 4 else 1
            m = pt.trim(pt.render(text, scale, "small_caps_bold"))
            c.mask(m, sx0 + (sw - len(m[0])) // 2, y0 + (SH - len(m)) // 2, (252, 252, 246))
            rects[f"sign{span}_{j}"] = (sx0, y0, sx0 + sw, y0 + SH)
            said.append(text)
    ty = DH + len(SECTION_WORDS) * SH + 1
    rects["tube"] = (0, ty, 6, ty + 6)
    c.rect(*rects["tube"], (255, 255, 250))
    rects["dark"] = (10, ty, 16, ty + 6)
    c.rect(*rects["dark"], (14, 14, 16))
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "rects": rects, "said": said,
            "name": f"coolerglow_v{variant % 4}_{W}x{H}_{digest:08x}"}
