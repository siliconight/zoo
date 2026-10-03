"""dumpster recipe: a front-load commercial trash container, one atlas, one
draw.

Zoo 1.58.0. Planned in pure Python by `core.dumpster_forms.plan`: every face
is a quad naming a tile, and `recipes/_card_atlas.build_art` builds them
into one object on one painted image -- the hauler's fleet colour, the
rust, the sticker and the lids' ribs are all paint. See that module for the
reference and the haulers. Origin on the ground under the middle; the front
(the sticker, the low edge) at -Y, the hinges and the wall behind at +Y.

Collision is the whole container: a body walks round a dumpster, and stands
behind one.
"""
from __future__ import annotations

from ..core import dumpster_forms as DF

#: Painted steel and moulded plastic, outdoors: neither card nor gloss.
ROUGHNESS = 0.62


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    variant = int(params.get("variant", 0) or 0)
    got = DF.plan(w, d, h, variant)
    from ._card_atlas import build_art
    tiles = {k: spec for k, (_a, spec) in got["tiles"].items()}
    objs, _atlas = build_art(got["prims"], collection, dict(plan, _tiles=tiles), streams,
                             "Dumpster", roughness=ROUGHNESS, smooth=True)
    f = got["facts"]
    print(f"[dumpster] {w:.2f} x {d:.2f} x {h:.2f} hauler={f['hauler']} {f['tris']} tris, 1 material")
    return {"objects": objs, "collision_boxes": [got["collision"]], "attachments": {},
            "dumpster": {"hauler": f["hauler"]}}
