"""A floor hole that says why it is there (Zoo 1.114.0; the factory's roadmap 265).

The walker, 2026-10-19: a hole should be "clear to the player" and have "some reason other than a
perfectly cut square". Pure: `core.hole_forms`' plans, the three species' genomes, the slot fields
Deli Counter writes reaching each plan, and `roof_hatch`'s floor form. The Blender builds are
checked by the coincident-face census and the kit build; these are the contracts the builds read.

FAIL ON 1.113.1: there is no `core.hole_forms`, no `hole_edge`, `hole_spoil` or `hole_kit`, and
`roof_hatch` has no forms and refuses a 3 cm frame as out of range.
"""
import math

import pytest

from zoo_keeper.core import genome, kit
from zoo_keeper.core import hole_forms as HF

SIZES = ((2.8, 2.8), (2.6, 2.6), (2.1, 2.1), (2.8, 2.2))
SLAB = 0.30
FORMS = HF.FORMS


def _edge_h(thick=SLAB):
    return HF.TOP + 2 * HF.SKIN + thick + HF.HANG


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("variant", range(HF.VARIANTS))
@pytest.mark.parametrize("w,d", SIZES)
def test_the_edge_reaches_its_slots_faces_and_no_further(w, d, variant, form):
    p = HF.edge_plan(w, d, _edge_h(), form, variant)
    xs = [r[0] for r in p["ring"]] + [r[2] for r in p["ring"]]
    ys = [r[1] for r in p["ring"]] + [r[3] for r in p["ring"]]
    assert min(xs) == pytest.approx(-w / 2) and max(xs) == pytest.approx(w / 2)
    assert min(ys) == pytest.approx(-d / 2) and max(ys) == pytest.approx(d / 2)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("variant", range(HF.VARIANTS))
@pytest.mark.parametrize("w,d", SIZES)
def test_no_tooth_closes_the_opening_and_every_end_is_past_the_cut(w, d, variant, form):
    """A body falls through the rectangle Deli Counter cut: CLEAR metres of it stay clear each way,
    and the collar's inner end is never ON the cut's plane (6 mm past it at least)."""
    p = HF.edge_plan(w, d, _edge_h(), form, variant)
    hx, hy = p["frame"]["hx"], p["frame"]["hy"]
    pts = HF.perimeter(hx, hy)
    assert len(pts) == len(p["ring"])
    for (x, y, nx, ny, _side), (_ox, _oy, ix, iy, _droop) in zip(pts, p["ring"]):
        # how far the end stands past the cut, along the sample's own outward normal
        past = -((ix - x) * nx + (iy - y) * ny)
        assert past >= 0.006 - 1e-9, (x, y, ix, iy)
        assert abs(ix) < hx and abs(iy) < hy
        assert not (abs(ix) < HF.CLEAR / 2 and abs(iy) < HF.CLEAR / 2)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("variant", range(HF.VARIANTS))
@pytest.mark.parametrize("w,d", SIZES)
def test_the_hangers_reach_the_slots_bottom_and_no_further(w, d, variant, form):
    p = HF.edge_plan(w, d, _edge_h(), form, variant)
    drops = [HF.hanger_drop(h[5], h[6], h[7]) for h in p["hangers"]]
    assert drops and max(drops) == pytest.approx(HF.HANG, abs=1e-4)
    assert all(dr <= HF.HANG + 1e-4 for dr in drops)
    kinds = {h[8] for h in p["hangers"]}
    assert kinds <= ({"plaster", "lath"} if form.endswith("_plaster") else {"tile", "grid"})


