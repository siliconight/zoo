"""A traffic signal for the driver's right (1.121.0). The walker, walking cold run 9386: "where are the traffic lights
for this side of the road?" -- Lot stood a signal only on a junction's yielding leg. The heads face -y off an arm along
+x, which is a pole on the driver's LEFT; the `right` form faces them +y, for the pole on an approach's far right
corner with its arm back over the lanes.

The kit half runs anywhere. The bpy half skips without Blender and was run inside Blender 5.1.1 for this change, from
the repo root:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_signal_hand.py'])))"
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import genome, kit


def _slot(form=None):
    s = {"slot_id": "sig", "role": "prop", "size_mod": "full", "style": 1, "species": "traffic_signal",
         "fit": {"dims": [8.0, 0.62, 6.5], "pivot": "center"}}
    if form:
        s["form"] = form
    return s


def test_the_genome_lists_the_right_form():
    assert genome.load_species("traffic_signal")["params"]["form"] == ["auto", "right"]


def test_the_kit_builds_the_right_form_under_its_own_name():
    plan = kit.plan_kit({"building_id": "t", "slots": [_slot("right"), _slot()]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == []
    stems = sorted(m["stem"] for m in plan["modules"])
    assert len(stems) == 2 and stems[0] != stems[1]
    assert any(s.endswith("_fright") for s in stems), stems


def test_a_hand_the_genome_does_not_list_is_dropped_and_said():
    got, why = kit.honour_dressing({"form": "left"}, "traffic_signal")
    assert got == {"form": None, "stock": None, "variant": None} and why


@pytest.mark.parametrize("form,side", [(None, -1), ("right", 1)])
def test_bpy_the_heads_face_minus_y_or_on_the_right_form_plus_y(form, side, tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    plan = kit.plan_kit({"building_id": "t", "slots": [_slot(form)]}, theme="delco_1997", style=1)
    B.build_module(plan["modules"][0], str(tmp_path / "out"), theme="delco_1997", style=1,
                   options={"save_blend": False})
    lenses = [o for o in bpy.data.objects if o.type == "MESH" and "TrafficSignal_Lens" in o.name]
    assert len(lenses) == 3, [o.name for o in bpy.data.objects]
    for o in lenses:
        ys = [(o.matrix_world @ v.co).y for v in o.data.vertices]
        assert ys and all(y * side > 0 for y in ys), (o.name, min(ys), max(ys))
