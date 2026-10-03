"""The front-load dumpster: its shape, its hauler, and its paint -- pure
Python, no bpy.

Zoo 1.58.0. The walker, 2026-10-03, with two photographs: "we should have
some trash dumpsters next to buildings (sides or back where its not in the
way of where customers would naturally walk into the building)".

REFERENCE (format only; the photographs' haulers are not reproduced): a
two-to-four yard front-load commercial container. A steel tub whose FRONT
leans out toward the top so the truck can tip it clean, lower at the front
than at the back; a rim bar along the front's top edge; a fork pocket (a
steel channel) down each side for the truck's arms; two black ribbed
plastic lids hinged along the back and sloping to the front; four small
casters; the hauler's white sticker and a yellow caution label on the
front. One fleet colour to a hauler.

ONE ATLAS, ONE MATERIAL, ONE DRAW. Every face is a quad naming a tile
(`machine_parts.quad`); `recipes/_card_atlas.build_art` builds them into one
object on one painted image. The fleet colour, the rust, the sticker and
the lids' ribs are paint, which costs a frame nothing; a dumpster in
another hauler's colour is another image, never another material on the
same mesh. 46 quads, 92 triangles.

Frame: metres, Z up, origin at the ground under the middle; the front (the
sticker, the low edge, the side a body walks up to) is -Y, the hinges and
the wall it backs onto are +Y. Extents exactly (w, d, h): the fork pockets
are the width, the front's top edge and the back are the depth, the casters'
feet and the lids' back edge are the height.
"""
from __future__ import annotations

import zlib

from . import machine_parts as MP
from . import paint as PT
from . import prims as P
from . import smooth_type as ST

#: The haulers: invented, Delco, PG-13 (`brands.py`'s rules). Each row is
#: the sticker's name, its line, a 555 number, the fleet paint and the
#: sticker's ink, sRGB 0..255. Four fleet colours chosen to stand off
#: asphalt (dark grey), brick (brown-red) and painted block (white, blue
#: grey): a prop a body walks into has to read against what is behind it.
HAULERS = (
    {"id": "delco_disposal", "name": "DELCO DISPOSAL", "line": "WE TAKE YOUR CRAP",
     "phone": "610-555-0142", "paint": (34, 104, 62), "ink": (20, 74, 44)},
    {"id": "jawn_haulers", "name": "JAWN HAULERS", "line": "ONE MAN'S TRASH. PERIOD.",
     "phone": "610-555-0177", "paint": (36, 70, 148), "ink": (24, 46, 110)},
    {"id": "macdade_refuse", "name": "MACDADE REFUSE", "line": "YOUS FILL IT. WE DUMP IT.",
     "phone": "610-555-0119", "paint": (132, 38, 44), "ink": (104, 26, 32)},
    {"id": "tinicum_trash", "name": "TINICUM TRASH CO", "line": "SMELLS LIKE HOME",
     "phone": "610-555-0163", "paint": (186, 104, 36), "ink": (120, 62, 16)},
)

#: The label's two lines; a notice nobody designed (`smooth_type.OWNERS`).
CAUTION = ("CAUTION", "KEEP OFF")

MAKER = ST.owned("maker")
MAKER_SMALL = ST.owned("maker_small")
NOTICE = ST.owned("notice_bold")

#: Pixels a metre of paint.
TEXEL = 256

CASTER_H = 0.10          # the casters' height: the tub's floor above the ground
CASTER = (0.10, 0.12)    # a caster's plan size
CASTER_IN = 0.12         # in from the tub's corner
LID_T = 0.05             # a lid's thickness
FRONT_DROP = 0.12        # the front's top edge below the back's, of the height
LEAN = 0.20              # how far the front's foot sits back from its top, of the depth
POCKET_PROUD = 0.06      # a fork pocket's stand-off from the tub's side
POCKET_BURY = 0.01       # ...and how far its inner edge sits inside the side
POCKET_Z = (0.42, 0.52)  # its band, of the height
POCKET_Y = (0.12, 0.72)  # its run from the front, of the depth
RIM_H = 0.06             # the rim bar's height
RIM_D = 0.05             # ...its depth
RIM_OVER = 0.02          # ...and how far it runs past the tub each side

