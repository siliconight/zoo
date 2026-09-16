"""back_bar recipe: the lit wall unit behind a bar.

Zoo 0.92.0, from the walker's club bar photos (see `core.back_bar_forms`,
which plans every dimension in pure Python, and `core.back_bar_art`, which
paints the bottle labels).

Built by `bpylayer.prim_mesh`, except the LABELS -- one quad a bottle,
carrying its own UVs into the atlas and a painted material, the way the
dartboard's board and the bracket TV's screen are built.

WHAT IS LIT, and therefore what a power cut takes. The bulbs behind the
shelves and the porthole's face are emissive: ``M_BackBar_bulb_Face`` and
``M_BackBar_backbar_niche_<n>_<digest>_Face``, the ``_Face`` suffix Lux's
emissive binder cuts with the room's power. `prim_mesh.build` paints a lit
material with no wear and no ambient, so its COLOR_0 stays white and Level
Factory's import leaves the albedo alone. The porthole is a BACKLIT RASTER
rather than a flat emissive colour (0.94.0): a flat lit n-gon is a sun, and
the walker's frame of one said so.

FORMS: ``straight`` (a mirror in the centre bay) and ``niche`` (the round
lit porthole); ``auto`` takes the porthole wherever the centre bay is wide
enough for one. A VARIANT is another draw from the liquor table -- a
different rotation of brands across the shelves -- another stage of label
wear, and the worktop's glass towers and bottles swapped bay for bay.

The back is the slot's +Y face, the wall; the front faces -Y. Collision is
the whole unit's box: a body walks into a back bar, it does not walk into
the shelves.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import back_bar_art as ART
from ..core import back_bar_forms as F

#: A printed paper label on glass: matte, a touch less than the dartboard's
#: chalk panel (0.86) and its sisal (0.92).
LABEL_ROUGHNESS = 0.88
#: How much of the diffuser's artwork also drives its BASE colour. The
#: vending panel's 0.35 is a backlit advert, which is meant to be readable
#: with the tubes off; a porthole with the power cut is a dark glass hole in
#: a dark cabinet, so it keeps less.
NICHE_ALBEDO = 0.22


def _hex(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def _uv_object(prims, name, collection, material, rng):
    """One mesh from primitives that carry their own UVs (the labels)."""
    bm = geometry.new_bm()
    uv = None
    for p in prims:
        vs = [bm.verts.new(v) for v in p["verts"]]
        faces = [bm.faces.new([vs[i] for i in f]) for f in p["faces"]]
        uv = uv or bm.loops.layers.uv.new("UVMap")
        for face, corners in zip(faces, p["uvs"]):
            for loop, co in zip(face.loops, corners):
                loop[uv].uv = co
    bm.normal_update()
    geometry.shade_by_angle(bm, 1.0)
    # printed artwork is not grimed: a white COLOR_0 leaves it as painted
    geometry.wear_colors(bm, rng, 0.0)
    obj = geometry.bm_to_object(bm, name, collection, finish=False)
    materials.assign([obj], material)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    variant = int(params.get("variant") or 0)
    key = (plan.get("module") or {}).get("stem") or plan.get("species", "back_bar")
    got = F.plan(w, d, h, params.get("form", "auto"), variant, key)

    atlas = ART.label_atlas(got["brands"], key=key, variant=variant)
    prims = F.resolve_uvs(got["prims"], atlas["rects"], atlas["size"])

    mats = {k: (f"M_BackBar_{k}_{_hex(c)}_{kk}", list(c), kk)
            for k, (c, kk) in F.materials(plan["color"], plan["material"]).items()}
    mats["bulb"] = ("M_BackBar_bulb_Face", list(F.BULB_COLOUR), "emissive",
                    F.BULB_STRENGTH)
    labels = [p for p in prims if p["mat"] == "label"]
    glow = [p for p in prims if p["mat"] == "niche_lit"]
    rest = [p for p in prims if p["mat"] not in ("label", "niche_lit")]
    objs = prim_mesh.build(rest, collection, plan, streams.stream("wear"), mats,
                           texel=1.0)

    rng = streams.stream("back_bar_labels")
    image = materials.image_from_png(atlas["name"], atlas["canvas"].png())
    paint = materials.make_painted_material(f"M_BackBar_{atlas['name']}", image,
                                            LABEL_ROUGHNESS)
    objs.append(_uv_object(labels, "BackBar_Label", collection, paint, rng))

    # THE PORTHOLE IS A DIFFUSER, NOT A LIT DISC (0.94.0). A flat emissive
    # face of one colour is a sun at any strength that reads as a light (see
    # `back_bar_art.NICHE_PX` for the frame that says so); a raster with a
    # core and a falloff is a frosted lamp. Backlit rather than plain
    # emissive so the face is DIMMED as albedo too -- a lamp behind glass is
    # not a mirror of the room -- and named `_Face` so the power cut still
    # takes it with the room, exactly as the flat material was.
    if glow:
        art = ART.niche_art(F.NICHE_COLOUR)
        lit = materials.make_backlit_material(
            f"M_BackBar_{art['name']}_Face",
            materials.image_from_png(art["name"], art["canvas"].png()),
            F.NICHE_STRENGTH, NICHE_ALBEDO)
        objs.append(_uv_object(glow, "BackBar_NicheLamp", collection, lit, rng))

    f = got["facts"]
    print(f"[back_bar] form={got['form']} bays={f['bays']} tiers={f['tiers']} "
          f"pitch={f['tier_pitch']:.3f} counter={f['counter_h']:.3f} "
          f"bottles={f['bottles']} stems={f['stems']} bulbs={f['bulbs']} "
          f"brands={len(got['brands'])} tris={f['tris']} art={atlas['name']}")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {k: tuple(v) for k, v in got["attachments"].items()},
            "back_bar": {"form": got["form"], "variant": variant % 4,
                         "bays": f["bays"], "tiers": f["tiers"],
                         "bottles": f["bottles"], "stems": f["stems"],
                         "bulbs": f["bulbs"], "brands": list(got["brands"]),
                         "art": atlas["name"]}}
