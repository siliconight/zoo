"""The sign over a door names who is inside (1.37.0).

Cold run 9120's FLAPPAHS walk: the box over the gas station's door was lit and
blank, and so was every sign Deli Counter derives (102 across the library) --
`sign_box` painted a face only from a sign pack, and no theme ships one. What
is held: the kind is read from the business's words and a club's name is its
neon's (the same key, the same modulus); a gas station says FLAPPAHS in the
pylon's colours; a building of no kind gets a street number, never a blank;
every name SETS on every sign size the library derives (`fit_text` drops what
it cannot set, silently); every name is invented; the business rides an
anchor to its placement; and a built sign's face is painted art in one `_Face`
material, with no back face lying on the cabinet's front.
"""
from __future__ import annotations

import json
import os
import re
import struct

import pytest

from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import club_names as CN
from zoo_keeper.core import fixtures
from zoo_keeper.core import genome
from zoo_keeper.core import poster_copy as PC
from zoo_keeper.core import price_pylon_forms as PY
from zoo_keeper.core import smooth_type as ST
from zoo_keeper.core import storefront_names as SN

#: Every width Deli Counter derived a sign at, measured on the library
#: (`deli_counter/build/*.lights.json`, 0.164.0): door + 0.8, height 0.6.
WIDTHS = (1.9, 2.0, 2.05, 2.1, 2.2, 2.3, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 4.8, 5.0)
#: Real chains a writer would reach for, none of which a sign may name.
REAL = {"WAWA", "SUNOCO", "PRIMO", "PRIMOS", "RITE", "CVS", "ACME", "GIANT", "SHOPRITE", "PATHMARK",
        "WALGREENS", "WINE", "PNC", "MERIDIAN", "CORESTATES", "WACHOVIA", "MELLON", "BEST",
        "DOMINOS", "PIZZA HUT", "GINO'S", "WHEEL", "PAWN STARS", "SAVE", "FOODTOWN"}


@pytest.mark.parametrize("business,kind", [
    ("strip_club_a01", "club"), ("lf_club_block_014_7 strip_club", "club"),
    ("gas_station_a02", "gas"), ("gs_corner_station", "gas"), ("stop_n_go", "gas"),
    ("fuel_stop_heist", "gas"), ("deli_a01", "deli"), ("night_deli", "deli"),
    ("primos_pizza", "pizza"), ("pawn_shop_a01", "pawn"), ("bank_branch_a02", "bank"),
    ("credit_union_a01", "bank"), ("pharmacy_a01", "pharmacy"), ("clinic_a01", "clinic"),
    ("supermarket_a01", "market"), ("market_hall_a01", "market"), ("card_shop_a01", "card"),
    ("brewery_a01", "brewery"), ("casino_a01", "casino"), ("funeral_home_a01", "funeral"),
    ("country_club_a01", "country"), ("07_police_station", "police"),
    ("courthouse_a01", "court"), ("museum_a01", "museum"), ("rail_station_a01", "rail"),
    ("train_yard_a01", "rail"), ("airport_terminal_a01", "airport"), ("arena_a01", "arena"),
    ("stadium_a01", "stadium"),
    ("apartment_walkup_a01", "number"), ("office", "number"), ("mansion_a01", "number")])
def test_the_kind_is_read_from_the_business_s_words(business, kind):
    assert SN.sign_for(business)["kind"] == kind


def test_a_station_is_not_a_gas_station():
    """`station` is in police, rail and gas alike; only gas' own words count."""
    for b in ("07_police_station", "rail_station_a01", "pvp_station_ref"):
        assert SN.sign_for(b)["kind"] != "gas", b


def test_a_club_s_door_says_what_its_neon_says():
    """Deli Counter keys a club's `neon_sign` variant on crc32 of this same
    identity, modulo the piece's 24 names; `neon_sign`'s genome holds that
    the table is that long."""
    assert genome.load_species("neon_sign")["module_variants"] == len(CN.NAMES)
    for b in ("strip_club_a01", "strip_club_a02", "lf_club_block_014_7 strip_club"):
        assert SN.sign_for(b)["text"] == CN.name_for(SN.key(b) % len(CN.NAMES))


def test_a_gas_station_says_flappahs_in_the_pylon_s_colours():
    s = SN.sign_for("gas_station_a02")
    assert s["text"] == PY.STORE and s["colours"] == PY.COLOURWAYS[0]


def test_the_brand_is_spelled_the_walkers_way():
    """1.75.0: FLAPPAHS, as the walker writes it and Pixelcoat's sign spells
    it. Zoo had FLAPPHAS."""
    assert PY.STORE == "FLAPPAHS"


def test_a_convenience_store_is_a_flappahs():
    """1.75.0: the Flappahs store is always Flappahs (the walker,
    2026-10-06). The library's is `convenience_store_a01`; a generated one
    reads `<level> convenience_store` -- neither carries gas, fuel, gs or
    stop, so before `convenience` joined the kind its door showed a street
    number."""
    for b in ("convenience_store_a01", "lf_flappahs_001_1 convenience_store"):
        s = SN.sign_for(b)
        assert s["kind"] == "gas" and s["text"] == PY.STORE, (b, s)


