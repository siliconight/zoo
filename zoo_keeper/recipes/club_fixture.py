"""club_fixture recipe: the hardware a club's coloured light comes out of.

Zoo 0.94.0, from the walker's frame of the strip club's main floor -- see
`core.club_fixture_forms`, which plans every dimension in pure Python and
carries the reason this species exists.

Two forms: ``can`` (a surface-mounted downlight, for a `club_wash`) and
``par`` (a PAR can on a yoke with barn doors, for a `stage_light`). Built
CENTRED, lens facing -Z, so the light-anchor pipeline's ``above`` mount puts
the lit face exactly on the anchor Lux puts its lamp at; a `par` is tilted
about that lens by the placement's `tilt_deg` before it is dropped in.

WHAT IS LIT: one face, ``M_ClubFixture_Lens_<hex>_Lens``, in the anchor's own
gel colour, so Lux's emissive binder cuts it with the room's power and so the
lens agrees with the pool underneath it. The barrel and the baffle are dark
metal: a can that is bright all over is a disc, not a fixture.

NO COLLISION and NO EMITTER MARKER. Ceiling hardware is not walked into, and
the club set's LIGHT stays on the manifest bake (`LuxLightLoader.bake_club`)
because the marker path hands the tuning table only {type, id, drop} -- a
wash would lose its zone colour and its pool radius, a stage light its
target. `core.fixtures` records that decision per type; see `FIXTURES`.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from ..core import club_fixture_forms as F


def _hex(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    form = str(params.get("form") or "can")
    got = F.plan(form, w, d, h)
    rng = streams.stream("wear")
    bevel, wear = plan["bevel"], plan["wear"]

    groups = {"body": geometry.new_bm(), "dark": geometry.new_bm(),
              "lens": geometry.new_bm()}
    names = {}
    for p in got["parts"]:
        bm = groups[p["part"]]
        names.setdefault(p["part"], p["name"])
        if p["kind"] == "cyl":
            geometry.add_cylinder(bm, p["center"], p["radius"], p["depth"],
                                  segments=F.SEGMENTS,
                                  radius_top=p.get("radius_top"))
        else:
            verts = geometry.add_box(bm, (0.0, 0.0, 0.0), p["size"])
            geometry.place(verts, p["center"], rot_z=math.radians(
                float(p.get("rot_z", 0.0))))

    objs = []
    body_mat = materials.make_material(
        f"M_ClubFixture_{plan['material']}_{_hex(plan['color'])}",
        plan["color"], plan["material"])
    # the baffle and the yoke: the same metal, taken most of the way to
    # black. A lit lens inside a pale throat has no depth from below.
    dark = [c * 0.34 for c in plan["color"][:3]]
    dark_mat = materials.make_material(
        f"M_ClubFixture_dark_{_hex(dark)}", dark, plan["material"])
    gel = F.gel(params.get("gel"))
    lens_mat = materials.make_emissive_material(
        f"M_ClubFixture_{_hex(gel)}_Lens", list(gel), F.LENS_STRENGTH)

    for key, mat, this_wear in (("body", body_mat, wear),
                                ("dark", dark_mat, wear * 0.6),
                                ("lens", lens_mat, 0.0)):
        bm = groups[key]
        if not bm.faces:
            bm.free()
            continue
        obj = geometry.bm_to_object(
            bm, names.get(key, "ClubFixture_Body"), collection,
            bevel=bevel if key != "lens" else 0.0, texel=1.5, rng=rng,
            wear=this_wear)
        materials.assign([obj], mat)
        objs.append(obj)

    f = got["facts"]
    print("[club_fixture] form=%s w=%.3f h=%.3f lens_r=%.3f gel=%s parts=%d"
          % (f["form"], w, h, f["lens_r"], params.get("gel") or "-",
             f["parts"]))
    return {"objects": objs, "collision_boxes": [], "attachments": {},
            "club_fixture": {"form": f["form"], "lens_r": f["lens_r"],
                             "lens_z": f["lens_z"],
                             "gel": params.get("gel") or ""}}
