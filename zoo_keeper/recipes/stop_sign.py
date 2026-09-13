"""stop_sign recipe: an octagonal blade on a u-channel post.

Roadmap 153, the 1990s American street. A stop sign is a 30-inch (0.75 m)
octagon, red with a white border, its bottom edge about 2.1 m above the
kerb on a galvanised u-channel post. The octagon is built as a prism with
eight sides -- the silhouette is the sign, and at any distance a driver
or a player reads the shape before the word.

The blade is a separate part on its own material so a Pixelcoat sign face
can be dropped on it later without touching the post; until then the
white border is geometry (a slightly larger white octagon behind the red
one), which is how the sign reads from across the street.

THE LEGEND IS GEOMETRY TOO, for the same reason. Up to 0.77.0 the sign was
a red octagon with a white rim and no word on it ("the stop sign has no
legend", the walker). The white STOP is four faceted glyphs from
`_legend` -- a third of the sign's width tall, centred, each a closed solid
whose front stands LEGEND_PROUD in front of the red face and whose back is
buried LEGEND_BURY behind it, in the border, so no legend face shares a
plane with any face of the sign.

Collision is the POST only: a body walks into a pole, never into a blade
2 m over its head. Centre pivot; extents exactly (w, d, h).
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from . import _legend

POST = 0.06
BLADE_T = 0.015
#: How far the red face stands proud of the white border. Enough that the two
#: never share a plane at any distance the depth buffer resolves.
FACE_PROUD = 0.004
BORDER = 0.035        # white margin around the red face
#: How far the legend's front stands in front of the red face: the same
#: depth-buffer argument as FACE_PROUD, so the same number.
LEGEND_PROUD = FACE_PROUD
#: How far the legend's back sits behind the red face's front: through the red
#: face and half-way into the border. FACE_PROUD / 2 was tried first and put
#: the back cap 1.93 mm from both of the red face's planes at the default
#: size and 1.35 mm at the genome's smallest, where `fit_to` squeezes the
#: depth -- enclosed, but inside the 2 mm tools/coplanar_probe.py reports.
#: Half the border's 15 mm keeps it 7.5 mm (5 mm squeezed) from every plane.
LEGEND_BURY = FACE_PROUD + BLADE_T / 2.0


def _glyph_solid(bm, verts2d, faces, y_front, y_back):
    """Extrude one flat glyph (``(x, z)`` verts, CCW from the front) into a
    closed prism between ``y_front`` and ``y_back`` (y_front < y_back)."""
    front = [bm.verts.new((x, y_front, z)) for x, z in verts2d]
    back = [bm.verts.new((x, y_back, z)) for x, z in verts2d]
    edges = {}
    for f in faces:
        # (x, z) counter-clockwise with x right and z up: (1,0,0) x (0,0,1)
        # is (0,-1,0), so the authored order already faces -Y
        bm.faces.new([front[i] for i in f])
        bm.faces.new([back[i] for i in reversed(f)])
        for k in range(len(f)):
            a, b = f[k], f[(k + 1) % len(f)]
            edges[(a, b)] = edges.get((a, b), 0) + 1
    # a boundary edge is one no neighbouring cell walks the other way; its
    # wall is wound so the normal points away from the glyph
    for (a, b) in edges:
        if (b, a) not in edges:
            bm.faces.new((front[b], front[a], back[a], back[b]))


def _octagon(bm, centre, across, thickness):
    """A regular octagon prism ``across`` flats-to-flats, lying in XZ (its
    face toward -Y), ``thickness`` deep."""
    cx, cy, cz = centre
    r = across / 2.0 / math.cos(math.pi / 8.0)     # circumradius from flats
    verts = geometry.add_cylinder(bm, (0.0, 0.0, 0.0), r, thickness,
                                  segments=8, axis="Y")
    # a Y-axis cylinder's 8 segments start at an edge; turn it an eighth so
    # the octagon stands on a flat, the way a sign is hung
    a = math.pi / 8.0
    ca, sa = math.cos(a), math.sin(a)
    for v in verts:
        x, z = v.co.x, v.co.z
        v.co.x = x * ca - z * sa + cx
        v.co.z = x * sa + z * ca + cz
        v.co.y += cy
    return verts


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]      # the blade, flats to flats
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]     # grade to the blade's top
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    steel, faces = [], []

    def part(bm, name, into, texel=1.2, part_bevel=None):
        obj = geometry.bm_to_object(
            bm, name, collection, bevel=bevel if part_bevel is None else part_bevel,
            texel=texel, rng=rng, wear=wear)
        objs.append(obj)
        into.append(obj)
        return obj

    blade_top = h / 2.0
    blade_c = blade_top - w / 2.0
    # post: grade to just under the blade's centre, and the only collider
    post_top = blade_c
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + (post_top - z0) / 2.0),
                     (POST, POST, post_top - z0))
    part(bm, "StopSign_Post", steel)
    cboxes.append(((-POST / 2.0, -POST / 2.0, z0),
                   (POST / 2.0, POST / 2.0, post_top)))

    # THE BLADE HANGS ON THE POST'S FRONT (the face looks toward -Y). It
    # used to sit inside the post's 6 cm depth, which put the post's front
    # face 19 mm in front of the red face: the pole in front of the sign (the
    # walker, cold run 9048). The border's back now touches the post's front
    # face; the red face stands FACE_PROUD in front of the border.
    border_c = -(POST / 2.0 + BLADE_T / 2.0)
    bm = geometry.new_bm()
    _octagon(bm, (0.0, border_c, blade_c), w, BLADE_T)
    border = part(bm, "StopSign_Border", [], part_bevel=0.0)

    face_c = -(POST / 2.0 + BLADE_T + FACE_PROUD / 2.0)
    bm = geometry.new_bm()
    _octagon(bm, (0.0, face_c, blade_c), w - 2.0 * BORDER, FACE_PROUD)
    part(bm, "StopSign_Face", faces, part_bevel=0.0)

    # the legend: STOP, a third of the width tall, centred on the blade
    red_front = -(POST / 2.0 + BLADE_T + FACE_PROUD)
    glyphs, _size = _legend.legend("STOP", w * _legend.LEGEND_H_OF_WIDTH)
    bm = geometry.new_bm()
    for verts2d, gfaces in glyphs:
        _glyph_solid(bm, [(x, z + blade_c) for x, z in verts2d], gfaces,
                     red_front - LEGEND_PROUD, red_front + LEGEND_BURY)
    legend = part(bm, "StopSign_Legend", [], part_bevel=0.0)

    post_mat = materials.make_material(
        f"M_StopSign_{plan['material']}", plan["color"], plan["material"])
    red = materials.make_material("M_StopSign_face", [0.62, 0.07, 0.09],
                                  "metal_painted")
    white = materials.make_material("M_StopSign_border", [0.86, 0.86, 0.84],
                                    "metal_painted")
    materials.assign(steel, post_mat)
    materials.assign(faces, red)
    materials.assign([border, legend], white)
    # the slot is exact; the detail is not (geometry.fit_to)
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_face": (0.0, face_c - FACE_PROUD / 2.0,
                                         blade_c)}}
