"""A fixtures build leaves out named anchor types (1.123.0): one sign a building, the walker walking cold run 9386 --
"in real life this would be 1 sign". FAILS ON 1.122.0, whose `plan` takes no `skip`."""
from zoo_keeper.core import fixtures


def _manifest():
    return {"light_manifest_version": "1.1.0", "building_id": "shop", "anchors": [
        {"id": "ext_0_S_sign", "type": "sign", "pos": [-3.5, -9.35, 2.55], "rot_y": 270.0, "size": [2.4, 0.6]},
        {"id": "ceiling_0", "type": "fluorescent", "pos": [0.0, 0.0, 3.0]}]}


def test_a_skipped_type_builds_nothing_and_says_why():
    p = fixtures.plan(_manifest(), skip=["sign"])
    assert {pl["type"] for pl in p["placements"]} == {"fluorescent"}
    assert any(s["id"] == "ext_0_S_sign" and "skip-fixture-types" in s["reason"] for s in p["skipped"])


def test_no_skip_builds_the_door_box_as_before():
    p = fixtures.plan(_manifest())
    assert {pl["type"] for pl in p["placements"]} == {"fluorescent", "sign"}
