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

import numpy as np

from . import brands as BR
from . import card_art as CA
from . import club_names as CN
from . import paint as PT
from . import prims as P
from . import smooth_type as ST

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

#: Pixels a metre of the glow art. 1.12.0: 160, a door's panel ~115 x ~270
#: px, every product a few pixel rectangles. 1.51.0: 400, the real look -- a
#: door's panel ~280 x ~700 px, the products drawn in metres (`SODA`, `CAN`
#: ...) with shading, and the image sampled with filtering. Not 768 as the
#: machines are: a door is behind glass and the whole wall is one image, so
#: a 6-door run at 768 would be the largest texture in the store.
TEXEL = 400
SECTION_WORDS = ("ICE COLD DRINKS", "DAIRY", "SPORTS DRINKS", "JUICE & TEA", "COLD SODA",
                 "COLD BEER")
DOOR_TYPES = ("soda", "cans", "milk", "juice", "beer", "sports")
#: WHAT A RUN SELLS, IN ORDER (1.28.0). The walker, 2026-09-29: "there
#: should be fridges of cold sodas, beer, milk, etc, with glowing lights too".
#: Until this a section's word was drawn by hash and each door's stock by
#: another, independently, so a DAIRY sign stood over soda bottles and no
#: section sold beer. Now a run is sections of two doors, read left to right
#: off this list -- the walker's three first -- and every door carries its
#: section's stock. A seed may choose among approved options, never whether
#: the sign says what is behind it.
#:
#: THE ORDER IS THE WALKER'S (1.29.0), 2026-09-29: "Bottled water wasn't
#: really a thing in the 1990s in USA ... so we should prioritize, soda,
#: gatorade (sports drink), milk, beer". BOTTLED WATER is gone, word and door
#: alike; SPORTS DRINKS takes its place. An 8 m run (ten doors) is soda,
#: sports drinks, dairy, beer and the canned drinks; a four-door run is soda
#: and sports drinks.
LINEUP = ("COLD SODA", "SPORTS DRINKS", "DAIRY", "COLD BEER", "ICE COLD DRINKS", "JUICE & TEA")
SECTION_STOCK = {"COLD SODA": "soda", "SPORTS DRINKS": "sports", "DAIRY": "milk",
                 "COLD BEER": "beer", "ICE COLD DRINKS": "cans", "JUICE & TEA": "juice"}
#: A sports drink's colours are the liquid's, through a clear bottle: fruit
#: punch, orange, lemon-lime, a cool blue, grape (the walker's reference: a
#: 20 oz bottle, orange cap, the liquid showing, a dark label with a bolt).
SPORTS_LIQUIDS = ((220, 30, 40), (250, 140, 20), (200, 230, 40), (40, 120, 230), (130, 50, 170))
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


def _lift(rgb, by):
    return tuple(max(0.0, min(255.0, c + by)) for c in rgb)


def _px(m):
    return int(round(m * TEXEL))


#: WHOSE VOICE (1.51.0). A 12-pack's name is the brewer's: each invented beer
#: in its own face, as the cigarette and candy makers have. The sign band is
#: the store's, in the shop's face.
BEER_FACES = {
    "WOODER ICE": "aileron_bold", "JAWN LITE": "highway_bold", "YOUSE BREW": "oldstyle_bold",
    "SHOOBIE SUDS": "oldstyle_italic", "SCRAPPLE STOUT": "oldstyle_bold", "COLD ONE HON": "vegur_bold",
}

#: Products, in METRES (1.51.0; until then every one was a pixel count at
#: 160 px/m): (width, height). A 20 oz bottle, a 12 oz can, a gallon jug, a
#: half-gallon carton, a 12-pack, a tallboy, a long-neck, a sports bottle, a
#: juice carton.
SODA = (0.070, 0.230)
CAN = (0.066, 0.122)
JUG = (0.150, 0.260)
CARTON = (0.095, 0.245)
TWELVE = (0.270, 0.130)
TALLBOY = (0.070, 0.160)
LONGNECK = (0.060, 0.235)
SPORTS = (0.070, 0.210)
JUICE = (0.090, 0.200)
#: A facing is this many of one product side by side: a shelf is stocked
#: by the case, and a case is one drink.
FACING = 3


def _stand(im, box, rgb, radius=2.0, shadow=0.45):
    """A product's body: its shadow on the panel, the body, graded as a
    round thing is -- lit from the sides, where the tubes are -- and its
    far edge in shade."""
    x0, y0, x1, y1 = box
    im.rrect((x0 + 2, y0 + 3, x1 + 3, y1 + 2), radius, (0, 0, 0), shadow)
    im.rrect(box, radius, rgb)
    im.vgrad((x0 + 1, y0 + 1, x1 - 1, y1 - 1), _lift(rgb, 10), _lift(rgb, -18))
    im.rect((x0, y0, x0 + 1.5, y1), (255, 255, 255), 0.22)
    im.rect((x1 - 2, y0, x1, y1), (0, 0, 0), 0.22)


