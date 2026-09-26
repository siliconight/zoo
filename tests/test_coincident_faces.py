"""No two of a sign's faces share a plane -- and what still does, measured.

0.97.0. `stop_sign` shipped THREE coincident face pairs at 0.00 mm at every
genome corner: the red face's back cap lay exactly on the white border's
front cap (2394 + 1436 cm2 at the default size, ONE defect the probe splits
into two rows because it keys them by the normal of whichever triangle sorted
first, and after `fit_to` the two offsets are two nanometres apart rather
than equal, so the two fans interleave), and the border's back cap exactly on
the post's front face (177 cm2).
`FACE_PROUD` separated the face's FRONT and nothing separated its back. The
species predates the rule the interior species keep and `sign_blade_forms`
spells out, and nothing gated it.

`mailbox` was the same cause in a second place, found by the census below:
its lip's back cap on the body's front face at 0.00 mm and its door's back
cap 0.46 mm behind that.

THE CENSUS THAT FOUND THEM. `tools/coplanar_census.py`, Blender 5.1.1,
2026-09-16: every species with a genome, at its min, default and max corner,
planned through `kit.plan_kit` and built through `build.build_module` -- 300
builds, of which 3 did not build (`boots`, KeyError 'shaft_h' at every
corner, which is a different defect and is not this release's). 61 species
reported 3027 coincident pairs between them.

WHAT THE CENSUS ADDED THAT THE PROBE DOES NOT MEASURE. Coplanar is not
visible. A pair of faces on one plane can only be argued over by a depth
buffer where a viewer can reach it, so the census casts a ray out of each
pair along its normal, both ways, and reports the distance to the first
surface it meets -- `cover`. Cover 0.00 mm is a pair on the outside of the
prop, which fights at every distance. A buried pair fights only once the
depth buffer stops resolving `cover`, which on a 24-bit buffer at Godot's
default near 0.05 / far 4000 is at sqrt(cover * 838871) metres: 13 m for
`soda_cup`'s 0.21 mm, 48 m for what `stop_sign` shipped, 183 m for a bench.

So the three pairs this release removes were REAL and were not visible: all
three sat behind 2.7 to 10.1 mm of the sign's own solid, and the before and
after frames at 3, 8 and 20 m are the same picture. They are removed because
the rule is the rule and because it costs nothing -- 372 triangles before and
372 after -- not because a frame showed them.

WHAT IS GATED AND WHAT IS NOT. `stop_sign` is held at zero. `mailbox` is held
at exactly its two BUTT JOINTS -- the lid's foot on the body's top face and
the legs' tops on its underside, 164 mm and 220 mm inside a closed solid --
because this release fixes the plate cause and not the butt-joint cause, and
a residue that is named is diagnostic where a residue that is not is a
surprise. `RESIDUE` below is every other species the census found, with its
numbers. It is data, not a verdict: nothing here says which of those 3003
pairs is worth a triangle.
"""
from __future__ import annotations

import ast
import json
import math
import os

import pytest

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPES = os.path.join(_ZOO, "zoo_keeper", "recipes")
_GENOMES = os.path.join(_ZOO, "zoo_keeper", "genome", "species")

#: tools/coplanar_probe.py's own --tol default, in metres.
PROBE_TOL = 0.002
#: The pure tests ask for a tenth more than the probe does, because floats
#: land on the number: tests/test_card_shop.py, 0.91.0.
PROBE_CUSHION = 1.1

#: A 24-bit fixed-point depth buffer at Godot's Camera3D defaults, classic
#: (non-reversed) z, which is what the GL Compatibility target gets:
#: resolvable separation at distance z is z^2 * (f - n) / (f * n * (2^24 - 1)),
#: so a separation of `s` metres survives to sqrt(s * K) metres.
DEPTH_K = 4000.0 * 0.05 / (4000.0 - 0.05) * (2 ** 24 - 1)


def fight_distance_m(cover_mm):
    """The distance at which the depth buffer stops resolving `cover_mm`."""
    return math.sqrt(cover_mm / 1000.0 * DEPTH_K)


