"""The four flat-art species and the textured playmat: the arithmetic, the
budgets, the ladders and the rules 0.98.0 adds.

Every test here fails on 0.97.0, where none of `core/flat_art.py`,
`core/flat_forms.py` or the four genomes exists -- except the three that
measure things 0.97.0 DID ship and got differently, which say so in their
own docstrings: the playmat's two flat border slabs, `card_art.paint`'s
kind list, and `painted_strings`' contents.

WHY THE WINDOW IS 2.2 mm AND NOT 2.0: `tools/coplanar_probe.py` measures a
built scene at 2 mm and floats land ON that number, which 0.91.0 recorded
and `tests/test_card_shop.py` has used since. Same number here, same reason.

THE BUILT CLAIM IS NOT THIS FILE'S. Everything below is pure. The built
scene was measured by `tools/coplanar_census.py` on Blender 5.1.1,
2026-09-16 -- "12 builds, 0 with coincident pairs, 0 that did not build" --
and `tests/test_coincident_faces.py`'s `CENSUS_BUILDS` is where that run is
recorded.
"""
from __future__ import annotations

import itertools
import math

import pytest

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import flat_art as FA
from zoo_keeper.core import flat_forms as FF
from zoo_keeper.core import genome, kit
from zoo_keeper.core import pixel_type as pt
from zoo_keeper.core import prims as P
from zoo_keeper.recipes import _surface_stock as SS

TOL = 0.0022
SPECIES = ("poster", "hanging_banner", "ceiling_hanger", "aisle_sign")
PLANNERS = {"poster": FF.plan_poster, "hanging_banner": FF.plan_banner,
            "ceiling_hanger": FF.plan_hanger, "aisle_sign": FF.plan_aisle_sign}


def _corners(name):
    d = genome.load_species(name)["dimensions"]
    axes = [(d[k]["min"], d[k]["max"]) for k in ("width", "depth", "height")]
    out = [tuple(v) for v in itertools.product(*axes)]
    out.append(tuple(d[k]["default"] for k in ("width", "depth", "height")))
    return out


def _forms(name):
    f = (genome.load_species(name).get("params") or {}).get("form")
    return [x for x in f if x != "auto"] if isinstance(f, list) else [None]


def _cases(name):
    n = genome.load_species(name)["module_variants"]
    for (w, d, h) in _corners(name):
        for form in _forms(name):
            for v in range(n):
                yield w, d, h, ({"form": form} if form else {}), v


def _plan(name, w, d, h, params, variant):
    return PLANNERS[name](w, d, h, params, variant, key=f"{name}{w}{d}")


# --- the species exist --------------------------------------------------------


@pytest.mark.parametrize("name", SPECIES)
def test_the_species_is_discovered_and_validates(name):
    assert name in genome.list_species()
    assert genome.validate_genome(genome.load_species(name)) == []


@pytest.mark.parametrize("name", SPECIES)
def test_it_plans_through_the_kit_at_its_own_defaults(name):
    d = genome.load_species(name)["dimensions"]
    dims = [d[k]["default"] for k in ("width", "depth", "height")]
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": f"{name}_0", "role": "prop", "size_mod": "full",
        "style": 1, "species": name,
        "fit": {"dims": dims, "pivot": "center"}}]},
        theme="delco_1997", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == name


@pytest.mark.parametrize("name", SPECIES)
def test_it_is_reachable_by_its_own_name(name):
    """A species nothing can ask for is a species nobody will use.
    `test_species_by_name` holds the whole library to this; the two new
    hanging species FAILED it on the first genome -- `ceiling hanger` went
    to `ceiling` (a shorter keyword at the same start) and `aisle sign`
    matched nothing at all -- which is why every keyword list here carries
    both the underscored and the spaced spelling."""
    from zoo_keeper.core import intent
    assert intent.parse(name.replace("_", " ")).species == name


# --- the rules every interior species keeps ----------------------------------


