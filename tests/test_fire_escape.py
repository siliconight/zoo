"""fire_escape (1.110.0): one storey of a steel fire escape on a walk-up's front.

Factory roadmaps 156 and 241. The walker's photo of a brick walk-up: "this is something i'd like to see in our
toolset, fireescape stairs brick". `core.fire_escape_forms` is the plan, drawn from a slot's box alone -- a landing
with its guards and a flight that switches back, the top landing, or the drop ladder -- and the recipe builds the
same lists through `bpylayer.prim_mesh`. Pure but the last check, which builds it in Blender and is skipped where
bpy is absent. On 1.109.0 there is no `core.fire_escape_forms`, so the module fails to import.

The no-coincident-faces sweep here is 132 sizes; the forms were written against 1,968 (flights 12 widths x 5 depths
x 15 storeys, top landings 60, drops 48), each with `prims.coincident_pairs` empty and the extents exact.
"""
import math

import pytest

from zoo_keeper.core import genome, kit, prims
from zoo_keeper.core import fire_escape_forms as F

#: a bay as Deli Counter stands it on a walk-up: 2.8 m on a 3.2 m bay, 1.2 m out, a 3.1 m storey
BAY = (2.8, 1.2, 3.1)
TOP = (2.8, 1.2, round(F.FRAME + F.GUARD_H + F.POST_PROUD, 4))
DROP = (0.45, 0.05, 0.9)
FLIGHT_SIZES = [(w, d, h) for w in (1.8, 2.8, 4.0) for d in (0.9, 1.2, 1.6) for h in (2.6, 3.1, 3.6, 4.5)]
TOP_SIZES = [(w, d, h) for w in (1.8, 2.8, 4.0) for d in (0.9, 1.2, 1.6) for h in (TOP[2], 1.3)]
DROP_SIZES = [(w, d, h) for w in (0.4, 0.6) for d in (0.03, 0.08) for h in (0.5, 1.5, 2.5)]
SIZES = {"flight_a": FLIGHT_SIZES, "flight_b": FLIGHT_SIZES, "top_a": TOP_SIZES, "top_b": TOP_SIZES,
         "drop": DROP_SIZES}
CASES = [(f, s) for f in F.FORMS for s in SIZES[f]]


def _volume(p):
    """The signed volume a primitive's faces enclose: positive when every face winds outward."""
    v, vol = p["verts"], 0.0
    for f in p["faces"]:
        a = v[f[0]]
        for i in range(1, len(f) - 1):
            b, c = v[f[i]], v[f[i + 1]]
            vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return vol


def _slot(form, dims):
    return {"slot_id": "fire_escape_" + form, "role": "prop", "size_mod": "full", "style": 1,
            "species": "fire_escape", "form": form, "material": "metal_painted",
            "fit": {"dims": list(dims), "pivot": "center", "collision": "none"}}


def test_fire_escape_is_discovered_and_validates():
    assert "fire_escape" in genome.list_species()
    g = genome.load_species("fire_escape")
    assert genome.validate_genome(g) == []
    assert g["collision"] is False
    # `auto` first: a list's first option is a plan's default, and the census names no form
    assert g["params"]["form"] == ["auto"] + list(F.FORMS)


def test_five_forms():
    assert F.FORMS == ("flight_a", "flight_b", "top_a", "top_b", "drop")


@pytest.mark.parametrize("form,dims", [("flight_a", BAY), ("flight_b", BAY), ("top_a", TOP), ("top_b", TOP),
                                       ("drop", DROP)])
