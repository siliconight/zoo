"""The five card-shop species: the arithmetic, the budgets and the rules the
0.94.0 entry names for an interior species -- exact extents, parts
overlapping by millimetres, no two faces within 2 mm of one plane,
deterministic output, colliders inside bounds, and a test at every genome
corner.

Zoo 0.95.0. All of it is pure and needs no Blender; the geometry itself is
checked by building the kit (`--build-kit`, which reported PASS on all nine
modules of `card_shop.slots.json`). Every test here fails on 0.94.0, where
none of the five species exists.

WHY THE WINDOW IS 2.2 mm AND NOT 2.0: `tools/coplanar_probe.py` measures a
built scene at 2 mm and floats land ON that number
(`0.0020000000000000018 > 0.002`), which 0.91.0 recorded after the pure probe
passed a pair Blender's failed. The pure tests use 2.2.
"""
from __future__ import annotations

import itertools

import pytest

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import display_case_forms as DC
from zoo_keeper.core import folding_forms as FF
from zoo_keeper.core import genome, kit
from zoo_keeper.core import pack_wall_forms as PW
from zoo_keeper.core import pennant_forms as PN
from zoo_keeper.core import prims as P

TOL = 0.0022
SPECIES = ("display_case", "pack_wall", "pennant_row", "folding_table",
           "folding_chair")


def _corners(name):
    """Every corner of a genome's dimension box, plus its defaults."""
    g = genome.load_species(name)
    d = g["dimensions"]
    axes = [(d[k]["min"], d[k]["max"]) for k in ("width", "depth", "height")]
    out = [tuple(v) for v in itertools.product(*axes)]
    out.append(tuple(d[k]["default"] for k in ("width", "depth", "height")))
    return out


def _budget(name):
    return genome.load_species(name)["budgets"]["tris_lod0"]


def _plan(name, w, d, h, params, variant):
    if name == "display_case":
        return DC.plan(w, d, h, params, variant, key=f"{name}{w}{d}")
    if name == "pack_wall":
        return PW.plan(w, d, h, params, variant, key=f"{name}{w}{d}")
    if name == "pennant_row":
        return PN.plan(w, d, h, params, variant, key=f"{name}{w}{d}",
                       budget=_budget(name))
    if name == "folding_table":
        return FF.plan_table(w, d, h, params, variant)
    return FF.plan_chair(w, d, h, params, variant)


def _forms(name):
    g = genome.load_species(name)
    f = (g.get("params") or {}).get("form")
    return [x for x in f if x != "auto"] if isinstance(f, list) else [None]


def _cases(name):
    for (w, d, h) in _corners(name):
        for form in _forms(name):
            for v in range(genome.load_species(name)["module_variants"]):
                yield w, d, h, ({"form": form} if form else {}), v


# --- the species exist -------------------------------------------------------


@pytest.mark.parametrize("name", SPECIES)
def test_the_species_is_discovered_and_validates(name):
    assert name in genome.list_species()
    assert genome.validate_genome(genome.load_species(name)) == []


@pytest.mark.parametrize("name", SPECIES)
def test_it_plans_through_the_kit_at_its_own_defaults(name):
    g = genome.load_species(name)
    dims = [g["dimensions"][k]["default"] for k in ("width", "depth", "height")]
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": f"{name}_0", "role": "prop", "size_mod": "full",
        "style": 1, "species": name,
        "fit": {"dims": dims, "pivot": "center"}}]},
        theme="delco_1997", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == name


# --- the rules every interior species keeps ----------------------------------


@pytest.mark.parametrize("name", SPECIES)
def test_no_two_faces_share_a_plane_at_any_genome_corner(name):
    for w, d, h, params, v in _cases(name):
        got = _plan(name, w, d, h, params, v)
        rows = P.coincident_pairs(got["prims"], tol=TOL)
        assert rows == [], (name, w, d, h, params, v, rows[:3])


