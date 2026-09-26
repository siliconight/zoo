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
# 'below' (body below AND stretched to grade — poles), 'center' (emitter IS
# the body's centre — sign faces), 'hang' (v0.94: body below, its TOP at the
# emitter, NOT stretched — a can under a ceiling). Extending the pipeline is
# one row here + one genome + one recipe.
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
    # v0.50, the below-grade rule (DC >= 0.98, roadmap 57's 90s palette):
    # basements and objective rooms derive `pendant` anchors. The anchor is
    # the BULB point 0.6 m below the ceiling; mount 'above' puts the
    # recipe's bottom (the bulb) at the anchor and the cord rises to the
    # slab. Before this row existed the type was skipped as "no fixture
    # species" -- and a skipped anchor emits NO MARKER, so on the marker
    # path (the one this pipeline ships) every basement was silently dark.
    "pendant": {"species": "pendant_fixture", "mount": "above"},
    # v0.94 the club set (Lux 0.37.0's anchors, walked 2026-09-16 as
    # "it doesn't look like that light is coming out of any viewable light
    # fixtures"). Both mount 'above', so the LIT LENS sits on the emitter
    # point and the barrel rises into the ceiling gap behind it.
    #
    # `marker: False` IS THE LOAD-BEARING FIELD HERE. Every row above emits
    # a LuxEmit empty and LuxFixtureSpawner puts the lamp there, which is
    # how lights ship. These two must not: the spawner hands
    # `LuxLightLoader.rig_for_anchor` only {type, id, drop}, so a club_wash
    # would lose the zone COLOUR and the pool RADIUS Deli Counter measured
    # and take a hash pick instead, and a stage_light would lose its TARGET
    # and be refused outright. Their light stays on the manifest bake
    # (`bake_club`), which has the whole anchor -- and a marker here would
    # DOUBLE every club light rather than replace it. Moving the club set
    # onto markers means widening the marker payload first.
    # MOUNT 'hang', NOT 'above', AND THE FIRST BUILD GOT IT WRONG. A club
    # anchor's pos IS the ceiling plane (Deli Counter writes z = the storey's
    # 3.2 m), so 'above' -- bottom at the emitter, body upward -- put the
    # whole can inside the slab and left a 7 cm lens recessed in a throat
    # nobody can see from the floor. Shot at the walker's own station and
    # looked at: two par cans visible, five wash cans not. 'hang' is the
    # mirror of it -- TOP at the emitter, body below, no pole stretch -- so
    # the can hangs under the ceiling with its mouth down, which is also
    # where Lux hangs the lamp (`FLUORESCENT_MOUNT` -0.25 m, which the club
    # wash inherits).
    "club_wash": {"species": "club_fixture", "mount": "hang", "marker": False,
                  "params": {"form": "can"}},
    "stage_light": {"species": "club_fixture", "mount": "hang",
                    "marker": False, "params": {"form": "par"}, "aim": True},
    # v1.5 THE FUEL CANOPY (DC light manifest v1.3). ONE placement covers the
    # whole deck: the species lays the lamp grid inside a single pair of
    # meshes, so a 24 x 10 m canopy is two draw calls rather than two per
    # lamp. `mount: above` puts the recipe's bottom -- the lit lens face --
    # at the anchor, which Deli Counter writes at the soffit, and the housing
    # rises into the deck above it.
    #
    # `marker: False` for the same reason the club rows carry it, reached from
    # the other direction. A marker would make LuxFixtureSpawner put a LAMP
    # here, and the grid holds 12 to 24 of them; every one would reach the
    # forecourt ground mesh against a `max_lights_per_object` of 8 on the
    # renderer packages ship on. The lenses are emissive and light nothing.
    # The light is `canopy_wash`, below.
    #
    # `sized: True` is new and this is the only row that needs it. The
    # species' dimensions are the DECK, not a fixture, so the anchor's `size`
    # has to reach the recipe -- a placement that drops it builds the genome's
    # default deck on every canopy there is.
    "canopy_lights": {"species": "canopy_lights", "mount": "above",
                      "marker": False, "sized": True},
}

