"""A string course (the factory's roadmap 324): Patina's floor-line band, built proud of the face, into the wall a
centimetre, over its declared height, in the stone trim."""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dressing as D
from zoo_keeper.core import genome


def test_the_band_stands_out_of_the_face_and_into_the_wall():
    """FAILS ON 1.147.0: no string course."""
    [(c, s)] = D.string_course_parts(2.0, 0.4)
    assert s == pytest.approx((2.0, D.STRING_PROUD + D.STRING_INTO, 0.4))
    assert c[1] - s[1] / 2 == pytest.approx(-D.STRING_INTO)
    assert c[1] + s[1] / 2 == pytest.approx(D.STRING_PROUD)
    assert c[2] == 0.0


def test_it_is_the_stone_trim():
    order = {"cover": "string_course", "pos": [0, 3.15, 3.45], "normal": [0, 1, 0], "size": 2.0,
             "size2": [2.0, 0.4], "collision": "none", "seed_offset": 1}
    plan = D.dress_plan(order, genome.load_species("dress_cover"), "delco_1997",
                        "spec/Blender Z-up raw coords", TOOL_VERSION)
    assert plan["material"] == D.STONE_TRIM_KIND and plan["order"]["size2"] == [2.0, 0.4]
