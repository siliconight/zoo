"""0.91.0 -- the pull-knob cigarette machine.

The walker, 2026-09-15: "we need retro cigarettes' machines in the strip club.
(Maybe we'll put em in other buildings too, it was the 1990s where smoking in
public was still legal in PA)", with three photos of the floor-standing
pull-knob machine of the 1970s-1990s.

Pure half (`core/cigarette_forms.py`, `core/cigarette_brands.py`): the slot
filled exactly at Deli Counter's sizes and the genome's corners, no
coincident faces, faces wound outward, the budget, the knobs real and one a
pack column, the art's bytes and what it says, the invented brands and the
denylist. Built half (bpy, skipped without it): PASS and fit, the header
the only thing lit and faintly, the display painted, determinism, variants.
"""
from __future__ import annotations

import itertools
import json
import os
import re
import struct
import zlib

import pytest

from zoo_keeper.core import cigarette_brands as CB
from zoo_keeper.core import cigarette_forms as F
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import kit
from zoo_keeper.core import prims as P

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _corners():
    return [tuple(c) for c in itertools.product(*(F.RANGES[a] for a in ("width", "depth", "height")))]


CASES = [(d, k) for d in F.DC_SIZES for k in ("chrome", "amber")] + [(c, "chrome") for c in _corners()]


@pytest.mark.parametrize("dims,knobs", CASES)
def test_the_machine_fills_its_slot_and_shares_no_plane(dims, knobs):
    w, d, h = dims
    got = F.plan(w, d, h, knobs)
    lo, hi = P.bounds(got["prims"])
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    assert all(abs(s - 1.0) < 0.005 for s in got["scale"]), got["scale"]
    assert P.coincident_pairs(got["prims"], tol=0.0022) == []   # 0.2 mm past the probe's window: a 2.0 mm gap passes here by float and fails in Blender
    for p in got["prims"]:
        assert F.signed_volume(p) > 0, (p["part"], p["mat"])
    assert P.tri_count(got["prims"]) <= genome_mod.load_species("cigarette_machine")["budgets"]["tris_lod0"]


@pytest.mark.parametrize("dims", F.DC_SIZES)
def test_the_knobs_are_real_one_a_column_and_the_front_of_the_slot(dims):
    w, d, h = dims
    got = F.plan(w, d, h)
    n = got["facts"]["n_packs"]
    assert 9 <= n <= 12
    caps = [p for p in got["prims"] if p["part"] == "Cig_Knob" and p["mat"] == "chrome"
            and max(v[1] for v in p["verts"]) < -d / 2 + 0.03]
    assert len(caps) == 2 * n
    front = min(v[1] for p in caps for v in p["verts"])
    assert front == pytest.approx(-d / 2, abs=1e-6)
    amber = F.plan(w, d, h, "amber")
    assert len([p for p in amber["prims"] if p["mat"] == "amber"]) == 2 * n
    # collision is the cabinet: the legs are under it, the knobs in front
    (c0, c1), = got["collision"]
    assert c0[2] > 0.15 * h and c1[2] == pytest.approx(h) and c0[1] > -d / 2 + 0.05


def test_the_zones_stack_to_the_cabinet_and_the_display_holds_the_rows():
    Z = F.zones(0.3, 1.2)
    names = [n for n, _f in F.ZONES]
    assert Z[names[0]][0] == pytest.approx(0.3) and Z[names[-1]][1] == pytest.approx(1.5)
    for a, b in zip(names, names[1:]):
        assert Z[a][1] == pytest.approx(Z[b][0])
    got = F.plan(*F.DC_SIZES[0])
    dx0, dx1, dz0, dz1 = got["facts"]["display"]
    for k in ("row_1", "row_2", "strip_1", "strip_2", "middle"):
        assert dz0 - 1e-9 <= got["facts"]["zones"][k][0] and got["facts"]["zones"][k][1] <= dz1 + 1e-9, k


# --- the art ---------------------------------------------------------------------------