# anchor types that are light without hardware, by design.
DAYLIGHT = {"window", "sun"}

# ...and the club anchors that ALREADY have hardware, built by something
# else, so "no fixture species for this type" would be a lie about them.
# A `neon` IS its sign and `sign_box` builds it; a `back_bar` is the bar's
# own bulbs and porthole and the `back_bar` species builds those; a
# `room_ambient` is a ReflectionProbe and has nothing to hang.
HARDWARE_ELSEWHERE = {
    "neon": "the sign it is mounted on (species sign_box)",
    "back_bar": "the bar's own bulbs and porthole (species back_bar)",
    "room_ambient": "a probe, not a lamp -- nothing to build",
    # v1.5: a canopy wash is a light POSITION under a fuel canopy and has no
    # hardware at all -- the lamps a player sees are the emissive grid the
    # `canopy_lights` row above builds. Cold run 9081 reported it as "no
    # fixture species for this type", which was true of the table and a lie
    # about the anchor, and this is the distinction that line exists to draw.
    "canopy_wash": ("the canopy's own lamp grid (species canopy_lights); "
                    "its light is on the manifest bake"),
}

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
        if t in HARDWARE_ELSEWHERE:
            skipped.append({"id": aid, "type": t,
                            "reason": "hardware built elsewhere: %s"
                                      % HARDWARE_ELSEWHERE[t]})
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
                # The lamp's distance down to its own room's floor (DC >=
                # 0.97). Rides every per-lamp marker as `lux_drop`, because
                # THE MARKER PATH IS THE SHIPPING PATH: the manifest chain
                # carried `drop` end to end while LuxFixtureSpawner handed
                # the tuning table only {type, id} -- measured on
                # lot_demo_001 as every fluorescent at the 4.5 fallback and
                # the arena's 5.6 m hall lit-ceiling-over-black-floor.
                "drop": float(a.get("drop", 0.0) or 0.0),
                "seed_offset": _seed_offset(aid, j),
                # v0.94: whether this placement emits a LuxEmit marker (see
                # the club rows in FIXTURES). Every row that does not say
                # otherwise does, so nothing above this changes.
                "marker": bool(fx.get("marker", True)),
            }
            # v1.5: WHICH TWO AXES `size` MEANS, which was never ambiguous
            # until now. Every sized row before this one is a SIGN PANEL, so
            # the builder has always read `size` as width x HEIGHT. A canopy's
            # size is a FOOTPRINT -- width x DEPTH -- and reading it as height
            # would try to build a 13 m tall fixture. The copy itself is
            # already done below for every placement; only the meaning is new.
            if fx.get("sized"):
                placement["size_is_footprint"] = True
            if fx.get("params"):
                placement["params"] = dict(fx["params"])
            if fx.get("aim"):
                # A FIXTURE THAT AIMS OVERRIDES THE ANCHOR'S OWN rot_y, and
                # takes a tilt with it. `rot_y` on a stage_light is the row's
                # axis, not the barrel's: the anchor carries a `target`, and
                # a par can that does not point at it is a prop. Both are in
                # the MANIFEST'S OWN FRAME, so this is only sound on the
                # per-building manifest Zoo builds from -- Lot's merge
                # transforms `pos` and copies `target` verbatim, which is
                # the defect Lux 0.40.0 refuses a light over. A placement
                # with no usable target keeps the anchor's rot_y and hangs
                # plumb, which is what an untargeted spot means.
                tgt = a.get("target")
                if isinstance(tgt, (list, tuple)) and len(tgt) >= 3:
                    from . import club_fixture_forms as _cff
                    bearing, tilt = _cff.tilt_for(p, tgt)
                    placement["rot_z"] = bearing
                    placement["tilt_deg"] = tilt
                else:
                    placement["tilt_deg"] = 0.0
            if a.get("color"):
                # the gel: the lens reads in the colour of the pool it makes
                placement["gel"] = str(a.get("color"))
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
