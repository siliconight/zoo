"""cash_register, Zoo 1.0.0: a 1997 till whose customer display is lit.

The decisions are pure (`core/register_forms.py`, `core/pixel_type.py`) and
tested here without Blender: the shape at every genome corner, the triangle
budget, exact fit, no shared plane, the type on both displays, and that every
painted string is a number or the word TOTAL. The built module -- the parts,
the fit, the emissive material, the ABSENCE of any light, the same GLB every
build -- is the bpy half at the bottom, skipped without Blender.

WHAT THIS REPLACES, and the assertion that pins it: `display_case_forms`
draws a till of four boxes on every showcase counter, and that is what the
walker photographed on cold run 9062. It still does, because `params.till`
defaults to 1 and a placer that has not learned to stand a `cash_register`
should not lose its shape -- `test_the_case_still_stands_its_own_till_by_default`
holds that, and `test_the_case_drops_its_till_when_asked` is the seam Deli
Counter needs. Both fail on 0.99.0, where the parameter does not exist.
"""
from __future__ import annotations

import itertools
import json
import os
import re
import struct

import pytest

from zoo_keeper import SEED_EPOCH
from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import display_case_forms as DF
from zoo_keeper.core import dna, genome, intent, kit, pixel_type as pt
from zoo_keeper.core import prims as P
from zoo_keeper.core import register_forms as RF
from zoo_keeper.core import seeding

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "cash_register.py")
_GENOME = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "cash_register.json")

#: The genome's corners, all 27 of them: a budget held at the default is not
#: a budget, and the display's type scale is decided by the slot.
DIMS = ((0.32, 0.40, 0.52), (0.34, 0.42, 0.52), (0.38, 0.46, 0.56))
CORNERS = list(itertools.product(*DIMS))
DEFAULT = (0.40, 0.42, 0.46)
#: What it actually builds, measured. Every corner, every price: one number,
#: because every part is a box or a fixed-segment cylinder and no primitive
#: asks for a bevel.
TRIS = 134
#: The digits' scale in `pixel_type`. 2 everywhere is the walker's whole
#: question about this species -- at scale 1 the green type is 17.6 mm on the
#: display instead of 35.2 and stops reading across a shop.
MIN_SCALE = 2
#: The atlas, decoded to RGB8 on a client's GPU. The worst corner measured at
#: 65.5 KiB; the cap is round and above it, and it is the figure that is
#: actually spent on every machine in a session.
ATLAS_KIB_MAX = 96


def _slot(w, d, h, style=4, variant=0):
    s = {"slot_id": "till_0", "role": "prop", "size_mod": "full", "style": style,
         "species": "cash_register", "material": "plastic",
         "fit": {"dims": [w, d, h], "pivot": "center", "collision": "convex"}}
    if variant:
        s["variant"] = variant
    return s


def _kit(w, d, h, style=4, variant=0):
    return kit.plan_kit({"building_id": "t", "slots": [_slot(w, d, h, style, variant)]},
                        theme="delco_1997", style=style)


def _module_plan(dims=DEFAULT, style=4, variant=0):
    mod = _kit(*dims, style=style, variant=variant)["modules"][0]
    return mod, dna.resolve_module_plan(mod, genome.load_species("cash_register"),
                                        "delco_1997", style, "1.0.0")


def _streams(stem):
    return seeding.RNGStreams(seeding.root_key(stem, "cash_register", 0, SEED_EPOCH))


# --- the species exists and is addressable ------------------------------------------


def test_the_species_is_discovered_and_validates():
    assert "cash_register" in genome.list_species()
    assert genome.validate_genome(genome.load_species("cash_register")) == []


def test_it_plans_at_its_authored_dims():
    plan = _kit(*DEFAULT)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "cash_register"


def test_a_cash_register_is_not_an_atm():
    """`atm` claimed the keyword "cash register" and won the prompt for it --
    measured on 0.99.0, where `intent.parse("cash register")` returned `atm`.
    An ATM is not a cash register; the keyword is off the ATM now."""
    assert intent.parse("cash register").species == "cash_register"
    assert intent.parse("register").species == "cash_register"
    assert intent.parse("till").species == "cash_register"
    for q in ("atm", "cash machine", "cashpoint"):
        assert intent.parse(q).species == "atm", q


