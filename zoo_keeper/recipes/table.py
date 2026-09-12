"""Table recipe: top slab on four posts (or two side panels), optional
lower shelf. Origin at floor center.

BAYS (roadmap 44). A Deli Counter `count_table` is 4 x 2 m and a
`kitchen_prep_table` 4 x 1.2: tables pushed together into a run. `_bays.bays`
divides the width into units of at most `bay_max` (genome params); the top
runs the full width as one surface and each bay stands on its own legs and
carries its own lower shelf. One bay is the table this recipe always built.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ._bays import bay_max_of, bays

TOP_T = 0.04
POST = 0.05
PANEL_T = 0.03


def _darker(c, f=0.6):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    leg_style = plan["params"]["leg_style"]
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.0, rng=rng, wear=wear))

    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, h - TOP_T / 2), (w, d, TOP_T))
    part(bm, "Table_Top")
    cboxes.append(((-w / 2, -d / 2, h - TOP_T), (w / 2, d / 2, h)))

    leg_h = h - TOP_T
    runs = bays(w, bay_max_of(plan))
    for bi, (bx, bw) in enumerate(runs):
        tag = "" if len(runs) == 1 else f"_B{bi + 1}"
        if leg_style == "panel":
            for side, sx in (("L", -1), ("R", 1)):
                x = bx + sx * (bw / 2 - PANEL_T / 2)
                bm = geometry.new_bm()
                geometry.add_box(bm, (x, 0, leg_h / 2), (PANEL_T, d * 0.9, leg_h))
                part(bm, f"Table_Leg_{side}{tag}")
                cboxes.append(((x - PANEL_T / 2, -d * 0.45, 0),
                               (x + PANEL_T / 2, d * 0.45, leg_h)))
        else:
            i = 0
            for sx in (-1, 1):
                for sy in (-1, 1):
                    i += 1
                    x = bx + sx * (bw / 2 - 0.06)
                    y = sy * (d / 2 - 0.06)
                    bm = geometry.new_bm()
                    geometry.add_box(bm, (x, y, leg_h / 2), (POST, POST, leg_h))
                    part(bm, f"Table_Leg_{i}{tag}")
                    cboxes.append(((x - POST / 2, y - POST / 2, 0),
                                   (x + POST / 2, y + POST / 2, leg_h)))
        if plan["params"].get("shelf"):
            bm = geometry.new_bm()
            geometry.add_box(bm, (bx, 0, leg_h * 0.3), (bw * 0.82, d * 0.82, 0.02))
            part(bm, f"Table_Shelf{tag}")

    top_mat = materials.make_material(
        f"M_Table_{plan['material']}", plan["color"], plan["material"])
    frame = materials.make_material(
        f"M_Table_frame_{plan['material']}", _darker(plan["color"]),
        plan["material"])
    tops = [o for o in objs if "Top" in o.name or "Shelf" in o.name]
    materials.assign(tops, top_mat)
    materials.assign([o for o in objs if o not in tops], frame)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_surface_center": (0, 0, h)}}
