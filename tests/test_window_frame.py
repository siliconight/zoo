"""A window has a frame and a sill (1.145.0). The walker, 2026-10-28: "i think its less about realistic textures and
more about the 3d shape themselves?" -- a window was a hole in a slab with a pane at mid-depth, its reveal in the
wall's own material, and read as a dark square painted on the wall. The pure half holds the geometry; the bpy half
builds the modules. FAILS ON 1.144.0. Run inside Blender for this change:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_window_frame.py'])))"
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import arch

W, D, H = 1.6, 0.3, 3.3


def _void(w=W, h=H):
    return arch.void_for("window", w, h)


def _bounds(box):
    _n, c, s = box
    return [(c[i] - s[i] / 2.0, c[i] + s[i] / 2.0) for i in range(3)]


def test_the_frame_rings_the_opening_on_the_panes_plane_and_stays_inside_it():
    void = _void()
    parts = arch.window_frame_parts(D, void)
    assert sorted(p[0] for p in parts) == ["Frame_B", "Frame_L", "Frame_M", "Frame_R", "Frame_T"]
    for p in parts:
        (x0, x1), (y0, y1), (z0, z1) = _bounds(p)
        assert void["x0"] - 1e-9 <= x0 and x1 <= void["x1"] + 1e-9, p
        assert void["z0"] - 1e-9 <= z0 and z1 <= void["z1"] + 1e-9, p
        assert y0 == pytest.approx(-arch.window_frame_depth(D) / 2.0) and y1 == pytest.approx(-y0)
    assert arch.window_frame_depth(D) == pytest.approx(0.07)


@pytest.mark.parametrize("d", [0.1, 0.3, 0.6])
def test_the_frame_stands_proud_of_the_pane_however_deep_the_wall(d):
    fd = arch.window_frame_depth(d)
    assert fd <= d
    assert fd - d * arch.SF_PANE_D == pytest.approx(min(2.0 * arch.WINDOW_FRAME_PROUD, d - d * arch.SF_PANE_D))
    (sill,) = arch.window_sill_parts(W, d, H, _void())
    assert _bounds(sill)[1][0] > d * arch.SF_PANE_D / 2.0 + 0.002     # clear of the pane, past the probe's 2 mm


def test_a_wide_pane_gets_a_mullion_and_a_narrow_one_does_not():
    assert "Frame_M" in [p[0] for p in arch.window_frame_parts(D, _void(2.4))]
    assert "Frame_M" not in [p[0] for p in arch.window_frame_parts(D, _void(0.95))]


def test_the_frame_drops_only_faces_that_lie_on_the_slab_or_in_the_frame():
    keep_front = (0.0, 1.0, 0.0)
    for name in ("Frame_L", "Frame_R", "Frame_B", "Frame_T", "Frame_M"):
        assert not arch.window_frame_dropped(name, keep_front), name
        assert not arch.window_frame_dropped(name, (0.0, -1.0, 0.0)), name
    assert arch.window_frame_dropped("Frame_L", (-1.0, 0.0, 0.0))
    assert not arch.window_frame_dropped("Frame_L", (1.0, 0.0, 0.0))
    assert arch.window_frame_dropped("Frame_R", (1.0, 0.0, 0.0))
    assert not arch.window_frame_dropped("Frame_R", (-1.0, 0.0, 0.0))
    assert arch.window_frame_dropped("Frame_B", (0.0, 0.0, -1.0))
    assert not arch.window_frame_dropped("Frame_B", (0.0, 0.0, 1.0))
    assert arch.window_frame_dropped("Frame_T", (0.0, 0.0, 1.0))
    assert not arch.window_frame_dropped("Frame_T", (0.0, 0.0, -1.0))
    assert not arch.window_frame_dropped("Frame_M", (1.0, 0.0, 0.0))


def test_the_sill_stands_on_the_slab_and_projects_past_the_outdoor_face():
    void = _void()
    (sill,) = arch.window_sill_parts(W, D, H, void)
    (x0, x1), (y0, y1), (z0, z1) = _bounds(sill)
    assert z1 == pytest.approx(void["z0"] + arch.WINDOW_SILL_LIFT)
    assert z0 < void["z0"]
    assert y1 == pytest.approx(D / 2.0 + arch.WINDOW_SILL_PROUD)
    assert y0 == pytest.approx(arch.window_frame_depth(D) / 2.0 - arch.WINDOW_SILL_TUCK)
    assert x0 == pytest.approx(void["x0"] - arch.WINDOW_SILL_BEAR)
    assert x1 == pytest.approx(void["x1"] + arch.WINDOW_SILL_BEAR)
    assert -W / 2.0 <= x0 and x1 <= W / 2.0


def test_no_sill_where_the_opening_reaches_the_floor():
    void = dict(_void(), z0=-H / 2.0)
    assert arch.window_sill_parts(W, D, H, void) == []


def _module(extra=None):
    from zoo_keeper.core import kit
    slot = {"slot_id": "s", "role": "window", "size_mod": "full", "style": 1, "material": "concrete",
            "fit": {"dims": [W, D, H], "pivot": "center", "collision": "convex", "openings": []}}
    slot.update(extra or {})
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)["modules"][0]


def _built(module, tmp_path):
    import bpy
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    B.build_module(module, str(tmp_path / module["stem"]), theme="delco_1997", style=1, options={"save_blend": False})
    return sorted(o.name for o in bpy.data.objects if o.type == "MESH")


def test_bpy_a_window_is_framed_and_silled_and_a_painted_pane_is_not(tmp_path):
    pytest.importorskip("bpy")
    names = _built(_module(), tmp_path)
    assert sum("_Frame_" in n for n in names) == 5, names
    assert sum("_Sill_Stone" in n for n in names) == 1, names
    import bpy
    # the slab stays on its slot: the sill stands out of one face, and the first build re-centred the module on it
    col = next(o for o in bpy.data.objects if o.name.endswith("-colonly"))
    ys = [v.co.y for v in col.data.vertices]
    assert min(ys) == pytest.approx(-D / 2.0, abs=1e-4) and max(ys) == pytest.approx(D / 2.0, abs=1e-4), (min(ys), max(ys))
    painted = _built(_module({"glazing": "facade", "pane": "dark"}), tmp_path)
    assert not any("_Frame_" in n or "_Sill_Stone" in n for n in painted), painted
