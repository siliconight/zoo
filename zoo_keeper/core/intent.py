"""Prompt -> Asset Intent Spec.

Rule-based, fully offline, sensible defaults, no blocking questions for
common requests. Anything the parser can't resolve lands in
Intent.unresolved and downstream falls back to genome defaults.

A SPECIES CAN ALSO BE NAMED OUTRIGHT. `parse(prompt, species="pebble")` skips
keyword matching entirely and takes the species as given, because a prompt is
the right interface for a person and the wrong one for a program.

Two reasons, both measured rather than argued:

  * `wallCorner` and `wallEnd` cannot be requested AT ALL through a prompt.
    `parse("wall corner")` returns species None -- their keyword sets do not
    cover their own names -- and until now a prompt was the only door in. Two
    species have been unreachable for their whole lives.
  * Layer 3 surface dressing (docs/SURFACE_DRESSING.md) needs a placement
    layer to ask for `pebble` several thousand times and get a pebble every
    time. `parse("pebble")` happens to work today; it works because a keyword
    table currently has no better match, which is a coincidence and not a
    contract. Adding a species whose keywords collide would silently change
    what a level is dressed with.

Naming the species does NOT switch the rest of the parser off: material,
colour, wear, size and era are still read from whatever prompt is supplied, so
a caller can say species="pebble", prompt="wet mossy" and get the species it
requires with the styling it wants. With no prompt the species name becomes
the canonical prompt, which keeps `seeding.root_key` stable for repeated
requests of the same species.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


# --- vocab tables ----------------------------------------------------------

import functools

from . import genome as _genome_mod


@functools.lru_cache(maxsize=1)
def _species_keywords():
    """Keywords + match_priority per species, read from the genomes so a
    species is self-describing (Knowledge Pack ready). Cached."""
    out = {}
    for sp in _genome_mod.list_species():
        g = _genome_mod.load_species(sp)
        out[sp] = (list(g.get("keywords", [])), int(g.get("match_priority", 0)))
    return out

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}

# nouns we try to count, mapped to intent param names
COUNT_NOUNS = {
    "drawer": "drawers",
    "stack": "stacks",
    "knob": "knobs",
    "latch": "latches",
    "leg": "legs",
    "wheel": "wheels",
    "door": "doors",
    "strap": "straps",
    "shelf": "shelves",
    "shelves": "shelves",
}

MATERIALS = [
    "laminate", "wood", "wooden", "oak", "pine", "metal", "steel",
    "aluminum", "plastic", "leather", "rubber", "canvas", "carbon",
]
MATERIAL_ALIASES = {
    "wooden": "wood", "oak": "wood", "pine": "wood",
    "steel": "metal", "aluminum": "metal",
}

COLORS = {
    "black": (0.05, 0.05, 0.05), "white": (0.92, 0.92, 0.92),
    "red": (0.62, 0.08, 0.06), "green": (0.10, 0.35, 0.12),
    "blue": (0.08, 0.18, 0.45), "grey": (0.45, 0.45, 0.45),
    "gray": (0.45, 0.45, 0.45), "brown": (0.30, 0.19, 0.10),
    "tan": (0.72, 0.60, 0.42), "beige": (0.80, 0.74, 0.62),
    "yellow": (0.85, 0.72, 0.10), "orange": (0.80, 0.38, 0.06),
    "silver": (0.75, 0.76, 0.78),
}

WEAR_TERMS = {
    "pristine": 0.02, "mint": 0.02, "new": 0.05, "clean": 0.12,
    "used": 0.35, "scuffed": 0.45, "worn": 0.60, "old": 0.60,
    "battered": 0.80, "beat-up": 0.80, "beaten": 0.80,
    "rusty": 0.85, "rusted": 0.85,
}

SIZE_TERMS = {
    "tiny": 0.70, "small": 0.85, "compact": 0.88,
    "large": 1.15, "big": 1.15, "huge": 1.30, "oversized": 1.25,
}

STYLE_TAGS = [
    "office", "executive", "gaming", "school", "military", "combat",
    "hiking", "work", "racing", "construction", "motorcycle", "sports",
    "vintage", "retro", "modern", "industrial", "police",
]

ERA_RE = re.compile(r"\b((?:19|20)\d0)s\b")


# --- intent spec -----------------------------------------------------------

@dataclass
class Intent:
    """Structured Asset Intent Spec parsed from a plain-text prompt."""
    prompt: str
    prompt_norm: str
    species: str | None = None
    # "keyword" when the parser inferred it from the prompt, "explicit" when a
    # caller named it. Recorded because a specimen's provenance should say
    # whether a human's words or a program's argument chose the species.
    species_source: str | None = None
    era: str | None = None                    # e.g. "1990s"
    style_tags: list[str] = field(default_factory=list)
    material: str | None = None
    color: tuple[float, float, float] | None = None
    color_name: str | None = None
    wear: float | None = None                 # 0.0 pristine .. 1.0 destroyed
    size_hint: float = 1.0                    # multiplier on default dims
    counts: dict[str, int] = field(default_factory=dict)
    seed: int = 0
    unresolved: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "prompt": self.prompt,
            "prompt_norm": self.prompt_norm,
            "species": self.species,
            "species_source": self.species_source,
            "era": self.era,
            "style_tags": list(self.style_tags),
            "material": self.material,
            "color": list(self.color) if self.color else None,
            "color_name": self.color_name,
            "wear": self.wear,
            "size_hint": self.size_hint,
            "counts": dict(self.counts),
            "seed": self.seed,
            "unresolved": list(self.unresolved),
        }


def normalize(prompt: str) -> str:
    return re.sub(r"\s+", " ", prompt.strip().lower())


def _find_species(text: str) -> str | None:
    # tie-break: earliest match wins; then the longer (more specific) keyword
    # ("soda machine" beats "soda", "cash machine" beats "cash"); then higher
    # match_priority; then species name for determinism.
    best = None  # (start, -keyword_len, -priority, species)
    for species, (keys, prio) in sorted(_species_keywords().items()):
        for k in keys:
            m = re.search(rf"\b{re.escape(k)}s?\b", text)
            if m:
                cand = (m.start(), -len(k), -prio, species)
                if best is None or cand < best:
                    best = cand
    return best[3] if best else None


def _find_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    num = r"(\d+|" + "|".join(NUMBER_WORDS) + r")"
    for noun, param in COUNT_NOUNS.items():
        m = re.search(rf"\b{num}\s+{noun}s?\b", text)
        if m:
            raw = m.group(1)
            counts[param] = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]
    return counts


def parse(prompt: str, seed: int = 0, species: str | None = None) -> Intent:
    """Parse a plain-text prompt into an Asset Intent Spec.

    Never raises on vague prompts; unknowns fall back to genome defaults
    downstream and are listed in Intent.unresolved.

    `species`, when given, is taken as the answer and keyword matching is
    skipped. An unknown name RAISES -- this is the programmatic door, and a
    caller that asks for a species which does not exist has a bug that should
    surface here rather than as a quietly different asset three stages later.
    """
    prompt = prompt or ""
    if species is not None:
        known = _genome_mod.list_species()
        if species not in known:
            raise ValueError(
                f"No species named {species!r}. Known species: "
                + ", ".join(known))
        # With no prompt the species name IS the prompt, so repeated requests
        # for the same species hash to the same seeding.root_key instead of
        # depending on whatever empty string a caller happened to pass.
        if not prompt.strip():
            prompt = species

    norm = normalize(prompt)
    intent = Intent(prompt=prompt, prompt_norm=norm, seed=seed)

    if species is not None:
        intent.species = species
        intent.species_source = "explicit"
    else:
        intent.species = _find_species(norm)
        intent.species_source = "keyword" if intent.species else None
    if intent.species is None:
        intent.unresolved.append("species")

    m = ERA_RE.search(norm)
    if m:
        intent.era = m.group(1) + "s"

    for tag in STYLE_TAGS:
        if re.search(rf"\b{tag}\b", norm):
            intent.style_tags.append(tag)

    for mat in MATERIALS:
        if re.search(rf"\b{mat}\b", norm):
            intent.material = MATERIAL_ALIASES.get(mat, mat)
            break

    for cname, rgb in COLORS.items():
        if re.search(rf"\b{cname}\b", norm):
            intent.color = rgb
            intent.color_name = cname
            break

    for term, val in WEAR_TERMS.items():
        if re.search(rf"\b{re.escape(term)}\b", norm):
            intent.wear = max(intent.wear or 0.0, val)

    for term, mult in SIZE_TERMS.items():
        if re.search(rf"\b{term}\b", norm):
            intent.size_hint = mult
            break

    intent.counts = _find_counts(norm)
    return intent
