"""The authored aperture: a doorway is the hole Deli Counter asked for.

Every doorway/window/breach slot carries its real opening in ``fit.openings``
-- ``{"kind": "door", "width": 1.2, "height": 2.2, "sill": 0.0}`` -- and
``void_for`` never read it, deriving the hole from genome FRACTIONS of the
module height instead. On a 3.7 m storey that made a 2.2 m door a 3.48 m slit
running floor to ceiling, and floated every window half a metre above its sill.
These pin both halves: the geometry, and the filename that has to tell two
apertures apart.
"""

from zoo_keeper.core import arch, kit

#: The real doorway slot off `category5_baie_dore_001`, storey height 3.7 m.
DOOR = {"kind": "door", "width": 1.2, "height": 2.2, "sill": 0.0}
WINDOW = {"kind": "window", "width": 3.0, "height": 1.4, "sill": 0.8}


def _hole(v, h):
    """(width, height, sill-above-the-module-floor) of a void."""
    return (round(v["x1"] - v["x0"], 4), round(v["z1"] - v["z0"], 4),
            round(v["z0"] + h / 2.0, 4))


# --------------------------------------------------------------------------- #
# arch.void_for -- the geometry
# --------------------------------------------------------------------------- #

def test_a_door_is_as_tall_as_the_slot_asked():
    """The defect: 2.20 m authored, 3.48 m cut. A slit, not a doorway."""
    v = arch.void_for("doorway", 1.2, 3.7, {"opening": DOOR})
    assert _hole(v, 3.7)[1] == 2.2
    # what it used to be, kept as the contrast rather than described
    old = arch.void_for("doorway", 1.2, 3.7)
    assert round(old["z1"] - old["z0"], 4) == 3.48


def test_a_window_sits_on_its_authored_sill():
    v = arch.void_for("window", 3.0, 3.7, {"opening": WINDOW})
    assert _hole(v, 3.7)[1:] == (1.4, 0.8)
    old = arch.void_for("window", 3.0, 3.7)
    assert round(old["z0"] + 3.7 / 2.0, 4) == 1.295      # half a metre high


def test_a_breach_too_is_the_authored_hole():
    """Breach had the largest error of the three: +1.40 m."""
    v = arch.void_for("breach", 1.5, 3.7,
                      {"opening": {"kind": "breach", "width": 1.5,
                                   "height": 2.2, "sill": 0.0}})
    assert _hole(v, 3.7)[1] == 2.2


def test_the_width_is_still_jamb_clamped():
    """DC authors the module exactly as wide as its aperture.

    Honouring that literally leaves no jamb, and with no jamb NOTHING in
    `slab_parts` spans the module's full height -- fit-to-exact-dims stops
    passing by construction. The jamb is 12 cm a side, which is a door frame.
    """
    v = arch.void_for("doorway", 1.2, 3.7, {"opening": DOOR})
    assert _hole(v, 3.7)[0] == 0.96          # not 1.2


def test_a_narrower_authored_width_is_honoured():
    """A 1.0 m door in a 2.0 m module is a real thing to ask for."""
    v = arch.void_for("doorway", 2.0, 3.7,
                      {"opening": {"width": 1.0, "height": 2.1, "sill": 0.0}})
    assert _hole(v, 3.7)[0] == 1.0
    assert v["x0"] == -0.5 and v["x1"] == 0.5     # centred in the module


def test_the_outer_bbox_still_equals_the_authored_dims():
    """The guarantee that makes Zoo a valid art/zoo library: DC never scales
    a module, so its union bbox must be the slot's box exactly."""
    v = arch.void_for("doorway", 1.2, 3.7, {"opening": DOOR})
    parts = arch.slab_parts(1.2, 0.35, 3.7, v)
    lo, hi = arch.parts_bbox(parts)
    assert [round(x, 6) for x in lo] == [-0.6, -0.175, -1.85]
    assert [round(x, 6) for x in hi] == [0.6, 0.175, 1.85]


def test_an_opening_taller_than_the_module_is_clamped_not_extended():
    v = arch.void_for("doorway", 1.2, 2.4,
                      {"opening": {"width": 1.2, "height": 9.0, "sill": 0.0}})
    assert v["z1"] == 1.2                     # the module top, h/2
    parts = arch.slab_parts(1.2, 0.35, 2.4, v)
    lo, hi = arch.parts_bbox(parts)
    assert round(hi[2] - lo[2], 6) == 2.4     # the jambs still carry the height


def test_no_authored_opening_falls_back_to_the_genome_unchanged():
    """A greybox kit, or a species the manifest does not describe, must build
    exactly what it built before. The fractions are the fallback, not dead."""
    for species in ("doorway", "window", "breach", "vault_door"):
        assert (arch.void_for(species, 2.0, 3.7, {})
                == arch.void_for(species, 2.0, 3.7))
        assert arch.void_for(species, 2.0, 3.7) is not None


def test_a_degenerate_opening_falls_back_rather_than_cutting_nothing():
    """Zero height, or a sill above the module top, is not an answer -- a
    module with no hole in it is a wall, and a doorway is not a wall."""
    for op in ({"width": 1.2, "height": 0.0, "sill": 0.0},
               {"width": 1.2, "height": 2.2, "sill": 9.0}):
        v = arch.void_for("doorway", 1.2, 3.7, {"opening": op})
        assert v == arch.void_for("doorway", 1.2, 3.7), op


