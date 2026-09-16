"""The back bar (0.92.0): the lit wall unit behind a club's bar, the dense
bar top that goes with it, and the counter's bartender-side fit-out.

What is held here, and why each one is a rule and not a preference:

  * EXACT SLOT EXTENTS and ZERO COINCIDENT FACES, over a sweep of unit
    sizes, both forms and all four variants. The first plan measured 18
    coincident pairs on one size; every fix is a named constant in
    `back_bar_forms` and this is what keeps them honest.
  * AN ODD NUMBER OF BAYS, because the mirror and the porthole go in the
    CENTRE bay and an even run has no centre bay.
  * THE LIT MATERIALS ARE ``M_*_Face``, which is what Lux's emissive
    binder cuts with the room's power. A bulb that is not named this way
    stays on through a power cut.
  * EVERY PAINTED STRING IS INVENTED. `liquor_brands.DENYLIST` is a
    tripwire, not a trademark search, and it is held over the strings the
    art actually paints rather than over the table -- the two differ the
    moment somebody adds a word to the art.
  * THE DENSE TOP IS LANES: a speed rail on the SERVICE side (+Y), liquor
    behind the customer's reach, glass nearest them, nothing overhanging,
    nothing sharing a plane.
  * THE COUNTER'S FOOT RAIL IS INSIDE THE SLOT and its taps and register
    are not: the rail is part of the counter's silhouette, the taps stand
    above it the way surface stock does.
"""
from __future__ import annotations

import random

import pytest

from zoo_keeper.core import back_bar_art as ART
from zoo_keeper.core import back_bar_forms as F
from zoo_keeper.core import genome
from zoo_keeper.core import liquor_brands as LB
from zoo_keeper.core import prims as P
from zoo_keeper.recipes import _surface_stock as S

#: Unit sizes across the genome's range, including the extremes.
SIZES = [(1.6, 0.35, 1.8), (2.2, 0.40, 2.0), (2.8, 0.42, 2.35),
         (3.0, 0.50, 2.4), (3.4, 0.60, 2.9), (4.0, 0.45, 2.2),
         (4.6, 0.50, 2.6), (5.0, 0.65, 2.75), (5.5, 0.55, 2.55),
         (6.0, 0.75, 3.0)]
VARIANTS = (0, 1, 2, 3)


def _plan(size, form="auto", variant=0):
    return F.plan(size[0], size[1], size[2], form, variant, key="t%d" % variant)


# --- geometry ----------------------------------------------------------------


@pytest.mark.parametrize("size", SIZES, ids=lambda s: "x".join("%g" % v for v in s))
@pytest.mark.parametrize("form", F.FORMS)
def test_extents_are_exactly_the_slot(size, form):
    w, d, h = size
    for v in VARIANTS:
        lo, hi = P.bounds(_plan(size, form, v)["prims"])
        assert lo == pytest.approx((-w / 2, -d / 2, 0.0), abs=1e-6)
        assert hi == pytest.approx((w / 2, d / 2, h), abs=1e-6)


@pytest.mark.parametrize("size", SIZES, ids=lambda s: "x".join("%g" % v for v in s))
@pytest.mark.parametrize("form", F.FORMS)
def test_no_two_faces_share_a_plane(size, form):
    for v in VARIANTS:
        # 0.2 mm past the probe's window: a 2.0 mm gap passes here by float
        # and fails in Blender
        rows = P.coincident_pairs(_plan(size, form, v)["prims"], tol=0.0022)
        assert rows == [], (size, form, v, rows[:3])


@pytest.mark.parametrize("size", SIZES, ids=lambda s: "x".join("%g" % v for v in s))
def test_inside_the_triangle_budget(size):
    budget = genome.load_species("back_bar")["budgets"]["tris_lod0"]
    for form in F.FORMS:
        for v in VARIANTS:
            got = _plan(size, form, v)
            assert got["facts"]["tris"] <= budget, (size, form, v,
                                                    got["facts"]["tris"])


@pytest.mark.parametrize("size", SIZES, ids=lambda s: "x".join("%g" % v for v in s))
def test_an_odd_number_of_bays_so_there_is_a_centre_one(size):
    n, bay = F.bays(size[0])
    assert n % 2 == 1, (size, n)
    assert n * bay == pytest.approx(size[0])


