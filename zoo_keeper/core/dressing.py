"""Plan facade covers from a Patina dressing manifest (pure, no bpy).

Patina v0.11 emits ``<building>.dressing.json``: a trim atlas plus per-anchor
build orders. This module turns that manifest into cover *plans* Zoo's
``dress_cover`` recipe can build — the pure half, so it is unit-testable
without Blender.

The contract (Patina ``docs/DRESSING_CONTRACT.md``):

* ``space`` — ``"spec/Blender Z-up raw coords"`` when Patina saw a DC
  slots.json (the normal case), else Patina's baked Y-up frame. Orders'
  ``pos``/``normal`` are already in that space; Zoo builds in Blender Z-up, so
  a Y-up manifest is converted here (the inverse of Patina's export).
* each order carries ``cover``, ``trim_piece``, ``uv_region``, ``pos``,
  ``normal``, ``size``, ``collision`` (always ``"none"``) and ``seed_offset``.

A plan is a small dict the recipe + orchestrator consume; the theme drives
material/color/wear via the ``dress_cover`` genome's style block, so covers
match the kit Zoo built for the same building.
"""
from __future__ import annotations

import json

DRESSING_SCHEMA = "patina-dressing/1"

# cover kind -> proud (how far it stands off the surface), cross (its height or
# width on the surface), span (nominal length along the run). Pure data so the
# recipe's geometry stays a thin wrapper and sizing is unit-testable.
# Dressing detail is capped against the surface it sits on: on a 3.7 m storey
# base_course was 1/11 and pilaster 1/15, coarse enough to read as structure
# rather than trim. Both halved. The four already finer than 1/20 -- gutter
# 1/26, curb 1/31, edge_strip 1/37, conduit 1/74 -- are left alone; the
# instinct that dressing was too chunky was right and pointed at these three.
_COVER = {
    "edge_strip":  {"proud": 0.06, "cross": 0.10, "span": 2.0},
    "base_course": {"proud": 0.04, "cross": 0.18, "span": 2.0},
    "curb":        {"proud": 0.05, "cross": 0.12, "span": 2.0},
    "conduit_run": {"proud": 0.04, "cross": 0.05, "span": 1.6},
    # One panel of a panel field (Patina v0.17 wall_panel orders): a thin
    # proud plate; the field effect comes from many orders in a grid, and
    # the gaps between plates are where the facade gets its shadow lines.
    "panel_field": {"proud": 0.03, "cross": 1.2, "span": 1.2},
    # v0.26 facade kit (Patina --frames/--gutters/--pilasters):
    "gutter_run":  {"proud": 0.10, "cross": 0.14, "span": 2.0},
    "pilaster":    {"proud": 0.05, "cross": 0.12, "span": 4.2},
    "frame":       {"proud": 0.05, "cross": 0.12, "span": 1.0},
}


def strip_size(cover: str, size_hint: float, size2=None):
    """(w, d, h) of a cover's local strip before the anchor normal orients it.

    span runs along the wall/edge (scaled by the anchor size hint); depth is how
    far it stands proud; the third axis is its height/width on the surface.
    conduit_run is the exception: a tall, slim vertical run. panel_field uses
    the order's ``size2`` = [face width, face height] exactly — panel grids
    are laid out by Patina, so cells must not be rescaled here.
    """
    c = _COVER.get(cover, _COVER["edge_strip"])
    if cover in ("panel_field", "pilaster"):
        w, h = (size2 if size2 and len(size2) == 2
                else (max(size_hint, 0.2), max(size_hint, 0.2)))
        return (max(float(w), 0.05), c["proud"], max(float(h), 0.05))
    if cover == "gutter_run":
        # spans its wall module exactly (sections join at module seams).
        return (max(size_hint, 0.2), c["proud"], c["cross"])
    if cover == "conduit_run":
        # `size` IS the run length (Patina v0.19: ground plane -> fixture), so
        # it is used as the span directly. It used to be a constant 0.3 hint
        # that got scaled by span/0.6; when the field's meaning changed and
        # this did not, a 2.45 m run became a 6.53 m bar centred on the
        # fixture, spanning -0.82..5.72 -- through the ground and up past the
        # next storey.
        return (c["cross"], c["proud"], max(float(size_hint), 0.2))
    span = max(0.2, c["span"] * max(size_hint, 0.1) / 0.6)
    return (span, c["proud"], c["cross"])              # long, short


