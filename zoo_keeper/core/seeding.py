"""Deterministic seeding for Zoo.

Same (normalized prompt, species, user seed, tool version) -> byte-identical
asset. Every subsystem draws from its own named RNG stream so adding a new
subsystem never disturbs the randomness of existing ones.
"""
from __future__ import annotations

import hashlib
import random


def _digest_int(*parts: str) -> int:
    data = "|".join(parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")


def root_key(prompt_norm: str, species: str, seed: int, version: str) -> str:
    """Canonical root key string for a specimen."""
    return f"{prompt_norm}|{species}|{seed}|{version}"


def short_hash(root: str, n: int = 6) -> str:
    """Short stable hex tag used in specimen ids and filenames."""
    return hashlib.sha256(root.encode("utf-8")).hexdigest()[:n]


class RNGStreams:
    """Named, independent, deterministic RNG streams from one root key.

    streams = RNGStreams(root_key(...))
    streams.stream("dims").uniform(0.0, 1.0)
    """

    def __init__(self, root: str):
        self.root = root
        self._streams: dict[str, random.Random] = {}

    def stream(self, name: str) -> random.Random:
        rng = self._streams.get(name)
        if rng is None:
            rng = random.Random(_digest_int(self.root, name))
            self._streams[name] = rng
        return rng

    def uniform(self, name: str, lo: float, hi: float) -> float:
        return self.stream(name).uniform(lo, hi)

    def choice(self, name: str, seq):
        return self.stream(name).choice(seq)