def test_the_centre_bay_carries_the_mirror_or_the_porthole():
    for size in SIZES:
        straight = _plan(size, "straight")
        niche = _plan(size, "niche")
        assert any(p["part"] == "BackBar_Mirror" for p in straight["prims"]), size
        assert not any(p["part"].startswith("BackBar_Niche") for p in straight["prims"])
        assert any(p["part"] == "BackBar_NicheLamp" for p in niche["prims"]), size
        assert not any(p["part"] == "BackBar_Mirror" for p in niche["prims"])
        # one of each, not one a bay
        assert sum(1 for p in niche["prims"] if p["part"] == "BackBar_NicheLamp") == 1


def test_auto_takes_the_porthole_where_the_centre_bay_can_hold_one():
    forms = {_plan(s, "auto")["form"] for s in SIZES}
    assert forms <= set(F.FORMS)
    assert "niche" in forms, "auto never chose a porthole"


def test_bottles_are_sized_to_the_shelf_and_stay_under_it():
    """A pinned bottle height is through the shelf above at some unit
    height; the pitch decides the bottle, so nothing ever is."""
    for size in SIZES:
        got = _plan(size, "niche")
        pitch = got["facts"]["tier_pitch"]
        shelves = [p for p in got["prims"] if p["part"] == "BackBar_Shelf"]
        tops = sorted({round(P.bounds([p])[1][2], 4) for p in shelves})
        bottles = [p for p in got["prims"] if p["part"] == "BackBar_Bottle"]
        assert bottles and len(tops) == got["facts"]["tiers"]
        for z in tops[:-1]:
            above = min(t for t in tops if t > z + 1e-6)
            on_this = [p for p in bottles
                       if z - 0.01 <= P.bounds([p])[0][2] <= z + 0.01]
            for p in on_this:
                assert P.bounds([p])[1][2] < above, (size, pitch)


def test_the_same_inputs_give_the_same_unit():
    a = F.plan(3.0, 0.5, 2.4, "niche", 2, "abc")
    b = F.plan(3.0, 0.5, 2.4, "niche", 2, "abc")
    assert [p["verts"] for p in a["prims"]] == [p["verts"] for p in b["prims"]]
    assert a["brands"] == b["brands"]


def test_two_variants_stock_different_bottles():
    """`module_variants` is 4 and a variant is a different draw from the
    liquor table, so two bars in one building are not one bar twice."""
    assert genome.load_species("back_bar")["module_variants"] == 4
    seen = {tuple(_plan((3.0, 0.5, 2.4), "niche", v)["brands"]) for v in VARIANTS}
    assert len(seen) > 1


# --- what is lit -------------------------------------------------------------


def test_the_lit_materials_carry_the_face_suffix_lux_cuts():
    """`prim_mesh.build` reads a 4-tuple as emissive; the recipe names both
    of them ``M_BackBar_*_Face``, which is what Lux's binder keys on."""
    # READ THE FILE, do not import it: the recipe imports `bpy` at module
    # scope and this suite runs without Blender (`test_skins.py` says so
    # in its first line).
    import os
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "zoo_keeper", "recipes", "back_bar.py"),
              encoding="utf-8") as fh:
        src = fh.read()
    assert '"M_BackBar_bulb_Face"' in src
    # The porthole's name carries its raster's digest (0.94.0) -- it is a
    # backlit texture now, not a flat emissive colour -- so the contract
    # that survives is the SUFFIX, which is all the binder reads.
    assert '_Face"' in src
    assert 'make_backlit_material' in src
    assert '"emissive"' in src
    # and nothing ELSE in the unit is lit: a lit shelf is a lit shelf, not
    # a whole cabinet glowing
    mats = F.materials([0.3, 0.2, 0.1], "wood_stained")
    assert all(len(v) == 2 for v in mats.values())
    assert "bulb" not in mats and "niche_lit" not in mats