def test_no_keyword_this_species_added_was_taken_from_another():
    """The sweep, because a new keyword set is the one thing that can
    redress a level silently (`test_species_by_name`'s own argument). The
    four that resolve elsewhere are deliberate shared words and predate
    this species; a fifth is a collision."""
    taken = [(sp, kw) for sp in genome.list_species()
             for kw in genome.load_species(sp).get("keywords", [])
             if intent.parse(kw).species != sp]
    assert sorted(taken) == [("pebble", "surface dressing"),
                             ("rubble_frag", "surface dressing"),
                             ("shelving", "gondola"),
                             ("weed_tuft", "surface dressing")]


# --- the shape ----------------------------------------------------------------------


@pytest.mark.parametrize("dims", CORNERS, ids=lambda d: "x".join(str(v) for v in d))
def test_it_is_exactly_its_slot_on_every_axis(dims):
    w, d, h = dims
    got = RF.plan(w, d, h, key="fit")
    lo, hi = RF.extents(got)
    assert lo == pytest.approx((-w / 2, -d / 2, -h / 2), abs=1e-12)
    assert hi == pytest.approx((w / 2, d / 2, h / 2), abs=1e-12)


@pytest.mark.parametrize("dims", CORNERS, ids=lambda d: "x".join(str(v) for v in d))
def test_the_triangle_count_is_the_same_at_every_corner_and_inside_budget(dims):
    got = RF.plan(*dims, key="tris")
    assert RF.triangles(got) == TRIS
    assert TRIS <= RF.TRI_BUDGET


def test_the_budget_in_the_genome_is_the_budget_in_the_planner():
    """A budget written down twice is two budgets. `tools/preview_specimen`
    and `bpylayer.validate` read the genome's; every test here reads the
    planner's."""
    g = json.load(open(_GENOME, encoding="utf-8"))
    assert g["budgets"]["tris_lod0"] == RF.TRI_BUDGET


def test_it_is_in_the_company_the_budget_was_set_against():
    """The budget was set before the layout was drawn, against the props
    this ships beside. Read off their genomes so the comparison cannot rot."""
    def budget(sp):
        return json.load(open(os.path.join(os.path.dirname(_GENOME), sp + ".json"),
                              encoding="utf-8"))["budgets"]["tris_lod0"]
    assert RF.TRI_BUDGET <= budget("crt_tv")
    assert RF.TRI_BUDGET <= budget("vending_machine")
    assert TRIS < budget("vending_machine")


def test_nothing_asks_for_a_bevel():
    """Bevel adds triangles after the count above is taken. Every style in
    the genome sets 0 and no primitive flags one, so the built module ships
    what `triangles` counted."""
    got = RF.plan(*DEFAULT, key="bevel")
    assert not [p for p in got["prims"] if p.get("bevel")]
    g = json.load(open(_GENOME, encoding="utf-8"))
    for name, style in g["styles"].items():
        assert style["bevel"] == 0.0, name


@pytest.mark.parametrize("dims", CORNERS, ids=lambda d: "x".join(str(v) for v in d))
def test_no_two_faces_share_a_plane_at_any_corner_or_price(dims):
    """`prims.coincident_pairs` at `tools/coplanar_probe.py`'s own defaults,
    so zero here is the claim that zero prints there.

    THE THREE THIS FOUND, kept because each was a real overlap and not a
    tolerance: the keypad island ran the full depth of the top and shared its
    base plane with the pole stem (5.7 cm2), the keypad's side plane sat
    1.6 mm from the operator bezel's, and the receipt was modelled at the
    1.6 mm a receipt is -- its own two faces inside the 2 mm window."""
    for price in RF.PRICES:
        got = RF.plan(*dims, price=price, key=f"{dims}{price}")
        assert P.coincident_pairs(got["prims"]) == [], (dims, price)


