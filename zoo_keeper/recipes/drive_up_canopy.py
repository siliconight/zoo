"""drive_up_canopy recipe: a bank's drive-up lane canopy -- a flat deck off the building's wall over the lane and the
tube station's island, two steel columns on the island line, a fascia in the bank's colour, a light soffit, and the
pneumatic tube's run under the deck from the station to the wall.

Zoo 1.138.0, from the walker's bank list, outside (the factory's docs/reference/BANK_INTERIOR_COMPS.md, researched).
Minted by `tools/new_species.py`; shaped here. The station is `drive_up_tube`, a module of its own on the island line:
this one stands over it, and the tube it raises meets the run here (`run_z`).

THE VARIANT IS THE BANK'S, as the time-and-temperature sign's (`teller_line_forms.bank_said`): the fascia is the
sixteen variants' field colour, so a lane reads as the bank whose sign is out front.

ONE MATERIAL: the fascia, the soffit, the columns, their footings and the tube are colour only, in the `Wear` vertex
colour (`geometry.tint_wear`): one submission.

Recipe frame: centre pivot, the building's wall at -X (the deck's -X face meets it; nothing stands on that side), the
island line at +X, the lane along Y. The module is exactly (w, d, h): the deck is the width and the depth, the
columns the height.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import teller_line_forms as TF

DECK = 0.50              # the deck's depth top to soffit: a drive-up canopy's fascia, not a gas station's
FASCIA_PROUD = 0.03      # the fascia band stands this far proud of the deck's sides
SOFFIT_IN = 0.12         # the soffit panel inside the deck's edges
SOFFIT_T = 0.02
COLUMN = 0.30
FOOTING = (0.50, 0.45)   # a column's concrete footing: its side and its height, a bollard a bumper meets first
TUBE_R = 0.065
TUBE_DROP = 0.18         # the run's centre under the soffit
#: THE CHASE (1.139.0): the run enclosed in a boxed housing, its section square about the run's centre -- the
#: remote-banking patents' "enclosed horizontal pneumatic tube portions ... below a canopy" (US 4,455,112), where
#: 1.138.0 drew a bare pipe. The station's tube rises 6 cm into it.
CHASE = 0.24
#: THE ENDS' BOARDS (1.139.0): DRIVE-UP on the two faces a driver meets coming up the lane, in the bank's colours.
#: The deck steps in by the board's thickness at each end and the board fills the step, so the envelope is the deck's
#: (the teller line's nameboard, 1.137.0). The words set on the nameboard painter at 0.17 m and up.
BOARD_T = 0.02
BOARD_INSET = 0.04
BOARD_TEXT = "DRIVE-UP"
BURY = 0.004
SHY = 0.003
SEG = 12

SOFFIT_RGB = (0.86, 0.85, 0.80)
COLUMN_RGB = (0.32, 0.33, 0.35)
FOOTING_RGB = (0.62, 0.61, 0.58)
TUBE_RGB = (0.66, 0.67, 0.69)


def fascia_rgb(variant):
    """The bank's field colour for this variant, 0..1."""
    return tuple(c / 255.0 for c in TF.bank_said(variant)["colours"][0])


def column_x(w):
    """The island line: the columns' centres and the station's, in the recipe frame -- a footing's outer face SHY
    inside the module's +X."""
    return w / 2.0 - FOOTING[0] / 2.0 - SHY


def column_y(d, side):
    """A column's centre along the lane, ``side`` -1 or 1: its footing SHY inside the module's end."""
    return side * (d / 2.0 - FOOTING[0] / 2.0 - SHY)


