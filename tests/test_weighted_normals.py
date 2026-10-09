"""Weighted normals (1.87.0, roadmap 214, trial 1).

`core.normals.weighted_corner_normals` is checked here on a chamfered prism:
a 1.986 m top face and a 1.986 m side face meeting through a 1.4 cm, 45-degree
chamfer, all 2 m long. Without Blender: the Blender half
(`bpylayer.geometry.weight_normals`, the export and the merge) is measured by
`docs/findings/weighted_normals/`, and the wiring is pinned by the source
checks at the bottom.

On 1.86.0 none of this runs: there is no `core.normals`, so the module fails
to import and every test here fails with it.
"""
import math
import os
import re

from zoo_keeper.core import normals

C, L = 0.014, 2.0
S = math.sqrt(0.5)
#: 0..3 the top face, 4..5 the chamfer's lower edge, 6..7 the side's foot.
VERTS = [(-1, 0, 1), (1 - C, 0, 1), (1 - C, L, 1), (-1, L, 1),
         (1, 0, 1 - C), (1, L, 1 - C), (1, 0, -1), (1, L, -1)]
TOP, CHAMFER, SIDE = [0, 1, 2, 3], [1, 4, 5, 2], [4, 6, 7, 5]
FACES = [TOP, CHAMFER, SIDE]
NORMALS = [(0.0, 0.0, 1.0), (S, 0.0, S), (1.0, 0.0, 0.0)]
AREAS = [(2 - C) * L, C * math.sqrt(2) * L, (2 - C) * L]
UP, OUT = (0.0, 0.0, 1.0), (1.0, 0.0, 0.0)


def _deg(a, b):
    d = sum(x * y for x, y in zip(a, b))
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))


def _corners(faces=FACES, normals_=NORMALS, areas=AREAS, smooth=(True,) * 3,
             sharp=frozenset()):
    out = normals.weighted_corner_normals(faces, normals_, areas, list(smooth),
                                          set(sharp))
    rows, i = [], 0
    for f in faces:
        rows.append(dict(zip(f, out[i:i + len(f)])))
        i += len(f)
    return rows


def test_the_fixture_is_one_the_default_would_dome():
    """Weighed by corner angle -- every corner here is 90 degrees -- the top
    face's corner beside the chamfer sits 22.5 degrees off the face: the
    dome. Not code under test; it says the fixture exercises the defect."""
    n = [a + b for a, b in zip(NORMALS[0], NORMALS[1])]
    k = math.sqrt(sum(x * x for x in n))
    assert abs(_deg(UP, [x / k for x in n]) - 22.5) < 1e-9


def test_a_big_face_keeps_its_own_normal_beside_a_chamfer():
    top, _, side = _corners()
    expected = math.degrees(math.atan2(AREAS[1] * S, AREAS[0] + AREAS[1] * S))
    assert 0.39 < expected < 0.41, expected
    for v in (1, 2):
        assert abs(_deg(UP, top[v]) - expected) < 1e-9, top[v]
    for v in (0, 3):
        assert top[v] == UP
    for v in (6, 7):
        assert side[v] == OUT


def test_the_chamfer_rolls_from_one_face_to_the_other():
    _, ch, _ = _corners()
    for v in (1, 2):
        assert _deg(UP, ch[v]) < 0.5, ch[v]
    for v in (4, 5):
        assert _deg(OUT, ch[v]) < 0.5, ch[v]


def test_a_sharp_edge_splits_the_fan():
    top, ch, side = _corners(sharp={frozenset({1, 2})})
    assert all(top[v] == UP for v in TOP)
    for v in (1, 2):
        assert _deg(NORMALS[1], ch[v]) < 1e-9, ch[v]
    for v in (4, 5):
        assert _deg(OUT, ch[v]) < 0.5 and ch[v] == side[v]


def test_a_flat_face_keeps_its_own_normal_and_joins_no_fan():
    top, ch, _ = _corners(smooth=(False, True, True))
    assert all(top[v] == UP for v in TOP)
    for v in (1, 2):
        assert _deg(NORMALS[1], ch[v]) < 1e-9, ch[v]


def test_faces_wound_the_same_way_round_an_edge_are_not_one_fan():
    """A flipped face walks the edge in its neighbour's direction. Blender
    splits there, so the fans here must too."""
    flipped = [TOP, list(reversed(CHAMFER)), SIDE]
    normals_ = [UP, (-S, 0.0, -S), OUT]
    top, ch, side = _corners(faces=flipped, normals_=normals_)
    assert all(top[v] == UP for v in TOP)
    assert all(side[v] == OUT for v in SIDE)
    assert all(_deg(normals_[1], ch[v]) < 1e-9 for v in CHAMFER)


def test_every_fold_hard_is_every_face_its_own_normal():
    """`shade_by_angle(bm, 1.0)` -- "faceted on purpose" -- comes out exactly
    as before."""
    sharp = {frozenset({1, 2}), frozenset({4, 5})}
    rows = _corners(sharp=sharp)
    for f, n, row in zip(FACES, NORMALS, rows):
        assert all(_deg(n, row[v]) < 1e-9 for v in f)


def test_a_fan_of_degenerate_faces_keeps_the_default():
    out = normals.weighted_corner_normals([[0, 1, 2]], [UP], [0.0], [True], set())
    assert out == [(0.0, 0.0, 0.0)] * 3


def test_corners_come_in_face_then_corner_order():
    out = normals.weighted_corner_normals(FACES, NORMALS, AREAS, [True] * 3, set())
    assert len(out) == sum(len(f) for f in FACES) == 12
    assert out[0] == UP                      # the top face's first corner, vertex 0
    assert out[-2] == OUT                    # the side face's third corner, vertex 7


# --- the wiring, which needs Blender to run, pinned in the source ------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _src(*rel):
    with open(os.path.join(ROOT, *rel), encoding="utf-8") as f:
        return f.read()


def test_every_build_export_passes_the_option():
    """A path that omits it would ship the default silently, and the control
    (`--no-weighted-normals`) would not reach it."""
    src = _src("zoo_keeper", "bpylayer", "build.py")
    calls = re.findall(r"export\.export_glb\([^)]*\)", src)
    assert len(calls) >= 5, calls
    for call in calls:
        assert 'weighted_normals=opts["weighted_normals"]' in call, call
    assert re.search(r'"weighted_normals": True,', src)


def test_ingest_keeps_its_authors_normals():
    """An imported mesh carries the normals its author made (the glTF
    importer sets them as custom normals). Weighing them would overwrite
    that work."""
    src = _src("zoo_keeper", "bpylayer", "ingest.py")
    assert re.search(r"export_glb\(glb_path, coll, weighted_normals=False\)", src)


def test_the_merge_carries_each_parts_corner_normals():
    """The merge copies faces into a new mesh, whose default normals are
    recomputed from its edges. That reproduced the parts' default normals
    exactly, because nothing welds; it cannot reproduce custom ones."""
    src = _src("zoo_keeper", "bpylayer", "merge.py")
    assert "corner_normals" in src and "normals_split_custom_set" in src
