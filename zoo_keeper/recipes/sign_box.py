"""sign_box recipe: a lit storefront cabinet sign — emissive acrylic face,
shallow metal cabinet behind it, two standoff arms back to the wall. The
anchor is the FACE plane centre (DC emits it 0.2 m proud of the wall) and
local +X is outward, so the face sits at x=0 and everything else hangs
toward -X; the light-anchor pipeline mounts this 'center' (no vertical
lift). The face is glTF-emissive with the M_*_Face naming Lux's emissive
binder keys on, so cutting the building power kills the glow."""
from __future__ import annotations

from ..bpylayer import geometry, materials

_WALL_GAP = 0.2      # DC's _SIGN_OUT: distance from face plane back to wall


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]      # face width (DC: door + pad)
    d = plan["dimensions"]["depth"]      # cabinet depth
    h = plan["dimensions"]["height"]     # face height
    bevel, wear = plan["bevel"], plan["wear"]
    style = plan.get("style_block", {})
    rng = streams.stream("wear")
    objs = []

    # Face: the lit panel, its front at x=0 (the anchor plane).
    face_t = 0.02
    bm = geometry.new_bm()
    geometry.add_box(bm, (-face_t / 2.0, 0.0, 0.0), (face_t, w, h))
    face = geometry.bm_to_object(
        bm, "SignBox_Face", collection, bevel=0.0, texel=1.0,
        rng=rng, wear=0.0)
    objs.append(face)

    # Cabinet: the metal body behind the face, slightly smaller.
    cab_d = max(d - face_t, 0.06)
    bm = geometry.new_bm()
    geometry.add_box(bm, (-face_t - cab_d / 2.0, 0.0, 0.0),
                     (cab_d, w * 0.98, h * 0.96))
    cabinet = geometry.bm_to_object(
        bm, "SignBox_Cabinet", collection, bevel=bevel, texel=1.5,
        rng=rng, wear=wear)
    objs.append(cabinet)

    # Standoff arms: bridge the cabinet back to the wall at x = -_WALL_GAP.
    arm_len = max(_WALL_GAP - d, 0.02)
    bm = geometry.new_bm()
    for sy in (-1.0, 1.0):
        geometry.add_box(bm, (-d - arm_len / 2.0, sy * w * 0.35, 0.0),
                         (arm_len, 0.05, 0.05))
    arms = geometry.bm_to_object(
        bm, "SignBox_Arms", collection, bevel=0.0, texel=1.5,
        rng=rng, wear=wear)
    objs.append(arms)

    mat = materials.make_material(
        f"M_SignBox_{plan['material']}", plan["color"], plan["material"])
    materials.assign([cabinet, arms], mat)
    lit = materials.make_emissive_material(
        "M_SignBox_Face",
        style.get("emissive_color", [1.0, 0.93, 0.78]),
        style.get("emissive_strength", 2.2))
    materials.assign([face], lit)

    # No collision: it's above head height, on a facade.
    return {"objects": objs, "collision_boxes": [], "attachments": {}}
