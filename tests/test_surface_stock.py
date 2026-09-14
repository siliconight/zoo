"""Surface stock (0.84.0): what is left out on a desk, a table, a counter
or a filing cabinet, and the slot fields that ask for it.

The planner's rules (`recipes/_surface_stock.py`): nothing overhangs the
top, nothing shares a plane with another item or with the top, every body
finish contrasts with every host colour, same seed same top. The contract
(`kit.DRESSING_FIELDS`): ``stock``, ``variant`` and ``form`` name distinct
module files only when the built species honours them, all or nothing, and
a slot without them plans exactly what it planned before.

That a host with ``stock`` none builds byte-identical geometry to Zoo 0.80.0
is a Blender measurement, pinned in tests/test_interior_bpy.py.
"""
from __future__ import annotations

import json
import os
import random

import pytest

from zoo_keeper.core import dna, genome, kit
from zoo_keeper.core import prims as P
from zoo_keeper.recipes import _surface_stock as S

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOSTS = ("desk", "table", "counter", "filing_cabinet")

#: (x0, x1, y0, y1, z0, facing): a desk bay, a long desk bay, a filing
#: cabinet top, a coffee table, a counter bay, a small table
TOPS = [(-0.8, 0.8, -0.4, 0.4, 0.75, 0.0), (-1.1, 1.1, -0.4, 0.4, 0.75, 3.14159),
        (-0.45, 0.45, -0.2, 0.25, 1.4, 0.0), (-0.6, 0.6, -0.4, 0.4, 0.5, None),
        (-1.0, 1.0, -0.45, 0.45, 1.05, None), (-0.5, 0.5, -0.3, 0.3, 0.9, None)]
SEEDS = range(10)


def _plan(fl, top, seed, host=(0.55, 0.4, 0.26), keep=()):
    x0, x1, y0, y1, z0, facing = top
    return S.plan_surface(random.Random(seed), fl, x0, x1, y0, y1, z0,
                          host_rgb=list(host), facing=facing, keep_out=keep)


@pytest.mark.parametrize("fl", S.FLAVOURS)
@pytest.mark.parametrize("top", TOPS, ids=lambda t: "x".join("%g" % v for v in t[:5]))
def test_items_within_the_top_no_overhang(fl, top):
    x0, x1, y0, y1, z0, _f = top
    for seed in SEEDS:
        got = _plan(fl, top, seed)
        assert got["items"], (fl, seed, "a top with room got nothing")
        for p in got["prims"]:
            for x, y, z in p["verts"]:
                assert x0 + S.EDGE - 1e-9 <= x <= x1 - S.EDGE + 1e-9, (fl, seed, p["part"])
                assert y0 + S.EDGE - 1e-9 <= y <= y1 - S.EDGE + 1e-9, (fl, seed, p["part"])
                assert z >= z0 - 0.02, (fl, seed, p["part"], z)
        # every item stands on the top: its lowest faces SINK into it
        for it in got["items"]:
            assert it["top"] > z0


@pytest.mark.parametrize("fl", S.FLAVOURS)
@pytest.mark.parametrize("top", TOPS, ids=lambda t: "x".join("%g" % v for v in t[:5]))
def test_no_face_shares_a_plane_with_another_or_the_top(fl, top):
    x0, x1, y0, y1, z0, _f = top
    host = P.box("Host_Top", "top", (x0, y0, z0 - 0.03), (x1, y1, z0))
    for seed in SEEDS:
        rows = P.coincident_pairs(_plan(fl, top, seed)["prims"] + [host])
        assert rows == [], (fl, seed, rows[:4])


def test_footprints_keep_their_gap():
    for fl in S.FLAVOURS:
        for seed in SEEDS:
            polys = [it["poly"] for it in _plan(fl, TOPS[4], seed)["items"]]
            for i in range(len(polys)):
                for j in range(i + 1, len(polys)):
                    assert P.poly_separated(polys[i], polys[j], S.MIN_GAP - 1e-9)


