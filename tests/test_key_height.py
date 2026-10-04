"""A slot marked `fit.key_height` names its height (1.60.0).

`module_stem` names a wall by width alone, on the stated ground that "the
storey height is fixed". Deli Counter 0.175.2's Empties broke it: their walls
are 3.1 m on the storeys that have no slab above and 2.8 m under the roof, so
both built as `wall_delco_1997_01_w200_mbrick_idrywall`, one overwrote the
other, and cold run 9148's side walls were 2.8 m panels in 3.1 m slots -- a
0.3 m strip at every storey line. Deli Counter (>= 0.176.0) marks every slot
whose name covers two heights; this side honours the mark, and an unmarked
slot is named exactly as before.
"""
from zoo_keeper.core import kit


def _wall(h, key=False):
    fit = {"dims": [2.0, 0.3, h], "pivot": "center", "openings": [], "collision": "convex"}
    if key:
        fit["key_height"] = True
    return {"slot_id": "ext_0_S_seg0", "role": "wall", "size_mod": "full", "style": 1,
            "material": "brick", "material_in": "drywall", "fit": fit}


def _stems(slots):
    plan = kit.plan_kit({"building_id": "t", "slots": slots}, theme="delco_1997", style=1)
    return sorted(m["stem"] for m in plan["modules"])


def test_two_heights_marked_build_two_named_walls():
    """FAILS ON 1.59.0: one name for both."""
    stems = _stems([_wall(3.1, True), _wall(2.8, True)])
    assert len(stems) == 2 and len(set(stems)) == 2, stems
    assert any("_h310" in s for s in stems) and any("_h280" in s for s in stems)


def test_an_unmarked_wall_is_named_as_before():
    """The control: every building without the mark keeps every name."""
    assert _stems([_wall(3.1)]) == ["wall_delco_1997_01_w200_mbrick_idrywall"]
