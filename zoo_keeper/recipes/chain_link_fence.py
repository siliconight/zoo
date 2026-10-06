"""chain_link_fence recipe: a run of commercial chain-link fence.

The walker, 2026-10-04: a fence between playable and non-playable ground is
good feedback to the player (`docs/findings/backdrop_mock/`). Where the steel
stands is `core.chain_link_fence_forms`; this file draws it.

TWO SUBMISSIONS, whatever the run's length, because a fence is the sort of
thing a level has a lot of and draw calls are the budget (CLAUDE.md):

  * THE STEEL -- every post, the top rail and the tension wire -- is one
    mesh in `metal_bare`, galvanised grey from the style;
  * THE FABRIC is one card the length of the run, in Pixelcoat's
    `chain_link` kind (0.56.0): an alpha-cut tile, read from both sides
    (`materials._textured` turns back-face culling off for a cutout). On
    the flat path, with no skin library, it is a grey panel -- the greybox
    reading of a fence, which is a wall.

Centre pivot. The extents are exactly (width, depth, height): a terminal
post's outer face is the run's end and its top is the run's top, and depth
is a terminal post's diameter. Collision is that box -- thin, but a body's
radius keeps it off the fabric, and the navmesh is eroded by the same
radius on both sides.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import chain_link_fence_forms as F


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]        # the run's length, local X
    d = plan["dimensions"]["depth"]        # a terminal post's diameter
    h = plan["dimensions"]["height"]
    wear = plan["wear"]
    rng = streams.stream("wear")
    z0 = -h / 2.0
    objs, cboxes = [], []

    steel = geometry.new_bm()
    for x, od in F.posts(w):
        # a terminal stands to the run's top; a line post to the rail's
        # centre, where its loop cap carries the rail
        top = h / 2.0 if od == F.TERMINAL_OD else F.rail_z(h)
        geometry.add_cylinder(steel, (x, 0.0, (z0 + top) / 2.0), od / 2.0,
                              top - z0, segments=F.POST_SIDES)
    span = w - F.TERMINAL_OD                # terminal centre to centre
    geometry.add_cylinder(steel, (0.0, 0.0, F.rail_z(h)), F.RAIL_OD / 2.0,
                          span, segments=F.POST_SIDES, axis="X")
    geometry.add_cylinder(steel, (0.0, F.fabric_y(), F.wire_z(h)),
                          F.WIRE_OD / 2.0, F.wire_length(w),
                          segments=F.WIRE_SIDES, axis="X")
    objs.append(geometry.bm_to_object(
        steel, "ChainLinkFence_Steel", collection, bevel=plan["bevel"],
        texel=1.0, rng=rng, wear=wear))

    fabric = geometry.new_bm()
    fz0, fz1 = F.fabric_z(h)
    geometry.add_box(fabric, (0.0, F.fabric_y(), (fz0 + fz1) / 2.0),
                     (span, F.FABRIC_T, fz1 - fz0))
    # texel 1.0: the pack is a 1 m tile, so a metre of run is a tile
    objs.append(geometry.bm_to_object(
        fabric, "ChainLinkFence_Fabric", collection, bevel=0.0, texel=1.0,
        rng=rng, wear=wear * 0.5, smooth_angle=0.0))

    cboxes.append(((-w / 2.0, -d / 2.0, z0), (w / 2.0, d / 2.0, h / 2.0)))
    cboxes = geometry.fit_to(objs, (w, d, h), cboxes)

    steel_mat = materials.make_material(
        f"M_ChainLinkFence_{plan['material']}", plan["color"], plan["material"])
    fabric_mat = materials.make_material(
        "M_ChainLinkFence_chain_link", plan["color"], "chain_link")
    materials.assign([objs[0]], steel_mat)
    materials.assign([objs[1]], fabric_mat)
    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
