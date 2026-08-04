"""Shared builder for architectural modules (wall / doorway / window / breach /
wallEnd): a center-pivot slab of exact dims with an optional passable void.

Leading underscore = not a dispatchable species (``recipes.get`` only imports a
module named after a genome). Each per-species recipe file is a one-liner that
calls :func:`build_slab` with its species name; the void shape and part layout
come from the pure ``core.arch`` module so they stay unit-testable.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import arch


def build_slab(plan, streams, collection, species):
    dims = plan["dimensions"]
    w, d, h = dims["width"], dims["depth"], dims["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    ambient = plan.get("ambient", 0.0)
    params = plan.get("params", {})
    rng = streams.stream("wear")
    root = arch.root_name(species)
    objs, cboxes = [], []

    def part(bm, name, wr=wear):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.2, rng=rng, wear=wr,
            ambient=ambient))

    if species in arch.PLATE_SPECIES:
        # A floor or ceiling SKIN. Two things differ from a standing slab and
        # both were wrong the first time this shipped.
        #
        # Its holes are in x/y, not x/z -- a stairwell, not a doorway -- so it
        # tiles with plate_parts. A plain rectangle lies across the stairwell:
        # ceiling visible above the stairs, and the stairs unusable.
        #
        # And it emits NO collision. Deli Counter's slab is trimesh precisely
        # so its cut holes stay open, and it stays authoritative; a skin that
        # added its own boxes would cap every hole in collision even after the
        # geometry stopped capping them visually. The slot declares
        # `collision: "none"` and this is the half that honours it -- declaring
        # it is not the same as respecting it, which is exactly how the stairs
        # got blocked.
        void = None
        slab = arch.plate_parts(w, d, h, params.get("voids"))
        visual = slab
    else:
        void = arch.void_for(species, w, h, params)
        slab = arch.slab_parts(w, d, h, void)
        # A SOLID WALL IS DRAWN WITH RELIEF AND COLLIDES AS A BOX. The two
        # tilings are deliberately different objects: `slab` is the structure
        # (and the collider), `visual` is the same volume with its fields
        # recessed between a plinth, piers and a cap.
        #
        # This is where facade articulation moved TO. It used to be additive
        # -- Patina emitted panel and pilaster orders, Zoo built each as a box
        # standing proud of the face -- and a module's collider ends exactly at
        # its face, so every one of those boxes was non-collision geometry in
        # space a body walks through. Aiming them inward put 546 panels in
        # rooms; aiming them outward put the same 546 in the alleys Lot makes
        # into routes. Carving inward has no such direction to get wrong.
        #
        # `wall` only. A `wallEnd` is one unit box that Deli Counter SCALES per
        # slot, so a 14 cm pier would come out anywhere between 4 cm and 40 cm
        # wide depending on the remainder it fills; an opening module already
        # articulates itself with jambs, a sill and a header. Neither wants a
        # second rhythm laid over it.
        visual = (arch.relief_parts(w, d, h, params.get("relief"))
                  if species == "wall" and not void else slab)
    for name, center, size in visual:
        bm = geometry.new_bm()
        geometry.add_box(bm, center, size)
        part(bm, f"{root}_{name}")
    if species not in arch.PLATE_SPECIES:
        # From `slab`, NOT `visual`. The collider is the solid wall it has
        # always been -- recessing the fields must not carve notches a player
        # can stand in, and must not change one collision box on any build
        # before this one.
        cboxes.extend(arch.collision_boxes(slab))

    structure = materials.make_material(
        f"M_{root}_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, structure)

    # a window gets a thin glass pane in its opening — decorative, no collision
    # (heist sightlines / breakable glass are gameplay's call, not the box).
    if species == "window" and void:
        pane_w = void["x1"] - void["x0"]
        pane_h = void["z1"] - void["z0"]
        cx = (void["x0"] + void["x1"]) / 2.0
        cz = (void["z0"] + void["z1"]) / 2.0
        bm = geometry.new_bm()
        geometry.add_box(bm, (cx, 0.0, cz),
                         (pane_w * 0.98, d * 0.15, pane_h * 0.98))
        pane = geometry.bm_to_object(
            bm, f"{root}_Glass", collection, bevel=0.0, texel=1.2,
            rng=rng, wear=wear * 0.25)
        # Enterable windows glaze see-through "glass"; facade-shell windows
        # (hollow building) glaze opaque "glass_facade" via plan.glazing_kind.
        glazing_kind = plan.get("glazing_kind", "glass")
        glass = materials.make_material(
            f"M_Window_{glazing_kind}",
            plan.get("glass_color", [0.55, 0.66, 0.72]), glazing_kind)
        materials.assign([pane], glass)
        objs.append(pane)

    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