def run_z(h):
    """The tube run's centre over the ground, the height the station's tube rises to."""
    return h - DECK - TUBE_DROP


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    wear = plan["wear"]
    variant = int((plan.get("module") or {}).get("variant") or (plan.get("params") or {}).get("variant") or 0)
    rng = streams.stream("wear")
    objs = []
    floor = -h / 2.0
    top = h / 2.0
    soffit = top - DECK

    def finish(bm, name, rgb):
        o = geometry.bm_to_object(bm, name, collection, bevel=0.0, texel=1.2, rng=rng, wear=wear)
        geometry.tint_wear(o, rgb)
        objs.append(o)

    def box(bm, lo, hi):
        geometry.add_box(bm, tuple((lo[i] + hi[i]) / 2.0 for i in range(3)), tuple(hi[i] - lo[i] for i in range(3)))

    # the deck: the fascia's colour all round, the module's width; its -X face meets the building's wall, and it
    # stands in by the boards' thickness at each end, where they fill the step
    bm = geometry.new_bm()
    box(bm, (-w / 2.0, -d / 2.0 + BOARD_T, soffit), (w / 2.0, d / 2.0 - BOARD_T, top))
    finish(bm, "DriveUpCanopy_Deck", fascia_rgb(variant))
    # the soffit: a light panel under the deck, inside its edges, its top buried in it
    bm = geometry.new_bm()
    box(bm, (-w / 2.0 + SOFFIT_IN, -d / 2.0 + SOFFIT_IN, soffit - SOFFIT_T), (w / 2.0 - SOFFIT_IN, d / 2.0 - SOFFIT_IN,
                                                                              soffit + BURY))
    finish(bm, "DriveUpCanopy_Soffit", SOFFIT_RGB)
    # two columns on the island line, each centred on a concrete footing whose outer faces stand SHY of the module's
    # (the deck owns those planes overhead); a column's top runs into the deck past the soffit
    cx = column_x(w)
    fs, fh = FOOTING
    bm_col, bm_foot = geometry.new_bm(), geometry.new_bm()
    for sy in (-1.0, 1.0):
        cy = column_y(d, sy)
        box(bm_foot, (cx - fs / 2.0, cy - fs / 2.0, floor), (cx + fs / 2.0, cy + fs / 2.0, floor + fh))
        box(bm_col, (cx - COLUMN / 2.0, cy - COLUMN / 2.0, floor + fh - BURY),
            (cx + COLUMN / 2.0, cy + COLUMN / 2.0, soffit + 0.05))
    finish(bm_foot, "DriveUpCanopy_Footing", FOOTING_RGB)
    finish(bm_col, "DriveUpCanopy_Column", COLUMN_RGB)
    # the tube's run under the soffit, from the island line to the wall, in its chase; the chase's top is buried in the
    # soffit, its island end runs past the column line by half its section
    bm = geometry.new_bm()
    rz = floor + run_z(h)
    box(bm, (-w / 2.0, -CHASE / 2.0, rz - CHASE / 2.0), (cx + CHASE / 2.0, CHASE / 2.0, soffit - SOFFIT_T + BURY))
    finish(bm, "DriveUpCanopy_Chase", TUBE_RGB)
    body = materials.make_material(f"M_DriveUpCanopy_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, body)
    # the ends' boards: an art front and four edges a board, no back (it would lie in the deck's stepped face)
    from ..core import prims as P
    from ._card_atlas import build_art
    said = TF.bank_said(variant)
    quad_uv = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))]
    bx0, bx1 = -w / 2.0 + BOARD_INSET, w / 2.0 - BOARD_INSET
    bz0, bz1 = soffit + BOARD_INSET / 2.0, top - BOARD_INSET / 2.0
    prims = []
    for sgn in (-1.0, 1.0):
        yf = sgn * d / 2.0                  # the board's front
        yb = sgn * (d / 2.0 - BOARD_T)      # the deck's stepped face
        tag = "S" if sgn < 0 else "N"
        # the front, wound to face out (-Y at the -Y end, +Y at the +Y end), read left to right from outside
        xa, xb = (bx0, bx1) if sgn < 0 else (bx1, bx0)
        art = P.mesh(f"DriveUpCanopy_Board{tag}", "art", [(xa, yf, bz0), (xb, yf, bz0), (xb, yf, bz1), (xa, yf, bz1)],
                     [(0, 1, 2, 3)])
        art["tile"] = "board"
        art["uvs"] = list(quad_uv)
        rim = P.box(f"DriveUpCanopy_BoardRim{tag}", "art", (bx0, min(yf, yb), bz0), (bx1, max(yf, yb), bz1))
        rim["faces"] = [f for k, f in enumerate(rim["faces"]) if k in (0, 1, 3, 5)]
        rim["tile"] = "edge"
        rim["uvs"] = list(quad_uv) * len(rim["faces"])
        prims += [art, rim]
    tiles = {"board": {"kind": "teller_board", "w_m": bx1 - bx0, "h_m": bz1 - bz0, "text": BOARD_TEXT,
                       "colours": said["colours"], "voice": "shop", "numbers": []},
             "edge": {"kind": "storefront_sign", "w_m": 0.1, "h_m": 0.1, "edge": True, "text": "",
                      "colours": said["colours"]}}
    got, _atlas = build_art(prims, collection, dict(plan, _tiles=tiles), streams, "DriveUpCanopy_Board", smooth=True)
    objs += got
    # a body walks under it: the columns and their footings collide, the deck overhead does not need to
    cols = [((cx - fs / 2.0, column_y(d, sy) - fs / 2.0, floor), (cx + fs / 2.0, column_y(d, sy) + fs / 2.0, soffit))
            for sy in (-1.0, 1.0)]
    return {"objects": objs, "collision_boxes": cols,
            "attachments": {"ATT_station": (cx, 0.0, floor), "ATT_wall": (-w / 2.0, 0.0, floor + run_z(h))}}
