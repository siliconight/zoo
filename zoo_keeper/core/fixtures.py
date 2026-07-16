"""Light fixtures (v0.28): physical hardware for the light-anchor pipeline.

Light in DELCO comes from the sun or from physical fixtures — never from
nowhere. Deli Counter derives WHERE lights belong (``<building>.lights.json``),
Lot merges every building plus its own exterior streetlights into one site
manifest, and Lux spawns the actual Light3D rigs at each anchor. This module
is the missing leg: it turns the SAME manifest into fixture *placements* —
the visible hardware (troffer housings, streetlight poles) the light appears
to come from — so the GLB Zoo bakes agrees exactly with the lamps Lux spawns.

Pure planning half (no bpy); ``bpylayer.build.build_fixtures`` executes the
plan with the real recipes. The placement math mirrors Lux's rigs on purpose:

* anchor ``pos`` is the EMITTER point (Blender Z-up, meters); ``rot_y`` is
  degrees about up with 0 == +X (Deli Counter's convention).
* a ``row`` {count, spacing} expands CENTERED on pos along the rot_y
  direction — the same ``start = -(count-1)/2 * spacing`` as
  LuxFluorescentRig — so every housing sits exactly under/over its lamp.
* per fixture kind the hardware hangs above or below the emitter:
  ``fluorescent`` mounts ABOVE (the housing fills DC's 0.1 m ceiling gap,
  diffuser face at pos); ``streetlight`` mounts BELOW (pole top at pos,
  dropping to grade at z=0 — Lot writes pole-top anchors at z=6).

``window`` anchors are daylight through glass — no hardware to build.
``sun`` belongs to the preset / SkyMint. Unknown types are reported in the
plan's ``skipped`` list, never guessed at.
"""
from __future__ import annotations

import math
import zlib

# anchor type -> which species builds its hardware and how it hangs off the
# emitter point: 'above' (body above the emitter — troffers, wall packs),
# 'below' (body below — poles), 'center' (emitter IS the body's centre —
# sign faces). Extending the pipeline is one row here + one genome + one
# recipe.
FIXTURES = {
    "fluorescent": {"species": "fluorescent_fixture", "mount": "above"},
    "streetlight": {"species": "streetlight", "mount": "below"},
    # v0.29 facade hardware (DC lights.json 1.1). Both anchors sit PROUD of
    # the wall: the sign's pos is its FACE plane (cabinet hangs behind,
    # toward the wall at -X local); the wall pack's pos is in free air
    # under the wedge (body above, arm back to the wall at -X local).
    # rot_y on both is the wall's OUTWARD facing, so local +X points away
    # from the building.
    "sign": {"species": "sign_box", "mount": "center"},
    "wall_pack": {"species": "wall_pack", "mount": "above"},
}

# anchor types that are light without hardware, by design.
DAYLIGHT = {"window", "sun"}

# Emitter marker contract (v0.30): every placement's EMITTER point (the
# anchor pos itself, before any mount lift) is exported into the fixtures
# GLB as an empty named ``LuxEmit_<type>`` carrying the placement payload
# as glTF extras (lux_type / lux_anchor_id / lux_slot / lux_reacts_to_alarm),
# which Godot imports as node metadata. Lux v0.15's LuxFixtureSpawner walks
# any scene for these markers and puts the matching lamp at each one — so a
# fixture GLB dragged ANYWHERE (Level Factory or by hand) lights itself,
# with no manifest in sight. Row expansion happened here, once; markers are
# per-lamp. Blender dedupes repeat names (.001, .002...); Godot's importer
# swaps the dot for an underscore — consumers match by PREFIX, and read the
# type from metadata first, name second.
MARKER_PREFIX = "LuxEmit"


def marker_name(placement: dict) -> str:
    """The contract name for a placement's emitter marker empty."""
    return "%s_%s" % (MARKER_PREFIX, placement["type"])


def light_anchors(manifest: dict) -> list[dict]:
    """The manifest's anchors, validated just enough to trust.

    Accepts both a Deli Counter per-building ``<name>.lights.json`` and a
    Lot-merged site manifest — same schema, different scope key.
    """
    ver = str(manifest.get("light_manifest_version", ""))
    if not ver.startswith("1."):
        raise ValueError(
            "not a lights manifest (light_manifest_version=%r)" % ver)
    anchors = manifest.get("anchors")
    if not isinstance(anchors, list):
        raise ValueError("lights manifest has no 'anchors' list")
    return [a for a in anchors if isinstance(a, dict)]


