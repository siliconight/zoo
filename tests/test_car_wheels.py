"""simple_car's wheels.

0.78.0: "these wheels jitter when I walk past them" (the walker). Measured
with tools/coplanar_probe.py: each tyre's outer cap lay exactly in the body's
side plane, both facing out. WHEEL_TUCK put the tyre face 2 cm inside it.

0.79.0 rebuilt the body around wheel WELLS -- an arch over each axle notched
into the outer underside -- and moved the layout into `core.car_forms` so it
can be checked here without Blender. The 0.78.0 guarantee is kept for every
body style at the genome's smallest, default and largest sizes, and the tyre
must now also sit inside its well. Recipe constants are read with `ast`
because the recipe imports bpy at module scope."""
from __future__ import annotations

import ast
import os
import re

from zoo_keeper.core import car_forms, genome

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "simple_car.py")


def _constants(path):
    ns = {}
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            try:
                ns[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return ns


def _sizes():
    d = genome.load_species("simple_car")["dimensions"]
    return [tuple(d[a][k] for a in ("width", "depth", "height"))
            for k in ("min", "default", "max")]


def test_the_tyre_face_stands_inside_the_body_side_and_the_tyre_inside_its_well():
    c = _constants(_RECIPE)
    for style in car_forms.FORMS:
        f = dict(car_forms.FORMS[style], style=style, rack=False)
        for W, L, H in _sizes():
            lay = car_forms.layout(f, W, L, H)
            outer = lay["tyre_outer_x"]
            inner = outer - lay["tyre_w"]
            assert lay["hw"] - outer >= 0.004, (style, W)       # not the skin's plane
            well_inner = lay["hw"] - car_forms.WHEEL_TUCK - lay["tyre_w"] - c["WELL_CLEAR"]
            assert inner - well_inner >= 0.004, (style, W)      # the well's wall clears it
            # the arch roof over the tyre's crown, by the arch gap
            assert (lay["wheel_r"] + lay["R"]) - 2 * lay["wheel_r"] >= 0.03


def test_the_recipe_places_the_wheel_with_that_layout():
    """A constant nothing reads is not a fix (CLAUDE.md, the null-result
    rule): the tyre, the well and the arch must all come from the layout."""
    src = open(_RECIPE, encoding="utf-8").read()
    assert re.search(r'xo = lay\["tyre_outer_x"\]', src)
    assert re.search(r"cxw = xo - tyre_w / 2\.0", src)
    assert re.search(r"xw = hw - WHEEL_TUCK - tyre_w - WELL_CLEAR", src)
    assert re.search(r"WHEEL_TUCK = car_forms\.WHEEL_TUCK", src)
    assert re.search(r'ya_f, ya_r, R = lay\["ya_f"\], lay\["ya_r"\], lay\["R"\]', src)
