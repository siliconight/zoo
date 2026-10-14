"""shop_awning (1.108.0): a corner shop's canvas awning over its storefront.

Factory roadmap 241, the corner shop. The comps: "Corners carry the life. The corner building has the shop at grade
(lit, awning), homes above." `core.shop_awning_forms` is the plan, drawn from a slot's box alone -- a shed of
canvas from the wall down to a valance, closed at each end -- in a form per canvas colour; the recipe builds the
same lists through `bpylayer.prim_mesh`. Pure but the last check, which builds it in Blender and is skipped where
bpy is absent. On 1.107.0 there is no `core.shop_awning_forms`, so the module fails to import.
"""
import math

import pytest

from zoo_keeper.core import genome, kit, prims
from zoo_keeper.core import shop_awning_forms as F

#: Deli Counter 0.219.0's corner blocks stand their awning 0.6 m narrower than the facade, 1.2 m out and 0.85 m
#: tall: 14.4 to 17.4 m wide
CORNER = (14.4, 1.2, 0.85)
SIZES = [(w, d, h) for w in (2.0, 6.0, 11.4, 14.4, 17.4, 25.0) for d in (0.6, 1.2, 2.0) for h in (0.4, 0.85, 1.5)]


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


def test_shop_awning_is_discovered_and_validates():
    assert "shop_awning" in genome.list_species()
    g = genome.load_species("shop_awning")
    assert genome.validate_genome(g) == []
    assert g["collision"] is False
    assert g["params"]["form"] == list(F.FORMS)


def test_four_canvas_colours_and_one_shape():
    assert F.SHAPES == ("shed",)
    assert len(F.COLOURS) == 4 and len(set(F.COLOURS.values())) == 4
    assert F.FORMS == ("shed_red", "shed_green", "shed_navy", "shed_black")


@pytest.mark.parametrize("form", F.FORMS)
def test_each_form_plans_at_the_size_deli_counter_writes(form):
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "shop_awning", "role": "prop", "size_mod": "full", "style": 1,
        "species": "shop_awning", "form": form, "material": "canvas",
        "fit": {"dims": list(CORNER), "pivot": "center", "collision": "none"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    (m,) = plan["modules"]
    assert m["species"] == "shop_awning" and m.get("form") == form, m
    assert "_f" + form in m["stem"], m["stem"]


def test_two_colours_are_two_modules():
    def slot(form):
        return {"slot_id": "a_" + form, "role": "prop", "size_mod": "full", "style": 1,
                "species": "shop_awning", "form": form, "material": "canvas",
                "fit": {"dims": list(CORNER), "pivot": "center", "collision": "none"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot("shed_red"), slot("shed_green")]},
                        theme="delco", style=1)
    assert len(plan["modules"]) == 2 and plan["stem_collisions"] == []


@pytest.mark.parametrize("form", F.FORMS)
@pytest.mark.parametrize("w,d,h", SIZES)
def test_the_extents_are_exactly_the_slots(form, w, d, h):
    got = F.plan(w, d, h, form)
    lo, hi = prims.bounds(got["prims"])
    for a, (want_lo, want_hi) in enumerate(((-w / 2, w / 2), (-d / 2, d / 2), (-h / 2, h / 2))):
        assert math.isclose(lo[a], want_lo, abs_tol=1e-9) and math.isclose(hi[a], want_hi, abs_tol=1e-9)


@pytest.mark.parametrize("w,d,h", SIZES)
def test_no_face_lies_on_another(w, d, h):
    assert prims.coincident_pairs(F.plan(w, d, h, "shed_red")["prims"]) == []


def test_the_coincidence_check_can_see_a_pair():
    """The control: a cheek laid with its outer face on the valance's end face is a pair the probe reports."""
    a = prims.box(F.PART, F.MAT, (0.0, 0.0, 0.0), (1.0, 0.02, 0.25))
    b = prims.box(F.PART, F.MAT, (1.0, 0.0, 0.0), (1.02, 1.0, 0.25))
    assert prims.coincident_pairs([a, b])


@pytest.mark.parametrize("w,d,h", SIZES)
def test_every_part_is_closed_and_faces_out(w, d, h):
    """Each part encloses a positive volume: its faces wind outward, so none is culled from the street."""
    for p in F.plan(w, d, h, "shed_navy")["prims"]:
        assert _volume(p) > 0.0, p["part"]


def test_the_shed_falls_from_the_wall_to_a_ten_inch_valance():
    w, d, h = CORNER
    got = F.plan(w, d, h, "shed_red")
    assert math.isclose(got["facts"]["valance_m"], F.VALANCE, abs_tol=1e-9)
    # the slope falls (h - valance) over the projection: 0.596 over 1.2 m
    want = math.degrees(math.atan2(h - F.VALANCE, d))
    assert math.isclose(got["facts"]["pitch_deg"], round(want, 3), abs_tol=1e-3)
    assert 20.0 < got["facts"]["pitch_deg"] < 35.0


@pytest.mark.parametrize("form", F.FORMS)
def test_one_material_one_part_inside_the_budget(form):
    got = F.plan(*CORNER, form)
    assert {p["mat"] for p in got["prims"]} == {F.MAT}
    assert {p["part"] for p in got["prims"]} == {F.PART}
    assert got["rgb"] == F.COLOURS[got["colour"]]
    assert got["facts"]["tris"] <= genome.load_species("shop_awning")["budgets"]["tris_lod0"]


def test_an_unknown_form_is_refused_and_auto_is_red():
    assert F.form_of(None) == F.form_of("auto") == ("shed", "red")
    with pytest.raises(ValueError):
        F.plan(*CORNER, "barrel_red")
    with pytest.raises(ValueError):
        F.plan(*CORNER, "shed_purple")


def test_bpy_an_awning_wears_its_colour(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "shop_awning", "role": "prop", "size_mod": "full", "style": 1,
        "species": "shop_awning", "form": "shed_green", "material": "canvas",
        "fit": {"dims": list(CORNER), "pivot": "center", "collision": "none"}}]},
        theme="delco_1997", style=1)
    B.build_module(plan["modules"][0], str(tmp_path / "out"), theme="delco_1997", style=1,
                   options={"save_blend": False})
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("ShopAwning")]
    assert meshes and {s.material.name for o in meshes for s in o.material_slots} == {"M_ShopAwning_canvas_green"}
