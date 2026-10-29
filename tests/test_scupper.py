"""A roof that drains through its parapet (1.147.0; Patina >= 0.34.0, the factory's roadmap 324).

Patina orders a downspout `head` on a side a parapet stands over, its run from the ground to the roof's surface; Zoo
ends it in a scupper's lip at the roof and a conductor head hung under it, with the leader entering the head's foot.
A downspout without `head` is built as it always was.
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dressing as D
from zoo_keeper.core import genome

L, CROSS = 7.2, 0.076


def _span(part):
    (cx, cy, cz), (sx, sy, sz) = part
    return (cy - sy / 2, cy + sy / 2), (cz - sz / 2, cz + sz / 2)


def test_a_headed_run_ends_in_a_scupper_and_a_head_at_the_roof():
    """FAILS ON 1.146.1: no scupper, no head, and the leader ran to the top."""
    parts = D.downspout_parts(L, CROSS, head=True)
    pipe, lip, head, foot = parts[0], parts[-3], parts[-2], parts[-1]
    (_ly, (lz0, lz1)), ((hy0, hy1), (hz0, hz1)) = _span(lip), _span(head)
    _fy, (fz0, fz1) = _span(foot)
    _py, (pz0, pz1) = _span(pipe)
    assert lz1 == pytest.approx(L / 2)                    # the lip's top is the roof's surface
    assert hz1 > lz0 and hz1 - lz0 < 0.01                 # the head hangs under the lip, into it, no shared face
    assert hy1 > _ly[1]                                   # and stands out past it, to catch what it spills
    assert fz1 > hz0 and fz0 < pz1 < fz1                  # the leader enters the head's foot
    assert all(_span(p)[0][0] >= 0.001 for p in parts[-3:])   # nothing in the wall


def test_an_unheaded_run_is_built_as_it_was():
    assert D.downspout_parts(L, CROSS) == D.downspout_parts(L, CROSS, head=False)
    assert len(D.downspout_parts(L, CROSS)) == 4


def test_the_plan_carries_head():
    order = {"cover": "downspout", "pos": [0, 11.15, 3.6], "normal": [0, 1, 0], "size": L, "head": True,
             "collision": "none", "seed_offset": 1}
    g = genome.load_species("dress_cover")
    plan = D.dress_plan(order, g, "delco_1997", "spec/Blender Z-up raw coords", TOOL_VERSION)
    assert plan["order"]["head"] is True and plan["material"] == "metal_painted"
    assert D.dress_plan(dict(order, head=False), g, "delco_1997", "spec/Blender Z-up raw coords",
                        TOOL_VERSION)["order"]["head"] is False