def test_each_form_plans_at_the_size_deli_counter_writes(form, dims):
    plan = kit.plan_kit({"building_id": "t", "slots": [_slot(form, dims)]}, theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    (m,) = plan["modules"]
    assert m["species"] == "fire_escape" and m.get("form") == form, m
    assert "_f" + form in m["stem"], m["stem"]


def test_the_two_flights_are_two_modules():
    plan = kit.plan_kit({"building_id": "t", "slots": [_slot("flight_a", BAY), _slot("flight_b", BAY)]},
                        theme="delco", style=1)
    assert len(plan["modules"]) == 2 and plan["stem_collisions"] == []


@pytest.mark.parametrize("form,size", CASES)
def test_the_extents_are_exactly_the_slots(form, size):
    w, d, h = size
    lo, hi = prims.bounds(F.plan(w, d, h, form)["prims"])
    for a, (want_lo, want_hi) in enumerate(((-w / 2, w / 2), (-d / 2, d / 2), (-h / 2, h / 2))):
        assert math.isclose(lo[a], want_lo, abs_tol=1e-9) and math.isclose(hi[a], want_hi, abs_tol=1e-9)


@pytest.mark.parametrize("form,size", CASES)
def test_no_face_lies_on_another(form, size):
    assert prims.coincident_pairs(F.plan(*size, form)["prims"]) == []


def test_the_coincidence_check_can_see_a_pair():
    """The control: a tread laid with its end on a stringer's end face is a pair the probe reports -- the pair the
    first draft had, at some storeys, before its treads stopped a step short."""
    a = prims.box(F.PART, F.MAT, (0.0, 0.0, 0.0), (0.1016, 0.5, 0.0095))
    b = prims.box(F.PART, F.MAT, (0.1016, 0.0, -0.1), (0.12, 0.5, 0.1))
    assert prims.coincident_pairs([a, b])


@pytest.mark.parametrize("form,size", CASES)
def test_every_part_is_closed_and_faces_out(form, size):
    """Each part encloses a positive volume: its faces wind outward, the reflected forms' sheared bars too."""
    for p in F.plan(*size, form)["prims"]:
        assert _volume(p) > 0.0, p["part"]


def test_a_bay_is_a_steep_old_flight_inside_the_code_s_numbers():
    got = F.plan(*BAY, "flight_a")["facts"]
    assert got["riser_m"] <= F.RISER + 1e-9                 # 405.4: risers at most 8 in
    assert got["treads"] >= 2 and 45.0 < got["pitch_deg"] < 65.0
    assert math.isclose(got["tread_m"], F.TREAD_D, abs_tol=1e-9)
    assert math.isclose(got["guard_m"], F.GUARD_H, abs_tol=1e-9)
    assert math.isclose(F.FLIGHT_W, 22 * 0.0254, abs_tol=1e-4)


def test_the_top_landing_s_guard_is_its_box():
    got = F.plan(*TOP, "top_a")["facts"]
    assert math.isclose(got["guard_m"], F.GUARD_H, abs_tol=1e-6)


def _band_slats(prims_, d):
    yb0, yb1 = F._band(d)
    out = []
    for p in prims_:
        lo, hi = prims.bounds([p])
        if math.isclose(hi[2] - lo[2], F.SLAT_T, abs_tol=1e-6) and yb0 < (lo[1] + hi[1]) / 2 < yb1:
            out.append((lo[0], hi[0]))
    return out


def test_a_flight_comes_up_through_the_next_landing_s_hatch():
    """A stack alternates a, b: `a`'s flight tops out at +X, and `b`'s landing leaves the stair band open there --
    no slat of `b`'s band reaches past its hatch's inner edge but for the `SINK` it sits in the trimmer -- and the
    same reflected."""
    w, d, h = BAY
    a, b = F.plan(w, d, h, "flight_a")["prims"], F.plan(w, d, h, "flight_b")["prims"]
    top_a = max(prims.bounds([p])[1][0] for p in a if math.isclose(prims.bounds([p])[1][2], h / 2, abs_tol=1e-9))
    top_b = min(prims.bounds([p])[0][0] for p in b if math.isclose(prims.bounds([p])[1][2], h / 2, abs_tol=1e-9))
    assert top_a > w / 2 - F.HATCH and top_b < -(w / 2 - F.HATCH)
    assert _band_slats(b, d) and all(x1 <= w / 2 - F.HATCH + F.SINK + 1e-9 for _x0, x1 in _band_slats(b, d))
    assert _band_slats(a, d) and all(x0 >= -(w / 2 - F.HATCH) - F.SINK - 1e-9 for x0, _x1 in _band_slats(a, d))


@pytest.mark.parametrize("form,dims", [("flight_a", BAY), ("top_b", TOP), ("drop", DROP)])
def test_one_material_one_part(form, dims):
    got = F.plan(*dims, form)
    assert {p["mat"] for p in got["prims"]} == {F.MAT}
    assert {p["part"] for p in got["prims"]} == {F.PART}


def test_every_size_is_inside_the_budget():
    budget = genome.load_species("fire_escape")["budgets"]["tris_lod0"]
    assert max(F.plan(*s, f)["facts"]["tris"] for f, s in CASES) <= budget


def test_auto_is_the_form_the_box_can_be_and_an_unknown_form_is_refused():
    assert F.form_of(None, *BAY) == F.form_of("auto", *BAY) == "flight_a"
    assert F.form_of(None, *TOP) == "top_a" and F.form_of(None, *DROP) == "drop"
    g = genome.load_species("fire_escape")["dimensions"]
    for which in ("min", "default", "max"):
        F.plan(g["width"][which], g["depth"][which], g["height"][which])      # the census's three corners draw
    with pytest.raises(ValueError):
        F.plan(*BAY, "spiral")
    with pytest.raises(ValueError):
        F.plan(2.8, 0.6, 3.1, "flight_a")                    # no deck behind the stair band


def test_bpy_a_bay_builds_in_its_paint(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    plan = kit.plan_kit({"building_id": "t", "slots": [_slot("flight_b", BAY)]}, theme="delco_1997", style=1)
    B.build_module(plan["modules"][0], str(tmp_path / "out"), theme="delco_1997", style=1,
                   options={"save_blend": False})
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("FireEscape")]
    assert meshes and {s.material.name for o in meshes for s in o.material_slots} == {"M_FireEscape_metal_painted"}
