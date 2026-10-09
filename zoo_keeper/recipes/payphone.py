"""payphone recipe: a 1990s coin payphone in one of three enclosures, one
atlas, one draw.

Zoo 1.88.0, roadmap 210. Planned in pure Python by `core.payphone_forms.plan`:
the booth on a post (the default), the pedestal shroud or the wall unit; the
stainless instrument with its keys, coin slot, coin-return recess, vault door,
card and cradle; the handset on its armoured cord. `recipes/_card_atlas.
build_art` builds every prim into one object on one painted image. See that
module for the reference, the forms and the company.

1.87.0's payphone was a half-booth of boxes in three materials and three
draws: no keypad, no coin slot, no cord, nothing printed. The walker,
2026-10-09: it "doesn't have a phone or appropriate decals".

Collision is the back panel and the instrument as one column, each side
panel, and the post: a body stands in the booth's mouth, never inside its
back. `ATT_hood` stays under the roof, where a light would go if a level lit
one. Origin on the ground under the middle (`build_module` re-centres it);
the caller at -Y.
"""
from __future__ import annotations

from ..core import payphone_forms as PF

#: Painted steel and brushed stainless, outdoors: neither card nor gloss.
ROUGHNESS = 0.55


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    got = PF.plan(w, d, h, params.get("form"), plan["color"])
    from ._card_atlas import build_art
    tiles = {k: spec for k, (_a, spec) in got["tiles"].items()}
    objs, _atlas = build_art(got["prims"], collection, dict(plan, _tiles=tiles), streams,
                             "Payphone", roughness=ROUGHNESS, smooth=True)
    f = got["facts"]
    print(f"[payphone] {w:.2f} x {d:.2f} x {h:.2f} form={f['form']} {f['tris']} tris, 1 material")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_hood": (0.0, 0.0, got["layout"]["top"] - PF.T_ROOF)},
            "payphone": {"form": f["form"], "company": f["company"]}}