def test_the_collision_box_is_the_slot_and_nothing_stands_outside_it():
    for dims in CORNERS:
        got = RF.plan(*dims, key="col")
        (lo, hi), = got["collision"]
        elo, ehi = RF.extents(got)
        assert lo == pytest.approx(elo, abs=1e-12)
        assert hi == pytest.approx(ehi, abs=1e-12)


def test_the_parts_are_the_genome_s_parts():
    got = RF.plan(*DEFAULT, key="parts")
    built = {p["part"] for p in got["prims"] if not p.get("tile")}
    built |= {"Register_Screen", "Register_Art"}      # the two art objects
    assert built == set(json.load(open(_GENOME, encoding="utf-8"))["parts"])


def test_a_slot_too_small_for_the_shape_refuses_rather_than_building_one():
    for bad in ((0.10, 0.42, 0.46), (0.40, 0.14, 0.46), (0.40, 0.42, 0.10)):
        with pytest.raises(ValueError):
            RF.layout(*bad)


# --- the display, which is the point ------------------------------------------------


@pytest.mark.parametrize("dims", CORNERS, ids=lambda d: "x".join(str(v) for v in d))
def test_the_green_type_sets_at_scale_two_at_every_corner(dims):
    """THE RULE THE WALKER ASKED FOR. `POLE_BEZEL_F` was 0.46 and the
    shortest slot in the genome gave a 28 px window against the 26 px a
    scale-2 line needs plus its margins -- one pixel short, and the display
    halved its digits for it. This is what stops that being spent again."""
    for price in RF.PRICES:
        f = RF.plan(*dims, price=price, key="type")["facts"]
        assert f["digit_scale"] >= MIN_SCALE, (dims, price, f)
        assert f["digit_h_m"] >= 0.030, (dims, price, f)


def test_the_two_displays_read_the_same_number():
    """`digits_layout` may drop a leading digit to keep the pole at scale 2.
    A pole reading 4.99 over a panel reading 24.99 is a defect a player can
    see, and the first draft had it."""
    for dims in CORNERS:
        for price in RF.PRICES:
            f = RF.plan(*dims, price=price, key="agree")["facts"]
            assert f["lcd_lines"][-1] == f["digits"], (dims, price, f)


def test_the_screen_is_the_only_lit_surface():
    got = RF.plan(*DEFAULT, key="lit")
    lit = [p for p in got["prims"] if p.get("lit")]
    assert [p["part"] for p in lit] == ["Register_Screen"]
    assert lit[0]["tile"] == "screen"


def test_the_screen_faces_the_customer():
    """-Y is the customer side. A quad wound the other way is a display that
    only the wall can read, and nothing else in the module would say so."""
    got = RF.plan(*DEFAULT, key="face")
    quad, = [p for p in got["prims"] if p.get("lit")]
    (a, b, c) = P.triangles(quad)[0]
    n = P._cross(P._sub(b, a), P._sub(c, a))
    assert n[1] < 0 and abs(n[0]) < 1e-12 and abs(n[2]) < 1e-12, n


def test_the_face_up_art_is_wound_so_the_clerk_can_read_it():
    """The operator stands at +Y and looks along -Y: "up" in the image is the
    -Y edge and "right" is -X. `_UV` puts vertex 0 at the tile's bottom-left,
    so vertex 0 must be the (+X, +Y) corner.

    THE FIRST DRAFT WOUND IT FROM (-X, -Y) and the panel rendered TOTAL 24.99
    upside down and mirrored -- both axes backwards, which is a 180 degree
    rotation and is invisible to every other check in this file. It was
    caught by looking at a frame, which is the point of rendering one."""
    quad = RF._top_art(0.0, 0.0, 0.2, 0.1, 1.0)
    assert quad[0] == (0.1, 0.05, 1.0)
    (a, b, c) = P.triangles({"verts": quad, "faces": [(0, 1, 2, 3)]})[0]
    n = P._cross(P._sub(b, a), P._sub(c, a))
    assert n[2] > 0 and abs(n[0]) < 1e-12 and abs(n[1]) < 1e-12, n
    got = RF.plan(*DEFAULT, key="wind")
    for part in ("Register_Keys", "Register_OpLcd"):
        q, = [p for p in got["prims"] if p["part"] == part]
        v = q["verts"]
        assert v[0][0] == max(p[0] for p in v), part
        assert v[0][1] == max(p[1] for p in v), part


