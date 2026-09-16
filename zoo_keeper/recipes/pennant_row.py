"""pennant_row recipe: the strip of angled felt pennants along a wall top.

Planned in pure Python by `core.pennant_forms`. Flat, untextured and cheap on
purpose: the cap on how many pennants a strip carries is DERIVED from the
genome's triangle budget (`pennant_forms.max_pennants`), so raising the budget
raises the count and nothing else in the species has to move.

ONE MATERIAL PER TEAM COLOUR, not per pennant. A strip draws its `colours`
pairs whatever its length -- the felt and the hoist band of one team share
the pair -- so a 44-pennant strip is 12 materials rather than 88.

COLLISION: NONE, and the genome agrees. A pennant hangs at ceiling height,
a body cannot reach it, and a collider up there is a shape the navmesh bake
has to carry for nothing.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import pennant_forms as PN


def _hx(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    budget = int((plan.get("budgets") or {}).get("tris_lod0") or 900)
    got = PN.plan(w, d, h, params, params.get("variant") or 0,
                  key=(plan.get("module") or {}).get("stem") or "pennant_row",
                  budget=budget)

    mats = {PN.BATTEN: (f"M_PennantRow_batten_{plan['material']}",
                        list(plan["color"]), plan["material"])}
    prims = []
    for p in got["prims"]:
        i = p.get("colour_index")
        if i is None:
            prims.append(p)
            continue
        primary, second = got["colours"][i]
        rgb = primary if p["mat"] == PN.FELT else second
        key = f"{p['mat']}{i}"
        mats.setdefault(key, (f"M_PennantRow_{p['mat']}_{_hx(rgb)}_cloth",
                              list(rgb), "cloth"))
        q = dict(p)
        q["mat"] = key
        prims.append(q)

    objs = prim_mesh.build(prims, collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    f = got["facts"]
    print(f"[pennant_row] {w:.2f} x {d:.2f} x {h:.2f} pennants={f['pennants']} "
          f"(cap {f['cap']} from a {budget} budget) colours={f['colours']} "
          f"pitch={f['pitch_m']:.3f} variant={f['variant']} "
          f"teams={','.join(f['teams'][:3])} {f['tris']} tris (pure)")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {}, "pennant_row": dict(f)}