@pytest.mark.parametrize("name", SPECIES)
def test_no_two_faces_share_a_plane_at_any_genome_corner(name):
    for w, d, h, params, v in _cases(name):
        got = _plan(name, w, d, h, params, v)
        rows = P.coincident_pairs(got["prims"], tol=TOL)
        assert rows == [], (name, w, d, h, params, v, rows[:3])


@pytest.mark.parametrize("name", SPECIES)
def test_the_built_plan_fills_the_slot_box_exactly(name):
    for w, d, h, params, v in _cases(name):
        got = _plan(name, w, d, h, params, v)
        lo, hi = P.bounds(got["prims"])
        for i, want in enumerate((w, d, h)):
            assert abs((hi[i] - lo[i]) - want) < 1e-6, (name, w, d, h, v, i)
        assert abs(lo[2]) < 1e-6, (name, w, d, h, lo)


@pytest.mark.parametrize("name", SPECIES)
def test_the_species_holds_its_triangle_budget_at_every_corner(name):
    budget = genome.load_species(name)["budgets"]["tris_lod0"]
    worst = 0
    for w, d, h, params, v in _cases(name):
        got = _plan(name, w, d, h, params, v)
        tris = P.tri_count(got["prims"])
        worst = max(worst, tris)
        assert tris <= budget, (name, w, d, h, v, tris, budget)
    assert worst >= budget * 0.25, (name, worst, budget)


@pytest.mark.parametrize("name", SPECIES)
def test_the_plan_is_deterministic(name):
    d = genome.load_species(name)["dimensions"]
    dims = [d[k]["default"] for k in ("width", "depth", "height")]
    a = _plan(name, dims[0], dims[1], dims[2], {}, 1)
    b = _plan(name, dims[0], dims[1], dims[2], {}, 1)
    assert [(p["part"], p["verts"]) for p in a["prims"]] == \
           [(p["part"], p["verts"]) for p in b["prims"]]
    assert a["tiles"] == b["tiles"]


@pytest.mark.parametrize("name", SPECIES)
def test_the_variants_are_different_modules(name):
    """`module_variants` on a species whose variants differ only in wear
    noise is one `kit.honour_dressing` refuses to carry. GEOMETRY, not just
    the tile: the first draft of the three non-poster species changed only
    which game the art came from, and three of four variants were the same
    mesh."""
    n = genome.load_species(name)["module_variants"]
    d = genome.load_species(name)["dimensions"]
    dims = [d[k]["default"] for k in ("width", "depth", "height")]
    shapes = set()
    for v in range(n):
        got = _plan(name, dims[0], dims[1], dims[2], {}, v)
        shapes.add(tuple(sorted((p["part"], tuple(p["verts"][0]))
                                for p in got["prims"])))
    assert len(shapes) == n, (name, n, len(shapes))


@pytest.mark.parametrize("name", SPECIES)
def test_nothing_in_the_flat_art_carries_a_collider(name):
    """All four hang above a body's reach, so a collider on one is a shape
    the navmesh bake carries for nothing -- `pennant_row`'s call, 0.95.0.
    The genome and the plan have to agree, or the recipe ships a collider
    the genome says is not there."""
    assert genome.load_species(name)["collision"] is False
    for w, d, h, params, v in _cases(name):
        assert _plan(name, w, d, h, params, v)["collision"] == []


# --- the poster's ladder ------------------------------------------------------


def test_the_posters_depth_ladder_clears_the_window_at_the_thinnest_slot():
    """The ladder is FRACTIONAL, so the worst case is the genome's minimum
    depth and there is exactly one place to check it."""
    d_min = genome.load_species("poster")["dimensions"]["depth"]["min"]
    planes = FF.poster_planes(d_min)
    assert len(set(round(v, 9) for v in planes.values())) == len(planes)
    rung = FF.min_rung_m(planes)
    assert rung >= TOL, (rung, planes)
    # ...and it is not extravagant: the ladder's own smallest step is what
    # sets it, so LADDER_MIN and the rung are the same claim
    assert math.isclose(rung, FF.LADDER_MIN * d_min)
    assert round(rung * 1000.0, 2) == 3.2


