"""ATM recipe: a 1990s freestanding surcharge ATM, two atlases, two draws.

Zoo 1.35.0. Planned in pure Python by `core.atm_forms.plan`: every face is a
quad naming a tile. `recipes/_card_atlas.build_art` builds the PAINT tiles --
the cabinet, the trim, the fascia, the keypad -- into one object with one
painted material, and the GLOW tiles -- the CRT and the topper -- into one
more with one backlit material named `_Face`, so a power cut takes them.
Origin at the floor's centre, the customer at -Y.
"""
from __future__ import annotations

from ..core import atm_forms as AF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    variant = int(params.get("variant", 0) or 0)
    sign = bool(params.get("sign", 1))
    got = AF.plan(w, d, h, variant, sign)
    from ._card_atlas import build_art, build_shutters
    objs = []
    for atlas_name, lit in (("paint", None), ("glow", (AF.GLOW_EMISSION, AF.GLOW_ALBEDO))):
        tiles = {k: spec for k, (a, spec) in got["tiles"].items() if a == atlas_name}
        prims = [p for p in got["prims"] if p["mat"] == atlas_name]
        name = "ATM" if atlas_name == "paint" else "ATMGlow"
        o, atlas = build_art(prims, collection, dict(plan, _tiles=tiles), streams, name, lit=lit)
        objs += o
    # the screen's shutters (1.45.0): one more object, drawn by the consumer
    objs += build_shutters(got["prims"], collection, streams, "ATM", AF.SHUTTER_RGB)
    f = got["facts"]
    print(f"[atm] {w:.2f} x {d:.2f} x {h:.2f} network={f['network']} sign={f['sign']} "
          f"{f['tris']} tris, 3 materials")
    return {"objects": objs, "collision_boxes": [got["collision"]], "attachments": {},
            "atm": {"network": f["network"], "sign": f["sign"]}}