@pytest.mark.parametrize("name", SPECIES)
def test_the_built_plan_fills_the_slot_box_exactly(name):
    """`validate.fit_*` gates a slot-fit module on its built bounds equalling
    the slot to 2 cm and `core.pivot` re-centres from them, so a plan short
    on any axis ships a module floating off its slot. The display case's
    counter-top stock is EXCLUDED, because it stands above the slot the way
    a monitor on a desk does and `bpylayer.build` returns it as dressing."""
    for w, d, h, params, v in _cases(name):
        got = _plan(name, w, d, h, params, v)
        prims = [p for p in got["prims"] if not p.get("above")]
        lo, hi = P.bounds(prims)
        for i, want in enumerate((w, d, h)):
            assert abs((hi[i] - lo[i]) - want) < 1e-6, (name, w, d, h, params, v, i)
        assert abs(lo[2]) < 1e-6, (name, w, d, h, lo)


@pytest.mark.parametrize("name", SPECIES)
def test_the_species_holds_its_triangle_budget_at_every_corner(name):
    budget = _budget(name)
    worst = 0
    for w, d, h, params, v in _cases(name):
        got = _plan(name, w, d, h, params, v)
        tris = P.tri_count(got["prims"])
        worst = max(worst, tris)
        assert tris <= budget, (name, w, d, h, params, v, tris, budget)
    # THE BUDGET ALSO HAS TO MEAN SOMETHING: one nothing comes near is a
    # number nobody would notice moving. `folding_table` is exempt and named
    # rather than quietly skipped -- its stock comes from `_surface_stock`
    # and is therefore NOT in `prims`, so this measurement sees only the
    # table itself (132 of 600; the built module with `cards` measured 240).
    if name != "folding_table":
        assert worst >= budget * 0.25, (name, worst, budget)


@pytest.mark.parametrize("name", SPECIES)
def test_every_collider_is_inside_the_module_bounds(name):
    for w, d, h, params, v in _cases(name):
        got = _plan(name, w, d, h, params, v)
        for lo, hi in got["collision"]:
            assert lo[0] >= -w / 2 - 1e-6 and hi[0] <= w / 2 + 1e-6, (name, lo, hi)
            assert lo[1] >= -d / 2 - 1e-6 and hi[1] <= d / 2 + 1e-6, (name, lo, hi)
            assert lo[2] >= -1e-6 and hi[2] <= h + 1e-6, (name, lo, hi)


@pytest.mark.parametrize("name", SPECIES)
def test_the_variants_are_different_modules(name):
    """`module_variants` on a species whose variants differ only in wear
    noise is one `kit.honour_dressing` refuses to carry."""
    n = genome.load_species(name)["module_variants"]
    g = genome.load_species(name)["dimensions"]
    dims = [g[k]["default"] for k in ("width", "depth", "height")]
    shapes = set()
    for v in range(n):
        got = _plan(name, dims[0], dims[1], dims[2], {}, v)
        # GEOMETRY AND COLOUR, because for `pennant_row` the colours ARE
        # half the difference -- a strip of the same felt shapes in another
        # set of team colours is a different module, and vertices alone
        # called four of them one. Geometry still has to move too: the tilt
        # phases with the variant, so this cannot pass on colour alone.
        shapes.add((tuple(sorted((p["part"], tuple(p["verts"][0]))
                                 for p in got["prims"])),
                    tuple(tuple(map(tuple, c)) for c in got.get("colours", ()))))
    assert len(shapes) == n, (name, n, len(shapes))


@pytest.mark.parametrize("name", SPECIES)
def test_the_plan_is_deterministic(name):
    g = genome.load_species(name)["dimensions"]
    dims = [g[k]["default"] for k in ("width", "depth", "height")]
    a = _plan(name, dims[0], dims[1], dims[2], {}, 1)
    b = _plan(name, dims[0], dims[1], dims[2], {}, 1)
    assert [(p["part"], p["verts"]) for p in a["prims"]] == \
           [(p["part"], p["verts"]) for p in b["prims"]]


