"""Grime at a wall's base (1.154.0, the factory's roadmap 324).

Patina (>= 0.40.0) orders a `stain_base` along each span of a ground storey's wall between its corners and openings,
naming the wall's kind. Zoo lays a grid `STAIN_PROUD` off the wall, darkest at the ground and fading up to a top edge
that wanders, in the wall's own skin renamed with `STAIN_SUFFIX` -- a stain in every other way, so Level Factory's
overlay (>= 0.271.0) draws it in the building's one stain mesh.
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import genome
from zoo_keeper.core import dressing as D

SPACE = "spec/Blender Z-up raw coords"


def test_grime_is_darkest_at_the_ground_and_fades_up_and_out():
    """FAILS ON 1.153.0: no grime."""
    verts, faces, shade = D.grime_grid(6.0, 0.6, 11)
    cols = len({round(v[0], 6) for v in verts}) - 1
    rows = D.GRIME_ROWS
    assert cols == 20 and len(verts) == (cols + 1) * (rows + 1) and len(faces) == cols * rows
    ground, top = shade[: cols + 1], shade[rows * (cols + 1):]
    # the ground row carries the darkest, never past GRIME_DARK; the top row is the wall exactly
    assert min(ground) >= D.GRIME_DARK - 1e-9 and min(ground) < 0.75
    assert all(s == 1.0 for s in top)
    # both ends are the wall exactly: a span ends at a corner or an opening
    for j in range(rows + 1):
        assert shade[j * (cols + 1)] == 1.0 and shade[j * (cols + 1) + cols] == 1.0
    # darkness falls going up every column
    for i in range(1, cols):
        col = [shade[j * (cols + 1) + i] for j in range(rows + 1)]
        assert col == sorted(col)


def test_its_top_edge_wanders_inside_the_band_and_its_foot_is_on_the_ground():
    verts, _faces, _shade = D.grime_grid(6.0, 0.6, 11)
    cols = 20
    foot = [v[2] for v in verts[: cols + 1]]
    tops = [v[2] for v in verts[D.GRIME_ROWS * (cols + 1):]]
    assert all(z == 0.0 for z in foot)
    assert all(0.6 * D.GRIME_TOP[0] - 1e-9 <= z <= 0.6 + 1e-9 for z in tops)
    assert max(tops) - min(tops) > 0.05
    assert all(abs(v[1] - D.STAIN_PROUD) < 1e-12 for v in verts)


def test_deterministic_for_a_seed():
    assert D.grime_grid(4.0, 0.5, 3) == D.grime_grid(4.0, 0.5, 3)
    assert D.grime_grid(4.0, 0.5, 3) != D.grime_grid(4.0, 0.5, 4)


def test_it_is_a_stain_and_wears_the_walls_kind():
    assert "stain_base" in D.STAIN_COVERS
    order = {"cover": "stain_base", "pos": [0.0, 11.0, 0.0], "normal": [0.0, 1.0, 0.0], "size": 6.0,
             "size2": [6.0, 0.6], "collision": "none", "seed_offset": 11, "wall_material": "brick"}
    plan = D.dress_plan(order, genome.load_species("dress_cover"), "delco_1997", SPACE, TOOL_VERSION)
    assert plan["material"] == "brick"
    assert plan["order"]["size2"] == [6.0, 0.6]


def test_bpy_the_grime_is_the_walls_skin_renamed_with_its_colours(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    order = {"cover": "stain_base", "pos": [0.0, 11.0, 0.0], "normal": [0.0, 1.0, 0.0], "size": 6.0,
             "size2": [6.0, 0.6], "collision": "none", "seed_offset": 11, "wall_material": "brick"}
    manifest = {"schema": "patina-dressing/1", "building_id": "t_bank", "space": SPACE, "orders": [order]}
    B.build_dressing(manifest, str(tmp_path), theme="delco_1997", options={"save_blend": False})
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    assert objs
    me = objs[0].data
    assert any(m.name.endswith(D.STAIN_SUFFIX) for m in me.materials), [m.name for m in me.materials]
    vals = [d.color[0] for d in me.color_attributes["Wear"].data]
    assert min(vals) < 0.8 and max(vals) == pytest.approx(1.0)


def _face_normals(verts, faces):
    out = []
    for f in faces:
        a, b, c = (verts[k] for k in f[:3])
        e1 = [b[i] - a[i] for i in range(3)]
        e2 = [c[i] - a[i] for i in range(3)]
        out.append((e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]))
    return out


def test_every_face_of_both_grids_faces_out_of_the_wall():
    """FAILS ON slice 18's grime_grid: its rows run up where a streak's run down, the same winding faced it into the
    wall, and the overlay's back-face culling drew none of it. Cover-local +y is out of the wall, for both."""
    for verts, faces, _shade in (D.grime_grid(6.0, 0.6, 11), D.stain_grid(0.9, 1.4, 7)):
        assert all(n[1] > 0 for n in _face_normals(verts, faces))