def test_the_ladders_rungs_are_the_order_the_reference_describes():
    """Front to back: the frame's face, then the mat, then the art, then the
    plate it is printed on. A mat BEHIND the art would be a border painted
    into the texture, which is what the reference says a mat is not."""
    p = FF.poster_planes(0.04)
    assert p["frame_front"] < p["mat_front"] < p["art"] < p["plate_front"]
    assert p["plate_front"] < p["mat_back"] < p["back"]


def test_the_frame_ring_is_one_mesh_and_every_face_points_outward():
    """FOUR BOXES CANNOT BE MADE TO WORK -- they share the ring's own outer
    silhouette wherever they overlap and butt wherever they do not, and the
    first draft measured 8 pairs per poster at 0.00 mm. One mesh has none.
    Its winding is hand-written, so it is measured and not trusted: a ring
    with an inverted face is a hole in the wall."""
    prims = []
    FF._ring(prims, "R", "m", 1.0, 0.8, 0.1, -0.02, 0.02)
    assert len(prims) == 1 and len(prims[0]["faces"]) == 16
    assert P.tri_count(prims) == 32
    assert P.coincident_pairs(prims, tol=TOL) == []
    for f in prims[0]["faces"]:
        v = [prims[0]["verts"][i] for i in f]
        n = P._cross(P._sub(v[1], v[0]), P._sub(v[2], v[0]))
        ln = math.sqrt(P._dot(n, n))
        n = tuple(c / ln for c in n)
        c = tuple(sum(q[k] for q in v) / len(v) for k in range(3))
        q = tuple(c[k] + n[k] * 0.001 for k in range(3))
        in_solid = (abs(q[1]) < 0.02
                    and max(abs(q[0]) / 0.5, abs(q[2]) / 0.4) <= 1.0
                    and max(abs(q[0]) / 0.4, abs(q[2]) / 0.3) >= 1.0)
        assert not in_solid, (f, n, c)


def test_a_framed_poster_is_three_rectangles_and_a_bare_one_is_not():
    """The fourth reference: 'a framed poster is three rectangles -- frame,
    mat, plate -- not one quad with a border painted into the texture'. And
    the bare form does not pay for the two it does not have."""
    framed = FF.plan_poster(0.6, 0.04, 0.9, {"form": "framed"}, 0, key="p")
    bare = FF.plan_poster(0.6, 0.04, 0.9, {"form": "bare"}, 0, key="p")
    parts = {p["part"] for p in framed["prims"]}
    assert {"Poster_Frame", "Poster_Mat", "Poster_Plate"} <= parts
    assert {p["part"] for p in bare["prims"]} == {"Poster_Plate", "Poster_Art"}
    assert framed["facts"]["tris"] == 78 and bare["facts"]["tris"] == 14
    # the mat and the frame cost 64 of the 78, which is the figure the
    # release note quotes for what the framed look buys
    assert framed["facts"]["tris"] - bare["facts"]["tris"] == 64


def test_a_tilted_poster_lands_on_its_slot_rather_than_being_squeezed():
    """`fit_exact` maps each axis independently, so squeezing a rotated
    rectangle SHEARS it. `_tilt_fit` solves for the un-rotated size whose
    rotated bounds are the slot, so nothing is squeezed and the corners
    stay square."""
    for w, h in ((0.6, 0.9), (1.4, 0.5), (0.4, 1.8)):
        for deg in FF.TILTS:
            got = FF._tilt_fit(w, h, deg)
            if got is None:
                continue
            a, b = got
            t = math.radians(abs(deg))
            c, s = math.cos(t), math.sin(t)
            assert math.isclose(a * c + b * s, w, abs_tol=1e-9)
            assert math.isclose(a * s + b * c, h, abs_tol=1e-9)
    # ...and a tilt the slot cannot hold is refused rather than shipped
    assert FF._tilt_fit(0.4, 1.8, 44.0) is None


