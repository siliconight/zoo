"""roof module recipe: a flat capping slab built to a Deli Counter roof slot's
exact dims (wide/deep, thin). Same slab construction as the wall module, just
fed the roof slot's horizontal-cap dimensions. Geometry lives in
recipes/_arch.py + core.arch.
"""
from __future__ import annotations

from ._arch import build_slab


def build(plan, streams, collection):
    return build_slab(plan, streams, collection, "roof")
