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

    #: FLAT, and this is not a style choice. Every architectural module is
    #: built from boxes, and `shade_by_angle`'s 50-degree default smooths the
    #: bevel's ~45-degree chamfer into the face it cuts -- which on a box means
    #: into the ONLY vertices the face has. See `bm_to_object`: the shipped
    #: 2 m wall panel had every front-face normal 28.9 degrees off flat,
    #: splayed at its own corners, so it shaded as a dome and drew a diagonal
    #: across every instance. Zero keeps every edge hard: flat faces, and the
    #: chamfer reads as the 3 mm highlight it is.
    _WALL_SMOOTH = 0.0

    def part(bm, name, wr=wear, bv=None):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=(bevel if bv is None else bv),
            texel=1.2, rng=rng, wear=wr, ambient=ambient,
            smooth_angle=_WALL_SMOOTH))

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
        # ...and the VISUAL is the same plate cut to light-budget-sized tiles
        # (roadmap 54). Godot budgets positional lights PER MESH (engine
        # default 8), and each part here becomes its own object, so a 52 m
        # roof panel was one budget for a whole building -- the reason
        # level_factory has to ship a per-object light cap at all. Tiling is
        # visual-only: collision below is built from `slab`, exactly the
        # split the wall path already makes between structure and relief.
        visual = arch.tile_parts(
            slab, float(params.get("plate_tile", arch.PLATE_TILE)))
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
    # PLATE TILES ARE UNBEVELED (walked 2026-08-24, arena ceiling). Every
    # box edge gets a chamfer from the style's bevel, and where two tiles
    # abut, the two chamfers form a V-groove a few centimetres wide that
    # catches light differently than the flat face -- a thin bright/dark
    # line drawn along every internal tile seam, worst near a fixture. The
    # census exonerated the light budget for those tiles, so the groove is
    # the whole line. A flat plate's chamfer carries no information (its
    # rim meets walls and parapets), so plates drop it entirely; walls and
    # opening modules keep theirs -- their chamfers sit on real corners.
    plate_bevel = 0.0 if species in arch.PLATE_SPECIES else None
    for name, center, size in visual:
        bm = geometry.new_bm()
        geometry.add_box(bm, center, size)
        part(bm, f"{root}_{name}", bv=plate_bevel)
    if species not in arch.PLATE_SPECIES or species in arch.PLATE_COLLIDES:
        # PLATE-NESS AND COLLISION ARE TWO FACTS, and this line used to test
        # one for the other. A floor or ceiling skin emits none because Deli
        # Counter's trimesh slab under it is authoritative and already holed;
        # a ROOF is a plate by geometry and still has to be stood on, and its
        # slot says `collision: "trimesh"`. Tiling comes from `plate_parts`
        # above, so these boxes now go around the void instead of over it.
        #
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
