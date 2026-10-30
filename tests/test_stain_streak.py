"""A stain where water runs down a wall (1.153.0, the factory's roadmap 324).

Patina (>= 0.39.0) orders a `stain_streak` below what sheds water onto a facade -- a sill, a coping, a scupper -- naming
the wall's kind as `wall_material`. Zoo lays a grid `STAIN_PROUD` off the wall in the WALL'S OWN SKIN, renamed with
`STAIN_SUFFIX` so Level Factory's import (>= 0.271.0) draws its vertex colour as a multiply overlay onto the wall:
darkest at the cause, fading down and out to nothing. The pure halves run anywhere; the build under Blender.
"""
import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome
from zoo_keeper.core import dressing as D

SPACE = "spec/Blender Z-up raw coords"


def _order(**kw):
    o = {"cover": "stain_streak", "pos": [0.0, 11.0, 4.0], "normal": [0.0, 1.0, 0.0], "size": 0.9,
         "size2": [0.9, 1.4], "collision": "none", "seed_offset": 7, "wall_material": "concrete"}
    o.update(kw)
    return o


def test_the_stain_is_darkest_at_its_cause_and_fades_to_nothing():
    """FAILS ON 1.152.0: no stain."""
    verts, faces, shade = D.stain_grid(0.9, 1.4, 7)
    cols, rows = D.STAIN_COLS, D.STAIN_ROWS
    assert len(verts) == (cols + 1) * (rows + 1) and len(faces) == cols * rows
    assert min(shade) >= D.STAIN_DARK - 1e-9 and min(shade) < 0.9
    foot = shade[rows * (cols + 1):]
    assert foot == [1.0] * (cols + 1)                                       # nothing at its foot
    assert all(shade[j * (cols + 1)] == 1.0 and shade[j * (cols + 1) + cols] == 1.0 for j in range(rows + 1))
    top = shade[: cols + 1]
    assert min(top) < min(shade[2 * (cols + 1): 3 * (cols + 1)])            # darker at the cause than below it
    assert all(abs(v[1] - D.STAIN_PROUD) < 1e-12 for v in verts)
    assert D.stain_grid(0.9, 1.4, 7) == (verts, faces, shade) and D.stain_grid(0.9, 1.4, 8)[2] != shade


def test_it_wears_the_walls_own_kind_and_colour():
    plan = D.dress_plan(_order(), genome.load_species("dress_cover"), "delco_1997", SPACE, TOOL_VERSION)
    wall = dna.theme_style(genome.load_species("wall"), "delco_1997")[1]
    assert plan["material"] == "concrete" and plan["color"] == [round(c, 4) for c in wall["color"]]
    brick = D.dress_plan(_order(wall_material="brick"), genome.load_species("dress_cover"), "delco_1997", SPACE,
                         TOOL_VERSION)
    assert brick["material"] == "brick"


def test_bpy_the_stain_is_the_walls_skin_renamed_with_its_colours_and_uvs(tmp_path):
    pytest.importorskip("bpy")
    import bpy
    from zoo_keeper.bpylayer import build as B
    manifest = {"schema": "patina-dressing/1", "building_id": "t_bank", "space": SPACE, "orders": [_order()]}
    B.build_dressing(manifest, str(tmp_path), theme="delco_1997", options={"save_blend": False})
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    assert objs
    me = objs[0].data
    assert any(m.name.endswith(D.STAIN_SUFFIX) for m in me.materials), [m.name for m in me.materials]
    assert me.uv_layers and me.color_attributes.get("Wear") is not None
    vals = [d.color[0] for d in me.color_attributes["Wear"].data]
    assert min(vals) < 0.9 and max(vals) == pytest.approx(1.0)
