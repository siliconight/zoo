"""1.82.0 -- the crew's getaway van (roadmap 206).

The walker, 2026-10-07: "a Box Truck. Like a Chevrolet P30. Matte
Black....faded, with patina, like a worn in truck...that's been on many
jobs", parked at the mission's spawn. Pure half (`core/van_forms.py`): the
van fills its slot exactly, its parts stand in a step van's order at every
genome corner, the wheels sit in their arches and on the ground, the crew's
door is wider than the crew, and the finish reads black first and faded
second -- rust low on the sides, never on the roof, one primer patch on the
kerb side -- in the genome's own colour, the same van every time. The
recipe read as source: one paint material, the plan's kind and colour.
Built half (bpy, skipped without it): PASS and an exact fit, five
submissions, the paint in the vertex, the same file every build.
"""
from __future__ import annotations

import ast
import itertools
import os
import re
import statistics

import pytest

from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import skins
from zoo_keeper.core import van_forms as V

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "step_van.py")
_MATERIALS = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "materials.py")


def _g():
    return genome_mod.load_species("step_van")


def _corners():
    r = _g()["dimensions"]
    return [tuple(c) for c in itertools.product(
        *((r[a]["min"], r[a]["default"], r[a]["max"]) for a in ("width", "depth", "height")))]


CORNERS = _corners()

#: MEASURED in Blender 5.1.1, 2026-10-07, on the recipe as shipped:
#: `tools/coplanar_probe.py --species step_van --dims W D H` at the genome's
#: corners and three sizes between them, and `tools/coplanar_census.py
#: --species step_van` at the corners ("3 builds, 0 with coincident pairs, 0
#: that did not build"). Triangles and coincident pairs within the probe's
#: 2 mm. The first probe read 10-12 pairs a build; every one was moved at
#: its source (see `van_forms.CAB_ROOF_INSET` and the recipe's comments).
MEASURED = {(2.4, 6.0, 2.9): (4640, 0), (2.6, 6.8, 3.05): (4860, 0),
            (2.8, 7.6, 3.3): (5080, 0), (2.5, 6.4, 3.0): (4662, 0),
            (2.7, 7.2, 3.2): (4948, 0), (2.45, 7.5, 2.95): (5058, 0)}

#: The crew's body radius, `characters.player.radius_m` in Deli Counter's
#: agent_contract.json. Pinned as a literal: Zoo does not read that contract.
CREW_RADIUS = 0.35


def _lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _side_and_roof(lay, base=V.BASE):
    """Luminance over the box's +X side (sill to roof) and its roof, on a
    5 cm grid, and the red excess (r - b) on the roof and low on the side."""
    hw, zr, zs = lay["hw"], lay["z_roof"], lay["z_sill"]
    ys = [lay["y_cab"] + 0.02 + k * 0.05 for k in range(int((lay["y_r"] - lay["y_cab"]) / 0.05))]
    zs_ = [zs + k * 0.05 for k in range(int((zr - zs) / 0.05))]
    xs = [-hw + 0.1 + k * 0.1 for k in range(int(2 * hw / 0.1) - 1)]
    side, roof, rb_roof, rb_low = [], [], [], []
    for y in ys:
        for z in zs_:
            c = V.finish_rgb((hw, y, z), (1.0, 0.0, 0.0), lay, base)
            side.append(_lum(c))
            if z < zs + 0.35:
                rb_low.append(c[0] - c[2])
        for x in xs:
            c = V.finish_rgb((x, y, zr), (0.0, 0.0, 1.0), lay, base)
            roof.append(_lum(c))
            rb_roof.append(c[0] - c[2])
    return side, roof, rb_roof, rb_low


# --------------------------------------------------------------------------- #
# The pure half: where the parts stand
# --------------------------------------------------------------------------- #

def test_the_genome_validates_and_names_every_part_the_recipe_builds():
    g = _g()
    assert genome_mod.validate_genome(g) == []
    assert g["license"]["construction_knowledge"] == "CC0"
    parts = set(g["parts"])
    src = open(_RECIPE, encoding="utf-8").read()
    named = set(re.findall(r'"(StepVan_[A-Za-z]+)"', src))
    named |= {n.rstrip("_") for n in re.findall(r'"(StepVan_[A-Za-z]+_)"', src)}
    assert named and named <= parts, sorted(named - parts)


@pytest.mark.parametrize("dims", CORNERS)
def test_the_slot_is_exact(dims):
    """Width is the mirror heads, depth the bumpers, height the clearance
    lamps: the slot the greybox site hands Laser Tag is the van."""
    W, L, H = dims
    lay = V.layout(W, L, H)
    assert abs(2.0 * (lay["hw"] + V.MIRROR_OUT) - W) < 1e-9
    assert abs((lay["yt"] - lay["y0"]) - L) < 1e-9
    assert abs((lay["z_roof"] + V.ROOF_LAMP) - H) < 1e-9


