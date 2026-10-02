"""Video-poker recipe: a 1997 tavern upright, "for amusement only", two draws.

Zoo 1.39.0. Planned in pure Python by `core.video_poker_forms.plan`: every
face is a quad naming a tile. `recipes/_card_atlas.build_art` builds the PAINT
tiles -- cabinet, trim, belly glass, button deck -- into one object with one
painted material, and the GLOW tiles -- the CRT and the marquee -- into one
more with one backlit material named `_Face`, so a power cut takes them.
Origin at the floor's centre, the player at -Y.
"""
from __future__ import annotations

from ..core import video_poker_forms as VF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    module = plan.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    got = VF.plan(w, d, h, variant)
    from ._card_atlas import build_art, build_shutters
    objs = []
    for atlas_name, lit in (("paint", None), ("glow", (VF.GLOW_EMISSION, VF.GLOW_ALBEDO))):
        tiles = {k: spec for k, (a, spec) in got["tiles"].items() if a == atlas_name}
        prims = [p for p in got["prims"] if p["mat"] == atlas_name]
        name = "VideoPoker" if atlas_name == "paint" else "VideoPokerGlow"
        o, _atlas = build_art(prims, collection, dict(plan, _tiles=tiles), streams, name, lit=lit,
                              smooth=True)
        objs += o
    # the deal's shutters (1.45.0): one more object, drawn by the consumer
    objs += build_shutters(got["prims"], collection, streams, "VideoPoker", VF.SHUTTER_RGB)
    f = got["facts"]
    print(f"[video_poker] {w:.2f} x {d:.2f} x {h:.2f} brand={f['brand']} {f['tris']} tris, 3 materials")
    return {"objects": objs, "collision_boxes": [got["collision"]], "attachments": {},
            "video_poker": {"brand": f["brand"]}}
