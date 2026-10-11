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

WHAT A PROP KEEPS OFF (1.101.0, roadmap 181). The roof slot carries the
slab's holes (``fit.voids``: stair heads and ladder hatches, in the plate's
own centred coords) and the landings Deli Counter 0.209.0 writes for the
ladders that top out on it (``fit.keep_out``, the same frame). A prop never
stands on a hole, and keeps ``VOID_CLEAR`` from its edge -- the stride a
body takes climbing out -- nor on a landing. A YAWED PROP IS TESTED AS THE
BOX IT OCCUPIES: the yaw is drawn before the position, and the footprint's
extents at that yaw decide both the edge clamp and the overlap. 0.25 read
the unrotated box for both; the 0.35 m clearance happened to absorb the
overlap for every current species, but a 90-degree HVAC (1.8 x 1.1) at a
long edge reached 0.25 m from the footprint's edge, inside a 0.35 m
parapet, and a 1.6 m tank yawed 149 degrees stood 9 cm past the margin. A
WATER TANK NEEDS HEIGHT: a gravity tank serves floors below it and a
one-storey roof is on street pressure, so one is planned only on a roof
``TANK_MIN_ROOF_M`` or more above the plan.

WHAT A ROOF CARRIES FOLLOWS THE BUILDING (1.102.0). The walker, on cold run
9245's roofs -- every one carrying the same 17 props, because the area
formula saturated every cap on any roof over about 300 m2 -- chose "by
building, fewer": a deli or a shop gets a unit or two, a vent and a fan,
warehouses and markets get more and the skylights, seeded so no two roofs
match. `ROOF_PROFILES` reads the building's use off its id's words (first
row whose word is a TOKEN of the id wins -- `barber` is not `bar`), and
`PROFILE_COUNTS` draws each species' count per roof inside its range. The
water tank keeps its formula and its height rule, which the walker kept.
"""

from __future__ import annotations

import math
import re

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

#: A building's use, read off its id's words (1.102.0): the first row with a
#: word that is a TOKEN of the id wins, so the specific stands before the
#: general and `barber` never reads as `bar`; a name no row claims is a shop.
#: Checked against every id in Deli Counter's library on 2026-10-11: 12
#: kitchens, 35 shops, 28 offices, 43 big boxes, 21 homes, 6 with nothing.
ROOF_PROFILES = (
    # a parking deck is parked on, and a construction site is not finished
    (("parking", "construction"), "none"),
    (("warehouse", "market", "supermarket", "depot", "freight", "factory",
      "foundry", "storage", "terminal", "yard", "brewery", "arena",
      "stadium", "airport", "rail", "hall"), "big_box"),
    (("deli", "diner", "pizza", "restaurant", "tavern", "bar", "club",
      "cafe"), "kitchen"),
    (("office", "bank", "credit", "courthouse", "clinic", "hospital",
      "museum", "police", "funeral", "casino", "hotel", "school"), "office"),
    (("rowhouse", "rowhome", "twin", "apartment", "walkup", "home",
      "house", "mansion"), "home"),
)
DEFAULT_PROFILE = "shop"

#: Per profile, each species' count is drawn per roof in [lo, hi] -- seeded
#: by the building, so no two roofs match -- then placed as before; a species
#: the roof is too small for is still skipped. A kitchen's fan is its hood's.
#: About a third of 1.101.0's 17 on a small commercial roof.
PROFILE_COUNTS = {
    "kitchen": {"hvac_unit": (1, 2), "vent_stack": (1, 1),
                "exhaust_fan": (1, 2), "satellite_dish": (0, 1)},
    "shop":    {"hvac_unit": (1, 2), "vent_stack": (1, 1),
                "exhaust_fan": (0, 1), "satellite_dish": (0, 1)},
    "office":  {"hvac_unit": (2, 3), "vent_stack": (1, 2),
                "exhaust_fan": (0, 1), "satellite_dish": (0, 1)},
    "big_box": {"hvac_unit": (2, 4), "vent_stack": (2, 4),
                "exhaust_fan": (1, 2), "skylight": (2, 4),
                "satellite_dish": (0, 1)},
    "home":    {"vent_stack": (1, 2), "satellite_dish": (0, 1)},
    "none":    {},
}


def profile_of(building_id) -> str:
    """The roof profile of a building, by its id's words (`ROOF_PROFILES`)."""
    tokens = {t for t in re.split(r"[^a-z]+", str(building_id or "").lower()) if t}
    for words, profile in ROOF_PROFILES:
        if tokens & set(words):
            return profile
    return DEFAULT_PROFILE