@pytest.mark.parametrize("form", F.FORMS)
@pytest.mark.parametrize("variant", range(4))
def test_the_display_is_the_same_bytes_and_says_what_a_machine_says(form, variant):
    got = F.plan(*F.DC_SIZES[0])
    brand, _v, key, _k, cards = F.resolve({"params": {}, "module": {
        "stem": "prop_cigarette_machine_x" + ("_n%d" % variant if variant else ""), "variant": variant}})
    a = F.art(got["facts"], brand, variant, key, form, cards)
    b = F.art(got["facts"], brand, variant, key, form, cards)
    assert a["canvas"].png() == b["canvas"].png() and a["name"] == b["name"]
    assert a["name"].endswith("%08x" % (zlib.crc32(bytes(a["canvas"].buf)) & 0xFFFFFFFF))
    said = a["said"]
    assert said.count(CB.MINORS) == 2
    assert CB.PRICE[0] in said and CB.WARNING[0] in said
    assert (CB.PANEL_WORD in said) == (form == "pull_knob_split")
    assert CB.BY_ID[brand]["logo"][0] in said
    # the header is the brand's gradient: its colours, not the rows' black
    x0, y0, x1, y1 = a["rects"]["header"]
    top = CB.hex_rgb(CB.BY_ID[brand]["bg"][0])
    px = a["canvas"].get(x0 + 3, y0 + 2)
    assert sum(abs(px[i] - top[i]) for i in range(3)) < 90, (px, top)


def test_the_variants_differ_and_cards_and_knobs_follow_them():
    stem = "prop_cigarette_machine_delco_1997_01_w88_d45_h150"
    picks = [F.resolve({"params": {}, "module": {"stem": stem + ("_n%d" % v if v else ""), "variant": v}})
             for v in range(4)]
    assert len({p[0] for p in picks}) == 4
    assert [p[3] for p in picks] == ["chrome", "amber", "chrome", "amber"]
    assert [p[4] for p in picks] == [False, True, True, False]
    assert F.resolve({"params": {"brand": "delco_reds"}, "module": {"stem": "s"}})[0] == "delco_reds"
    # the middle ad differs between variants too (one brand on all four,
    # first contact sheet)
    got = F.plan(*F.DC_SIZES[0])
    middles = [F.art(got["facts"], brand, v, key, "pull_knob", cards)["brands"]["middle"]
               for v, (brand, _v, key, _k, cards) in enumerate(picks)]
    assert all(m and m != p[0] for m, p in zip(middles, picks)), middles
    middles = set(middles)
    assert len(middles) == 4, middles


def test_the_genome_and_the_kit():
    g = genome_mod.load_species("cigarette_machine")
    assert genome_mod.validate_genome(g) == []
    assert g["module_variants"] == 4
    for a in ("width", "depth", "height"):
        assert (g["dimensions"][a]["min"], g["dimensions"][a]["max"]) == F.RANGES[a]
    for form in F.FORMS:
        for v in range(4):
            dress, why = kit.honour_dressing({"form": form, "variant": v}, "cigarette_machine")
            assert not why and dress["form"] == form
    assert kit.material_tag("metal_painted", "cigarette_machine", "delco_1997") is None


# --- the invented brands ----------------------------------------------------------------


def _tokens(text):
    return set(re.findall(r"[A-Z0-9&']+", text.upper()))


def test_no_brand_is_a_real_cigarette_mark_or_its_pack():
    from zoo_keeper.core import pixel_type as pt
    from zoo_keeper.core import pixel_type_glyphs as G
    assert len(CB.BRANDS) == len(CB.BY_ID) >= 8
    for b in CB.BRANDS:
        text = CB.words(b)
        up = text.upper()
        hits = (_tokens(text) & set(CB.DENY_WORDS)) | {p for p in CB.DENY_PARTS if p in up}
        hits |= {p for p in CB.DENY_PARTS if p.replace(" ", "") in up.replace(" ", "")}
        assert not hits, (b["id"], hits)
        assert b["design"] in CB.DESIGNS and b["design"] not in CB.DENY_DESIGNS
        assert all(ch in G.GLYPHS for ch in text), text
        # the pack's name fits a pack at the display's density
        assert pt.ink_width(b["short"], 1) <= F.pack_px() - 1, b["short"]
    assert not set(CB.DESIGNS) & set(CB.DENY_DESIGNS)
    # the guard is live, and it caught the suggestion it was built around
    assert _tokens("CHESTER 100s") & set(CB.DENY_WORDS)
    assert any(p in "VIRGINIA SLIMS" for p in CB.DENY_PARTS)
    assert _tokens("NEWPORT") & set(CB.DENY_WORDS) and _tokens("MARLBORO LIGHTS") & set(CB.DENY_WORDS)
    for text in (CB.MINORS, CB.PANEL_WORD) + CB.PRICE + CB.WARNING:
        assert not _tokens(text) & set(CB.DENY_WORDS), text