def test_the_digits_are_the_factory_s_own_typeface():
    """`pixel_type`, which is Pixelcoat's Pixel Operator Bold -- the face
    `card_art`'s letterer sets every card-shop sign in and the one
    `vending_forms.paint_display` already sets a lit price readout in. Not a
    fourth glyph table."""
    got = RF.plan(*DEFAULT, price="14.95", key="face2")
    A = got["art"]
    mask = pt.trim(pt.render(A["text"], A["scale"]))
    canvas, rects = A["canvas"], A["rects"]
    x0, y0, x1, y1 = rects["screen"]
    ox = x0 + ((x1 - x0) - len(mask[0])) // 2
    oy = y0 + ((y1 - y0) - len(mask)) // 2
    ink = {(x, y) for y, row in enumerate(mask) for x, v in enumerate(row) if v}
    for y in range(len(mask)):
        for x in range(len(mask[0])):
            got_px = canvas.get(ox + x, oy + y)
            assert got_px == (RF.VFD_INK if (x, y) in ink else RF.VFD_GROUND), (x, y)


def test_the_screen_is_green_on_black_and_the_contrast_is_not_marginal():
    from zoo_keeper.core.vending_forms import contrast, luminance
    r, g, b = RF.VFD_INK
    assert g > 180 and r < 120 and b < 180 and g > r and g > b
    assert luminance(RF.VFD_GROUND) < 0.02
    assert contrast(RF.VFD_INK, RF.VFD_GROUND) > 10.0
    # and the operator panel is the reference's OTHER reading: dark on green
    assert luminance(RF.LCD_INK) < luminance(RF.LCD_GROUND)
    assert contrast(RF.LCD_INK, RF.LCD_GROUND) > 4.5


def test_the_keypad_is_painted_and_carries_its_coloured_keys():
    c = RF.paint_keys(44, 64)
    seen = {c.get(x, y) for y in range(c.h) for x in range(c.w)}
    assert RF.KEY_ACCENT_A in seen and RF.KEY_ACCENT_B in seen
    assert RF.KEY_GROUND in seen


def test_the_keypad_carries_no_lettering_at_all():
    """`card_art`'s rule: a key face is 7 px across here and a legend at that
    size is noise costing the pixels a legend somebody can read would cost.
    Measured as: the keypad holds no glyph of the face at scale 1."""
    src = open(os.path.join(_ZOO, "zoo_keeper", "core", "register_forms.py"),
               encoding="utf-8").read()
    body = src[src.index("def paint_keys"):src.index("def art(")]
    assert "pt.render" not in body and "pt.trim" not in body


# --- the texture, which is the whole cost -------------------------------------------


@pytest.mark.parametrize("dims", CORNERS, ids=lambda d: "x".join(str(v) for v in d))
def test_there_is_one_image_and_it_fits_the_cap(dims):
    got = RF.plan(*dims, key="atlas")
    A = got["art"]
    W, H = A["size"]
    kib = W * H * 3 / 1024.0
    assert kib <= ATLAS_KIB_MAX, (dims, W, H, kib)
    for name, (x0, y0, x1, y1) in A["rects"].items():
        assert 0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H, name
    assert {p["tile"] for p in got["prims"] if p.get("tile")} <= set(A["rects"])