def strip_yaw(normal, tangent=None) -> float:
    """Rotation about up, in radians, that orients a cover strip.

    A strip's local shape is (span, proud, cross): LONG in +X, thin in +Y. Two
    axes have to be pinned -- which way it stands proud, and which way it runs
    -- and a normal alone pins only one.

    * Horizontal normal (wall base, conduit): yaw local +Y onto the normal.
      Local +X then lies along the wall for free. Unchanged behaviour.
    * Vertical normal (roofline, curb): the normal says nothing about yaw. This
      used to return no rotation at all, so every such strip kept world +X as
      its run direction no matter which facade it sat on -- on a wall running
      along Y, 64 capping strips became 64 sticks jutting out of the building.
      With a tangent, +X runs along the wall as intended.

    ``tangent`` is optional: absent, this reproduces the old result exactly, so
    a manifest written before Patina emitted one still builds the same way.
    """
    import math
    nx, ny, nz = (float(normal[0]), float(normal[1]), float(normal[2]))
    if abs(nz) > 0.99:
        if tangent is None:
            return 0.0
        tx, ty = float(tangent[0]), float(tangent[1])
        if (tx * tx + ty * ty) < 1e-12:      # tangent is vertical: no yaw to take
            return 0.0
        return math.atan2(ty, tx)
    return math.atan2(ny, nx) - math.pi / 2.0


def uv_offset(order) -> tuple:
    """Where this cover sits, expressed in its OWN rotated frame.

    Covers are built at the origin and moved afterwards, so
    ``geometry.cube_project_uv`` -- which reads ``loop.vert.co``, a LOCAL
    coordinate -- gave all 1374 panel covers on a building the identical UV
    rect. Every panel then sampled the identical patch of concrete, and the
    facade read as a grid of stamped tiles. The seams a player sees are not
    the 3 cm gaps; they are the texture restarting in every cell.

    Adding this offset before projecting makes the projection continuous
    across covers that share a wall: rotating it back through the cover's own
    yaw gives exactly the world position, so the projection axes stay local
    while the COORDINATE is world. Bloodborne's set-dressing writeup calls the
    underlying technique "mixing tileables with simple inserts" -- inserts only
    read as inserts when the tileable behind them is continuous.
    """
    import math
    pos = order.get("pos") or (0.0, 0.0, 0.0)
    px, py, pz = (float(pos[0]), float(pos[1]), float(pos[2]))
    yaw = strip_yaw(order.get("normal") or (0.0, 1.0, 0.0), order.get("tangent"))
    c, sn = math.cos(yaw), math.sin(yaw)
    return (px * c + py * sn, -px * sn + py * c, pz)


