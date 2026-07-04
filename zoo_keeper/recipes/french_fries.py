"""French fries recipe (scatter showcase): a paper boat holding a pile of
jittered fry sticks. 'Model one fry, duplicate, randomize, join' — exactly
core.scatter. Origin at floor center."""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import scatter


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    place_rng = streams.stream("dims")
    n = plan["params"].get("fries", 20)
    objs, cboxes = [], []

    def part(bm, name, texel=5.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    # paper boat: shallow open tapered tray (wider at the rim)
    boat_h = h * 0.5
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0, 0, boat_h / 2), min(w, d) * 0.42, boat_h,
                          segments=4, radius_top=min(w, d) * 0.5)
    part(bm, "Fries_Boat", texel=3.0)
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, h)))

    # fry pile: thin long sticks, scattered and jittered above the boat
    fry = (0.008, 0.06, 0.008)
    bm = geometry.new_bm()
    for t in scatter.scatter_transforms(
            n, place_rng, area=(w * 0.28, d * 0.28),
            base_z=boat_h * 0.9, layer_rise=0.006,
            scale_range=(0.8, 1.2)):
        fv = geometry.add_box(bm, (0, 0, 0), fry)
        geometry.jitter_verts(fv, place_rng, 0.004)
        geometry.place(fv, t["pos"], t["rot_z"], t["scale"])
    part(bm, "Fries_Pile", texel=8.0)

    boat_mat = materials.make_material("M_Fries_boat", [0.85, 0.30, 0.24],
                                       "paper")
    fry_mat = materials.make_material(
        f"M_Fries_{plan['material']}", plan["color"], plan["material"])
    for o in objs:
        materials.assign([o], boat_mat if "Boat" in o.name else fry_mat)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_center": (0, 0, h)}}
