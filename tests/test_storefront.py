"""1.18.0 -- a storefront is see-through glass.

The walker, 2026-09-28: "yes, make the storefront see-through glass", after
six photographs of stores at night glowing through their glass doors and
shop fronts. Deli Counter tags a storefront's full-width wall and door slots
`glazing: "storefront"`; Zoo builds them as a kick, header, mullions and a
see-through pane (a door: head rail, transom, and closed leaves with push
bars), the collider unchanged. Everything else in the library is untouched:
the names, the opaque-structure rule, every other door's states.
"""
from __future__ import annotations

import json
import os

import pytest

from zoo_keeper.core import arch, dna, genome, kit
from zoo_keeper.core import prims as P

HERE = os.path.dirname(os.path.abspath(__file__))
SLOTS = os.path.join(HERE, "..", "..", "deli_counter", "build", "gas_station_a02.slots.json")
DOOR = {"kind": "door", "width": 1.8, "height": 2.2, "sill": 0.0}


def _boxes(parts, mat):
    return [P.box(n, mat, tuple(c[i] - s[i] / 2 for i in range(3)), tuple(c[i] + s[i] / 2 for i in range(3)))
            for n, c, s in parts]


CASES = [("wall", 2.0, 0.3, 3.9, False), ("wall", 2.0, 0.3, 2.8, False), ("wall", 0.9, 0.3, 3.9, False),
         ("doorway", 1.8, 0.3, 3.9, True), ("doorway", 1.8, 0.3, 3.9, False), ("doorway", 1.2, 0.2, 2.6, True)]


@pytest.mark.parametrize("species,w,d,h,leaves", CASES)
def test_a_storefront_fills_its_slot_and_no_pane_shares_a_plane(species, w, d, h, leaves):
    void = arch.void_for(species, w, h, {"opening": dict(DOOR, width=min(1.8, w))} if species == "doorway" else {})
    frame, glass = arch.storefront_parts(w, d, h, void, leaves)
    pr = _boxes(frame, "frame") + _boxes(glass, "glass")
    lo, hi = P.bounds(pr)
    assert [round(v, 6) for v in lo] == [round(-w / 2, 6), round(-d / 2, 6), round(-h / 2, 6)]
    assert [round(v, 6) for v in hi] == [round(w / 2, 6), round(d / 2, 6), round(h / 2, 6)]
    pairs = P.coincident_pairs(pr, tol=0.0022)
    # the frame TILES, as `slab_parts` does: touching boxes, opposite faces,
    # hidden inside the frame. Nothing else: no pane on a frame face, and no
    # two faces lying in one plane facing one way.
    for p in pairs:
        assert p["facing"] == "OPP" and p["gap_mm"] == 0.0, p
        assert not any("Glass" in x or "Transom" in x for x in (p["a"], p["b"])), p
    assert glass, "a storefront with no glass"


def test_the_glass_runs_from_the_kick_to_the_header_and_the_door_to_the_transom():
    frame, glass = arch.storefront_parts(2.0, 0.3, 3.9)
    g = dict((n, (c, s)) for n, c, s in glass)["Glass"]
    bottom, top = g[0][2] - g[1][2] / 2 + 3.9 / 2, g[0][2] + g[1][2] / 2 + 3.9 / 2
    assert bottom == pytest.approx(arch.SF_KICK - arch.SF_BURY)
    assert top == pytest.approx(arch.SF_GLASS_TOP + arch.SF_BURY)
    void = arch.void_for("doorway", 1.8, 3.9, {"opening": DOOR})
    closed = arch.storefront_parts(1.8, 0.3, 3.9, void, True)
    opened = arch.storefront_parts(1.8, 0.3, 3.9, void, False)
    assert {n for n, _c, _s in closed[1]} == {"Transom", "Leaf_L_Glass", "Leaf_R_Glass"}
    assert {n for n, _c, _s in opened[1]} == {"Transom"}
    assert not any(n.startswith("Leaf") for n, _c, _s in opened[0])


def test_the_leaves_leave_the_opening_clear_of_the_jambs_and_the_floor():
    void = arch.void_for("doorway", 1.8, 3.9, {"opening": DOOR})
    frame, _g = arch.storefront_parts(1.8, 0.3, 3.9, void, True)
    leaves = [(c, s) for n, c, s in frame if n.startswith("Leaf")]
    x0 = min(c[0] - s[0] / 2 for c, s in leaves)
    x1 = max(c[0] + s[0] / 2 for c, s in leaves)
    z0 = min(c[2] - s[2] / 2 for c, s in leaves)
    assert x0 > void["x0"] and x1 < void["x1"] and z0 > -3.9 / 2


def test_the_name_carries_the_storefront_and_nothing_else_moves():
    base = kit.module_stem("wall", "delco_1997", 2, 200, material="glass_facade")
    assert base == "wall_delco_1997_02_w200_mglass_facade"
    assert kit.module_stem("wall", "delco_1997", 2, 200, material="glass_facade",
                           glazing="storefront") == base + "_gstorefront"
    # a facade shell's window swaps its pane kind and keeps its name
    assert kit.module_stem("window", "delco_1997", 2, 200, glazing="facade") == \
        kit.module_stem("window", "delco_1997", 2, 200)