def test_the_image_is_named_for_its_own_pixels():
    """Two registers reading the same price at the same size share one image;
    two that differ do not, and nothing has to know which."""
    import zlib
    a = RF.plan(*DEFAULT, price="14.95", key="x")["art"]
    b = RF.plan(*DEFAULT, price="14.95", key="y")["art"]
    c = RF.plan(*DEFAULT, price="2.50", key="x")["art"]
    d = RF.plan(0.52, 0.42, 0.46, price="14.95", key="x")["art"]
    # two registers of a size reading a price ARE one image, whatever module
    # each came from -- the keypad's per-key shade is keyed on the grid and
    # not on the stem, so a second counter costs no second atlas
    assert a["name"] == b["name"]
    assert a["name"] != c["name"] and a["name"] != d["name"]
    assert a["name"].endswith("%08x" % (zlib.crc32(bytes(a["canvas"].buf)) & 0xFFFFFFFF))


def test_the_same_inputs_give_the_same_bytes():
    for _ in range(2):
        got = RF.plan(*DEFAULT, price="9.95", key="det")
        assert got["art"]["canvas"].png() == RF.plan(
            *DEFAULT, price="9.95", key="det")["art"]["canvas"].png()
        assert got["prims"] == RF.plan(*DEFAULT, price="9.95", key="det")["prims"]


# --- the price ------------------------------------------------------------------------


def test_the_price_is_deterministic_and_the_variants_differ():
    seen = set()
    for v in range(4):
        _mod, plan = _module_plan(variant=v)
        p = RF.pick_price(plan)
        assert p == RF.pick_price(plan)
        seen.add(p)
    assert len(seen) == 4


def test_an_asked_for_price_is_honoured_and_a_bogus_one_is_not():
    _mod, plan = _module_plan()
    plan["params"]["price"] = "24.99"
    assert RF.pick_price(plan) == "24.99"
    plan["params"]["price"] = "999999.99"
    assert RF.pick_price(plan) in RF.PRICES


def test_every_painted_string_is_a_number_or_the_word_total():
    """No mark, no maker, no model, no sticker. The denylist is a tripwire
    and not a trademark search -- `card_brands`' own words -- so this holds
    both halves: the strings are what they say they are, AND they clear the
    list."""
    strings = set(RF.PRICES) | {RF.LCD_HEAD}
    for dims in CORNERS:
        for price in RF.PRICES:
            f = RF.plan(*dims, price=price, key="deny")["facts"]
            strings.add(f["digits"])
            strings.update(f["lcd_lines"])
    for s in strings:
        assert re.fullmatch(r"\d+\.\d{2}|TOTAL", s), s
        up = s.upper()
        assert not (set(re.findall(r"[A-Z0-9']+", up)) & set(CB.DENY_WORDS)), s
        assert not [p for p in CB.DENY_PARTS if p in up], s


def test_the_denylist_can_actually_fail_on_these_strings():
    """Guard the guard: the assertion above is a loop over a set, and a loop
    that never trips is indistinguishable from one that passed."""
    assert len(CB.DENY_WORDS) >= 30 and len(CB.DENY_PARTS) >= 20
    probe = sorted(CB.DENY_WORDS)[0].upper()
    assert set(re.findall(r"[A-Z0-9']+", probe)) & set(CB.DENY_WORDS)


# --- the recipe does not add a light --------------------------------------------------


def test_the_recipe_adds_no_light_and_says_so():
    """Compatibility allows `max_lights_per_object` 8 and the card-shop
    package already ships 84. The display is a MATERIAL. Read off the source
    rather than off a build, so it holds whether or not Blender is here."""
    src = open(_RECIPE, encoding="utf-8").read()
    assert "lights.new" not in src and "OmniLight" not in src
    assert not re.search(r"bpy\.data\.lights|type\s*=\s*['\"]LIGHT", src)
    assert "make_backlit_material" in src and "make_painted_material" in src


def test_the_lit_material_carries_the_suffix_lux_binds_on():
    src = open(_RECIPE, encoding="utf-8").read()
    assert '_Face"' in src
    assert "RF.SCREEN_EMISSION if lit_on else 0.0" in src


# --- the seam the showcase counter needs ----------------------------------------------


def _case(**params):
    p = {"form": "flat", "shelves": 2, "case_depth": 0.6, "bay_max": 1.2}
    p.update(params)
    return DF.plan(2.4, 0.6, 1.0, p, 0, key="card_shop_a01")


