"""Floaters (1.106.0, factory roadmap 234; the README's "Floaters"): a detail made as its own mesh and laid on a
surface, built in its own frame and carried onto the host by one rule.

The pure half checks `core.floaters`: the two numbers against the census they answer to, the frame on every
kind of normal, a solid floater resting with only its skirt below the host, a flat floater standing proud and
facing out. The bpy half builds floaters with `bpylayer.geometry.add_floater` and `add_flat_floater` and reads
the vertices back; it skips without Blender and was run inside Blender 5.1.1 for this change, from the repo
root:

    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, '.'); print('rc', int(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_floaters.py'])))"

On 1.105.0 there is no `core.floaters`, so the module fails to import and every test here fails with it.
"""
import math

import pytest

from tests.test_coincident_faces import PROBE_TOL, fight_distance_m
from zoo_keeper.core import floaters

NORMALS = [(0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (1, 1, 0), (0.3, -0.2, 0.9),
           (0.95, 0.31, 0.0), (-0.9, 0.1, 0.42), (0.0, 0.7, -0.7)]
SPINS = [0.0, 0.7, math.pi / 2, -2.0, math.pi]
EPS = 1e-9


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _unit(v):
    n = math.sqrt(_dot(v, v))
    return tuple(c / n for c in v)


def test_the_skirt_goes_past_the_census_window():
    """FAILS ON 1.105.0: there is no `core.floaters`."""
    assert floaters.PROBE_WINDOW == PROBE_TOL
    assert floaters.FLOATER_SKIRT > floaters.PROBE_WINDOW


def test_a_flat_floater_stands_far_enough_to_fight_only_beyond_fifty_metres():
    assert floaters.FLOATER_PROUD > floaters.PROBE_WINDOW
    assert fight_distance_m(floaters.FLOATER_PROUD * 1000.0) >= 50.0


@pytest.mark.parametrize("normal", NORMALS)
def test_the_frame_is_orthonormal_right_handed_and_stands_on_the_normal(normal):
    for spin in SPINS:
        x, y, z = floaters.basis(normal, spin)
        for v in (x, y, z):
            assert abs(_dot(v, v) - 1.0) < EPS
        assert abs(_dot(x, y)) < EPS and abs(_dot(x, z)) < EPS and abs(_dot(y, z)) < EPS
        assert all(abs(a - b) < EPS for a, b in zip(floaters._cross(x, y), z))
        assert all(abs(a - b) < EPS for a, b in zip(z, _unit(normal)))


@pytest.mark.parametrize("normal", NORMALS)
def test_spin_turns_the_frame_about_the_normal(normal):
    x0, y0, _ = floaters.basis(normal, 0.0)
    for spin in SPINS:
        x, _, _ = floaters.basis(normal, spin)
        assert abs(_dot(x, x0) - math.cos(spin)) < 1e-9
        assert abs(_dot(x, y0) - math.sin(spin)) < 1e-9


@pytest.mark.parametrize("normal", NORMALS)
def test_a_solid_floater_rests_with_only_its_skirt_below_the_host(normal):
    point = (0.4, -1.2, 0.85)
    n = _unit(normal)
    for spin in (0.0, 1.1):
        m = floaters.solid_frame(point, normal, spin)
        x, y, _ = floaters.basis(normal, spin)
        for local in ((0.0, 0.0, 0.0), (0.05, -0.02, 0.0), (0.03, 0.01, 0.07)):
            p = floaters.apply(m, local)
            # how far off the host plane: its height in its own frame, less the skirt
            assert abs(_dot(_sub(p, point), n) - (local[2] - floaters.FLOATER_SKIRT)) < EPS
            # and where along it: its own x and y, on the host's turned axes
            assert abs(_dot(_sub(p, point), x) - local[0]) < EPS
            assert abs(_dot(_sub(p, point), y) - local[1]) < EPS


@pytest.mark.parametrize("normal", NORMALS)
def test_a_flat_floater_stands_proud_and_faces_along_the_normal(normal):
    point, w, h = (-2.0, 0.5, 1.25), 0.3, 0.12
    n = _unit(normal)
    for spin in (0.0, 0.6):
        q = floaters.flat_quad(point, normal, w, h, spin)
        for c in q:
            assert abs(_dot(_sub(c, point), n) - floaters.FLOATER_PROUD) < EPS
        face = floaters._cross(_sub(q[1], q[0]), _sub(q[2], q[0]))
        assert _dot(_unit(face), n) > 1.0 - EPS
        x, y, _ = floaters.basis(normal, spin)
        assert abs(_dot(_sub(q[1], q[0]), x) - w) < EPS
        assert abs(_dot(_sub(q[3], q[0]), y) - h) < EPS


def test_what_it_cannot_lay_it_refuses():
    with pytest.raises(ValueError):
        floaters.basis((0.0, 0.0, 0.0))
    with pytest.raises(ValueError):
        floaters.solid_frame((0, 0, 0), (0, 0, 1), skirt=-0.001)
    with pytest.raises(ValueError):
        floaters.flat_quad((0, 0, 0), (0, 0, 1), 0.1, 0.1, proud=0.0)


def test_the_same_floater_lands_in_the_same_place():
    a = floaters.flat_quad((1, 2, 3), (0.2, 0.3, 0.9), 0.4, 0.2, 0.5)
    b = floaters.flat_quad((1, 2, 3), (0.2, 0.3, 0.9), 0.4, 0.2, 0.5)
    assert a == b


# --- the bpy half: built and read back ---------------------------------------

def _bpy():
    try:
        import bmesh  # noqa: F401
        from zoo_keeper.bpylayer import geometry
    except ImportError:
        pytest.skip("needs Blender: bpylayer.geometry imports bpy and bmesh")
    return geometry


@pytest.mark.parametrize("normal", [(0, 0, 1), (1, 0, 0), (0.0, -0.6, 0.8)])
def test_a_built_floater_rests_on_its_host(normal):
    geometry = _bpy()
    bm = geometry.new_bm()
    point = (0.1, 0.2, 0.3)

    def knob(b):
        # a cylinder 0.05 tall, its base at z = 0 in its own frame
        return geometry.add_cylinder(b, (0.0, 0.0, 0.025), 0.02, 0.05, segments=8)

    verts = geometry.add_floater(bm, point, normal, knob, spin=0.4)
    n = _unit(normal)
    heights = sorted(_dot(_sub(tuple(v.co), point), n) for v in verts)
    assert abs(heights[0] + geometry.FLOATER_SKIRT) < 1e-5, heights[0]
    assert abs(heights[-1] - (0.05 - geometry.FLOATER_SKIRT)) < 1e-5, heights[-1]
    bm.free()


@pytest.mark.parametrize("normal", [(0, 0, 1), (-1, 0, 0), (0.6, 0.0, -0.8)])
def test_a_built_flat_floater_faces_out_proud(normal):
    geometry = _bpy()
    bm = geometry.new_bm()
    point = (0.5, -0.5, 1.0)
    face = geometry.add_flat_floater(bm, point, normal, 0.2, 0.1, spin=0.3)
    n = _unit(normal)
    bm.normal_update()
    assert _dot(tuple(face.normal), n) > 1.0 - 1e-5
    for v in face.verts:
        assert abs(_dot(_sub(tuple(v.co), point), n) - geometry.FLOATER_PROUD) < 1e-5
    bm.free()
