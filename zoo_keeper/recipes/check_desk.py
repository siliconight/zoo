"""check_desk recipe: a bank lobby's check-writing desk -- a standing-height island on two pedestals, a dark top with
slip pockets along both long edges, a date block on its middle.

Zoo 1.135.0, from the walker's bank comps (the factory's docs/reference/BANK_INTERIOR_COMPS.md, 2026-10-27): "a check
desk island stands mid-floor in front of [the teller line]: a standing-height table with slots for slips" (comps 1, 4,
7). Comp 1's carries a perpetual date block on its middle -- the day, the month and the date on cards in a dark stand
-- which is the comps' "date clock", so it stands here rather than as a species of its own. Minted by
`tools/new_species.py`; shaped here.

REFERENCE: the 1920s-1990s banking-hall writing desk. Two pedestals on a plinth each and a low stretcher between them;
a top that overhangs them all round, dark (glass over wood, or a dark laminate); under its edge on both long sides a
row of small slanted pockets holding the slips -- deposit, withdrawal -- so a customer on either side reaches one.

TWO MATERIALS: the body (the plan's material: wood by default) with the top's dark and the pockets' brass as COLOUR
ONLY, in the `Wear` vertex colour (`geometry.tint_wear`), and the paper -- the date cards and a slip or two on the top
-- in a second, white. Two submissions whatever its size.

Recipe frame: centre pivot. Both long faces (+y and -y) are shopped. The module is exactly (w, d, h): the top is the
footprint, the plinths stand on the floor, the date block's crown is the slot's top.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

TOP_T = 0.05             # the top's thickness
DATE_H = 0.14            # the date block's height above the top
DATE_W, DATE_D = 0.30, 0.12
PED_W = 0.28             # a pedestal along x
PED_INSET = 0.12         # a pedestal's outer face this far inside the top's end
PED_D_INSET = 0.14       # and its faces this far inside the top's long edges
PLINTH_H = 0.07
PLINTH_OUT = 0.03        # a plinth this much wider than its pedestal, each side
STRETCH = 0.06           # the stretcher's square section
STRETCH_Z = 0.18         # its centre above the floor
POCKET_W, POCKET_D, POCKET_H = 0.14, 0.05, 0.09
POCKET_GAP = 0.04
POCKET_IN = 0.012        # a pocket's front this far inside the top's edge
CARD_T = 0.004           # a date card's thickness, proud of the block
#: a slip lies on the top, half buried: its faces 4 mm either side of the top's, past the census's 2.2 mm
SLIP = (0.18, 0.09, 0.008)
BURY = 0.008             # a part runs this far into the one it meets, never onto its face

DARK_TOP = (0.10, 0.10, 0.11)
BRASS = (0.78, 0.62, 0.30)
DATE_BODY = (0.06, 0.05, 0.05)
PAPER = (0.95, 0.94, 0.90)


def pedestal(w):
    """``(width, inset)`` of each pedestal: `PED_W` and `PED_INSET` on a desk of 1.6 m or more, in proportion below
    it, so a short desk's pedestals and plinths keep a stretcher's length apart (at 0.8 m the fixed pair met)."""
    k = min(1.0, w / 1.6)
    return PED_W * k, PED_INSET * k


def layout(w, d, h):
    """``[(part, kind, [(centre, size), ...], rgb)]`` in the recipe frame, kind ``"body"`` or ``"paper"``. Pure: the
    tests read it without Blender."""
    z0 = -h / 2.0
    top_z1 = h / 2.0 - DATE_H                     # the top's upper face
    top_z0 = top_z1 - TOP_T
    parts = []
    parts.append(("CheckDesk_Top", "body", [((0.0, 0.0, (top_z0 + top_z1) / 2.0), (w, d, TOP_T))], DARK_TOP))
    ped_d = d - 2.0 * PED_D_INSET
    ped_w, ped_in = pedestal(w)
    peds, plinths = [], []
    for s in (-1.0, 1.0):
        px = s * (w / 2.0 - ped_in - ped_w / 2.0)
        pz0, pz1 = z0 + PLINTH_H - BURY, top_z0 + BURY
        peds.append(((px, 0.0, (pz0 + pz1) / 2.0), (ped_w, ped_d, pz1 - pz0)))
        plinths.append(((px, 0.0, z0 + PLINTH_H / 2.0), (ped_w + 2.0 * PLINTH_OUT, ped_d + 2.0 * PLINTH_OUT,
                                                         PLINTH_H)))
    parts.append(("CheckDesk_Pedestal", "body", peds, (1.0, 1.0, 1.0)))
    parts.append(("CheckDesk_Plinth", "body", plinths, (0.55, 0.50, 0.45)))
    inner = w / 2.0 - ped_in - ped_w                    # a pedestal's inner face
    parts.append(("CheckDesk_Stretcher", "body",
                  [((0.0, 0.0, z0 + STRETCH_Z), (2.0 * (inner + BURY), STRETCH, STRETCH))], (1.0, 1.0, 1.0)))
    # the slip pockets: a row under each long edge, between the pedestals' ends
    span = 2.0 * (w / 2.0 - ped_in * 0.5)
    n = max(2, int((span + POCKET_GAP) // (POCKET_W + POCKET_GAP)))
    x0 = -((n - 1) * (POCKET_W + POCKET_GAP)) / 2.0
    pockets = []
    for s in (-1.0, 1.0):
        py = s * (d / 2.0 - POCKET_IN - POCKET_D / 2.0)
        for i in range(n):
            pockets.append(((x0 + i * (POCKET_W + POCKET_GAP), py, top_z0 - POCKET_H / 2.0 + BURY),
                            (POCKET_W, POCKET_D, POCKET_H)))
    parts.append(("CheckDesk_Pockets", "body", pockets, BRASS))
    # the date block on the top's middle, its crown the slot's top
    parts.append(("CheckDesk_DateBlock", "body",
                  [((0.0, 0.0, (top_z1 - BURY + h / 2.0) / 2.0), (DATE_W, DATE_D, DATE_H + BURY))], DATE_BODY))
    # the paper: the date's cards on both faces of the block, and a slip on the top either side of it
    cards = []
    for s in (-1.0, 1.0):
        cy = s * (DATE_D / 2.0 + CARD_T / 2.0 - BURY / 4.0)
        for k, (cw, ch) in enumerate(((0.22, 0.035), (0.16, 0.030), (0.08, 0.040))):
            cz = top_z1 + 0.115 - k * 0.045
            cards.append(((0.0, cy, cz), (cw, CARD_T + BURY / 2.0, ch)))
    slips = [((s * 0.45 * w / 2.0, -s * 0.15 * d, top_z1), SLIP)
             for s in (-1.0, 1.0)]
    parts.append(("CheckDesk_Paper", "paper", cards + slips, PAPER))
    return parts


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    body_objs, paper_objs = [], []
    for name, kind, boxes, rgb in layout(w, d, h):
        bm = geometry.new_bm()
        for centre, size in boxes:
            geometry.add_box(bm, centre, size)
        o = geometry.bm_to_object(bm, name, collection, bevel=bevel if kind == "body" else 0.0, texel=1.2, rng=rng,
                                  wear=wear)
        geometry.tint_wear(o, rgb)
        (body_objs if kind == "body" else paper_objs).append(o)
    body = materials.make_material(f"M_CheckDesk_{plan['material']}", plan["color"], plan["material"])
    paper = materials.make_material("M_CheckDesk_paper", (1.0, 1.0, 1.0), "plastic")
    materials.assign(body_objs, body)
    materials.assign(paper_objs, paper)
    return {"objects": body_objs + paper_objs,
            "collision_boxes": [((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0))],
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