# --- display_case ------------------------------------------------------------


def test_the_L_is_one_case_and_its_top_is_one_mesh():
    """The brief's own test: the L needs a corner that reads as ONE case and
    not two colliding boxes. The claim is geometric -- the glass top is a
    single prim whose footprint covers both runs, and the corner run is
    glazed on TWO adjacent faces through one corner column."""
    got = DC.plan(3.6, 2.4, 1.05, {"form": "L"}, 0, key="L")
    tops = [p for p in got["prims"] if p["part"] == "DisplayCase_Top"]
    assert len(tops) == 1, [p["part"] for p in tops]
    lo, hi = P.bounds(tops)
    assert abs(hi[0] - lo[0] - 3.6) < 1e-9 and abs(hi[1] - lo[1] - 2.4) < 1e-9
    # and it is not a slab over the whole slot: the corner is empty
    area = sum(abs((a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])) / 2.0
               for a, b, c in P.triangles(tops[0])
               if abs(a[2] - hi[2]) < 1e-9 and abs(b[2] - hi[2]) < 1e-9
               and abs(c[2] - hi[2]) < 1e-9)
    assert area < 3.6 * 2.4 * 0.85, area
    corners = [p for p in got["prims"] if "Corner" in p["part"]]
    assert len(corners) == 1, [p["part"] for p in corners]
    glazed = {p["part"][-4:-2] for p in got["prims"] if "Rail" in p["part"]}
    assert len(glazed) >= 2, glazed


def test_the_Ls_collision_leaves_the_inside_of_the_corner_open():
    """One box over the slot would wall off where the staff stand -- and
    where Deli Counter's own aisle runs."""
    got = DC.plan(3.6, 2.4, 1.05, {"form": "L"}, 0, key="L")
    boxes = got["collision"]
    assert len(boxes) >= 2, boxes
    covered = sum((hi[0] - lo[0]) * (hi[1] - lo[1]) for lo, hi in boxes)
    assert covered < 3.6 * 2.4 * 0.85, covered
    # the inside corner is not inside any of them
    px, py = -3.6 / 2 + 0.6, 2.4 / 2 - 0.6
    assert not any(lo[0] <= px <= hi[0] and lo[1] <= py <= hi[1]
                   for lo, hi in boxes), (px, py, boxes)


def test_the_stock_cap_is_what_holds_the_case_in_budget():
    """Not an assertion that a cap is nice: the claim is that removing it
    BLOWS the budget at the genome's largest slot, which is the only thing
    that makes a cap load-bearing rather than decorative."""
    big = (6.0, 3.0, 1.25)
    capped = P.tri_count(DC.plan(*big, {"form": "L"}, 0, key="c")["prims"])
    old = dict(DC.CAPS)
    try:
        DC.CAPS.update({k: 99 for k in DC.CAPS})
        uncapped = P.tri_count(DC.plan(*big, {"form": "L"}, 0, key="c")["prims"])
    finally:
        DC.CAPS.clear()
        DC.CAPS.update(old)
    budget = _budget("display_case")
    assert capped <= budget < uncapped, (capped, budget, uncapped)


def test_the_case_stocks_more_than_one_game():
    got = DC.plan(2.4, 0.6, 1.0, {"form": "flat"}, 0, key="c")
    games = {t.split("_", 1)[1] for t in got["tiles"] if t.startswith("box_")}
    assert len(games) >= 3, sorted(got["tiles"])


# --- pack_wall ---------------------------------------------------------------


def test_a_wide_pack_wall_is_bays_and_no_two_carry_one_game():
    """'module_variants so a row of bays is not one bay repeated' -- and the
    same has to be true INSIDE one wide module, because Deli Counter authors
    aisles as single volumes."""
    got = PW.plan(4.8, 0.5, 2.4, {}, 0, key="run")
    assert got["facts"]["bays"] == 4, got["facts"]
    assert len(set(got["facts"]["games"])) == 4, got["facts"]["games"]
    headers = [t for t in got["tiles"] if t.startswith("header_")]
    assert len(headers) == 4, headers