@pytest.mark.parametrize("dims", CORNERS)
def test_the_parts_stand_in_a_step_vans_order(dims):
    lay = V.layout(*dims)
    ys = [lay[k] for k in ("y0", "y_n", "y_ws", "y_wt", "y_cab", "y_r", "yt")]
    assert ys == sorted(ys) and len(set(ys)) == len(ys), ys
    zs = [lay[k] for k in ("z_sill", "z_arch", "z_nose", "z_belt", "z_roof")]
    assert zs == sorted(zs) and len(set(zs)) == len(zs), zs
    # a longer slot is a longer box behind the same cab
    assert lay["y_cab"] - lay["y_n"] == pytest.approx(V.NOSE_LEN + V.CAB_LEN)
    assert lay["y_r"] - lay["y_cab"] > V.CAB_LEN


@pytest.mark.parametrize("dims", CORNERS)
def test_the_wheels_sit_in_their_arches(dims):
    lay = V.layout(*dims)
    r, A = lay["r"], lay["arch"]
    assert lay["y_n"] < lay["ya_f"] - A and lay["ya_f"] + A < lay["y_cab"]
    assert lay["y_cab"] < lay["ya_r"] - A and lay["ya_r"] + A < lay["y_r"]
    assert A - r >= 0.10 and lay["z_arch"] - 2.0 * r >= 0.05


@pytest.mark.parametrize("seg", range(10, 21))
def test_the_tread_touches_the_ground_at_any_wheel_count(seg):
    """`_lathe_x` sets a vertex every 360/seg degrees from the axle's level.
    At the default 14 an axle at r floated the built van 10.3 mm."""
    import math
    r = 0.41
    za = V.axle_height(r, seg)
    lowest = min(za + r * math.sin(2.0 * math.pi * k / seg) for k in range(seg))
    assert abs(lowest) < 1e-12, (seg, lowest)
    assert (za == pytest.approx(r)) == (seg % 4 == 0), (seg, za)


@pytest.mark.parametrize("dims", CORNERS)
def test_the_crews_door_is_wider_than_the_crew(dims):
    """The kerb-side door, between the front arch and the bulkhead: where
    the crew gets in and out (`ATT_side_door`)."""
    lay = V.layout(*dims)
    assert lay["ya_f"] + lay["arch"] < lay["y_door0"] < lay["y_door1"] < lay["y_cab"]
    assert lay["y_door1"] - lay["y_door0"] >= 2.0 * CREW_RADIUS


@pytest.mark.parametrize("dims", CORNERS)
def test_the_primer_patch_is_on_the_kerb_side_of_the_box(dims):
    lay = V.layout(*dims)
    px, py, pz, prad = lay["primer"]
    assert px < 0.0
    assert lay["y_cab"] < py - prad and py + prad < lay["y_r"]
    assert lay["z_sill"] < pz - 0.7 * prad


# --------------------------------------------------------------------------- #
# The pure half: the finish
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("dims", CORNERS)
def test_the_van_reads_black_first_and_faded_second(dims):
    """Half the side darker than 0.06 linear (measured 0.051-0.053), the
    roof's sun-chalk at least 1.3 times that (measured 0.078-0.080). The
    first draft chalked the sides linearly and read as a mid-grey van."""
    side, roof, _rb_roof, _rb_low = _side_and_roof(V.layout(*dims))
    med = statistics.median(side)
    assert med < 0.06, med
    assert statistics.mean(roof) > 1.3 * med, (statistics.mean(roof), med)


@pytest.mark.parametrize("dims", CORNERS)
def test_rust_blooms_low_on_the_sides_and_never_on_the_roof(dims):
    _side, _roof, rb_roof, rb_low = _side_and_roof(V.layout(*dims))
    assert max(rb_roof) <= 0.01, max(rb_roof)
    assert max(rb_low) >= 0.10, max(rb_low)


@pytest.mark.parametrize("dims", CORNERS)
def test_the_primer_shows_on_the_kerb_side_only(dims):
    lay = V.layout(*dims)
    hw = lay["hw"]
    _px, py, pz, _pr = lay["primer"]
    kerb = _lum(V.finish_rgb((-hw, py, pz), (-1.0, 0.0, 0.0), lay))
    road = _lum(V.finish_rgb((hw, py, pz), (1.0, 0.0, 0.0), lay))
    assert kerb > 0.15 and road < 0.06, (kerb, road)


def test_the_finish_is_the_same_van_every_time():
    lay = V.layout(2.6, 6.8, 3.05)
    pts = [((x, y, z), n) for x in (-1.15, 1.15) for y in (-3.0, -1.0, 0.5, 2.5)
           for z in (0.3, 0.7, 1.2, 2.4, 2.99)
           for n in ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0))]
    a = [V.finish_rgb(p, n, lay) for p, n in pts]
    b = [V.finish_rgb(p, n, lay) for p, n in pts]
    assert a == b
    assert all(0.0 <= V.vnoise(x * 0.37, x * 0.91, s) <= 1.0 for x in range(-40, 40) for s in range(5))


