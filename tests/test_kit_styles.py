"""Per-slot skin styles + material overrides (Deli Counter >= 0.88 slots).

DC derives each slot's `style` from its surface MATERIAL and carries both on
the slot. The kit planner must build one module family per material zone --
not funnel every slot through the kit-level default -- and the DNA resolver
must build each module in the slot's material kind. Older manifests (no
style/material on slots) must plan exactly as before.
"""
from zoo_keeper.core import dna, kit


def _slot(style=None, material=None, width=2.0, role="wall"):
    s = {"slot_id": f"s_{style}_{material}", "role": role, "size_mod": "full",
         "fit": {"dims": [width, 0.35, 4.0], "pivot": "center"}}
    if style is not None:
        s["style"] = style
    if material is not None:
        s["material"] = material
    return s


def _manifest(slots):
    return {"building_id": "b", "slots": slots}


def test_slots_split_into_per_style_module_families():
    plan = kit.plan_kit(_manifest([
        _slot(style=1, material="concrete"),
        _slot(style=1, material="concrete"),
        _slot(style=3, material="drywall"),
        _slot(style=4, material="metal"),
    ]), theme="rockay", style=1)
    stems = sorted(m["stem"] for m in plan["modules"])
    assert stems == ["wall_rockay_01_w200", "wall_rockay_03_w200",
                     "wall_rockay_04_w200"]
    by = {m["stem"]: m for m in plan["modules"]}
    assert by["wall_rockay_01_w200"]["count"] == 2
    assert by["wall_rockay_03_w200"]["material"] == "drywall"
    assert by["wall_rockay_04_w200"]["material"] == "metal"


def test_legacy_slots_without_style_plan_exactly_as_before():
    plan = kit.plan_kit(_manifest([_slot(), _slot()]), theme="rockay", style=1)
    assert [m["stem"] for m in plan["modules"]] == ["wall_rockay_01_w200"]
    assert plan["modules"][0]["count"] == 2
    assert plan["modules"][0]["material"] is None


def test_same_width_different_material_never_merges():
    plan = kit.plan_kit(_manifest([
        _slot(style=2, material="glass"),
        _slot(style=3, material="drywall"),
    ]), theme="rockay", style=1)
    assert plan["module_count"] == 2


def _wall_genome():
    return {"species": "wall", "version": 1,
            "materials": {"default": "concrete",
                          "options": ["concrete", "plaster", "metal"]},
            "styles": {"default": {"material": "concrete",
                                   "color": [0.5, 0.5, 0.5]}},
            "parts": ["Wall_Panel"], "params": {},
            "budgets": {"tris": 1000}}


def _module(style=3, material="drywall"):
    return {"type": "wall", "species": "wall", "state": None, "width_cm": 200,
            "style": style, "material": material, "fit": "exact",
            "dims": [2.0, 0.35, 4.0], "pivot": "center",
            "stem": f"wall_rockay_{style:02d}_w200"}


def test_dna_material_override_beats_genome_default():
    plan = dna.resolve_module_plan(_module(material="drywall"), _wall_genome(),
                                   "rockay", 1, "test")
    # drywall is a known surface KIND even though the wall species' own
    # options list doesn't name it -- the slot's demand wins.
    assert plan["material"] == "drywall"
    assert plan["module"]["style"] == 3
    assert plan["module"]["stem"] == "wall_rockay_03_w200"


def test_dna_unknown_material_falls_back_to_genome():
    plan = dna.resolve_module_plan(_module(material="unobtainium"),
                                   _wall_genome(), "rockay", 1, "test")
    assert plan["material"] == "concrete"


def test_dna_no_override_keeps_theme_material():
    m = _module()
    m.pop("material")
    m.pop("style")
    m["stem"] = "wall_rockay_01_w200"
    plan = dna.resolve_module_plan(m, _wall_genome(), "rockay", 1, "test")
    assert plan["material"] == "concrete"
    assert plan["module"]["style"] == 1