def test_four_separate_bays_differ_by_variant():
    games = [PW.plan(1.2, 0.5, 2.4, {}, v, key="bay")["facts"]["games"][0]
             for v in range(genome.load_species("pack_wall")["module_variants"])]
    assert len(set(games)) == len(games), games


def test_the_shelf_count_follows_the_bay_s_height():
    """0.99.0. `CAPS["shelves_per_bay"]` was 6 and bound at EVERY height the
    genome allows, so a taller bay was emptier per metre rather than fuller:
    a 2.4 m bay measured 1,416 triangles at 2.2 m and 1,416 at 3.2 m, and
    the only thing height bought was re-spacing the same six shelves from a
    0.259 pitch to a 0.401 one over a 0.092 m booster box.

    Fails on 0.98.0 on the first assert: the counts are equal there."""
    tall = PW.plan(2.4, 0.5, 2.70, {}, 0, key="bay")["facts"]
    short = PW.plan(2.4, 0.5, 2.20, {}, 0, key="bay")["facts"]
    assert tall["shelves_per_bay"] > short["shelves_per_bay"], (tall, short)
    assert tall["tris"] > short["tris"], (tall["tris"], short["tris"])
    # and the gap NARROWS rather than growing with the height
    assert tall["pitch_m"] - short["pitch_m"] < 0.045, (tall, short)


def test_the_shelf_pitch_takes_the_tallest_product_the_row_stands():
    """`SHELF_CLEAR` was `BOX_H + 0.075` and the tallest thing a row stands
    is the BLISTER PACK, 53 mm taller than a box. The count therefore said
    a row fitted where it did not, and the peg row's own measured-clear
    check dropped it -- silently, and at sixteen of the genome's corners.

    Fails on 0.98.0: at 1.6 m the pitch there is 0.173 and every bay in the
    corner set draws zero peg rows."""
    assert PW.SHELF_CLEAR >= PW.PEG_H + 0.025
    assert PW.SHELF_PITCH_MIN == PW.SHELF_CLEAR + PW.SHELF_T
    for w, d, h, params, v in _cases("pack_wall"):
        got = PW.plan(w, d, h, params, v, key="k")
        pegs = [p for p in got["prims"]
                if p["part"].startswith("PackWall_Peg") and "Art" not in p["part"]]
        assert pegs, ("no blister row", w, d, h, v)
        # ...and the pitch the count derived is really the pitch that got
        # built, so the two guards below it can never straddle a threshold
        f = got["facts"]
        assert f["pitch_m"] >= PW.SHELF_PITCH_MIN - 1e-9, (w, d, h, v, f)


def test_a_bay_costs_what_the_cap_assumes_it_costs():
    """The cap's arithmetic is only sound while `bay_tris` and `module_tris`
    really are what the planner draws -- add a part to a bay and the cap
    silently stops holding the budget. `pennant_row` has the same test for
    the same reason."""
    for w, d, h, params, v in _cases("pack_wall"):
        got = PW.plan(w, d, h, params, v, key="k")
        f = got["facts"]
        ax_w = (w / max(1, f["bays"])) - 2 * PW.X_IN["shelf"]
        cols_box = min(PW.CAPS["boxes_per_shelf"], int(ax_w / (PW.BOX_W + 0.010)))
        cols_peg = min(PW.CAPS["pegs_per_row"], int(ax_w / (PW.PEG_W + 0.012)))
        assert PW.module_tris(f["rows_per_bay"], f["bays"],
                              cols_box, cols_peg, v) == f["tris"], \
            (w, d, h, v, f)
        # and the variant-free pricing a cap uses is never OPTIMISTIC
        assert PW.module_tris(f["rows_per_bay"], f["bays"],
                              cols_box, cols_peg) >= f["tris"], (w, d, h, v, f)


