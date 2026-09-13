"""simple_car's wheels (0.78.0): "these wheels jitter when I walk past them"
(the walker). Measured with tools/coplanar_probe.py: each tyre's outer cap
lay exactly in the body's side plane, both facing out. Constants are read
with `ast` because the recipe imports bpy at module scope."""
from __future__ import annotations

import ast
import json
import os
import re

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "simple_car.py")
_GENOME = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "simple_car.json")


def _constants(path):
    """Module-level literal assignments, including ``A, B = 1, 2``."""
    ns = {}
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
            continue
        target = node.targets[0]
        try:
            value = ast.literal_eval(node.value)
        except ValueError:
            continue
        if isinstance(target, ast.Name):
            ns[target.id] = value
        elif isinstance(target, ast.Tuple):
            for elt, v in zip(target.elts, value):
                ns[elt.id] = v
    return ns


def test_the_tyre_face_stands_inside_the_body_side():
    c = _constants(_RECIPE)
    for name in ("WHEEL_INSET", "WHEEL_W", "WHEEL_TUCK", "ROCKER_W"):
        assert name in c, name
    dims = json.load(open(_GENOME, encoding="utf-8"))["dimensions"]["width"]
    for w in (dims["min"], dims["default"], dims["max"]):
        body_side = w / 2
        centre = w / 2 - c["WHEEL_INSET"] - c["WHEEL_TUCK"]
        outer = centre + c["WHEEL_W"] / 2
        inner = centre - c["WHEEL_W"] / 2
        assert body_side - outer >= 0.004, w          # not the body's plane
        rocker = w * c["ROCKER_W"] / 2
        # nor the rocker's: the rocker face must cut through the tyre well
        # clear of both of its caps
        assert inner + 0.004 <= rocker <= outer - 0.004, w


def test_the_recipe_places_the_wheel_with_those_constants():
    """A constant nothing reads is not a fix (CLAUDE.md, the null-result
    rule): the placement line has to use both of them."""
    src = open(_RECIPE, encoding="utf-8").read()
    assert re.search(r"wheel_x\s*=\s*w\s*/\s*2\s*-\s*WHEEL_INSET\s*-\s*WHEEL_TUCK", src)
    assert re.search(r"depth\s*=\s*WHEEL_W", src)
