"""The 1990s coin payphone (Zoo 1.88.0, roadmap 210): three enclosures, an
invented phone company, a real coin-return recess, and no two faces on one
plane at any size. Since 1.89.0, two atlases and two draws: the header's face
and a hood lamp's diffuser are lit, and the lamp's marker hangs under the
diffuser in free air, carrying its height above the ground.

1.87.0's payphone was a half-booth of boxes in three materials -- no keypad,
no coin slot, no cord, nothing printed -- and the coincident-face census
pinned it at 2 pairs (`test_coincident_faces.RESIDUE`). On 1.87.0 this file
fails at its import: there is no `core.payphone_forms`. On 1.88.0 the lit
atlas, the lamp and the built GLB's second material fail: there is no
`PF.GLOW_TILES` and no layout `lamp`.
"""
from __future__ import annotations

import json
import math
import os
import re
import struct

import numpy as np
import pytest

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import card_brands as CB
from zoo_keeper.core import club_names as CN
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import kit
from zoo_keeper.core import paint as PT
from zoo_keeper.core import payphone_forms as PF
from zoo_keeper.core import poster_copy as PC
from zoo_keeper.core import prims as P

CORNERS = [(w, d, h) for w in (0.525, 0.75, 1.05) for d in (0.35, 0.5, 0.7) for h in (1.61, 2.3, 3.22)]
#: The telephone companies and payphone makers of the 1990s, none of whose
#: names an invented one may use as a word.
REAL_TELCOS = {"BELL", "ATLANTIC", "VERIZON", "NYNEX", "AMERITECH", "QWEST", "SPRINT", "MCI", "GTE",
               "PACBELL", "SOUTHWESTERN", "ATT", "PROTEL", "ELCOTEL", "INTELLICALL", "NORTEL"}
#: Real graffiti writers, Philadelphia's first, whose names no tag in a booth may be (1.117.0).
REAL_WRITERS = {"CORNBREAD", "COOL EARL", "TOP CAT", "ESPO", "REVS", "COST", "KAWS", "TAKI", "SEEN", "DONDI",
                "BLADE", "CRASH", "DAZE", "LEE", "FUTURA", "ZEPHYR", "PHASE", "KASE", "SKEME", "DURO", "SABER",
                "BANKSY", "OBEY", "JA", "IZ"}


def _slot(form=None):
    slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": "payphone",
            "material": "metal_painted", "fit": {"dims": [0.75, 0.5, 2.3], "pivot": "center"}}
    if form:
        slot["form"] = form
    return slot


def test_the_genome_names_the_forms_and_the_stem_carries_one():
    g = genome_mod.load_species("payphone")
    assert genome_mod.validate_genome(g) == []
    assert g["parts"] == ["Payphone_Art", "PayphoneGlow_Art"]
    assert g["params"]["form"] == ["auto"] + list(PF.FORMS)
    for form, tail in ((None, "_h230"), ("pedestal", "_h230_fpedestal"), ("wall", "_h230_fwall")):
        plan = kit.plan_kit({"building_id": "t", "slots": [_slot(form)]}, theme="delco_1997", style=1)
        assert plan["dressing_fallbacks"] == [], plan["dressing_fallbacks"]
        assert plan["modules"][0]["stem"].endswith(tail), plan["modules"][0]["stem"]


def test_auto_is_the_booth_and_an_unknown_form_is_refused():
    assert PF.resolve_form("auto") == PF.resolve_form(None) == PF.resolve_form("") == "booth"
    with pytest.raises(ValueError):
        PF.resolve_form("glass_booth")


@pytest.mark.parametrize("form", PF.FORMS)
def test_every_form_fills_its_slot_with_no_shared_plane(form):
    budget = genome_mod.load_species("payphone")["budgets"]["tris_lod0"]
    for w, d, h in CORNERS:
        g = PF.plan(w, d, h, form)
        lo, hi = P.bounds(g["prims"])
        assert (round(hi[0] - lo[0], 6), round(hi[1] - lo[1], 6)) == (round(w, 6), round(d, 6)), (form, w, d, h)
        assert abs(lo[2]) < 1e-9 and abs(hi[2] - h) < 1e-9, (form, w, d, h)
        assert abs(lo[0] + hi[0]) < 1e-9 and abs(lo[1] + hi[1]) < 1e-9
        # at 3 mm, not the probe's 2: a gap the probe would read either side of
        # in float32 fails here first (the vault lock's cap, 2.0 mm, did)
        assert P.coincident_pairs(g["prims"], tol=0.003) == [], (form, w, d, h)
        assert g["facts"]["tris"] <= budget, (form, w, d, h, g["facts"]["tris"])


