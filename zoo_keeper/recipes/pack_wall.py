"""pack_wall recipe: a gondola bay of booster displays under a header sign.

Planned in pure Python by `core.pack_wall_forms` and built by
`bpylayer.prim_mesh`, except the ART QUADS -- the header signs and every
faced-out product -- which go into one atlas through `recipes/_card_atlas.py`.

A WIDE SLOT IS BAYS, not one wide bay: ``bay_max`` divides it and each bay
takes its own game, its own header and its own product mix, so an aisle
authored as one volume is a row of different bays. ``module_variants`` walks
the same table a different way, so four 1.2 m slots differ too.

THE BACK IS `slatwall` (Pixelcoat 0.44.0's `slatwall_retail`), a kind this
release adds to `skins.KNOWN_KINDS` -- before it, a slot asking for it built
the genome default and said nothing.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import pack_wall_forms as PF

PALETTE = {
    PF.METAL: ("M_PackWall_frame_metal_painted", [0.80, 0.79, 0.76],
               "metal_painted"),
    PF.BACK: ("M_PackWall_back_slatwall", [0.78, 0.76, 0.71], "slatwall"),
    PF.STOCK: ("M_PackWall_stock_paper", [0.55, 0.52, 0.47], "paper"),
}


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    stem = (plan.get("module") or {}).get("stem") or "pack_wall"
    budgets = plan.get("budgets") or {}
    got = PF.plan(w, d, h, params, params.get("variant") or 0, key=stem,
                  budget=int(budgets.get("tris_lod0") or PF.BUDGET),
                  bay_budget=int(budgets.get("tris_per_bay") or PF.BAY_BUDGET))

    mats = dict(PALETTE)
    mats[PF.BODY] = (f"M_PackWall_body_{plan['material']}",
                     list(plan["color"]), plan["material"])
    solid = [p for p in got["prims"] if not p.get("tile")]
    objs = prim_mesh.build(solid, collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    from ._card_atlas import build_art
    art, atlas = build_art(got["prims"], collection,
                           dict(plan, _tiles=got["tiles"]), streams, "PackWall")
    objs += art

    f = got["facts"]
    print(f"[pack_wall] {w:.2f} x {d:.2f} x {h:.2f} bays={f['bays']} "
          f"shelves={f['shelves_per_bay']} (cap {f['cap_rows'] - 1} from a "
          f"{f['bay_budget']} bay budget) pitch={f['pitch_m']:.3f} "
          f"items={f['items']} variant={f['variant']} tiles={f['tiles']} "
          f"games={','.join(f['games'])} "
          f"atlas={atlas['name'] if atlas else '-'} "
          f"{f['tris']} tris (pure), {f['per_bay_tris']} a bay")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {},
            "pack_wall": dict(f, atlas=atlas["name"] if atlas else None)}
