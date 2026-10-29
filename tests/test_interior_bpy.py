"""The interior species and surface stock, built in Blender.

Skipped without Blender (`bpy`), like tests/test_see_through_glass.py's bpy
half; run inside Blender 5.1 for 0.84.0. What only a build can answer:

  * a host with no stock is BYTE-IDENTICAL to the one Zoo 0.80.0 built --
    the digests below were measured on a `git archive` of main (0.80.0),
    through the kit path, theme delco_1997: every mesh object's name,
    vertex coordinates to 0.1 mm and Wear colour to 1e-4;
  * a stocked host still passes validation and keeps its slot's size and
    pivot (the stock is `dressing_objects`, measured apart);
  * each new species builds with status pass, within budget (beveled), and
    with zero coincident face pairs by tools/coplanar_probe.py's own probe.
"""
from __future__ import annotations

import hashlib
import os

import pytest

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: THE DIGEST IS ORDER-FREE (1.147.0). It hashed each object's vertices in the
#: order Blender stored them, so it pinned an ORDER as well as a shape, and two
#: deliberate releases moved the order and nothing else: 1.103.0 sorts every
#: mesh's faces so two builds write the same bytes (the factory's
#: docs/findings/grader_speed/), and a later one moved it again. Measured in
#: Blender 5.1.1 on 0.90.0 (82d23b1, the ordered pins taken on 0.80.0 still held there), 1.102.0, 1.103.0 and 1.146.0: the ordered
#: digest is each old pin until 1.102.0 and differs from 1.103.0 on, while the
#: digest below -- each object's vertex and wear lines sorted, objects sorted
#: by name -- is the same at all four for every key. So the pins are re-taken
#: in that form and still describe the shapes main built; the old ordered pins
#: are kept beside them.
#: measured on Zoo 0.80.0 (main at 295a3fe), kit path, theme delco_1997, ordered
#: (held to 1.102.0): desk 1.6 2374d64849a5..., desk 4.4 8de4dc3118a1..., table
#: 0.5 dac69cddbefb..., table 0.9 105412ce2b31..., counter 817d0c443e4f...,
#: filing_cabinet 0.9 1b2b032391e9..., filing_cabinet 2.0 64963084df6f...;
#: order-free, the same shapes:
MAIN_DIGESTS = {
    ("desk", (1.6, 0.8, 0.75)): "2ecb5b5ac26a68dd6599c4357406992c2ea1c94a",
    ("desk", (4.4, 1.5, 1.2)): "6fc0cf392e6764087830682a09f14ad70e427507",
    ("table", (1.2, 0.8, 0.5)): "8518291f11d684ed549d7a90817ca87f36aeda15",
    ("table", (4.0, 1.2, 0.9)): "bf1667ab1d115e509a9821612ed1caa1cc0f01ee",
    ("counter", (2.2, 0.8, 1.05)): "88132078c3d946c86d55cf79c700460cec033a21",
    ("filing_cabinet", (0.9, 0.5, 1.4)): "cf5bf04ea92a0f31ef4ae0e8e02a6f2457f96746",
    ("filing_cabinet", (2.0, 0.6, 1.8)): "b9e11d1a23b7fd3110785623ce59278b509168ab",
}


def _build(tmp_path, sp, dims, **fields):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import kit
    slot = {"slot_id": sp, "role": "prop", "size_mod": "full", "style": 1,
            "species": sp, "fit": {"dims": list(dims), "pivot": "center"}}
    slot.update(fields)
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES)), key=lambda o: o.name)
    return res, objs


def _digest(objs):
    """Every object's name, vertices and wear, in no stored order (see
    `MAIN_DIGESTS`)."""
    rows = []
    for o in sorted(objs, key=lambda o: o.name):
        vs = sorted("%.4f,%.4f,%.4f" % tuple(v.co) for v in o.data.vertices)
        ca = o.data.color_attributes.get("Wear")
        ws = sorted("%.4f" % c.color[0] for c in ca.data) if ca else []
        rows.append("%s|%s|%s|" % (o.name, ";".join(vs), ",".join(ws)))
    return hashlib.sha1("\n".join(rows).encode()).hexdigest()


def _probe(objs):
    import bpy
    import mathutils
    src = open(os.path.join(_ZOO, "tools", "coplanar_probe.py"), encoding="utf-8").read()
    # The probe calls `main()` only as __main__ (0.83.0), so the whole file
    # loads as a library under any other name; cutting the source at its last
    # `main()` would now leave that `if` without a body.
    ns = {"__name__": "coplanar_probe_lib"}
    exec(compile(src, "coplanar_probe.py", "exec"), ns)
    rows, _n = ns["probe"](bpy, mathutils, objs, 0.002, 1e-6, 1e-3)
    return rows


@pytest.mark.parametrize("key", sorted(MAIN_DIGESTS), ids=lambda k: "%s-%s" % k)
def test_bpy_host_without_stock_is_what_main_built(tmp_path, key):
    pytest.importorskip("bpy")
    sp, dims = key
    res, objs = _build(tmp_path, sp, dims)
    assert _digest(objs) == MAIN_DIGESTS[key]
    assert not any(o.name.startswith("Stock_") for o in objs)


@pytest.mark.parametrize("sp,dims", [("desk", (1.6, 0.8, 0.75)), ("table", (1.2, 0.8, 0.74)),
                                     ("counter", (2.2, 0.8, 1.05)),
                                     ("filing_cabinet", (0.9, 0.5, 1.4))])
@pytest.mark.parametrize("fl", ("office", "bar", "kitchen", "vault", "storage"))
def test_bpy_stocked_host_keeps_its_slot(tmp_path, sp, dims, fl):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, sp, dims, stock=fl, variant=1)
    assert res["stem"].endswith("_s%s_n1" % fl)
    assert res["report"]["status"] != "fail", res["report"]["checks"]
    assert any(o.name.startswith("Stock_") for o in objs)
    assert max(abs(c) for c in res["facts"]["center"]) <= 0.02
    same = [r for r in _probe(objs) if r["facing"] == "SAME"
            and ("Stock_" in r["a"] or "Stock_" in r["b"])]
    assert same == []


@pytest.mark.parametrize("sp,dims,fields", [
    ("carton_stack", (1.2, 0.8, 1.4), {}), ("carton_stack", (1.6, 1.2, 1.8), {"variant": 3}),
    ("furnace", (0.9, 1.0, 2.4), {"form": "furnace"}), ("furnace", (0.6, 0.6, 2.4), {}),
    ("dust_sheet", (1.0, 0.9, 0.95), {}), ("dust_sheet", (3.2, 1.6, 2.2), {"variant": 2}),
    ("pool_table", (2.0, 1.14, 0.79), {}), ("pool_table", (2.8, 1.6, 0.84), {"variant": 2}),
    ("booth_seat", (4.0, 1.6, 1.4), {"form": "booth"}), ("booth_seat", (2.0, 0.9, 0.85), {}),
])
def test_bpy_species_builds_clean(tmp_path, sp, dims, fields):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, sp, dims, **fields)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    assert res["facts"]["tris"] <= res["plan"]["budgets"]["tris_lod0"]
    assert _probe(objs) == []
    first = _digest(objs)          # before the rebuild clears the scene
    _again, objs2 = _build(tmp_path, sp, dims, **fields)
    assert _digest(objs2) == first