def test_the_case_still_stands_its_own_till_by_default():
    """NOTHING CHANGES FOR ANYBODY WHO DOES NOT ASK. A placer that has not
    learned to stand a `cash_register` still gets a shape in the right place,
    which is better than a bare counter."""
    got = _case()
    assert got["facts"]["till"] is True
    assert {p["part"] for p in got["prims"] if "Till" in p["part"]} == {
        "DisplayCase_Till", "DisplayCase_TillKeys",
        "DisplayCase_TillStem", "DisplayCase_TillHead"}


def test_the_case_drops_its_till_when_asked():
    """The seam Deli Counter needs: `params.till: 0` beside the placement of
    a `cash_register`, and no other change in this repo. Fails on 0.99.0,
    where the parameter does not exist and the boxes are drawn regardless."""
    got = _case(till=0)
    assert got["facts"]["till"] is False
    assert [p["part"] for p in got["prims"] if "Till" in p["part"]] == []


def test_dropping_the_till_changes_nothing_but_the_till():
    """MEASURED AT EVERY SHIPPED WIDTH before it was claimed. The till's
    keep-out band only bites where the storage row is short of room: on the
    genome's narrowest case (0.9 m) it costs one item, 32 against 33, and at
    every width Deli Counter actually authors -- 1.8, 2.4 and 3.6 m, flat and
    L -- the item count and every non-till primitive are identical. So the
    cost of the switch is 48 triangles and nothing else, and a counter
    standing a `cash_register` is not a counter with a hole in it."""
    for w, d, h in ((1.8, 0.6, 0.95), (2.4, 0.6, 1.0), (3.6, 0.6, 1.05)):
        for form in ("flat", "L"):
            on = DF.plan(w, d, h, {"form": form, "shelves": 3, "case_depth": 0.6,
                                   "bay_max": 1.2}, 0, key="k")
            off = DF.plan(w, d, h, {"form": form, "shelves": 3, "case_depth": 0.6,
                                    "bay_max": 1.2, "till": 0}, 0, key="k")
            keep = [p for p in on["prims"] if "Till" not in p["part"]]
            assert [p for p in off["prims"] if "Till" not in p["part"]] == keep
            assert off["facts"]["items"] == on["facts"]["items"]
            assert on["facts"]["tris"] - off["facts"]["tris"] == 48
    narrow = DF.plan(0.9, 0.45, 0.85, {"form": "flat", "shelves": 3,
                                       "case_depth": 0.6, "bay_max": 1.2}, 0, key="k")
    wide = DF.plan(0.9, 0.45, 0.85, {"form": "flat", "shelves": 3, "case_depth": 0.6,
                                     "bay_max": 1.2, "till": 0}, 0, key="k")
    assert wide["facts"]["items"] == narrow["facts"]["items"] + 1


def test_the_case_genome_declares_the_switch():
    g = json.load(open(os.path.join(os.path.dirname(_GENOME), "display_case.json"),
                       encoding="utf-8"))
    assert g["params"]["till"] == {"min": 0, "max": 1, "default": 1}


# --- bpy: the built module ------------------------------------------------------------


def _build(tmp_path, dims, style=4, variant=0, params=None):
    from zoo_keeper.bpylayer import build as B
    mod = _kit(*dims, style=style, variant=variant)["modules"][0]
    if params:
        real = B.dna.resolve_module_plan

        def patched(*a, **k):
            p = real(*a, **k)
            p["params"].update(params)
            return p
        B.dna.resolve_module_plan = patched
        try:
            return B.build_module(mod, str(tmp_path), theme="delco_1997",
                                  style=style, options={"save_blend": False})
        finally:
            B.dna.resolve_module_plan = real
    return B.build_module(mod, str(tmp_path), theme="delco_1997", style=style,
                          options={"save_blend": False})