def test_an_opening_with_no_width_still_gets_its_authored_height():
    """HEIGHT is what the genome got wrong; width it already had about right.

    So a slot that names a height and omits the width is not degenerate -- it
    gets the authored height at the jamb-clamped width, which is strictly
    better than throwing the height away too.
    """
    v = arch.void_for("doorway", 1.2, 3.7,
                      {"opening": {"height": 2.2, "sill": 0.0}})
    assert _hole(v, 3.7) == (0.96, 2.2, 0.0)


def test_a_solid_species_ignores_an_opening():
    assert arch.void_for("wall", 2.0, 3.7, {"opening": DOOR}) is None
    assert arch.void_for("floor", 2.0, 0.02, {"opening": DOOR}) is None


def test_deterministic():
    assert (arch.void_for("window", 3.0, 3.7, {"opening": WINDOW})
            == arch.void_for("window", 3.0, 3.7, {"opening": WINDOW}))


# --------------------------------------------------------------------------- #
# kit -- width alone stopped identifying a doorway
# --------------------------------------------------------------------------- #

def _slot(role, dims, openings=None):
    return {"slot_id": "s", "role": role, "size_mod": "full", "style": 1,
            "material": "concrete",
            "fit": {"dims": dims, "pivot": "center",
                    "openings": openings or [], "voids": []}}


def test_same_width_different_aperture_are_different_modules():
    """Two 1.4 m doorway slots, one with a 2.2 m door and one with a 2.4 m
    door, both resolved to `doorway_rockay_01_w140`: one file wins and one
    room gets the other's hole. The third time this collision has been paid
    for -- `_d` fixed it for plate depth, `_v` for stairwells."""
    a = [{"kind": "door", "width": 1.4, "height": 2.2, "sill": 0.0}]
    b = [{"kind": "door", "width": 1.4, "height": 2.4, "sill": 0.0}]
    plan = kit.plan_kit({"slots": [_slot("doorway", [1.4, 0.35, 3.7], a),
                                   _slot("doorway", [1.4, 0.35, 3.7], b),
                                   _slot("doorway", [1.4, 0.35, 3.7], a)]},
                        theme="rockay")
    assert len(plan["modules"]) == 2
    assert len({m["stem"] for m in plan["modules"]}) == 2
    assert sorted(m["count"] for m in plan["modules"]) == [1, 2]


def test_a_window_sill_alone_splits_the_module():
    """Same size hole, different height up the wall. Same file, before."""
    a = [{"kind": "window", "width": 2.0, "height": 1.4, "sill": 0.8}]
    b = [{"kind": "window", "width": 2.0, "height": 1.4, "sill": 0.9}]
    plan = kit.plan_kit({"slots": [_slot("window", [2.0, 0.35, 3.7], a),
                                   _slot("window", [2.0, 0.35, 3.7], b)]},
                        theme="rockay")
    assert len({m["stem"] for m in plan["modules"]}) == 2


def test_wall_and_plate_names_are_untouched():
    """A wall has no aperture, so no wall filename in the library moves."""
    plan = kit.plan_kit({"slots": [_slot("wall", [2.0, 0.35, 3.7])]},
                        theme="rockay")
    assert plan["modules"][0]["stem"] == "wall_rockay_01_w200"


def test_the_aperture_rides_onto_the_module():
    """dna puts this on plan.params['opening']; without it the recipe is back
    to genome fractions however good the filename is."""
    plan = kit.plan_kit({"slots": [_slot("doorway", [1.2, 0.35, 3.7], [DOOR])]},
                        theme="rockay")
    m = plan["modules"][0]
    assert m["openings"] == [DOOR]
    assert m["openings_tag"] and m["stem"].endswith("_o" + m["openings_tag"])


def test_the_opening_tag_keeps_order():
    """Only the FIRST opening is cut, so a different order is different
    geometry. A plate's voids are a set and sort; these must not."""
    a = {"kind": "door", "width": 1.2, "height": 2.2, "sill": 0.0}
    b = {"kind": "window", "width": 1.2, "height": 1.4, "sill": 0.9}
    assert kit.opening_tag([a, b]) != kit.opening_tag([b, a])
    assert kit.opening_tag([]) is None and kit.opening_tag(None) is None
    assert kit.opening_tag([a]) == kit.opening_tag([dict(a)])


def test_the_tag_values_are_pinned_across_the_repo_seam():
    """THE HALF OF THE CONTRACT A UNIT TEST CANNOT SEE.

    Deli Counter's ``themed_tscn.opening_tag`` computes this same string and
    looks for the file Zoo named with it. Neither side parses; both construct.
    So the only thing that keeps them agreeing is that both are pinned to the
    same literals -- `deli_counter/test_themed_stem.py` asserts these exact
    six characters, and either repo drifting alone fails its own suite instead
    of silently resolving to a module that is not there.
    """
    assert kit.opening_tag(
        [{"kind": "door", "width": 1.2, "height": 2.2, "sill": 0.0}]) == "97cfbf"
    assert kit.opening_tag(
        [{"kind": "window", "width": 3.0, "height": 1.4,
          "sill": 0.8}]) == "ba672d"
    assert kit.module_stem("doorway", "rockay", 1, 120, None, None, None,
                           "97cfbf") == "doorway_rockay_01_w120_o97cfbf"


def test_the_kind_is_part_of_the_identity():
    """A garage door and a person door of the same rect are not one module
    once the art pass gives them different leaves."""
    a = [{"kind": "door", "width": 2.4, "height": 2.2, "sill": 0.0}]
    b = [{"kind": "garage", "width": 2.4, "height": 2.2, "sill": 0.0}]
    assert kit.opening_tag(a) != kit.opening_tag(b)
