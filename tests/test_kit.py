from zoo_keeper.core import kit

# a synthetic slots manifest exercising the naming law
MANIFEST = {
    "building_id": "test_shop",
    "module_size": 2.0,
    "slots": [
        # full 2m walls -> one exact module, shared
        {"role": "wall", "size_mod": "full",
         "fit": {"dims": [2.0, 0.3, 3.6], "pivot": "center"}},
        {"role": "wall", "size_mod": "full",
         "fit": {"dims": [2.0, 0.3, 3.6], "pivot": "center"}},
        # wall remainders (varied sizes) -> ONE wallEnd unit module
        {"role": "wall", "size_mod": "end",
         "fit": {"dims": [0.3, 0.3, 3.6], "pivot": "center"}},
        {"role": "wall", "size_mod": "end",
         "fit": {"dims": [0.45, 0.3, 3.6], "pivot": "center"}},
        # a doorway at 110cm
        {"role": "doorway", "size_mod": "full",
         "fit": {"dims": [1.1, 0.3, 2.2], "pivot": "center"}},
        # a window at 130cm
        {"role": "window", "size_mod": "full",
         "fit": {"dims": [1.3, 0.3, 1.5], "pivot": "center"}},
    ],
}


def test_slot_typename_naming_law():
    assert kit.slot_typename("wall", "full") == "wall"
    assert kit.slot_typename("wall", "end") == "wallEnd"
    assert kit.slot_typename("doorway", "full") == "doorway"


def test_module_stem_matches_deli_counter_convention():
    assert kit.module_stem("wall", "delco", 1, 200) == "wall_delco_01_w200"
    assert kit.module_stem("wallEnd", "delco", 1) == "wallEnd_delco_01"
    assert kit.module_stem("doorway", "delco", 2, 110, "damaged") == \
        "doorway_delco_02_w110_damaged"


def test_plan_collapses_to_distinct_modules():
    plan = kit.plan_kit(MANIFEST, theme="delco", style=1)
    stems = {m["stem"]: m for m in plan["modules"]}
    # 2 full walls collapse to one module; 2 remainders collapse to one unit
    assert "wall_delco_01_w200" in stems
    assert stems["wall_delco_01_w200"]["count"] == 2
    assert stems["wall_delco_01_w200"]["fit"] == "exact"
    assert "wallEnd_delco_01" in stems
    assert stems["wallEnd_delco_01"]["count"] == 2
    assert stems["wallEnd_delco_01"]["fit"] == "unit"
    assert stems["wallEnd_delco_01"]["dims"] == [1.0, 1.0, 1.0]
    assert "doorway_delco_01_w110" in stems
    assert "window_delco_01_w130" in stems
    # 4 distinct modules dress 6 slots
    assert plan["module_count"] == 4
    assert plan["slot_count"] == 6


def test_plan_respects_role_filter():
    plan = kit.plan_kit(MANIFEST, roles={"wall"})
    types = {m["type"] for m in plan["modules"]}
    assert types == {"wall", "wallEnd"}


def test_exact_modules_carry_real_dims():
    plan = kit.plan_kit(MANIFEST)
    door = next(m for m in plan["modules"] if m["type"] == "doorway")
    assert door["dims"] == [1.1, 0.3, 2.2]
    assert door["width_cm"] == 110
    assert door["pivot"] == "center"