def _glb_json(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    return json.loads(b[20:20 + n])


@pytest.mark.parametrize("dims", (DEFAULT, CORNERS[0], CORNERS[-1]),
                         ids=lambda d: "x".join(str(v) for v in d))
def test_bpy_fits_its_slot_with_every_part(tmp_path, dims):
    bpy = pytest.importorskip("bpy")
    res = _build(tmp_path, dims)
    checks = {c["id"]: c for c in res["report"]["checks"]}
    for cid in ("fit_width", "fit_depth", "fit_height", "fit_pivot", "collision",
                "wear_colors", "uvs", "parts_named", "materials", "transforms",
                "tri_budget"):
        assert checks[cid]["level"] == "pass", (dims, checks[cid])
    assert res["report"]["status"] == "pass"
    f = res["facts"]
    for axis, v in zip(("width", "depth", "height"), dims):
        assert abs(f["dimensions"][axis] - v) <= 0.001, (dims, axis, f["dimensions"])
    assert max(abs(c) for c in f["center"]) <= 0.001
    assert f["tris"] == TRIS
    col = [o for o in bpy.context.scene.objects if o.name.endswith("-colonly")]
    assert len(col) == 1


def test_bpy_the_screen_glows_nothing_else_does_and_no_lamp_exists(tmp_path):
    bpy = pytest.importorskip("bpy")
    res = _build(tmp_path, DEFAULT)
    objs = {o.name: o for o in bpy.context.scene.objects}
    assert not [o for o in bpy.context.scene.objects if o.type == "LIGHT"]

    def emission(mat):
        bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        sock = bsdf.inputs["Emission Color"]
        img = sock.links[0].from_node.image if sock.is_linked else None
        return bsdf.inputs["Emission Strength"].default_value, img

    mat = objs["Register_Screen"].data.materials[0]
    assert mat.name.startswith("M_Register_") and mat.name.endswith("_Face")
    s, img = emission(mat)
    assert s == pytest.approx(RF.SCREEN_EMISSION) and s > 0
    assert img is not None and img.packed_file is not None
    for name, o in objs.items():
        if o.type != "MESH" or name == "Register_Screen" or name.endswith("-colonly"):
            continue
        st, _i = emission(o.data.materials[0])
        assert st == 0.0, name
    # ONE image for the whole module: the screen's and the art's material
    # share it, so the atlas is one texture on a client and not three
    assert objs["Register_Art"].data.materials[0].name.endswith("_Panel")
    imgs = {o.data.materials[0].name: emission(o.data.materials[0])[1]
            for o in bpy.context.scene.objects
            if o.type == "MESH" and len(o.data.materials)}
    assert len({i.name for i in imgs.values() if i is not None}) == 1
    g = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    assert len(g.get("images", [])) == 1


def test_bpy_pulling_the_plug_kills_the_glow_and_keeps_the_artwork(tmp_path):
    bpy = pytest.importorskip("bpy")
    _build(tmp_path, DEFAULT, params={"lit": 0})
    mat = {o.name: o for o in bpy.context.scene.objects}["Register_Screen"].data.materials[0]
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    assert bsdf.inputs["Emission Strength"].default_value == 0.0
    assert bsdf.inputs["Base Color"].is_linked


def test_bpy_no_two_built_faces_share_a_plane(tmp_path):
    """`tools/coplanar_probe.py`'s own function on the built scene, at its own
    defaults -- the measurement `tools/coplanar_census.py` makes, so this is
    the same number the census prints and not a second opinion.

    Read the signature before calling it: `probe` takes
    ``(bpy, mathutils, objs, tol, min_area, normal_tol)`` and returns
    ``(rows, ntris)``. The first draft of this test called ``probe()`` and
    read a dict, which is a checker written against a guessed schema."""
    bpy = pytest.importorskip("bpy")
    import importlib.util
    import mathutils
    _build(tmp_path, DEFAULT)
    spec = importlib.util.spec_from_file_location(
        "coplanar_probe", os.path.join(_ZOO, "tools", "coplanar_probe.py"))
    cp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cp)
    objs = cp._visual_meshes(bpy, bpy.context.scene)
    rows, ntris = cp.probe(bpy, mathutils, objs, 0.002, 1e-6, 1e-3)
    assert rows == [], rows
    assert ntris == TRIS
