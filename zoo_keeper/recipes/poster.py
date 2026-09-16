"""poster recipe: the painted set poster on the wall above the shelving.

Zoo 0.98.0. Planned in pure Python by `core.flat_forms.plan_poster` and
built by `bpylayer.prim_mesh`, except the ART QUAD, which goes through
`recipes/_card_atlas.py` into one atlas carrying one painted material --
the same road `pack_wall` and `display_case` take.

THREE RECTANGLES, NOT ONE QUAD. The walker's fourth poster reference is a
framed magazine cover and the mat is what makes it read as framed rather
than taped up, so the `framed` form builds a frame ring, a mat ring and a
plate: 78 triangles. `bare` is the plate alone at 14, and `tilted` is a
bare plate turned in the wall plane. All three carry ONE art tile.

THE MATERIAL IS PAINT, NOT LIGHT (`_card_atlas`'s rule). A poster is lit by
the room; a backlit one would glow in a shop with the power cut.
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
    stem = (plan.get("module") or {}).get("stem") or "poster"
    got = FF.plan_poster(w, d, h, params, params.get("variant") or 0, key=stem)
    f = got["facts"]

    mats = {
        # the frame wears the slot's own material, so a delco shop's frames
        # are its metal and a modern one's are its aluminium
        FF.FRAME: (f"M_Poster_frame_{plan['material']}",
                   list(plan["color"]), plan["material"]),
        FF.CLOTH: ("M_Poster_mat_cloth", list(f["mat_rgb"]), "cloth"),
        FF.BOARD: ("M_Poster_plate_paper", list(f["plate_rgb"]), "paper"),
    }
    solid = [p for p in got["prims"] if not p.get("tile")]
    objs = prim_mesh.build(solid, collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    from ._card_atlas import build_art
    art, atlas = build_art(got["prims"], collection,
                           dict(plan, _tiles=got["tiles"]), streams, "Poster",
                           roughness=FA.POSTER_ROUGHNESS)
    objs += art

    png, raw = FA.atlas_bytes(atlas) if atlas else (0, 0)
    print(f"[poster] {w:.2f} x {d:.2f} x {h:.2f} form={f['form']} "
          f"tilt={f['tilt_deg']:.1f} game={f['game']} maker={f['maker']} "
          f"atlas={atlas['name'] if atlas else '-'} "
          f"({png / 1024.0:.1f} KiB png, {raw / 1048576.0:.3f} MiB raw) "
          f"rung={f['rung_m'] * 1000.0:.1f} mm {f['tris']} tris (pure)")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {},
            "poster": dict(f, atlas=atlas["name"] if atlas else None,
                           atlas_png_bytes=png, atlas_raw_bytes=raw)}