# --- the built module (bpy) ---------------------------------------------------------------


def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    slot = {"slot_id": "cig", "role": "prop", "size_mod": "full", "style": 1,
            "species": "cigarette_machine", "material": "metal_painted",
            "fit": {"dims": list(dims), "pivot": "center"}}
    slot.update(fields)
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES)), key=lambda o: o.name)
    return res, objs


def _glb_json(path):
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    return json.loads(raw[20:20 + n])


def _probe(objs):
    import bpy
    import mathutils
    src = open(os.path.join(_ZOO, "tools", "coplanar_probe.py"), encoding="utf-8").read()
    ns = {"__name__": "coplanar_probe_lib"}
    exec(compile(src, "coplanar_probe.py", "exec"), ns)
    rows, _n = ns["probe"](bpy, mathutils, objs, 0.002, 1e-6, 1e-3)
    return rows


@pytest.mark.parametrize("dims,fields", [(F.DC_SIZES[0], {}), (F.DC_SIZES[1], {"form": "pull_knob_split", "variant": 1}),
                                         ((0.78, 0.4, 1.3), {}), ((1.02, 0.58, 1.75), {"variant": 3})])
def test_bpy_the_machine_passes_fits_and_shares_no_plane(tmp_path, dims, fields):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims, **fields)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    assert _probe(objs) == []
    parts = set(genome_mod.load_species("cigarette_machine")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name


def test_bpy_only_the_header_glows_and_faintly(tmp_path):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, F.DC_SIZES[0])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    lit = [m for m in doc["materials"] if m.get("emissiveFactor") and any(m["emissiveFactor"])
           or "emissiveTexture" in m]
    assert [m["name"] for m in lit] and all(m["name"].startswith("M_CigMachine_cig_") and
                                            m["name"].endswith("_Face") for m in lit)
    # below 1.0 the exporter folds the strength into the factor and writes no
    # KHR_materials_emissive_strength; above it, the factor is 1 and the
    # extension carries it (the bracket TV's 1.5)
    strength = max(lit[0]["emissiveFactor"]) * (lit[0].get("extensions") or {}).get(
        "KHR_materials_emissive_strength", {}).get("emissiveStrength", 1.0)
    assert strength == pytest.approx(F.HEADER_EMISSION, abs=1e-6) and strength < 1.0
    painted = [m for m in doc["materials"] if m["name"].endswith("_Display")]
    assert len(painted) == 1 and "baseColorTexture" in painted[0]["pbrMetallicRoughness"]
    disp = [o for o in objs if o.name == "Cig_Display"]
    assert disp and len(disp[0].data.materials) == 2
    lit_faces = [p for p in disp[0].data.polygons if p.material_index == 1]
    assert len(lit_faces) == 1
    ca = disp[0].data.color_attributes.get("Wear")
    assert ca is not None and min(min(c.color[:3]) for c in ca.data) >= 0.999


def test_bpy_the_same_file_every_build_and_four_variants_four_displays(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, F.DC_SIZES[0], variant=2)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]
    names = set()
    for v in range(4):
        out = tmp_path / ("v%d" % v)
        res, _o = _build(out, F.DC_SIZES[0], variant=v)
        doc = _glb_json(os.path.join(str(out), res["files"]["glb"]))
        arts = [i["name"] for i in doc["images"] if i["name"].startswith("cig_")]
        assert len(arts) == 1
        names.add(arts[0])
    assert len(names) == 4
