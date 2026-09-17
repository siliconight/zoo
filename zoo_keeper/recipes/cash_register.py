"""cash_register recipe: a 1997 till, with the green display lit.

Planned in pure Python by `core.register_forms` -- every box, every digit and
every pixel -- and built by `bpylayer.prim_mesh`, except the three ART QUADS,
which carry their own UVs into one atlas this file paints. The shape, the
reference it was drawn from and the triangle budget are in that module; this
one only executes it.

TWO MATERIALS OFF ONE IMAGE, which is `vending_machine`'s split and made for
the same reason:

  * ``M_Register_<art>_Face`` is BACKLIT -- the customer display's green type
    is its own light, and the ``_Face`` suffix is what Lux's emissive binder
    cuts with the building's power. It is a MATERIAL and not a lamp: nothing
    here adds a Light3D, because Compatibility allows 8 lights on one mesh
    and the package this ships into already carries 84;
  * ``M_Register_<art>_Panel`` is PAINTED -- the operator's LCD is reflective
    (dark type on a green-grey ground: what the reference shows) and the
    keypad is printed plastic. `make_backlit_material` at strength 0 is not
    this and was not used for it; see that function.

FACETED ON PURPOSE, and no primitive asks for a bevel, so the module ships
the triangle count `register_forms.triangles` counted.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import register_forms as RF

#: Constants, not options a slot can ask for -- the lock's barrel is the one
#: bright thing on the front and a receipt is white, whatever the body is.
#: The same call `display_case` makes about its aluminium frame.
LOCK_RGB = [0.60, 0.61, 0.63]
PAPER_RGB = [0.86, 0.85, 0.82]
#: The trim -- the pull, the keypad island, the printer, the pole -- is the
#: body lifted by this much, NOT a second colour. A black register whose
#: every part is the same black is one silhouette with no parts in it, and
#: this is the smallest lift that separates them under a shop's fluorescents.
TRIM_LIFT = 0.045


def _trim(rgb):
    return [min(1.0, float(c) + TRIM_LIFT) for c in rgb]


def _art_object(quads, name, collection, atlas, mat, streams, stream):
    """Build art quads carrying their own UVs into ONE object with ONE
    material. Empty list -> no object, and no draw call for it."""
    if not quads:
        return []
    size = atlas["size"]
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    for q in quads:
        rect = atlas["rects"].get(q["tile"])
        if rect is None:
            raise KeyError(f"cash_register: quad {q['part']} names tile "
                           f"{q['tile']!r}, which the atlas does not hold")
        u0, v0, u1, v1 = RF.uv(rect, size)
        vs = [bm.verts.new(v) for v in q["verts"]]
        for face, corners in zip(q["faces"], q["uvs"]):
            f = bm.faces.new([vs[i] for i in face])
            for loop, c in zip(f.loops, corners):
                loop[uv].uv = (u0 + (u1 - u0) * c[0], v0 + (v1 - v0) * c[1])
    bm.normal_update()
    geometry.shade_by_angle(bm, 1.0)
    # a painted or lit face does not grime, and a white COLOR_0 is what makes
    # it arrive as painted through Level Factory's import (the `crt_tv` rule)
    geometry.wear_colors(bm, streams.stream(stream), 0.0)
    obj = geometry.bm_to_object(bm, name, collection, finish=False)
    materials.assign([obj], mat)
    return [obj]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    module = plan.get("module") or {}
    stem = module.get("stem") or "cash_register"
    price = RF.pick_price(plan, streams)
    got = RF.plan(w, d, h, params, int(module.get("variant") or 0),
                  price=price, key=stem)

    body_rgb = list(plan["color"])
    kind = plan["material"]
    mats = {
        RF.CASE: (f"M_Register_body_{kind}_{materials._tint_key(body_rgb)}",
                  body_rgb, kind),
        RF.TRIM: (f"M_Register_trim_{kind}_{materials._tint_key(_trim(body_rgb))}",
                  _trim(body_rgb), kind),
        RF.LOCK: ("M_Register_lock_metal_bare", list(LOCK_RGB), "metal_bare"),
        RF.PAPER: ("M_Register_paper", list(PAPER_RGB), "paper"),
    }
    prims = got["prims"]
    solid = [p for p in prims if not p.get("tile")]
    objs = prim_mesh.build(solid, collection, plan, streams.stream("wear"),
                           mats, texel=1.0)

    A = got["art"]
    image = materials.image_from_png(A["name"], A["canvas"].png())
    # `lit` 0 is a register with its plug pulled: the same artwork, no glow.
    # `vending_machine`'s switch, and the tag on the material name is what
    # keeps a lit and an unlit machine from sharing one cached material.
    lit_on = float(params.get("lit", 1)) > 0.0
    tag = A["name"] if lit_on else A["name"] + "_unlit"
    face = materials.make_backlit_material(
        f"M_Register_{tag}_Face", image,
        RF.SCREEN_EMISSION if lit_on else 0.0, RF.SCREEN_ALBEDO)
    panel = materials.make_painted_material(
        f"M_Register_{A['name']}_Panel", image, 0.40)
    quads = [p for p in prims if p.get("tile")]
    objs += _art_object([q for q in quads if q.get("lit")], "Register_Screen",
                        collection, A, face, streams, "register_screen")
    objs += _art_object([q for q in quads if not q.get("lit")], "Register_Art",
                        collection, A, panel, streams, "register_art")

    f = got["facts"]
    print(f"[cash_register] {w:.2f} x {d:.2f} x {h:.2f} price={f['price']} "
          f"digits={f['digits']} scale={f['digit_scale']} "
          f"digit_h={f['digit_h_m'] * 1000:.1f}mm screen={f['screen_m'][0]:.3f}"
          f"x{f['screen_m'][1]:.3f} m art={f['art']} "
          f"{f['tris']} tris (pure) of {f['budget']}")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": got["attachments"],
            "register": {"price": f["price"], "digits": f["digits"],
                         "art": f["art"], "tris": f["tris"]}}
