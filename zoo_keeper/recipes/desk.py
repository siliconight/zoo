"""Desk recipe. Acceptance target: '1990s office desk with two drawers'
-> correctly scaled desk with drawers, handles, bevels, worn laminate,
collision, UVs, metadata, GLB.

Layout (origin at floor center, user sits at -Y):
  top slab, panel/post legs, right-hand drawer pedestal with proud fronts
  and bar handles, optional modesty panel at the back.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

TOP_T = 0.03        # top slab thickness
PANEL_T = 0.03      # panel leg thickness
POST_S = 0.05       # post leg square size
PED_W = 0.42        # drawer pedestal width


def _darker(c, f=0.55):
    return [v * f for v in c]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel = plan["bevel"]
    wear = plan["wear"]
    rng = streams.stream("wear")
    n_drawers = plan["params"]["drawers"]
    leg_style = plan["params"]["leg_style"]

    objs = []
    cboxes = []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.0,
            rng=rng, wear=wear))

    # top slab
    bm = geometry.new_bm()
    geometry.add_box(bm, (0, 0, h - TOP_T / 2), (w, d, TOP_T))
    part(bm, "Desk_Top")
    cboxes.append(((-w / 2, -d / 2, h - TOP_T), (w / 2, d / 2, h)))

    # legs
    leg_h = h - TOP_T
    if leg_style == "panel":
        for side, sx in (("L", -1), ("R", 1)):
            x = sx * (w / 2 - PANEL_T / 2)
            bm = geometry.new_bm()
            geometry.add_box(bm, (x, 0, leg_h / 2),
                             (PANEL_T, d * 0.92, leg_h))
            part(bm, f"Desk_Leg_{side}")
            cboxes.append(((x - PANEL_T / 2, -d * 0.46, 0),
                           (x + PANEL_T / 2, d * 0.46, leg_h)))
    else:  # post
        inset = 0.06
        i = 0
        for sx in (-1, 1):
            for sy in (-1, 1):
                i += 1
                x = sx * (w / 2 - inset)
                y = sy * (d / 2 - inset)
                bm = geometry.new_bm()
                geometry.add_box(bm, (x, y, leg_h / 2),
                                 (POST_S, POST_S, leg_h))
                part(bm, f"Desk_Leg_{i}")
                cboxes.append(((x - POST_S / 2, y - POST_S / 2, 0),
                               (x + POST_S / 2, y + POST_S / 2, leg_h)))

    # drawer pedestal (right side), fronts proud toward -Y
    if n_drawers > 0:
        ped_x = w / 2 - PANEL_T - PED_W / 2 - 0.01
        ped_h = leg_h - 0.02
        bm = geometry.new_bm()
        geometry.add_box(bm, (ped_x, 0.01, ped_h / 2),
                         (PED_W, d * 0.9 - 0.02, ped_h))
        part(bm, "Desk_Pedestal")
        cboxes.append(((ped_x - PED_W / 2, -d * 0.45, 0),
                       (ped_x + PED_W / 2, d * 0.45, ped_h)))

        gap = 0.012
        dh = (ped_h - gap * (n_drawers + 1)) / n_drawers
        front_y = 0.01 - (d * 0.9 - 0.02) / 2 - 0.008
        for i in range(n_drawers):
            z = gap + dh / 2 + i * (dh + gap)
            bm = geometry.new_bm()
            geometry.add_box(bm, (ped_x, front_y, z),
                             (PED_W - 0.03, 0.018, dh))
            part(bm, f"Desk_Drawer_{i + 1}")
            # bar handle
            bm = geometry.new_bm()
            geometry.add_box(bm, (ped_x, front_y - 0.018, z),
                             (PED_W * 0.45, 0.015, 0.015))
            part(bm, f"Desk_Handle_{i + 1}")

    # modesty panel at the back
    if plan["params"].get("modesty_panel"):
        span = w - 2 * PANEL_T if leg_style == "panel" else w - 0.3
        if n_drawers > 0:
            span = max(0.2, span - PED_W)
        mp_x = -(w - span) / 2 + PANEL_T if n_drawers > 0 else 0
        bm = geometry.new_bm()
        geometry.add_box(bm, (mp_x, d / 2 - 0.02, leg_h * 0.62),
                         (span, 0.02, leg_h * 0.55))
        part(bm, "Desk_ModestyPanel")

    # materials: surface color on top/drawers, darker frame elsewhere
    surface = materials.make_material(
        f"M_Desk_{plan['material']}", plan["color"], plan["material"])
    frame = materials.make_material(
        f"M_Desk_frame_{plan['material']}", _darker(plan["color"]),
        plan["material"])
    tops = [o for o in objs if "Top" in o.name or "Drawer" in o.name]
    rest = [o for o in objs if o not in tops]
    materials.assign(tops, surface)
    materials.assign(rest, frame)

    return {
        "objects": objs,
        "collision_boxes": cboxes,
        "attachments": {"ATT_surface_center": (0, 0, h)},
    }