#: A hole's edge is where a body climbs out; this is the stride it takes
#: (1.101.0), grown around every void of the roof slot.
VOID_CLEAR = 1.0
#: A gravity tank serves floors below it; a roof whose top is lower than this
#: is on street pressure and plans none (1.101.0). Delco's library stands 3.2
#: to 13 m above its plan; two roofs of 133 reach 12.
TANK_MIN_ROOF_M = 12.0


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
            # the plate's holes and its landings, in its own centred coords
            "voids": [dict(v) for v in (fit.get("voids") or ())],
            "keep_out": [dict(k) for k in (fit.get("keep_out") or ())],
        })
    return out


def _footprint(species: str) -> tuple[float, float, float]:
    """(width, depth, height) defaults from the species genome."""
    g = genome_mod.load_species(species)
    d = g["dimensions"]
    return (d["width"]["default"], d["depth"]["default"],
            d["height"]["default"])


def _extents(fw: float, fd: float, yaw_deg: float) -> tuple[float, float]:
    """Half-extents along the slot's x and y of a ``fw x fd`` footprint yawed
    by ``yaw_deg`` -- the box the prop actually occupies (1.101.0)."""
    c = abs(math.cos(math.radians(yaw_deg)))
    s = abs(math.sin(math.radians(yaw_deg)))
    return (fw / 2.0 * c + fd / 2.0 * s, fw / 2.0 * s + fd / 2.0 * c)


def forbidden_rects(slot: dict, clear: float = VOID_CLEAR) -> list[tuple]:
    """Where no prop may stand on ``slot``, as (x0, y0, x1, y1) in its own
    centred coords: every void grown by ``clear``, every keep_out as given."""
    out = []
    for v in slot.get("voids", ()):
        out.append((float(v["x0"]) - clear, float(v["y0"]) - clear,
                    float(v["x1"]) + clear, float(v["y1"]) + clear))
    for k in slot.get("keep_out", ()):
        out.append((float(k["x0"]), float(k["y0"]),
                    float(k["x1"]), float(k["y1"])))
    return out


def _overlaps(box, rects) -> bool:
    return any(not (box[2] < r[0] or box[0] > r[2]
                    or box[3] < r[1] or box[1] > r[3]) for r in rects)


