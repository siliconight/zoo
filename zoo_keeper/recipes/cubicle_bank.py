"""cubicle_bank recipe: a 1990s panel-system office bank -- fabric screens on
a painted frame, work surfaces cantilevered off them, and an AISLE.

WHAT IT IS AND WHAT IT IS NOT. Ten volumes in the library name themselves
`cubicle*`; every one was routed to `desk`, whose ranges reach 12 m wide and
6 m deep, so an 8 x 6 m cubicle farm FIT and was built as desk geometry at
that size -- `desk.py`'s rows butted edge to edge, a raft of tops with
nothing between them. The walker, cold run 9060: "these desks are too close
to each other?". A bank is screens first: the desks live INSIDE them, and
the space between two rows of them is circulation, not furniture.

THE LAYOUT IS `core.cubicle_forms`, pure and testable without Blender, the
way `club_forms` and `cigarette_forms` are. This file turns its boxes into
objects, paints them and hands back the collision.

MATERIALS. The screens are the mass, and they are CLOTH by
`dna.UPHOLSTERED`: Deli Counter's ten volumes are authored `drywall`, which
on this species names the FRAME and not the fabric, exactly as `wood` on a
sofa names its legs. Without that the bank would wear the building's own
partition surface and read as a lump of wall. The frame, caps, feet, rails,
handles and bins are `metal_painted` and the work surfaces, pedestals and
drawer fronts `laminate`: a species' own palette, because those are what
make it read as a cubicle rather than as whatever the slot happened to say.

COLLISION: per part, never the slot's box. Spine and cross screens, work
surfaces, pedestals and bins declare their own; drawer fronts, handles,
rails, caps and levelling feet declare none, because each sits inside or
under something that already does. The aisle and the knee space under every
surface declare nothing at all, which is the point of the species.
`bpylayer.build` bakes the list into the module's `-colonly` mesh.

VARIANTS. `module_variants` 4: which end of a bay the pedestal takes, how
many drawers it has, and which bays carry a bin where one fits -- so four
banks in one office are not one bank four times. `stock` (default `office`)
puts `_surface_stock`'s monitors, paperwork and phones on every work
surface, facing that band's sitter.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import cubicle_forms as CF


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel = plan["bevel"]
    wear = plan["wear"]
    rng = streams.stream("wear")
    params = plan.get("params") or {}
    got = CF.plan(w, d, h, params, params.get("variant") or 0)

    soft = (plan.get("upholstery") or {}).get("material") or plan["material"]
    mats = {
        CF.FABRIC: materials.make_material(
            f"M_CubicleBank_{soft}", list(plan["color"]), soft),
        CF.FRAME: materials.make_material(
            "M_CubicleBank_frame_metal_painted", [0.30, 0.31, 0.30],
            "metal_painted"),
        CF.TOP: materials.make_material(
            "M_CubicleBank_surface_laminate", [0.74, 0.71, 0.63], "laminate"),
    }
    groups = {k: [] for k in mats}
    objs, cboxes = [], []

    for name, key, centre, size, solid in got["boxes"]:
        bm = geometry.new_bm()
        geometry.add_box(bm, centre, size)
        # `smooth_angle=1.0`: every edge hard. A spine screen is the slot's
        # full width -- 8 m on every one of the library's banks -- and
        # `bm_to_object`'s own docstring records what the default crease does
        # to a panel that size: the chamfer is smoothed INTO the face, a box
        # face has no interior vertices to hold the middle flat, and the
        # panel shades as a dome with a diagonal wedge across it. That is the
        # defect `wall_delco_01_w200` was measured with. A cubicle screen is
        # a wall panel by every dimension that matters here.
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                    texel=1.0, rng=rng, wear=wear,
                                    ambient=plan.get("ambient", 0.0),
                                    smooth_angle=1.0)
        objs.append(obj)
        groups[key].append(obj)
        if solid:
            cboxes.append(((centre[0] - size[0] / 2.0,
                            centre[1] - size[1] / 2.0,
                            centre[2] - size[2] / 2.0),
                           (centre[0] + size[0] / 2.0,
                            centre[1] + size[1] / 2.0,
                            centre[2] + size[2] / 2.0)))
    for key, mat in mats.items():
        materials.assign(groups[key], mat)

    stock = prim_mesh.build_stock(plan, streams, collection, got["regions"],
                                  [0.74, 0.71, 0.63])
    objs += stock

    f = got["facts"]
    print(f"[cubicle_bank] {w:.2f} x {d:.2f} x {h:.2f} -- {f['bands']} band(s) "
          f"x {f['bays']} bay(s), aisle {f['aisle_m']:.2f} m, band "
          f"{f['band_depth_m']:.2f} m, bins {f['bins']}, variant "
          f"{f['variant']}, screens {soft}, stock {params.get('stock')}, "
          f"{len(cboxes)} collision boxes of {len(got['boxes'])} parts")
    return {"objects": objs, "dressing_objects": stock,
            "collision_boxes": cboxes, "attachments": {},
            "cubicle_bank": dict(f)}
