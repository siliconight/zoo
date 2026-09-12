"""teller_line recipe: a bank teller line (intact state).

An interactive architectural module. Center-pivot, fit-to-exact-dims: a solid
COUNTER base (floor to waist), POSTS and a HEADER framing the glass above it,
and a bulletproof GLASS barrier with one SERVICE WINDOW per station -- a
pass-through opening at counter height where the tray sits. The counter,
frame and glass all block, so an intact teller line is a barrier; the
service openings are the only holes in it.

WHAT IT IS A DRAWING OF (roadmap 44, 2026-09-12, from the walker's
references: a Chase branch line, a bank service window, a teller window
under construction). A continuous counter at 1.0-1.1 m; a glass barrier
from the counter to a header at 2.1-2.4 m; posts between stations every
1.8-2.0 m; per station a service opening at the counter with a deal tray
and a speak-through. This recipe builds that per BAY (`_bays.bays`, at most
`bay_max` per station, genome params): the counter and header run the full
width, a post stands at every bay boundary, and each bay's glass carries
its own service opening.

This builds only the intact state. Its `shattered` state reuses this same
species art (the resolver falls back to the base) until a shattered-glass
art pass gives it distinct geometry. The frame + counter tile the exact
(w, d, h) box, so fit-to-exact-dims holds; the glass sits inside.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import arch
from ._bays import bay_max_of, bays


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

    # solid counter (floor -> waist), the full run
    box(f"{root}_Counter", (0.0, 0.0, -hh + counter_h / 2.0), (w, d, counter_h))
    # header, the full run
    if header > 1e-4:
        box(f"{root}_Header", (0.0, 0.0, (header_bot + hh) / 2.0),
            (w - 2.0 * post, d, header))

    # BAYS: a post at the two ends and at every station boundary; one
    # glass panel with a service opening per station.
    runs = bays(w, bay_max_of(plan))
    edges = [-hw + post / 2.0] + [bx + bw / 2.0 for bx, bw in runs[:-1]] + [hw - post / 2.0]
    if post > 1e-4:
        for i, x in enumerate(edges):
            tag = "L" if i == 0 else ("R" if i == len(edges) - 1 else "M%d" % i)
            box(f"{root}_Post_{tag}", (x, 0.0, (counter_top + hh) / 2.0),
                (post, d, hh - counter_top))

    glass_th = max(0.02, float(p.get("glass_frac", 0.12)) * d)
    glass_mat = materials.make_material(
        "M_TellerLine_glass", plan.get("glass_color", [0.6, 0.7, 0.74]),
        "glass")
    for bi, (bx, bw) in enumerate(runs):
        tag = "" if len(runs) == 1 else f"_B{bi + 1}"
        pane_w = bw - post
        if pane_w <= 0.05:
            continue
        # THE SERVICE WINDOW: an opening at the counter, wide enough for a
        # deal tray and a pair of hands, low enough that the glass above
        # it still reads as a barrier. `slot_w` / `slot_h` are the genome's
        # pass-through; the window is that opening sized to a station.
        slot_w = min(float(p.get("slot_w", 0.40)) * 2.0, pane_w * 0.6)
        slot_h = min(float(p.get("slot_h", 0.22)) * 2.0, open_h * 0.5)
        void = {"x0": -slot_w / 2.0, "x1": slot_w / 2.0,
                "z0": -open_h / 2.0, "z1": -open_h / 2.0 + slot_h}
        panels = arch.slab_parts(pane_w, glass_th, open_h, void)
        for name, c, s in panels:
            bm = geometry.new_bm()
            geometry.add_box(bm, (bx + c[0], 0.0, c[2] + open_cz), s)
            obj = geometry.bm_to_object(bm, f"{root}_Glass_{name}{tag}", collection,
                                        bevel=0.0, texel=1.2, rng=rng,
                                        wear=wear * 0.3)
            glassboxes.append(obj)
            lo = (bx + c[0] - s[0] / 2.0, -s[1] / 2.0, c[2] + open_cz - s[2] / 2.0)
            hi = (bx + c[0] + s[0] / 2.0, s[1] / 2.0, c[2] + open_cz + s[2] / 2.0)
            cboxes.append((lo, hi))          # bulletproof -> glass panels collide
    materials.assign(glassboxes, glass_mat)
    body = materials.make_material(
        f"M_TellerLine_{plan['material']}", plan["color"], plan["material"])
    materials.assign(structure, body)
    attachments = {f"ATT_tray{'' if len(runs) == 1 else '_B%d' % (i + 1)}":
                   (bx, -d / 2.0, counter_top) for i, (bx, bw) in enumerate(runs)}
    return {"objects": structure + glassboxes, "collision_boxes": cboxes,
            "attachments": attachments}
