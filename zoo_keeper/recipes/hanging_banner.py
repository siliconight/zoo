"""hanging_banner recipe: the printed cloth hung above the shelving.

Zoo 0.98.0. Planned by `core.flat_forms.plan_banner`; the printed face is
one art quad through `recipes/_card_atlas.py`.

THE ROD AND THE HEM WEAR THE GAME'S OWN DARK, not the room's grey. A prop
that falls back to the building default disappears into it (the contrast
rule `_shelf_stock` and `_surface_stock` both keep), and a banner's
hardware is the one part of it a shopper sees against the wall.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import flat_art as FA
from ..core import flat_forms as FF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    stem = (plan.get("module") or {}).get("stem") or "hanging_banner"
    got = FF.plan_banner(w, d, h, params, params.get("variant") or 0, key=stem)
    f = got["facts"]

    mats = {
        FF.CLOTH: (f"M_Banner_cloth_{plan['material']}",
                   list(f["cloth_rgb"]), plan["material"]),
        FF.CHAIN: ("M_Banner_rod_metal_painted", list(f["rod_rgb"]),
                   "metal_painted"),
    }
    solid = [p for p in got["prims"] if not p.get("tile")]
    objs = prim_mesh.build(solid, collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    from ._card_atlas import build_art
    art, atlas = build_art(got["prims"], collection,
                           dict(plan, _tiles=got["tiles"]), streams, "Banner",
                           roughness=FA.BANNER_ROUGHNESS)
    objs += art

    png, raw = FA.atlas_bytes(atlas) if atlas else (0, 0)
    print(f"[hanging_banner] {w:.2f} x {d:.2f} x {h:.2f} game={f['game']} "
          f"cloth={f['cloth_m'][0]:.2f} x {f['cloth_m'][1]:.2f} "
          f"variant={f['variant']} atlas={atlas['name'] if atlas else '-'} "
          f"({png / 1024.0:.1f} KiB png, {raw / 1048576.0:.3f} MiB raw) "
          f"{f['tris']} tris (pure)")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {},
            "hanging_banner": dict(f, atlas=atlas["name"] if atlas else None,
                                   atlas_png_bytes=png, atlas_raw_bytes=raw)}