def test_a_retail_strip_is_not_a_strip_club():
    """1.76.0: the word `strip` alone made `strip_retail_a01`'s door say a
    club's name, THE WOODER HOLE. Deli Counter's rule is `strip_club` in
    the id, and the door follows it."""
    for b in ("strip_retail_a01", "strip_retail_a02"):
        assert SN.sign_for(b)["kind"] != "club", b
    for b in ("strip_club_a01", "lf_club_block_014_7 strip_club"):
        assert SN.sign_for(b)["kind"] == "club", b


def test_no_kind_is_a_street_number_never_blank():
    for b in ("", "ext_0_S_sign", "twin_a01", "self_storage_a02"):
        s = SN.sign_for(b)
        assert s["kind"] == "number" and SN.NUMBERS[0] <= int(s["text"]) <= SN.NUMBERS[1]


def test_every_name_sets_on_every_sign_the_library_derives():
    """1.90.0: each name in the voice it is painted in -- a civic building's
    in the institution's face, every other in the shop's (`voice_for`)."""
    civic = {t for kind, _m, names in SN.KINDS if kind in SN.CIVIC for t in names}
    texts = SN.all_strings() + list(CN.NAMES) + [str(SN.NUMBERS[1])]
    for w in WIDTHS:
        for t in texts:
            voice = "civic" if t in civic else "shop"
            c = SN.paint({"w_m": w, "h_m": 0.6, "text": t, "colours": PY.COLOURWAYS[0],
                          "voice": voice})
            assert not c.unset, (w, t, voice)


def test_a_sign_is_in_its_owner_s_hand():
    """1.90.0. The walker, 2026-10-09: "use Blue Highway for the shop signs".
    The face is the owner's (`smooth_type.OWNERS`, the walker's font
    catalog): a shop's sign is the shop's own hand, Blue Highway in its
    condensed weight, and a civic building's fascia is the institution's."""
    for kind, _m, _names in SN.KINDS:
        assert SN.voice_for(kind) == ("civic" if kind in SN.CIVIC else "shop"), kind
    assert SN.voice_for("number") == "shop"
    assert ST.owned(SN.VOICES["shop"]) == "highway_cond"
    assert ST.owned(SN.VOICES["civic"]) == "aileron_bold"
    face, cap, _lines = SN.layout("JAWN'S HOAGIES", 700, 100, "shop")
    assert face == "highway_cond" and cap >= SN.MIN_CAP, (face, cap)
    face, cap, _lines = SN.layout("POLICE", 700, 100, "civic")
    assert face == "aileron_bold" and cap >= SN.MIN_CAP, (face, cap)
    with pytest.raises(ValueError):
        SN.layout("POLICE", 700, 100, "law")


def test_a_sign_is_painted_smooth_at_three_times_its_texel():
    """1.90.0: 240 px a metre, and a letter's edge is coverage, not a step.
    1.89.0 painted 80 px a metre in three colours -- the field, the rule and
    the ink -- which a Closest sample shows from the street as a CRT's
    letter."""
    c = SN.paint({"w_m": 2.4, "h_m": 0.6, "text": "JAWN'S HOAGIES", "colours": PY.COLOURWAYS[0]})
    assert (c.w, c.h) == (576, 144), (c.w, c.h)
    colours = {bytes(c.buf[i:i + 3]) for i in range(0, len(c.buf), 3)}
    assert len(colours) > 12, len(colours)


def test_a_name_too_long_for_its_sign_is_reported_not_cropped():
    """Not even 5 cm caps on two lines fit a 0.3 m face: nothing is lettered,
    and the name is listed, where a crop would ship half a name."""
    c = SN.paint({"w_m": 0.3, "h_m": 0.6, "text": "STIFF & SONS FUNERAL HOME",
                  "colours": PY.COLOURWAYS[0]})
    assert c.unset == ["STIFF & SONS FUNERAL HOME"]
    assert len({bytes(c.buf[i:i + 3]) for i in range(0, len(c.buf), 3)}) == 2


def test_a_long_name_takes_two_lines_when_that_sets_it_bigger():
    """The 2.0 m sign's box, 450 x 102 px: on one line the name's width
    bounds its cap; split at the even word break, both lines set bigger, and
    the composed block -- baselines `LINE_STEP` caps apart -- still sits in
    the box."""
    face, cap, lines = SN.layout("STIFF & SONS FUNERAL HOME", 450, 102, "shop")
    assert lines == ["STIFF & SONS", "FUNERAL HOME"], (cap, lines)
    one = ST.fit_cap("STIFF & SONS FUNERAL HOME", 450, 102, face, SN.MIN_CAP)
    assert one is not None and cap > one, (cap, one)
    block = SN._block(lines, cap, face)
    assert block.shape[0] <= 102 and block.shape[1] <= 450, block.shape
    assert block.shape[0] > (1.0 + SN.LINE_STEP) * cap * 0.95, (block.shape, cap)


