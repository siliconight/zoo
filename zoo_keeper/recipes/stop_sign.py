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

Collision is the POST only: a body walks into a pole, never into a blade
2 m over its head. Centre pivot; extents exactly (w, d, h).
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials

POST = 0.06
BLADE_T = 0.015
BORDER = 0.035        # white margin around the red face


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

    # the white border: the outer octagon, a hair behind the red face
    bm = geometry.new_bm()
    _octagon(bm, (0.0, BLADE_T / 2.0, blade_c), w, BLADE_T)
    border = part(bm, "StopSign_Border", [], part_bevel=0.0)

    # the red face, inset by the border and proud of it
    bm = geometry.new_bm()
    _octagon(bm, (0.0, -BLADE_T / 4.0, blade_c), w - 2.0 * BORDER, BLADE_T)
    part(bm, "StopSign_Face", faces, part_bevel=0.0)

    post_mat = materials.make_material(
        f"M_StopSign_{plan['material']}", plan["color"], plan["material"])
    red = materials.make_material("M_StopSign_face", [0.62, 0.07, 0.09],
                                  "metal_painted")
    white = materials.make_material("M_StopSign_border", [0.86, 0.86, 0.84],
                                    "metal_painted")
    materials.assign(steel, post_mat)
    materials.assign(faces, red)
    materials.assign([border], white)
    # the slot is exact; the detail is not (geometry.fit_to)
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)

    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_face": (0.0, -BLADE_T, blade_c)}}
