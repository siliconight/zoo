"""poster_wall recipe: a run of posters, one atlas, one mesh, one draw.

Zoo 1.30.0. Planned in pure Python by `core.poster_wall_forms.plan`; every
sheet is an ART QUAD naming a tile, and `recipes/_card_atlas.py` paints them
into one atlas and builds them into ONE object with ONE painted material --
the road `pack_wall` and `display_case` already take. The posters are paper
lit by the room: paint, not light, as `_card_atlas` says a poster is.
"""
from __future__ import annotations

from ..core import flat_art as FA
from ..core import poster_wall_forms as PWF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    family = str(params.get("form") or "club")
    if family == "auto":
        family = "club"
    variant = int(params.get("variant", 0) or 0)
    stem = (plan.get("module") or {}).get("stem") or "poster_wall"
    got = PWF.plan(w, d, h, family, variant, key=stem)
    from ._card_atlas import build_art
    objs, atlas = build_art(got["prims"], collection, dict(plan, _tiles=got["tiles"]), streams,
                            "PosterWall", roughness=FA.POSTER_ROUGHNESS)
    f = got["facts"]
    png, raw = FA.atlas_bytes(atlas) if atlas else (0, 0)
    print(f"[poster_wall] {w:.2f} x {d:.3f} x {h:.2f} family={family} sheets={f['sheets']} "
          f"courses={f['courses']} atlas={atlas['name'] if atlas else '-'} "
          f"({png / 1024.0:.1f} KiB png, {raw / 1048576.0:.3f} MiB raw) {f['tris']} tris")
    return {"objects": objs, "collision_boxes": [], "attachments": {},
            "poster_wall": dict(f, atlas=atlas["name"] if atlas else None,
                                atlas_png_bytes=png, atlas_raw_bytes=raw)}
