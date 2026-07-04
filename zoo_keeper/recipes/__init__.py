"""DNA recipe registry: species name -> build(plan, streams, collection).

Recipes auto-discover by filename: a species named ``fryer`` is served by
``recipes/fryer.py`` exposing ``build(...)``. Dropping in a new recipe module
(e.g. from a Knowledge Pack) needs no edit here.
"""
from __future__ import annotations

import importlib


def get(species):
    try:
        mod = importlib.import_module(f".{species}", __name__)
    except ImportError as exc:
        raise KeyError(f"No recipe for species '{species}'") from exc
    return mod.build