PLASTIC = (27, 27, 30)
RUST = (112, 58, 26)
BARE = (150, 152, 154)
DARK = (22, 22, 24)


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def _px(m):
    return max(8, int(round(m * TEXEL)))


def _lift(rgb, by):
    return tuple(max(0, min(255, c + by)) for c in rgb)


# --- the shape -------------------------------------------------------------------------


def _box(part, tile, lo, hi, skip=()):
    """An axis-aligned box as quads, each wound and mapped as its viewer
    sees it; ``skip`` names faces left out (front, back, left, right, top,
    under). A skipped face is one that would lie on another prim's plane, or
    that nothing can see."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    faces = {
        "front": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        "back": [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
        "right": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        "left": [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
        "top": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        "under": [(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)],
    }
    return [MP.quad(f"{part}_{k}", "paint", tile if isinstance(tile, str) else tile.get(k, tile["*"]), v)
            for k, v in faces.items() if k not in skip]


def plan(w, d, h, variant=0):
    """``{"prims", "tiles", "collision", "facts"}``: every prim a quad on
    the one atlas, ``paint``."""
    v = int(variant) % len(HAULERS)
    hauler = HAULERS[v]
    x0, x1 = -w / 2.0 + POCKET_PROUD, w / 2.0 - POCKET_PROUD     # the tub's sides
    yf, yb = -d / 2.0, d / 2.0                                    # front top edge, back
    yff = yf + d * LEAN                                           # the front's foot
    zc = CASTER_H
    zb = h - LID_T                                                # the back's top
    zf = zb - h * FRONT_DROP                                      # the front's top
    t = LID_T
    prims = []
    # the tub: front leaning, back and sides upright, a floor; no top (the
    # lids close it, and they have no underside)
    prims.append(MP.quad("Dumpster_Front", "paint", "front",
                         [(x0, yff, zc), (x1, yff, zc), (x1, yf, zf), (x0, yf, zf)]))
    prims.append(MP.quad("Dumpster_Back", "paint", "back",
                         [(x1, yb, zc), (x0, yb, zc), (x0, yb, zb), (x1, yb, zb)]))
    prims.append(MP.quad("Dumpster_SideR", "paint", "side",
                         [(x1, yff, zc), (x1, yb, zc), (x1, yb, zb), (x1, yf, zf)]))
    prims.append(MP.quad("Dumpster_SideL", "paint", "side",
                         [(x0, yb, zc), (x0, yff, zc), (x0, yf, zf), (x0, yb, zb)],
                         uv=(1.0, 0.0, 0.0, 1.0)))
    prims.append(MP.quad("Dumpster_Under", "paint", "under",
                         [(x1, yff, zc), (x0, yff, zc), (x0, yb, zc), (x1, yb, zc)]))
    # the two lids: one slope from the back's top to the front's, meeting on
    # the centre line, with an edge all round
    for name, xa, xb in (("L", x0, 0.0), ("R", 0.0, x1)):
        prims.append(MP.quad(f"Dumpster_Lid{name}", "paint", "lid",
                             [(xa, yf, zf + t), (xb, yf, zf + t), (xb, yb, zb + t), (xa, yb, zb + t)]))
    prims.append(MP.quad("Dumpster_LidFront", "paint", "lid_edge",
                         [(x0, yf, zf), (x1, yf, zf), (x1, yf, zf + t), (x0, yf, zf + t)]))
    prims.append(MP.quad("Dumpster_LidBack", "paint", "lid_edge",
                         [(x1, yb, zb), (x0, yb, zb), (x0, yb, zb + t), (x1, yb, zb + t)]))
    prims.append(MP.quad("Dumpster_LidEdgeR", "paint", "lid_edge",
                         [(x1, yf, zf), (x1, yb, zb), (x1, yb, zb + t), (x1, yf, zf + t)]))
    prims.append(MP.quad("Dumpster_LidEdgeL", "paint", "lid_edge",
                         [(x0, yb, zb), (x0, yf, zf), (x0, yf, zf + t), (x0, yb, zb + t)]))
    # the rim bar under the lids' front edge, a hand past the tub each side
    # so its ends do not lie on the sides' planes; no back (inside the tub)
    prims += _box("Dumpster_Rim", "rim", (x0 - RIM_OVER, yf, zf - RIM_H), (x1 + RIM_OVER, yf + RIM_D, zf),
                  skip=("back",))
    # the fork pockets: a channel down each side, its inner edge inside the
    # tub's side, its front end the dark mouth the truck's arm goes in
    zp0, zp1 = h * POCKET_Z[0], h * POCKET_Z[1]
    yp0, yp1 = yf + d * POCKET_Y[0], yf + d * POCKET_Y[1]
    tiles_p = {"*": "pocket", "front": "mouth"}
    prims += _box("Dumpster_PocketR", tiles_p, (x1 - POCKET_BURY, yp0, zp0), (w / 2.0, yp1, zp1),
                  skip=("left",))
    prims += _box("Dumpster_PocketL", tiles_p, (-w / 2.0, yp0, zp0), (x0 + POCKET_BURY, yp1, zp1),
                  skip=("right",))
    # the casters: no top (it would lie on the floor's plane)
    cw, cd = CASTER
    for name, cx, cy in (("FL", x0 + CASTER_IN, yff + CASTER_IN), ("FR", x1 - CASTER_IN, yff + CASTER_IN),
                         ("BL", x0 + CASTER_IN, yb - CASTER_IN), ("BR", x1 - CASTER_IN, yb - CASTER_IN)):
        prims += _box(f"Dumpster_Caster{name}", "caster",
                      (cx - cw / 2.0, cy - cd / 2.0, 0.0), (cx + cw / 2.0, cy + cd / 2.0, zc),
                      skip=("top",))
    slant = ((yff - yf) ** 2 + (zf - zc) ** 2) ** 0.5
    lid_run = ((yb - yf) ** 2 + (zb - zf) ** 2) ** 0.5
    tiles = {
        "front": ("paint", {"kind": "dumpster_front", "w_m": x1 - x0, "h_m": slant, "variant": v}),
        "back": ("paint", {"kind": "dumpster_back", "w_m": x1 - x0, "h_m": zb - zc, "variant": v}),
        "side": ("paint", {"kind": "dumpster_side", "w_m": d, "h_m": zb - zc, "variant": v}),
        "under": ("paint", {"kind": "dumpster_dark", "w_m": 0.25, "h_m": 0.25, "variant": v}),
        "lid": ("paint", {"kind": "dumpster_lid", "w_m": (x1 - x0) / 2.0, "h_m": lid_run, "variant": v}),
        "lid_edge": ("paint", {"kind": "dumpster_lid_edge", "w_m": 0.5, "h_m": 0.06, "variant": v}),
        "rim": ("paint", {"kind": "dumpster_rim", "w_m": 0.5, "h_m": 0.08, "variant": v}),
        "pocket": ("paint", {"kind": "dumpster_pocket", "w_m": 0.5, "h_m": 0.12, "variant": v}),
        "mouth": ("paint", {"kind": "dumpster_dark", "w_m": 0.12, "h_m": 0.12, "variant": v}),
        "caster": ("paint", {"kind": "dumpster_caster", "w_m": 0.12, "h_m": 0.12, "variant": v}),
    }
    return {"prims": prims, "tiles": tiles,
            "collision": ((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h)),
            "facts": {"hauler": hauler["id"], "variant": v,
                      "tris": P.tri_count(prims), "materials": 1}}


# --- the paint -------------------------------------------------------------------------


def _steel(im, w, h, body, seed, streaks=7):
    """Fleet paint on plate that lives outside: lighter where the sky falls
    on it, rust run down from the top edge, grime risen from the ground,
    chips to bare metal along the rim."""
    im.vgrad((0, 0, w, h), _lift(body, 18), _lift(body, -30))
    im.grain((0, 0, w, h), 4.0, seed)
    im.edge_dark((0, 0, w, h), max(4, w * 0.06), 0.22)
    for k in range(streaks):
        r = _h("streak", seed, k)
        x = 4 + r % max(1, w - 8)
        run = int(h * (0.18 + ((r >> 8) % 100) / 100.0 * 0.45))
        wide = 1 + (r >> 16) % 3
        im.rect((x, 0, x + wide, run), RUST, 0.30)
        im.rect((x, 0, x + wide, run // 3), RUST, 0.25)
    im.vgrad((0, int(h * 0.82), w, h), _lift(body, -30), _lift(body, -62))
    for k in range(max(3, w // 40)):
        r = _h("chip", seed, k)
        x = r % max(1, w - 4)
        im.rect((x, (r >> 8) % 5, x + 2 + (r >> 12) % 4, 2 + (r >> 8) % 5), BARE, 0.6)


def paint(spec):
    """One tile as a Canvas; ``c.unset`` lists every line that did not set."""
    kind = spec["kind"]
    v = int(spec.get("variant", 0)) % len(HAULERS)
    hauler = HAULERS[v]
    body = hauler["paint"]
    w, h = _px(spec["w_m"]), _px(spec["h_m"])
    if kind == "dumpster_front":
        im = PT.Img(w, h, body)
        _steel(im, w, h, body, 11 + v)
        # the hauler's sticker: white vinyl, the name, the number in a bar,
        # the line under it
        sx0, sx1 = int(w * 0.22), int(w * 0.66)
        sy0, sy1 = int(h * 0.30), int(h * 0.80)
        im.rrect((sx0, sy0, sx1, sy1), 3, (236, 236, 230))
        im.edge_dark((sx0, sy0, sx1, sy1), 3, 0.10)
        sh = sy1 - sy0
        pad = max(3, (sx1 - sx0) // 20)
        im.text(hauler["name"], (sx0 + pad, sy0 + sh * 0.06, sx1 - pad, sy0 + sh * 0.40),
                hauler["ink"], face=MAKER)
        im.rrect((sx0 + pad, sy0 + sh * 0.44, sx1 - pad, sy0 + sh * 0.72), 4, hauler["ink"])
        im.text(hauler["phone"], (sx0 + 2 * pad, sy0 + sh * 0.47, sx1 - 2 * pad, sy0 + sh * 0.69),
                (244, 244, 238), face=MAKER)
        im.text(hauler["line"], (sx0 + pad, sy0 + sh * 0.76, sx1 - pad, sy0 + sh * 0.96),
                hauler["ink"], face=MAKER_SMALL)
        # the caution label, top right: a yellow header on white
        cx0, cx1 = int(w * 0.76), int(w * 0.93)
        cy0, cy1 = int(h * 0.20), int(h * 0.52)
        ch = cy1 - cy0
        im.rect((cx0, cy0, cx1, cy1), (238, 238, 232))
        im.rect((cx0, cy0, cx1, cy0 + ch * 0.42), (240, 196, 40))
        im.text(CAUTION[0], (cx0 + 2, cy0 + 1, cx1 - 2, cy0 + ch * 0.42 - 1), (20, 20, 20), face=NOTICE)
        im.text(CAUTION[1], (cx0 + 2, cy0 + ch * 0.50, cx1 - 2, cy0 + ch * 0.92), (20, 20, 20), face=NOTICE)
        return im.to_canvas()
    if kind == "dumpster_back":
        im = PT.Img(w, h, body)
        _steel(im, w, h, body, 23 + v)
        # the hinge bar the lids hang on, along the top
        im.rect((0, 0, w, max(3, h * 0.06)), _lift(body, -46))
        im.rect((0, max(3, h * 0.06), w, max(4, h * 0.06) + 1), _lift(body, 24), 0.5)
        return im.to_canvas()
    if kind == "dumpster_side":
        im = PT.Img(w, h, body)
        _steel(im, w, h, body, 37 + v, streaks=5)
        # the shadow the fork pocket throws down the plate under it
        z0, z1 = POCKET_Z
        im.rect((0, int(h * (1.0 - z0 * 1.12)), w, int(h * (1.0 - z0 * 1.12)) + max(3, h // 18)), (0, 0, 0), 0.28)
        return im.to_canvas()
    if kind == "dumpster_lid":
        # black moulded plastic: ribs running front to back, a lip along the
        # front (the tile's foot), the sky's streak across it
        im = PT.Img(w, h, PLASTIC)
        im.vgrad((0, 0, w, h), _lift(PLASTIC, 10), _lift(PLASTIC, -4))
        ribs = 6
        gap = w / float(ribs)
        for k in range(ribs):
            bx0, bx1 = int(k * gap + gap * 0.18), int((k + 1) * gap - gap * 0.18)
            box = (bx0, int(h * 0.08), bx1, int(h * 0.86))
            im.rect(box, _lift(PLASTIC, 16))
            im.bevel(box, max(1, int(gap * 0.08)), light=34.0, dark=22.0)
        im.rect((0, int(h * 0.92), w, h), _lift(PLASTIC, 12))
        im.gloss((0, 0, w, h), strength=0.10)
        im.grain((0, 0, w, h), 2.5, 53 + v)
        im.edge_dark((0, 0, w, h), max(2, w * 0.04), 0.3)
        return im.to_canvas()
    if kind == "dumpster_lid_edge":
        im = PT.Img(w, h, PLASTIC)
        im.vgrad((0, 0, w, h), _lift(PLASTIC, 20), _lift(PLASTIC, -8))
        im.grain((0, 0, w, h), 2.0, 59)
        return im.to_canvas()
    if kind == "dumpster_rim":
        im = PT.Img(w, h, _lift(body, -24))
        im.vgrad((0, 0, w, h), _lift(body, 6), _lift(body, -44))
        for k in range(10):
            r = _h("rim", v, k)
            x = r % max(1, w - 6)
            im.rect((x, (r >> 8) % max(1, h - 3), x + 3 + (r >> 12) % 6, (r >> 8) % max(1, h - 3) + 2), BARE, 0.55)
        im.grain((0, 0, w, h), 3.0, 61 + v)
        return im.to_canvas()
    if kind == "dumpster_pocket":
        im = PT.Img(w, h, _lift(body, -18))
        im.vgrad((0, 0, w, h), _lift(body, 10), _lift(body, -40))
        im.grain((0, 0, w, h), 3.0, 67 + v)
        im.edge_dark((0, 0, w, h), max(2, h * 0.25), 0.25)
        return im.to_canvas()
    if kind == "dumpster_caster":
        im = PT.Img(w, h, (46, 46, 48))
        im.vgrad((0, 0, w, h), (70, 70, 72), (20, 20, 22))
        im.grain((0, 0, w, h), 3.0, 71)
        return im.to_canvas()
    if kind == "dumpster_dark":
        im = PT.Img(w, h, DARK)
        im.vgrad((0, 0, w, h), (8, 8, 9), (30, 30, 32))
        return im.to_canvas()
    raise ValueError(f"no dumpster tile {kind!r}")


def all_strings():
    """Every word painted on a dumpster, for the invented-names test."""
    out = list(CAUTION)
    for hauler in HAULERS:
        out += [hauler["name"], hauler["line"], hauler["phone"]]
    return out
