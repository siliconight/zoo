"""Build an exhibit from a folder of assets — the "Generate Asset Zoo" step.

Scans *.meta.json sidecars (generated *or* ingested), reads each asset's
footprint + category, and lays them out via core.layout into an exhibit
manifest the Godot importer can place. Pure — no Blender, so it runs anywhere.
"""
from __future__ import annotations

import glob
import json
import os

from . import layout as _layout

META_SUFFIX = ".meta.json"


def _stem(meta_path):
    base = os.path.basename(meta_path)
    if base.endswith(META_SUFFIX):
        return base[:-len(META_SUFFIX)]
    return os.path.splitext(base)[0]


def _asset_from_meta(meta, meta_path):
    """Normalize a generated (nested) or ingested (flat) meta into an asset."""
    if "zoo" in meta and "plan" in meta:                 # generated
        name = meta["zoo"].get("specimen_id") or _stem(meta_path)
        dims = meta.get("plan", {}).get("dimensions", {})
        species = (meta.get("genome", {}).get("species")
                   or meta.get("plan", {}).get("species"))
        glb = meta.get("files", {}).get("glb")
    else:                                                # ingested (flat)
        name = meta.get("specimen_id") or _stem(meta_path)
        dims = meta.get("dimensions", {})
        species = meta.get("species_hint") or meta.get("species")
        glb = None
    if not glb:
        glb = _stem(meta_path) + ".glb"
    return {
        "name": name,
        "glb": os.path.basename(glb),
        "w": float(dims.get("width", 0.0) or 0.0),
        "d": float(dims.get("depth", 0.0) or 0.0),
        "h": float(dims.get("height", 0.0) or 0.0),
        "category": species or "misc",
    }


def scan_collection(directory):
    """Return assets found via *.meta.json in a folder (sorted by name).
    Assets with no usable dimensions are skipped."""
    assets = []
    for mp in sorted(glob.glob(os.path.join(directory, "*" + META_SUFFIX))):
        try:
            meta = json.load(open(mp, encoding="utf-8"))
        except (ValueError, OSError):
            continue
        a = _asset_from_meta(meta, mp)
        if max(a["w"], a["d"], a["h"]) <= 0.0:
            continue
        assets.append(a)
    return sorted(assets, key=lambda a: a["name"])


def build_exhibit(assets, scheme="zoo", name="exhibit", tool_version="0.0.0",
                  cols=None, gap=0.5, scale_ref=True):
    plan = _layout.arrange(assets, scheme=scheme, cols=cols, gap=gap,
                           scale_ref=scale_ref)
    return {
        "exhibit": name,
        "scheme": plan["scheme"],
        "tool_version": tool_version,
        "asset_count": len(plan["members"]),
        "members": plan["members"],
        "props": plan["props"],
        "bounds": plan["bounds"],
    }


def write_exhibit(manifest, out_dir, name=None):
    name = name or manifest.get("exhibit", "exhibit")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{name}.exhibit.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    return path
