"""cash_cart: minted 2026-10-27 by tools/new_species.py (roadmap 150), shaped for the walker's bank comps (the
factory's docs/reference/BANK_INTERIOR_COMPS.md: the money room's "canvas hampers on wheels, a steel cage cart", the
depot's "carts and tubs"). The pure half plans it; the bpy half builds it. FAILS ON 1.134.0, which has no cash cart.
Run inside Blender for the shape:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_cash_cart.py'])))"
"""
import pytest

from zoo_keeper.core import genome, kit


def test_cash_cart_is_discovered_and_validates():
    assert "cash_cart" in genome.list_species()
    assert genome.validate_genome(genome.load_species("cash_cart")) == []


def _plan(dims=(1.2, 0.7, 1.1), variant=0):
    slot = {"slot_id": "cash_cart_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": "cash_cart", "fit": {"dims": list(dims), "pivot": "center"}}
    if variant:
        slot["variant"] = variant
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco", style=1)


def test_cash_cart_plans_at_its_authored_dims_and_takes_a_variant():
    plan = _plan()
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "cash_cart"
    assert genome.load_species("cash_cart")["module_variants"] == 4      # the load
    assert _plan(variant=2)["modules"][0]["stem"] != plan["modules"][0]["stem"]


def _build(tmp_path, dims, variant=0):
    import bpy
    from mathutils import Vector
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    m = _plan(dims, variant)["modules"][0]
    B.build_module(m, str(tmp_path / m["stem"]), theme="delco", style=1, options={"save_blend": False})
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("-colonly")]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    return meshes, pts


@pytest.mark.parametrize("dims", [(0.8, 0.5, 0.9), (1.2, 0.7, 1.1), (1.6, 0.9, 1.4)])
def test_bpy_a_cart_is_its_slot_on_two_materials(tmp_path, dims):
    pytest.importorskip("bpy")
    meshes, pts = _build(tmp_path, dims)
    for axis, size in enumerate(dims):
        lo, hi = min(p[axis] for p in pts), max(p[axis] for p in pts)
        assert hi - lo == pytest.approx(size, abs=0.02), (axis, lo, hi)
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 2
    assert any(o.name.startswith("CashCart_Load") for o in meshes)


def test_bpy_a_stacked_bag_stands_inside_the_one_under_it(tmp_path):
    """Drawn independently, two stacked bags' sides landed 1-2 mm apart (the census's first reading, 2.4 m)."""
    pytest.importorskip("bpy")
    from zoo_keeper.recipes import cash_cart as C
    for v in range(4):
        _parts, load = C.layout(1.6, 0.9, 1.4, v)
        for (c1, s1, _r1), (c2, s2, _r2) in zip(load, load[1:]):
            if abs((c2[2] - s2[2] / 2.0) - (c1[2] + s1[2] / 2.0)) < 0.02:      # c2 stands on c1
                for k in (0, 1):
                    assert c2[k] - s2[k] / 2.0 >= c1[k] - s1[k] / 2.0 + C.STACK_IN - 1e-9, (v, k)
                    assert c2[k] + s2[k] / 2.0 <= c1[k] + s1[k] / 2.0 - C.STACK_IN + 1e-9, (v, k)
