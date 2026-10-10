"""backdrop_rowhome recipe: a rowhome for the bands beyond the plate's edge (Zoo 1.95.0,
roadmap 228 step C).

ONE PAINTED BOX WITH A ROOFLINE, ONE MATERIAL, ONE SURFACE. The edge menu's mockup drew a house
as a box and a quad per lit window and found the houses "read as buildings by their lit windows,
and only by those". This one has the cornice, chimney and stoop the mockup lacked, as geometry,
and its windows and door in the paint: `core.backdrop_forms.paint` makes the albedo and the
emission (lit panes only) for the facade, and `uv_for` sends the body's front to the facade,
the roof, cornice and stoop to a dark strip and the rest to brick. All of it is one object on one
`_Face` material (Lux's emissive binder darkens the lit windows with the power), so a band of
houses is one MultiMesh and one draw a side. The body is narrower, shallower and lower than the
slot by the cornice, the stoop and the chimney, so the whole stands exactly (w, d, h): Zoo's
exact fit, which the first build failed on all three axes.

Which windows are lit is `backdrop_forms.lit_pattern`, deterministic for the module's stem: Lot
asks for a few widths and heights, and a band drawn from them shows a few patterns. Centre pivot,
front toward -Y, bottom at -h/2. No collision: it is backdrop, never inside the playable extent.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import backdrop_forms as BF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    stem = (plan.get("module") or {}).get("stem") or f"backdrop_rowhome_w{int(round(w * 100))}_h{int(round(h * 100))}"
    bm = geometry.new_bm()
    for _name, centre, size in BF.rowhome_parts(w, d, h):
        geometry.add_box(bm, centre, size)
    # painted faces carry a white Wear: the paint is the look, not the grime
    obj = geometry.bm_to_object(bm, "BackdropRowhome_Face", collection, bevel=0.0,
                                texel=1.0, rng=streams.stream("wear"), wear=0.0)
    n = geometry.set_uv_by(obj, lambda co, nrm: BF.uv_for(co, nrm, w, d, h))
    if n == 0:
        raise RuntimeError("backdrop_rowhome: the facade's UVs did not land (no UV layer)")
    bw, _bd, bh, _y_front = BF.body_dims(w, d, h)
    albedo, emission, _lit = BF.paint(bw, bh, plan["color"], stem)
    key = stem.replace("/", "_")
    img_a = materials.image_from_png(f"backdrop_rowhome_{key}_albedo", albedo.to_canvas().png())
    img_e = materials.image_from_png(f"backdrop_rowhome_{key}_emission", emission.to_canvas().png())
    mat = materials.make_pane_material(f"M_BackdropRowhome_{key}_Face", img_a, img_e,
                                       strength=2.0, albedo_factor=1.0, roughness=0.9)
    materials.assign([obj], mat)
    return {"objects": [obj], "collision_boxes": [], "attachments": {}}
