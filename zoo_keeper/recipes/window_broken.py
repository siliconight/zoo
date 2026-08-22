"""window_broken module recipe: the broken STATE of a window slot.

Same center-pivot slab as `window` -- jambs, sill, header, an IDENTICAL
void at identical dims, so the frame the players learned stays where it
was -- but the pane is gone and remnant glass strips are left in the
frame. Built as per-state art under INTERACTIVES.md: a window slot whose
interactive block maps state_geometry {"intact": "window", "broken":
"window_broken"} gets `window_<theme>_<style>_w<cm>_broken.glb` from this
recipe at the slot's exact dims, and the resolver falls back to the
intact window until it exists.

The void must MATCH the intact window's, so this asks `arch.void_for` the
window's question (species "window", same params, same authored opening)
rather than its own -- a broken window whose hole moved is a different
window, not a state of the same one.

Collision: the slab boxes only. The opening is walk/shoot-through, per
the same law that keeps doorways passable, and the remnant strips carry
none -- a sliver of glass must never stop a laser the eye says goes
through. The remnants are CLEAN strips: a jagged shatter-edge look is a
later art pass, exactly as breach ships the clean cutout.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import arch


def build(plan, streams, collection):
    dims = plan["dimensions"]
    w, d, h = dims["width"], dims["depth"], dims["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    ambient = plan.get("ambient", 0.0)
    params = plan.get("params", {})
    rng = streams.stream("wear")
    root = arch.root_name("window_broken")

    # The window's void, not a new one (see docstring).
    void = arch.void_for("window", w, h, params)
    slab = arch.slab_parts(w, d, h, void)

    objs = []
    for name, center, size in slab:
        bm = geometry.new_bm()
        geometry.add_box(bm, center, size)
        objs.append(geometry.bm_to_object(
            bm, f"{root}_{name}", collection, bevel=bevel, texel=1.2,
            rng=rng, wear=wear, ambient=ambient))

    structure = materials.make_material(
        f"M_{root}_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, structure)

    remnants = []
    if void:
        pane_t = d * 0.15
        x0, x1, z0, z1 = void["x0"], void["x1"], void["z0"], void["z1"]
        opening_w = x1 - x0
        opening_h = z1 - z0
        cx = (x0 + x1) / 2.0
        rise = opening_h * float(params.get("remnant_rise", 0.14))
        hang = opening_h * float(params.get("remnant_hang", 0.09))
        bm = geometry.new_bm()
        # A strip rising from the sill and a shorter one hanging from the
        # header, spanning just inside the jambs like the pane did.
        geometry.add_box(bm, (cx, 0.0, z0 + rise / 2.0),
                         (opening_w * 0.98, pane_t, rise))
        geometry.add_box(bm, (cx, 0.0, z1 - hang / 2.0),
                         (opening_w * 0.98, pane_t, hang))
        remnant = geometry.bm_to_object(
            bm, f"{root}_Remnant", collection, bevel=0.0, texel=1.2,
            rng=rng, wear=wear * 0.25)
        # Same glazing plumbing as the intact pane: see-through glass for
        # enterable windows, opaque glass_facade for hollow-shell facades.
        glazing_kind = plan.get("glazing_kind", "glass")
        glass = materials.make_material(
            f"M_WindowBroken_{glazing_kind}",
            plan.get("glass_color", [0.55, 0.66, 0.72]), glazing_kind)
        materials.assign([remnant], glass)
        remnants.append(remnant)

    return {"objects": objs + remnants,
            "collision_boxes": arch.collision_boxes(slab),
            "attachments": {}}
