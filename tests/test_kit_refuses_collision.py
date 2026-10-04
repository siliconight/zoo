"""A kit whose plan gives two geometries one name is refused (1.62.0).

`plan_kit` has reported `stem_collisions` and printed "STEM COLLISION ... one
will overwrite the other" since it was written. Cold run 9148 printed it in
all six rowhome Empties' kit logs -- 2.8 m and 3.1 m walls and windows under
one name each -- and `--build-kit` exited 0, so the 2.8 m module stood in every
3.1 m slot and the frames showed a strip at each storey line. A print nobody
reads stopped nothing. The collision now rides in the kit index and fails the
build like a failed module.
"""
import importlib.util
import os

from zoo_keeper.core import kit

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "zoo_cli_under_test", os.path.join(HERE, "..", "tools", "zoo_cli.py"))
zoo_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(zoo_cli)


def _wall(h):
    return {"slot_id": "s%d" % int(h * 100), "role": "wall", "size_mod": "full", "style": 1,
            "material": "brick", "fit": {"dims": [2.0, 0.3, h], "pivot": "center",
                                         "openings": [], "collision": "convex"}}


def test_the_plan_still_names_the_collision():
    plan = kit.plan_kit({"building_id": "t", "slots": [_wall(3.1), _wall(2.8)]},
                        theme="delco_1997", style=1)
    assert [c["stem"] for c in plan["stem_collisions"]] == [
        "wall_delco_1997_01_w200_mbrick"]


def test_a_collision_fails_the_kit_build():
    """FAILS ON 1.61.0: the exit code read only failed modules."""
    res = {"n_fail": 0, "stem_collisions": [{"stem": "wall_x", "count": 2}]}
    assert zoo_cli.kit_exit_code(res) == 2


def test_a_clean_kit_passes_and_a_failed_module_still_fails():
    assert zoo_cli.kit_exit_code({"n_fail": 0, "stem_collisions": []}) == 0
    assert zoo_cli.kit_exit_code({"n_fail": 1, "stem_collisions": []}) == 2
