"""litter_bin recipe: a 1990s municipal street bin (Zoo 1.92.0, roadmap 219 note 5).

Until 1.92.0 this was the PLACEHOLDER SILHOUETTE `tools/new_species.py` minted on 2026-09-12: one
grey box at each crossing. Every prim and tile is `core.litter_bin_forms`, which is pure and
tested: a square body of vertical slats in the township's green, a lid with a square mouth and
the bag showing in it, four short feet, and a placard on two faces. One atlas and one material,
so one draw a bin, as the dumpster's.
"""
from __future__ import annotations

from ..core import litter_bin_forms as LB

#: Painted steel outdoors: neither card nor gloss, as the dumpster's.
ROUGHNESS = 0.62


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    got = LB.plan(w, d, h)
    from ._card_atlas import build_art
    tiles = {k: spec for k, (_a, spec) in got["tiles"].items()}
    objs, _atlas = build_art(got["prims"], collection, dict(plan, _tiles=tiles), streams,
                             "LitterBin", roughness=ROUGHNESS, smooth=True)
    f = got["facts"]
    print(f"[litter_bin] {w:.2f} x {d:.2f} x {h:.2f} {f['tris']} tris, 1 material")
    return {"objects": objs, "collision_boxes": [got["collision"]], "attachments": {}}