def test_the_tilted_form_is_actually_turned():
    """A `tilted` poster whose plate is axis-aligned is a `bare` one with a
    different name."""
    got = FF.plan_poster(0.6, 0.04, 0.9, {"form": "tilted"}, 0, key="p")
    assert abs(got["facts"]["tilt_deg"]) >= 2.0
    plate = [p for p in got["prims"] if p["part"] == "Poster_Plate"][0]
    zs = {round(v[2], 6) for v in plate["verts"]}
    assert len(zs) > 2, "the plate is still axis-aligned in z"


# --- what hangs, and from what -----------------------------------------------


def test_the_hanging_species_top_out_at_the_contracts_headroom():
    """DERIVED, NOT CHOSEN. `deli_counter/agent_contract.json`
    clearances.min_headroom_m is 2.0; `level_design._clear_height` takes the
    storey less the thicker slab less `_CEILING_AIR`, and the piece's own
    `under` spends that air again. At the library's shortest storey the drop
    left over is 0.60 m, and that is the two genomes' `height.max`."""
    assert FF.MIN_HEADROOM == 2.0
    assert FF.hang_max_height() == 0.6
    assert math.isclose(FF.hang_max_height(),
                        FF.SHORT_STOREY - FF.SLAB_CAP
                        - 2.0 * FF.CEILING_AIR - FF.MIN_HEADROOM)
    for name in ("ceiling_hanger", "aisle_sign"):
        g = genome.load_species(name)
        assert g["dimensions"]["height"]["max"] == FF.hang_max_height(), name
    # a taller storey buys drop, and a thicker slab spends it -- which is
    # why this is a genome cap and not a guarantee
    assert FF.hang_max_height(story=3.4) == 1.0
    assert FF.hang_max_height(cap=0.5) == 0.4


@pytest.mark.parametrize("name", ("ceiling_hanger", "aisle_sign"))
def test_the_chain_starts_at_the_top_of_the_slot_box(name):
    """THE HANGING POINT, and the whole answer to 'what does it hang from'.
    There is no ceiling-grid geometry and the light pipeline's `hang` mount
    is for lamps; the point that exists is `level_design._piece`'s `under`,
    so Zoo's side of the contract is that the TOP of the slot box is the
    ceiling plane. A chain that stops short of it hangs from nothing."""
    for w, d, h, params, v in _cases(name):
        got = _plan(name, w, d, h, params, v)
        chain = [p for p in got["prims"] if "_0_" in p["part"]
                 or "_1_" in p["part"]]
        assert chain, (name, w, d, h, v)
        top = max(v2[2] for p in chain for v2 in p["verts"])
        assert abs(top - h) < 1e-6, (name, w, d, h, top)


@pytest.mark.parametrize("name", ("ceiling_hanger", "aisle_sign"))
def test_a_hung_board_is_printed_both_sides_from_one_tile(name):
    """A hanging sign is printed both sides, and a second tile is atlas
    spent on a difference nobody can see from either side. Two quads, one
    tile, and the back one has its U mirrored so it reads the right way
    round."""
    got = _plan(name, 1.0, 0.06, 0.5, {}, 0)
    quads = [p for p in got["prims"] if p.get("tile")]
    assert len(quads) == 2 and len(got["tiles"]) == 1
    assert {q["tile"] for q in quads} == set(got["tiles"])
    us = [tuple(c[0] for c in q["uvs"][0]) for q in quads]
    assert us[0] != us[1] and sorted(us[0]) == sorted(us[1])


def test_an_aisle_sign_says_something_from_the_invented_table():
    for v in range(genome.load_species("aisle_sign")["module_variants"]):
        got = FF.plan_aisle_sign(1.1, 0.05, 0.4, {}, v, key="a")
        assert got["facts"]["says"] in CB.AISLE_SAYS
    # ...and an explicit one is honoured, so a room can name its own aisle
    got = FF.plan_aisle_sign(1.1, 0.05, 0.4, {"says": "SEALED BOXES"}, 0)
    assert got["facts"]["says"] == "SEALED BOXES"


# --- the art ------------------------------------------------------------------


