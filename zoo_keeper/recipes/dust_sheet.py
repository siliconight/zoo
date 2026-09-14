"""dust_sheet recipe: a cloth draped over a hidden piece of furniture.

Planned in pure Python by `core.drape_forms` (the profiles, the cloth and
the rules are in its docstring) and built vertex for vertex by
`bpylayer.prim_mesh`. The cloth takes the genome's colour and kind,
lightened or dulled a little per seed so a room of sheets is not one
white; a table profile's legs are dark wood. No bevel: the cloth is its
own faceting.

Collision is the slot's box: whatever is under the sheet is solid, and
a body does not walk into a draped sofa's folds.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import drape_forms

#: per-seed tone of the cloth: a newer sheet, a greyed one, a yellowed one
TONES = ((1.0, 1.0, 1.0), (0.86, 0.87, 0.88), (0.97, 0.92, 0.80))


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    rng = streams.stream("form")
    got = drape_forms.plan(w, d, h, rng,
                           (plan.get("params") or {}).get("profile", "auto"))
    tone_i = rng.randrange(len(TONES))
    tone = TONES[tone_i]
    kind = plan["material"]
    cloth = [min(1.0, c * t) for c, t in zip(plan["color"], tone)]
    mats = {key: (f"M_DustSheet_{key}_{k}", list(c), k)
            for key, (c, k) in drape_forms.MATERIALS.items()}
    mats["cloth"] = (f"M_DustSheet_cloth_{kind}_{tone_i}", cloth, kind)
    objs = prim_mesh.build(got["prims"], collection, dict(plan, bevel=0.0),
                           streams.stream("wear"), mats, texel=1.0)
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {}}
