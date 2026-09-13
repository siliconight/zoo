"""Desk recipe. Acceptance target: '1990s office desk with two drawers'
-> correctly scaled desk with drawers, handles, bevels, worn laminate,
collision, UVs, metadata, GLB.

Layout (origin at floor center, user sits at -Y):
  top slab, panel/post legs, right-hand drawer pedestal with proud fronts
  and bar handles, optional modesty panel at the back.

BAYS (roadmap 44). A Deli Counter `cubicles_w` or `boss_desk` volume is a
RUN of desks, 2.8-5 m wide; one desk cannot be. `_bays.bays` divides the
width into units of at most `bay_max` (genome params): the top runs the
full width as one work surface, and every bay stands on its own legs with
its own pedestal, drawers and modesty panel -- a row of desks butted
together, which is what an office row is. One bay is the desk this recipe
always built.

ROWS (roadmap 154). The same division on the other axis. Ten of the
library's desk volumes are 6.0 m DEEP -- a cubicle block, not a desk -- so
`row_max` divides the depth the way `bay_max` divides the width, and
alternate rows face opposite ways, which is what back-to-back cubicles are.
`row_max` absent or 0 means one row and this recipe behaves exactly as it
did.

A TRANSACTION TOP. Twenty-seven of the library's desk volumes are 1.1 or
1.2 m tall. That is a reception desk: the work surface is still at 0.75 and
a raised ledge stands over its back edge for the person on the other side.
So the work surface stops at `DESK_WORK_H` whatever the slot asks for, and
everything above it becomes the ledge -- raising the top slab instead would
build a desk nobody can sit at.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ._bays import bay_max_of, bays

TOP_T = 0.03        # top slab thickness
PANEL_T = 0.03      # panel leg thickness
POST_S = 0.05       # post leg square size
PED_W = 0.42        # drawer pedestal width
#: The tallest the top slab is built AT. Up to here the slot's height is the
#: desk's height, which is what every desk this recipe built before the
#: range opened -- and `fit_height` is an EXACT check, so lowering a 0.80 m
#: desk to a 0.78 m work surface failed validation on the first build.
DESK_TOP_MAX = 1.0
#: Above `DESK_TOP_MAX` the slot is a reception desk, and a person still
#: sits at 0.72-0.76: the work surface stops here and the remainder becomes
#: a ledge.
DESK_WORK_H = 0.78
#: How deep the raised ledge is, and how far it stands above the work top
#: before it counts as one at all.
LEDGE_D = 0.26
LEDGE_MIN = 0.05


def _row_max_of(plan):
    """The plan's `row_max` param, 0.0 when the species has none -- the
    depth-axis twin of `_bays.bay_max_of`."""
    try:
        return float((plan.get("params") or {}).get("row_max") or 0.0)
    except (TypeError, ValueError):
        return 0.0


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

    # THE WORK SURFACE STOPS AT SITTING HEIGHT. A slot 1.2 m tall is a
    # reception desk, and raising the top to meet it would build a desk
    # nobody can sit at; the remainder becomes a ledge below.
    top_h = h if h <= DESK_TOP_MAX + 1e-9 else DESK_WORK_H
    leg_h = top_h - TOP_T
    runs = bays(w, bay_max_of(plan))
    rows = bays(d, _row_max_of(plan))
    for ri, (ry, rd) in enumerate(rows):
        # back-to-back: alternate rows face opposite ways, which is what a
        # cubicle block is. `face` flips every -Y (the sitter's side).
        face = 1 if ri % 2 == 0 else -1
        rtag = "" if len(rows) == 1 else f"_R{ri + 1}"
        # top slab, the full run of this row
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, ry, top_h - TOP_T / 2), (w, rd, TOP_T))
        part(bm, f"Desk_Top{rtag}")
        cboxes.append(((-w / 2, ry - rd / 2, top_h - TOP_T),
                       (w / 2, ry + rd / 2, top_h)))
        for bi, (bx, bw) in enumerate(runs):
            tag = rtag + ("" if len(runs) == 1 else f"_B{bi + 1}")
            # legs
            if leg_style == "panel":
                for side, sx in (("L", -1), ("R", 1)):
                    x = bx + sx * (bw / 2 - PANEL_T / 2)
                    bm = geometry.new_bm()
                    geometry.add_box(bm, (x, ry, leg_h / 2),
                                     (PANEL_T, rd * 0.92, leg_h))
                    part(bm, f"Desk_Leg_{side}{tag}")
                    cboxes.append(((x - PANEL_T / 2, ry - rd * 0.46, 0),
                                   (x + PANEL_T / 2, ry + rd * 0.46, leg_h)))
            else:  # post
                inset = 0.06
                i = 0
                for sx in (-1, 1):
                    for sy in (-1, 1):
                        i += 1
                        x = bx + sx * (bw / 2 - inset)
                        y = ry + sy * (rd / 2 - inset)
                        bm = geometry.new_bm()
                        geometry.add_box(bm, (x, y, leg_h / 2),
                                         (POST_S, POST_S, leg_h))
                        part(bm, f"Desk_Leg_{i}{tag}")
                        cboxes.append(((x - POST_S / 2, y - POST_S / 2, 0),
                                       (x + POST_S / 2, y + POST_S / 2, leg_h)))

            # drawer pedestal (right side of the bay), fronts proud toward
            # the row's own front -- `face` is -Y for row 1 and +Y for the
            # row butted against its back.
            if n_drawers > 0:
                ped_x = bx + bw / 2 - PANEL_T - PED_W / 2 - 0.01
                ped_h = leg_h - 0.02
                bm = geometry.new_bm()
                geometry.add_box(bm, (ped_x, ry + face * 0.01, ped_h / 2),
                                 (PED_W, rd * 0.9 - 0.02, ped_h))
                part(bm, f"Desk_Pedestal{tag}")
                cboxes.append(((ped_x - PED_W / 2, ry - rd * 0.45, 0),
                               (ped_x + PED_W / 2, ry + rd * 0.45, ped_h)))
                gap = 0.012
                dh = (ped_h - gap * (n_drawers + 1)) / n_drawers
                front_y = ry + face * (0.01 - (rd * 0.9 - 0.02) / 2 - 0.008)
                for i in range(n_drawers):
                    z = gap + dh / 2 + i * (dh + gap)
                    bm = geometry.new_bm()
                    geometry.add_box(bm, (ped_x, front_y, z),
                                     (PED_W - 0.03, 0.018, dh))
                    part(bm, f"Desk_Drawer_{i + 1}{tag}")
                    # bar handle
                    bm = geometry.new_bm()
                    geometry.add_box(bm, (ped_x, front_y - face * 0.018, z),
                                     (PED_W * 0.45, 0.015, 0.015))
                    part(bm, f"Desk_Handle_{i + 1}{tag}")

            # modesty panel at the back
            if plan["params"].get("modesty_panel"):
                span = bw - 2 * PANEL_T if leg_style == "panel" else bw - 0.3
                if n_drawers > 0:
                    span = max(0.2, span - PED_W)
                mp_x = bx + (-(bw - span) / 2 + PANEL_T if n_drawers > 0 else 0)
                bm = geometry.new_bm()
                geometry.add_box(bm, (mp_x, ry - face * (rd / 2 - 0.02),
                                      leg_h * 0.62),
                                 (span, 0.02, leg_h * 0.55))
                part(bm, f"Desk_ModestyPanel{tag}")

    # THE TRANSACTION LEDGE, when the slot is taller than a work surface.
    if h - top_h > LEDGE_MIN:
        ly = d / 2 - LEDGE_D / 2
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, ly, h - TOP_T / 2), (w, LEDGE_D, TOP_T))
        part(bm, "Desk_Ledge")
        bm = geometry.new_bm()
        geometry.add_box(bm, (0, d / 2 - 0.02, (top_h + h) / 2 - TOP_T / 2),
                         (w, 0.03, h - top_h - TOP_T))
        part(bm, "Desk_LedgeFascia")
        cboxes.append(((-w / 2, d / 2 - LEDGE_D, top_h), (w / 2, d / 2, h)))

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
        # the work surface, not the ledge: something set down on a desk
        # sits where a person can reach it.
        "attachments": {"ATT_surface_center": (0, 0, top_h)},
    }
