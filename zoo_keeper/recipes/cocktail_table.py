"""cocktail_table recipe: a small round club table on a cast pedestal,
under a floor-length cloth (form ``cloth``, the default) or bare (``bare``).

Planned in pure Python by `core.club_forms.plan_table`, built by
`bpylayer.prim_mesh`. A bare top takes the genome's colour and kind; the
cloth is `club_forms.CLOTHS[variant]` -- dark red or white, on the `cloth`
kind whose delco packs are a tintable linen (Pixelcoat 0.43.0; 0.88.0's
`canvas` was a fixed beige weave, so every cloth read as gold burlap) --
and the base is black painted iron. ``stock`` ``bar`` sets `_surface_stock`'s
bar items -- bottles, pints on coasters, an ashtray -- on the two halves of
the square inscribed in the round top, so nothing can hang over its edge,
from the recipe's own "stock" stream.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import club_forms as CF


def _hex(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    form = (plan.get("params") or {}).get("form", "auto")
    variant = int((plan.get("params") or {}).get("variant", 0) or 0)
    got = CF.plan_table(w, d, h, streams.stream("form"), form, variant=variant)
    kind = plan["material"]
    cloth, cloth_kind = got["cloth_rgb"], got["cloth_kind"]
    mats = {key: (f"M_CocktailTable_{key}_{k}", list(c), k)
            for key, (c, k) in CF.TABLE_MATERIALS.items()}
    mats["top"] = (f"M_CocktailTable_top_{kind}", list(plan["color"]), kind)
    mats["cloth"] = (f"M_CocktailTable_cloth_{_hex(cloth)}", list(cloth), cloth_kind)
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    host = cloth if got["form"] == "cloth" else plan["color"]
    stock = prim_mesh.build_stock(
        plan, streams, collection,
        [(x0, x1, y0, y1, z0, None, 0.6, ()) for x0, x1, y0, y1, z0 in got["stock_regions"]],
        host)
    return {"objects": objs + stock, "dressing_objects": stock,
            "collision_boxes": got["collision"],
            "attachments": {"ATT_surface_center": (0.0, 0.0, h)}}