def scatter(manifest: dict, seed: int, *, density: float = 1.0,
            margin: float = 0.6, species: tuple = None) -> dict:
    """A roof-prop plan for every roof slot in the manifest.

    Returns ``{"building_id", "seed", "space", "placements", "counts"}``.
    Each placement: species, slot_id, ``pos`` on the roof's top surface
    (spec space), ``rot_z`` degrees, ``footprint`` [w, d], ``local`` [lx, ly]
    and ``extents`` [ex, ey] -- the box it occupies in the slot's own centred
    coords (1.101.0) -- and ``seed_offset``. ``forbidden`` counts the rects
    each roof kept its props off; ``profile`` is the building's
    (`profile_of`, 1.102.0), which decides each species' count.
    """
    building = manifest.get("building_id", "building")
    allowed = set(species) if species else {r[0] for r in _RULES}
    profile = profile_of(building)
    ranges = PROFILE_COUNTS[profile]
    placements: list[dict] = []
    counts: dict[str, int] = {}
    forbidden_by_slot: dict[str, int] = {}

    for slot in roof_slots(manifest):
        w, d, h = slot["dims"]
        area = w * d
        tz_top = (slot["translation"][2] + (h / 2.0 if slot["pivot"] == "center"
                                            else h))
        rad = math.radians(slot["rot_y"])
        cos_r, sin_r = math.cos(rad), math.sin(rad)
        taken: list[tuple[float, float, float, float]] = []  # local AABBs
        # the holes (grown by the stride out of them) and the landings
        forbidden = forbidden_rects(slot)
        forbidden_by_slot[slot["slot_id"]] = len(forbidden)

        for name, min_area, base, per_m2, cap, bias in _RULES:
            if name not in allowed or area < min_area:
                continue
            if name == "water_tank" and tz_top < TANK_MIN_ROOF_M:
                continue   # a low roof is on street pressure
            if profile == "none":
                continue   # a deck or a site: nothing stands on it
            if name == "water_tank":
                # the tank keeps its formula and its height rule above
                want = min(cap, int(round((base + area * per_m2) * density)))
            else:
                lo, hi = ranges.get(name, (0, 0))
                if hi < 1:
                    continue
                count_rng = seeding.RNGStreams(seeding.root_key(
                    building, name, seed, slot["slot_id"])).stream("count")
                want = int(round(count_rng.randint(lo, hi) * density))
            fw, fd, fh = _footprint(name)
            if want < 1:
                continue
            rng = seeding.RNGStreams(seeding.root_key(
                building, name, seed, slot["slot_id"])).stream("scatter")
            for k in range(want):
                placed = False
                for _ in range(_ATTEMPTS):
                    # THE YAW FIRST (1.101.0), so the box it is tested in is
                    # the box it occupies: the clamp and the overlap read the
                    # footprint's extents at this yaw, not the unrotated
                    # fw x fd. Units and skylights sit square to the roof.
                    yaw = (rng.choice([0.0, 90.0]) if name in
                           ("hvac_unit", "skylight")
                           else rng.uniform(0.0, 360.0))
                    ex, ey = _extents(fw, fd, yaw)
                    half_w = w / 2.0 - margin - ex
                    half_d = d / 2.0 - margin - ey
                    if half_w <= 0 or half_d <= 0:
                        continue   # does not fit at this yaw
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
                    box = (lx - ex - _CLEARANCE, ly - ey - _CLEARANCE,
                           lx + ex + _CLEARANCE, ly + ey + _CLEARANCE)
                    if _overlaps(box, taken):
                        continue
                    # a hole or a landing: the clearance there is the ring's
                    if _overlaps((lx - ex, ly - ey, lx + ex, ly + ey), forbidden):
                        continue
                    taken.append(box)
                    px = slot["translation"][0] + lx * cos_r - ly * sin_r
                    py = slot["translation"][1] + lx * sin_r + ly * cos_r
                    rot_z = slot["rot_y"] + yaw
                    placements.append({
                        "species": name,
                        "slot_id": slot["slot_id"],
                        "pos": [round(px, 3), round(py, 3), round(tz_top, 3)],
                        "rot_z": round(rot_z % 360.0, 1),
                        "footprint": [fw, fd],
                        # the box it occupies, in the slot's own centred coords
                        "local": [round(lx, 3), round(ly, 3)],
                        "extents": [round(ex, 3), round(ey, 3)],
                        "seed_offset": rng.randrange(1_000_000),
                    })
                    counts[name] = counts.get(name, 0) + 1
                    placed = True
                    break
                if not placed:
                    break   # roof is full for this species

    return {"building_id": building, "seed": seed,
            "space": manifest.get("space", ""),
            "placements": placements, "counts": dict(sorted(counts.items())),
            # how many rects each roof kept its props off (1.101.0)
            "forbidden": forbidden_by_slot,
            # what the building is, which decided the counts (1.102.0)
            "profile": profile}
