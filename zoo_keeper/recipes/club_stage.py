"""club_stage recipe: a strip club's stage -- round, a runway, or the middle
of an oval bar -- with a pole, a padded rail on brass posts and a warm rope
light along the lip.

Planned in pure Python by `core.club_forms.plan_stage` (the forms, heights
and rules are in its docstring) and built vertex for vertex by
`bpylayer.prim_mesh`. The fascia and steps take the genome's colour and kind
(Deli Counter's stage volume says `wood`); lip, carpet, pad, brass and
chrome are sub-part finishes from `club_forms.STAGE_MATERIALS`; the rope
light is emissive, ``M_ClubStage_rope_Face``, so Lux's power cut takes it.

``form`` is the slot's (``kit.DRESSING_FIELDS``) when Deli Counter writes
one, else ``auto``: round up to 1.4 : 1, a runway past it. ``stock`` ``bar``
sets glasses, bottles and ashtrays on a bar_stage's straight runs.

Collision is the platform (bands inscribed in its outline), the steps and
the rail -- not the pole, which stands inside the platform's collider.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import club_forms as CF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    form = (plan.get("params") or {}).get("form", "auto")
    got = CF.plan_stage(w, d, h, streams.stream("form"), form)
    kind = plan["material"]
    mats = {key: (f"M_ClubStage_{key}_{k}", list(c), k)
            for key, (c, k) in CF.STAGE_MATERIALS.items()}
    mats["fascia"] = (f"M_ClubStage_fascia_{kind}", list(plan["color"]), kind)
    for key, (c, strength) in CF.STAGE_EMISSIVE.items():
        mats[key] = (f"M_ClubStage_{key}_Face", list(c), "emissive", strength)
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    stock = prim_mesh.build_stock(
        plan, streams, collection,
        [(x0, x1, y0, y1, z0, facing, 0.6, ())
         for x0, x1, y0, y1, z0, facing in got["stock_regions"]],
        CF.STAGE_MATERIALS["bartop"][0])
    return {"objects": objs + stock, "dressing_objects": stock,
            "collision_boxes": got["collision"],
            "attachments": {"ATT_deck": (0.0, 0.0, got["platform"])}}
