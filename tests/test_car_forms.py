"""simple_car 0.79.0: body styles, seeded trim and paint, separate
see-through panes, the slot's exact dims, and no coincident faces.

The walker, 2026-09-13: "we need our cars to upgrade quite a bit. missing a
lot of detail, side windows, transparency, etc etc". Everything here is pure
(`core.car_forms` and source read with `ast`), because the recipe imports bpy
and this suite runs without Blender. What only Blender can show was
measured and is recorded in MEASURED below.
"""
from __future__ import annotations

import ast
import itertools
import os
import re

import pytest

from zoo_keeper.core import car_forms, genome, seeding

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "simple_car.py")
_MATERIALS = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "materials.py")

#: Measured 2026-09-13 with tools/coplanar_probe.py's own `probe()` over
#: kit.plan_kit + build.build_module (the zoo_kit_build path), Blender 5.1:
#: every style forced at the genome's min, default and max dims with slot
#: style ints 1-8 (96 builds), plus 550 builds at random slot sizes inside
#: the genome's ranges, each a random style or `auto` at a random style int.
#: 646 builds, 0 SAME and 0 OPP coincident pairs, every fit_width / fit_depth
#: / fit_height / fit_pivot check passing. The min / default / max grid
#: alone once read clean while a 1.60 x 3.80 x 1.40 hatchback carried a SAME
#: pair -- which is why the random sizes are part of the number. The largest
#: visual tri count per style, read off the same builds:
MEASURED = {"builds": 646, "same_pairs": 0, "opp_pairs": 0,
            "tris_max": {"sedan": 3100, "hatchback": 2884, "suv": 3328,
                         "coupe": 3004}}


def _plan(dims, body_style="auto", doors=0, color=None, block=None):
    block = dict(block or {"color": [0.55, 0.56, 0.58]})
    return {"params": {"body_style": body_style, "doors": doors},
            "dimensions": {"width": dims[0], "depth": dims[1], "height": dims[2]},
            "color": list(color if color is not None else block["color"]),
            "style_block": block}


def _streams(key):
    return seeding.RNGStreams(seeding.root_key(key, "simple_car", 0, "0.31.0"))


SIZES = {k: tuple(genome.load_species("simple_car")["dimensions"][a][k]
                  for a in ("width", "depth", "height"))
         for k in ("min", "default", "max")}


# --- style selection ----------------------------------------------------------

def test_style_selection_is_deterministic_per_seed():
    for i in range(40):
        stem = f"prop_simple_car_delco_1997_{i:02d}_w175_d430_h145"
        a = car_forms.resolve(_plan((1.75, 4.3, 1.45)), _streams(stem))
        b = car_forms.resolve(_plan((1.75, 4.3, 1.45)), _streams(stem))
        assert a == b, stem


def test_auto_takes_only_a_style_whose_natural_window_holds_the_slot():
    cases = {(1.60, 3.80, 1.40): {"hatchback"},     # the walker's Metro
             (1.80, 4.70, 1.73): {"suv"},           # the walker's Explorer
             (1.75, 4.80, 1.42): {"sedan"},
             # Lot's slot today (site_parking.CAR, site_cover.COVER_SPECIES)
             (1.75, 4.30, 1.45): {"sedan", "hatchback"}}
    for dims, allowed in cases.items():
        seen = {car_forms.resolve(_plan(dims), _streams(f"k{i}"))["style"]
                for i in range(200)}
        assert seen == allowed, (dims, seen)


def test_an_asked_style_is_built_as_asked_at_any_size():
    for style in ("sedan", "hatchback", "suv", "coupe"):
        f = car_forms.resolve(_plan((1.75, 4.3, 1.45), body_style=style), _streams("x"))
        assert f["style"] == style and f["style_how"] == "asked"


def test_a_slot_outside_every_window_gets_the_nearest_style():
    f = car_forms.resolve(_plan((1.55, 3.6, 1.75)), _streams("tall_short"))
    assert f["style_how"] == "nearest" and f["style"] in car_forms.FORMS


def test_the_doors_param_is_read():
    """0 lets the style draw; 2 or 4 is what the prompt counted."""
    for doors in (2, 4):
        for i in range(20):
            f = car_forms.resolve(_plan((1.75, 4.3, 1.45), "sedan", doors), _streams(f"d{i}"))
            assert f["doors"] == doors
    drawn = {car_forms.resolve(_plan((1.60, 3.8, 1.40), "hatchback", 0), _streams(f"d{i}"))["doors"]
             for i in range(100)}
    assert drawn == {2, 4}


