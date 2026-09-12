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
    # slot-driven module builds carry exact fit targets; for those the SLOT is
    # the authority on size (fit_* checks below gate hard) and the genome's
    # prompt-era dimension ranges are advisory only (warn, don't fail) — a
    # Deli Counter building may legitimately need a 0.3 m wall return the
    # prop-range never anticipated.
    fit_targets = (plan.get("target_dims")
                   or (plan.get("module") or {}).get("target_dims") or {})
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
               f"{name}={v:.3f}m OUTSIDE [{lo:.3f}, {hi:.3f}]m"
               + (" (advisory: exact slot fit governs)" if fit_targets else ""),
               warn_only=bool(fit_targets))

    # THE PIVOT, MEASURED. Every module is contracted centre-pivot and the
    # kit index repeats the plan's claim per row; Deli Counter and Lot place
    # the module's origin at the slot's centre. `gather_facts` now reports
    # where the visual bounds' centre actually is, and a module whose centre
    # is off the origin by more than the fit tolerance fails here -- the
    # minted placeholders and `simple_car` were built base-up (centre at
    # z = h/2) under a "center" claim, and stood h/2 in the air on cold run
    # 9019's site. Facts without a centre (older gatherers, tests) skip it.
    # Only a SLOT-FIT module carries a `module` block with a pivot claim.
    # A habitat or dressing species -- a pebble, a weed tuft -- is built base
    # -up on purpose, to sit on the surface Patina scatters it over, and has
    # no claim to measure: cold run 9020 failed all four clutter species on
    # this check the first time it ran, because a missing block defaulted
    # to "center".
    center = facts.get("center")
    pivot = plan.get("pivot") or (plan.get("module") or {}).get("pivot")
    if center is not None and pivot == "center":
        off = max(abs(float(c)) for c in center)
        _check(checks, "fit_pivot", off <= tol,
               f"bounds centred at ({center[0]:.3f}, {center[1]:.3f}, "
               f"{center[2]:.3f}) -- "
               + ("on the origin" if off <= tol else
                  f"OFF the claimed centre pivot by {off:.3f}m"))

    # architectural modules are built to a slot's EXACT dims (Deli Counter
    # never scales them) — verify the built size matches the target, not just
    # the genome envelope. Only fires when a plan carries target_dims.
    target = plan.get("target_dims")
    if target:
        for name in sorted(target):
            if name not in dims:
                continue
            tv = target[name]
            v = dims[name]
            ok = abs(v - tv) <= tol
            _check(checks, f"fit_{name}", ok,
                   f"{name}={v:.3f}m fits exact target {tv:.3f}m" if ok
                   else f"{name}={v:.3f}m != exact target {tv:.3f}m")

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
