"""ceiling_hanger recipe: the painted board on a drop chain.

Zoo 0.98.0, and the first thing this pipeline has hung from a ceiling.
Planned by `core.flat_forms.plan_hanger`; both faces of the board carry ONE
art tile through `recipes/_card_atlas.py`.

WHAT IT HANGS FROM: `flat_forms.HANG_NOTE` and the genome's `notes` carry
the whole answer, and the short version is that the top of the slot box IS
the ceiling plane. There is no grid geometry to hang from -- a dropped
ceiling here is one solid slab with a Pixelcoat `ceiling_tile` skin -- and
Deli Counter's `mount: "hang"` is the LIGHT pipeline. The hanging point
that exists is `level_design._piece`'s `under`, which `pennant_row` has
used since 0.95.0.

COLLISION: none, and the genome agrees. The species' height is capped at
`flat_forms.hang_max_height()` so the board's bottom stays above the
contract's 2.0 m headroom at the library's shortest storey.
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
    stem = (plan.get("module") or {}).get("stem") or "ceiling_hanger"
    got = FF.plan_hanger(w, d, h, params, params.get("variant") or 0, key=stem)
    f = got["facts"]

    mats = {
        FF.BOARD: (f"M_Hanger_board_{plan['material']}",
                   list(f["board_rgb"]), plan["material"]),
        FF.CHAIN: ("M_Hanger_chain_metal_bare", list(f["chain_rgb"]), "metal_bare"),
    }
    solid = [p for p in got["prims"] if not p.get("tile")]
    objs = prim_mesh.build(solid, collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    from ._card_atlas import build_art
    art, atlas = build_art(got["prims"], collection,
                           dict(plan, _tiles=got["tiles"]), streams, "Hanger",
                           roughness=FA.HANGER_ROUGHNESS)
    objs += art

    png, raw = FA.atlas_bytes(atlas) if atlas else (0, 0)
    print(f"[ceiling_hanger] {w:.2f} x {d:.2f} x {h:.2f} game={f['game']} "
          f"drop={f['drop_m']:.2f} board={f['board_m']:.2f} "
          f"variant={f['variant']} atlas={atlas['name'] if atlas else '-'} "
          f"({png / 1024.0:.1f} KiB png, {raw / 1048576.0:.3f} MiB raw) "
          f"{f['tris']} tris (pure)")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {},
            "ceiling_hanger": dict(f, atlas=atlas["name"] if atlas else None,
                                   atlas_png_bytes=png, atlas_raw_bytes=raw)}
