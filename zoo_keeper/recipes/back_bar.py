"""back_bar recipe: the lit wall unit behind a bar.

Zoo 0.92.0, from the walker's club bar photos (see `core.back_bar_forms`,
which plans every dimension in pure Python, and `core.back_bar_art`, which
paints the bottle labels).

Built by `bpylayer.prim_mesh`, except the LABELS -- one quad a bottle,
carrying its own UVs into the atlas and a painted material, the way the
dartboard's board and the bracket TV's screen are built.

WHAT IS LIT, and therefore what a power cut takes. The bulbs behind the
shelves and the porthole's disc are emissive: ``M_BackBar_bulb_Face`` and
``M_BackBar_niche_Face``, the ``_Face`` suffix Lux's emissive binder cuts
with the room's power. `prim_mesh.build` paints a lit material with no wear
and no ambient, so its COLOR_0 stays white and Level Factory's import
leaves the albedo alone.

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
    mats["niche_lit"] = ("M_BackBar_niche_Face", list(F.NICHE_COLOUR),
                         "emissive", F.NICHE_STRENGTH)
    labels = [p for p in prims if p["mat"] == "label"]
    rest = [p for p in prims if p["mat"] != "label"]
    objs = prim_mesh.build(rest, collection, plan, streams.stream("wear"), mats,
                           texel=1.0)

    rng = streams.stream("back_bar_labels")
    image = materials.image_from_png(atlas["name"], atlas["canvas"].png())
    paint = materials.make_painted_material(f"M_BackBar_{atlas['name']}", image,
                                            LABEL_ROUGHNESS)
    objs.append(_uv_object(labels, "BackBar_Label", collection, paint, rng))

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