def test_the_two_kind_tuples_are_the_same_tuple():
    """`card_art.FLAT_KINDS` is a literal copy of `flat_art.KINDS`, because
    importing that module at card_art's scope is the cycle. A copy that
    drifts is a kind the one dispatcher does not route.

    FAILS ON 0.97.0: `card_art` has no `FLAT_KINDS`."""
    assert CA.FLAT_KINDS == FA.KINDS


def test_every_flat_kind_paints_and_fills_its_box():
    specs = [
        {"kind": "poster", "game": "hexes_and_hoagies", "maker": "pike_press",
         "w_m": 0.5, "h_m": 0.8, "key": "k"},
        {"kind": "banner", "game": "jawn_beasts", "w_m": 1.6, "h_m": 0.5,
         "key": "k"},
        {"kind": "hanger", "game": "blue_route_2099", "w_m": 0.7, "h_m": 0.35,
         "key": "k"},
        {"kind": "aisle", "says": CB.AISLE_SAYS[0], "w_m": 1.0, "h_m": 0.3,
         "key": "k"},
        {"kind": "playmat", "game": "nanas_grimoire", "w_m": 0.55, "h_m": 0.26,
         "key": "k"},
    ]
    # The painted kinds carry a gradient and a creature; the aisle sign is
    # board, rule and marker and is SUPPOSED to be three colours -- a
    # hand-lettered section sign that needed six would be a poster. Said
    # here rather than loosening one number for all five.
    want = {"poster": 8, "banner": 8, "hanger": 8, "playmat": 8, "aisle": 3}
    for spec in specs:
        c = CA.paint(spec)
        assert c.w == int(round(spec["w_m"] * CA.TEXEL)), spec
        assert c.h == int(round(spec["h_m"] * CA.TEXEL)), spec
        assert len({c.get(x, y) for y in range(c.h)
                    for x in range(0, c.w, 3)}) >= want[spec["kind"]], spec
    with pytest.raises(ValueError):
        CA.paint({"kind": "napkin", "w_m": 0.1, "h_m": 0.1})


def test_the_posters_title_is_at_the_top_and_the_makers_mark_at_the_bottom():
    """THE FOURTH REFERENCE'S ONE CORRECTION, and the reason this test is
    a pixel measurement rather than a reading of the source: the first three
    poster references read as a title block along the BOTTOM, the brief said
    bottom, and the walker's framed magazine cover settles it the other way
    -- 'THE TITLE IS AT THE TOP, in an ornate fantasy serif, over the art
    rather than under it; the only thing at the bottom is a small publisher
    mark in a corner.'

    Measured by painting the same plate twice with the title's ink removed
    and again with the maker's, and asking WHERE the pixels moved.
    """
    game = dict(CB.BY_ID["hexes_and_hoagies"])
    maker = CB.MAKERS[0]
    w, h = 160, 240
    full = FA.poster_plate(game, w, h, "k", maker)
    no_title = FA.poster_plate(dict(game, name=" "), w, h, "k", maker)
    rows = [y for y in range(h) for x in range(w)
            if full.get(x, y) != no_title.get(x, y)]
    assert rows, "the title painted nothing"
    assert max(rows) < h * 0.30, (min(rows), max(rows))

    no_mark = FA.poster_plate(game, w, h, "k", dict(maker, short=" "))
    marks = [(x, y) for y in range(h) for x in range(w)
             if full.get(x, y) != no_mark.get(x, y)]
    assert marks, "the maker's mark painted nothing"
    assert min(y for _x, y in marks) > h * 0.85, marks[:4]
    assert min(x for x, _y in marks) > w * 0.50, marks[:4]
    # ...and the mark is SMALL: the title's ink is the bigger of the two
    assert len(marks) * 3 < len(rows)


def test_the_serif_widens_the_stems_ends_and_nothing_else():
    """The factory has one typeface and it is a sans. `_serif` is the drawn
    substitute: the top and bottom row of every stem widened by a pixel.
    What a minted serif face would buy is in the release note; what this
    buys is that a title is not a price sign."""
    m = pt.trim(pt.render("I", 2))
    s = FA._serif(m)
    assert len(s) == len(m) and len(s[0]) == len(m[0]) + 2
    assert sum(s[0]) > sum(m[0]) and sum(s[-1]) > sum(m[-1])
    mid = len(m) // 2
    assert sum(s[mid]) == sum(m[mid])
    assert FA._serif([bytearray(3)]) == [bytearray(3)]


