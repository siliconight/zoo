"""The pivot is enforced, not declared.

Every module is contracted centre-pivot: the kit index says so per row, and
Deli Counter and Lot place a module's origin at its slot's centre. A recipe
that builds base-up -- the minting template did until 2026-09-12, and
`simple_car` does -- ships a module those consumers stand h/2 in the air.
Measured on cold run 9019's site kit: three cover modules, all z 0 .. h under
a "center" claim.

Pure: bounds in, offsets out, vertices moved component-wise so the same code
runs on Blender's `Vector` and on a test's stand-in. `bpylayer.build` calls it
with `geometry.bounds_of`; `core.validate.fit_pivot` then measures the result
rather than trusting this.
"""
from __future__ import annotations

TOL = 1e-4


def offset(lo, hi):
    """The bounds' centre, i.e. what to subtract to centre them."""
    return ((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, (lo[2] + hi[2]) / 2.0)


def recentre(result: dict, plan: dict, lo, hi, tol: float = TOL) -> dict:
    """Shift a recipe's output so its visual bounds ``lo..hi`` are centred on
    the origin when the plan's pivot is ``center``. Vertices move in place;
    collision boxes and attachment points move by the same offset, so the
    three stay in step. A result already centred is returned untouched, and
    a re-centred one records ``recentred_by``."""
    # An explicit claim only: a species built for a surface (clutter,
    # dressing) carries no `module` block and is left where its recipe put it.
    pivot = plan.get("pivot") or (plan.get("module") or {}).get("pivot")
    if pivot != "center":
        return result
    ox, oy, oz = offset(lo, hi)
    if max(abs(ox), abs(oy), abs(oz)) <= tol:
        return result
    for o in result.get("objects", []):
        if getattr(o, "type", "MESH") != "MESH":
            continue
        for v in o.data.vertices:
            v.co.x -= ox
            v.co.y -= oy
            v.co.z -= oz
        if hasattr(o.data, "update"):
            o.data.update()
    result["collision_boxes"] = [
        ((a[0] - ox, a[1] - oy, a[2] - oz), (b[0] - ox, b[1] - oy, b[2] - oz))
        for a, b in result.get("collision_boxes", [])]
    result["attachments"] = {
        n: (p[0] - ox, p[1] - oy, p[2] - oz)
        for n, p in result.get("attachments", {}).items()}
    result["recentred_by"] = [round(ox, 4), round(oy, 4), round(oz, 4)]
    return result
