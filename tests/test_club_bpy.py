"""The club species (0.87.0) built in Blender, through the kit path.

Skipped without `bpy`; run inside Blender 5.1.1. What only a build answers:

  * every species validates PASS at its genome's min, default and max, fits
    the slot, stays inside its budget and names only genome parts;
  * `tools/coplanar_probe.py`'s own probe finds no coincident faces;
  * two builds write the same geometry, wear and materials;
  * the light is where it is promised and nowhere else -- the rope light,
    the neon's two tube colours and a bracket TV's screen are emissive
    materials named ``M_*_Face`` (Lux's power cut), their COLOR_0 is white
    (so Level Factory's import leaves their albedo alone), and the exported
    GLB carries them as glTF emissive;
  * the dressing fields change the module: bar stock stands on a stage's bar
    and a cocktail table, and the stock is measured apart from the slot;
  * what already shipped is unchanged: booth_seat's sofa, the pool table and
    a stocked table, the digests measured on a `git archive` of Zoo 0.86.0
    (5b15338). crt_tv's stand form changed ON PURPOSE in 0.90.0 (its knobs
    hung 22 mm past the slot and its screen was inside the body); its
    digests are 0.90.0's, the 0.86.0 ones kept beside them.

The bracket TV's lit screen is a picture since 0.90.0 and is tested in
tests/test_crt_screens.py.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct

import pytest

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: measured on Zoo 0.86.0 (5b15338), kit path, theme delco_1997, flat
#: materials: object names, vertices to 0.1 mm, Wear to 1e-4, material names
MAIN_DIGESTS = {
    # 0.86.0 - 0.89.0, the stand set that failed `fit_depth`:
    #   (0.55, 0.5, 0.42) ca85dce48259f1b238fcabd387b3033de8b0446f
    #   (0.9, 0.62, 0.7)  3f8cc9bbf7137bb708a200673bf0a86f28b35b86
    # 0.90.0, measured on the first build of `crt_forms.stand_layout`:
    ("crt_tv", (0.55, 0.5, 0.42), ()): "ea931596f371006cdda67be9e6f4f6a1bde869f6",
    ("crt_tv", (0.9, 0.62, 0.7), ()): "13598510af7123b6ce3b4d87fb04d93036c8ecbd",
    ("booth_seat", (2.0, 0.9, 0.85), (("form", "sofa"),)): "13cba2a4abf87dbfe4be1dc10e75cbefeefe8438",
    ("pool_table", (2.0, 1.14, 0.79), ()): "c904dc4002de72713a3111dd26b0787d8c18dbb1",
    ("table", (1.2, 0.8, 0.74), (("stock", "bar"), ("variant", 1))): "1a8cc276ae4b5d5ccb2c4bcde9bf008c05d128a6",
}

LIT = {"club_stage": 1, "neon_sign": 2, "crt_tv": 1}


def _genome(sp):
    from zoo_keeper.core import genome
    return genome.load_species(sp)


def _corners(sp):
    dims = _genome(sp)["dimensions"]
    return [tuple(dims[a][k] for a in ("width", "depth", "height")) for k in ("min", "default", "max")]


def _build(tmp_path, sp, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": sp, "role": "prop", "size_mod": "full", "style": 1,
            "species": sp, "fit": {"dims": list(dims), "pivot": "center"}}
    slot.update(fields)
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES)), key=lambda o: o.name)
    return res, objs


def _digest(objs):
    h = hashlib.sha1()
    for o in objs:
        h.update(o.name.encode())
        for v in o.data.vertices:
            h.update(("%.4f,%.4f,%.4f;" % tuple(v.co)).encode())
        ca = o.data.color_attributes.get("Wear")
        if ca:
            for c in ca.data:
                h.update(("%.4f" % c.color[0]).encode())
        for s in o.material_slots:
            h.update((s.material.name if s.material else "-").encode())
    return h.hexdigest()


def _probe(objs):
    import bpy
    import mathutils
    src = open(os.path.join(_ZOO, "tools", "coplanar_probe.py"), encoding="utf-8").read()
    ns = {"__name__": "coplanar_probe_lib"}
    exec(compile(src, "coplanar_probe.py", "exec"), ns)
    rows, _n = ns["probe"](bpy, mathutils, objs, 0.002, 1e-6, 1e-3)
    return rows


def _lit_objects(objs):
    return [o for o in objs if any(s.material and s.material.name.endswith("_Face")
                                   for s in o.material_slots)]


def _glb_json(path):
    raw = open(path, "rb").read()
    assert raw[:4] == b"glTF"
    ln, kind = struct.unpack_from("<I4s", raw, 12)
    assert kind == b"JSON"
    return json.loads(raw[20:20 + ln])


_CASES = ([("club_stage", d, {"form": f}) for d in _corners("club_stage")
           for f in ("round", "runway", "bar_stage")]
          + [("cocktail_table", d, {"form": f, "stock": "bar", "variant": 2})
             for d in _corners("cocktail_table") for f in ("cloth", "bare")]
          + [("club_chair", d, {"variant": 1}) for d in _corners("club_chair")]
          + [("bar_stool", d, {"variant": 2}) for d in _corners("bar_stool")]
          + [("neon_sign", d, {"variant": 3}) for d in _corners("neon_sign")]
          + [("crt_tv", d, {"form": "bracket"}) for d in _corners("crt_tv")])


def _id(c):
    return "%s-%s-%s" % (c[0], "x".join("%g" % v for v in c[1]), "-".join(str(v) for v in c[2].values()))


@pytest.mark.parametrize("case", _CASES, ids=_id)
def test_bpy_builds_pass_fit_budget_parts_and_no_shared_planes(tmp_path, case):
    pytest.importorskip("bpy")
    sp, dims, fields = case
    res, objs = _build(tmp_path, sp, dims, **fields)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    assert abs(got["width"] - dims[0]) <= 0.001 and abs(got["depth"] - dims[1]) <= 0.001
    assert abs(got["height"] - dims[2]) <= 0.001, got
    assert res["facts"]["tris"] <= res["plan"]["budgets"]["tris_lod0"]
    parts = _genome(sp)["parts"]
    for o in objs:
        if o.name.startswith("Stock_"):
            continue
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
    assert _probe([o for o in objs if not o.name.startswith("Stock_")]) == []
    lit = _lit_objects(objs)
    want = LIT.get(sp, 0)
    mats = {s.material.name for o in lit for s in o.material_slots}
    if sp == "neon_sign":
        assert len(mats) == 2
    assert bool(lit) == bool(want), [o.name for o in lit]
    for o in lit:
        ca = o.data.color_attributes.get("Wear")
        assert ca is not None and min(min(c.color[:3]) for c in ca.data) >= 0.999, o.name


@pytest.mark.parametrize("sp,dims,fields", [
    ("club_stage", (8.0, 4.0, 3.6), {"form": "bar_stage", "stock": "bar", "variant": 1}),
    ("cocktail_table", (0.75, 0.75, 0.74), {"stock": "bar", "variant": 2}),
    ("neon_sign", (1.4, 0.1, 0.6), {"variant": 19}),
    ("club_chair", (0.95, 0.9, 0.95), {"variant": 3}),
    ("crt_tv", (0.55, 0.62, 0.5), {"form": "bracket"}),
])
def test_bpy_the_same_module_every_build(tmp_path, sp, dims, fields):
    pytest.importorskip("bpy")
    _res, objs = _build(tmp_path, sp, dims, **fields)
    first = _digest(objs)
    _res2, objs2 = _build(tmp_path, sp, dims, **fields)
    assert _digest(objs2) == first


@pytest.mark.parametrize("sp,dims,fields", [
    ("club_stage", (8.0, 4.0, 3.6), {"form": "bar_stage", "stock": "bar", "variant": 1}),
    ("cocktail_table", (0.75, 0.75, 0.74), {"form": "bare", "stock": "bar", "variant": 1}),
])
def test_bpy_bar_stock_stands_on_the_top_and_is_measured_apart(tmp_path, sp, dims, fields):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, sp, dims, **fields)
    stock = [o for o in objs if o.name.startswith("Stock_")]
    assert stock and res["report"]["status"] == "pass"
    assert max(abs(c) for c in res["facts"]["center"]) <= 0.002
    _bare, objs0 = _build(tmp_path, sp, dims, form=fields["form"]) if "form" in fields else _build(tmp_path, sp, dims)
    assert not any(o.name.startswith("Stock_") for o in objs0)


def _lit_table():
    from zoo_keeper.core import club_forms, club_names
    rope_rgb, rope_s = club_forms.STAGE_EMISSIVE["rope"]
    pink, blue = club_names.palette_for(0)
    return {"M_ClubStage_rope_Face": max(rope_rgb) * rope_s,
            "M_NeonSign_ff0f52_Face": max(pink) * club_names.NEON_STRENGTH,
            "M_NeonSign_1a47ff_Face": max(blue) * club_names.NEON_STRENGTH}


@pytest.mark.parametrize("sp,dims,fields,names", [
    ("club_stage", (4.0, 4.0, 3.6), {"form": "round"}, ("M_ClubStage_rope_Face",)),
    ("neon_sign", (1.4, 0.1, 0.6), {"variant": 0}, ("M_NeonSign_ff0f52_Face", "M_NeonSign_1a47ff_Face")),
])
def test_bpy_the_exported_glb_carries_the_emission(tmp_path, sp, dims, fields, names):
    pytest.importorskip("bpy")
    res, _objs = _build(tmp_path, sp, dims, **fields)
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    by = {m["name"]: m for m in doc["materials"]}
    for n in names:
        m = by[n]
        # the exporter folds a strength that fits into the factor (the 1.2
        # screen came back as 0.32 x 1.2 = 0.384 with no extension) and
        # writes KHR_materials_emissive_strength only past 1.0 of factor
        strength = (m.get("extensions") or {}).get("KHR_materials_emissive_strength", {})
        lit = max(m.get("emissiveFactor", [0, 0, 0])) * strength.get("emissiveStrength", 1.0)
        # the declared colour x strength, whichever way the exporter split it
        # (a fixed floor of 0.35 was written against the first strengths and
        # failed the screen once it was dimmed to 0.35)
        assert lit == pytest.approx(_lit_table()[n], rel=0.02), m
    unlit = [k for k, m in by.items() if not k.endswith("_Face")]
    assert all(max(by[k].get("emissiveFactor", [0, 0, 0])) == 0 for k in unlit)


@pytest.mark.parametrize("key", sorted(MAIN_DIGESTS), ids=lambda k: "%s-%s" % (k[0], k[1]))
def test_bpy_what_shipped_before_is_what_main_built(tmp_path, key):
    pytest.importorskip("bpy")
    sp, dims, fields = key
    _res, objs = _build(tmp_path, sp, dims, **dict(fields))
    assert _digest(objs) == MAIN_DIGESTS[key]


def test_bpy_no_collision_on_a_neon_sign_and_a_collider_on_the_stage(tmp_path):
    bpy = pytest.importorskip("bpy")
    _build(tmp_path, "neon_sign", (1.4, 0.1, 0.6), variant=5)
    assert not [o for o in bpy.context.scene.objects if o.name.endswith("-colonly")]
    _build(tmp_path, "club_stage", (4.0, 4.0, 3.6), form="round")
    assert [o for o in bpy.context.scene.objects if o.name.endswith("-colonly")]
