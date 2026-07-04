"""meta.json sidecar: everything needed to reproduce or audit a specimen.

Deliberately timestamp-free — the sidecar is part of the deterministic
output (same inputs => byte-identical meta.json).
"""
from __future__ import annotations

import json


def build_meta(tool_version: str, intent, plan: dict, genome: dict,
               report: dict, files: dict, specimen_id: str) -> dict:
    return {
        "zoo": {
            "tool_version": tool_version,
            "specimen_id": specimen_id,
        },
        "intent": intent.to_dict(),
        "plan": plan,
        "genome": {
            "species": genome["species"],
            "version": genome["version"],
        },
        "license": genome.get("license", {}),
        "validation": report,
        "files": files,
    }


def write_meta(path: str, meta: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True)
        fh.write("\n")