def test_same_seed_same_top_and_seeds_differ():
    a = _plan("office", TOPS[0], 3)
    assert a == _plan("office", TOPS[0], 3)
    assert len({json.dumps(_plan("bar", TOPS[4], s)["prims"]) for s in SEEDS}) == len(SEEDS)


def test_off_kilter_by_rule():
    """Items are turned off their cluster's line (no top of ten comes out
    with every item square to the table) and never by more than the rule
    allows plus the cluster's own 4 degrees and a group's authored turn."""
    import math
    turned = 0
    for seed in SEEDS:
        for it in _plan("office", TOPS[0], seed)["items"]:
            (ax, ay), (bx, by) = it["poly"][0], it["poly"][1]
            ang = math.degrees(math.atan2(by - ay, bx - ax)) % 90.0
            if min(ang, 90.0 - ang) > 0.5:
                turned += 1
    assert turned >= 10


def test_keep_out_is_kept():
    for seed in SEEDS:
        got = _plan("bar", TOPS[4], seed, keep=((0.0, 0.0, 0.22),))
        square = P.rect_poly(0.0, 0.0, 0.44, 0.44, 0.0)
        for it in got["items"]:
            assert P.poly_separated(it["poly"], square, 0.0)


def test_unknown_flavour_and_tiny_top_are_empty():
    assert _plan("florist", TOPS[0], 1)["prims"] == []
    assert S.plan_surface(random.Random(1), "office", 0, 0.1, 0, 0.1, 0.7)["prims"] == []


def _host_colours():
    out = []
    for sp, k in (("desk", 1.0), ("table", 1.0), ("counter", 0.85), ("filing_cabinet", 1.0)):
        g = json.load(open(os.path.join(_ZOO, "zoo_keeper", "genome", "species", sp + ".json"),
                           encoding="utf-8"))
        out += [(sp, name, [c * k for c in st["color"]]) for name, st in g["styles"].items()]
    return out


def test_every_body_finish_contrasts_with_every_host_style():
    """Luminance ratio >= 1.4, `_shelf_stock`'s number, for the candidate
    `resolve_finish` picks. Details (a screen in a monitor, foam on a pint)
    sit on their own item and are listed in DETAIL_FINISHES."""
    hosts = _host_colours()
    assert len(hosts) >= 30
    for finish in S.FINISHES:
        if finish in S.DETAIL_FINISHES:
            continue
        for sp, name, colour in hosts:
            _i, rgb = S.resolve_finish(finish, colour)
            assert S.contrast(rgb, colour) >= 1.4, (finish, sp, name)


def test_every_finish_kind_is_known():
    from zoo_keeper.core import skins
    for finish, (_c, kind) in S.FINISHES.items():
        assert kind in skins.KNOWN_KINDS, (finish, kind)
    for fin in S.DETAIL_FINISHES:
        assert fin in S.FINISHES


# --- the slot fields ------------------------------------------------------------


def _slot(sp, dims, **fields):
    s = {"slot_id": sp, "role": "prop", "size_mod": "full", "style": 1,
         "species": sp, "fit": {"dims": dims, "pivot": "center"}}
    s.update(fields)
    return s


def _kit(*slots):
    return kit.plan_kit({"building_id": "t", "slots": list(slots)},
                        theme="delco_1997", style=1)


@pytest.mark.parametrize("host", HOSTS)
def test_hosts_offer_every_flavour_and_default_none(host):
    g = genome.load_species(host)
    assert g["params"]["stock"][0] == "none"
    assert set(g["params"]["stock"][1:]) == set(S.FLAVOURS)
    assert g["module_variants"] == 4


