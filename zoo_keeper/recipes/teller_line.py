"""teller_line recipe: a bank teller line (intact state).

An interactive architectural module. Center-pivot, fit-to-exact-dims: a solid
COUNTER base (floor to waist), two side POSTS + a HEADER framing the opening
above it, and a bulletproof GLASS barrier filling that opening with a central
transaction PASS-SLOT (money slides through -> no collision there). The counter,
frame and glass all block, so an intact teller line is a barrier.

This builds only the intact state. Its `shattered` state reuses this same
species art (the resolver falls back to the base) until a shattered-glass art
pass gives it distinct geometry -- same progressive-art-pass deal as a broken
window or an unlocked vault. The frame + counter tile the exact (w, d, h) box,
so fit-to-exact-dims holds; the glass sits inside.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import arch


def build(plan, streams, collection):
    dims = plan["dimensions"]
    w, d, h = dims["width"], dims["depth"], dims["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    p = plan.get("params", {})
    rng = streams.stream("wear")
    root = arch.root_name("teller_line")          # "TellerLine"

    counter_h = min(float(p.get("counter_h", 1.1)), h * 0.6)
    post = min(float(p.get("post", 0.10)), w * 0.3)
    header = min(float(p.get("header", 0.20)), (h - counter_h) * 0.5)
    hw, hh = w / 2.0, h / 2.0

    counter_top = -hh + counter_h
    header_bot = hh - header
    open_w = w - 2.0 * post
    open_h = header_bot - counter_top
    open_cz = (counter_top + header_bot) / 2.0

    structure, glassboxes = [], []
    cboxes = []

    def box(name, center, size, wr=wear):
        bm = geometry.new_bm()
        geometry.add_box(bm, center, size)
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                    texel=1.2, rng=rng, wear=wr)
        structure.append(obj)
        lo = tuple(center[i] - size[i] / 2.0 for i in range(3))
        hi = tuple(center[i] + size[i] / 2.0 for i in range(3))
        cboxes.append((lo, hi))
        return obj

    # solid counter (floor -> waist), then the frame around the glass opening
    box(f"{root}_Counter", (0.0, 0.0, -hh + counter_h / 2.0), (w, d, counter_h))
    if post > 1e-4 and open_w > 0.05:
        box(f"{root}_Post_L", (-hw + post / 2.0, 0.0,
                               (counter_top + hh) / 2.0),
            (post, d, hh - counter_top))
        box(f"{root}_Post_R", (hw - post / 2.0, 0.0,
                               (counter_top + hh) / 2.0),
            (post, d, hh - counter_top))
    if header > 1e-4:
        box(f"{root}_Header", (0.0, 0.0, (header_bot + hh) / 2.0),
            (open_w, d, header))

    # bulletproof GLASS filling the opening, thin + centered in depth, with a
    # central transaction slot (built as slab panels around a bottom-centre
    # void). The glass blocks (bulletproof) -> it gets collision; the slot does
    # not (that's the pass-through).
    glass_th = max(0.02, float(p.get("glass_frac", 0.12)) * d)
    slot_w = min(float(p.get("slot_w", 0.40)), open_w * 0.6)
    slot_h = min(float(p.get("slot_h", 0.22)), open_h * 0.5)
    void = {"x0": -slot_w / 2.0, "x1": slot_w / 2.0,
            "z0": -open_h / 2.0, "z1": -open_h / 2.0 + slot_h}
    panels = arch.slab_parts(open_w, glass_th, open_h, void)
    glass_mat = materials.make_material(
        "M_TellerLine_glass", plan.get("glass_color", [0.6, 0.7, 0.74]),
        "glass")
    for name, c, s in panels:
        bm = geometry.new_bm()
        geometry.add_box(bm, (c[0], 0.0, c[2] + open_cz), s)
        obj = geometry.bm_to_object(bm, f"{root}_Glass_{name}", collection,
                                    bevel=0.0, texel=1.2, rng=rng,
                                    wear=wear * 0.3)
        glassboxes.append(obj)
        lo = (c[0] - s[0] / 2.0, -s[1] / 2.0, c[2] + open_cz - s[2] / 2.0)
        hi = (c[0] + s[0] / 2.0, s[1] / 2.0, c[2] + open_cz + s[2] / 2.0)
        cboxes.append((lo, hi))          # bulletproof -> glass panels collide
    materials.assign(glassboxes, glass_mat)

    body = materials.make_material(
        f"M_TellerLine_{plan['material']}", plan["color"], plan["material"])
    materials.assign(structure, body)

    return {"objects": structure + glassboxes, "collision_boxes": cboxes,
            "attachments": {}}
