"""CRT TV recipe: chunky plastic body, dark glass screen, small feet and
tuning knobs. 1990s tube-television silhouette. Origin at floor center,
screen faces -Y.

FORMS (0.87.0). ``stand`` -- and ``auto``, the default -- is the set on its
feet on a surface; ``bracket`` is a bar TV up on a wall bracket, tipped
toward the room, planned in pure Python by `core.crt_forms` and built by
`bpylayer.prim_mesh`.

0.90.0: the bracket set's screen is ON, showing a ballgame painted by
`core.crt_screens` (the module's variant picks the game), as a backlit
texture on a curved face. The stand set's parts come from
`crt_forms.stand_layout`, which fits the slot exactly and puts its glass in
front of the body where it can be seen -- 0.86.0 to 0.89.0 hung the knobs
22 mm past the slot and buried the screen inside the body. The stand set's
screen is still dark glass: a set on a surface is off.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import crt_forms, crt_screens


def _darker(c, f=0.6):
    return [v * f for v in c]


def build(plan, streams, collection):
    if crt_forms.pick_form((plan.get("params") or {}).get("form", "auto")) == "bracket":
        return _bracket(plan, streams, collection)
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    n_knobs = plan["params"].get("knobs", 2)
    objs, cboxes = [], []

    def part(bm, name, texel=2.0):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=texel, rng=rng, wear=wear))

    L = crt_forms.stand_layout(w, d, h, n_knobs)
    c, size = L["body"][0]
    bm = geometry.new_bm()
    geometry.add_box(bm, c, size)
    part(bm, "CRT_Body")
    cboxes.append(((-w / 2, -d / 2, 0), (w / 2, d / 2, h)))

    # the glass, proud of the body's front face
    for c, size in L["screen"]:
        bm = geometry.new_bm()
        geometry.add_box(bm, c, size)
        part(bm, "CRT_Screen")

    # tuning knobs, lower-right of the front face, their caps on the slot's
    # front plane
    for i, (c, radius, depth) in enumerate(L["knobs"]):
        bm = geometry.new_bm()
        geometry.add_cylinder(bm, c, radius=radius, depth=depth, segments=12, axis="Y")
        part(bm, f"CRT_Knob_{i + 1}")

    # two feet, buried into the body's underside
    for side, (c, size) in zip(("L", "R"), L["feet"]):
        bm = geometry.new_bm()
        geometry.add_box(bm, c, size)
        part(bm, f"CRT_Foot_{side}")

    body_mat = materials.make_material(
        f"M_CRT_{plan['material']}", plan["color"], plan["material"])
    screen_mat = materials.make_material(
        "M_CRT_screen", [0.03, 0.04, 0.05], "glass")
    knob_mat = materials.make_material(
        "M_CRT_knob", _darker(plan["color"], 0.4), "plastic")
    screens = [o for o in objs if "Screen" in o.name]
    knobs = [o for o in objs if "Knob" in o.name or "Foot" in o.name]
    materials.assign(screens, screen_mat)
    materials.assign(knobs, knob_mat)
    materials.assign([o for o in objs if o not in screens and o not in knobs],
                     body_mat)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_screen_center": L["screen_centre"]}}


def _bracket(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    got = crt_forms.plan_bracket(w, d, h)
    # the genome's kind and colour are the stand set's; the bracket set's
    # housing is `crt_forms.MATERIALS` (why is written there)
    mats = {key: (f"M_CRT_{key}_{k}", list(c), k)
            for key, (c, k) in crt_forms.MATERIALS.items()}
    screens = [p for p in got["prims"] if p["part"] == "CRT_Screen"]
    rest = [p for p in got["prims"] if p["part"] != "CRT_Screen"]
    objs = prim_mesh.build(rest, collection, plan, streams.stream("wear"), mats, texel=2.0)

    game = crt_screens.pick_game(plan, streams)
    canvas, facts = crt_screens.paint(game)
    image = materials.image_from_png(facts["name"], canvas.png())
    face = materials.make_backlit_material(f"M_CRT_Screen_{facts['name']}_Face", image,
                                           crt_forms.SCREEN_EMISSION, crt_forms.SCREEN_ALBEDO)
    for p in screens:
        bm = geometry.new_bm()
        vs = [bm.verts.new(v) for v in p["verts"]]
        faces = [bm.faces.new([vs[i] for i in f]) for f in p["faces"]]
        uv = bm.loops.layers.uv.new("UVMap")
        for face_, corners in zip(faces, p["uvs"]):
            for loop, co in zip(face_.loops, corners):
                loop[uv].uv = co
        bm.normal_update()
        # a curved face: smooth across the grid, hard at its sides
        geometry.shade_by_angle(bm)
        # a lit face does not grime; a white COLOR_0 keeps Level Factory's
        # import from dimming it
        geometry.wear_colors(bm, streams.stream("crt_screen_wear"), 0.0)
        obj = geometry.bm_to_object(bm, "CRT_Screen", collection, finish=False)
        materials.assign([obj], face)
        objs.append(obj)
    print(f"[crt_tv] bracket game={facts['game']} sport={facts['sport']} scene={facts['scene']} "
          f"bug={' / '.join(facts['bug'])} art={facts['name']}")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_screen_center": got["screen_centre"]},
            "crt": {"game": facts["game"], "sport": facts["sport"], "art": facts["name"]}}
