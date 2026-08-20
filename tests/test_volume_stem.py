"""A prop's filename has to name every axis a prop is free on.

The plate bug, one axis further on. `module_stem` grew `_d<cm>` when a 44x24
room and a 44x16 room both resolved to `floor_rockay_01_w4400` and the shorter
room got a slab eight metres too deep. The argument for leaving every other
role on width alone was written down at the time:

    "A wall varies on one axis -- its width -- while its thickness and the
     storey height are fixed, so `_w<cm>` is a complete key."

True for a wall. `prop` was added later, and `recipes/prop.py` describes it as
"a vault, a teller counter, a desk, a cabinet, a crate stack" -- a solid free
on all three axes. It inherited an argument that was never about it.

MEASURED, over 52 of the 136 shipped `slots.json` manifests: 15 buildings (28%)
planned two or more DISTINCT prop modules onto one filename. The worst was
`cr_gas`, where `prop_delco_04_w90` was claimed by both [0.9, 10.0, 1.8] and
[0.9, 0.9, 1.0] -- a 9.1 m difference in depth.
"""
from __future__ import annotations

from zoo_keeper.core import kit


def _slots(*dims):
    return {"building_id": "t",
            "slots": [{"role": "prop", "fit": {"dims": list(d)}} for d in dims]}


def _stems(manifest):
    plan = kit.plan_kit(manifest, theme="delco", style=1)
    return [m["stem"] for m in plan["modules"]]


# --- the defect, from the real data ----------------------------------------

def test_the_cr_gas_pair_no_longer_shares_a_filename():
    """The worst real collision found: a 10 m counter and a 0.9 m cube."""
    stems = _stems(_slots((0.9, 10.0, 1.8), (0.9, 0.9, 1.0)))
    assert len(stems) == 2
    assert len(set(stems)) == 2, stems


def test_props_differing_only_in_height_are_different_modules():
    """DEPTH ALONE WOULD NOT HAVE CAUGHT THIS.

    Every real collision in the sample happened to differ on depth as well as
    height, so adding `_d<cm>` would have separated all of them and looked like
    a complete fix. This pair differs on height only, which is why the key
    names every axis rather than the ones that happened to be measured.
    """
    stems = _stems(_slots((4.0, 1.2, 0.9), (4.0, 1.2, 2.2)))
    assert len(set(stems)) == 2, stems


def test_props_differing_only_in_depth_are_different_modules():
    stems = _stems(_slots((4.0, 1.2, 2.2), (4.0, 1.4, 2.2)))
    assert len(set(stems)) == 2, stems


def test_identical_props_still_collapse_to_one_module():
    """The other half of the contract. A key that splits identical solids
    would build the same GLB twice and call it a kit."""
    stems = _stems(_slots((3.0, 0.8, 2.0), (3.0, 0.8, 2.0)))
    assert len(stems) == 1


# --- the naming law -------------------------------------------------------

def test_a_prop_stem_carries_width_depth_and_height():
    assert kit.module_stem("prop", "delco", 4, 300, None, 80, None, None,
                           200) == "prop_delco_04_w300_d80_h200"


def test_the_axis_order_is_w_then_d_then_h():
    """Both sides CONSTRUCT the stem and neither parses it, so order is only
    a convention -- but a convention the two must share exactly."""
    stem = kit.module_stem("prop", "t", 1, 100, None, 200, None, None, 300)
    assert stem.index("_w") < stem.index("_d") < stem.index("_h")


def test_a_wall_filename_is_untouched():
    """The whole back-compatibility promise: only volumes gain a key."""
    assert kit.module_stem("wall", "delco", 1, 200) == "wall_delco_01_w200"


def test_a_plate_keeps_width_and_depth_and_gains_no_height():
    """A floor is 2 cm thick whatever room it is in; a height key on a plate
    would rename every floor in the game for no information."""
    assert kit.module_stem("floor", "delco", 1, 4400, None, 2400) == \
        "floor_delco_01_w4400_d2400"


def test_volume_roles_and_plate_roles_do_not_overlap():
    assert not set(kit.VOLUME_ROLES) & set(kit.PLATE_ROLES)


def test_prop_is_the_volume_role():
    assert "prop" in kit.VOLUME_ROLES


def test_a_wall_end_is_still_a_unit_module():
    """`wallEnd` is one 1x1x1 box Deli Counter scales per slot. It must not
    acquire dimension keys, or one unit module splits into hundreds."""
    plan = kit.plan_kit(
        {"building_id": "t",
         "slots": [{"role": "wall", "size_mod": "end",
                    "fit": {"dims": [0.30, 0.2, 3.0]}},
                   {"role": "wall", "size_mod": "end",
                    "fit": {"dims": [0.45, 0.2, 3.0]}}]},
        theme="delco", style=1)
    assert len(plan["modules"]) == 1
    assert plan["modules"][0]["stem"] == "wallEnd_delco_01"
