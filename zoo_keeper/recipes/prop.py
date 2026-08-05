"""prop module recipe: a solid center-pivot box built to a Deli Counter
VOLUME's exact dims -- a vault, a teller counter, a desk, a cabinet, a crate
stack.

Why this exists at all. Deli Counter draws these as boxes and, until now, never
recorded them as slots, so the art pass could not see them: measured on
art_probe_001 seed 5017, eleven prop meshes rendered as untextured white boxes
in a scene where every wall, floor, ceiling and opening themed correctly. Once
the slots were emitted, `kit.plan_kit` reported the gap precisely -- seven
distinct modules, "no 'prop' species in the genome library". This is that
species.

It is deliberately the PLAIN slab. A prop's silhouette is authored upstream (DC
picked the box), its material is declared upstream (metal for the vault, wood
for the counter), and its interest should come from the skin rather than from
geometry Zoo invents -- the same conclusion the wall relief work reached from
the other direction. A vault that reads as a vault rather than a white cube is
the whole win here; shaping it into a believable vault DOOR is a later, richer
species, not a reason to leave it white.

Geometry and part layout live in recipes/_arch.py + core.arch, as for every
architectural module. `prop` is in `arch._SOLID`, so it never grows an opening.
"""
from __future__ import annotations

from ._arch import build_slab


def build(plan, streams, collection):
    return build_slab(plan, streams, collection, "prop")
