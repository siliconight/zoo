"""safe_deposit_boxes recipe: a vault-room wall of deposit boxes (intact state).

An interactive architectural module. Center-pivot, fit-to-exact-dims: a solid
metal BACKING slab (rear of the depth) plus a bordered GRID of raised DIVIDERS
on the front, so the compartments between them read as the little numbered
boxes. The backing reaches the exact (w, d, h) box on width/height/rear and the
dividers reach the front, so fit-to-exact-dims holds; the wall is solid (one
collision box).

Cheap by construction: (cols+1) vertical + (rows+1) horizontal dividers, not a
box per cell, and the grid is capped so a big wall stays low-poly. Builds only
the intact state; a `drilled` state reuses this art (resolver falls back to the
base) until a drilled-boxes art pass. Numbers, handles and keyholes are a Delco
art pass.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import arch


def _grid_count(usable, cell, cap):
    n = int(round(usable / cell)) if cell > 1e-6 else 1
    return max(1, min(n, int(cap)))


def build(plan, streams, collection):
    dims = plan["dimensions"]
    w, d, h = dims["width"], dims["depth"], dims["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    p = plan.get("params", {})
    rng = streams.stream("wear")
    root = arch.root_name("safe_deposit_boxes")   # "SafeDepositBoxes"

    cell = float(p.get("cell", 0.22))
    bar = float(p.get("bar", 0.03))
    margin = min(float(p.get("margin", 0.06)), min(w, h) * 0.3)
    cap_c = int(p.get("max_cols", 16))
    cap_r = int(p.get("max_rows", 16))

    objs, cboxes = [], []

    def emit(name, center, size, wr=wear):
        bm = geometry.new_bm()
        geometry.add_box(bm, center, size)
        objs.append(geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                          texel=1.2, rng=rng, wear=wr))

    # solid metal backing: rear 70% of the depth, full w x h -> defines the
    # exact envelope on width/height and the rear face.
    back_d = d * 0.7
    emit(f"{root}_Backing", (0.0, -d / 2.0 + back_d / 2.0, 0.0), (w, back_d, h))

    # front dividers live in the front 30% of the depth, reaching +d/2.
    front_d = d * 0.3
    fy = d / 2.0 - front_d / 2.0

    uw = max(0.05, w - 2.0 * margin)
    uh = max(0.05, h - 2.0 * margin)
    cols = _grid_count(uw, cell, cap_c)
    rows = _grid_count(uh, cell, cap_r)
    cw, ch = uw / cols, uh / rows

    # vertical dividers at every column boundary (cols + 1), spanning usable h
    for i in range(cols + 1):
        x = -uw / 2.0 + i * cw
        c = (x, fy, 0.0)
        s = (bar, front_d, uh)
        emit(f"{root}_Divider_V{i}", c, s, wr=wear * 0.9)
    # horizontal dividers at every row boundary (rows + 1), spanning usable w
    for j in range(rows + 1):
        z = -uh / 2.0 + j * ch
        c = (0.0, fy, z)
        s = (uw, front_d, bar)
        emit(f"{root}_Divider_H{j}", c, s, wr=wear * 0.9)

    materials.assign(objs, materials.make_material(
        f"M_SafeDepositBoxes_{plan['material']}", plan["color"],
        plan["material"]))

    # the wall is solid -> a single envelope collision box (no walking through)
    cboxes.append(((-w / 2.0, -d / 2.0, -h / 2.0),
                   (w / 2.0, d / 2.0, h / 2.0)))

    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