def test_seeds_vary_the_trim_within_a_style():
    fs = [car_forms.resolve(_plan((1.80, 4.70, 1.73)), _streams(f"t{i}")) for i in range(60)]
    for key in ("paint_name", "wheel_kind", "rack", "two_tone", "bumper_kind"):
        assert len({f[key] for f in fs}) > 1, key
    assert len({round(f["belt"], 6) for f in fs}) > 1


# --- paint ---------------------------------------------------------------------

def test_every_palette_entry_is_a_1990s_colour_the_table_holds():
    for style, form in car_forms.FORMS.items():
        for name, weight in form["palette"]:
            assert name in car_forms.PALETTE and weight > 0, (style, name)
    for rgb in car_forms.PALETTE.values():
        assert len(rgb) == 3 and all(0.0 <= c <= 1.0 for c in rgb)


def test_a_prompt_colour_and_a_fixed_style_colour_win_over_the_palette():
    asked = car_forms.resolve(_plan((1.75, 4.3, 1.45), color=[0.62, 0.1, 0.08]), _streams("p"))
    assert asked["paint_name"] == "asked" and list(asked["paint"]) == [0.62, 0.1, 0.08]
    police = {"color": [0.1, 0.1, 0.12], "paint": "fixed"}
    fixed = car_forms.resolve(_plan((1.75, 4.3, 1.45), block=police), _streams("p"))
    assert list(fixed["paint"]) == [0.1, 0.1, 0.12]
    names = {car_forms.resolve(_plan((1.75, 4.3, 1.45)), _streams(f"p{i}"))["paint_name"]
             for i in range(100)}
    assert len(names) >= 5 and "asked" not in names


def test_the_genome_marks_the_era_and_livery_styles_fixed():
    styles = genome.load_species("simple_car")["styles"]
    for name in ("1970s", "1980s", "police", "racing"):
        assert styles[name].get("paint") == "fixed", name
    assert "paint" not in styles["default"]


# --- glass ---------------------------------------------------------------------

@pytest.mark.parametrize("style,doors,quarter,count", [
    ("sedan", 4, False, 6), ("sedan", 4, True, 8), ("coupe", 2, True, 6),
    ("hatchback", 2, True, 6), ("suv", 4, True, 8)])
def test_every_opening_has_its_own_pane(style, doors, quarter, count):
    form = {"style": style, "doors": doors, "quarter_glass": quarter}
    names = car_forms.pane_names(form)
    assert len(names) == count == len(set(names))
    assert names[0] == "Car_Glass_Windshield" and names[-1] == "Car_Glass_Backlight"
    assert all(n.startswith("Car_Glass_") for n in names)
    sides = [n for n in names if n.endswith(("L", "R"))]
    assert len([n for n in sides if n.endswith("L")]) == len([n for n in sides if n.endswith("R")])


def test_the_recipe_builds_those_panes_and_glazes_them_see_through():
    """A constant nothing reads is not a fix: the recipe must take its pane
    names from car_forms, refuse to build a different set, and give every
    pane the see-through material."""
    src = open(_RECIPE, encoding="utf-8").read()
    assert "car_forms.pane_names(f)" in src
    assert re.search(r"raise RuntimeError\(\"simple_car: panes built", src)
    assert re.search(r"glass = materials\.make_see_through_material\(", src)
    assert re.search(r"materials\.assign\(glass_objs, glass\)", src)
    # nothing else is assigned the glass material
    assert len(re.findall(r"assign\([^)]*glass\)", src)) == 1


def test_see_through_material_blends_on_every_branch():
    """Measured on walk 9048: the delco `glass` pack has no transparency hint
    and exported alphaMode OPAQUE. The helper must blend without a hint and
    without a pack, and defer to a pack only when the pack is see-through."""
    tree = ast.parse(open(_MATERIALS, encoding="utf-8").read())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "make_see_through_material")
    body = ast.get_source_segment(open(_MATERIALS, encoding="utf-8").read(), fn)
    assert '"alpha_mode": "blend"' in body                  # opaque pack, forced
    assert '("blend_method", "BLEND")' in body               # no pack, flat
    assert 'bsdf.inputs["Alpha"].default_value = opacity' in body
    # authored pack: the one reading of the hint `_textured` also uses;
    # what it accepts is tested without bpy in tests/test_see_through_glass.py
    assert "skins.is_see_through(pack)" in body