def _constants(name):
    """Module-level NAME = <arithmetic> assignments of a recipe, in order.
    The recipes import bpy at module scope, so they are read, not imported."""
    path = os.path.join(_RECIPES, name + ".py")
    ns = {}
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            try:
                ns[node.targets[0].id] = eval(
                    compile(ast.Expression(node.value), path, "eval"),
                    {"__builtins__": {}}, dict(ns))
            except Exception:
                continue
    return ns


def _genome(name):
    with open(os.path.join(_GENOMES, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def _min_rung_mm(planes):
    """The closest two of a set of parallel planes, in millimetres."""
    ys = sorted(planes.values())
    return min((b - a) for a, b in zip(ys, ys[1:])) * 1000.0


# --- stop_sign: the ladder ----------------------------------------------------

def stop_sign_planes(c):
    """Every plane the recipe's build() puts perpendicular to y, from its
    constants. The recipe's own arithmetic; the bpy test at the bottom reads
    the built mesh instead, so the two are not the same claim."""
    border_front = -(c["POST"] / 2.0 + c["BLADE_T"])
    red_front = border_front - c["FACE_PROUD"]
    return {
        "legend_front": red_front - c["LEGEND_PROUD"],
        "face_front": red_front,
        "border_front": border_front,
        "face_back": red_front + c["FACE_T"],
        "legend_back": red_front + c["LEGEND_BURY"],
        "post_front": -c["POST"] / 2.0,
        "border_back": border_front + c["BORDER_T"],
        "post_back": c["POST"] / 2.0,
    }


def test_the_stop_signs_constants_are_readable():
    """Guard the guard: every check below reads these."""
    c = _constants("stop_sign")
    for name in ("POST", "BLADE_T", "BORDER", "FACE_PROUD", "LEGEND_PROUD",
                 "LEGEND_BURY", "SEP", "SEP_FLOOR", "FACE_T", "BORDER_T",
                 "PROBE_TOL", "PROBE_CUSHION", "DEPTH_AUTHORED", "DEPTH_MIN"):
        assert name in c, name
    for name in ("DOOR_PROUD", "LIP_PROUD", "BACK_BURY", "BURY_FLOOR",
                 "DEPTH_MIN"):
        assert name in _constants("mailbox"), name


def test_no_two_planes_of_the_stop_sign_are_within_SEP():
    """FAILS ON 0.96.0, where face_back == border_front and
    border_back == post_front, both at 0.00 mm."""
    c = _constants("stop_sign")
    planes = stop_sign_planes(c)
    assert len(set(round(v, 9) for v in planes.values())) == len(planes), planes
    assert _min_rung_mm(planes) >= c["SEP"] * 1000.0 - 1e-9, sorted(planes.items())


def test_the_stop_signs_separation_is_what_the_squeeze_makes_it():
    """SEP is a round number above a floor the recipe COMPUTES, so the test
    is that it sits on that floor from both sides. `geometry.fit_to` scales
    DEPTH_AUTHORED into the slot's depth, which makes the smallest slot the
    worst case, and the floor is the probe's window divided by that factor."""
    c = _constants("stop_sign")
    floor = PROBE_TOL * PROBE_CUSHION * c["DEPTH_AUTHORED"] / c["DEPTH_MIN"]
    assert math.isclose(c["SEP_FLOOR"], floor), c["SEP_FLOOR"]
    assert c["SEP"] >= c["SEP_FLOOR"]
    # and it is not extravagant: half a millimetre less would not clear it
    assert c["SEP"] - 0.0005 < c["SEP_FLOOR"]
    squeeze = c["DEPTH_MIN"] / c["DEPTH_AUTHORED"]
    assert round(c["SEP"] * squeeze * 1000.0, 2) == 2.36


def test_the_stop_signs_probe_constants_are_the_probes():
    c = _constants("stop_sign")
    assert c["PROBE_TOL"] == PROBE_TOL and c["PROBE_CUSHION"] == PROBE_CUSHION
    src = open(os.path.join(_ZOO, "tools", "coplanar_probe.py"),
               encoding="utf-8").read()
    assert '"tol": %s' % PROBE_TOL in src


def test_the_stop_signs_depth_numbers_are_the_genomes():
    """DEPTH_MIN is a copy of a genome field, so it has to be checked against
    it: a genome edit that left it behind would silently narrow SEP's floor.
    DEPTH_AUTHORED is arithmetic and is checked against the planes."""
    c = _constants("stop_sign")
    assert c["DEPTH_MIN"] == _genome("stop_sign")["dimensions"]["depth"]["min"]
    planes = stop_sign_planes(c)
    span = max(planes.values()) - min(planes.values())
    assert math.isclose(span, c["DEPTH_AUTHORED"], abs_tol=1e-12)


def test_the_red_face_still_stands_proud_by_what_it_always_did():
    """The fix is a thicker plate, not a moved one: the look is unchanged and
    the blade is still BLADE_T where a player sees its edge."""
    c = _constants("stop_sign")
    planes = stop_sign_planes(c)
    assert math.isclose(planes["border_front"] - planes["face_front"],
                        c["FACE_PROUD"])
    assert math.isclose(planes["face_front"] - planes["legend_front"],
                        c["LEGEND_PROUD"])
    assert math.isclose(planes["post_front"] - planes["border_front"],
                        c["BLADE_T"])


def test_the_legend_stays_inside_the_blade():
    """0.78.0's rule, re-checked against the planes that moved under it."""
    c = _constants("stop_sign")
    planes = stop_sign_planes(c)
    assert planes["border_front"] < planes["legend_back"] < planes["border_back"]


# --- mailbox: the same cause in a second place --------------------------------

def mailbox_planes(c):
    """The three planes the door, its lip and the body's front face stand on,
    as offsets from the body's front face."""
    return {"lip_front": -c["LIP_PROUD"], "door_front": -c["DOOR_PROUD"],
            "body_front": 0.0, "door_back": c["BACK_BURY"],
            "lip_back": 2.0 * c["BACK_BURY"]}


def test_no_two_planes_of_the_mailboxs_door_are_within_BACK_BURY():
    """FAILS ON 0.96.0, where the lip's back cap was the body's front face
    (0.00 mm) and the door's back cap sat 0.5 mm behind it."""
    c = _constants("mailbox")
    assert _min_rung_mm(mailbox_planes(c)) >= c["BACK_BURY"] * 1000.0 - 1e-9


def test_the_mailboxs_burial_is_what_its_own_squeeze_makes_it():
    """Its squeeze is not the stop sign's: the lip is what stands proud of
    the slot's depth, so the factor is d / (d + LIP_PROUD) at the genome's
    smallest depth. A shared constant would be wrong in both places."""
    c = _constants("mailbox")
    d = _genome("mailbox")["dimensions"]["depth"]["min"]
    assert c["DEPTH_MIN"] == d
    squeeze = d / (d + c["LIP_PROUD"])
    assert math.isclose(c["BURY_FLOOR"], PROBE_TOL * PROBE_CUSHION / squeeze)
    assert c["BACK_BURY"] >= c["BURY_FLOOR"]
    assert c["BACK_BURY"] - 0.0005 < c["BURY_FLOOR"]
    assert round(c["BACK_BURY"] * squeeze * 1000.0, 2) == 2.31
    # the two squeezes really are different numbers, which is the point
    s = _constants("stop_sign")
    assert round(squeeze, 3) == 0.925
    assert round(s["DEPTH_MIN"] / s["DEPTH_AUTHORED"], 3) == 0.675


def test_the_mailboxs_door_stands_out_by_what_it_always_did():
    c = _constants("mailbox")
    assert (c["DOOR_PROUD"], c["LIP_PROUD"]) == (0.0245, 0.04)


# --- the residue, named and measured ------------------------------------------

#: The gated species and what each is held at. `tools/coplanar_census.py`,
#: Blender 5.1.1, 2026-09-16, min / default / max corners, theme delco_1997,
#: style 1, probe defaults (2 mm, 1 mm^2, normal 1e-3).
#: Summed over the three corners, the way `RESIDUE` below is, so that the two
#: add up to one number: `mailbox` is two pairs at each of three corners.
GATED = {"stop_sign": 0, "mailbox": 6}
#: The two `mailbox` pairs that are NOT this release's cause, by part, so a
#: third one cannot appear without the gate noticing.
MAILBOX_BUTT_JOINTS = {("Mailbox_Body", "Mailbox_Lid"),
                       ("Mailbox_Body", "Mailbox_Legs")}

#: Every other species the census found, as
#: (pairs, SAME, OPP, exposed, min cover mm or None where every pair is
#: exposed, largest overlap cm2) summed over the three corners. Measured on
#: the same run. This is the honest residue: it is not a to-do list in
#: priority order and nothing here has been attributed to a recipe.
RESIDUE = {
    "safe_deposit_boxes": (884, 822, 62, 411, 2.08, 1169.8),
    "cubicle_bank": (583, 290, 293, 127, 15.0, 8315.9),
    "stair_rail": (162, 162, 0, 100, 5.0, 148.4),
    "glass_shard": (118, 64, 54, 118, None, 258.0),
    "teller_line": (114, 31, 83, 25, 100.0, 3882.2),
    "flat_top_grill": (92, 69, 23, 60, 1.08, 15163.2),
    "bus_shelter": (87, 66, 21, 30, 2.83, 469.4),
    "street_tree": (39, 22, 17, 6, 2.09, 437884.4),
    "pin_oak": (31, 21, 10, 7, 4.02, 391635.0),
    "cheesesteak": (29, 4, 25, 20, 0.27, 0.2),
    "red_maple": (28, 17, 11, 9, 1.48, 235404.6),
    "callery_pear": (26, 11, 15, 5, 1.82, 116580.0),
    "london_plane": (21, 10, 11, 4, 3.8, 350560.2),
    "honey_locust": (19, 10, 9, 7, 11.82, 113356.1),
    "cash_stack": (16, 16, 0, 16, None, 28.9),
    "hvac_unit": (13, 7, 6, 7, 112.0, 96445.4),
    "vault_door": (12, 4, 8, 1, 3.39, 43.5),
    "parking_meter": (9, 3, 6, 3, 10.31, 781.2),
    "club_fixture": (7, 3, 4, 3, 16.8, 1323.6),
    "water_barrel": (6, 6, 0, 6, None, 4652.1),
    "rubble_frag": (3, 2, 1, 3, None, 53.4),
    "payphone": (2, 2, 0, 2, None, 2.4),
    "weed_tuft": (2, 2, 0, 2, None, 2.4),
    "security_camera": (2, 1, 1, 1, 59.9, 55.9),
    "desk": (182, 0, 182, 0, 15.75, 10180.2),
    "ladder": (110, 0, 110, 0, 5.0, 6.2),
    "filing_cabinet": (83, 0, 83, 0, 18.0, 29769.2),
    "ceiling": (40, 0, 40, 0, 8000.0, 24000.0),
    "floor": (40, 0, 40, 0, 8000.0, 32000.0),
    "roof": (40, 0, 40, 0, 8000.0, 64000.0),
    "table": (24, 0, 24, 0, 40.0, 16.0),
    "bench": (18, 0, 18, 0, 40.0, 135.0),
    "window_broken": (18, 0, 18, 0, 20.25, 6201.4),
    "window": (12, 0, 12, 0, 100.0, 6201.4),
    "queue_stanchion": (9, 0, 9, 0, 35.0, 9.7),
    "water_tank": (9, 0, 9, 0, 72.0, 57325.4),
    "pallet_stack": (8, 0, 8, 0, 25.0, 14017.1),
    "condiment_bottle": (7, 0, 7, 0, 13.21, 10.0),
    "newspaper_box": (7, 1, 6, 0, 10.77, 958.7),
    "soda_cup": (7, 3, 4, 0, 0.21, 84.0),
    "atm": (6, 0, 6, 0, 30.0, 2726.5),
    "breach": (6, 0, 6, 0, 80.0, 572.2),
    "briefcase": (6, 0, 6, 0, 49.0, 0.6),
    "counter": (6, 0, 6, 0, 45.0, 202227.8),
    "doorway": (6, 0, 6, 0, 120.0, 1271.2),
    "jersey_barrier": (6, 0, 6, 0, 145.91, 39853.4),
    "sign_box": (6, 0, 6, 0, 20.0, 84233.2),
    "traffic_signal": (6, 0, 6, 0, 17.86, 740.1),
    "wall_pack": (6, 0, 6, 0, 20.0, 918.0),
    "bollard": (5, 0, 5, 0, 50.0, 395.5),
    "streetlight": (4, 0, 4, 0, 60.0, 87.7),
    "drop_safe": (3, 0, 3, 0, 30.0, 11298.4),
    "exhaust_fan": (3, 0, 3, 0, 50.92, 3567.1),
    "fluorescent_fixture": (3, 0, 3, 0, 28.0, 10828.8),
    "pendant_fixture": (3, 0, 3, 0, 35.62, 2.2),
    "skylight": (3, 0, 3, 0, 75.0, 23449.6),
    "vent_stack": (3, 0, 3, 0, 60.0, 3720.4),
    "wallCorner": (2, 0, 2, 0, 300.0, 19092.4),
    "litter_scrap": (1, 0, 1, 0, 0.34, 1.2),
}
#: Species the census built clean at all three corners, and the ones it could
#: not build at all. The sum of the three has to be every genome there is, or
#: the census has a hole in it that nobody can see.
DID_NOT_BUILD = {"boots"}
#: 0.98.0: the flat art adds four species, so the census is 12 builds longer.
#: They were run through the same tool on the same Blender the same day --
#: `blender -b --python tools/coplanar_census.py -- --species poster
#: hanging_banner ceiling_hanger aisle_sign` -- and reported "12 builds, 0
#: with coincident pairs, 0 that did not build", so all four land in `clean`
#: and neither `RESIDUE` nor the 3009 below moves. Counting them WITHOUT
#: running the census would have been the defect this test exists to catch.
#:
#: 1.0.0: `cash_register`, three builds more. Run through the same tool --
#: `blender -b --python tools/coplanar_census.py -- --species cash_register
#: display_case` -- and reported "6 builds, 0 with coincident pairs, 0 that
#: did not build", so it lands in `clean`, `display_case` is confirmed
#: unmoved by its new `till` parameter, and neither `RESIDUE` nor the 3009
#: below changes.
#: 1.4.0: `canopy_lights`, three builds more. Run through the same tool --
#: `blender -b --python tools/coplanar_census.py -- --species canopy_lights`
#: on Blender 5.1.1 (b70da489d7f4) -- and reported "3 builds, 0 with
#: coincident pairs, 0 that did not build", so it lands in `clean` and neither
#: `RESIDUE` nor the 3009 below moves. Its three corners measured 224 / 1176 /
#: 3024 tris, which is also where its genome budget came from.
CENSUS_BUILDS = 318


def test_the_census_covers_every_species_there_is():
    """A checker that cannot find a species has learned nothing about it."""
    species = {f[:-5] for f in os.listdir(_GENOMES) if f.endswith(".json")}
    accounted = set(RESIDUE) | set(GATED) | DID_NOT_BUILD
    assert accounted <= species, sorted(accounted - species)
    clean = species - accounted
    assert len(species) * 3 == CENSUS_BUILDS, len(species)
    assert clean, "every species reported pairs: check the census ran"


def test_nothing_is_gated_and_in_the_residue_at_once():
    assert not (set(GATED) & set(RESIDUE))


def test_the_residue_is_the_count_the_entry_claims():
    """0.96.0 shipped 3027 pairs over 61 species; this release removes 18 of
    them (stop_sign's 9, mailbox's 9 of 15) and leaves 3009."""
    total = sum(v[0] for v in RESIDUE.values()) + sum(GATED.values())
    assert total == 3009, total
    exposed = sum(v[3] for v in RESIDUE.values())
    assert exposed == 973, exposed
    assert total + 18 == 3027


def test_every_residue_row_is_self_consistent():
    for sp, (pairs, same, opp, exposed, cover, area) in RESIDUE.items():
        assert same + opp == pairs, sp
        assert 0 <= exposed <= pairs, sp
        # a species with a cover figure has at least one buried pair, and one
        # with none has every pair on the outside
        assert (cover is None) == (exposed == pairs), sp
        assert area > 0.0, sp


def test_the_worst_buried_residue_fights_closer_than_the_stop_sign_did():
    """The reading that decides what to do next, stated as arithmetic rather
    than as an opinion: what 0.96.0's stop sign shipped was 2.70 mm of cover,
    and four species ship less."""
    worse = {sp: v[4] for sp, v in RESIDUE.items()
             if v[4] is not None and v[4] < 2.70}
    assert set(worse) == {"soda_cup", "litter_scrap", "cheesesteak",
                          "flat_top_grill", "red_maple", "callery_pear",
                          "safe_deposit_boxes", "street_tree"}, sorted(worse)
    assert round(fight_distance_m(0.21), 1) == 13.3
    assert round(fight_distance_m(2.70), 1) == 47.6


# --- bpy: what was actually built ---------------------------------------------

def _census_module():
    """`tools/coplanar_census.py` itself, not a second copy of what it does.

    The census owns the role a species is planned under -- a `prop` slot
    asking for `wall` gets a slab, and half the residue below is named after
    a role -- and it owns the exposure pass. Re-implementing either here is
    how two instruments come to disagree."""
    path = os.path.join(_ZOO, "tools", "coplanar_census.py")
    # `_repo()` reads __file__, and an exec'd module has none unless it is
    # given one -- re-read in the turn it is called, not remembered
    ns = {"__name__": "coplanar_census_lib", "__file__": path}
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), ns)
    return ns