def test_the_check_sees_a_shared_plane():
    """A checker that cannot fail is indistinguishable from one that passed:
    the instrument flush on its back panel is a pair, and INSET clears it."""
    inst = P.box("A", "paint", (0.0, 0.0, 0.0), (0.19, 0.11, 0.5))
    flush = P.box("B", "paint", (-0.3, 0.11, -0.2), (0.3, 0.135, 0.8))
    into = P.box("B", "paint", (-0.3, 0.11 - PF.INSET, -0.2), (0.3, 0.135, 0.8))
    assert P.coincident_pairs([inst, flush]) != []
    assert P.coincident_pairs([inst, into]) == []


def _normal(p):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = [p["verts"][i] for i in p["faces"][0][:3]]
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    m = sum(c * c for c in n) ** 0.5
    return tuple(c / m for c in n)


#: A flat part's name -> (axis, sign) it must face. Curved parts -- the
#: cord, the cups, the lock, the binder's rings -- are left out.
FACING = (("_front", (1, -1)), ("_back", (1, 1)), ("_right", (0, 1)), ("_left", (0, -1)),
          ("_top", (2, 1)), ("_under", (2, -1)), ("_Face_B", (1, -1)), ("_Face_T", (1, -1)),
          ("_Face_L", (1, -1)), ("_Face_R", (1, -1)), ("_Well_B", (2, 1)), ("_Well_T", (2, -1)),
          ("_Well_L", (0, 1)), ("_Well_R", (0, -1)), ("Return_Back", (1, -1)), ("SlotFace_Back", (1, -1)))
CURVED = ("Payphone_Cord", "Payphone_EarCup", "Payphone_MouthCup", "Payphone_Lock", "Payphone_BinderRing")


@pytest.mark.parametrize("form", PF.FORMS)
def test_every_flat_face_points_out_of_what_it_closes(form):
    """A quad wound the wrong way is culled, and the payphone has a hole in
    it. Each part's name says which way it faces."""
    g = PF.plan(0.75, 0.5, 2.3, form)
    for p in g["prims"]:
        name = p["part"]
        if name.startswith(CURVED):
            continue
        if name.startswith("Payphone_BackFace_"):
            want = (1, -1)
        else:
            want = next((d for suffix, d in FACING if name.endswith(suffix)), None)
        assert want is not None, name
        axis, sign = want
        assert _normal(p)[axis] * sign > 0.5, (name, _normal(p))


def test_two_atlases_and_the_lit_one_holds_the_header_and_the_diffuser():
    """The header's face and the diffuser are lit (1.89.0); everything else is
    paint. A tile on the wrong atlas is a sign that does not glow, or a shroud
    that does."""
    for form in PF.FORMS:
        g = PF.plan(0.75, 0.5, 2.3, form)
        assert {p["mat"] for p in g["prims"]} == {"paint", "glow"}
        for p in g["prims"]:
            assert (p["mat"] == "glow") == (p["tile"] in PF.GLOW_TILES), p["part"]
        for name, (atlas, _spec) in g["tiles"].items():
            assert atlas == ("glow" if name in PF.GLOW_TILES else "paint"), name
        assert {p["tile"] for p in g["prims"]} <= set(g["tiles"])
        lit = {p["tile"] for p in g["prims"] if p["mat"] == "glow"}
        assert lit == ({"lens"} if form == "pedestal" else {"header", "lens"}), (form, lit)
        assert g["facts"]["materials"] == 2


def test_every_line_of_every_tile_sets_in_every_form_at_every_size():
    """A line the painter cannot set is dropped in silence: the card, the
    keys and the header are the point of the redraw."""
    for form in PF.FORMS:
        for w, d, h in CORNERS:
            for k, (_a, spec) in PF.plan(w, d, h, form)["tiles"].items():
                c = CA.paint(spec)
                assert not getattr(c, "unset", []), (form, w, d, h, k, c.unset)


def test_the_company_line_rides_a_header_wide_enough_to_set_it():
    """The default booth's header carries the line; the narrowest carries
    the name alone, by the plan's word rather than a line dropped in
    silence."""
    assert PF.plan(0.75, 0.5, 2.3, "booth")["tiles"]["header"][1]["line"] is True
    assert PF.plan(0.525, 0.5, 2.3, "booth")["tiles"]["header"][1]["line"] is False


