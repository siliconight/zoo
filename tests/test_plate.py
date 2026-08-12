"""Horizontal plates: floor/ceiling skins with the slab's holes in them.

Deli Counter's slabs are trimesh because stairwells, ramps and hatches
boolean-cut holes in them. A skin laid over one as a plain rectangle caps those
holes -- ceiling visible above a staircase, and the staircase unusable if the
skin carries collision. These pin both halves of the fix.
"""

from zoo_keeper.core import arch, kit


def _area(parts):
    return sum(s[0] * s[1] for _n, _c, s in parts)


# --------------------------------------------------------------------------- #
# arch.plate_parts -- the tiling
# --------------------------------------------------------------------------- #

def test_no_voids_is_one_panel_exactly_as_before():
    """A plate with no holes must be byte-identical to the old solid slab."""
    p = arch.plate_parts(44.0, 24.0, 0.02, None)
    assert p == [("Panel", (0.0, 0.0, 0.0), (44.0, 24.0, 0.02))]
    assert arch.plate_parts(4.0, 4.0, 0.02, []) == arch.plate_parts(4.0, 4.0, 0.02, None)


def test_a_hole_removes_exactly_its_own_area():
    p = arch.plate_parts(10.0, 8.0, 0.02,
                         [{"x0": -1.0, "y0": -1.5, "x1": 1.0, "y1": 1.5}])
    assert _area(p) == 80.0 - 6.0
    assert len(p) > 1


def test_the_outer_bbox_still_equals_the_authored_dims():
    """Fit-to-exact-dims has to pass by construction, same as the wall jambs.

    A stairwell cut hard against a wall would otherwise shrink the plate and
    the module would no longer match its slot.
    """
    p = arch.plate_parts(10.0, 8.0, 0.02,
                         [{"x0": 3.0, "y0": -9.0, "x1": 9.0, "y1": 9.0}])
    lo, hi = arch.parts_bbox(p)
    assert (round(lo[0], 6), round(hi[0], 6)) == (-5.0, 5.0)
    assert (round(lo[1], 6), round(hi[1], 6)) == (-4.0, 4.0)


def test_two_holes():
    p = arch.plate_parts(20.0, 10.0, 0.02,
                         [{"x0": -8, "y0": -2, "x1": -4, "y1": 2},
                          {"x0": 4, "y0": -2, "x1": 8, "y1": 2}])
    assert _area(p) == 200.0 - 32.0


def test_a_void_entirely_outside_the_plate_is_ignored():
    p = arch.plate_parts(4.0, 4.0, 0.02,
                         [{"x0": 50, "y0": 50, "x1": 60, "y1": 60}])
    assert p[0][0] == "Panel"


def test_overlapping_voids_do_not_double_count():
    p = arch.plate_parts(10.0, 10.0, 0.02,
                         [{"x0": -2, "y0": -2, "x1": 2, "y1": 2},
                          {"x0": -1, "y0": -1, "x1": 3, "y1": 1}])
    # union of the two rects, not the sum of their areas
    assert _area(p) < 100.0
    assert _area(p) == 100.0 - (16.0 + 2.0)


def test_plate_species_are_declared_solid_rather_than_falling_through():
    """void_for used to return None for floor/ceiling by reaching its end.

    Solid-by-accident is how a ceiling skin came to cap a stairwell, so the
    species are named.
    """
    assert arch.void_for("floor", 4.0, 0.02) is None
    assert arch.void_for("ceiling", 4.0, 0.02) is None
    assert "floor" in arch.PLATE_SPECIES and "ceiling" in arch.PLATE_SPECIES
    assert arch.void_for("doorway", 2.0, 3.0) is not None


def test_deterministic():
    voids = [{"x0": -1, "y0": -1, "x1": 1, "y1": 1}]
    assert arch.plate_parts(6.0, 6.0, 0.02, voids) == \
        arch.plate_parts(6.0, 6.0, 0.02, voids)


# --------------------------------------------------------------------------- #
# kit -- width alone stopped identifying a module
# --------------------------------------------------------------------------- #

def _slot(role, dims, voids=None):
    return {"slot_id": "s", "role": role, "size_mod": "full", "style": 1,
            "material": "concrete",
            "fit": {"dims": dims, "pivot": "center", "openings": [],
                    "voids": voids or []}}


