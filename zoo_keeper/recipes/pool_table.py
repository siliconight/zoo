"""pool_table recipe: a 1990s coin-op bar pool table, with the game left on it.

Planned in pure Python by `core.pool_table_forms` (parts and rules in its
docstring) and built vertex for vertex by `bpylayer.prim_mesh`. Rails and
corner posts take the genome's colour and kind; the cabinet is that colour
darkened; the cloth is one of the three 1997 bar colours, drawn per seed;
castings, cushions, sights, coin slide, balls and cue are sub-part
finishes from `pool_table_forms.MATERIALS` and `BALLS`.

Collision is the table's box: nobody walks through a pool table, and a
body crouched behind one has the cover a bar fight actually offers.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import pool_table_forms


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    got = pool_table_forms.plan(w, d, h, streams.stream("form"))
    kind = plan["material"]
    colour = list(plan["color"])
    mats = {key: (f"M_PoolTable_{key}_{k}", list(c), k)
            for key, (c, k) in pool_table_forms.MATERIALS.items()}
    for key, c in pool_table_forms.BALLS.items():
        mats[key] = (f"M_PoolTable_{key}_plastic", list(c), "plastic")
    mats["rail"] = (f"M_PoolTable_rail_{kind}", colour, kind)
    mats["cabinet"] = (f"M_PoolTable_cabinet_{kind}", [v * 0.72 for v in colour], kind)
    cloth = pool_table_forms.CLOTHS[got["cloth"]]
    mats["cloth"] = (f"M_PoolTable_cloth_{got['cloth']}_canvas", list(cloth), "canvas")
    objs = prim_mesh.build(got["prims"], collection, plan,
                           streams.stream("wear"), mats, texel=1.2)
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_surface_center": (0.0, 0.0, h)}}
