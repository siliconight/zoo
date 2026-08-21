"""vault_door recipe: the CLOSED armored vault door.

An interactive architectural module. The species builds only the closed
(locked/unlocked) state -- a heavy portal frame + a thick armored leaf filling
the opening + a wheel hub, center-pivot and built to the slot's exact dims. Its
OTHER states are handled by the slot's interactive.state_geometry (see
INTERACTIVES.md): `open` reuses `doorway` (the leaf gone, a passage), `breached`
reuses `breach` (blown), and `unlocked` is identical art to `locked` today so
the resolver falls back to the base. So this file only needs the closed door.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import arch


def build(plan, streams, collection):
    dims = plan["dimensions"]
    w, d, h = dims["width"], dims["depth"], dims["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    params = plan.get("params", {})
    rng = streams.stream("wear")
    root = arch.root_name("vault_door")           # "VaultDoor"
    objs, cboxes = [], []

    def emit(bm, name, bev=bevel, wr=wear):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bev,
                                    texel=1.2, rng=rng, wear=wr)
        objs.append(obj)
        return obj

    # 1) heavy portal frame (jambs + header + threshold lip) around the opening
    void = arch.void_for("vault_door", w, h, params)
    frame = arch.slab_parts(w, d, h, void)
    for name, center, size in frame:
        bm = geometry.new_bm()
        geometry.add_box(bm, center, size)
        emit(bm, f"{root}_{name}")
    cboxes.extend(arch.collision_boxes(frame))

    # opening rect (centered: jambs are symmetric so it's centred on x=0)
    ox0, ox1 = void["x0"], void["x1"]
    oz0, oz1 = void["z0"], void["z1"]
    ow, oh = ox1 - ox0, oz1 - oz0
    ocx, ocz = (ox0 + ox1) / 2.0, (oz0 + oz1) / 2.0

    # 2) the thick armored LEAF filling the opening, set into the FRONT of the
    #    portal. Everything stays within [-d/2, d/2] so the frame defines the
    #    exact outer box (fit-to-exact-dims holds). A closed vault door is solid
    #    -> the leaf gets collision (blocks the passage), unlike a doorway void.
    hub_len = min(0.14, d * 0.3)
    front = d / 2.0 - hub_len                     # leaf front sits behind hub
    leaf_frac = float(params.get("leaf_frac", 0.7))
    leaf_thick = max(0.05, min(leaf_frac * d, d - hub_len - 0.02))
    leaf_cy = front - leaf_thick / 2.0
    leaf_c = (ocx, leaf_cy, ocz)
    leaf_s = (ow * 0.98, leaf_thick, oh * 0.98)
    bm = geometry.new_bm()
    geometry.add_box(bm, leaf_c, leaf_s)
    emit(bm, f"{root}_Leaf")
    cboxes.append((tuple(leaf_c[i] - leaf_s[i] / 2.0 for i in range(3)),
                   tuple(leaf_c[i] + leaf_s[i] / 2.0 for i in range(3))))

    # 3) the wheel HUB: a short cylinder set into the front, its face flush with
    #    the portal's front plane (+d/2) so the module reads as a vault door and
    #    still fits the slot exactly. Decorative (no collision).
    hub_frac = float(params.get("hub_frac", 0.32))
    hub_r = max(0.05, hub_frac * min(ow, oh) / 2.0)
    hub_cy = d / 2.0 - hub_len / 2.0
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (ocx, hub_cy, ocz), hub_r, hub_len,
                          segments=16, axis="Y")
    emit(bm, f"{root}_Hub", bev=min(bevel, 0.004))

    # materials: armored metal for frame + leaf; hub a touch darker
    body_mat = materials.make_material(
        f"M_VaultDoor_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs[:-1], body_mat)
    # plan["material"], not the literal "metal": the body above already reads
    # the genome, and a hard-coded hub would leave one door split across two
    # material kinds the moment the genome moved off `metal`.
    hub_mat = materials.make_material(
        "M_VaultDoor_hub", [c * 0.75 for c in plan["color"]],
        plan["material"])
    materials.assign([objs[-1]], hub_mat)

    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
