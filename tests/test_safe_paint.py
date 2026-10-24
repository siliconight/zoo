"""A drop safe is painted steel (1.125.0). The walker, walking cold run 9386: "drop safe looks like a brown box" --
`metal` was its only kind, and a theme's `metal` is its street metal. Each test FAILS ON 1.124.0 but the
last, which passes there too (a slot naming a known kind builds it) and guards Deli Counter 0.267.0's safe
row, which asks for `metal_painted`."""
import os

import pytest

from zoo_keeper.core import dna, genome, kit

RECIPE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zoo_keeper", "recipes",
                      "drop_safe.py")


def test_the_genome_paints_a_safe_and_offers_no_raw_metal():
    m = genome.load_species("drop_safe")["materials"]
    assert m == {"default": "metal_painted", "options": ["metal_painted"]}, m


def test_the_dial_and_handle_are_bare_steel_not_the_street_metal():
    src = open(RECIPE, encoding="utf-8").read()
    assert '"metal")' not in src
    assert '"metal_bare")' in src


def _resolved(**extra):
    """The plan a kit module's build executes: `kit.plan_kit`, then `dna.resolve_module_plan`, where a module's
    material is decided -- the style's, unless the slot names a known kind, which wins whatever the genome offers."""
    slot = {"slot_id": "s", "role": "prop", "size_mod": "full", "style": 1, "species": "drop_safe",
            "fit": {"dims": [0.9, 0.9, 1.0], "pivot": "center"}}
    slot.update(extra)
    module = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)["modules"][0]
    return dna.resolve_module_plan(module, genome.load_species("drop_safe"), "delco_1997", 1, "test")


def test_a_safe_that_names_no_material_is_painted_steel():
    """Every style named `metal` for itself, so a slot asking nothing took the street metal."""
    assert _resolved()["material"] == "metal_painted"


def test_a_safe_asked_for_painted_steel_builds_painted_steel():
    assert _resolved(material="metal_painted")["material"] == "metal_painted"


def test_bpy_a_safe_naming_no_material_is_built_in_painted_steel(tmp_path):
    """Built in Blender: the body and door in the painted kind, the dial and handle the trim. Run inside Blender for
    this change: `blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.');
    pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_safe_paint.py'])"`."""
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    slot = {"slot_id": "s", "role": "prop", "size_mod": "full", "style": 1, "species": "drop_safe",
            "fit": {"dims": [0.9, 0.9, 1.0], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    B.build_module(plan["modules"][0], str(tmp_path / "out"), theme="delco_1997", style=1,
                   options={"save_blend": False})
    mats = {o.name: o.data.materials[0].name for o in bpy.data.objects if o.type == "MESH" and o.data.materials}
    assert mats.get("DropSafe_Body") == "M_DropSafe_metal_painted", mats
    assert mats.get("DropSafe_Door") == "M_DropSafe_metal_painted", mats
    assert mats.get("DropSafe_Handle") == "M_DropSafe_trim", mats


# NOT TESTED, and why: a slot naming `metal` still builds `metal`. A module's slot override wins with any known kind
# (`dna.resolve_module_plan`), whatever the genome's options say -- so the library's stored safes, which name `metal`,
# are Deli Counter 0.267.0's migration to repaint, not this genome's. This file's first draft asserted the opposite,
# from `resolve_plan`'s fallback, which a kit module does not take.
