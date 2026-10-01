"""Pump recipe: a 1997 two-sided mechanical gas pump, two atlases, two draws.

Zoo 1.36.0, replacing the placeholder box minted 2026-09-12. Planned in pure
Python by `core.pump_forms.plan`: every face is a quad or a tube naming a
tile. `recipes/_card_atlas.build_art` builds the PAINT tiles -- the grade
panels, the base, the nozzles and hoses -- into one object with one painted
material, and the GLOW tiles -- the price wheels and the header -- into one
more with one backlit material named `_Face`, so a power cut takes them.
Origin at the floor's centre; the faces are the slot's two long sides.
"""
from __future__ import annotations

from ..core import pump_forms as PF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    module = plan.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    got = PF.plan(w, d, h, variant)
    from ._card_atlas import build_art
    objs = []
    for atlas_name, lit in (("paint", None), ("glow", (PF.GLOW_EMISSION, PF.GLOW_ALBEDO))):
        tiles = {k: spec for k, (a, spec) in got["tiles"].items() if a == atlas_name}
        prims = [p for p in got["prims"] if p["mat"] == atlas_name]
        name = "Pump" if atlas_name == "paint" else "PumpGlow"
        o, _atlas = build_art(prims, collection, dict(plan, _tiles=tiles), streams, name, lit=lit)
        objs += o
    f = got["facts"]
    print(f"[pump] {w:.2f} x {d:.2f} x {h:.2f} faces={f['faces']} prices={','.join(f['prices'])} "
          f"{f['tris']} tris, 2 materials")
    return {"objects": objs, "collision_boxes": got["collision"], "attachments": {},
            "pump": {"prices": list(f["prices"]), "faces": f["faces"]}}
