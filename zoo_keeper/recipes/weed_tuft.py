"""weed_tuft recipe: a small clump of blades — Layer 3 ground cover.

The guide's rule 3 again: growth belongs at cracks, moisture, shade and edges.
A tuft is the marker for that cause, which is why it is a CLUMP rather than a
single blade -- one blade reads as an artifact, a clump reads as something that
grew there.

Height capped at 0.10 m in the genome, under `unassisted_step_max` 0.117 m
(`lot/site_steps.py`), so the whole first kit is unconditionally legal in
traversed space. Real grass is often taller; that is a later band and a later
decision, not a reason to make the first kit untestable.

STILL SOLID, NOT CARDS. Blades are closed prisms rather than crossed quads. A
crossed quad is a single-sided plane, and this pipeline has already spent a
session chasing a white QuadMesh that turned out to be a Lux sign face -- a
layer meant to be instanced in the thousands should not also be the layer that
reintroduces "what is that surface I can only see from one side". An
alpha-cutout card species is the right answer for DENSE foliage and is a
separate species, per "coverage first, alpha cutouts second, and true
transparency only when the material physically calls for it".

SHAPE, SECOND PASS. The first version used `add_cylinder` with three segments
and a near-zero top radius, then leaned each spike by displacing its upper
verts. A cone has no stations along its length, so a lean is all it can do: the
render was five straight tapered slivers fanned out evenly from a base as wide
as the tuft, which reads as paper, not grass. Four changes:

  - `geometry.add_blade` builds each blade with stations along its length, so
    it can CURVE. Real blades leave the ground vertical and bend over.
  - A shared wind direction with per-blade scatter, so the clump agrees with
    itself instead of splaying evenly in every direction -- an even fan is the
    guide's rule 2 stated at the scale of one asset.
  - Blade lengths drawn with a power law, so a few stand tall and most are
    short. A uniform draw gives five blades of nearly equal height, which is
    the single loudest procedural tell in the first render.
  - Blades emerge from a TIGHT base (a tenth of the tuft width, not half), so
    the clump reads as one plant rather than five unrelated spikes.

MATERIAL KIND IS DELIBERATELY UNSKINNED. `vegetation` has no skin pack, so
`make_material` falls back to a flat material carrying the genome colour. That
is intentional: inheriting `concrete` or `wood` would paint a weed with a
building's surface treatment. If a vegetation pack is added later this picks it
up with no change here.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")

    blades = max(2, int(plan["params"].get("blades", 7)))
    thick = float(plan["params"].get("blade_thickness", 0.006))
    # Blade width at the base. A blade is a ribbon, not a needle: the first
    # kit's blades were as thin as they were deep, which is why they read as
    # slivers rather than leaves.
    bwidth = float(plan["params"].get("blade_width", thick * 2.2))
    stations = max(2, int(plan["params"].get("stations", 4)))
    # How tightly the blades share one root, as a fraction of tuft width.
    root = float(plan["params"].get("root_spread", 0.12))
    # How hard the clump leans, as a fraction of blade height, and how far
    # individual blades stray from that direction in radians.
    lean = float(plan["params"].get("lean", 0.34))
    scatter = float(plan["params"].get("lean_scatter", 0.85))

    wind = rng.random() * 6.2831853

    bm = geometry.new_bm()
    for i in range(blades):
        # Power law: most blades short, a few tall. A uniform draw over
        # 0.55..1.0 -- what the first version did -- produces five blades of
        # nearly the same height, and equal heights read as manufactured.
        u = rng.random() ** 1.9
        bh = h * (0.32 + 0.68 * u)
        ang = wind + (rng.random() * 2.0 - 1.0) * scatter
        amt = bh * lean * (0.5 + rng.random())
        bend = (math.cos(ang) * amt, math.sin(ang) * amt)
        rr = root * (rng.random() ** 0.5)
        ra = rng.random() * 6.2831853
        base = (math.cos(ra) * w * rr, math.sin(ra) * d * rr, 0.0)
        taper_i = 1.2 + rng.random() * 0.9
        geometry.add_blade(bm, base, bh,
                           bwidth * (0.7 + rng.random() * 0.6),
                           thick * (0.7 + rng.random() * 0.6),
                           bend=bend, stations=stations, taper=taper_i,
                           curl=rng.random() * 0.6)

    tuft = geometry.bm_to_object(bm, "Dress_WeedTuft", collection,
                                 bevel=bevel, texel=8.0, rng=rng, wear=wear)
    materials.assign([tuft], materials.make_material(
        f"M_Weed_{plan['material']}", plan["color"], plan["material"]))

    return {"objects": [tuft], "collision_boxes": [], "attachments": {}}
