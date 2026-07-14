"""wall_pack recipe: an exterior wall-pack light over a service door — wedge
body with an emissive lens on the underside, mounting arm back to the wall.
The anchor is the EMITTER in free air under the lens (DC emits it 0.15 m
proud of the wall, 0.25 m above the door head) and local +X is outward; the
light-anchor pipeline mounts this 'above', so the recipe's bottom (-h/2)
lands at the anchor and Lux's downward spot spawns just beneath the lens.
The lens carries the M_*_Lens naming Lux's emissive binder keys on."""
from __future__ import annotations

from ..bpylayer import geometry, materials

_WALL_GAP = 0.15     # DC's _WALL_PACK_OUT: emitter distance from the wall


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]      # along the wall
    d = plan["dimensions"]["depth"]      # proud of the wall
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    style = plan.get("style_block", {})
    rng = streams.stream("wear")
    z0 = -h / 2.0
    objs = []

    # Lens: emissive underside at the bottom, centred over the emitter.
    lens_t = 0.02
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + lens_t / 2.0),
                     (d * 0.8, w * 0.85, lens_t))
    lens = geometry.bm_to_object(
        bm, "WallPack_Lens", collection, bevel=0.0, texel=1.0,
        rng=rng, wear=0.0)
    objs.append(lens)

    # Body: the wedge above the lens (a box reads fine at sixth-gen).
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + lens_t + (h - lens_t) / 2.0),
                     (d, w, h - lens_t))
    body = geometry.bm_to_object(
        bm, "WallPack_Body", collection, bevel=bevel, texel=1.5,
        rng=rng, wear=wear)
    objs.append(body)

    # Arm: bridge the body back to the wall plane at x = -_WALL_GAP.
    arm_len = max(_WALL_GAP - d / 2.0, 0.02)
    bm = geometry.new_bm()
    geometry.add_box(bm, (-d / 2.0 - arm_len / 2.0, 0.0, z0 + h * 0.6),
                     (arm_len, w * 0.4, h * 0.3))
    arm = geometry.bm_to_object(
        bm, "WallPack_Arm", collection, bevel=0.0, texel=1.5,
        rng=rng, wear=wear)
    objs.append(arm)

    mat = materials.make_material(
        f"M_WallPack_{plan['material']}", plan["color"], plan["material"])
    materials.assign([body, arm], mat)
    lit = materials.make_emissive_material(
        "M_WallPack_Lens",
        style.get("emissive_color", [1.0, 0.78, 0.45]),
        style.get("emissive_strength", 2.2))
    materials.assign([lens], lit)

    # No collision: above head height over a door.
    return {"objects": objs, "collision_boxes": [], "attachments": {}}
