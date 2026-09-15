"""cigarette_machine recipe: a 1990s pull-knob cigarette machine on splayed
legs, chrome and woodgrain, two rows of packs behind the front.

Planned in pure Python by `core.cigarette_forms` -- the layout, the brands
and the display's artwork -- and built by `bpylayer.prim_mesh`, except the
display insert, which carries its own UVs and two materials on one mesh:
the header ad is backlit faintly (`materials.make_backlit_material`, named
``M_CigMachine_<art>_Face`` so Lux's power cut takes it) and the pack rows,
strips and middle panel are painted (`materials.make_painted_material`).

FORMS: ``pull_knob`` (``auto``) with a second ad between the rows,
``pull_knob_split`` with the black CIGARETTES panel there. A VARIANT is
another header brand, another run of packs, chrome or amber knobs and cream
display cards or none.

The back is the slot's +Y face, the wall; the front faces -Y. Collision is
the cabinet box.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import cigarette_forms as CF


def _hex(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    form = CF.pick_form(params.get("form", "auto"))
    brand, variant, key, knobs, cards = CF.resolve(plan)
    got = CF.plan(w, d, h, knobs)
    A = CF.art(got["facts"], brand, variant, key, form, cards)
    size = A["size"]
    art_uv = CF.uv_rect((0, 0, size[0], size[1] - 6), size)
    dark_uv = CF.uv_rect(A["rects"]["dark"], size)

    mats = {k: (f"M_CigMachine_{k}_{_hex(c)}_{kk}", list(c), kk) for k, (c, kk) in CF.MATERIALS.items()}
    display = [p for p in got["prims"] if p["mat"] == "display"]
    rest = [p for p in got["prims"] if p["mat"] != "display"]
    objs = prim_mesh.build(rest, collection, plan, streams.stream("wear"), mats, texel=1.0)

    image = materials.image_from_png(A["name"], A["canvas"].png())
    lit = materials.make_backlit_material(f"M_CigMachine_{A['name']}_Face", image,
                                          CF.HEADER_EMISSION, CF.HEADER_ALBEDO)
    paint = materials.make_painted_material(f"M_CigMachine_{A['name']}_Display", image,
                                            CF.DISPLAY_ROUGHNESS)
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    for p in display:
        vs = [bm.verts.new(v) for v in p["verts"]]
        for f, corners, fm in zip(p["faces"], p["uvs"], p["face_mats"]):
            face = bm.faces.new([vs[i] for i in f])
            face.material_index = 1 if fm == "lit" else 0
            for loop, c in zip(face.loops, corners):
                if c[0] == "art":
                    loop[uv].uv = (art_uv[0] + (art_uv[2] - art_uv[0]) * c[1],
                                   art_uv[1] + (art_uv[3] - art_uv[1]) * c[2])
                else:
                    loop[uv].uv = ((dark_uv[0] + dark_uv[2]) / 2.0, (dark_uv[1] + dark_uv[3]) / 2.0)
    bm.normal_update()
    geometry.shade_by_angle(bm, 1.0)
    # the art is not grimed, and the lit face must keep a white COLOR_0
    geometry.wear_colors(bm, streams.stream("cig_display"), 0.0)
    obj = geometry.bm_to_object(bm, "Cig_Display", collection, finish=False)
    obj.data.materials.append(paint)
    obj.data.materials.append(lit)
    objs.append(obj)

    rows = A["brands"]["rows"]
    print(f"[cigarette_machine] form={form} header={brand} variant={variant % 4} knobs={knobs} "
          f"cards={cards} packs={got['facts']['n_packs']}x2 row1={','.join(rows[1])} art={A['name']}")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_tray": (0.0, -d / 2.0, (got["facts"]["tray"][2] + got["facts"]["tray"][3]) / 2.0)},
            "cigarette_machine": {"form": form, "header": brand, "variant": variant % 4,
                                  "knobs": knobs, "cards": cards, "art": A["name"]}}