def _soda(im, x, yb, b):
    w, h = _px(SODA[0]), _px(SODA[1])
    top, bottom = _rgb(b["bg"][0]), _rgb(b["bg"][1])
    # cap, neck, shoulder, body
    im.rrect((x + w * 0.36, yb - h, x + w * 0.64, yb - h * 0.9), 1.5, (236, 236, 232))
    im.rrect((x + w * 0.3, yb - h * 0.9, x + w * 0.7, yb - h * 0.72), 2, bottom)
    _stand(im, (x, yb - h * 0.72, x + w, yb), bottom, w * 0.18, 0.4)
    im.vgrad((x + 1, yb - h * 0.71, x + w - 1, yb - 1), _lift(bottom, 12), _lift(bottom, -16))
    # the label, in the brand's colours
    im.rect((x, yb - h * 0.48, x + w, yb - h * 0.16), top)
    im.rect((x, yb - h * 0.34, x + w, yb - h * 0.30), bottom, 0.5)
    im.rect((x, yb - h * 0.72, x + 1.5, yb), (255, 255, 255), 0.22)
    im.rect((x + w - 2, yb - h * 0.72, x + w, yb), (0, 0, 0), 0.25)
    return w


def _can(im, x, yb, b, tier):
    w, h = _px(CAN[0]), _px(CAN[1])
    top, bottom = _rgb(b["bg"][0]), _rgb(b["bg"][1])
    y = yb - tier * (h + 2)
    _stand(im, (x, y - h, x + w, y), top, 2, 0.4)
    im.vgrad((x + 1, y - h + 1, x + w - 1, y - 1), _lift(top, 12), _lift(top, -16))
    im.rect((x, y - h * 0.68, x + w, y - h * 0.30), bottom)
    im.rect((x, y - h, x + w, y - h + 2), (214, 214, 218))             # the rim
    im.rect((x, y - h, x + 1.5, y), (255, 255, 255), 0.22)
    return w


def _jug(im, x, yb, cap):
    w, h = _px(JUG[0]), _px(JUG[1])
    white = (240, 240, 234)
    _stand(im, (x, yb - h * 0.78, x + w, yb), white, w * 0.1, 0.4)
    im.vgrad((x + 1, yb - h * 0.77, x + w - 1, yb - 1), (246, 246, 240), (214, 214, 206))
    im.rrect((x + w * 0.58, yb - h, x + w * 0.86, yb - h * 0.76), 2, white)   # the neck
    im.rrect((x + w * 0.6, yb - h - 3, x + w * 0.84, yb - h + 1), 2, cap)       # the cap
    im.rrect((x + w * 0.12, yb - h * 0.72, x + w * 0.42, yb - h * 0.5), 3, (150, 150, 146))  # the handle's hole
    im.rect((x + 1, yb - h * 0.42, x + w - 1, yb - h * 0.24), cap)              # the label band
    im.rect((x, yb - h * 0.78, x + 1.5, yb), (255, 255, 255), 0.25)
    return w


def _carton(im, x, yb, strip, ink):
    w, h = _px(CARTON[0]), _px(CARTON[1])
    _stand(im, (x, yb - h * 0.8, x + w, yb), (246, 244, 238), 1, 0.4)
    im.vgrad((x + 1, yb - h * 0.79, x + w - 1, yb - 1), (246, 244, 238), (222, 220, 212))
    im.rect((x + w * 0.12, yb - h * 0.9, x + w * 0.88, yb - h * 0.8), (232, 230, 224))   # the gable
    im.rect((x + w * 0.3, yb - h, x + w * 0.7, yb - h * 0.9), (226, 222, 216))           # the fin
    im.rect((x + 1, yb - h * 0.76, x + w - 1, yb - h * 0.7), strip)
    im.rect((x, yb - h * 0.6, x + w, yb - h * 0.42), ink)
    return w


def _twelve(im, x, yb, name, tier):
    w, h = _px(TWELVE[0]), _px(TWELVE[1])
    top, band = _rgb(BEER_COLOURS[name][0]), _rgb(BEER_COLOURS[name][1])
    y = yb - tier * (h + 2)
    _stand(im, (x, y - h, x + w, y), top, 1.5, 0.5)
    im.vgrad((x + 1, y - h + 1, x + w - 1, y - 1), _lift(top, 10), _lift(top, -14))
    im.rect((x, y - h * 0.78, x + w, y - h * 0.62), band)
    ink = (250, 250, 244) if sum(top) < 420 else (24, 24, 28)
    im.text(name, (x + 6, y - h * 0.58, x + w - 6, y - h * 0.12), ink, BEER_FACES.get(name, "highway_bold"))
    return w


