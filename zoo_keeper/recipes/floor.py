"""floor module recipe: a flat floor slab built to a Deli Counter floor slot's
exact dims (wide/deep, thin). Same solid-slab construction as the roof/wall
modules (a single center-pivot panel); void_for() returns None for 'floor', so
build_slab emits one solid Floor_Panel. Geometry lives in recipes/_arch.py +
core.arch.
"""
from __future__ import annotations

from ._arch import build_slab


def build(plan, streams, collection):
    return build_slab(plan, streams, collection, "floor")