def test_same_width_different_depth_are_different_modules():
    """The defect: a 44x24 room and a 44x16 room both planned as
    floor_rockay_01_w4400, one won the name, and the shorter room was handed a
    slab eight metres too deep."""
    plan = kit.plan_kit({"slots": [_slot("floor", [44.0, 24.0, 0.02]),
                                   _slot("floor", [44.0, 16.0, 0.02]),
                                   _slot("floor", [44.0, 32.0, 0.02])]},
                        theme="rockay")
    stems = {m["stem"] for m in plan["modules"]}
    assert len(stems) == 3
    assert "floor_rockay_01_w4400_d2400" in stems
    assert "floor_rockay_01_w4400_d1600" in stems


def test_wall_names_are_untouched():
    """A wall varies on one axis, so _w<cm> is still a complete key and every
    existing filename in the library keeps working."""
    plan = kit.plan_kit({"slots": [_slot("wall", [2.0, 0.35, 3.7]),
                                   _slot("wall", [2.0, 0.35, 3.7])]},
                        theme="rockay")
    assert len(plan["modules"]) == 1
    assert plan["modules"][0]["stem"] == "wall_rockay_01_w200"
    assert plan["modules"][0]["count"] == 2


def test_same_footprint_different_stairwell_are_different_modules():
    """Two rooms of identical size are still different geometry if the holes
    are in different places."""
    a = [{"x0": -1, "y0": -1, "x1": 1, "y1": 1}]
    b = [{"x0": 3, "y0": 1, "x1": 4, "y1": 2}]
    plan = kit.plan_kit({"slots": [_slot("floor", [10.0, 8.0, 0.02], a),
                                   _slot("floor", [10.0, 8.0, 0.02], b),
                                   _slot("floor", [10.0, 8.0, 0.02], a)]},
                        theme="rockay")
    assert len(plan["modules"]) == 2
    assert sorted(m["count"] for m in plan["modules"]) == [1, 2]


def test_same_footprint_different_stairwell_get_different_FILENAMES():
    """The key knowing they differ is not enough -- the stem has to as well.

    security_office and count_room are both 22x16 with stairwells in different
    places. They planned as two modules and both were named
    floor_rockay_01_w2200_d1600; one file wins and one room gets the other's
    holes. Same collision the depth suffix fixed, one level down.
    """
    a = [{"x0": -1, "y0": -1, "x1": 1, "y1": 1}]
    b = [{"x0": 3, "y0": 1, "x1": 4, "y1": 2}]
    plan = kit.plan_kit({"slots": [_slot("floor", [22.0, 16.0, 0.02], a),
                                   _slot("floor", [22.0, 16.0, 0.02], b),
                                   _slot("floor", [22.0, 16.0, 0.02])]},
                        theme="rockay")
    stems = [m["stem"] for m in plan["modules"]]
    assert len(set(stems)) == 3, stems
    # the hole-free one keeps the plain name
    assert "floor_rockay_01_w2200_d1600" in stems


def test_the_void_tag_is_order_independent():
    a = {"x0": -1, "y0": -1, "x1": 1, "y1": 1}
    b = {"x0": 3, "y0": 1, "x1": 4, "y1": 2}
    assert kit.void_tag([a, b]) == kit.void_tag([b, a])
    assert kit.void_tag([]) is None and kit.void_tag(None) is None


def test_voids_ride_onto_the_module():
    v = [{"x0": -1, "y0": -1, "x1": 1, "y1": 1}]
    plan = kit.plan_kit({"slots": [_slot("ceiling", [10.0, 8.0, 0.02], v)]},
                        theme="rockay")
    assert plan["modules"][0]["voids"] == v
    assert plan["modules"][0]["depth_cm"] == 800


# --------------------------------------------------------------------------- #
# THE ROOF IS A PLATE TOO (2026-08-09)
#
# It was in `_SOLID` beside `wall` and `prop`, so it got no void tiling, no
# depth in its stem and no void tag -- and it emitted collision, which is what
# made it a wall rather than a cosmetic fault. Measured on `bank_branch_a04`:
# DC cut the ladder's through-hole in `slab_col_2-colonly` (corners 15.45 /
# 16.55 / -10.90) and Zoo laid a solid 40 x 30 `roof_rockay_01_w4000.glb` over
# it carrying `Roof-colonly`. The walk bot stalled against a collider named
# `Roof` at the slab underside.
# --------------------------------------------------------------------------- #

def test_a_roof_is_a_plate_and_not_a_standing_slab():
    """Its holes are in x/y -- a hatch, not a doorway."""
    assert "roof" in arch.PLATE_SPECIES
    assert "roof" not in arch._SOLID
    assert arch.void_for("roof", 40.0, 0.3) is None      # no x/z opening


