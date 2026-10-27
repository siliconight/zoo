"""1.133.0 -- `snack_gondola`'s `grocery` form: a supermarket's gondola that sells what the sign over its lane says.

The walker's grocery comps (the factory's docs/reference/GROCERY_STORE_COMPS.md): "shiny floor, bright lights,
isles, glowing freezer section, stacked high"; the supermarket's gondolas sold the convenience store's chips under
markers that said CEREAL and CANNED VEG. Pure half (`core/snack_gondola_forms.py`, `core/grocery_brands.py`): every
category a marker prints is stocked; the variant is the gondola's line, its two faces the categories either side of
it; the module fills its slot, no two faces share a plane, every solid is wound outward; each face sells its own
category, cans stack; every product face maps into the form's own image; the products are invented and legible.
Built half (bpy, skipped without it): PASS, two submissions, the grocery image.

FAILS ON 1.132.0: `grocery_brands` does not exist.
"""
from __future__ import annotations

import itertools
import re

import pytest

from zoo_keeper.core import card_brands as KB
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import grocery_brands as GB
from zoo_keeper.core import prims as P
from zoo_keeper.core import snack_gondola_forms as S

#: Deli Counter's supermarket gondolas (`gondola_run`), then the genome's corners
DC_RUNS = ((14.0, 1.4, 1.45), (9.6, 1.4, 1.45), (7.2, 1.4, 1.45))
CORNERS = [tuple(c) for c in itertools.product(*(S.RANGES[a] for a in ("width", "depth", "height")))]


def _brand(p):
    return p["uvs"][p["front"][0]][0][0][len("tile_"):]


def test_every_category_a_marker_prints_is_stocked():
    said = [c for lane in KB.GROCERY_AISLE_SAYS for c in lane]
    assert list(S.GROCERY_CATEGORIES) == said
    assert list(GB.CATEGORIES) == said
    for cat in said:
        pack, _items = GB.CATEGORIES[cat]
        assert pack in S.GROCERY_PACKS and pack in S.GROCERY_TILES, cat
        assert len(S.grocery_ids(cat)) >= 2, cat


def test_a_line_sells_the_categories_either_side_of_it():
    """Line n stands between lane n - 1 and lane n: its faces sell category 2n - 1 (the second of the lane before)
    and 2n (the first of the lane after). Twelve lines sell all 24 categories, each once."""
    flat = S.GROCERY_CATEGORIES
    seen = []
    for v in range(12):
        a, b = S.grocery_faces(v)
        assert b == KB.GROCERY_AISLE_SAYS[v][0]
        assert a == KB.GROCERY_AISLE_SAYS[v - 1][1]
        seen += [a, b]
    assert sorted(seen) == sorted(flat)
    assert genome_mod.load_species("snack_gondola")["module_variants"] == 12


@pytest.mark.parametrize("dims,variant", [(d, v) for d in DC_RUNS for v in range(12)]
                         + [(c, v) for c in CORNERS for v in (0, 7)])
def test_the_grocery_gondola_fills_its_slot_and_shares_no_plane(dims, variant):
    w, d, h = dims
    pr = S.plan(w, d, h, "snack_gondola", variant, "grocery")["prims"]
    lo, hi = P.bounds(pr)
    for a, b in ((lo[0], -w / 2), (hi[0], w / 2), (lo[1], -d / 2), (hi[1], d / 2), (lo[2], 0.0), (hi[2], h)):
        assert abs(a - b) < 1e-6, (dims, lo, hi)
    assert P.coincident_pairs(pr, tol=0.0022) == []
    for p in pr:
        assert S.signed_volume(p) > 0, (p["part"], p["mat"])
    assert P.tri_count(pr) <= genome_mod.load_species("snack_gondola")["budgets"]["tris_lod0"]


def test_each_face_sells_its_own_category_and_the_end_caps_cereal():
    w, d, h = DC_RUNS[0]
    for v in range(12):
        g = S.plan(w, d, h, "snack_gondola", v, "grocery")
        f = g["facts"]
        a, b = S.grocery_faces(v)
        assert f["faces"] == (a, b) and f["form"] == "grocery"
        ids = {"a": set(S.grocery_ids(a)), "b": set(S.grocery_ids(b)), "cap": set(S.grocery_ids("CEREAL"))}
        for p in (q for q in g["prims"] if q["mat"] == "bag"):
            cx = sum(q[0] for q in p["verts"]) / len(p["verts"])
            cy = sum(q[1] for q in p["verts"]) / len(p["verts"])
            where = "cap" if abs(cx) > f["run"] / 2.0 else ("a" if cy < 0 else "b")
            assert _brand(p) in ids[where], (v, where, _brand(p))
        assert set(f["stock"]) == {a, b, "CEREAL"} | ({"CEREAL"} if a == b else set())
        assert sum(f["stock"].values()) == f["bags"]


def test_a_products_printed_front_looks_at_the_shopper():
    """The faces carrying a product's tile look away from the gondola: -Y on face a, +Y on face b."""
    w, d, h = DC_RUNS[2]
    for v in range(12):
        g = S.plan(w, d, h, "snack_gondola", v, "grocery")
        run = g["facts"]["run"]
        for p in (q for q in g["prims"] if q["mat"] == "bag"):
            cx = sum(q[0] for q in p["verts"]) / len(p["verts"])
            if abs(cx) > run / 2.0:
                continue
            cy = sum(q[1] for q in p["verts"]) / len(p["verts"])
            assert p["front"]
            for k in p["front"]:
                a, b, c = (p["verts"][i] for i in p["faces"][k][:3])
                u = [b[j] - a[j] for j in range(3)]
                t = [c[j] - a[j] for j in range(3)]
                ny = u[2] * t[0] - u[0] * t[2]
                assert ny * cy > 0, (v, cy, ny)


