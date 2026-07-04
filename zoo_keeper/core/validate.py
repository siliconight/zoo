"""Validation: evaluate gathered scene facts against genome + plan.

Pure Python. The bpy layer gathers `facts`; this module judges them so the
logic is unit-testable without Blender.
"""
from __future__ import annotations

PASS, WARN, FAIL = "pass", "warn", "fail"


def _check(checks, cid, ok, msg, warn_only=False):
    level = PASS if ok else (WARN if warn_only else FAIL)
    checks.append({"id": cid, "level": level, "msg": msg})


def evaluate(facts: dict, genome: dict, plan: dict, options: dict) -> dict:
    """facts = {dimensions:{w,d,h}, tris:int, parts:[names], has_uvs:bool,
    has_wear_colors:bool, materials:[names], has_collision:bool,
    unapplied_transforms:[names]}"""
    checks: list[dict] = []
    tol = 0.02  # 2 cm grace on bound checks

    dims = facts.get("dimensions", {})
    scale = plan.get("dim_scale", {})
    for name, spec in genome["dimensions"].items():
        if name not in dims:
            continue
        s = scale.get(name, 1.0)
        lo, hi = spec["min"] * s, spec["max"] * s
        v = dims[name]
        ok = (lo - tol) <= v <= (hi + tol)
        _check(checks, f"dim_{name}", ok,
               f"{name}={v:.3f}m within [{lo:.3f}, {hi:.3f}]m"
               if ok else
               f"{name}={v:.3f}m OUTSIDE [{lo:.3f}, {hi:.3f}]m")

    tris = facts.get("tris", 0)
    budget = plan["budgets"].get("tris_lod0", 0)
    _check(checks, "tri_budget", tris <= budget,
           f"{tris} tris <= budget {budget}" if tris <= budget
           else f"{tris} tris exceeds budget {budget}", warn_only=True)

    _check(checks, "uvs", bool(facts.get("has_uvs")),
           "UV layer present" if facts.get("has_uvs") else "missing UVs")

    _check(checks, "wear_colors", bool(facts.get("has_wear_colors")),
           "vertex wear colors present" if facts.get("has_wear_colors")
           else "missing 'Wear' color attribute", warn_only=True)

    _check(checks, "materials", bool(facts.get("materials")),
           "materials assigned" if facts.get("materials")
           else "no materials assigned")

    parts = facts.get("parts", [])
    _check(checks, "parts_named", bool(parts) and all(parts),
           f"{len(parts)} named parts" if parts else "no named parts")

    if options.get("collision", True):
        _check(checks, "collision", bool(facts.get("has_collision")),
               "collision mesh present ('-col')"
               if facts.get("has_collision") else "collision mesh missing")

    bad_xf = facts.get("unapplied_transforms", [])
    _check(checks, "transforms", not bad_xf,
           "all transforms applied" if not bad_xf
           else "unapplied transforms on: " + ", ".join(bad_xf))

    levels = {c["level"] for c in checks}
    status = FAIL if FAIL in levels else (WARN if WARN in levels else PASS)
    return {"status": status, "checks": checks}


def summarize(report: dict) -> str:
    n = len(report["checks"])
    fails = [c for c in report["checks"] if c["level"] == FAIL]
    warns = [c for c in report["checks"] if c["level"] == WARN]
    lines = [f"validation: {report['status'].upper()} "
             f"({n} checks, {len(fails)} fail, {len(warns)} warn)"]
    for c in fails + warns:
        lines.append(f"  [{c['level']}] {c['id']}: {c['msg']}")
    return "\n".join(lines)