def test_the_porthole_is_a_diffuser_and_not_a_flat_lit_disc():
    """0.94.0. Walked on cold run 9060 at 4.15 m: the flat 0.74 m face came
    back at mean luma 200.8, 1.57% of it pinned at 250+, brightest pixels
    (250, 250, 250) -- white, with the tungsten gone. A raster with a core
    and a smooth falloff to zero at the rim is what a frosted lamp is."""
    from zoo_keeper.core import back_bar_art as ART
    art = ART.niche_art(F.NICHE_COLOUR)
    c = art["canvas"]
    n = ART.NICHE_PX
    assert (c.w, c.h) == (n, n)
    # the CORE is the colour, encoded to sRGB so it decodes back to the
    # linear value a glTF emissiveFactor used to carry
    assert c.get(n // 2, n // 2) == tuple(ART._srgb_byte(v) for v in F.NICHE_COLOUR)
    # ...and every channel of the core is warm, in that order
    r, g, b = c.get(n // 2, n // 2)
    assert r > g > b
    # THE RIM IS (all but) ZERO, which is what dissolves the polygon edge.
    # Not exactly zero: a pixel CENTRE sits half a pixel inside the rim, and
    # 3/255 is what the smoothstep leaves there -- under the preset's own
    # 24-level dither, so it is black on screen.
    assert max(c.get(n // 2, 0)) <= 6
    assert max(c.get(0, n // 2)) <= 6
    assert c.get(0, 0) == (0, 0, 0)           # off the inscribed circle
    # and it falls MONOTONICALLY from the core out along a radius
    row = [c.get(x, n // 2)[0] for x in range(n // 2, n)]
    assert row == sorted(row, reverse=True)
    assert row[0] == 255 and row[-1] <= 6
    # the same colour gives the same bytes and the same name, every build
    assert ART.niche_art(F.NICHE_COLOUR)["name"] == art["name"]
    assert ART.niche_art([1.0, 0.5, 0.2])["name"] != art["name"]


def test_the_lit_face_carries_uvs_onto_its_own_bounding_square():
    """The disc's uvs map the raster's inscribed circle onto it exactly, so
    the core lands at the centre and the falloff reaches zero at the edge of
    the geometry rather than somewhere inside it."""
    got = _plan((5.0, 0.5, 2.4), "niche")
    lit = [p for p in got["prims"] if p["mat"] == "niche_lit"]
    assert len(lit) == 1
    uvs = lit[0]["uvs"][0]
    assert len(uvs) == F.NICHE_SEGMENTS == len(lit[0]["verts"])
    # every corner sits on the unit circle in uv space, to the tolerance
    # `fit_exact`'s sub-percent rescale of the vertices leaves
    for u, v in uvs:
        assert abs(((u - 0.5) ** 2 + (v - 0.5) ** 2) ** 0.5 - 0.5) < 5e-3
        assert -1e-6 <= u <= 1.0 + 1e-6 and -1e-6 <= v <= 1.0 + 1e-6


def test_the_lit_strengths_stay_under_the_presets_clipping():
    """Both numbers came down in 0.94.0 and neither may drift back up
    without a frame to justify it: 1.6 flat and 2.0 on the bulbs both read
    as colourless white at the walker's station."""
    assert F.NICHE_STRENGTH < 1.6
    assert F.BULB_STRENGTH < 2.0
    assert F.NICHE_SEGMENTS >= 32


def test_every_bay_and_tier_has_a_bulb():
    for size in SIZES:
        got = _plan(size, "niche")
        assert got["facts"]["bulbs"] == got["facts"]["bays"] * got["facts"]["tiers"]


# --- the brands --------------------------------------------------------------


def test_every_painted_string_is_invented():
    """The denylist over what the ART paints, not over the table: the two
    differ the moment a word is added to the art."""
    for bid in LB.IDS:
        blob = " ".join(LB.painted_strings(bid)).upper()
        for bad in LB.DENYLIST:
            assert bad not in blob, (bid, bad)


def test_the_table_itself_is_clean_and_well_formed():
    assert len(LB.IDS) == len(set(LB.IDS)) == len(LB.BRANDS)
    for b in LB.BRANDS:
        up = LB.words(b).upper()
        for bad in LB.DENYLIST:
            assert bad not in up, (b["id"], bad)
        assert b["glass"] in F.GLASS, b["id"]
        assert b["proof"].isdigit()
        assert 1 <= len(b["logo"]) <= 3
        for line in b["logo"]:
            assert line == line.upper()


def test_the_labels_fit_their_cells():
    """`paint_label` refuses rather than truncating; a row whose slogan
    does not wrap into the space under the mark is a defect in the row."""
    for bid in LB.IDS:
        c = ART.paint_label(bid, 0)
        assert (c.w, c.h) == ART.LABEL_PX


def test_the_atlas_is_deterministic_and_names_itself_by_its_bytes():
    a = ART.label_atlas(LB.IDS[:6], key="x", variant=1)
    b = ART.label_atlas(LB.IDS[:6], key="x", variant=1)
    assert a["name"] == b["name"] and bytes(a["canvas"].buf) == bytes(b["canvas"].buf)
    c = ART.label_atlas(LB.IDS[:6], key="x", variant=2)
    assert c["name"] != a["name"], "variant did not change the wear"


def test_every_bottle_on_a_unit_has_a_label_in_the_atlas():
    got = _plan((4.0, 0.45, 2.2), "niche", 1)
    atlas = ART.label_atlas(got["brands"], key="k")
    resolved = F.resolve_uvs(got["prims"], atlas["rects"], atlas["size"])
    labels = [p for p in resolved if p["mat"] == "label"]
    assert len(labels) == got["facts"]["bottles"]
    for p in labels:
        for face in p["uvs"]:
            for u, v in face:
                assert 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0


def test_the_liquor_order_is_a_rotation_not_a_shuffle():
    for key in ("a", "b", "back_bar_delco_1997_01_w300"):
        got = LB.order(key)
        assert sorted(got) == sorted(LB.IDS)
        assert len(got) == len(LB.IDS)


# --- the dense bar top -------------------------------------------------------

DENSE_TOPS = [(-0.8, 0.8, -0.4, 0.4, 0.75), (-1.0, 1.0, -0.45, 0.45, 1.05),
              (-2.0, 2.0, -0.4, 0.4, 1.08), (-4.0, 4.0, -0.45, 0.45, 1.08),
              (-0.45, 0.45, -0.2, 0.25, 1.4)]


def _dense(top, seed, host=(0.55, 0.4, 0.26), keep=()):
    x0, x1, y0, y1, z0 = top
    return S.plan_surface(random.Random(seed), "bar_dense", x0, x1, y0, y1, z0,
                          host_rgb=list(host), keep_out=keep)


@pytest.mark.parametrize("top", DENSE_TOPS, ids=lambda t: "x".join("%g" % v for v in t[:4]))
def test_the_dense_top_overhangs_nothing_and_shares_no_plane(top):
    x0, x1, y0, y1, z0 = top
    for seed in range(4):
        got = _dense(top, seed)
        assert got["items"], (top, seed)
        for p in got["prims"]:
            for x, y, z in p["verts"]:
                assert x0 + S.EDGE - 1e-9 <= x <= x1 - S.EDGE + 1e-9, p["part"]
                assert y0 + S.EDGE - 1e-9 <= y <= y1 - S.EDGE + 1e-9, p["part"]
                assert z >= z0 - 0.02, p["part"]
        assert P.coincident_pairs(got["prims"], tol=0.0022) == []


def test_the_speed_rail_is_on_the_service_side():
    """+Y is the service side: a counter's top overhangs the customer
    side, so the spouted bottles stand on the +Y run and the glasses on
    the customer half."""
    top = (-2.0, 2.0, -0.4, 0.4, 1.08)
    got = _dense(top, 0)
    lanes = {}
    for it in got["items"]:
        ys = [y for _x, y in it["poly"]]
        lanes.setdefault(it["group"], []).append(sum(ys) / len(ys))
    assert "rail" in lanes and "glass" in lanes
    assert min(lanes["rail"]) > max(lanes["glass"])
    spouts = [p for p in got["prims"] if p["part"] == "Stock_Spout"]
    assert spouts, "the speed rail carries no pour spouts"


def test_the_dense_top_keeps_clear_of_a_register_station():
    top = (-2.0, 2.0, -0.4, 0.4, 1.08)
    keep = ((0.0, 0.0, S.__dict__.get("_REGISTER", 0.22)),)
    got = _dense(top, 0, keep=keep)
    kx, ky, kr = keep[0]
    box = P.rect_poly(kx, ky, 2 * kr, 2 * kr, 0.0)
    for it in got["items"]:
        assert P.poly_separated(it["poly"], box, 0.0), it["group"]


def test_the_dense_top_is_bounded_by_its_length():
    """Without the cap a 4 m bay drew 96 items; the pitch grows with the
    run so a long bar costs what a short one does."""
    short = _dense((-2.0, 2.0, -0.4, 0.4, 1.08), 0)
    long = _dense((-4.0, 4.0, -0.45, 0.45, 1.08), 0)
    assert len(long["items"]) <= S.DENSE_MAX_ITEMS
    assert len(short["items"]) <= S.DENSE_MAX_ITEMS
    assert P.tri_count(long["prims"]) < 2 * P.tri_count(short["prims"])


def test_the_dense_top_is_deterministic():
    a = _dense((-2.0, 2.0, -0.4, 0.4, 1.08), 7)
    b = _dense((-2.0, 2.0, -0.4, 0.4, 1.08), 7)
    assert [p["verts"] for p in a["prims"]] == [p["verts"] for p in b["prims"]]


def test_every_new_finish_contrasts_with_every_counter_style():
    """`_shelf_stock`'s number, the rule the whole module keeps: a body
    finish reads against the top it stands on."""
    g = genome.load_species("counter")
    tops = [[c * 0.85 for c in st["color"]] for st in g["styles"].values()]
    new = [k for k in S.FINISHES if k.startswith("lbl_")] + \
          ["liquor_amber", "liquor_clear", "liquor_green", "tumbler"]
    for key in new:
        if key in S.DETAIL_FINISHES:
            continue
        for host in tops:
            _idx, rgb = S.resolve_finish(key, host)
            assert S.contrast(rgb, host) >= 1.4, (key, host)


def test_every_host_offers_the_dense_flavour():
    for host in ("desk", "table", "counter", "filing_cabinet"):
        g = genome.load_species(host)
        assert "bar_dense" in g["params"]["stock"]


# --- the counter's bar fit-out -----------------------------------------------


def test_the_foot_rail_is_inside_the_slot_and_the_taps_are_above_it():
    w, d, h = 4.0, 0.8, 1.08
    inside, on_top = F.counter_fitout(w, d, h,
                                      {"ATT_register": (0.6, 0.0, h)}, w)
    lo, hi = P.bounds(inside)
    assert lo[0] >= -w / 2 - 1e-9 and hi[0] <= w / 2 + 1e-9
    assert lo[1] >= -d / 2 - 1e-9 and hi[1] <= d / 2 + 1e-9
    assert hi[2] <= h + 1e-9, "the foot rail stands above the counter's top"
    assert lo[2] >= -1e-9
    # the rail is on the CUSTOMER side (-Y) and below the knee
    rail = [p for p in inside if p["part"] == "Counter_FootRail"]
    assert rail
    rlo, rhi = P.bounds(rail)
    assert rhi[1] < 0.0, "the foot rail is on the service side"
    assert rhi[2] < 0.35
    # the taps and the register stand ON the top, service side
    tlo, thi = P.bounds(on_top)
    assert tlo[2] >= h - 0.01 and thi[2] > h
    for part in ("Counter_TapTower", "Counter_TapHandle", "Counter_Register"):
        got = [p for p in on_top if p["part"] == part]
        assert got, part
        assert P.bounds(got)[0][1] >= -1e-9, (part, "not on the service side")


def test_the_bar_fitout_shares_no_plane_with_itself():
    for (w, d, h) in ((3.0, 0.8, 1.08), (4.0, 0.8, 1.1), (5.0, 0.9, 1.05)):
        inside, on_top = F.counter_fitout(w, d, h,
                                          {"ATT_register": (0.4, 0.0, h)}, w)
        assert P.coincident_pairs(inside + on_top, tol=0.0022) == [], (w, d, h)


def test_the_counter_offers_the_bar_form_and_nothing_else_moved():
    g = genome.load_species("counter")
    assert g["params"]["form"] == ["auto", "straight", "bar"]