def test_the_names_are_invented():
    parts = PC.DENYLIST + tuple(CB.DENY_PARTS) + CN.DENYLIST + CN.BEER_DENYLIST
    for text in PF.all_strings():
        up = text.upper()
        tokens = set(re.findall(r"[A-Z0-9']+", up))
        assert not tokens & set(CB.DENY_WORDS), text
        assert not tokens & REAL_TELCOS, text
        assert "AT&T" not in up, text
        assert not any(bad in up for bad in parts), (text, [b for b in parts if b in up])
    for sticker in PF.STICKERS:
        for line in sticker:
            if re.search(r"\d{3}-\d{3}-\d{4}", line):
                assert re.fullmatch(r"610-555-01\d\d", line), line     # the fictional exchange
    # the tags and the keyed initials (1.117.0) are painted words like the rest, and no real writer's
    assert set(PF.TAG_WORDS) | set(PF.INITIALS) <= set(PF.all_strings())
    assert not (set(PF.TAG_WORDS) | set(PF.INITIALS)) & REAL_WRITERS


def test_the_shroud_is_painted_the_genome_s_colour():
    """Editing the genome repaints the payphone. `test_recipe_reads_its_genome`
    checked that on 1.87.0's materials; an atlas recipe builds none, so that
    test now skips the payphone ("builds no materials") and this holds it:
    the style colour reaches the shroud's tile, and the recipe passes it."""
    rgb = genome_mod.load_species("payphone")["styles"]["default"]["color"]
    mine = PF.plan(0.75, 0.5, 2.3, "booth", rgb)["tiles"]["shroud"][1]
    other = PF.plan(0.75, 0.5, 2.3, "booth", (0.5, 0.1, 0.1))["tiles"]["shroud"][1]
    assert mine["paint"] == tuple(PF._srgb8(c) for c in rgb)
    assert CA.paint(mine).png() != CA.paint(other).png()
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "zoo_keeper", "recipes", "payphone.py"), encoding="utf-8").read()
    # 1.116.0 passes the kit's variant after the colour (`test_the_recipe_hands_the_variant_to_the_plan`)
    assert 'PF.plan(w, d, h, params.get("form"), plan["color"], variant=' in src


def test_the_coin_return_is_a_real_recess():
    """The standard's ask: a real recess where the camera can see into it.
    Its back stands RETURN_DEPTH behind the face, four walls run to it, and
    nothing at the face's plane covers the opening."""
    g = PF.plan(0.75, 0.5, 2.3, "booth")
    yf = g["layout"]["inst"][2]
    back = next(p for p in g["prims"] if p["part"] == "Payphone_Return_Back")
    assert all(abs(v[1] - (yf + PF.RETURN_DEPTH)) < 1e-9 for v in back["verts"])
    xs, zs = [v[0] for v in back["verts"]], [v[2] for v in back["verts"]]
    cx, cz = (min(xs) + max(xs)) / 2.0, (min(zs) + max(zs)) / 2.0
    for p in g["prims"]:
        if p["part"].startswith("Payphone_Return_Face"):
            pxs, pzs = [v[0] for v in p["verts"]], [v[2] for v in p["verts"]]
            assert not (min(pxs) < cx < max(pxs) and min(pzs) < cz < max(pzs)), p["part"]
    assert len([p for p in g["prims"] if p["part"].startswith("Payphone_Return_Well")]) == 4


def test_twelve_keys_each_showing_its_own_legend():
    g = PF.plan(0.75, 0.5, 2.3, "booth")
    fronts = [p for p in g["prims"] if re.fullmatch(r"Payphone_Key\d+_front", p["part"])]
    assert len(fronts) == 12
    assert all(p["tile"] == "face" for p in fronts)
    windows = {tuple(round(c, 6) for corner in p["uvs"][0] for c in corner) for p in fronts}
    assert len(windows) == 12