def test_the_genome_colour_is_the_paint():
    """BASE is the genome's style colour and the recipe passes the plan's in,
    so editing the genome repaints the van; the chalk derives from it."""
    styles = _g()["styles"]
    style = styles["default"]
    assert tuple(style["color"]) == pytest.approx(V.BASE, abs=1e-9)
    assert style["material"] == _g()["materials"]["default"] == "paint_matte"
    # the crew's van is the same van in every theme: `delco` is there so
    # `delco_1997` resolves (test_theme_style_resolution.py), not to differ
    assert all(s == style for s in styles.values()), sorted(styles)
    assert V.chalk(V.BASE) == pytest.approx((0.100, 0.096, 0.092), abs=1e-9)
    lay = V.layout(2.6, 6.8, 3.05)
    red = V.finish_rgb((lay["hw"], 1.0, 1.6), (1.0, 0.0, 0.0), lay, (0.5, 0.05, 0.05))
    assert red[0] > 2.0 * red[1] and red[0] > 2.0 * red[2], red


def _dict_value(path, name, key):
    tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
            raise AssertionError("%s has no %r" % (name, key))
    raise AssertionError("no module-level %s in %s" % (name, path))


def test_paint_matte_is_a_known_matte_dielectric():
    """Read off materials.py with `ast`: it imports bpy at module scope."""
    assert "paint_matte" in skins.KNOWN_KINDS
    assert _dict_value(_MATERIALS, "ROUGHNESS", "paint_matte") >= 0.8
    assert _dict_value(_MATERIALS, "METALLIC", "paint_matte") == 0.0


def test_the_recipe_paints_one_material_in_the_plans_kind_and_colour():
    """The draw-call rule: the van's colour varies per corner in `Wear`,
    never as a material per colour, and the genome's kind and colour are
    what the body is drawn in (a recipe that hard-codes them makes the
    genome inert)."""
    src = open(_RECIPE, encoding="utf-8").read()
    assert 'plan["material"]' in src and 'plan["color"]' in src
    assert "geometry.tint_wear_by(" in src and "van_forms.finish_rgb(" in src
    made = re.findall(r'make_material\(\s*(f?)"([^"]+)"', src)
    assert sorted(n for _f, n in made) == ["M_Van_interior", "M_Van_paint",
                                          "M_Van_painted", "M_Van_rubber"], made
    assert not any(f for f, _n in made), "a material name built from a value"
    assert re.search(r'make_see_through_material\(\s*"M_Van_glass"', src)


def test_the_measured_builds_are_clean_and_inside_the_budget():
    budget = _g()["budgets"]["tris_lod0"]
    r = _g()["dimensions"]
    for (w, d, h), (tris, pairs) in MEASURED.items():
        assert r["width"]["min"] <= w <= r["width"]["max"]
        assert r["depth"]["min"] <= d <= r["depth"]["max"]
        assert r["height"]["min"] <= h <= r["height"]["max"]
        assert pairs == 0 and tris <= budget, ((w, d, h), tris, pairs)


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, dims):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "getaway_van", "role": "prop", "size_mod": "full", "style": 1,
            "species": "step_van", "fit": {"dims": list(dims), "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == [], plan["dressing_fallbacks"]
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES)), key=lambda o: o.name)
    return res, objs


def _glb_json(path):
    import json
    import struct
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    return json.loads(raw[20:20 + n])


@pytest.mark.parametrize("dims", [CORNERS[0], (2.6, 6.8, 3.05), CORNERS[-1]])
def test_bpy_the_van_passes_and_fills_its_slot(tmp_path, dims):
    """Fit to the millimetre: before `axle_height` the default build stood
    3.040 m in its 3.05 m slot and this failed."""
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    parts = set(_g()["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name


def test_bpy_five_submissions_and_one_paint(tmp_path):
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, (2.6, 6.8, 3.05))
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    mats = {m["name"]: m for m in doc["materials"]}
    assert sorted(mats) == ["M_Van_glass", "M_Van_interior", "M_Van_paint",
                            "M_Van_painted", "M_Van_rubber"], sorted(mats)
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 5, [m["name"] for m in visual]
    assert mats["M_Van_glass"].get("alphaMode") == "BLEND"
    pbr = mats["M_Van_paint"]["pbrMetallicRoughness"]
    assert pbr["roughnessFactor"] == pytest.approx(0.86) and pbr.get("metallicFactor", 1.0) == 0


def test_bpy_the_paint_is_in_the_vertex(tmp_path):
    """The roof's corners chalked lighter than the side's, as built."""
    pytest.importorskip("bpy")
    _res, objs = _build(tmp_path, (2.6, 6.8, 3.05))
    body = [o for o in objs if o.name == "StepVan_Body"]
    assert len(body) == 1, [o.name for o in objs]
    mesh = body[0].data
    wear = mesh.color_attributes["Wear"].data
    up, side = [], []
    for poly in mesh.polygons:
        lums = [_lum(wear[li].color) for li in poly.loop_indices]
        if poly.normal[2] > 0.9:
            up.extend(lums)
        elif abs(poly.normal[0]) > 0.9:
            side.extend(lums)
    assert up and side
    assert statistics.mean(up) > statistics.median(side), (statistics.mean(up), statistics.median(side))


def test_bpy_the_same_file_every_build(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, (2.6, 6.8, 3.05))
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]