def test_a_roof_still_collides_and_a_ceiling_still_does_not():
    """The two facts `PLATE_SPECIES` used to conflate, asserted apart. A
    ceiling skin declares `collision: none`; a roof slot declares `trimesh`."""
    assert "roof" in arch.PLATE_COLLIDES
    assert "ceiling" not in arch.PLATE_COLLIDES
    assert "floor" not in arch.PLATE_COLLIDES


def test_a_roof_tiles_around_its_void_instead_of_over_it():
    parts = arch.plate_parts(40.0, 30.0, 0.3,
                             [{"x0": 15.45, "y0": 10.9,
                               "x1": 16.55, "y1": 12.2}])
    assert len(parts) > 1, "a solid panel is exactly the bug"
    # nothing survives over the hole
    for _n, c, s in parts:
        over_x = c[0] - s[0] / 2 < 16.0 < c[0] + s[0] / 2
        over_y = c[1] - s[1] / 2 < 11.55 < c[1] + s[1] / 2
        assert not (over_x and over_y), "a part still covers the ladder"
    # and the plate's outer footprint is still exact
    assert _area(parts) < 40.0 * 30.0


def test_the_clean_roof_is_still_one_panel_byte_for_byte():
    """THE CASE THAT MUST NOT CHANGE. Every roof without a hatch has to come
    out of this exactly as it did before -- "it cut the hole in the broken
    building" cannot tell you it did not also punch one in the other 133."""
    assert arch.plate_parts(40.0, 30.0, 0.3, None) == [
        ("Panel", (0.0, 0.0, 0.0), (40.0, 30.0, 0.3))]
    assert arch.plate_parts(40.0, 30.0, 0.3, []) == [
        ("Panel", (0.0, 0.0, 0.0), (40.0, 30.0, 0.3))]


def test_two_roofs_of_one_width_are_no_longer_the_same_module():
    """`roof_rockay_01_w4000` was the stem for a 40x30 roof AND a 40x20 one:
    plates were keyed on both axes, and `roof` was not a plate. That is the
    `module_stem` width-only collision this repo has already paid for twice.
    Latent while `roof_mode` is `footprint` (one roof per building); live the
    moment a building roofs `per_room`."""
    plan = kit.plan_kit({"slots": [_slot("roof", [40.0, 30.0, 0.3]),
                                   _slot("roof", [40.0, 20.0, 0.3])]},
                        theme="rockay")
    stems = {m["stem"] for m in plan["modules"]}
    assert len(stems) == 2, stems
    assert "roof_rockay_01_w4000_d3000" in stems
    assert "roof_rockay_01_w4000_d2000" in stems


def test_two_roofs_with_different_hatches_get_different_filenames():
    hatch_n = [{"x0": -1.0, "y0": -1.0, "x1": 0.1, "y1": 0.3}]
    hatch_e = [{"x0": 15.45, "y0": 10.9, "x1": 16.55, "y1": 12.2}]
    plan = kit.plan_kit({"slots": [_slot("roof", [40.0, 30.0, 0.3], hatch_n),
                                   _slot("roof", [40.0, 30.0, 0.3], hatch_e)]},
                        theme="rockay")
    stems = sorted(m["stem"] for m in plan["modules"])
    assert len(set(stems)) == 2, stems
    assert all("_v" in s for s in stems), stems


def test_the_bank_branch_ladder_reaches_the_roof(): 
    """THE REGRESSION, with the shipped numbers. 40 x 30 roof, ladder at spec
    (16, 12) width 0.5 facing S, so `ladder_geom.through_hole` puts the cut at
    x 15.45..16.55, y 10.90..12.20. The climb column the capsule needs is
    CLIMB_STANDOFF +/- its radius off the face."""
    void = {"x0": 15.45, "y0": 10.9, "x1": 16.55, "y1": 12.2}
    plan = kit.plan_kit({"slots": [_slot("roof", [40.0, 30.0, 0.3], [void])]},
                        theme="rockay")
    m = plan["modules"][0]
    assert m["voids"] == [void]
    assert m["voids_tag"], "no void tag means two hatches share one filename"
    parts = arch.plate_parts(40.0, 30.0, 0.3, m["voids"])
    standoff, capsule_r = 0.5, 0.35
    for x in (16.0 - 0.25, 16.0, 16.0 + 0.25):
        for y in (12.0 - (standoff + capsule_r), 12.0 - standoff,
                  12.0 - (standoff - capsule_r)):
            for _n, c, s in parts:
                assert not (c[0] - s[0] / 2 < x < c[0] + s[0] / 2
                            and c[1] - s[1] / 2 < y < c[1] + s[1] / 2), \
                    f"the roof still covers the climb column at ({x}, {y})"
