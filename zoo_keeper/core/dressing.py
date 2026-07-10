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
_COVER = {
    "edge_strip":  {"proud": 0.06, "cross": 0.10, "span": 2.0},
    "base_course": {"proud": 0.04, "cross": 0.35, "span": 2.0},
    "curb":        {"proud": 0.05, "cross": 0.12, "span": 2.0},
    "conduit_run": {"proud": 0.04, "cross": 0.05, "span": 1.6},
    # One panel of a panel field (Patina v0.17 wall_panel orders): a thin
    # proud plate; the field effect comes from many orders in a grid, and
    # the gaps between plates are where the facade gets its shadow lines.
    "panel_field": {"proud": 0.03, "cross": 1.2, "span": 1.2},
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
    if cover == "panel_field":
        w, h = (size2 if size2 and len(size2) == 2
                else (max(size_hint, 0.2), max(size_hint, 0.2)))
        return (max(float(w), 0.05), c["proud"], max(float(h), 0.05))
    span = max(0.2, c["span"] * max(size_hint, 0.1) / 0.6)
    if cover == "conduit_run":
        return (c["cross"], c["proud"], span)          # slim, tall
    return (span, c["proud"], c["cross"])              # long, short


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
            "size": float(order.get("size", 0.6)),
            "pos": order_position(order, space),
            "normal": order_normal(order, space),
            "collision": order.get("collision", "none"),
            "seed_offset": int(order.get("seed_offset", 0)),
            "size2": ([float(v) for v in order["size2"]]
                      if isinstance(order.get("size2"), (list, tuple))
                      else None),
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
