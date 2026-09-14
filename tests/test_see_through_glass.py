"""Glass is see-through when its pack says so, and every pane Zoo builds asks.

Measured on walk 9050 (delco_1997): `M_Skin_glass_delco_1997` exported
alphaMode OPAQUE on 12 GLBs -- 7 window modules, the teller line, the bus
shelter, the newspaper box, the parking meter and the car -- because the
theme's `glass` pack carried no `import_hints.transparency`. The owner of that
declaration is Pixelcoat (0.40.0 refuses a `glass` grammar without one). What
Zoo owns, and what these tests hold without Blender:

  * the hint survives `skins.load_pack`, and `skins.is_see_through` is the one
    reading of it both material paths act on;
  * every building pane -- window, broken-window remnant, teller line, bus
    shelter, skylight -- is made from a see-through kind unless the slot is a
    hollow facade, which glazes `glass_facade` and stays opaque;
  * a broken window has no pane across its opening.

The bpy half (a built module's pane material really blends) is at the bottom,
skipped without Blender, and was run inside Blender 5.1 for this change.
"""

import ast
import json
import os
import re

import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import arch, dna, genome, skins

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPES = os.path.join(_ZOO, "zoo_keeper", "recipes")
_MATERIALS = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "materials.py")


def _pack(root, dirname, asset_id, transparency=None):
    d = os.path.join(root, dirname)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{asset_id}_albedo.png"), "wb") as f:
        f.write(b"\x89PNG stub")
    manifest = {"schema": skins.PACK_SCHEMA, "asset_id": asset_id,
                "maps": {"albedo": f"{asset_id}_albedo.png"},
                "meters_per_tile": 2.0, "import_hints": {}}
    if transparency is not None:
        manifest["import_hints"]["transparency"] = transparency
    with open(os.path.join(d, f"{asset_id}.pack.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f)
    return d


# --- the declaration round-trips -------------------------------------------

def test_a_see_through_declaration_round_trips(tmp_path):
    """The manifest Pixelcoat 0.40.0 writes for delco_1997 `glass`."""
    hint = {"alpha_mode": "blend", "ior": 1.5, "opacity": 0.38}
    _pack(str(tmp_path), "glass_delco_1997", "glass_delco", hint)
    pack = skins.find_pack(str(tmp_path), "glass", "delco_1997")
    assert pack["transparency"] == hint
    assert skins.is_see_through(pack)


def test_the_shipped_opaque_pack_reads_opaque(tmp_path):
    """The manifest cold run 9050 actually shipped: no hint at all."""
    _pack(str(tmp_path), "glass_delco_1997", "glass_delco")
    pack = skins.find_pack(str(tmp_path), "glass", "delco_1997")
    assert pack["transparency"] is None
    assert not skins.is_see_through(pack)


@pytest.mark.parametrize("hint,want", [
    ({"alpha_mode": "blend", "opacity": 0.5}, True),
    ({"opacity": 0.34}, True),                      # pre-alpha_mode manifests
    ({"alpha_mode": "blend", "opacity": 1.0}, False),
    ({"alpha_mode": "scissor"}, False),             # road paint, foliage
    ({"alpha_mode": "scissor", "opacity": 0.5}, False),
    ({"opacity": "not a number"}, False),
    ({}, False),
    (None, False),
])
def test_is_see_through_reads_the_hint(hint, want):
    assert skins.is_see_through({"transparency": hint}) is want


def test_no_pack_and_a_legacy_bare_pack_are_not_see_through(tmp_path):
    assert not skins.is_see_through(None)
    d = tmp_path / "glass"
    d.mkdir()
    (d / "glass_albedo.png").write_bytes(b"\x89PNG stub")
    assert not skins.is_see_through(skins.load_pack(str(d)))


def test_see_through_kinds_are_the_kinds_dna_makes_opaque_for_structure():
    """`dna.OPAQUE_FOR` names the kinds a person sees through (so a slab of
    them is swapped out); this list names the same kinds for the consumer
    warning. Two spellings of one fact must agree."""
    assert set(skins.SEE_THROUGH_KINDS) == set(dna.OPAQUE_FOR)


def test_both_material_paths_read_the_hint_one_way():
    """`_textured` (every skinned pane) and `make_see_through_material` (the
    car) must decide blend-or-not from `skins.is_see_through`, not from two
    hand-written conditions that can drift apart."""
    src = open(_MATERIALS, encoding="utf-8").read()
    tree = ast.parse(src)
    fns = {n.name: ast.get_source_segment(src, n) for n in tree.body
           if isinstance(n, ast.FunctionDef)}
    assert "skins.is_see_through(pack)" in fns["_textured"]
    assert "skins.is_see_through(pack)" in fns["make_see_through_material"]
    # and the consumer says so when a see-through kind resolves opaque
    assert "SEE_THROUGH_KINDS" in fns["make_material"]
    assert "WARNING" in fns["make_material"]


# --- every building pane asks for a see-through kind ------------------------

def _src(name):
    with open(os.path.join(_RECIPES, name), encoding="utf-8") as f:
        return f.read()


@pytest.mark.parametrize("recipe", ["_arch.py", "window_broken.py"])
def test_window_panes_default_to_the_see_through_kind(recipe):
    src = _src(recipe)
    assert re.search(r'plan\.get\("glazing_kind", "glass"\)', src), recipe


@pytest.mark.parametrize("recipe,material", [
    ("teller_line.py", "M_TellerLine_glass"),
    ("bus_shelter.py", "M_BusShelter_glass"),
    ("skylight.py", "M_Skylight_glass"),
])
def test_building_glass_props_use_the_see_through_kind(recipe, material):
    kinds = []
    for node in ast.walk(ast.parse(_src(recipe))):
        if (isinstance(node, ast.Call) and getattr(node.func, "attr", None)
                == "make_material" and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == material):
            last = node.args[-1]
            kinds.append(last.value if isinstance(last, ast.Constant) else None)
    assert kinds, (recipe, material)
    assert all(k in skins.SEE_THROUGH_KINDS for k in kinds), (recipe, kinds)


def _window_module(glazing=None):
    module = {"type": "window", "species": "window", "width_cm": 200,
              "fit": "exact", "dims": [2.0, 0.3, 3.3], "pivot": "center",
              "stem": "window_delco_1997_01_w200", "style": 1,
              "material": "concrete", "openings": [], "voids": []}
    if glazing:
        module["glazing"] = glazing
    return module


def test_an_enterable_window_plans_see_through_glazing():
    plan = dna.resolve_module_plan(_window_module(), genome.load_species("window"),
                                   "delco_1997", 1, TOOL_VERSION)
    assert plan.get("glazing_kind", "glass") in skins.SEE_THROUGH_KINDS


def test_a_facade_shell_window_plans_opaque_glazing():
    """Hollow shell: nothing behind the glass, so it must not be see-through."""
    plan = dna.resolve_module_plan(_window_module("facade"),
                                   genome.load_species("window"),
                                   "delco_1997", 1, TOOL_VERSION)
    assert plan["glazing_kind"] == "glass_facade"
    assert plan["glazing_kind"] not in skins.SEE_THROUGH_KINDS


# --- a broken window has no pane --------------------------------------------

def test_broken_window_remnants_never_span_the_opening():
    """The remnants are a strip up from the sill and a strip down from the
    header, as fractions of the opening's height. Together they must leave a
    gap, or the 'broken' state is a pane with a seam in it."""
    g = genome.load_species("window_broken")
    rise = float(g["params"]["remnant_rise"])
    hang = float(g["params"]["remnant_hang"])
    assert 0.0 <= rise and 0.0 <= hang
    assert rise + hang < 0.5, (rise, hang)


def test_broken_window_builds_no_full_pane():
    """No `_Glass` object: the intact window's pane is named `<root>_Glass`;
    the broken state carries only `<root>_Remnant`."""
    src = _src("window_broken.py")
    assert '_Glass"' not in src and "_Glass'" not in src
    assert '_Remnant"' in src
    assert src.count("geometry.add_box(bm, (cx, 0.0, z0 + rise") == 1
    assert src.count("geometry.add_box(bm, (cx, 0.0, z1 - hang") == 1


def test_broken_window_keeps_the_intact_void():
    w = genome.load_species("window")
    params = {k: (v["default"] if isinstance(v, dict) else v)
              for k, v in w["params"].items()}
    assert arch.void_for("window", 2.0, 3.3, params) is not None


# --- bpy: the built pane really blends ---------------------------------------

def _build(tmp_path, species, glazing=None, hint=None):
    import bpy
    from zoo_keeper.bpylayer import build as B, materials
    # Skinned materials are cached by NAME for the whole Blender session, so a
    # pane built earlier against another pack would be handed back unchanged.
    for mat in list(bpy.data.materials):
        if mat.name.startswith("M_Skin_glass"):
            bpy.data.materials.remove(mat)
    skins_dir = tmp_path / "skins"
    _pack(str(skins_dir), "glass_delco_1997", "glass_delco",
          hint if hint is not None else {"alpha_mode": "blend",
                                         "opacity": 0.38, "ior": 1.5})
    _pack(str(skins_dir), "glass_facade_delco_1997", "glass_facade_bronze")
    materials.set_skin_library(str(skins_dir), "delco_1997")
    module = _window_module(glazing)
    module["type"] = species
    module["species"] = species
    module["stem"] = f"{species}_delco_1997_01_w200"
    try:
        B.build_module(module, str(tmp_path / "out"), theme="delco_1997",
                       style=1, options={"collision": False})
    finally:
        materials.set_skin_library(None)
    return {o.name: o for o in bpy.data.objects}


def _blended(mat):
    alpha = mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value
    return alpha < 1.0 and getattr(mat, "surface_render_method", "BLENDED") == "BLENDED"


def test_bpy_window_pane_blends(tmp_path):
    pytest.importorskip("bpy")
    objs = _build(tmp_path, "window")
    panes = [o for n, o in objs.items() if n.endswith("_Glass")]
    assert len(panes) == 1
    assert _blended(panes[0].data.materials[0])


def test_bpy_facade_window_pane_stays_opaque(tmp_path):
    pytest.importorskip("bpy")
    objs = _build(tmp_path, "window", glazing="facade")
    pane = [o for n, o in objs.items() if n.endswith("_Glass")][0]
    assert pane.data.materials[0].name.startswith("M_Skin_glass_facade")
    assert not _blended(pane.data.materials[0])


def test_bpy_broken_window_has_no_pane_and_blended_remnants(tmp_path):
    pytest.importorskip("bpy")
    objs = _build(tmp_path, "window_broken")
    assert not [n for n in objs if n.endswith("_Glass")]
    rem = [o for n, o in objs.items() if n.endswith("_Remnant")]
    assert len(rem) == 1
    assert _blended(rem[0].data.materials[0])
