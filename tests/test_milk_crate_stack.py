"""1.14.0 -- a stack of plastic milk crates, for the walk-in coolers.

Grown because Deli Counter 0.149.0 furnishes walk-ins with `milk_crates` and
its `test_furnish` refuses a furnished piece that routes to no species. Pure
half: the stack fills its slot exactly at Deli Counter's piece sizes and the
genome's corners, no two faces share a plane, every face is wound outward,
the crates are hollow. Built half (bpy): PASS and fit, one submission, the
colour by variant.
"""
from __future__ import annotations

import itertools
import os

import pytest

from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import milk_crate_forms as M
from zoo_keeper.core import prims as P

CASES = list(M.DC_SIZES) + [tuple(c) for c in itertools.product(*(M.RANGES[a] for a in ("width", "depth", "height")))]


@pytest.mark.parametrize("dims", CASES)
def test_the_stack_fills_its_slot_and_shares_no_plane(dims):
    w, d, h = dims
    pr = M.plan(w, d, h)["prims"]
    lo, hi = P.bounds(pr)
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    assert P.coincident_pairs(pr, tol=0.0022) == []
    for p in pr:
        assert M.signed_volume(p) > 0
    assert P.tri_count(pr) <= genome_mod.load_species("milk_crate_stack")["budgets"]["tris_lod0"]


def test_the_crates_are_hollow_and_nest():
    g = M.plan(0.35, 0.35, 1.0)
    f = g["facts"]
    assert (f["cols"], f["rows"], f["layers"]) == (1, 1, 4)
    assert len(g["prims"]) == 5 * f["crates"]
    # each crate's plate is well inside its walls: an open crate, not a block
    plates = [p for k, p in enumerate(g["prims"]) if k % 5 == 4]
    for p in plates:
        xs = [v[0] for v in p["verts"]]
        assert max(xs) - min(xs) < 0.35 - 0.05
    # a crate above sits into the one below
    zs = sorted(min(v[2] for v in p["verts"]) for p in plates)
    ch = 1.0 / 4
    assert zs[1] == pytest.approx(ch - M.NEST)


def test_the_genome_validates():
    g = genome_mod.load_species("milk_crate_stack")
    assert genome_mod.validate_genome(g) == []
    for w, d, h in M.DC_SIZES:
        r = g["dimensions"]
        assert r["width"]["min"] <= w <= r["width"]["max"] and r["depth"]["min"] <= d <= r["depth"]["max"]
        assert r["height"]["min"] <= h <= r["height"]["max"]


def _build(tmp_path, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "milk_crates_r0_1", "role": "prop", "size_mod": "full", "style": 1,
            "species": "milk_crate_stack", "material": "plastic",
            "fit": {"dims": list(dims), "pivot": "center"}}
    slot.update(fields)
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == [], plan["dressing_fallbacks"]
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES)), key=lambda o: o.name)
    return res, objs


@pytest.mark.parametrize("dims", M.DC_SIZES)
def test_bpy_the_stack_passes_fits_and_is_one_submission(tmp_path, dims):
    pytest.importorskip("bpy")
    import json
    import struct
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    doc = json.loads(raw[20:20 + n])
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert len(doc["materials"]) == 1 and sum(len(m["primitives"]) for m in visual) == 1