def _probe_species(species, corner):
    """One species at one genome corner, through the census, returning the
    census's own record: `pairs`, `tris`, `status`, or `error`."""
    import bpy
    import mathutils
    import tempfile
    census = _census_module()
    ppath = os.path.join(_ZOO, "tools", "coplanar_probe.py")
    probe = {"__name__": "coplanar_probe_lib", "__file__": ppath}
    exec(compile(open(ppath, encoding="utf-8").read(), ppath, "exec"), probe)
    with tempfile.TemporaryDirectory() as tmp:
        rows = census["run"](bpy, mathutils, probe, [species], [corner],
                             "delco_1997", 1, tmp, 0.002, 1e-6, 1e-3)
    assert len(rows) == 1
    assert "error" not in rows[0], rows[0].get("error")
    return rows[0]


CORNERS = ("min", "default", "max")


@pytest.mark.parametrize("corner", CORNERS)
def test_bpy_the_stop_sign_builds_with_no_coincident_faces(corner):
    """FAILS ON 0.96.0 with three pairs at every corner."""
    pytest.importorskip("bpy")
    rec = _probe_species("stop_sign", corner)
    assert rec["pairs"] == [], rec["pairs"][:3]
    assert rec["tris"] == 372, rec["tris"]   # thicker prisms, not more of them


