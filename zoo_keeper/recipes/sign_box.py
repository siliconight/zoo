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
#: THE NAMED FACE TAKES LITTLE LIGHT (1.37.1). Its own lamp stands 0.29 m in
#: front of it (Lux), and at the pylon's 0.6 diffuse copy and the backlit
#: material's 0.35 roughness cold run 9122 photographed a white hot spot
#: mid-word on FLAPPAHS and TERMINAL A. The glow is unchanged; what the face
#: no longer does is mirror the lamp in front of it.
SIGN_ALBEDO = 0.15
SIGN_ROUGHNESS = 1.0


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]      # face width (DC: door + pad)
    d = plan["dimensions"]["depth"]      # cabinet depth
    h = plan["dimensions"]["height"]     # face height
    bevel, wear = plan["bevel"], plan["wear"]
    style = plan.get("style_block", {})
    rng = streams.stream("wear")
    objs = []

    # Face: the lit panel, its front at x=0 (the anchor plane). A sign pack
    # dresses it below; without one (1.37.0) it is painted art naming the
    # business, built here and lit in the block after the cabinet.
    face_t = 0.02
    pack = None
    if plan.get("sign_pack"):
        # 1.79.0: the business Level Factory dealt this building -- the pack
        # its street band wears -- so the door and the band are one name
        from ..core import skins as skinlib
        pack = skinlib.load_pack(str(plan["sign_pack"]))
    skins_dir, skin_theme = materials.get_skin_library()
    if pack is None and skins_dir:
        from ..core import skins as skinlib
        pack = skinlib.pick_pack(
            skinlib.find_sign_packs(skins_dir, skin_theme),
            str(plan.get("anchor_id", "")))
    face = None
    if pack:
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
    # each arm runs 2 cm INTO the cabinet (1.37.0): ending on its back put
    # the arm's end face on the cabinet's, the census's last shared plane
    for sy in (-1.0, 1.0):
        geometry.add_box(bm, (-d - arm_len / 2.0 + 0.01, sy * w * 0.35, 0.0),
                         (arm_len + 0.02, 0.05, 0.05))
    arms = geometry.bm_to_object(
        bm, "SignBox_Arms", collection, bevel=0.0, texel=1.5,
        rng=rng, wear=wear)
    objs.append(arms)

    mat = materials.make_material(
        f"M_SignBox_{plan['material']}", plan["color"], plan["material"])
    materials.assign([cabinet, arms], mat)

    # Branded face when the skin library ships sign packs (Pixelcoat
    # ``signs_<theme>/``): the pack albedo becomes the lit artwork, picked
    # deterministically per anchor id so each storefront keeps its sign
    # across rebuilds. The material name keeps the ``_Face`` suffix — Lux's
    # emissive binder keys on it, so the power cut kills branded and named
    # signs alike.
    if pack:
        _planar_uv_fit(face, w, h)
        lit = materials.make_emissive_textured_material(
            f"M_SignBox_{pack['id']}_Face", pack,
            style.get("emissive_strength", 2.2))
        materials.assign([face], lit)
    else:
        # NO PACK -> THE BUSINESS'S NAME (1.37.0). Until this the face was a
        # flat warm glow, and no theme ships a pack, so every derived sign
        # in the library -- 102 -- was a blank lit box (cold run 9120). The
        # name comes from the anchor's `business` (Deli Counter's identity
        # for the building); a sign without one is named from its anchor id,
        # which no kind matches, so it shows a street number -- never blank.
        from ..core import prims as P
        from ..core import storefront_names as SN
        from ..core import price_pylon_forms as PY
        from ._card_atlas import build_art
        said = SN.sign_for(plan.get("business") or plan.get("anchor_id", ""))
        front = P.mesh("SignBox_FaceFront", "glow",
                       [(0.0, -w / 2.0, -h / 2.0), (0.0, w / 2.0, -h / 2.0),
                        (0.0, w / 2.0, h / 2.0), (0.0, -w / 2.0, h / 2.0)], [(0, 1, 2, 3)])
        front["tile"] = "face"
        front["uvs"] = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))]
        # the panel's four edges; its front is the art and its back lies on
        # the cabinet's front (6 shared planes in the census until 1.37.0)
        rim = P.box("SignBox_FaceRim", "glow", (-face_t, -w / 2.0, -h / 2.0), (0.0, w / 2.0, h / 2.0))
        rim["faces"] = [f for k, f in enumerate(rim["faces"]) if k in (0, 1, 2, 4)]
        rim["tile"] = "edge"
        rim["uvs"] = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))] * len(rim["faces"])
        tiles = {"face": {"kind": "storefront_sign", "w_m": w, "h_m": h,
                          "text": said["text"], "colours": said["colours"]},
                 "edge": {"kind": "storefront_sign", "w_m": 0.1, "h_m": 0.1, "edge": True,
                          "text": "", "colours": said["colours"]}}
        got, _atlas = build_art([front, rim], collection, dict(plan, _tiles=tiles), streams,
                                "SignBox_Face", roughness=SIGN_ROUGHNESS,
                                lit=(PY.GLOW_EMISSION, SIGN_ALBEDO))
        objs += got
        print(f"[sign_box] {w:.2f} x {h:.2f} {said['kind']}: {said['text']}")

    # No collision: it's above head height, on a facade.
    return {"objects": objs, "collision_boxes": [], "attachments": {}}


def _planar_uv_fit(obj, width, height):
    """Fit the face's UVs 0..1 across its panel: cube-projected UVs are
    meters*texel (tiling — right for brick, wrong for a sign, which would
    repeat across any face wider than a meter). Local +X is outward, so the
    panel spans local Y (width) and Z (height); side slivers of the thin box
    smear edge pixels, which reads as the cabinet lip."""
    mesh = obj.data
    uv = mesh.uv_layers.active
    if uv is None:
        uv = mesh.uv_layers.new(name="UVMap")
    for loop in mesh.loops:
        co = mesh.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = (
            (co.y + width / 2.0) / width if width else 0.5,
            (co.z + height / 2.0) / height if height else 0.5)