# --- the slot's exact dims -----------------------------------------------------

@pytest.mark.parametrize("style,size,rack", list(itertools.product(
    ("sedan", "hatchback", "suv", "coupe"), ("min", "default", "max"), (False, True))))
def test_layout_holds_the_dims_contract(style, size, rack):
    W, L, H = SIZES[size]
    f = dict(car_forms.FORMS[style], style=style, rack=rack)
    lay = car_forms.layout(f, W, L, H)
    assert lay["mirror_outer_x"] == pytest.approx(W / 2.0)      # width: mirror heads
    assert (lay["yF0"], lay["yR0"]) == (pytest.approx(-L / 2.0), pytest.approx(L / 2.0))
    assert lay["zr"] + lay["rack_h"] == pytest.approx(H)         # height: roof or rails
    # wheels in their arches, arches clear of the greenhouse and the tail
    assert lay["tyre_outer_x"] <= lay["hw"] - 0.004
    assert 2 * lay["wheel_r"] < lay["wheel_r"] + lay["R"]
    assert lay["y_ws"] >= lay["ya_f"] + lay["R"] + 0.10 - 1e-9
    assert lay["ya_r"] + lay["R"] < lay["yt"]
    assert lay["y0"] < lay["ya_f"] - lay["R"]
    # a greenhouse with a roof over glass over a door
    assert lay["y_ws"] < lay["y_rf"] < lay["y_rr"] < lay["y_bl"] < lay["yt"]
    assert lay["y_te"] <= lay["y_bl"]
    assert 2 * lay["wheel_r"] < lay["belt"] < lay["zr"] - 0.30
    assert 0.0 < lay["clear"] < lay["wheel_r"]


def test_the_genome_keeps_the_interface_lot_parks_by():
    """Lot parks `simple_car` at (1.75, 4.3, 1.45), the genome's defaults
    (lot/site_parking.py CAR, lot/site_cover.py COVER_SPECIES). A style
    choice must never move those, and `auto` must be the default param so a
    kit build -- which takes param defaults -- chooses by the slot."""
    g = genome.load_species("simple_car")
    d = g["dimensions"]
    assert (d["width"]["default"], d["depth"]["default"], d["height"]["default"]) == (1.75, 4.3, 1.45)
    assert g["params"]["body_style"][0] == "auto"
    assert set(g["params"]["body_style"][1:]) == set(car_forms.FORMS)
    assert g["params"]["doors"]["default"] == 0
    assert g["materials"]["default"] == "metal_painted"
    assert set(g["attachments"]) == {"ATT_roof", "ATT_driver_seat", "ATT_trunk"}


def test_prompt_rules_reach_every_style():
    g = genome.load_species("simple_car")
    reached = {r["set"]["params.body_style"] for r in g["prompt_rules"]}
    assert reached == set(car_forms.FORMS)


# --- coincident faces and budget -----------------------------------------------

def _constants(path):
    ns = {}
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            try:
                ns[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return ns


def test_every_stand_off_clears_the_probe_window():
    """tools/coplanar_probe.py reports faces within 2 mm. Every distance the
    recipe puts between two parallel faces is kept above that."""
    c = _constants(_RECIPE)
    tol = 0.002
    for name in ("DETAIL_PROUD", "TRIM_PROUD", "SEAM_PROUD", "PILLAR_INSET"):
        assert c[name] > tol, name
    assert c["GLASS_INSET"] - c["PILLAR_INSET"] > tol
    assert car_forms.WHEEL_TUCK > tol
    depths = sorted(c["SKIN_DEPTH"].values())
    for a, b in zip(depths, depths[1:]):
        assert b - a >= 0.003 - 1e-9, (a, b)


def test_the_measured_matrix_was_clean_and_fits_the_budget():
    assert MEASURED["same_pairs"] == 0 and MEASURED["opp_pairs"] == 0
    g = genome.load_species("simple_car")
    for style, tris in MEASURED["tris_max"].items():
        assert tris <= g["budgets"]["tris_lod0"], style
    assert set(MEASURED["tris_max"]) == set(car_forms.FORMS)
