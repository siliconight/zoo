"""dome_fixture recipe: the flush-mount dome a 1990s home hangs from the middle of a room.

Roadmap 229's species step (1.98.0). Deli Counter lays a home's rooms with its
own row rule, a fixture a bay (0.207.1), and until now each was a 2 x 4
office troffer -- a fluorescent in a bedroom. A home's room takes a `dome`
anchor now, and this is its hardware: a round canopy against the ceiling and
a frosted glass bowl under it, with a small finial at the bottom of the bowl
where the screw holds the glass.

WHAT IS BUILT, in the module frame (Z up, metres, centre pivot): the body
spans -h/2 .. +h/2. Zoo's fixture table mounts the species 'hang' -- its TOP
at the emitter, the body below -- and Deli Counter writes a home's anchor at
the ceiling plane, so the canopy's top lands on the ceiling.

  * THE CANOPY: a short drum, `CANOPY_H` deep, a hand wider than the glass
    (`CANOPY_LIP`), so the glass meets its underside inside its rim.
  * THE GLASS: the lower half of an ellipsoid, as wide as the species and as
    deep as the rest of the height, its rim on the canopy's underside. Built
    as Zoo's upper hemisphere mirrored downward with its faces turned back
    outward, so the open rim is closed by the canopy and no face of the glass
    lies on the canopy's plane.
  * THE FINIAL: a small knob at the bowl's lowest point, sunk into the glass
    by half its depth (`FINIAL_SINK`) so no face of it lies on the glass.

The glass carries the `M_*_Lens` name Lux's emissive binder keys on, as the
pendant's bulb and the troffer's diffuser do. Lux hangs the lamp under the
glass, not inside it (its `DOME_LAMP_DROP_M`, derived from this genome's
deepest bowl): a lamp inside a closed shell bakes to nothing.

No collision: overhead, above the walk plane by construction.
"""
from __future__ import annotations

import bmesh

from ..bpylayer import geometry, materials

#: The canopy drum's depth, metres: a pressed-steel pan.
CANOPY_H = 0.022
#: How much wider than the glass the canopy is, on the radius.
CANOPY_LIP = 0.012
#: The finial: radius and depth; it sinks into the glass by this share of its depth.
FINIAL_R = 0.012
FINIAL_H = 0.02
FINIAL_SINK = 0.5


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]       # the glass's diameter
    h = plan["dimensions"]["height"]      # canopy + glass, total
    bevel, wear = plan["bevel"], plan["wear"]
    style = plan.get("style_block", {})
    rng = streams.stream("wear")
    top = h / 2.0
    r = w / 2.0
    objs = []

    # Canopy: a short drum whose top is the body's top.
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, top - CANOPY_H / 2.0), r + CANOPY_LIP,
                          CANOPY_H, segments=20)
    canopy = geometry.bm_to_object(
        bm, "Dome_Canopy", collection, bevel=bevel, texel=1.5,
        rng=rng, wear=wear)
    objs.append(canopy)

    # Glass: the lower half of an ellipsoid hanging from the canopy's
    # underside -- the upper hemisphere helper, mirrored and turned outward.
    rim_z = top - CANOPY_H
    # the finial's exposed half is inside the height, so the body ends at -h/2
    depth = max(h - CANOPY_H - FINIAL_H * (1.0 - FINIAL_SINK), 0.02)
    bm = geometry.new_bm()
    verts = geometry.add_hemisphere(bm, (0.0, 0.0, 0.0), r, r, depth, segments=20)
    for v in verts:
        v.co.z = rim_z - v.co.z
    bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    glass = geometry.bm_to_object(
        bm, "Dome_Glass", collection, bevel=0.0, texel=1.0,
        rng=rng, wear=0.0)
    objs.append(glass)

    # Finial: a small knob at the bowl's lowest point, half sunk into it.
    bottom = rim_z - depth
    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, bottom - FINIAL_H * (0.5 - FINIAL_SINK)),
                          FINIAL_R, FINIAL_H, segments=8)
    finial = geometry.bm_to_object(
        bm, "Dome_Finial", collection, bevel=0.0, texel=1.5,
        rng=rng, wear=wear * 0.5)
    objs.append(finial)

    mat = materials.make_material(
        f"M_Dome_{plan['material']}", plan["color"], plan["material"])
    materials.assign([canopy, finial], mat)
    lit = materials.make_emissive_material(
        "M_Dome_Lens",
        style.get("emissive_color", [1.0, 0.86, 0.66]),
        style.get("emissive_strength", 1.8))
    materials.assign([glass], lit)

    return {"objects": objs, "collision_boxes": [], "attachments": {}}