def test_both_pack_wall_caps_are_load_bearing_and_neither_alone_is_enough():
    """The 0.95.0 rule, kept: a cap that is not the thing holding the number
    is a comment, so the claim is that REMOVING it blows a budget.

    `shelves_per_bay` was one hand-set number; `max_rows` is two derived
    ones, and each bites somewhere the other does not:

      * lift BOTH at the genome's largest slot (8.0 x 0.6 x 3.2) and the
        MODULE draws 7,486 against a 6,000 budget;
      * lift only the bay budget and the module budget still holds 8.0 m --
        seven bays share it -- but a 3.6 m run goes to ten shelves a bay,
        and four of those plus four islands put Deli Counter's card-shop
        room at 29,704 against 24,000.

    Fails on 0.98.0: neither `max_rows` nor the budgets it reads exist."""
    big = (8.0, 0.6, 3.2)
    budget = _budget("pack_wall")
    capped = PW.plan(*big, {}, 0, key="c")["facts"]["tris"]
    uncapped = PW.plan(*big, {}, 0, key="c",
                       budget=10 ** 9, bay_budget=10 ** 9)["facts"]["tris"]
    assert capped <= budget < uncapped, (capped, budget, uncapped)
    # the MODULE budget alone is what holds seven bays
    assert PW.plan(*big, {}, 0, key="c", bay_budget=10 ** 9)["facts"]["tris"] \
        == capped
    # ...and the BAY budget alone is what holds three, which is what a room
    # actually stands four of
    run = PW.plan(3.6, 0.5, 3.2, {}, 0, key="r")["facts"]
    loose = PW.plan(3.6, 0.5, 3.2, {}, 0, key="r", bay_budget=10 ** 9)["facts"]
    assert loose["tris"] > run["tris"] and loose["tris"] <= budget, (run, loose)


def test_the_bay_budget_is_the_one_dial_that_makes_a_gondola_denser():
    """`pennant_row`'s rule, applied to the species a ROOM stands eight of:
    raising the genome budget raises the count and nothing else has to move
    with it."""
    g = genome.load_species("pack_wall")
    assert PW.BUDGET == g["budgets"]["tris_lod0"]
    assert PW.BAY_BUDGET == g["budgets"]["tris_per_bay"]
    base = PW.plan(1.2, 0.5, 3.2, {}, 0, key="d")["facts"]
    rich = PW.plan(1.2, 0.5, 3.2, {}, 0, key="d",
                   bay_budget=PW.BAY_BUDGET * 2)["facts"]
    assert rich["shelves_per_bay"] > base["shelves_per_bay"], (base, rich)
    # the cap is a real bound at the shipped height, not a formality
    assert base["shelves_per_bay"] == base["cap_rows"] - 1


def test_the_pack_wall_faces_its_product_out():
    """A booster display is read from the aisle: every art quad on a product
    faces -Y, and none of them is behind the shelf it stands on."""
    got = PW.plan(1.2, 0.5, 2.4, {}, 0, key="bay")
    quads = [p for p in got["prims"] if p.get("tile") and "Box" in p["part"]]
    assert quads
    for q in quads:
        ys = {round(v[1], 6) for v in q["verts"]}
        assert len(ys) == 1, q["part"]
        assert ys.pop() < 0.0, q["part"]


# --- pennant_row -------------------------------------------------------------


def test_the_pennant_cap_is_derived_from_the_budget():
    """Derive constants from something rather than choosing them: raising
    the budget is the ONE dial that makes a strip denser."""
    budget = _budget("pennant_row")
    assert PN.max_pennants(budget) == (budget - PN.FIXED_TRIS) // PN.TRIS_PER_PENNANT
    assert PN.max_pennants(budget * 2) > PN.max_pennants(budget)
    got = PN.plan(14.0, 0.12, 0.5, {}, 0, key="p", budget=budget)
    assert got["facts"]["pennants"] <= got["facts"]["cap"]
    assert P.tri_count(got["prims"]) <= budget


