"""Deterministic variant families.

A *family* is one prompt built across a contiguous block of seeds. Style,
material and colour are resolved from the prompt and are seed-independent, so
the whole family shares a look while dimensions and wear vary per specimen.

Variant i is exactly a normal single build at seed = base_seed + i, so any
specimen in a family is reproducible on its own with --seed. On top of the
per-specimen meta.json files, a family writes one `<family_id>.family.json`
index listing every sibling — handy for batch import later.

Pure Python: no bpy, fully deterministic, unit-testable.
"""
from __future__ import annotations

from . import seeding


def variant_seeds(base_seed: int, count: int) -> list[int]:
    """The seed block for a family: [base, base+1, ..., base+count-1]."""
    if count < 1:
        raise ValueError("count must be >= 1")
    return [base_seed + i for i in range(count)]


def family_id(prompt_norm: str, species: str, base_seed: int, count: int,
              version: str) -> str:
    """Stable id for a family — same inputs give the same id."""
    key = f"{prompt_norm}|{species}|family|{base_seed}|{count}|{version}"
    return f"{species}_family_{seeding.short_hash(key)}"


def build_family_manifest(tool_version: str, fid: str, prompt: str,
                          species: str, base_seed: int, count: int,
                          shared: dict, specimens: list[dict]) -> dict:
    """Index of a family. Timestamp-free — same inputs give byte-identical
    JSON when written with sort_keys (see meta.write_meta)."""
    return {
        "zoo": {"tool_version": tool_version, "family_id": fid},
        "prompt": prompt,
        "species": species,
        "base_seed": base_seed,
        "count": count,
        "shared": shared,          # style / material / colour common to all
        "specimens": specimens,    # per-sibling: seed, id, dimensions, files
    }
