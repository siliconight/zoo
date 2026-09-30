"""pole_flyers recipe: a sleeve of flyers round a pole, one atlas, one mesh, one draw.

Zoo 1.34.0. Planned in pure Python by `core.pole_flyers_forms.plan`; every
sheet is a curved strip of ART facets naming a tile, and
`recipes/_card_atlas.py` paints them into one atlas and builds them into ONE
object with ONE painted material -- the road `poster_wall` takes. Paper lit by
the street: paint, not light.
"""
from __future__ import annotations

from ..core import flat_art as FA
from ..core import pole_flyers_forms as PFF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    form = str(params.get("form") or "stack")
    if form == "auto":
        form = "stack"
    variant = int(params.get("variant", 0) or 0)
    stem = (plan.get("module") or {}).get("stem") or "pole_flyers"
    got = PFF.plan(w, d, h, form, variant, key=stem)
    from ._card_atlas import build_art
    objs, atlas = build_art(got["prims"], collection, dict(plan, _tiles=got["tiles"]), streams,
                            "PoleFlyers", roughness=FA.POSTER_ROUGHNESS)
    f = got["facts"]
    png, raw = FA.atlas_bytes(atlas) if atlas else (0, 0)
    print(f"[pole_flyers] {w:.3f} x {d:.3f} x {h:.2f} form={form} sheets={f['sheets']} "
          f"atlas={atlas['name'] if atlas else '-'} ({png / 1024.0:.1f} KiB png, "
          f"{raw / 1048576.0:.3f} MiB raw) {f['tris']} tris")
    return {"objects": objs, "collision_boxes": [], "attachments": {},
            "pole_flyers": dict({k: v for k, v in f.items() if k != "pieces"},
                                atlas=atlas["name"] if atlas else None,
                                atlas_png_bytes=png, atlas_raw_bytes=raw)}
