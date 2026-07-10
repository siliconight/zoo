"""Roof props (v0.25): deterministic rooftop scatter planning.

The roofline is where a flat greybox betrays itself against the sky, and
breaking it up is pure prop work — HVAC units, water tanks, vent stacks,
exhaust fans, skylights, dishes. This module is the **pure planning half**:
it reads a DC ``slots.json``, finds the ``roof`` slots, and lays out a
deterministic, non-overlapping scatter of species placements on each roof
plane. ``bpylayer.build.build_roof_props`` executes the plan with the real
recipes; nothing here needs Blender, so the layout logic is fully testable.

Density scales with roof area; every placement respects an edge margin and
an inter-prop clearance (rejection-sampled on seeded streams, so the same
manifest + seed always yields the same roofscape). Positions are emitted in
the manifest's own spec / Blender Z-up space, sitting on the roof slot's top
surface — the builder only has to lift each prop by half its own height.
"""

from __future__ import annotations

import math

from . import genome as genome_mod
from . import seeding

# Species scatter rules: (min area to appear, count formula cap, edge bias).
# Counts scale with roof area (m^2); water tanks and dishes hug edges/corners
# the way real installs do; skylights stay clear of the perimeter.
_EDGE, _CENTER, _ANY = "edge", "center", "any"
_RULES = (
    # species, min_area, base, per_m2, cap, bias
    ("water_tank",     50.0, 1, 0.0,       1, _EDGE),
    ("hvac_unit",      12.0, 1, 1 / 45.0,  4, _ANY),
    ("vent_stack",      6.0, 2, 1 / 50.0,  6, _ANY),
    ("exhaust_fan",     8.0, 1, 1 / 70.0,  3, _ANY),
    ("skylight",       40.0, 0, 1 / 55.0,  2, _CENTER),
    ("satellite_dish", 10.0, 0, 1 / 90.0,  2, _EDGE),
)
_CLEARANCE = 0.35     # metres between prop AABBs
_ATTEMPTS = 24        # rejection-sampling tries per prop


def roof_slots(manifest: dict) -> list[dict]:
    """Roof-role slots with dims, as plain dicts."""
    out = []
    for s in manifest.get("slots", []):
        if s.get("role") != "roof":
            continue
        fit = s.get("fit", {})
        dims = fit.get("dims")
        if not dims:
            continue
        t = s.get("transform", {})
        out.append({
            "slot_id": s["slot_id"],
            "translation": [float(v) for v in t.get("translation", (0, 0, 0))],
            "rot_y": float(t.get("rot_y", 0.0)),
            "dims": [float(v) for v in dims],
            "pivot": fit.get("pivot", "center"),
        })
    return out


def _footprint(species: str) -> tuple[float, float, float]:
    """(width, depth, height) defaults from the species genome."""
    g = genome_mod.load_species(species)
    d = g["dimensions"]
    return (d["width"]["default"], d["depth"]["default"],
            d["height"]["default"])


def scatter(manifest: dict, seed: int, *, density: float = 1.0,
            margin: float = 0.6, species: tuple = None) -> dict:
    """A roof-prop plan for every roof slot in the manifest.

    Returns ``{"building_id", "seed", "space", "placements", "counts"}``.
    Each placement: species, slot_id, ``pos`` on the roof's top surface
    (spec space), ``rot_z`` degrees, ``footprint`` [w, d], ``seed_offset``.
    """
    building = manifest.get("building_id", "building")
    allowed = set(species) if species else {r[0] for r in _RULES}
    placements: list[dict] = []
    counts: dict[str, int] = {}

    for slot in roof_slots(manifest):
        w, d, h = slot["dims"]
        area = w * d
        tz_top = (slot["translation"][2] + (h / 2.0 if slot["pivot"] == "center"
                                            else h))
        rad = math.radians(slot["rot_y"])
        cos_r, sin_r = math.cos(rad), math.sin(rad)
        taken: list[tuple[float, float, float, float]] = []  # local AABBs

        for name, min_area, base, per_m2, cap, bias in _RULES:
            if name not in allowed or area < min_area:
                continue
            want = min(cap, int(round((base + area * per_m2) * density)))
            fw, fd, fh = _footprint(name)
            half_w = w / 2.0 - margin - fw / 2.0
            half_d = d / 2.0 - margin - fd / 2.0
            if want < 1 or half_w <= 0 or half_d <= 0:
                continue
            rng = seeding.RNGStreams(seeding.root_key(
                building, name, seed, slot["slot_id"])).stream("scatter")
            for k in range(want):
                placed = False
                for _ in range(_ATTEMPTS):
                    if bias == _EDGE:
                        lx = rng.choice([-1.0, 1.0]) * rng.uniform(
                            half_w * 0.6, half_w)
                        ly = rng.uniform(-half_d, half_d)
                    elif bias == _CENTER:
                        lx = rng.uniform(-half_w * 0.5, half_w * 0.5)
                        ly = rng.uniform(-half_d * 0.5, half_d * 0.5)
                    else:
                        lx = rng.uniform(-half_w, half_w)
                        ly = rng.uniform(-half_d, half_d)
                    box = (lx - fw / 2 - _CLEARANCE, ly - fd / 2 - _CLEARANCE,
                           lx + fw / 2 + _CLEARANCE, ly + fd / 2 + _CLEARANCE)
                    if any(not (box[2] < t[0] or box[0] > t[2]
                                or box[3] < t[1] or box[1] > t[3])
                           for t in taken):
                        continue
                    taken.append(box)
                    px = slot["translation"][0] + lx * cos_r - ly * sin_r
                    py = slot["translation"][1] + lx * sin_r + ly * cos_r
                    rot_z = (slot["rot_y"] +
                             (rng.choice([0.0, 90.0]) if name in
                              ("hvac_unit", "skylight")
                              else rng.uniform(0.0, 360.0)))
                    placements.append({
                        "species": name,
                        "slot_id": slot["slot_id"],
                        "pos": [round(px, 3), round(py, 3), round(tz_top, 3)],
                        "rot_z": round(rot_z % 360.0, 1),
                        "footprint": [fw, fd],
                        "seed_offset": rng.randrange(1_000_000),
                    })
                    counts[name] = counts.get(name, 0) + 1
                    placed = True
                    break
                if not placed:
                    break   # roof is full for this species

    return {"building_id": building, "seed": seed,
            "space": manifest.get("space", ""),
            "placements": placements, "counts": dict(sorted(counts.items()))}
