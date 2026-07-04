"""Ingest core (pure) — adopt external assets into Zoo's pipeline.

Zoo's value isn't only procedural generation; it's normalization to one
standard (1u=1m, pivot bottom-center, Z-up, applied transforms, collision,
meta.json, Godot-ready GLB). This module holds the offline, testable brains of
"take a random asset and condition it to that standard": scanning an archive
for importable files, resolving a target size (optionally from a genome, so
"ingest as a chair" scales it to chair dimensions), and writing honest
provenance metadata. The Blender-side import/normalize/export lives in
bpylayer/ingest.py.
"""
from __future__ import annotations

import os
import zipfile

# mesh formats we can bring in through Blender
SUPPORTED_EXTS = {".glb", ".gltf", ".fbx", ".obj", ".dae", ".stl", ".ply",
                  ".blend"}


def scan_archive(zip_path: str) -> list[dict]:
    """List importable mesh files inside a .zip (recursively). Pure — no
    Blender. Returns [{path, ext, size}] sorted by path."""
    out = []
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            ext = os.path.splitext(info.filename)[1].lower()
            if ext in SUPPORTED_EXTS:
                out.append({"path": info.filename, "ext": ext,
                            "size": info.file_size})
    return sorted(out, key=lambda e: e["path"])


def resolve_target_height(target_height, species, genome_module):
    """Meters to scale the asset's overall height to: explicit value wins,
    else a species' genome default height, else None (assume already meters)."""
    if target_height:
        return float(target_height)
    if species:
        g = genome_module.load_species(species)
        return float(g["dimensions"]["height"]["default"])
    return None


def ingest_meta(name, origin_file, tool_version, dimensions=None,
                species=None, license_note=None):
    """Provenance sidecar for an adopted asset. Mirrors the generated
    meta.json shape but marks it ingested and records the source. Zoo does NOT
    grant any rights — the license note is the user's to confirm."""
    return {
        "specimen_id": name,
        "source": "ingested",
        "generator": "zoo-ingest",
        "origin_file": os.path.basename(origin_file),
        "species_hint": species,
        "dimensions": dimensions or {},
        "tool_version": tool_version,
        "license": license_note or "third-party — user must confirm rights",
    }


def safe_name(raw: str) -> str:
    """Clean an arbitrary filename into a specimen id (no spaces/paths)."""
    stem = os.path.splitext(os.path.basename(raw))[0]
    keep = [c if (c.isalnum() or c in "-_") else "_" for c in stem.lower()]
    out = "".join(keep).strip("_") or "asset"
    return out