def test_the_cord_hangs_from_the_handset_into_the_instrument_clear_of_everything():
    for form in PF.FORMS:
        for w, d, h in CORNERS:
            L = PF.layout(form, w, d, h)
            ix0 = L["inst"][0]
            gx, gy, _gz0, _gz1 = L["grip"]
            path = L["cord"]
            assert math.dist(path[0], (gx, gy, L["mouth_z"])) < PF.CUP_R     # starts in the mouth cup
            assert path[-1][0] > ix0                                       # ends inside the instrument
            for x, y, z in path:
                if form != "pedestal":
                    assert x + PF.CORD_R < L["shelf_x0"], (form, w, d, h)
                assert -w / 2.0 < x - PF.CORD_R and x + PF.CORD_R < w / 2.0
                assert -d / 2.0 < y - PF.CORD_R and y + PF.CORD_R < d / 2.0
                assert z - PF.CORD_R > 0.0


def test_a_narrow_booth_keeps_only_the_sticker_that_fits():
    assert [t for _r, t in PF.stickers(PF.layout("booth", 0.525, 0.5, 2.3))] == ["sticker_2"]
    assert len(PF.stickers(PF.layout("booth", 0.75, 0.5, 2.3))) == 3


def test_the_instrument_stands_at_a_callers_height():
    """Its foot a metre up wherever the slot allows, so the keypad sits
    under a standing caller's eye in every form."""
    for form in PF.FORMS:
        z0 = PF.layout(form, 0.75, 0.5, 2.3)["inst"][4]
        assert z0 == pytest.approx(PF.INST_FOOT)
        assert 1.15 < z0 + PF.KEYPAD_Z < 1.45


def _part_boxes(prims):
    """Each part's bounds, a part being its prims' name up to a box face's
    suffix; a part that is one prim is its own."""
    boxes = {}
    for p in prims:
        key = p["part"]
        if key.endswith(("_front", "_back", "_left", "_right", "_top", "_under")):
            key = key.rsplit("_", 1)[0]
        lo, hi = boxes.get(key, ((1e9,) * 3, (-1e9,) * 3))
        boxes[key] = (tuple(min(lo[k], min(v[k] for v in p["verts"])) for k in range(3)),
                      tuple(max(hi[k], max(v[k] for v in p["verts"])) for k in range(3)))
    return boxes


def test_the_hood_lamp_hangs_in_free_air_under_its_diffuser():
    """A lamp inside closed hardware bakes to nothing (Lux 0.65.0's pole,
    0.67.0's bulbs). The marker hangs LAMP_EMIT under the diffuser's face,
    behind the header, in front of the instrument and above it, inside no
    part, and carries its own height above the ground for Lux to solve
    from."""
    for form in PF.FORMS:
        for w, d, h in CORNERS:
            g = PF.plan(w, d, h, form)
            L = g["layout"]
            x0, x1, y0, y1, z0, z1 = L["lens"]
            lx, ly, lz = L["lamp"]
            assert x0 < lx < x1 and y0 < ly < y1, (form, w, d, h)
            assert lz == pytest.approx(z0 - PF.LAMP_EMIT)
            assert z1 == pytest.approx(h - PF.T_ROOF)
            assert lz > L["inst"][5], (form, w, d, h)
            assert ly < L["y_face"], (form, w, d, h)
            if form != "pedestal":
                hdr = next(p for p in g["prims"] if p["part"] == "Payphone_Header_front")
                assert y0 - max(v[1] for v in hdr["verts"]) > PF.T_HEADER, (form, w, d, h)
            for part, (lo, hi) in _part_boxes(g["prims"]).items():
                assert not all(lo[k] < c < hi[k] for k, c in enumerate((lx, ly, lz))), (form, w, d, h, part)
            assert g["lamp"]["name"] == "LuxEmit_payphone_hood"
            assert g["lamp"]["at"] == L["lamp"]
            assert g["lamp"]["props"] == {"lux_type": "payphone_hood", "lux_drop": lz}


