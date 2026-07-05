"""window module recipe: center-pivot slab built to a Deli Counter slot's exact
dims. Geometry, void shape and part layout live in recipes/_arch.py + core.arch.
"""
from __future__ import annotations

from ._arch import build_slab


def build(plan, streams, collection):
    return build_slab(plan, streams, collection, "window")