def _tallboy(im, x, yb, name):
    w, h = _px(TALLBOY[0]), _px(TALLBOY[1])
    top, band = _rgb(BEER_COLOURS[name][0]), _rgb(BEER_COLOURS[name][1])
    _stand(im, (x, yb - h, x + w, yb), top, 2, 0.4)
    im.vgrad((x + 1, yb - h + 1, x + w - 1, yb - 1), _lift(top, 12), _lift(top, -16))
    im.rect((x, yb - h * 0.7, x + w, yb - h * 0.3), band)
    im.rect((x, yb - h, x + w, yb - h + 2), (214, 214, 218))
    return w


def _longneck(im, x, yb, name):
    w, h = _px(LONGNECK[0]), _px(LONGNECK[1])
    glass = ((40, 110, 50), (120, 70, 25))[_h("glass", name) % 2]
    im.rrect((x + w * 0.3, yb - h - 2, x + w * 0.7, yb - h + 1), 1.5, (200, 170, 90))      # the crown
    im.rrect((x + w * 0.32, yb - h, x + w * 0.68, yb - h * 0.68), 2, glass)                 # the neck
    _stand(im, (x, yb - h * 0.68, x + w, yb), glass, w * 0.3, 0.4)
    im.vgrad((x + 1, yb - h * 0.67, x + w - 1, yb - 1), _lift(glass, 14), _lift(glass, -14))
    im.rect((x, yb - h * 0.5, x + w, yb - h * 0.2), (236, 226, 196))                         # the label
    im.rect((x + 1, yb - h * 0.42, x + w - 1, yb - h * 0.34), _rgb(BEER_COLOURS[name][1]))
    im.rect((x, yb - h * 0.68, x + 1.5, yb), (255, 255, 255), 0.25)
    return w


def _sports(im, x, yb, liquid):
    w, h = _px(SPORTS[0]), _px(SPORTS[1])
    im.rrect((x + w * 0.3, yb - h, x + w * 0.7, yb - h * 0.88), 2, (240, 120, 20))          # the cap
    im.rrect((x + w * 0.2, yb - h * 0.88, x + w * 0.8, yb - h * 0.74), 2, liquid)
    _stand(im, (x, yb - h * 0.74, x + w, yb), liquid, w * 0.2, 0.4)
    im.vgrad((x + 1, yb - h * 0.73, x + w - 1, yb - 1), _lift(liquid, 20), _lift(liquid, -20))
    im.rect((x, yb - h * 0.5, x + w, yb - h * 0.2), (24, 96, 44))                           # the label
    im.rect((x + w * 0.38, yb - h * 0.44, x + w * 0.62, yb - h * 0.26), (250, 130, 20))       # the bolt
    im.rect((x, yb - h * 0.74, x + 1.5, yb), (255, 255, 255), 0.3)
    return w


def _juice(im, x, yb, b):
    w, h = _px(JUICE[0]), _px(JUICE[1])
    top, bottom = _rgb(b["bg"][0]), _rgb(b["bg"][1])
    _stand(im, (x, yb - h, x + w, yb), top, 1, 0.4)
    im.vgrad((x + 1, yb - h + 1, x + w - 1, yb - 1), _lift(top, 10), _lift(top, -14))
    im.rect((x, yb - h, x + w, yb - h * 0.82), bottom)
    im.rrect((x + w * 0.18, yb - h * 0.6, x + w * 0.82, yb - h * 0.36), 2, (250, 246, 230))
    return w


