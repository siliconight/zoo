"""aisle_sign recipe: the hand-lettered sign hung over an aisle.

Zoo 0.98.0. Planned by `core.flat_forms.plan_aisle_sign`; both faces of the
board carry ONE art tile through `recipes/_card_atlas.py`.

THE BOARD KEEPS THE SLOT'S OWN COLOUR and the lettering is the tile's. This
is the one species in the flat-art set that does NOT take a game's palette:
a section sign is board and marker, and colouring it by whatever game the
rotation landed on would say the aisle belongs to that game, which is a
claim the sign is not making. The words are `card_brands.AISLE_SAYS`.

WHAT IT HANGS FROM: see `flat_forms.HANG_NOTE` -- the top of the slot box
is the ceiling plane, and the genome's height cap is derived from the
contract's headroom.
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
    stem = (plan.get("module") or {}).get("stem") or "aisle_sign"
    got = FF.plan_aisle_sign(w, d, h, params, params.get("variant") or 0,
                             key=stem)
    f = got["facts"]

    mats = {
        FF.BOARD: (f"M_AisleSign_board_{plan['material']}",
                   list(plan["color"]), plan["material"]),
        FF.CHAIN: ("M_AisleSign_chain_metal_bare", [0.34, 0.35, 0.37], "metal_bare"),
    }
    solid = [p for p in got["prims"] if not p.get("tile")]
    objs = prim_mesh.build(solid, collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    from ._card_atlas import build_art
    art, atlas = build_art(got["prims"], collection,
                           dict(plan, _tiles=got["tiles"]), streams,
                           "AisleSign", roughness=FA.HANGER_ROUGHNESS)
    objs += art

    png, raw = FA.atlas_bytes(atlas) if atlas else (0, 0)
    print(f"[aisle_sign] {w:.2f} x {d:.2f} x {h:.2f} says={f['says']!r} "
          f"drop={f['drop_m']:.2f} board={f['board_m']:.2f} "
          f"variant={f['variant']} atlas={atlas['name'] if atlas else '-'} "
          f"({png / 1024.0:.1f} KiB png, {raw / 1048576.0:.3f} MiB raw) "
          f"{f['tris']} tris (pure)")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {},
            "aisle_sign": dict(f, atlas=atlas["name"] if atlas else None,
                               atlas_png_bytes=png, atlas_raw_bytes=raw)}
