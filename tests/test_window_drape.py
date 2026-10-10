"""A den's window drawn shut: two velvet panels under a pelmet (1.91.0).

The walker, 2026-10-09 (roadmap 219, note 2): "the windows in any 'den of sin'
building should have curtains or drapes or blinds So people outside can't see
in, and you keep the streetlight light out of the club". What is held: the
drape is its slot exactly at every genome corner, inside its budget, with no
coincident faces; its pleats stay under the smoothing angle, which is why it
has the facets it has; both sides are cloth; the panels cross at the middle as
two parallel sheets; the velvet is the club chairs'; and built, it is one
velvet mesh with no collision.
"""
from __future__ import annotations

import itertools
import json
import os
import struct

import pytest

from zoo_keeper.core import club_forms as CF
from zoo_keeper.core import window_drape_forms as DF
from zoo_keeper.core import genome
from zoo_keeper.core import prims as P

G = genome.load_species("window_drape")
DIMS = [(G["dimensions"][k]["min"], G["dimensions"][k]["max"]) for k in ("width", "depth", "height")]
CORNERS = list(itertools.product(*DIMS))


def _normal(vs, f):
    a, b, c = vs[f[0]], vs[f[1]], vs[f[2]]
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


@pytest.mark.parametrize("w,d,h", CORNERS)
def test_the_drape_is_its_slot_exactly_inside_its_budget(w, d, h):
    prims = DF.plan_drape(w, d, h)["prims"]
    lo, hi = P.bounds(prims)
    for got, want in zip(lo + hi, (-w / 2, -d / 2, 0.0, w / 2, d / 2, h)):
        assert got == pytest.approx(want, abs=1e-9), (lo, hi)
    assert P.tri_count(prims) <= G["budgets"]["tris_lod0"], P.tri_count(prims)
    assert P.coincident_pairs(prims) == []


def test_the_pleats_stay_under_the_smoothing_angle():
    """Zoo smooths across an edge whose faces meet under 50 degrees. At 12
    facets a pitch the sharpest turn, at the crest, is 43.8 degrees; at 8 it
    is 60.7 and the crest would split into a ridge -- the count is derived."""
    assert DF.max_facet_turn() < 50.0
    assert DF.max_facet_turn(DF.SWING * DF.TOP_SWING) < DF.max_facet_turn()
    keep = DF.PLEAT_SAMPLES
    try:
        DF.PLEAT_SAMPLES = 8
        assert DF.max_facet_turn() > 50.0
    finally:
        DF.PLEAT_SAMPLES = keep


def test_both_sides_are_cloth():
    """The street sees the back through the glass: every panel's front faces
    the room (-y), its back the glass (+y), its hem the floor."""
    for p in DF.plan_drape(1.5, 0.16, 1.62)["prims"]:
        if p["part"] != "Drape_Panel":
            continue
        vs, fs = p["verts"], p["faces"]
        cols = (len(fs) - 2) // 3
        for i in range(cols):
            assert _normal(vs, fs[3 * i])[1] < 0.0
            assert _normal(vs, fs[3 * i + 1])[1] > 0.0
            assert _normal(vs, fs[3 * i + 2])[2] < 0.0
        assert _normal(vs, fs[-2])[0] < 0.0 < _normal(vs, fs[-1])[0]


def test_the_panels_cross_at_the_middle_as_two_sheets():
    """No slit shows the glass, and where the panels cross the nearer one's
    back stays clear of the farther one's front -- parallel, never through."""
    panels = [p for p in DF.plan_drape(1.5, 0.16, 1.62)["prims"] if p["part"] == "Drape_Panel"]
    assert len(panels) == 2
    left, right = sorted(panels, key=lambda p: min(v[0] for v in p["verts"]))
    assert max(v[0] for v in left["verts"]) >= DF.OVERLAP / 2.0 - 1e-9
    assert min(v[0] for v in right["verts"]) <= -DF.OVERLAP / 2.0 + 1e-9
    def at(ring, x):
        pts = sorted((v[0], v[1]) for v in ring)
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * ((x - x0) / (x1 - x0) if x1 > x0 else 0.0)
        return None

    # rings of m: front hem, front top, back hem, back top (`_panel`)
    m = len(right["verts"]) // 4
    ml = len(left["verts"]) // 4
    gaps = []
    for ring in (0, 1):                          # the hem, then under the pelmet
        far_front = left["verts"][ring * ml:(ring + 1) * ml]
        for v in right["verts"][(2 + ring) * m:(3 + ring) * m]:
            if -DF.OVERLAP / 2.0 <= v[0] <= DF.OVERLAP / 2.0:
                y = at(far_front, v[0])
                if y is not None:
                    gaps.append(y - v[1])
    # a sample a facet across the overlap, at the hem and under the pelmet
    assert len(gaps) >= 2 * int(DF.OVERLAP / (DF.PLEAT_PITCH / DF.PLEAT_SAMPLES)), len(gaps)
    # clear by more than the census's 2 mm, everywhere they cross
    assert min(gaps) >= 0.002, min(gaps)


def test_the_velvet_is_the_club_chairs():
    """The comp's red, as the club's own velvet: one material, no collision."""
    assert DF.VELVET == list(CF.VELVETS[0][0])
    for style in G["styles"].values():
        assert style["material"] == "velvet" and style["color"] == DF.VELVET
    assert G["materials"]["options"] == ["velvet"]
    assert G["collision"] is False and DF.plan_drape(1.5, 0.16, 1.7)["collision"] == []
    assert {p["mat"] for p in DF.plan_drape(1.5, 0.16, 1.7)["prims"]} == {"velvet"}


def test_bpy_a_drape_is_one_velvet_mesh_with_no_collision(tmp_path):
    pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import kit
    slot = {"slot_id": "drape", "role": "prop", "size_mod": "full", "style": 1,
            "species": "window_drape", "material": "velvet",
            "fit": {"dims": [1.5, 0.16, 1.62], "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    doc = json.loads(raw[20:20 + struct.unpack("<I", raw[12:16])[0]])
    want = "M_WindowDrape_velvet_" + "".join("%02x" % int(round(v * 255)) for v in DF.VELVET)
    assert [m["name"] for m in doc["materials"]] == [want], doc["materials"]
    # one submission: the pelmet and the panels pack into one primitive
    meshes = [n for n in doc["nodes"] if "mesh" in n]
    assert sum(len(doc["meshes"][n["mesh"]]["primitives"]) for n in meshes) == 1, \
        [n["name"] for n in meshes]
    # no collision proxy (`-colonly`): the window's pane seals the opening
    assert not any("colonly" in n["name"] for n in doc["nodes"]), [n["name"] for n in doc["nodes"]]