def load_manifest(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    schema = data.get("schema", "")
    if not schema.startswith("patina-dressing/"):
        raise ValueError(
            f"{path}: not a Patina dressing manifest (schema={schema!r})")
    return data


def _patina_yup_to_blender(pos):
    """Patina baked Y-up (x, y, z) -> Blender Z-up (x, -z, y).

    Inverse of Patina's ``blender_to_patina`` (which is the glTF axis
    convention). Only used when a manifest is in Patina space; a DC-aligned
    manifest is already Blender Z-up and passes through untouched.
    """
    x, y, z = pos
    return [float(x), float(-z), float(y)]


def _needs_conversion(space: str) -> bool:
    # Blender-Z-up manifests (the DC-aligned default) pass through; only a
    # Patina baked-frame manifest is rotated into Blender.
    return "Blender" not in (space or "")


def order_position(order: dict, space: str):
    pos = order.get("pos", [0.0, 0.0, 0.0])
    return _patina_yup_to_blender(pos) if _needs_conversion(space) else list(pos)


def order_normal(order: dict, space: str):
    n = order.get("normal", [0.0, 0.0, 1.0])
    return _patina_yup_to_blender(n) if _needs_conversion(space) else list(n)


def _style_block(genome: dict, theme: str):
    styles = genome.get("styles", {})
    return styles.get(theme) or styles.get("default") or {}


def dress_plan(order: dict, genome: dict, theme: str, space: str,
               tool_version: str) -> dict:
    """A build plan for one cover order (consumed by recipes/dress_cover.build)."""
    style = _style_block(genome, theme)
    material = style.get("material") or genome["materials"]["default"]
    if material not in genome["materials"]["options"]:
        material = genome["materials"]["default"]
    return {
        "species": "dress_cover",
        "tool_version": tool_version,
        "theme": theme,
        "style": theme if theme in genome.get("styles", {}) else "default",
        "material": material,
        "color": [round(float(c), 4) for c in style.get("color", [0.6, 0.6, 0.6])],
        "wear": round(float(style.get("wear", 0.15)), 3),
        "bevel": style.get("bevel", 0.002),
        "order": {
            "cover": order.get("cover", "edge_strip"),
            "trim_piece": order.get("trim_piece"),
            "uv_region": order.get("uv_region"),
            "tangent": order.get("tangent"),
            "size": float(order.get("size", 0.6)),
            "pos": order_position(order, space),
            "normal": order_normal(order, space),
            "collision": order.get("collision", "none"),
            "seed_offset": int(order.get("seed_offset", 0)),
            "size2": ([float(v) for v in order["size2"]]
                      if isinstance(order.get("size2"), (list, tuple))
                      else None),
            "frame_width": float(order.get("frame_width", 0.12)),
        },
    }


def plan_dressing(manifest: dict, genome: dict, theme: str,
                  tool_version: str) -> dict:
    """All cover plans for a dressing manifest, plus a summary.

    Orders with ``collision`` other than ``"none"`` are dropped defensively —
    the contract is non-collision only; Zoo never builds a colliding cover from
    a dressing order.
    """
    space = manifest.get("space", "")
    orders = [o for o in manifest.get("orders", [])
              if o.get("collision", "none") == "none"]
    plans = [dress_plan(o, genome, theme, space, tool_version) for o in orders]
    counts: dict[str, int] = {}
    for p in plans:
        k = p["order"]["cover"]
        counts[k] = counts.get(k, 0) + 1
    return {
        "building_id": manifest.get("building_id"),
        "trim_sheet": manifest.get("trim_sheet"),
        "space": space,
        "theme": theme,
        "plans": plans,
        "counts": dict(sorted(counts.items())),
        "cover_count": len(plans),
    }


def frame_strips(w: float, h: float, frame_w: float, proud: float):
    """The four strips of an opening frame, as (center, size) box specs in
    cover-local space (x along the wall, y proud, z up; opening centered on
    the origin). Pure so the geometry contract is testable without Blender:
    top and bottom strips overhang the jambs (butt joints at the corners),
    the jambs run the opening height exactly.
    """
    f, p = float(frame_w), float(proud)
    return [
        ((0.0, 0.0, h / 2 + f / 2), (w + 2 * f, p, f)),      # head
        ((0.0, 0.0, -h / 2 - f / 2), (w + 2 * f, p, f)),     # sill
        ((-w / 2 - f / 2, 0.0, 0.0), (f, p, h)),             # left jamb
        ((w / 2 + f / 2, 0.0, 0.0), (f, p, h)),              # right jamb
    ]
