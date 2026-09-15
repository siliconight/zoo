"""dartboard recipe: a bar's wall dartboard cabinet, doors open or shut, with
a bristle board, chalkboard doors and a chalk tray.

Planned in pure Python by `core.dartboard_forms.plan` (every size, the
opening, the collision box and the bull's position) and painted by
`core.dartboard_art` (the board and both chalkboards, from the module's
variant: the brand, the game in chalk, the wear). Built by
`bpylayer.prim_mesh`, except the two textured parts -- the board's face and
the chalk panels -- which carry their own UVs and a painted material
(`materials.make_painted_material`), built the way the bracket TV's screen
is.

A VARIANT is a different board: another invented brand, another stage of
the game chalked on the doors, stained wood or black paint, other flights,
and darts stuck in the board instead of on the rails.

The back is the slot's +Y face, the wall; the board faces -Y. The bull is
the slot's centre height (``ATT_bull``). Collision is the cabinet box only.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import dartboard_art as ART
from ..core import dartboard_forms as F

#: Roughness of the painted faces: sisal is matte, slate a little less.
BOARD_ROUGHNESS = 0.92
CHALK_ROUGHNESS = 0.86


def _hex(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def _uv_object(prims, name, collection, material, rng):
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
    # painted artwork is not grimed: a white COLOR_0 leaves it as painted
    geometry.wear_colors(bm, rng, 0.0)
    obj = geometry.bm_to_object(bm, name, collection, finish=False)
    materials.assign([obj], material)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    brand, variant, key = ART.pick(plan)
    got = F.plan(w, d, h, params.get("form", "auto"), variant)
    v = variant % 4
    board, bfacts = ART.paint_board(brand, v, key)
    pw, ph = F.chalk_panel_size(got)
    chalk = ART.chalk_art(pw, ph, brand, v, key)
    prims = F.resolve_uvs(got["prims"], chalk["rects"], chalk["size"])

    kind, colour = F.CABINET[v]
    mats = {k: (f"M_Dartboard_{k}_{_hex(c)}_{kk}", list(c), kk) for k, (c, kk) in F.MATERIALS.items()}
    mats["cabinet"] = (f"M_Dartboard_cabinet_{_hex(colour)}_{kind}", list(colour), kind)
    for i, c in enumerate(F.FLIGHTS[v]):
        mats[f"flight_{i}"] = (f"M_Dartboard_flight_{_hex(c)}", list(c), "plastic")
    textured = [p for p in prims if p["mat"] in ("board", "chalkboard")]
    rest = [p for p in prims if p["mat"] not in ("board", "chalkboard")]
    objs = prim_mesh.build(rest, collection, plan, streams.stream("wear"), mats, texel=1.0)

    rng = streams.stream("dartboard_paint")
    b_img = materials.image_from_png(bfacts["name"], board.png())
    c_img = materials.image_from_png(chalk["name"], chalk["canvas"].png())
    b_mat = materials.make_painted_material(f"M_Dartboard_Board_{bfacts['name']}", b_img,
                                            BOARD_ROUGHNESS)
    c_mat = materials.make_painted_material(f"M_Dartboard_Chalk_{chalk['name']}", c_img,
                                            CHALK_ROUGHNESS)
    objs.append(_uv_object([p for p in textured if p["mat"] == "board"], "Dartboard_Board",
                           collection, b_mat, rng))
    objs.append(_uv_object([p for p in textured if p["mat"] == "chalkboard"],
                           "Dartboard_Chalkboard", collection, c_mat, rng))
    stages = {k: f["stage"] for k, f in chalk["facts"].items()}
    print(f"[dartboard] form={got['form']} angle={got['angle_deg']:.1f} brand={brand} "
          f"variant={v} cabinet={kind} chalk={stages['L']} stuck={got['facts']['stuck']} "
          f"rails={got['facts']['rails']} board={bfacts['name']} chalk_art={chalk['name']}")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_bull": tuple(got["bull"])},
            "dartboard": {"brand": brand, "variant": v, "form": got["form"],
                          "angle_deg": round(got["angle_deg"], 2),
                          "chalk_stage": stages["L"], "board_art": bfacts["name"],
                          "chalk_art": chalk["name"]}}
