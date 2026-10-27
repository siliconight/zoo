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

    # the deck: the fascia's colour all round, the module's width and depth; its -X face meets the building's wall
    bm = geometry.new_bm()
    box(bm, (-w / 2.0, -d / 2.0, soffit), (w / 2.0, d / 2.0, top))
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
    # the tube's run under the soffit, from the island line to the wall
    bm = geometry.new_bm()
    rz = floor + run_z(h)
    geometry.add_cylinder(bm, ((cx - w / 2.0) / 2.0, 0.0, rz), TUBE_R, cx + w / 2.0, segments=SEG, axis="X")
    finish(bm, "DriveUpCanopy_Tube", TUBE_RGB)
    body = materials.make_material(f"M_DriveUpCanopy_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, body)
    # a body walks under it: the columns and their footings collide, the deck overhead does not need to
    cols = [((cx - fs / 2.0, column_y(d, sy) - fs / 2.0, floor), (cx + fs / 2.0, column_y(d, sy) + fs / 2.0, soffit))
            for sy in (-1.0, 1.0)]
    return {"objects": objs, "collision_boxes": cols,
            "attachments": {"ATT_station": (cx, 0.0, floor), "ATT_wall": (-w / 2.0, 0.0, floor + run_z(h))}}
