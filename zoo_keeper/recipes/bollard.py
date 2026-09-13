"""bollard recipe: a steel pipe bollard on a base.

Roadmap 153, the forecourt. The walker's Call of Duty frames: red and
white banded bollards at the base of every canopy column and either side
of a door. They are the smallest object that says "vehicles stop here",
and a forecourt without them reads as a car park somebody forgot.

A pipe with a domed cap on a small concrete foot; the bands are geometry
(three rings), so the read survives an unskinned build. Collision is the
pipe. Centre pivot; extents exactly (w, d, h).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

FOOT_H = 0.05
BAND_H = 0.12


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0 = -h / 2.0
    r = min(w, d) / 2.0
    pipe, bands = [], []

    def part(bm, name, into, texel=1.6):
        obj = geometry.bm_to_object(bm, name, collection, bevel=bevel,
                                    texel=texel, rng=rng, wear=wear)
        objs.append(obj)
        into.append(obj)
        return obj

    bm = geometry.new_bm()
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + FOOT_H / 2.0), r, FOOT_H,
                          segments=10)
    pipe_h = h - FOOT_H
    geometry.add_cylinder(bm, (0.0, 0.0, z0 + FOOT_H + pipe_h / 2.0),
                          r * 0.72, pipe_h, segments=10)
    geometry.add_hemisphere(bm, (0.0, 0.0, h / 2.0), r * 0.72, r * 0.72,
                            r * 0.42, segments=10)
    part(bm, "Bollard_Pipe", pipe)

    # the bands: rings a hair proud, so the stripe survives no skin at all
    bm = geometry.new_bm()
    for frac in (0.30, 0.62):
        geometry.add_cylinder(bm, (0.0, 0.0, z0 + FOOT_H + pipe_h * frac),
                              r * 0.76, BAND_H, segments=10)
    part(bm, "Bollard_Bands", bands)

    cboxes.append(((-r, -r, z0), (r, r, h / 2.0)))
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)

    paint = materials.make_material(
        f"M_Bollard_{plan['material']}", plan["color"], plan["material"])
    white = materials.make_material("M_Bollard_band", [0.88, 0.87, 0.84],
                                    "metal_painted")
    materials.assign(pipe, paint)
    materials.assign(bands, white)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_top": (0.0, 0.0, h / 2.0)}}
