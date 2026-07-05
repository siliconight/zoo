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


def build_module_meta(tool_version: str, plan: dict, genome: dict,
                      report: dict, files: dict, stem: str) -> dict:
    """Sidecar for an architectural module. Modules aren't prompt-driven, so
    this records the Deli Counter swap contract (type/theme/style/width/fit/
    pivot/dims) in place of an intent block. Timestamp-free + deterministic."""
    m = plan["module"]
    return {
        "zoo": {
            "tool_version": tool_version,
            "module_stem": stem,
        },
        "module": {
            "type": m["type"],
            "theme": m["theme"],
            "style": m["style"],
            "width_cm": m["width_cm"],
            "fit": m["fit"],
            "pivot": plan.get("pivot", "center"),
            "dims": [plan["dimensions"]["width"],
                     plan["dimensions"]["depth"],
                     plan["dimensions"]["height"]],
        },
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