def scope_id(manifest: dict) -> str:
    """What the output files are named for: the building or the site."""
    return str(manifest.get("building_id") or manifest.get("site") or "scene")


def row_points(anchor: dict) -> list[list[float]]:
    """Every lamp point an anchor expands to, in the manifest's own space.

    Centered on ``pos`` along the ``rot_y`` direction, matching
    LuxFluorescentRig's ``start = -(count-1)/2 * spacing`` exactly. A rowless
    anchor is a single point at pos.
    """
    pos = anchor.get("pos") or [0.0, 0.0, 0.0]
    x, y, z = (float(pos[0]), float(pos[1]),
               float(pos[2]) if len(pos) > 2 else 0.0)
    row = anchor.get("row") or {}
    count = max(1, int(row.get("count", 1)))
    spacing = float(row.get("spacing", 0.0))
    if count == 1 or spacing <= 0.0:
        return [[round(x, 4), round(y, 4), round(z, 4)]]
    a = math.radians(float(anchor.get("rot_y", 0.0)))
    dx, dy = math.cos(a), math.sin(a)
    start = -(count - 1) * 0.5 * spacing
    return [[round(x + (start + i * spacing) * dx, 4),
             round(y + (start + i * spacing) * dy, 4),
             round(z, 4)] for i in range(count)]


def pole_height_for(anchor_z: float, height_dim: dict) -> float:
    """A below-mounted fixture stretches to reach grade at z=0: its height is
    the anchor's z, clamped into the genome's range. Anchors at or below
    grade (malformed) fall back to the genome default."""
    if anchor_z is None or anchor_z <= 0.0:
        return float(height_dim["default"])
    return round(min(max(float(anchor_z), float(height_dim["min"])),
                     float(height_dim["max"])), 4)


def clamp_dim(value: float, dim: dict) -> float:
    """A DC-supplied panel dimension, clamped into a genome range."""
    return round(min(max(float(value), float(dim["min"])),
                     float(dim["max"])), 4)


def _seed_offset(anchor_id: str, slot: int) -> int:
    """Stable per-lamp variation key: same manifest -> same hardware."""
    return (zlib.crc32(str(anchor_id).encode("utf-8")) + slot) % 100000


def plan(manifest: dict, types=None) -> dict:
    """The fixture build plan for a lights manifest.

    ``types``: optional iterable of anchor types to include (default: every
    type in FIXTURES). Returns::

        {"scope_id", "space", "counts": {species: n},
         "placements": [{"anchor_id", "slot", "type", "species", "mount",
                         "pos", "rot_z", "reacts_to_alarm", "seed_offset"}],
         "skipped": [{"id", "type", "reason"}]}
    """
    wanted = set(types) if types else set(FIXTURES)
    placements, skipped, counts = [], [], {}
    for a in light_anchors(manifest):
        t = str(a.get("type", ""))
        aid = str(a.get("id", "light"))
        if t in DAYLIGHT:
            skipped.append({"id": aid, "type": t,
                            "reason": "daylight/preset — no hardware"})
            continue
        fx = FIXTURES.get(t)
        if fx is None:
            skipped.append({"id": aid, "type": t,
                            "reason": "no fixture species for this type"})
            continue
        if t not in wanted:
            skipped.append({"id": aid, "type": t,
                            "reason": "filtered out by --fixture-types"})
            continue
        for j, p in enumerate(row_points(a)):
            placement = {
                "anchor_id": aid,
                "slot": j,
                "type": t,
                "species": fx["species"],
                "mount": fx["mount"],
                "pos": p,
                "rot_z": float(a.get("rot_y", 0.0)) % 360.0,
                "reacts_to_alarm": bool(a.get("reacts_to_alarm", False)),
                "seed_offset": _seed_offset(aid, j),
            }
            size = a.get("size")
            if (isinstance(size, (list, tuple)) and len(size) >= 2):
                # DC sizes the panel (signs); the builder clamps it into the
                # genome's dimension range.
                placement["size"] = [float(size[0]), float(size[1])]
            placements.append(placement)
            counts[fx["species"]] = counts.get(fx["species"], 0) + 1
    return {
        "scope_id": scope_id(manifest),
        "space": manifest.get("space", "Blender Z-up, meters"),
        "counts": counts,
        "placements": placements,
        "skipped": skipped,
    }