@pytest.mark.parametrize("corner", CORNERS)
def test_bpy_the_mailbox_keeps_only_its_two_butt_joints(corner):
    """FAILS ON 0.96.0 with five pairs: these two and the three the door and
    its lip made. Held at exactly these two by part, so a new one shows."""
    pytest.importorskip("bpy")
    rec = _probe_species("mailbox", corner)
    rows = rec["pairs"]
    assert {(r["a"], r["b"]) for r in rows} == MAILBOX_BUTT_JOINTS, rows
    assert len(rows) == 2, rows
    assert rec["tris"] == 264, rec["tris"]
    # and both of them are deep inside a closed solid, which is the reason
    # they are left: see the entry's table
    assert min(r["cover_mm"] for r in rows) >= 100.0, rows


@pytest.mark.parametrize("species", sorted(RESIDUE))
def test_bpy_the_residue_is_exactly_the_count_the_table_says(species):
    """Every species that does not keep the rule, pinned to the number of
    pairs it shipped on 2026-09-16, summed over the three corners.

    A strict xfail was tried here first and was the wrong instrument: asked
    only at the default corner it went XPASS on six species -- ceiling,
    floor, roof, payphone, security_camera, vault_door -- which are dirty at
    ONE corner and clean at the default. The count says by how much it moved
    and at which corner it was measured; a red/green says neither."""
    pytest.importorskip("bpy")
    got = sum(len(_probe_species(species, c)["pairs"]) for c in CORNERS)
    assert got == RESIDUE[species][0], (species, got, RESIDUE[species][0])


@pytest.mark.xfail(strict=True, reason="59 species still ship coincident "
                                       "faces -- the RESIDUE table above")
def test_every_species_in_the_library_keeps_the_rule():
    """The rule Zoo states for an interior species, asked of the whole
    library. IT FAILS, and it is a test so that it fails on the board rather
    than in a paragraph nobody runs. The day RESIDUE empties this goes green
    and strict xfail turns that into a red somebody has to come and close."""
    assert RESIDUE == {}, "%d species, %d pairs" % (
        len(RESIDUE), sum(v[0] for v in RESIDUE.values()))