def test_a_pennant_costs_what_the_cap_assumes_it_costs():
    """The cap's arithmetic is only sound while a pennant really is
    `TRIS_PER_PENNANT` triangles -- add a part to one and the cap silently
    stops holding the budget."""
    one = PN._pennant("x", 0.0, 0.30, 0.26, 0.11, 0.0, 12.0, 0)
    assert P.tri_count(one) == PN.TRIS_PER_PENNANT, P.tri_count(one)


def test_overlapping_pennants_are_never_in_one_layer():
    """Neighbours overlap, so two in one plane would share it. They
    alternate between two layers, and `OVERLAP` under 0.5 is what stops a
    pennant reaching the SECOND one along -- which is in its own layer."""
    assert PN.OVERLAP < 0.5
    assert PN.LAYER_STEP > PN.FELT_T + PN.BAND_PROUD
    got = PN.plan(6.0, 0.1, 0.35, {}, 0, key="p", budget=_budget("pennant_row"))
    felts = [p for p in got["prims"] if p["part"].startswith("PennantRow_Felt")]
    ys = [round(min(v[1] for v in p["verts"]), 5) for p in felts]
    assert len(set(ys)) == 2, sorted(set(ys))
    assert ys[0] != ys[1] and ys[0] == ys[2]


def test_the_pennant_row_declares_no_collision():
    """A pennant hangs at ceiling height; a collider up there is a shape the
    navmesh bake carries for nothing. The GENOME has to say so too, or
    `validate` fails the module for a missing collision mesh -- which is how
    this was found."""
    assert genome.load_species("pennant_row").get("collision") is False
    got = PN.plan(6.0, 0.1, 0.35, {}, 0, key="p", budget=900)
    assert got["collision"] == []


# --- the play area -----------------------------------------------------------


def test_the_table_dresses_both_sides_facing_each_other():
    got = FF.plan_table(1.8, 0.76, 0.74, {"form": "cloth"}, 0)
    assert len(got["regions"]) == 2
    facings = sorted(round(r[5], 4) for r in got["regions"])
    assert abs(facings[0]) < 1e-9 and abs(facings[1] - 3.14159265) < 1e-4
    for r in got["regions"]:
        assert r[4] == 0.74, r


def test_the_cards_flavour_exists_and_the_hosts_offer_it():
    from zoo_keeper.recipes import _surface_stock as S
    assert "cards" in S.FLAVOURS and "cards" in S.GROUPS
    assert "cards" in S.AREA_PER_CLUSTER
    for host in ("desk", "table", "counter", "filing_cabinet", "folding_table"):
        assert "cards" in genome.load_species(host)["params"]["stock"], host


def test_a_playmat_fits_the_half_of_a_folding_table_it_has_to():
    """MEASURED, and it decided the mat's size: `_surface_stock` takes its
    own `EDGE` off each side of the region the host hands it, and the host's
    own inset comes off before that. A full 0.61 x 0.356 mat never fit on a
    0.76 m table and `_place_group` quietly drew card piles instead."""
    from zoo_keeper.recipes import _surface_stock as S
    got = FF.plan_table(1.8, 0.76, 0.74, {"form": "bare"}, 0)
    x0, x1, y0, y1, _z, _f, _c, _k = got["regions"][0]
    usable = (y1 - y0) - 2 * S.EDGE
    jitter = S.MAT_W * (min(S.MAX_JITTER_DEG, S.JITTER_K / S.MAT_W) * 3.14159 / 180.0)
    assert S.MAT_D + jitter <= usable, (S.MAT_D, jitter, usable)
    assert x1 - x0 > S.MAT_W


def test_the_chair_seat_is_a_height_somebody_can_sit_at():
    for (w, d, h) in _corners("folding_chair"):
        got = FF.plan_chair(w, d, h, {}, 0)
        assert 0.38 <= got["facts"]["seat_h_m"] <= 0.47, (w, d, h, got["facts"])


ALL = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
