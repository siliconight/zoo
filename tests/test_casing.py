"""A doorway or breach panel is cased at its ends (1.126.0). The walker, walking cold run 9386: "textures have visible
seams" -- where an interactive opening, its own mesh and its own lightmap rect, meets the wall; and of framing a breach
panel: "Yes hide the seam for breaches". The pure half holds the geometry; the bpy half builds the modules. FAILS ON
1.125.0. Run inside Blender for this change:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_casing.py'])))"
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import arch


def _span(box):
    _n, (cx, _cy, _cz), (sx, _sy, _sz) = box
    return cx - sx / 2.0, cx + sx / 2.0


def test_each_end_has_a_casing_on_each_face_straddling_the_joint():
    w, d, h = 1.4, 0.3, 3.1
    parts = arch.casing_parts(w, d, h)
    assert sorted(p[0] for p in parts) == ["Casing_L_In", "Casing_L_Out", "Casing_R_In", "Casing_R_Out"]
    for p in parts:
        lo, hi = _span(p)
        joint = -w / 2.0 if "_L_" in p[0] else w / 2.0
        assert lo < joint < hi, p
        assert abs(p[2][2] - h) < 1e-9


def test_a_casing_sits_on_the_face_and_drops_only_what_nobody_sees():
    d = 0.3
    for name, (_cx, cy, _cz), (_sx, sy, _sz) in arch.casing_parts(1.4, d, 3.1):
        assert abs(cy) - sy / 2.0 == pytest.approx(d / 2.0), name
        assert abs(cy) + sy / 2.0 - d / 2.0 == pytest.approx(arch.CASING_PROUD), name
        out = 1.0 if name.endswith("_Out") else -1.0
        assert not arch.casing_dropped(name, (0.0, out, 0.0)), name          # its front
        assert not arch.casing_dropped(name, (1.0, 0.0, 0.0)), name          # its sides
        assert arch.casing_dropped(name, (0.0, -out, 0.0)), name             # its back
        assert arch.casing_dropped(name, (0.0, 0.0, 1.0)) and arch.casing_dropped(name, (0.0, 0.0, -1.0))


def test_a_casing_never_narrows_the_opening():
    void = {"x0": -0.5, "x1": 0.5, "z0": -1.55, "z1": 0.65}
    for p in arch.casing_parts(1.25, 0.3, 3.1, void):
        lo, hi = _span(p)
        assert hi <= void["x0"] - arch.CASING_VOID_CLEAR + 1e-9 or lo >= void["x1"] + arch.CASING_VOID_CLEAR - 1e-9, p


def _module(role, extra=None):
    from zoo_keeper.core import kit
    slot = {"slot_id": "s", "role": role, "size_mod": "full", "style": 1, "material": "concrete",
            "fit": {"dims": [1.4, 0.3, 3.1], "pivot": "center", "collision": "convex",
                    "openings": [{"kind": "door", "width": 1.0, "height": 2.2, "sill": 0.0}] if role == "doorway" else []}}
    slot.update(extra or {})
    return kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)["modules"]


def _built(module, tmp_path):
    import bpy
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    B.build_module(module, str(tmp_path / module["stem"]), theme="delco_1997", style=1, options={"save_blend": False})
    return sorted(o.name for o in bpy.data.objects if o.type == "MESH")


BREACH = {"interactive": {"id": "t:if:1", "kind": "breach_wall", "states": ["intact", "breached"],
                          "default": "intact", "state_geometry": {"intact": "wall", "breached": "breach"},
                          "collision_per_state": {"intact": True, "breached": False}}}


def test_bpy_a_doorway_and_both_states_of_a_breach_panel_are_cased_and_a_wall_is_not(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    doorway = _module("doorway")[0]
    assert sum("_Casing_" in n for n in _built(doorway, tmp_path)) == 4
    assert all(len(o.data.polygons) == 3 for o in bpy.data.objects if "_Casing_" in o.name)
    breach = _module("breach", BREACH)
    assert {m.get("state") for m in breach} == {None, "breached"}
    for m in breach:
        assert sum("_Casing_" in n for n in _built(m, tmp_path)) == 4, m["stem"]
    wall = _module("wall")[0]
    assert not any("_Casing_" in n for n in _built(wall, tmp_path))
