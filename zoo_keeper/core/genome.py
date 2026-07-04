"""Genome: per-species construction knowledge stored as JSON.

CC0-derived construction knowledge only. No copyrighted source meshes,
no scraped data. License metadata rides along in every genome file and is
copied into every specimen's meta.json sidecar.
"""
from __future__ import annotations

import json
import os

REQUIRED_KEYS = ["species", "version", "license", "dimensions", "parts",
                 "params", "materials", "styles", "budgets"]

_DEFAULT_DIR = os.path.join(os.path.dirname(__file__), "..", "genome",
                            "species")


def genome_dir() -> str:
    return os.path.normpath(_DEFAULT_DIR)


def list_species(directory: str | None = None) -> list[str]:
    d = directory or genome_dir()
    return sorted(
        f[:-5] for f in os.listdir(d)
        if f.endswith(".json") and not f.startswith("_")
    )


def load_species(species: str, directory: str | None = None) -> dict:
    d = directory or genome_dir()
    path = os.path.join(d, f"{species}.json")
    if not os.path.isfile(path):
        known = ", ".join(list_species(d)) or "(none)"
        raise FileNotFoundError(
            f"No genome for species '{species}'. Known species: {known}")
    with open(path, "r", encoding="utf-8") as fh:
        g = json.load(fh)
    problems = validate_genome(g)
    if problems:
        raise ValueError(f"Genome '{species}' invalid: " + "; ".join(problems))
    return g


def validate_genome(g: dict) -> list[str]:
    problems = []
    for k in REQUIRED_KEYS:
        if k not in g:
            problems.append(f"missing key '{k}'")
    dims = g.get("dimensions", {})
    for name, spec in dims.items():
        for k in ("min", "max", "default"):
            if k not in spec:
                problems.append(f"dimension '{name}' missing '{k}'")
                break
        else:
            if not (spec["min"] <= spec["default"] <= spec["max"]):
                problems.append(f"dimension '{name}' default outside range")
    lic = g.get("license", {})
    if lic and "construction_knowledge" not in lic:
        problems.append("license missing 'construction_knowledge'")
    return problems
