"""Habitats: themed sets of different species that share a look.

A variant *family* is one species across many seeds. A *habitat* is many
species under one theme string — "1990s office" -> desk + chair that read as
the same place. Cohesion is free: the theme (era, palette, material, style
tags) is prepended to each species' prompt, so every member parses the same
descriptors through the normal pipeline. No shared-state plumbing.

Pure Python, deterministic, unit-testable.
"""
from __future__ import annotations

from . import seeding

# Named species sets. "starter" is the full MVP Starter Habitat.
HABITATS = {
    "starter": ["desk", "chair", "helmet", "boots", "simple_car",
                "filing_cabinet"],
    "office": ["desk", "chair", "filing_cabinet"],
    "gear": ["helmet", "boots"],
    "corner_store": ["vending_machine", "atm", "table", "crt_tv"],
    "score": ["briefcase", "cash_stack", "atm"],
    "diner": ["table", "chair", "cheesesteak", "soda_cup"],
}


def _norm(text: str) -> str:
    return " ".join((text or "").lower().split())


def resolve_species(habitat: str, known_species) -> list[str]:
    """habitat -> ordered species list. Accepts a named set (starter/office/
    gear) or a comma-separated list (desk,chair). Validated against
    known_species."""
    name = _norm(habitat).replace(" ", "_")
    if name in HABITATS:
        species = list(HABITATS[name])
    else:
        species = [s.strip().lower() for s in habitat.split(",") if s.strip()]
    if not species:
        raise ValueError(f"no species resolved from habitat '{habitat}'")
    known = set(known_species)
    unknown = [s for s in species if s not in known]
    if unknown:
        raise ValueError(
            f"unknown species {unknown}; known: {sorted(known)}, "
            f"or a named habitat: {sorted(HABITATS)}")
    return species


def species_prompt(theme: str, species: str) -> str:
    """Per-species prompt = theme descriptors + the species noun."""
    noun = species.replace("_", " ")
    return f"{(theme or '').strip()} {noun}".strip()


def habitat_id(theme: str, species: list[str], seed: int, version: str) -> str:
    """Stable id — same theme + species set + seed + version give the same
    id."""
    key = f"{_norm(theme)}|habitat|{','.join(species)}|{seed}|{version}"
    return "habitat_" + seeding.short_hash(key)


def build_habitat_manifest(tool_version: str, hid: str, theme: str,
                           species: list[str], seed: int,
                           members: list[dict]) -> dict:
    """Index of a habitat. Timestamp-free / deterministic (see
    meta.write_meta)."""
    return {
        "zoo": {"tool_version": tool_version, "habitat_id": hid},
        "theme": theme,
        "seed": seed,
        "species": list(species),
        "members": members,   # per species: species, specimen_id, status, files
    }