def test_the_reading_arithmetic_is_what_the_release_note_says():
    """'Reads as art at 3 m and as a coloured rectangle at 10 m' is the
    brief's own gate, and it is arithmetic about a display, not a taste. One
    metre subtends 519 screen px at 3 m and 157 at 10 m on the target
    assumed in `flat_art`; at `TEXEL` a poster is magnified about 2:1 at
    three metres, which is the house's 4 mm pixel, and minified 3.3:1 at
    ten, which is the coloured rectangle."""
    near = FA.reads_at(1.0, 3.0)
    far = FA.reads_at(1.0, 10.0)
    assert round(near[0]) == 519 and round(far[0]) == 157
    assert round(near[2], 2) == 2.03 and round(1.0 / far[2], 2) == 1.63
    # a 0.6 m poster is 313 screen px at 3 m and 94 at 10 m
    assert round(FA.reads_at(0.6, 3.0)[0]) == 313
    assert round(FA.reads_at(0.6, 10.0)[0]) == 94
    # 512 px/m is where a poster is 1:1 at three metres -- what the
    # expensive version would have bought, priced in the release note
    assert round(FA.reads_at(1.0, 3.0, texel=512)[2], 2) == 1.01


def test_the_atlas_is_one_image_per_module_and_named_from_its_pixels():
    got = FF.plan_poster(0.6, 0.04, 0.9, {"form": "framed"}, 0, key="p")
    a = CA.build_atlas(got["tiles"], "Poster")
    b = CA.build_atlas(got["tiles"], "Poster")
    assert a["name"] == b["name"]
    assert bytes(a["canvas"].buf) == bytes(b["canvas"].buf)
    png, raw = FA.atlas_bytes(a)
    assert png > 0 and raw == a["size"][0] * a["size"][1] * 3
    # ONE RECT PER QUAD AND ONE ATLAS PER MODULE: a poster is one tile, so
    # its material is one and its draw is one
    assert len(a["rects"]) == 1
    # a different game in the same slot is a different image, which is what
    # lets two identical posters share one
    other = FF.plan_poster(0.6, 0.04, 0.9, {"form": "framed"}, 1, key="q")
    assert CA.build_atlas(other["tiles"], "Poster")["name"] != a["name"]


# --- the denylist -------------------------------------------------------------


def test_the_aisle_words_are_held_by_the_same_guard_as_everything_else():
    """`painted_strings` is ONE list on purpose: the denylist test walks it,
    and a new painted string that is not in it is a string nothing checks.
    `AISLE_SAYS` is new in 0.98.0 and is lettered on every aisle sign.

    FAILS ON 0.97.0: `card_brands` has no `AISLE_SAYS` and
    `painted_strings` has no `aisle` argument."""
    strings = CA.painted_strings()
    for s in CB.AISLE_SAYS:
        assert s in strings, s
    import re
    for s in CB.AISLE_SAYS:
        toks = set(re.findall(r"[A-Z0-9']+", s.upper()))
        assert not (toks & set(CB.DENY_WORDS)), s
        assert not any(p in s.upper() for p in CB.DENY_PARTS), s
        for ch in s:
            assert ch in pt.GLYPHS, (s, ch)


def test_the_aisle_words_are_read_across_a_room_and_the_shop_words_are_not():
    """Two tables and not one. `SHOP_SAYS` is what a 0.15 m storage-box end
    carries and wraps to three lines; an aisle sign is read over somebody's
    head. The first draft used one list and 'NO TRADES WITHOUT A GROWN-UP'
    became an aisle header."""
    assert set(CB.AISLE_SAYS) & set(CB.SHOP_SAYS) == set()
    assert max(len(s) for s in CB.AISLE_SAYS) < max(len(s) for s in CB.SHOP_SAYS)


