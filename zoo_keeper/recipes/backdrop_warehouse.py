"""backdrop_warehouse recipe: the yards backdrop recipe's far bands (Zoo 1.96.0, roadmap 228).

A long low box with three roof monitors, its front painted as siding with a roll-up door and a
strip of high windows, one in three lit cool white by the module's stem
(`core.backdrop_forms.paint_warehouse`); the roof and the monitors take the tar strip, the sides
and back the siding strip (`warehouse_uv_for`). One object on one `_Face` material, so a band of
warehouses is one MultiMesh and one draw a side, as the rowhome. Every part stands exactly the
slot's dims, the monitors INSET into the roof. Centre pivot, front toward -Y, bottom at -h/2, no
collision.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import backdrop_forms as BF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    stem = (plan.get("module") or {}).get("stem") or f"backdrop_warehouse_w{int(round(w * 100))}_h{int(round(h * 100))}"
    bm = geometry.new_bm()
    for _name, centre, size in BF.warehouse_parts(w, d, h):
        geometry.add_box(bm, centre, size)
    obj = geometry.bm_to_object(bm, "BackdropWarehouse_Face", collection, bevel=0.0,
                                texel=1.0, rng=streams.stream("wear"), wear=0.0)
    n = geometry.set_uv_by(obj, lambda co, nrm: BF.warehouse_uv_for(co, nrm, w, d, h))
    if n == 0:
        raise RuntimeError("backdrop_warehouse: the front's UVs did not land (no UV layer)")
    albedo, emission, _lit = BF.paint_warehouse(w, h - BF.MONITOR_H, plan["color"], stem)
    key = stem.replace("/", "_")
    img_a = materials.image_from_png(f"backdrop_warehouse_{key}_albedo", albedo.to_canvas().png())
    img_e = materials.image_from_png(f"backdrop_warehouse_{key}_emission", emission.to_canvas().png())
    mat = materials.make_pane_material(f"M_BackdropWarehouse_{key}_Face", img_a, img_e,
                                       strength=2.0, albedo_factor=1.0, roughness=0.8)
    materials.assign([obj], mat)
    return {"objects": [obj], "collision_boxes": [], "attachments": {}}
