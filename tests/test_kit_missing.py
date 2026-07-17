"""Missing-module gap report (pure planner side)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from zoo_keeper.core import kit


def _manifest():
    return {"building_id": "test_bldg", "slots": [
        {"role": "wall", "fit": {"dims": [2.0, 0.3, 3.0], "pivot": "center"}},
        {"role": "stair_rail", "fit": {"dims": [1.2, 0.1, 0.9], "pivot": "center"}},
        {"role": "doorway", "fit": {"dims": [1.2, 0.3, 2.1], "pivot": "center"}},
    ]}


def test_unknown_species_lands_in_missing_modules():
    plan = kit.plan_kit(_manifest(), known_species={"wall", "doorway", "wallEnd"})
    stems = {m["stem"] for m in plan["modules"]}
    assert any("wall_" in s for s in stems)
    assert any("doorway_" in s for s in stems)
    missing = plan["missing_modules"]
    assert len(missing) == 1
    assert missing[0]["species"] == "stair_rail"
    assert "genome library" in missing[0]["reason"]


def test_no_known_species_keeps_legacy_behavior():
    plan = kit.plan_kit(_manifest())
    assert len(plan["modules"]) == 3
    assert plan["missing_modules"] == []


def test_all_known_no_missing():
    plan = kit.plan_kit(_manifest(),
                        known_species={"wall", "doorway", "wallEnd", "stair_rail"})
    assert plan["missing_modules"] == []
    assert len(plan["modules"]) == 3