def test_a_slot_without_the_fields_plans_what_it_always_did():
    """Stem and module keys as 0.80.0 planned them, and the module plan's
    params the genome defaults -- `stock` "none" among them."""
    plan = _kit(_slot("desk", [1.6, 0.8, 0.75]))
    m = plan["modules"][0]
    assert m["stem"] == "prop_desk_delco_1997_01_w160_d80_h75"
    assert (m["form"], m["stock"], m["variant"]) == (None, None, None)
    mp = dna.resolve_module_plan(m, genome.load_species("desk"), "delco_1997", 1, "t")
    assert mp["params"]["stock"] == "none"
    assert "variant" not in mp["params"] and "form" not in mp["params"]
    assert "stock" not in mp["module"]
    # "none" and 0 are the same as absent
    same = _kit(_slot("desk", [1.6, 0.8, 0.75], stock="none", variant=0, form="auto"))
    assert same["modules"][0]["stem"] == m["stem"]
    assert same["dressing_fallbacks"] == []


def test_stock_and_variant_name_distinct_modules():
    plan = _kit(_slot("desk", [1.6, 0.8, 0.75], stock="office"),
                dict(_slot("desk", [1.6, 0.8, 0.75], stock="office", variant=2), slot_id="b"),
                dict(_slot("desk", [1.6, 0.8, 0.75], stock="bar"), slot_id="c"),
                dict(_slot("desk", [1.6, 0.8, 0.75]), slot_id="d"))
    stems = sorted(m["stem"] for m in plan["modules"])
    assert stems == ["prop_desk_delco_1997_01_w160_d80_h75",
                     "prop_desk_delco_1997_01_w160_d80_h75_sbar",
                     "prop_desk_delco_1997_01_w160_d80_h75_soffice",
                     "prop_desk_delco_1997_01_w160_d80_h75_soffice_n2"]
    assert plan["stem_collisions"] == []
    m = [x for x in plan["modules"] if x["stem"].endswith("_n2")][0]
    mp = dna.resolve_module_plan(m, genome.load_species("desk"), "delco_1997", 1, "t")
    assert mp["params"]["stock"] == "office" and mp["params"]["variant"] == 2
    assert mp["module"]["stock"] == "office" and mp["module"]["variant"] == 2


def test_module_stem_suffix_order():
    assert kit.module_stem("prop", "delco_1997", 1, 160, None, 80, None, None, 75,
                           species="booth_seat", form="sofa", stock="bar",
                           variant=3) == "prop_booth_seat_delco_1997_01_w160_d80_h75_fsofa_sbar_n3"
    assert kit.module_stem("prop", "delco_1997", 1, 160, None, 80, None, None, 75,
                           species="desk", stock="none", variant=0) == \
        "prop_desk_delco_1997_01_w160_d80_h75"


@pytest.mark.parametrize("fields,why", [
    ({"stock": "office"}, "stock 'office' is not one of chair's"),     # a chair takes no stock
    ({"stock": "florist"}, None),
    ({"variant": 9}, "variant"),
    ({"variant": 2}, "without stock"),
    ({"form": "sofa"}, "form 'sofa'"),
])
def test_what_a_species_cannot_honour_drops_all_three_and_says_so(fields, why):
    sp = "chair" if fields.get("stock") == "office" else "desk"
    dims = [0.55, 0.55, 0.9] if sp == "chair" else [1.6, 0.8, 0.75]
    both = dict(fields)
    if "variant" in fields and fields["variant"] == 9:
        both["stock"] = "office"
    plan = _kit(_slot(sp, dims, **both))
    m = plan["modules"][0]
    assert (m["form"], m["stock"], m["variant"]) == (None, None, None)
    assert m["stem"].endswith(("_h75", "_h90"))
    assert len(plan["dressing_fallbacks"]) == 1
    if why:
        assert why in plan["dressing_fallbacks"][0]["reason"]


def test_a_box_fallback_takes_no_dressing():
    """A desk that does not fit is built as the `prop` box, which has no
    stock -- the stem is the box's, and the drop is reported."""
    plan = _kit(_slot("desk", [20.0, 0.8, 0.75], stock="office"))
    m = plan["modules"][0]
    assert m["stem"] == "prop_delco_1997_01_w2000_d80_h75"
    assert plan["species_fallbacks"] and plan["dressing_fallbacks"]
