"""An Empty's window is painted (1.64.0): one atlas, one material, a state
per window, and glow only where the room light shows.

The pure half runs anywhere; the built half needs Blender, as
`test_storefront.py` does, and is skipped where bpy is absent.
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, kit, window_panes as P


def _px(canvas, x, y):
    return canvas.get(x, y)


def _cell_sum(canvas, state):
    x0, y0, x1, y1 = P.cell_rect(state)
    return sum(sum(canvas.get(x, y)) for y in range(y0, y1) for x in range(x0, x1))


def test_the_atlas_is_the_same_bytes_every_build():
    a1, e1 = P.atlas()
    a2, e2 = P.atlas()
    assert a1.png() == a2.png() and e1.png() == e2.png()
    assert (a1.w, a1.h) == (P.COLS * P.CELL_W, P.ROWS * P.CELL_H)


def test_the_atlas_has_sixteen_states_and_five_room_lights():
    """1.65.0, "color variation is key": more than one warm light."""
    assert len(P.STATES) == P.COLS * P.ROWS == 16
    lights = {P.ROOMS[s] for s in P.STATES if s.startswith("lit")}
    assert len(lights) >= 4


def test_only_a_lit_window_glows():
    """Glow taken from the albedo would light plywood and curtains; the
    emission image is black in every unlit cell and bright in every lit one."""
    _, e = P.atlas()
    for state in P.STATES:
        glow = _cell_sum(e, state)
        if state.startswith("lit"):
            assert glow > 0, state
        else:
            assert glow == 0, state


def test_each_state_s_uvs_sit_inside_its_own_cell():
    w, h = P.COLS * P.CELL_W, P.ROWS * P.CELL_H
    for state in P.STATES:
        u0, v0, u1, v1 = P.uv_rect(state)
        x0, y0, x1, y1 = P.cell_rect(state)
        assert x0 / w < u0 < u1 < x1 / w
        assert 1 - y1 / h < v0 < v1 < 1 - y0 / h


def _inside(uv, state):
    u0, v0, u1, v1 = P.uv_rect(state)
    return u0 - 1e-9 <= uv[0] <= u1 + 1e-9 and v0 - 1e-9 <= uv[1] <= v1 + 1e-9


def test_both_big_faces_carry_the_cell_and_the_edges_the_frame():
    """FAILS ON 1.65.0: only the +Y face was painted, and cold run 9151
    measured that face pointing INTO the house -- the street saw frame paint."""
    box = (0.0, 1.55, 0.475, 0.8)          # cx, cz, hx, hz
    for ny in (1.0, -1.0):
        for x in (-0.475, 0.475):
            for z in (0.75, 2.35):
                assert _inside(P.face_uv("lit_amber", ny, x, z, *box), "lit_amber")
    assert P.face_uv("lit_amber", 0.0, 0.475, 1.5, *box) == P.frame_uv()
    a, _ = P.atlas()
    w, h = P.COLS * P.CELL_W, P.ROWS * P.CELL_H
    fu, fv = P.frame_uv()
    assert a.get(int(fu * w), min(h - 1, int((1 - fv) * h))) == P.FRAME_RGB


def test_each_face_reads_unmirrored_from_its_own_side():
    """Seen from +Y the viewer's right is -X; seen from -Y it is +X. On both,
    u must grow toward the viewer's right, or one side shows the cell
    mirrored."""
    box = (0.0, 1.55, 0.475, 0.8)
    left_from_plus = P.face_uv("lit", 1.0, 0.4, 1.5, *box)[0]
    right_from_plus = P.face_uv("lit", 1.0, -0.4, 1.5, *box)[0]
    assert right_from_plus > left_from_plus
    left_from_minus = P.face_uv("lit", -1.0, -0.4, 1.5, *box)[0]
    right_from_minus = P.face_uv("lit", -1.0, 0.4, 1.5, *box)[0]
    assert right_from_minus > left_from_minus
    # and up is up on both: v grows with z
    assert P.face_uv("lit", 1.0, 0.0, 2.3, *box)[1] > P.face_uv("lit", 1.0, 0.0, 0.8, *box)[1]
    assert P.face_uv("lit", -1.0, 0.0, 2.3, *box)[1] > P.face_uv("lit", -1.0, 0.0, 0.8, *box)[1]


def _window(pane=None, glazing="facade"):
    s = {"slot_id": "w", "role": "window", "size_mod": "full", "style": 1,
         "material": "brick", "fit": {"dims": [0.95, 0.3, 3.1], "pivot": "center",
                                      "openings": [{"kind": "window", "width": 0.95,
                                                    "height": 1.6, "sill": 0.85}],
                                      "collision": "convex"}}
    if glazing:
        s["glazing"] = glazing
    if pane:
        s["pane"] = pane
    return s


def _stems(slots):
    plan = kit.plan_kit({"building_id": "t", "slots": slots}, theme="delco_1997", style=1)
    return sorted(m["stem"] for m in plan["modules"]), plan


def test_two_states_of_one_window_are_two_named_modules():
    """FAILS ON 1.63.0: no state in the name, one module for both."""
    stems, plan = _stems([_window("lit"), _window("dark")])
    assert len(stems) == 2 and plan["stem_collisions"] == []
    # `_p<state>` sits before the openings tag: window_..._mbrick_plit_o173e47
    assert any("_plit_" in s for s in stems) and any("_pdark_" in s for s in stems)


def test_a_state_is_only_honoured_on_a_facade_window():
    """The controls: an enterable window, or an unknown state, is named as
    before -- see-through glass is never painted over."""
    assert _stems([_window("lit", glazing=None)])[0] == _stems([_window(None, glazing=None)])[0]
    assert _stems([_window("purple")])[0] == _stems([_window(None)])[0]


def test_the_state_reaches_the_build_plan():
    _, plan = _stems([_window("lit_bars")])
    mod = plan["modules"][0]
    built = dna.resolve_module_plan(mod, genome.load_species("window"), "delco_1997", 1,
                                    TOOL_VERSION)
    assert built.get("pane") == "lit_bars" and built.get("glazing_kind") == "glass_facade"


def test_bpy_a_painted_pane_wears_the_face_material(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    _, plan = _stems([_window("lit")])
    B.build_module(plan["modules"][0], str(tmp_path / "out"), theme="delco_1997", style=1,
                   options={"save_blend": False})
    glass = [o for o in bpy.data.objects if o.type == "MESH" and "Glass" in o.name]
    assert glass and glass[0].data.materials[0].name == "M_Window_pane_Face"