def test_the_sign_box_builds_its_face_smooth_in_its_voice():
    """1.90.0: the face's art is built `smooth` -- a bled gutter and a
    material sampled with filtering -- or the coverage above is shown
    Closest; and the face's tile carries its voice. Read as source: the
    recipe imports `bpy` at module scope."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "zoo_keeper", "recipes", "sign_box.py"), encoding="utf-8") as fh:
        src = fh.read()
    assert src.count("build_art(") == 1
    call = src[src.index("build_art("):src.index("objs += got")]
    assert "smooth=True" in call, call
    assert '"voice": SN.voice_for(said["kind"])' in src


def test_the_names_are_invented():
    parts = PC.DENYLIST + tuple(CB.DENY_PARTS) + CN.DENYLIST + CN.BEER_DENYLIST
    # The civic kinds' plain words (STADIUM, ARENA, POLICE ...) say what a
    # building IS; the card list's words are marks only on a card (Stadium
    # Club is a card line), so it is asked of the business names alone.
    civic = {t for kind, _m, names in SN.KINDS if kind in SN.CIVIC for t in names}
    for text in SN.all_strings():
        up = text.upper()
        tokens = set(re.findall(r"[A-Z0-9']+", up))
        if text not in civic:
            assert not tokens & set(CB.DENY_WORDS), text
        assert not tokens & REAL and not any(r in up for r in REAL if " " in r), text
        assert not any(bad in up for bad in parts), (text, [b for b in parts if b in up])


def test_the_business_rides_the_anchor_to_its_placement():
    man = {"light_manifest_version": "1.1.0", "building_id": "deli_a01",
           "space": "Blender Z-up, meters",
           "anchors": [{"id": "ext_0_S_sign", "type": "sign", "pos": [6.0, -0.2, 2.55],
                        "rot_y": 270.0, "size": [2.0, 0.6], "business": "deli_a01"},
                       {"id": "ext_0_N_pack_1", "type": "wall_pack", "pos": [6.0, 12.15, 2.45],
                        "rot_y": 90.0}]}
    by = {p["species"]: p for p in fixtures.plan(man)["placements"]}
    assert by["sign_box"]["business"] == "deli_a01"
    assert "business" not in by["wall_pack"]


def test_bpy_a_sign_is_named_art_in_one_face_material(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build
    man = {"light_manifest_version": "1.1.0", "building_id": "sign_bpy",
           "space": "Blender Z-up, meters",
           "anchors": [{"id": "ext_0_S_sign", "type": "sign", "pos": [0.0, -0.2, 2.55],
                        "rot_y": 270.0, "size": [2.4, 0.6], "business": "gas_station_a02"}]}
    build.build_fixtures(man, str(tmp_path), theme="delco_1997", options={"save_blend": False})
    names = [o.name for o in bpy.context.scene.objects if o.type == "MESH"]
    assert any(n.startswith("SignBox_Face_Art") for n in names), names
    assert not any(n == "SignBox_Face" for n in names), names
    with open(os.path.join(str(tmp_path), "sign_bpy_fixtures.built.json"), encoding="utf-8") as fh:
        index = json.load(fh)
    raw = open(os.path.join(str(tmp_path), index["files"]["glb"]), "rb").read()
    ln, _k = struct.unpack_from("<I4s", raw, 12)
    doc = json.loads(raw[20:20 + ln])
    lit = [m["name"] for m in doc["materials"] if m.get("emissiveFactor") and max(m["emissiveFactor"]) > 0]
    assert len(lit) == 1 and lit[0].endswith("_Face"), lit
    # 1.37.1: the face takes little light and mirrors none -- its own lamp
    # stands 0.29 m in front of it, and at the pylon's 0.6 diffuse copy cold
    # run 9122 photographed a white blob mid-word (26.5% of the sign clipped
    # against 20.0% with the copy at 0.15; matte alone moved it 0.3 points)
    face = next(m for m in doc["materials"] if m["name"] == lit[0])
    pbr = face.get("pbrMetallicRoughness", {})
    assert max(pbr.get("baseColorFactor", [1.0, 1.0, 1.0])[:3]) <= 0.15 + 1e-6, pbr
    assert pbr.get("roughnessFactor", 1.0) == pytest.approx(1.0), pbr
    # 1.90.0: the face is sampled with filtering (glTF magFilter 9729): its
    # letter is coverage, which Closest would step -- and a texture every
    # sampler filters ships VRAM-compressed (Level Factory 0.128.0)
    used = [t["index"] for t in (pbr.get("baseColorTexture"), face.get("emissiveTexture")) if t]
    assert used, face
    for ti in used:
        assert doc["samplers"][doc["textures"][ti]["sampler"]]["magFilter"] == 9729, face["name"]
