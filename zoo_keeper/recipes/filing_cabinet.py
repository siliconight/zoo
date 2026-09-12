"""Filing cabinet recipe: a vertical file — body box, N stacked drawer
fronts (proud toward -Y) with bar handles, and a recessed kick base.

Layout (origin at floor center, drawers face -Y). Reuses the same proud-front
+ bar-handle construction as the desk pedestal.

BAYS (roadmap 44). Deli Counter's `cabinet_*` and `*_LOCKER` volumes are
0.9-3.0 m wide: a bank of cabinets or lockers, not one file. `_bays.bays`
divides the width into units of at most `bay_max` (genome params); the base
and the body run the full width, each bay carries its own stack of drawer
fronts and handles. One bay is the cabinet this recipe always built.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ._bays import bay_max_of, bays


def _darker(c, f=0.62):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    n_drawers = plan["params"]["drawers"]
    has_base = plan["params"].get("base", 1)
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.5,
            rng=rng, wear=wear))

    base_h = 0.06 if has_base else 0.0
    # EXACT FIT (roadmap 44): the drawer fronts and their bar pulls stand
    # 0.05 m proud of the body's front face. On a free-standing cabinet
    # that is the silhouette; built into a Deli Counter slot the whole
    # thing must be the slot's depth -- the first 3.0 x 0.8 x 2.0 locker
    # bank came out 0.840 deep and failed `fit_depth`. Under `fit_exact`
    # the body gives up the proud amount and the fronts end at -d/2.
    proud = 0.05
    exact = bool(plan.get("fit_exact"))
    body_d = d - proud if exact else d
    body_y = proud / 2 if exact else 0.0
    # recessed kick base
    if has_base:
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, body_y, base_h / 2), (w * 0.94, body_d * 0.94, base_h))
        part(bm, "Cabinet_Base")
        cboxes.append(((-w * 0.47, body_y - body_d * 0.47, 0),
                       (w * 0.47, body_y + body_d * 0.47, base_h)))
    # main body
    body_h = h - base_h
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, body_y, base_h + body_h / 2), (w, body_d, body_h))
    part(bm, "Cabinet_Body")
    cboxes.append(((-w / 2, -d / 2, base_h), (w / 2, d / 2, h)))
    # stacked drawer fronts, proud of the front face (-Y), per bay
    gap = 0.015
    dh = (body_h - gap * (n_drawers + 1)) / n_drawers
    front_y = body_y - body_d / 2 - 0.009
    runs = bays(w, bay_max_of(plan))
    for bi, (bx, bw) in enumerate(runs):
        tag = "" if len(runs) == 1 else f"_B{bi + 1}"
        for i in range(n_drawers):
            z = base_h + gap + dh / 2 + i * (dh + gap)
            bm = geometry.new_bm()
            geometry.add_box(bm, (bx, front_y, z), (bw - 0.04, 0.018, dh))
            part(bm, f"Cabinet_Drawer_{i + 1}{tag}")
            # horizontal bar pull, upper third of the drawer face
            bm = geometry.new_bm()
            geometry.add_box(bm, (bx, front_y - 0.02, z + dh * 0.28),
                             (bw * 0.4, 0.022, 0.02))
            part(bm, f"Cabinet_Handle_{i + 1}{tag}")
    # materials: body + drawer fronts share the cabinet color; base and
    # handles are the darker frame tone.
    surface = materials.make_material(
        f"M_Cabinet_{plan['material']}", plan["color"], plan["material"])
    frame = materials.make_material(
        f"M_Cabinet_frame_{plan['material']}", _darker(plan["color"]),
        plan["material"])
    frame_objs = [o for o in objs if "Base" in o.name or "Handle" in o.name]
    materials.assign([o for o in objs if o not in frame_objs], surface)
    materials.assign(frame_objs, frame)
    return {
        "objects": objs,
        "collision_boxes": cboxes,
        "attachments": {"ATT_top_center": (0, 0, h)},
    }
