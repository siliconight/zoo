"""A corner shop's window is painted (1.107.0): its own atlas and material, a state per storefront, glow only
where the shop's light shows -- `window_panes`' machinery on a landscape cell.

The pure half runs anywhere; the built half needs Blender, as `test_window_panes.py` does, and is skipped where
bpy is absent. It was run inside Blender for this change, from the repo root:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_shop_panes.py'])))"

On 1.106.0 there is no `core.shop_panes`, so the module fails to import. With the module alone added, the
module's name and its build plan fail; the ten atlas checks and the facade-only control pass.
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, kit, shop_panes as S, window_panes as P


def _cell_sum(canvas, state):
    x0, y0, x1, y1 = S.cell_rect(state)
    return sum(sum(canvas.get(x, y)) for y in range(y0, y1) for x in range(x0, x1))


def test_the_atlas_is_the_same_bytes_every_build():
    a1, e1 = S.atlas()
    a2, e2 = S.atlas()
    assert a1.png() == a2.png() and e1.png() == e2.png()
    assert (a1.w, a1.h) == (S.COLS * S.CELL_W, S.ROWS * S.CELL_H)


def test_a_storefront_cell_is_wider_than_tall_and_a_sash_is_not():
    """A shopfront bay is about 2.8 x 2.4 m and a sash 0.95 x 1.6 m: the reason it is its own atlas."""
    assert S.CELL_W > S.CELL_H and P.CELL_W < P.CELL_H


def test_six_states_four_rooms_each_its_own_light():
    assert len(S.STATES) == S.COLS * S.ROWS == 6
    assert set(S.ROOMS) <= set(S.STATES)
    assert len({S.ROOMS[s] for s in S.ROOMS}) == len(S.ROOMS) == 4


def test_no_shop_state_is_a_window_state():
    """FAILS IF THE TWO SETS MEET: `_arch.build_slab` picks the atlas by which set a state is in, so a name in
    both would paint one atlas's cell from the other's UVs."""
    assert not set(S.STATES) & set(P.STATES)


def test_only_a_lit_shop_glows():
    """The gate and the dark glass are black in the emission; every shop with its light on glows."""
    _, e = S.atlas()
    for state in S.STATES:
        glow = _cell_sum(e, state)
        if state in S.ROOMS:
            assert glow > 0, state
        else:
            assert glow == 0, state


def test_the_aluminium_never_glows():
    """The frame, the transom bar, both mullions and the kick plate are black in the emission of every cell --
    the shop lights the glass, not the metal round it."""
    _, e = S.atlas()
    for state in S.STATES:
        x0, y0, x1, y1 = S.cell_rect(state)
        gx0, gy0, gx1, gy1 = x0 + S.FRAME, y0 + S.FRAME, x1 - S.FRAME, y1 - S.FRAME
        transom = gy0 + (gy1 - gy0) // 5
        metal = [(x, y) for x in range(x0, x1) for y in range(y0, y0 + S.FRAME)]
        metal += [(x, transom) for x in range(gx0, gx1)]
        metal += [(gx0 + (gx1 - gx0) * j // 3, y) for j in (1, 2) for y in range(transom, gy1)]
        metal += [(x, gy1 - 1) for x in range(gx0, gx1)]
        assert all(e.get(x, y) == (0, 0, 0) for x, y in metal), state


def test_a_shop_glows_brighter_than_a_home():
    """The light the eye goes to first: the shop's material is built brighter than a window's."""
    assert S.EMISSION > P.EMISSION


def test_each_state_s_uvs_sit_inside_its_own_cell():
    w, h = S.COLS * S.CELL_W, S.ROWS * S.CELL_H
    for state in S.STATES:
        u0, v0, u1, v1 = S.uv_rect(state)
        x0, y0, x1, y1 = S.cell_rect(state)
        assert x0 / w < u0 < u1 < x1 / w
        assert 1 - y1 / h < v0 < v1 < 1 - y0 / h


def _inside(uv, state):
    u0, v0, u1, v1 = S.uv_rect(state)
    return u0 - 1e-9 <= uv[0] <= u1 + 1e-9 and v0 - 1e-9 <= uv[1] <= v1 + 1e-9


def test_both_big_faces_carry_the_cell_and_the_edges_the_frame():
    box = (0.0, 1.4, 1.35, 1.1)            # cx, cz, hx, hz
    for ny in (1.0, -1.0):
        for x in (-1.35, 1.35):
            for z in (0.3, 2.5):
                assert _inside(S.face_uv("shop_deli", ny, x, z, *box), "shop_deli")
    assert S.face_uv("shop_deli", 0.0, 1.35, 1.4, *box) == S.frame_uv()
    a, _ = S.atlas()
    w, h = S.COLS * S.CELL_W, S.ROWS * S.CELL_H
    fu, fv = S.frame_uv()
    assert a.get(int(fu * w), min(h - 1, int((1 - fv) * h))) == S.FRAME_RGB


def test_each_face_reads_unmirrored_from_its_own_side():
    box = (0.0, 1.4, 1.35, 1.1)
    assert S.face_uv("shop_bar", 1.0, -1.2, 1.4, *box)[0] > S.face_uv("shop_bar", 1.0, 1.2, 1.4, *box)[0]
    assert S.face_uv("shop_bar", -1.0, 1.2, 1.4, *box)[0] > S.face_uv("shop_bar", -1.0, -1.2, 1.4, *box)[0]
    assert S.face_uv("shop_bar", 1.0, 0.0, 2.4, *box)[1] > S.face_uv("shop_bar", 1.0, 0.0, 0.4, *box)[1]
    assert S.face_uv("shop_bar", -1.0, 0.0, 2.4, *box)[1] > S.face_uv("shop_bar", -1.0, 0.0, 0.4, *box)[1]


def _window(pane=None, glazing="facade"):
    s = {"slot_id": "w", "role": "window", "size_mod": "full", "style": 1,
         "material": "brick", "fit": {"dims": [2.9, 0.3, 3.1], "pivot": "center",
                                      "openings": [{"kind": "window", "width": 2.8,
                                                    "height": 2.4, "sill": 0.3}],
                                      "collision": "convex"}}
    if glazing:
        s["glazing"] = glazing
    if pane:
        s["pane"] = pane
    return s


def _stems(slots):
    plan = kit.plan_kit({"building_id": "t", "slots": slots}, theme="delco_1997", style=1)
    return sorted(m["stem"] for m in plan["modules"]), plan


def test_a_shop_state_is_its_own_named_module():
    """FAILS ON 1.106.0: `kit.plan_kit` honoured only `window_panes.STATES`, so a shop window built as an
    unpainted facade window under the unpainted name."""
    stems, plan = _stems([_window("shop_deli"), _window("shop_gate"), _window(None)])
    assert len(stems) == 3 and plan["stem_collisions"] == []
    assert any("_pshop_deli_" in s for s in stems) and any("_pshop_gate_" in s for s in stems)


def test_a_shop_state_is_only_honoured_on_a_facade_window():
    assert _stems([_window("shop_deli", glazing=None)])[0] == _stems([_window(None, glazing=None)])[0]


def test_the_shop_state_reaches_the_build_plan():
    """FAILS ON 1.106.0: the kit dropped the state, so the plan carried none."""
    _, plan = _stems([_window("shop_laundry")])
    built = dna.resolve_module_plan(plan["modules"][0], genome.load_species("window"), "delco_1997", 1,
                                    TOOL_VERSION)
    assert built.get("pane") == "shop_laundry" and built.get("glazing_kind") == "glass_facade"


def test_bpy_a_shop_pane_wears_the_shop_material(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    _, plan = _stems([_window("shop_grocery")])
    B.build_module(plan["modules"][0], str(tmp_path / "out"), theme="delco_1997", style=1,
                   options={"save_blend": False})
    glass = [o for o in bpy.data.objects if o.type == "MESH" and "Glass" in o.name]
    assert glass and glass[0].data.materials[0].name == "M_Shop_pane_Face"
