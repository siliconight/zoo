"""ceiling module recipe: a flat ceiling/soffit slab built to a Deli Counter
ceiling slot's exact dims (wide/deep, thin). Same solid-slab construction as the
roof/floor modules; void_for() returns None for 'ceiling', so build_slab emits
one solid Ceiling_Panel. Geometry lives in recipes/_arch.py + core.arch.
"""
from __future__ import annotations

from ._arch import build_slab


def build(plan, streams, collection):
    return build_slab(plan, streams, collection, "ceiling")