def _shelf_row(im, x0, x1, y_top, y_bot, kind, key, row):
    """One shelf's products, faced out, standing on ``y_bot``: a case of one
    drink at a time (`FACING` side by side), as a shelf is stocked."""
    drinks = list(BR.BRANDS)
    x = x0 + 3
    i = 0
    gap = max(2, _px(0.008))
    while True:
        slot = i // FACING
        b = drinks[(_h(key, row, slot) + slot) % len(drinks)]
        if kind == "soda":
            w = _px(SODA[0])
            if x + w > x1 - 2: break
            _soda(im, x, y_bot, b)
        elif kind == "cans":
            w = _px(CAN[0])
            if x + w > x1 - 2: break
            for tier in (0, 1):
                _can(im, x, y_bot, b, tier)
        elif kind == "milk" and row % 2 == 1:
            w = _px(CARTON[0])
            if x + w > x1 - 2: break
            ink, strip = (((200, 30, 40), (30, 70, 170)),
                          ((30, 70, 170), (200, 30, 40)))[(_h(key, "carton", row, slot)) % 2]
            _carton(im, x, y_bot, strip, ink)
        elif kind == "milk":
            w = _px(JUG[0])
            if x + w > x1 - 2: break
            cap = ((200, 30, 30), (40, 90, 200), (230, 120, 170), (40, 150, 70))[(row + slot) % 4]
            _jug(im, x, y_bot, cap)
        elif kind == "beer":
            name = CN.WINDOW_NAMES[(_h(key, "beer", row, slot) + slot) % len(CN.WINDOW_NAMES)]
            if row % 3 == 2:
                w = _px(LONGNECK[0])
                if x + w > x1 - 2: break
                _longneck(im, x, y_bot, name)
            elif row % 3 == 0:
                w = _px(TWELVE[0])
                if x + w > x1 - 2: break
                for tier in (0, 1):
                    _twelve(im, x, y_bot, name, tier)
            else:
                w = _px(TALLBOY[0])
                if x + w > x1 - 2: break
                _tallboy(im, x, y_bot, name)
        elif kind == "sports":
            w = _px(SPORTS[0])
            if x + w > x1 - 2: break
            liquid = SPORTS_LIQUIDS[(_h(key, "sports", row, slot) + slot) % len(SPORTS_LIQUIDS)]
            _sports(im, x, y_bot, liquid)
        else:
            w = _px(JUICE[0])
            if x + w > x1 - 2: break
            _juice(im, x, y_bot, b)
        x += w + gap
        i += 1
    # the shelf: a wire shelf's front edge, and its price strip, lit from above
    im.rect((x0, y_bot, x1, y_bot + _px(0.006)), (250, 250, 244))
    im.rect((x0, y_bot + _px(0.006), x1, y_bot + _px(0.009)), (120, 124, 128))


def _door_panel(dt, DW, DH, key):
    """One door's interior: the lit back panel, brightest at its sides where
    the tubes are, five shelves of product, each shelf's underside in shade."""
    im = PT.Img(DW, DH, (206, 222, 236))
    im.vgrad((0, 0, DW, DH), (214, 228, 240), (196, 212, 228))
    u = (np.arange(DW, dtype=np.float32) + 0.5) / DW
    im.shade((0, 0, DW, DH), np.tile((0.80 + 0.20 * np.abs(2.0 * u - 1.0))[None, :], (DH, 1)))
    step = DH / float(SHELVES)
    for k in range(SHELVES):
        y_top = int(k * step) + 2
        y_bot = int((k + 1) * step) - 4
        # the shelf above keeps the head of this bay in its shade
        im.rect((0, y_top, DW, y_top + step * 0.08), (0, 0, 0), 0.3)
        _shelf_row(im, 1, DW - 1, y_top, y_bot, dt, key, k)
    return im.to_canvas()


def glow_art(door_w, door_h, key="cooler_run", variant=0):
    """ONE image for everything that glows: a panel per door type (`door_*`),
    each sign-band section at one and two doors wide (`sign1_*`, `sign2_*`),
    a white tube block, and a dark block -- packed with a gutter each tile
    bleeds into, because the image is sampled with filtering (1.51.0).
    ``{canvas, size, rects, name, said, unset}``; rects are pixel boxes,
    row 0 at the top."""
    DW = max(40, int(round(door_w * TEXEL)))
    DH = max(80, int(round(door_h * TEXEL)))
    S2 = int(round((2 * door_w + MULLION) * TEXEL))
    SH = int(round((HEADER_H - 0.08) * TEXEL))
    tiles, said, unset = [], [], []
    for dt in DOOR_TYPES:
        c = _door_panel(dt, DW, DH, key)
        unset += c.unset
        tiles.append(("door_" + dt, c))
    # sign sections: white letters on a coloured band, in the shop's face
    band_cols = ((20, 70, 160), (190, 30, 40), (0, 130, 110), (230, 120, 20), (40, 140, 60),
                 (150, 100, 20))
    face = ST.owned("shop")
    for j, word in enumerate(SECTION_WORDS):
        for span, sw in ((2, S2), (1, DW)):
            im = PT.Img(sw, SH, band_cols[j])
            im.vgrad((0, 0, sw, SH), _lift(band_cols[j], 24), _lift(band_cols[j], -12))
            text = word if span == 2 or ST.fit_cap(word, sw - 10, int(SH * 0.5), face, 8) else word.split()[0]
            im.text(text, (5, SH * 0.15, sw - 5, SH * 0.85), (252, 252, 246), face, shadow=_lift(band_cols[j], -60))
            im.vignette((0, 0, sw, SH), 0.22)
            c = im.to_canvas()
            unset += c.unset
            tiles.append((f"sign{span}_{j}", c))
            said.append(text)
    tiles.append(("tube", PT.Img(24, 24, (255, 255, 250)).to_canvas()))
    tiles.append(("dark", PT.Img(24, 24, (14, 14, 16)).to_canvas()))
    A = CA.atlas(tiles, f"coolerglow_v{variant % 4}", gutter=CA.SMOOTH_GUTTER, bleed=True)
    A["said"] = said
    A["unset"] = unset
    return A