def test_cans_stack_as_high_as_the_shelf_takes_them():
    """The comps' "stacked high": on Deli Counter's 1.45 m gondola a shelf's clearance takes two cans."""
    w, d, h = DC_RUNS[0]
    v = next(v for v in range(12) if "CANNED VEG" in S.grocery_faces(v))
    g = S.plan(w, d, h, "snack_gondola", v, "grocery")
    cans = [p for p in g["prims"] if p["mat"] == "bag" and len(p["faces"]) == 8]
    feet = sorted({round(min(q[2] for q in p["verts"]), 3) for p in cans})
    levels, pitch = S.shelf_levels(h)
    assert len(feet) >= 2 * len(levels), (feet, levels)
    assert P.tri_count(cans[:1]) == 20


def test_the_hexagons_are_their_width_along_the_shelf():
    for fn, tris in ((S.can, 20), (S.jar, 44), (S.bottle, 44)):
        p = fn(0.0, 0.0, 0.0, 0.10, 0.2, "x")
        xs = [v[0] for v in p["verts"]]
        ys = [v[1] for v in p["verts"]]
        assert abs(max(xs) - 0.05) < 1e-9 and abs(min(xs) + 0.05) < 1e-9
        assert abs(min(ys) - 0.0) < 1e-9                      # the front flat on y_front
        assert S.signed_volume(p) > 0 and P.tri_count([p]) == tris
        assert len(p["front"]) == 3


def test_every_product_face_maps_into_the_grocery_image():
    art = S.grocery_art()
    for v in range(12):
        for p in (q for q in S.plan(*DC_RUNS[2], "snack_gondola", v, "grocery")["prims"] if q["mat"] == "bag"):
            assert len(p["uvs"]) == len(p["faces"])
            fronts = [c for k in p["front"] for c in p["uvs"][k]]
            assert all(c[0].startswith("tile_") and c[0] in art["rects"] for c in fronts)
            assert all(0.0 <= c[1] <= 1.0 and 0.0 <= c[2] <= 1.0 for c in fronts)
            others = [c for k, f in enumerate(p["uvs"]) if k not in p["front"] for c in f]
            assert all(c[0].startswith("solid_") and c[0] in art["rects"] for c in others)


def test_the_grocery_image_is_its_own_and_the_same_bytes():
    a, b = S.grocery_art(), S.grocery_art()
    assert bytes(a["canvas"].buf) == bytes(b["canvas"].buf) and a["name"] == b["name"]
    assert a["name"].startswith("grocery_") and a["name"] != S.bag_art()["name"]
    W, H = a["size"]
    tiles = list(a["rects"].items())
    for n, (x0, y0, x1, y1) in tiles:
        assert 0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H, n
    for (n, r), (m, q) in itertools.combinations(tiles, 2):
        assert r[2] <= q[0] or q[2] <= r[0] or r[3] <= q[1] or q[3] <= r[1], (n, m)
    for cat in S.GROCERY_CATEGORIES:
        for i in S.grocery_ids(cat):
            assert "tile_" + i in a["rects"] and "solid_" + i in a["rects"], i
    for p in GB.PRODUCTS:
        assert p["short"] in a["said"], p["id"]
    assert GB.PASTA_MARK in a["said"]


def test_every_grocery_is_invented_and_legible():
    ids = set()
    for p in GB.PRODUCTS:
        assert p["id"] not in ids, p["id"]
        ids.add(p["id"])
        assert 1 <= len(p["short"]) <= GB.SHORT_MAX, p["short"]
        up = GB.words(p).upper()
        toks = set(re.findall(r"[A-Z0-9&'!.-]+", up))
        for w_ in GB.DENY_WORDS:
            assert w_ not in toks, (p["id"], w_)
        for part in GB.DENY_PARTS:
            assert part not in up, (p["id"], part)
    assert "WAWA" not in " ".join(GB.words(p).upper() for p in GB.PRODUCTS)


def test_the_form_is_read_off_the_module_or_its_params():
    assert S.form_of({"module": {"form": "grocery"}}) == "grocery"
    assert S.form_of({"params": {"form": "grocery"}}) == "grocery"
    assert S.form_of({"module": {"form": None}, "params": {"form": ["auto"]}}) == "snack"
    g = genome_mod.load_species("snack_gondola")
    assert genome_mod.validate_genome(g) == []
    assert g["params"]["form"] == ["auto", "grocery"]


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _glb_json(path):
    import json
    import struct
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    return json.loads(raw[20:20 + n])


def test_bpy_a_grocery_gondola_passes_in_two_submissions_on_its_own_image(tmp_path):
    """The same submissions as the snack form: the steel and the products, the products on the grocery image."""
    pytest.importorskip("bpy")
    import os
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import kit, partnames
    slot = {"slot_id": "gondola_run_1", "role": "prop", "size_mod": "full", "style": 1,
            "species": "snack_gondola", "material": "metal", "form": "grocery", "variant": 2,
            "fit": {"dims": list(DC_RUNS[2]), "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == [], plan["dressing_fallbacks"]
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    assert len(doc["materials"]) == 2, [m["name"] for m in doc["materials"]]
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 2, [m["name"] for m in visual]
    names = [m["name"] for m in doc["materials"]]
    assert any(n.startswith("M_Snack_grocery_") for n in names), names
    assert not any(n.startswith("M_Snack_snackbags_") for n in names), names
