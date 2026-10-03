"""street_tree: minted 2026-09-12 by tools/new_species.py (roadmap 150)."""
import os

import pytest

from zoo_keeper.core import genome, kit


def test_street_tree_is_discovered_and_validates():
    assert "street_tree" in genome.list_species()
    assert genome.validate_genome(genome.load_species("street_tree")) == []


def test_street_tree_plans_at_its_authored_dims():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "street_tree_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "street_tree",
        "fit": {"dims": [4.0, 4.0, 6.0], "pivot": "center"}}]},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "street_tree"



def _glb_json(path):
    import json
    import struct
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    return json.loads(raw[20:20 + n])


def _glb_bin(path):
    import struct
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    off = 20 + n
    m = struct.unpack("<I", raw[off:off + 4])[0]
    return raw[off + 8:off + 8 + m]


def _accessor(doc, raw_bin, idx):
    import struct
    acc = doc["accessors"][idx]
    bv = doc["bufferViews"][acc["bufferView"]]
    n = {"VEC2": 2, "VEC3": 3, "SCALAR": 1}[acc["type"]]
    off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = bv.get("byteStride", 4 * n)
    return [struct.unpack_from("<%df" % n, raw_bin, off + i * stride) for i in range(acc["count"])]


def test_bpy_the_crown_carries_its_sway_weight_against_its_own_height(tmp_path):
    """1.56.0: the shipped crown's TEXCOORD_1.x is each vertex's height
    over the crown's, squared -- read against the crown's OWN vertices as
    shipped, after the re-centring and the fit -- and .y is a phase in
    [0, 1); the wood and the grate carry no second UV set."""
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import tree_forms
    slot = {"slot_id": "london_plane", "role": "prop", "size_mod": "full", "style": 1,
            "species": "london_plane", "material": "wood",
            "fit": {"dims": [5.0, 5.0, 6.5], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    path = os.path.join(str(tmp_path), res["files"]["glb"])
    doc = _glb_json(path)
    raw = _glb_bin(path)
    seen = {}
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            has = "TEXCOORD_1" in prim["attributes"]
            seen[mesh["name"]] = has
            if not has:
                continue
            pos = _accessor(doc, raw, prim["attributes"]["POSITION"])
            uv2 = _accessor(doc, raw, prim["attributes"]["TEXCOORD_1"])
            y0 = min(v[1] for v in pos)
            y1 = max(v[1] for v in pos)
            off = [abs(u[0] - tree_forms.sway_weight(v[1], y0, y1)) for v, u in zip(pos, uv2)]
            assert max(off) < 1e-3, max(off)
            assert all(0.0 <= u[1] < 1.0 + 1e-6 for u in uv2)
            assert len({round(u[1], 4) for u in uv2}) >= 10          # many clusters, their own phases
    assert [n for n, h in seen.items() if h] == ["StreetTree_Crown"], seen
