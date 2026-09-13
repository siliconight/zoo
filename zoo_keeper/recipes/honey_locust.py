"""honey_locust recipe: Gleditsia triacanthos inermis.

One of the five street trees (roadmap 153). Every tree is grown by the same
builder -- trunk, leader, branches at the species' angles, twigs, faceted
leaf clusters -- and the SPECIES is which row of `core.tree_forms` the
genome names in ``params.form``. This module exists because Zoo resolves a
recipe by species name; the shape lives in `street_tree.py` and the
proportions in `core/tree_forms.py`.
"""
from __future__ import annotations

from .street_tree import build  # noqa: F401