@pytest.mark.parametrize("form", FORMS)
def test_the_cuts_walls_stand_proud_of_the_cut_and_inside_the_slab(form):
    w = d = 2.8
    p = HF.edge_plan(w, d, _edge_h(), form, 1)
    f = p["frame"]
    for kind, cx, cy, cz, sx, sy, sz in p["walls"]:
        assert f["slab_bot"] - 1e-9 <= cz - sz / 2 and cz + sz / 2 <= f["slab_top"] + 1e-9
        if kind == "void":
            face = cy + (sy / 2 if cy < 0 else -sy / 2)
            assert abs(abs(face) - f["hy"]) == pytest.approx(HF.PROUD, abs=1e-6)
        else:
            face = cx + (sx / 2 if cx < 0 else -sx / 2)
            assert abs(abs(face) - f["hx"]) == pytest.approx(HF.PROUD, abs=1e-6)
    for cx, cy, cz, sx, sy, sz, pitch, _axis in p["joists"]:
        assert f["slab_bot"] < cz < f["slab_top"]
        if form.startswith("cut"):
            assert pitch == 0.0
    if "_slab" in form:
        # a concrete slab has bars, not joists, and nothing lining its cut
        assert p["rebar"] and not p["joists"] and not p["walls"]
        for x0, y0, z0, x1, y1, z1 in p["rebar"]:
            assert f["slab_bot"] < z0 < f["slab_top"] and z1 <= z0 + 1e-9
            assert not (abs(x1) < HF.CLEAR / 2 and abs(y1) < HF.CLEAR / 2)
    else:
        assert p["joists"] and p["walls"] and not p["rebar"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("variant", range(HF.VARIANTS))
@pytest.mark.parametrize("w,d,h", [(2.7, 2.7, 0.10), (2.5, 1.6, 0.10), (1.4, 1.2, 0.08), (5.5, 3.5, 0.10)])
def test_the_spoil_lies_flat_inside_its_slot_none_on_another(w, d, h, variant, form):
    pieces = HF.spoil_plan(w, d, h, form, variant)
    polys = [HF._rect_corners(c[1], c[2], c[3], c[4], c[6]) for c in pieces]
    for poly in polys:
        assert all(abs(x) <= w / 2 + 1e-9 and abs(y) <= d / 2 + 1e-9 for x, y in poly)
    for i in range(len(polys)):
        for j in range(i):
            assert not HF._overlap(polys[i], polys[j], 0.0)
    assert max(c[5] for c in pieces) == pytest.approx(h)
    assert all(c[5] <= h + 1e-9 for c in pieces)
    kinds = {c[0] for c in pieces}
    assert kinds <= {k for k, *_r in HF.spoil_rows(form)}
    main = "slab" if "_slab" in form else ("panel" if form.startswith("cut") else "plank")
    assert main in kinds


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("variant", range(HF.VARIANTS))
@pytest.mark.parametrize("w,d", [(2.7, 2.7), (2.29, 1.83)])
def test_a_spoil_carries_every_kind_its_form_names(w, d, variant, form):
    # one of each kind is placed before the rest, so a slot the size of the walk-ups' still shows
    # the ceiling the drop came through as well as the floor that came down
    kinds = {c[0] for c in HF.spoil_plan(w, d, 0.10, form, variant)}
    assert kinds == {k for k, *_r in HF.spoil_rows(form)}


def test_a_form_names_its_cause_construction_and_ceiling_and_nothing_else():
    assert HF.parse_form("auto") == ("cut", False, False)
    assert HF.parse_form("cut_slab") == ("cut", True, False)
    assert HF.parse_form("broken_slab_plaster") == ("broken", True, True)
    assert len(HF.FORMS) == 8
    with pytest.raises(ValueError):
        HF.parse_form("burnt")


def test_plans_are_the_same_every_time_and_differ_by_variant():
    assert HF.spoil_plan(2.7, 2.7, 0.1, "cut", 2) == HF.spoil_plan(2.7, 2.7, 0.1, "cut", 2)
    assert HF.spoil_plan(2.7, 2.7, 0.1, "cut", 2) != HF.spoil_plan(2.7, 2.7, 0.1, "cut", 3)
    assert HF.edge_plan(2.8, 2.8, _edge_h(), "cut", 1) == HF.edge_plan(2.8, 2.8, _edge_h(), "auto", 1)


@pytest.mark.parametrize("variant", range(HF.VARIANTS))
def test_the_kit_is_its_slot_the_tarp_its_width_and_depth_the_lamp_its_height(variant):
    w, d, h = 1.4, 0.7, 0.7
    k = HF.kit_plan(w, d, h, "cut", variant)
    assert (k["tarp"]["w"], k["tarp"]["d"]) == (w, d)
    assert k["light"]["top"] == h
    L = k["light"]
    assert abs(L["cx"]) + L["foot"] <= w / 2 + 1e-9 and abs(L["cy"]) + L["foot"] <= d / 2 + 1e-9
    for item in (k["saw"], k["bag"], k["coil"], k["bar"]):
        assert abs(item["cx"]) < w / 2 and abs(item["cy"]) < d / 2


@pytest.mark.parametrize("species", ["hole_edge", "hole_spoil", "hole_kit"])
def test_the_species_are_discovered_and_validate(species):
    assert species in genome.list_species()
    g = genome.load_species(species)
    assert genome.validate_genome(g) == []
    assert g["license"]["construction_knowledge"] == "CC0"
    assert int(g["module_variants"]) == HF.VARIANTS


def _plan(species, dims, **fields):
    slot = {"slot_id": species + "_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": species, "fit": {"dims": dims, "pivot": "center"}}
    slot.update(fields)
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


@pytest.mark.parametrize("species,dims,fields,stem_has", [
    ("hole_edge", [2.8, 2.8, 0.652], {"form": "cut", "variant": 1}, "_fcut_n1"),
    ("hole_edge", [2.6, 2.6, 0.652], {"form": "broken", "variant": 3}, "_fbroken_n3"),
    ("hole_spoil", [2.7, 2.7, 0.1], {"form": "cut", "stock": "carpet", "variant": 2}, "_fcut_scarpet_n2"),
    ("hole_edge", [2.8, 2.8, 0.652], {"form": "cut_slab", "variant": 2}, "_fcut_slab_n2"),
    ("hole_spoil", [2.7, 2.7, 0.1], {"form": "broken_slab_plaster", "variant": 1}, "_fbroken_slab_plaster_n1"),
    ("hole_kit", [1.4, 0.7, 0.7], {"form": "cut", "variant": 1}, "_fcut_n1"),
])
def test_deli_counters_slot_fields_reach_the_plan(species, dims, fields, stem_has):
    plan = _plan(species, dims, **fields)
    assert plan["species_fallbacks"] == [] and plan.get("dressing_fallbacks", []) == []
    m = plan["modules"][0]
    assert m["species"] == species and stem_has in m["stem"]


def test_the_roof_hatch_has_a_floor_form_with_a_three_centimetre_frame():
    g = genome.load_species("roof_hatch")
    assert g["params"]["form"] == ["auto", "roof", "floor"]
    assert g["dimensions"]["height"]["min"] == 0.03
    plan = _plan("roof_hatch", [1.66, 1.66, 0.03], form="floor")
    assert plan["species_fallbacks"] == [] and plan.get("dressing_fallbacks", []) == []
    assert plan["modules"][0]["species"] == "roof_hatch" and "_ffloor" in plan["modules"][0]["stem"]


def test_the_floor_form_paints_on_a_tintable_kind_never_the_slots_material():
    """Cold run 9343 (the factory's roadmap 265): the floor hatch's safety-yellow frame shipped dark brown. The
    yellow rides in the frame's vertex colours (`geometry.tint_wear`) and multiplies into the pack's albedo, and the
    slot's `metal` resolves to the theme's rusted street steel -- Pixelcoat declares that pack not tintable, mean sRGB
    (0.45, 0.32, 0.21) -- so yellow times rust read brown. The floor form paints on `metal_painted`, which Pixelcoat
    declares tintable (a near-white grain, mean 0.93), whatever material the slot carries. Read off the recipe's
    source, because a recipe imports Blender's layer."""
    import ast
    import os

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "zoo_keeper", "recipes", "roof_hatch.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    consts = {t.id: n.value.value for n in tree.body if isinstance(n, ast.Assign)
              for t in n.targets if isinstance(t, ast.Name) and isinstance(n.value, ast.Constant)}
    assert consts.get("FLOOR_PAINT") == "metal_painted", consts.get("FLOOR_PAINT")
    build = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "build")
    branch = next(n for n in ast.walk(build) if isinstance(n, ast.If)
                  and isinstance(n.test, ast.Name) and n.test.id == "floor")
    calls = [c for stmt in branch.body for c in ast.walk(stmt)
             if isinstance(c, ast.Call) and getattr(c.func, "attr", "") == "make_material"]
    assert len(calls) == 1, [ast.dump(c) for c in calls]
    kind = calls[0].args[2]
    assert isinstance(kind, ast.Name) and kind.id == "FLOOR_PAINT", ast.dump(kind)
    # the colour is the mesh's: the paint itself stays white
    assert [ast.literal_eval(v) for v in calls[0].args[1].elts] == [1.0, 1.0, 1.0]


def test_a_roof_hatch_slot_without_a_form_plans_as_it_always_did():
    """The 40 roof scuttles Deli Counter emits name no form: their stems must not move."""
    plan = _plan("roof_hatch", [1.66, 1.66, 0.2])
    stem = plan["modules"][0]["stem"]
    assert "_f" not in stem.split("roof_hatch")[1]
