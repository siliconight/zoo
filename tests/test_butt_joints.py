"""A module's end edges are not bevelled, so a run of modules has no groove.

Walk 9052, delco_1997, an interior partition: "you can see the seams here",
and a thin bright vertical line at every 2.00 m. Measured on the walk copy's
own `site.tscn` and module GLBs over all three buildings, 434 joints between
consecutive modules of a run:

    gap along the run      0.000 mm at every joint
    depth-face offset      0.000 mm at every joint
    V-groove               6.00 mm wide x 3.00 mm deep at 300 of them

Deli Counter lays the modules flush and coplanar; what drew the line was the
style's 3 mm bevel on each module's END edges, two 45-degree facets meeting
in a V. A rebuilt kit with those edges sharp measures 0.00 mm at 48 of
strip_retail_a02's 52 joints (the other 4 were window modules left as
shipped), and in the rendered frame the joint columns go from 22-30 codes of
line contrast to the texture's own 4-6.

The pure half (which planes, which edges) runs anywhere. The bpy half builds
a wall and a doorway and reads the mesh; it skips without Blender and was run
inside Blender 5.1 for this change.
"""

import ast
import os

import pytest

from zoo_keeper.core import arch

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ARCH_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "_arch.py")
_GEOMETRY = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "geometry.py")


# --- which planes -----------------------------------------------------------

@pytest.mark.parametrize("species", ["wall", "wallEnd", "doorway", "window", "breach"])
def test_a_standing_module_meets_its_neighbours_at_its_two_ends(species):
    assert arch.butt_planes(species, 2.0) == ((0, -1.0), (0, 1.0))


@pytest.mark.parametrize("species", arch.PLATE_SPECIES)
def test_plates_declare_no_butt_planes(species):
    """Their tiles are unbevelled already; nothing to exempt."""
    assert arch.butt_planes(species, 12.0) == ()


def test_a_prop_stands_alone_and_keeps_every_chamfer():
    """`prop` shares the slab builder with walls; a desk's ends are corners."""
    assert arch.butt_planes("prop", 1.6) == ()


def test_the_tolerance_is_below_any_bevel_a_style_uses():
    """A chamfered vertex sits one bevel inside the plane; it must never pass."""
    assert arch.BUTT_TOL < 0.002


# --- which edges -------------------------------------------------------------

_W, _D, _H = 2.0, 0.3, 3.1


def _planes():
    return arch.butt_planes("wall", _W)


def test_the_vertical_edge_at_a_module_end_is_a_butt_edge():
    a = (1.0, -_D / 2, -_H / 2)
    b = (1.0, -_D / 2, _H / 2)
    assert arch.edge_on_butt_plane(a, b, _planes())


def test_the_top_edge_of_a_face_is_not_although_both_ends_touch_a_butt_plane():
    """One end on each plane lies in neither: the chamfer along the top stays."""
    a = (-1.0, -_D / 2, _H / 2)
    b = (1.0, -_D / 2, _H / 2)
    assert not arch.edge_on_butt_plane(a, b, _planes())


def test_a_jamb_reveal_is_a_real_corner_and_keeps_its_chamfer():
    """A 1.25 m doorway's jamb: its outer end is a butt edge, its reveal is not."""
    planes = arch.butt_planes("doorway", 1.25)
    outer = ((-0.625, -_D / 2, -_H / 2), (-0.625, -_D / 2, _H / 2))
    reveal = ((-0.505, -_D / 2, -_H / 2), (-0.505, -_D / 2, _H / 2))
    assert arch.edge_on_butt_plane(*outer, planes)
    assert not arch.edge_on_butt_plane(*reveal, planes)


def test_a_bevelled_vertex_one_chamfer_inside_the_plane_is_not_on_it():
    a = (0.997, -_D / 2, -_H / 2)
    b = (0.997, -_D / 2, _H / 2)
    assert not arch.edge_on_butt_plane(a, b, _planes())


# --- the recipe asks, and the bevel listens -----------------------------------

def _src(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def test_every_architectural_part_is_finished_with_the_butt_planes():
    calls = [n for n in ast.walk(ast.parse(_src(_ARCH_RECIPE)))
             if isinstance(n, ast.Call)
             and getattr(n.func, "attr", None) == "bm_to_object"]
    structural = [c for c in calls
                  if not any(k.arg == "bevel" and isinstance(k.value, ast.Constant)
                             and k.value.value == 0.0 for k in c.keywords)]
    assert structural, "no bevelled bm_to_object call found in _arch.py"
    for c in structural:
        assert any(k.arg == "butt_planes" for k in c.keywords), ast.dump(c)[:200]


def test_bm_to_object_hands_the_planes_to_the_bevel():
    tree = ast.parse(_src(_GEOMETRY))
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "bm_to_object")
    bevels = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
              and getattr(n.func, "id", None) == "bevel_edges"]
    assert bevels and all(any(k.arg == "butt_planes" for k in c.keywords)
                          for c in bevels)


# --- bpy: a built module has no chamfer at its ends ----------------------------

def _build(tmp_path, species, width_cm):
    import bpy
    from zoo_keeper.bpylayer import build as B, materials
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    materials.set_skin_library(None)
    w = width_cm / 100.0
    module = {"type": species, "species": species, "width_cm": width_cm,
              "fit": "exact", "dims": [w, _D, _H], "pivot": "center",
              "stem": f"{species}_delco_1997_02_w{width_cm}", "style": 2,
              "material": "drywall", "openings": [], "voids": []}
    B.build_module(module, str(tmp_path / "out"), theme="delco_1997",
                   style=2, options={"collision": False})
    return w, [o for o in bpy.data.objects if o.type == "MESH"
               and "colonly" not in o.name]


def _xs(objs):
    return sorted({round(v.co.x, 4) for o in objs for v in o.data.vertices})


def test_bpy_a_wall_has_no_chamfer_at_its_ends_and_keeps_its_top(tmp_path):
    pytest.importorskip("bpy")
    w, objs = _build(tmp_path, "wall", 200)
    xs = _xs(objs)
    assert xs[0] == pytest.approx(-w / 2) and xs[-1] == pytest.approx(w / 2)
    inside = [x for x in xs if w / 2 - 0.01 < abs(x) < w / 2 - 1e-4]
    assert not inside, inside
    zs = sorted({round(v.co.z, 4) for o in objs for v in o.data.vertices})
    assert any(0.0 < _H / 2 - z < 0.01 for z in zs), zs      # top chamfer kept


def test_bpy_a_doorway_keeps_its_reveal_and_loses_its_ends(tmp_path):
    pytest.importorskip("bpy")
    w, objs = _build(tmp_path, "doorway", 125)
    xs = _xs(objs)
    assert not [x for x in xs if w / 2 - 0.01 < abs(x) < w / 2 - 1e-4], xs
    reveal = arch.void_for("doorway", w, _H)["x1"]
    assert any(0.0 < abs(abs(x) - reveal) < 0.01 for x in xs), (reveal, xs)
