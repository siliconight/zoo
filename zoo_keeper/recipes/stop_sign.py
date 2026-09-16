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
buried LEGEND_BURY behind it, in the border.

NO TWO OF THIS SIGN'S FACES SHARE A PLANE. That was said of the legend from
0.78.0 and was never true of the sign: the red face's back cap lay on the
border's front cap and the border's back cap lay on the post's front face,
both at 0.00 mm over the whole octagon. See the y ladder below.

Collision is the POST only: a body walks into a pole, never into a blade
2 m over its head. Centre pivot; extents exactly (w, d, h).
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from . import _legend

POST = 0.06
BLADE_T = 0.015       # the blade's nominal thickness, edge-on
BORDER = 0.035        # white margin around the red face
#: How far the red face stands proud of the white border's front. The relief
#: that makes the octagon read as a raised sign rather than a painted disc.
FACE_PROUD = 0.004
#: How far the legend's front stands in front of the red face's front.
LEGEND_PROUD = FACE_PROUD

# --- the y ladder ------------------------------------------------------------
#
# EVERY PLANE IN THIS SIGN IS A RUNG AND NONE OF THEM MAY SHARE ONE. Up to
# 0.96.0 two pairs did, both at 0.00 mm over the whole octagon: the red face's
# BACK cap lay exactly on the border's FRONT cap, and the border's BACK cap
# exactly on the post's FRONT face. FACE_PROUD separated the face's front and
# nothing separated its back -- the recipe's own docstring claimed "no legend
# face shares a plane with any face of the sign", which was true of the legend
# and of nothing else. `core/sign_blade_forms.py` (0.96.0) spells the rule out
# for the same geometry: eleven parallel planes stack up behind a sign face,
# every one overlaps every other in projection, so the rule binds on all pairs
# at once and a solid is pushed THROUGH its neighbour rather than laid on it.
#
#: The window `tools/coplanar_probe.py` reports on, its own `--tol` default.
PROBE_TOL = 0.002
#: Floats land ON that number in a built scene -- 0.91.0 measured
#: `0.0020000000000000018 > 0.002` after the pure probe passed a pair
#: Blender's failed, and `tests/test_card_shop.py` has asked pure tests for
#: 2.2 mm ever since. The same tenth here.
PROBE_CUSHION = 1.1
#: What this recipe authors, front to back: the legend's front to the post's
#: back. `geometry.fit_to` scales exactly this into the slot's depth.
DEPTH_AUTHORED = POST + BLADE_T + FACE_PROUD + LEGEND_PROUD
#: The genome's smallest depth (`genome/species/stop_sign.json`, pinned by
#: tests/test_stop_legend.py). The smallest slot is the worst squeeze, and the
#: squeeze is what decides whether an authored gap survives into the GLB.
DEPTH_MIN = 0.056
#: THE FLOOR EVERY RUNG HAS TO CLEAR, computed rather than remembered: an
#: authored gap reaches the probe multiplied by DEPTH_MIN / DEPTH_AUTHORED
#: (0.675), so it has to be at least this much before the squeeze. Move any
#: of the four numbers above and this moves with them -- 3.26 mm today.
SEP_FLOOR = PROBE_TOL * PROBE_CUSHION * DEPTH_AUTHORED / DEPTH_MIN
#: THE SEPARATION: the next half-millimetre above that floor, which leaves
#: 2.36 mm in the smallest built sign. It is not a taste, and a test holds it
#: to the floor from both sides -- narrow it and the min corner fails.
SEP = 0.0035
#: The red plate is built thick enough to stand FACE_PROUD in front of the
#: border's front plane AND end SEP behind it, so neither of its caps shares
#: a plane with the border. Thickening a prism costs no triangles.
FACE_T = FACE_PROUD + SEP
#: The border likewise runs SEP past the post's front face, into the channel,
#: instead of stopping on it. THIS IS VISIBLE FROM BEHIND: the blade's back
#: cap is the blade's back everywhere except over the pole's own 6 cm, so the
#: white rim goes from 14.5 mm to 17.8 mm at the default size. Pulling the
#: blade forward instead would leave daylight between sign and pole, which is
#: cold run 9048's defect in mirror image; see the 0.97.0 entry for what the
#: version that held the rim at 14.5 mm would have cost.
BORDER_T = BLADE_T + SEP
#: How far the legend's back sits behind the red face's front: through the red
#: face and half-way into the border. FACE_PROUD / 2 was tried first and put
#: the back cap 1.93 mm from both of the red face's planes at the default
#: size and 1.35 mm at the genome's smallest -- enclosed, but inside the
#: window. At FACE_PROUD + BLADE_T / 2 its nearest neighbour is the red
#: face's back cap, 4.0 mm in front of it (2.7 mm squeezed).
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
    # walker, cold run 9048). The border's front is one blade thickness in
    # front of the post's front face and its back runs SEP past it, into the
    # channel, so the two never share a plane.
    border_front = -(POST / 2.0 + BLADE_T)
    border_c = border_front + BORDER_T / 2.0
    bm = geometry.new_bm()
    _octagon(bm, (0.0, border_c, blade_c), w, BORDER_T)
    border = part(bm, "StopSign_Border", [], part_bevel=0.0)

    # the red face stands FACE_PROUD in front of the border and ends SEP
    # behind its front plane, so neither cap lands on it
    red_front = border_front - FACE_PROUD
    face_c = red_front + FACE_T / 2.0
    bm = geometry.new_bm()
    _octagon(bm, (0.0, face_c, blade_c), w - 2.0 * BORDER, FACE_T)
    part(bm, "StopSign_Face", faces, part_bevel=0.0)

    # the legend: STOP, a third of the width tall, centred on the blade
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

    # the attachment is the RED FACE'S FRONT PLANE, which is where a Pixelcoat
    # sign face would land. It is `red_front` and not an offset from the
    # plate's centre: the plate's thickness is now FACE_T, so `face_c` less
    # half of FACE_PROUD stopped naming that plane.
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_face": (0.0, red_front, blade_c)}}
