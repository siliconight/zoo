"""The stop sign's STOP legend (0.78.0): "the stop sign has no legend" (the
walker). The glyph layout is pure Python; the recipe's constants are read with
`ast` because `stop_sign.py` imports bpy at module scope."""
from __future__ import annotations

import ast
import json
import math
import os

import pytest

from zoo_keeper.recipes import _legend

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "stop_sign.py")
_GENOME = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "stop_sign.json")


def _constants(path):
    """Module-level NAME = <arithmetic> assignments, evaluated in order."""
    ns = {}
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            try:
                ns[node.targets[0].id] = eval(
                    compile(ast.Expression(node.value), path, "eval"),
                    {"__builtins__": {}}, dict(ns))
            except Exception:
                continue
    return ns


def _area(poly):
    return sum(poly[k][0] * poly[(k + 1) % len(poly)][1]
               - poly[(k + 1) % len(poly)][0] * poly[k][1]
               for k in range(len(poly))) / 2.0


def _inside(p, poly):
    """Strictly inside a CCW convex polygon."""
    for k in range(len(poly)):
        a, b = poly[k], poly[(k + 1) % len(poly)]
        if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) <= 1e-9:
            return False
    return True


def test_the_recipe_constants_are_readable():
    """Guard the guard: every check below reads these."""
    c = _constants(_RECIPE)
    for name in ("POST", "BLADE_T", "FACE_PROUD", "BORDER", "LEGEND_PROUD",
                 "LEGEND_BURY"):
        assert name in c, name


def test_the_legend_stands_proud_and_its_back_is_clear_of_every_plane():
    c = _constants(_RECIPE)
    assert c["LEGEND_PROUD"] >= 0.002
    # measured from the red face's front, going back: the red face's back,
    # then the border's back. The cap must be inside the blade and at least
    # 3 mm from each plane -- fit_to squeezes depth to 0.675 at the smallest
    # sign, and the probe reports anything within 2 mm
    planes = (0.0, c["FACE_PROUD"], c["FACE_PROUD"] + c["BLADE_T"])
    assert c["LEGEND_BURY"] < planes[-1]
    for p in planes:
        assert abs(c["LEGEND_BURY"] - p) >= 0.003, p


@pytest.mark.parametrize("ch", sorted(_legend.GLYPHS))
def test_each_glyph_is_ccw_and_its_cells_never_overlap(ch):
    verts, faces = _legend.glyph_cells(ch)
    polys = [[verts[i] for i in f] for f in faces]
    for p in polys:
        assert _area(p) > 1e-6, (ch, p)
    # sample a fine grid: no point may be strictly inside two cells
    for i in range(1, 80):
        for j in range(1, 80):
            pt = (i / 80.0 * _legend.LETTER_W, j / 80.0)
            assert sum(_inside(pt, p) for p in polys) <= 1, (ch, pt)


@pytest.mark.parametrize("ch", sorted(_legend.GLYPHS))
def test_each_glyph_outline_is_closed(ch):
    """The recipe walls every edge no neighbouring cell walks the other way.
    That is a closed solid only if the boundary is closed loops: every
    boundary vertex has as many edges leaving as arriving."""
    _verts, faces = _legend.glyph_cells(ch)
    edges = set()
    for f in faces:
        for k in range(len(f)):
            edges.add((f[k], f[(k + 1) % len(f)]))
    boundary = [(a, b) for a, b in edges if (b, a) not in edges]
    assert boundary
    out_deg, in_deg = {}, {}
    for a, b in boundary:
        out_deg[a] = out_deg.get(a, 0) + 1
        in_deg[b] = in_deg.get(b, 0) + 1
    assert out_deg == in_deg, ch


def test_every_corner_cut_is_45_degrees():
    """A cut cell is stroke x stroke, so the chamfer is square."""
    for ch in _legend.GLYPHS:
        verts, faces = _legend.glyph_cells(ch)
        for f in faces:
            if len(f) != 3:
                continue
            xs = sorted({round(verts[i][0], 9) for i in f})
            zs = sorted({round(verts[i][1], 9) for i in f})
            assert math.isclose(xs[1] - xs[0], _legend.STROKE, abs_tol=1e-9), ch
            assert math.isclose(zs[1] - zs[0], _legend.STROKE, abs_tol=1e-9), ch


@pytest.mark.parametrize("which", ["min", "default", "max"])
def test_the_word_is_a_third_of_the_width_and_fits_inside_the_red_face(which):
    c = _constants(_RECIPE)
    w = json.load(open(_GENOME, encoding="utf-8"))["dimensions"]["width"][which]
    height = w * _legend.LEGEND_H_OF_WIDTH
    glyphs, (lw, lh) = _legend.legend("STOP", height)
    assert math.isclose(lh, w / 3.0)
    # the red face: a regular octagon standing on a flat, flats-to-flats
    across = w - 2.0 * c["BORDER"]
    r = across / 2.0 / math.cos(math.pi / 8.0)
    octagon = [(r * math.cos(math.pi / 8.0 + k * math.pi / 4.0),
                r * math.sin(math.pi / 8.0 + k * math.pi / 4.0)) for k in range(8)]
    margin = 0.01
    shrunk = [(x * (1 - margin / r), z * (1 - margin / r)) for x, z in octagon]
    for verts, _faces in glyphs:
        for x, z in verts:
            assert _inside((x, z), shrunk), (which, x, z)
    # centred
    xs = [x for verts, _f in glyphs for x, _z in verts]
    zs = [z for verts, _f in glyphs for _x, z in verts]
    assert math.isclose(min(xs), -max(xs), abs_tol=1e-9)
    assert math.isclose(min(zs), -max(zs), abs_tol=1e-9)
    assert math.isclose(max(xs) - min(xs), lw)


def test_the_budget_carries_the_legend():
    g = json.load(open(_GENOME, encoding="utf-8"))
    # 372 tris measured at 0.75 x 0.08 x 2.85 through the kit path (0.78.0)
    assert g["budgets"]["tris_lod0"] >= 372
