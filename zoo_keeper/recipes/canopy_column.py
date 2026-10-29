"""canopy_column recipe: a filling station canopy's column -- a painted steel shaft on a concrete guard a bumper meets
first, the guard in safety yellow.

Minted by `tools/new_species.py`; shaped here (the factory's roadmap 324), beside `fuel_canopy`: Deli Counter's specs
author six `canopy_col` volumes a canopy, and until this species each shipped as its greybox box.

ONE MATERIAL, colour in the `Wear` vertex colour (`geometry.tint_wear`). THE ENVELOPE IS THE SLOT'S: the guard is the
slot's full plan to `GUARD_H` (or a fifth of the height, the smaller); the shaft rises from inside it, buried by
`BURY`, to the module's top -- the canopy's soffit, which owns that plane overhead.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core.canopy_forms import GUARD_RGB, SHAFT_RGB
from ..core.canopy_forms import column_boxes as boxes


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    rng = streams.stream("wear")
    rgb = {"Guard": GUARD_RGB, "Shaft": SHAFT_RGB}
    objs = []
    for name, lo, hi in boxes(w, d, h):
        bm = geometry.new_bm()
        geometry.add_box(bm, tuple((lo[i] + hi[i]) / 2.0 for i in range(3)), tuple(hi[i] - lo[i] for i in range(3)))
        o = geometry.bm_to_object(bm, f"CanopyColumn_{name}", collection, bevel=plan["bevel"], texel=1.2, rng=rng,
                                  wear=plan["wear"])
        geometry.tint_wear(o, rgb[name])
        objs.append(o)
    surface = materials.make_material(f"M_CanopyColumn_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, surface)
    return {"objects": objs, "collision_boxes": [((-w / 2, -d / 2, -h / 2), (w / 2, d / 2, h / 2))],
            "attachments": {"ATT_top": (0.0, 0.0, h / 2)}}
