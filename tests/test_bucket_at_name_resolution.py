"""A module is grouped no finer than the name it is given (1.63.0).

`plan_kit` grouped exact-fit slots by dims to 0.1 mm while naming them in
whole centimetres. Cold run 9149: the freight terminal's parapet tiles,
cut at millimetre-snapped lines by Deli Counter, were 4.514 and 4.515 m --
two groups, one name `wall_delco_1997_04_w451_mmetal`, and Zoo 1.62.0
rightly refused the collision. Two slots that can only get one name are one
module: grouped at the name's resolution, they build once.
"""
from zoo_keeper.core import kit


def _wall(w, h=1.0, key=False):
    fit = {"dims": [w, 0.2, h], "pivot": "center", "openings": [], "collision": "convex"}
    if key:
        fit["key_height"] = True
    return {"slot_id": "p%s_%s" % (w, h), "role": "wall", "size_mod": "full", "style": 4,
            "material": "metal", "fit": fit}


def _plan(slots):
    return kit.plan_kit({"building_id": "t", "slots": slots}, theme="delco_1997", style=1)


def test_a_millimetre_apart_is_one_module():
    """FAILS ON 1.62.0: two modules, one name, a refused kit."""
    plan = _plan([_wall(4.514), _wall(4.515)])
    assert plan["stem_collisions"] == []
    assert len(plan["modules"]) == 1 and plan["modules"][0]["count"] == 2


def test_a_real_height_difference_still_collides_unless_marked():
    """The control: 2.8 against 3.1 is two geometries the name cannot tell
    apart without the mark, and with it they are two named modules."""
    assert _plan([_wall(2.0, 3.1), _wall(2.0, 2.8)])["stem_collisions"]
    marked = _plan([_wall(2.0, 3.1, True), _wall(2.0, 2.8, True)])
    assert marked["stem_collisions"] == [] and len(marked["modules"]) == 2