def test_the_recipe_hands_the_lamp_and_its_payload_to_the_marker():
    """The marker is an attachment and its payload rides `marker_props`, which
    `bpylayer.build` passes to `markers.add_marker` at both call sites."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    recipe = open(os.path.join(root, "zoo_keeper", "recipes", "payphone.py"), encoding="utf-8").read()
    assert 'lamp["name"]: lamp["at"]' in recipe
    assert '"marker_props": {lamp["name"]: dict(lamp["props"])}' in recipe
    build_src = open(os.path.join(root, "zoo_keeper", "bpylayer", "build.py"), encoding="utf-8").read()
    call = 'markers.add_marker(name, loc, coll, props=result.get("marker_props", {}).get(name))'
    assert build_src.count(call) == 2
    assert "markers.add_marker(name, loc, coll)\n" not in build_src


@pytest.mark.parametrize("form", PF.FORMS)
def test_bpy_a_payphone_is_two_objects_two_materials_and_its_lamp(tmp_path, form):
    """Built as a kit builds it and read back out of the GLB: the paint and the
    lit art, the lit material named `_Face` for Lux's power cut, and the lamp's
    marker with its payload in the node's extras, re-centred with the geometry
    (1.89.0)."""
    bpy = pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    plan = kit.plan_kit({"building_id": "t", "slots": [_slot(form)]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    objs = sorted(o.name for o in bpy.context.scene.objects
                  if o.type == "MESH" and not o.name.endswith(_COL_SUFFIXES))
    assert objs == ["PayphoneGlow_Art", "Payphone_Art"], objs
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    ln, _kind = struct.unpack_from("<I4s", raw, 12)
    doc = json.loads(raw[20:20 + ln])
    assert len(doc["materials"]) == 2
    assert [m["name"].endswith("_Face") for m in doc["materials"]].count(True) == 1, doc["materials"]
    lamps = [n for n in doc["nodes"] if n["name"].startswith("LuxEmit_payphone_hood")]
    assert len(lamps) == 1, [n["name"] for n in doc["nodes"]]
    want = PF.layout(form, 0.75, 0.5, 2.3)["lamp"]
    assert lamps[0]["extras"]["lux_type"] == "payphone_hood"
    assert lamps[0]["extras"]["lux_drop"] == pytest.approx(want[2])
    # glTF is Y up with the caller at +Z, and the module is re-centred on its slot
    assert lamps[0]["translation"] == pytest.approx([want[0], want[2] - 2.3 / 2.0, -want[1]], abs=1e-4)


# --- the booth's marks come in looks (1.116.0) ------------------------------------------------------------------------


def _marked(form, variant):
    """Every tile of the booth that somebody else marks, painted: the enclosure's insides and the stickers."""
    got = PF.plan(0.75, 0.5, 2.3, form, variant=variant)
    return {k: CA.paint(spec).png() for k, (_a, spec) in got["tiles"].items()
            if spec["kind"] in ("payphone_side_in", "payphone_back_in", "payphone_sticker")}


@pytest.mark.parametrize("form", PF.FORMS)
def test_variant_zero_is_the_plan_without_one_and_marked_like_the_rest(form):
    """A plan without a variant is variant 0's, and since 1.117.0 its insides carry marks like every other look's:
    the walker's note of 2026-10-20 was on all of them. FAILS ON 1.116.0: variant 0 was the 1.115.0 booth, two
    inside tiles carrying no `marks` key."""
    plain = PF.plan(0.75, 0.5, 2.3, form)
    assert plain == PF.plan(0.75, 0.5, 2.3, form, variant=0)
    inside = [spec for _a, spec in plain["tiles"].values() if spec["kind"] in _INSIDE]
    assert len(inside) == 3 and all(spec.get("marks") == 0 for spec in inside), inside


@pytest.mark.parametrize("form", PF.FORMS)
def test_each_variant_marks_its_booth_differently_and_the_same_every_build(form):
    """The walker's look review, 2026-10-19: the booth's graffiti "too similar/uniform". Each of the four looks paints
    the enclosure's insides its own way, and the same way every build. FAILS ON 1.115.0: `plan` takes no variant."""
    seen = set()
    for v in range(PF.VARIANTS):
        a = _marked(form, v)
        assert a == _marked(form, v)
        seen.add(tuple(sorted(a.items())))
    assert len(seen) == PF.VARIANTS


