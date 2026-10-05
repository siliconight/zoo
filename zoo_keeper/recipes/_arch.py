"""Shared builder for architectural modules (wall / doorway / window / breach /
wallEnd): a center-pivot slab of exact dims with an optional passable void.

Leading underscore = not a dispatchable species (``recipes.get`` only imports a
module named after a genome). Each per-species recipe file is a one-liner that
calls :func:`build_slab` with its species name; the void shape and part layout
come from the pure ``core.arch`` module so they stay unit-testable.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import arch, partnames, window_panes


#: The flat colour a room face falls back to with no skin library: a warm
#: off-white wall, the drywall a 1990s store is painted.
INNER_COLOR = (0.82, 0.80, 0.74)

#: AN EMPTY'S DOOR (1.61.0): a painted panel door, set back from the street
#: face the depth a real frame recesses it, and as thick as a solid-core door.
#: Navy, one of the rowhouse comp's three door colours
#: (`docs/reference/EMPTIES_COMPS.md`); per-house colour is instance data,
#: not a material per colour, when it comes.
FACADE_DOOR_SETBACK = 0.08
FACADE_DOOR_THICK = 0.045
FACADE_DOOR_COLOR = (0.16, 0.20, 0.28)


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

    #: Where this module meets its neighbours. Edges lying in these planes
    #: stay sharp, so two modules' chamfers no longer cut a V-groove into
    #: every joint of a run (`arch.butt_planes`).
    butts = arch.butt_planes(species, w)

    def part(bm, name, wr=wear, bv=None):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=(bevel if bv is None else bv),
            # TEXEL 1.0, NOT 1.2 -- roadmap 108, and it is a density
            # target rather than a preference. On-screen density is
            # `size * texel / meters_per_tile`, so a 1.2 here multiplied
            # every architectural surface in the library by 1.2 against
            # the 128 px/m target `pixelcoat/docs/CONTRAST_DIRECTION.md`
            # 6.3 sets: 256 * 1.2 / 2.0 = 153.6. At 1.0 it lands on
            # 128.0. That document's whole argument is that the library
            # is authored far finer than the aesthetic wants, and this
            # multiplier was quietly undoing a fifth of every step taken
            # toward it in `meters_per_tile`.
            texel=1.0, rng=rng, wear=wr, ambient=ambient,
            smooth_angle=_WALL_SMOOTH, butt_planes=butts))

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
    # A STOREFRONT (1.18.0): a wall or door slot Deli Counter tagged
    # `glazing: "storefront"` is drawn as a kick, a header, mullions and a
    # see-through pane (`arch.storefront_parts`) instead of the slab. The
    # COLLIDER still comes from `slab` below: the glass stops a body. A door
    # draws its closed leaves in every state but "open", which `kit.plan_kit`
    # builds as its own module for storefront doors.
    storefront_glass = []
    if plan.get("storefront") and species in ("wall", "doorway"):
        state = (plan.get("module") or {}).get("state")
        visual, storefront_glass = arch.storefront_parts(
            w, d, h, void, leaves=(species == "doorway" and state != "open"))
    # PLATE TILES ARE UNBEVELED (walked 2026-08-24, arena ceiling). Every
    # box edge gets a chamfer from the style's bevel, and where two tiles
    # abut, the two chamfers form a V-groove a few centimetres wide that
    # catches light differently than the flat face -- a thin bright/dark
    # line drawn along every internal tile seam, worst near a fixture. The
    # census exonerated the light budget for those tiles, so the groove is
    # the whole line. A flat plate's chamfer carries no information (its
    # rim meets walls and parapets), so plates drop it entirely; walls and
    # opening modules keep theirs -- their chamfers sit on real corners.
    #
    # EXCEPT AT THEIR ENDS, which was the same groove and was missed. A wall's
    # end edges sit on the plane its neighbour shares, not on a corner, and
    # walk 9052 showed the line at every 2.00 m of an interior partition. They
    # stay sharp now (`butts` above); every other chamfer is unchanged.
    plate_bevel = 0.0 if species in arch.PLATE_SPECIES else None
    # a storefront-lit room's plate keeps its tiles apart in the merge (1.24.0)
    mark = (partnames.LIGHT_BUDGET_MARK
            if species in arch.PLATE_SPECIES and plan.get("light_budget_tiles") else "")
    for name, center, size in visual:
        bm = geometry.new_bm()
        geometry.add_box(bm, center, size)
        part(bm, f"{root}_{name}{mark}", bv=plate_bevel)
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
    # THE ROOM FACE (1.38.0). Deli Counter places a wall module with its
    # local +Y outdoors on every facing (measured through its placement
    # basis), so the ROOM is at -Y: every structure face pointing -Y on the
    # -Y half -- the wall's inner face and its recessed fields' -- takes the
    # interior finish. Jambs, sill and head keep the wall's own: they face
    # across the opening, not into the room. Before the storefront panes and
    # the window glass below, which are not structure.
    inner = plan.get("material_in")
    if inner and species in ("wall", "window", "doorway", "breach", "wallEnd") \
            and not plan.get("storefront"):
        room = materials.make_material(f"M_{root}_{inner}", INNER_COLOR, inner)
        done = set()
        for o in objs:
            if id(o.data) in done:        # a mesh shared by two parts takes it once
                continue
            done.add(id(o.data))
            o.data.materials.append(room)
            for poly in o.data.polygons:
                if poly.normal.y < -0.9 and poly.center.y < 0.0:
                    poly.material_index = len(o.data.materials) - 1

    # the storefront's panes: the theme's glass surface at a storefront's
    # own opacity (`arch.SF_GLASS_OPACITY`, clear float glass), one material
    # of its own. It was the window's material until 1.20.0; a storefront
    # module has one glass material either way, so this costs no submission.
    for name, center, size in storefront_glass:
        bm = geometry.new_bm()
        geometry.add_box(bm, center, size)
        pane = geometry.bm_to_object(
            bm, f"{root}_{name}", collection, bevel=0.0, texel=1.0,
            rng=rng, wear=wear * 0.25)
        materials.assign([pane], materials.make_see_through_material(
            "M_Storefront_glass", plan.get("glass_color", [0.55, 0.66, 0.72]),
            arch.SF_GLASS_OPACITY, "glass", own="storefront"))
        objs.append(pane)

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
        glazing_kind = plan.get("glazing_kind", "glass")
        state = plan.get("pane")
        if glazing_kind == "glass_facade" and state in window_panes.STATES:
            # A PAINTED PANE (1.64.0): the street face (+Y, outdoors) shows
            # its state's cell of the shared atlas; every other face takes a
            # point of the frame paint. Own UVs, so `finish=False` -- the
            # cube projection would overwrite them -- and a white COLOR_0,
            # which Level Factory's import multiplies by.
            u0, v0, u1, v1 = window_panes.uv_rect(state)
            frame = window_panes.uv_rect("lit")[0] * 0.25
            uv = bm.loops.layers.uv.new("UVMap")
            hx, hz = pane_w * 0.49, pane_h * 0.49
            bm.normal_update()
            for face in bm.faces:
                for loop in face.loops:
                    if face.normal.y > 0.9:
                        co = loop.vert.co
                        # seen from +Y looking at -Y, +X is the viewer's
                        # LEFT: u runs from the +X edge, or the cell mirrors
                        loop[uv].uv = (u0 + (u1 - u0) * ((cx + hx) - co.x) / (2 * hx),
                                       v0 + (v1 - v0) * (co.z - (cz - hz)) / (2 * hz))
                    else:
                        loop[uv].uv = (frame, frame)
            geometry.wear_colors(bm, streams.stream("pane"), 0.0)
            pane = geometry.bm_to_object(bm, f"{root}_Glass", collection,
                                         finish=False, bevel=0.0)
            albedo, emission = window_panes.atlas()
            pane.data.materials.append(materials.make_pane_material(
                "M_Window_pane_Face",
                materials.image_from_png("window_pane_albedo", albedo.png()),
                materials.image_from_png("window_pane_emission", emission.png()),
                window_panes.EMISSION, window_panes.ALBEDO))
            objs.append(pane)
        else:
            pane = geometry.bm_to_object(
                bm, f"{root}_Glass", collection, bevel=0.0, texel=1.0,
                rng=rng, wear=wear * 0.25)
            # Enterable windows glaze see-through "glass"; facade-shell windows
            # (hollow building) glaze opaque "glass_facade" via plan.glazing_kind.
            glass = materials.make_material(
                f"M_Window_{glazing_kind}",
                plan.get("glass_color", [0.55, 0.66, 0.72]), glazing_kind)
            materials.assign([pane], glass)
            objs.append(pane)

    # AN EMPTY'S DOOR IS SHUT (1.61.0). A doorway tagged `glazing: "facade"`
    # belongs to a shell with nothing behind it (Deli Counter >= 0.178.0), the
    # same tag that glazes its windows opaque. Its collision has been solid
    # since Deli Counter 0.174.0; drawn as an open frame it was a doorway the
    # player could see into and not walk through. Filled with a leaf, set back
    # from the +Y street face (+Y is outdoors, see THE ROOM FACE above), no
    # collision of its own -- the wall's box already holds. After the room
    # face, like the panes: a door is not structure.
    if species == "doorway" and void and plan.get("glazing_kind") == "glass_facade":
        lw = void["x1"] - void["x0"]
        lh = void["z1"] - void["z0"]
        bm = geometry.new_bm()
        geometry.add_box(bm, ((void["x0"] + void["x1"]) / 2.0,
                              d / 2.0 - FACADE_DOOR_SETBACK - FACADE_DOOR_THICK / 2.0,
                              (void["z0"] + void["z1"]) / 2.0),
                         (lw - 0.004, FACADE_DOOR_THICK, lh - 0.002))
        leaf = geometry.bm_to_object(
            bm, f"{root}_Leaf", collection, bevel=bevel, texel=1.0,
            rng=rng, wear=wear, smooth_angle=_WALL_SMOOTH, butt_planes=butts)
        materials.assign([leaf], materials.make_material(
            "M_Door_wood_panel", plan.get("door_color", FACADE_DOOR_COLOR), "wood_panel"))
        objs.append(leaf)

    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