def test_an_aisle_sign_at_ship_size_is_actually_legible():
    """The one tile in this set whose lettering HAS to resolve: a sign
    nobody can read over an aisle is a coloured rectangle with a chain on
    it. Measured by finding the marker ink, not by trusting `_stamp`."""
    for says in CB.AISLE_SAYS:
        c = FA.aisle_letters(says, int(1.1 * CA.TEXEL), int(0.3 * CA.TEXEL), "k")
        ink = sum(1 for y in range(c.h) for x in range(c.w)
                  if c.get(x, y) == CA.MARKER)
        assert ink > 200, (says, ink)


# --- the textured playmat (finding 5) -----------------------------------------


def test_the_cards_flavour_now_plans_a_tile_and_no_other_flavour_does():
    """FINDING 5. `_surface_stock`'s own 0.95.0 docstring records the gap --
    'NOT TEXTURED, and that is a limit rather than a choice:
    `prim_mesh.build_stock` has no textured path'. This is that path, and
    the thing worth holding is that it changed NOTHING for the other six
    flavours: an empty `tiles` means the atlas is never built and the
    "card_art" stream is never drawn from."""
    import random
    seen = {}
    for flavour in SS.FLAVOURS:
        tiles = {}
        for seed in range(12):
            got = SS.plan_surface(random.Random(seed), flavour,
                                  -0.9, 0.9, -0.38, 0.38, 0.74,
                                  host_rgb=[0.3, 0.3, 0.3], clear=1.6)
            tiles.update(got.get("tiles") or {})
        seen[flavour] = tiles
    assert seen["cards"], "no playmat tile in twelve seeds of the card table"
    for flavour in SS.FLAVOURS:
        if flavour != "cards":
            assert seen[flavour] == {}, flavour
    for key, spec in seen["cards"].items():
        assert spec["kind"] == "playmat" and spec["game"] in CB.IDS
        assert key == f"playmat_{spec['game']}"
        CA.paint(spec)          # it has to actually paint


def test_the_playmats_printed_border_is_in_the_print_now():
    """0.95.0 stood two flat slabs (`Stock_MatEdge*`) in for a printed
    border because there was no textured path. The border is in the texture
    now, which is 24 triangles back per mat and where a real one is.

    FAILS ON 0.97.0, where `_playmat` emits the two slabs and no quad."""
    import random
    prims = SS._playmat(random.Random(7))
    parts = [p["part"] for p in prims]
    assert "Stock_MatPrint" in parts
    assert not any(p.startswith("Stock_MatEdge") for p in parts)
    q = [p for p in prims if p["part"] == "Stock_MatPrint"][0]
    assert q["tile"] and q["tile_spec"]["kind"] == "playmat"
    assert P.tri_count(prims) == 14          # the mat's 12 plus the quad's 2


def test_the_printed_face_floats_clear_of_the_mat_it_is_printed_on():
    """This module's own rule: nothing shares a plane, and no face sits
    between the host's top and `SINK` + 4 mm above it."""
    import random
    prims = SS._playmat(random.Random(3))
    assert P.coincident_pairs(prims, tol=TOL) == []
    q = [p for p in prims if p["part"] == "Stock_MatPrint"][0]
    z = q["verts"][0][2]
    assert z - SS.MAT_T >= TOL
    assert z - SS.SINK > SS.SINK + 0.004


def test_the_mat_print_survives_being_placed():
    """The quad is turned and translated by `_place_group` like any item,
    and `P.rotate_z` copies the dict -- so `tile`, `uvs` and `tile_spec`
    have to come out the other side or the atlas never hears about it."""
    import random
    rng = random.Random(11)
    for _ in range(40):
        got = SS.plan_surface(rng, "cards", -1.2, 1.2, -0.38, 0.38, 0.74,
                              host_rgb=[0.28, 0.26, 0.24], clear=1.6)
        quads = [p for p in got["prims"] if p.get("tile")]
        if quads:
            for q in quads:
                assert q["uvs"] and len(q["verts"]) == 4
                assert q["tile"] in got["tiles"]
            return
    pytest.fail("forty seeds and no playmat placed")


ALL = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