def test_the_genome_takes_four_variants_and_the_stem_carries_one():
    g = genome_mod.load_species("payphone")
    assert genome_mod.validate_genome(g) == []
    assert g["module_variants"] == PF.VARIANTS == 4
    for v, tail in ((1, "_h230_n1"), (3, "_h230_n3")):
        plan = kit.plan_kit({"building_id": "t", "slots": [dict(_slot(), variant=v)]}, theme="delco_1997", style=1)
        assert plan["dressing_fallbacks"] == [], plan["dressing_fallbacks"]
        assert plan["modules"][0]["stem"].endswith(tail), plan["modules"][0]["stem"]
    plan = kit.plan_kit({"building_id": "t", "slots": [dict(_slot(), variant=4)]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"], "a variant past module_variants is dropped, and said"


def test_the_recipe_hands_the_variant_to_the_plan():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    recipe = open(os.path.join(root, "zoo_keeper", "recipes", "payphone.py"), encoding="utf-8").read()
    assert 'variant=int(params.get("variant") or 0)' in recipe


# --- the marks are small, and mostly weather (1.117.0) ----------------------------------------------------------------

#: An inside panel's kind -> how `paint` lays its paint before the marks: its body's lift, its weather's seed and
#: grime (`_outdoor`). The same in 1.116.0, which is what lets the tests below be run against it.
_INSIDE = {"payphone_side_in": (-10, 23, 0.8), "payphone_back_in": (-12, 29, 0.7)}


def _rgb(canvas):
    return np.frombuffer(bytes(canvas.buf), dtype=np.uint8).reshape(canvas.h, canvas.w, 3).astype(np.int32)


def _unmarked(spec):
    """The panel's paint before anybody marked it, laid with the module's own helpers as `paint` lays it."""
    lift, seed, grime = _INSIDE[spec["kind"]]
    w, h = PF._px(spec["w_m"]), PF._px(spec["h_m"])
    body = PF._lift(tuple(spec["paint"]), lift)
    im = PT.Img(w, h, body)
    PF._outdoor(im, w, h, body, seed, grime=grime)
    return _rgb(im.to_canvas())


def _panels(rgb=(0.22, 0.26, 0.32)):
    """Every inside panel of every form and variant at the default slot and the genome's two extreme corners,
    painted, with its paint unmarked: ``(where, painted, unmarked)``. A rebuilt paint that is not the panel's fails
    here rather than reading as marks: seven tenths of a panel must be untouched to the bit (1.117.0 leaves 0.81 at
    the least; a rebuild with the wrong weather seed, 0.26)."""
    for form in PF.FORMS:
        for w, d, h in ((0.75, 0.5, 2.3), (0.525, 0.35, 1.61), (1.05, 0.7, 3.22)):
            for v in range(PF.VARIANTS):
                for k, (_a, spec) in sorted(PF.plan(w, d, h, form, rgb, variant=v)["tiles"].items()):
                    if spec["kind"] in _INSIDE:
                        where = (form, w, d, h, v, k)
                        painted, plain = _rgb(CA.paint(spec)), _unmarked(spec)
                        assert (painted == plain).all(axis=2).mean() >= 0.7, where
                        yield where, painted, plain


def test_no_mark_is_a_band_of_paint():
    """The walker's look review, 2026-10-20: "a large shapie squigle doesn't look like anything". 1.116.0 drew a
    tag as a wave of discs 3 px (19 mm) across. A marker's line is a pixel: of the pixels the marks darkened by more
    than 40, no more than 4 in a panel may sit in a 3 x 3 block of them -- where two strokes of a letter meet (1.117.0
    measured 1 at most). FAILS ON 1.116.0: 92 on the default booth's back panel and 230 on its side panel, 987 at
    the genome's corners."""
    for where, painted, plain in _panels():
        dark = (plain - painted).sum(axis=2) / 3.0 > 40
        pad = np.pad(dark, 1)
        block = np.ones_like(dark)
        for dy in range(3):
            for dx in range(3):
                block &= pad[dy:dy + dark.shape[0], dx:dx + dark.shape[1]]
        assert int(block.sum()) <= 4, (where, int(block.sum()))


def test_the_marks_are_faded():
    """Worn, not fresh: on a booth painted white, where a mark shows at its strongest, none inks a pixel more than
    85 % of the way to the black marker (1.117.0's strongest is 0.75, a black tag at its freshest). FAILS ON
    1.116.0: its strokes were laid at 0.85, disc over disc, and inked all but opaque."""
    black = np.array(PF.TAG_INKS[0])
    for where, painted, plain in _panels(rgb=(1.0, 1.0, 1.0)):
        share = ((plain - painted) / np.maximum(plain - black, 1)).mean(axis=2)
        assert share.max() <= 0.85, (where, round(float(share.max()), 3))


def test_every_inside_panel_is_marked():
    """The floor under the two tests above, which a booth with no marks at all would pass: every inside panel of
    every look shows weather and writing, at least 0.3 % of it moved by more than 8. Passes on 1.116.0 too."""
    for where, painted, plain in _panels():
        assert (np.abs(painted - plain).sum(axis=2) / 3.0 > 8).mean() >= 0.003, where


def _drawn(g):
    """``{tile: [(kind, text, box)]}``: what `paint` put up on each inside panel of a plan, as it reports it."""
    return {k: CA.paint(spec).marks for k, (_a, spec) in sorted(g["tiles"].items()) if spec["kind"] in _INSIDE}


def test_the_tags_are_words_each_once_in_a_booth():
    """A tag is a word of `TAG_WORDS` -- three letters drawn at random can spell anything -- and no booth repeats a
    word or a pair of initials across its panels: the first painting of 1.117.0 wrote the same two words on the back
    panel and on a side panel of one booth. FAILS ON 1.116.0: `paint` reported nothing."""
    for form in PF.FORMS:
        for v in range(PF.VARIANTS):
            words, initials = [], []
            for drawn in _drawn(PF.plan(0.75, 0.5, 2.3, form, variant=v)).values():
                words += [text for kind, text, _b in drawn if kind in ("tag", "buff")]
                initials += [pair for kind, text, _b in drawn if kind == "initials" for pair in text.split("+")]
            assert len(words) >= 3 and set(words) <= set(PF.TAG_WORDS), (form, v, words)
            assert len(words) == len(set(words)), (form, v, words)
            assert set(initials) <= set(PF.INITIALS) and len(initials) == len(set(initials)), (form, v, initials)


@pytest.mark.parametrize("form", PF.FORMS)
def test_each_side_panel_is_marked_on_its_own(form):
    """Both side panels' insides showed one tile until 1.117.0, so a booth's two sides carried the same marks facing
    each other across its mouth. FAILS ON 1.116.0: one `side_in` tile."""
    for v in range(PF.VARIANTS):
        g = PF.plan(0.75, 0.5, 2.3, form, variant=v)
        faces = {p["part"]: p["tile"] for p in g["prims"] if p["tile"] in ("side_in_l", "side_in_r")}
        assert faces == {"Payphone_SideL_right": "side_in_l", "Payphone_SideR_left": "side_in_r"}, faces
        assert CA.paint(g["tiles"]["side_in_l"][1]).png() != CA.paint(g["tiles"]["side_in_r"][1]).png()


def test_nobody_writes_behind_the_phone():
    """`behind_phone` is where the instrument and its handset hang in front of the back panel's face, read in that
    face's tile, and the back panel's marks keep out of it: a tag behind the phone is a tag nobody sees. Held at every
    corner of the genome, against the prims where they are built. FAILS ON 1.116.0: no `behind_phone`."""
    hung = ("Payphone_Inst", "Payphone_Cradle", "Payphone_Grip", "Payphone_EarCup", "Payphone_MouthCup")
    for form in PF.FORMS:
        for w, d, h in CORNERS:
            g = PF.plan(w, d, h, form)
            u0, v0, u1, v1 = PF.behind_phone(g["layout"])
            face = [v for p in g["prims"] if p["part"].startswith("Payphone_BackFace_") for v in p["verts"]]
            fx0, fx1 = min(v[0] for v in face), max(v[0] for v in face)
            fz0, fz1 = min(v[2] for v in face), max(v[2] for v in face)
            for part in hung:
                vs = [v for p in g["prims"] if p["part"].startswith(part) for v in p["verts"]]
                assert vs, part
                assert u0 <= (min(v[0] for v in vs) - fx0) / (fx1 - fx0), (form, w, d, h, part)
                assert (max(v[0] for v in vs) - fx0) / (fx1 - fx0) <= u1, (form, w, d, h, part)
                assert v0 <= (fz1 - max(v[2] for v in vs)) / (fz1 - fz0), (form, w, d, h, part)
                assert (fz1 - min(v[2] for v in vs)) / (fz1 - fz0) <= v1, (form, w, d, h, part)
            spec = g["tiles"]["back_in"][1]
            pw, ph = PF._px(spec["w_m"]), PF._px(spec["h_m"])
            keep = (u0 * pw, v0 * ph, u1 * pw, v1 * ph)
            for v in range(PF.VARIANTS):
                for kind, text, (bx0, by0, bx1, by1) in CA.paint(dict(spec, marks=v)).marks:
                    if kind in ("tag", "buff", "initials", "paper"):
                        clear = bx1 <= keep[0] or bx0 >= keep[2] or by1 <= keep[1] or by0 >= keep[3]
                        assert clear, (form, w, d, h, v, kind, text)