def test_the_tag_reaches_the_plan_and_the_structure_rule_holds():
    g = genome.load_species("wall")
    plan = dna.resolve_module_plan({"type": "wall", "species": "wall", "dims": [2.0, 0.3, 3.9],
                                    "material": "glass", "glazing": "storefront"}, g, "delco_1997", 1, "t")
    assert plan["storefront"] is True and "glazing_kind" not in plan
    assert plan["material"] == "glass_facade"          # the slab is still never glass


@pytest.mark.skipif(not os.path.exists(SLOTS), reason="needs Deli Counter's built slots")
def test_only_a_storefront_door_builds_its_open_state():
    """1.18.0 scopes the open door's own art to storefront doors: every
    other door in the library still defers its open state to the base."""
    d = json.load(open(SLOTS, encoding="utf-8"))
    door = next(s for s in d["slots"] if s["slot_id"] == "ext_0_S_open1")
    wall = next(s for s in d["slots"] if s["role"] == "wall" and s.get("size_mod") == "full"
                and s["wall"] == "ext_0_S")
    plain = kit.plan_kit({"building_id": "t", "slots": [dict(door, glazing=None), dict(wall, glazing=None)]},
                         theme="delco_1997", style=1)
    shop = kit.plan_kit({"building_id": "t", "slots": [dict(door, glazing="storefront"),
                                                        dict(wall, glazing="storefront")]},
                        theme="delco_1997", style=1)
    pstems = [m["stem"] for m in plain["modules"]]
    sstems = [m["stem"] for m in shop["modules"]]
    assert not any("_gstorefront" in s or s.endswith("_open") for s in pstems), pstems
    assert sum(s.endswith("_open") for s in sstems) == 1 and all("_gstorefront" in s for s in sstems), sstems
    assert shop["stem_collisions"] == []


def test_the_genomes_name_the_storefront_parts():
    assert {"Wall_Mullion_L", "Wall_Kick", "Wall_Header", "Wall_Glass"} <= set(genome.load_species("wall")["parts"])
    assert {"Doorway_Rail", "Doorway_Transom", "Doorway_Leaf"} <= set(genome.load_species("doorway")["parts"])


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, typ, dims, state=None, openings=None):
    """Built as `test_see_through_glass` builds a window: a skin library with
    the theme's see-through glass pack, the objects read before export."""
    import bpy
    from zoo_keeper.bpylayer import build as B, materials
    from tests.test_see_through_glass import _pack
    for mat in list(bpy.data.materials):
        if mat.name.startswith(("M_Skin_glass", "M_Window_glass")):
            bpy.data.materials.remove(mat)
    skins_dir = tmp_path / "skins"
    _pack(str(skins_dir), "glass_delco_1997", "glass_delco",
          {"alpha_mode": "blend", "opacity": 0.38, "ior": 1.5})
    _pack(str(skins_dir), "glass_facade_delco_1997", "glass_facade_bronze")
    materials.set_skin_library(str(skins_dir), "delco_1997")
    slot = {"slot_id": "s", "role": typ, "size_mod": "full", "style": 2, "material": "glass_facade",
            "glazing": "storefront", "fit": {"dims": list(dims), "pivot": "center",
                                             "openings": openings or [], "collision": "convex"}}
    if typ == "doorway":
        slot["interactive"] = {"id": "x", "kind": "door", "states": ["closed", "open"], "default": "closed",
                               "collision_per_state": {"closed": True, "open": False}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    mod = next(m for m in plan["modules"] if m["stem"].endswith("_open") == (state == "open"))
    try:
        res = B.build_module(mod, str(tmp_path / "out"), theme="delco_1997", style=1,
                             options={"save_blend": False})
    finally:
        materials.set_skin_library(None)
    # plain values, read now: the next build clears the scene and frees these
    return res, {o.name: (_blended(o.data.materials[0]) if o.data.materials else None)
                 for o in bpy.data.objects if o.type == "MESH"}


def _blended(mat):
    alpha = mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value
    return alpha < 1.0 and getattr(mat, "surface_render_method", "BLENDED") == "BLENDED"


def test_bpy_a_storefront_wall_is_see_through_and_collides_as_before(tmp_path):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, "wall", (2.0, 0.3, 3.9))
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    panes = [b for n, b in objs.items() if "Glass" in n]
    assert panes and all(panes), objs
    frame = [o for n, o in objs.items() if any(k in n for k in ("Kick", "Header", "Mullion"))]
    assert len(frame) >= 4, sorted(objs)


def test_bpy_a_storefront_door_has_leaves_closed_and_none_open(tmp_path):
    pytest.importorskip("bpy")
    _r, closed = _build(tmp_path / "c", "doorway", (1.8, 0.3, 3.9), openings=[DOOR])
    leaves_c = [n for n in closed if "Leaf" in n]
    glass_c = [b for n, b in closed.items() if "Glass" in n or "Transom" in n]
    _r, opened = _build(tmp_path / "o", "doorway", (1.8, 0.3, 3.9), state="open", openings=[DOOR])
    leaves_o = [n for n in opened if "Leaf" in n]
    assert leaves_c and not leaves_o, (sorted(closed), sorted(opened))
    assert any("Transom" in n for n in opened), sorted(opened)
    assert glass_c and all(glass_c), closed
