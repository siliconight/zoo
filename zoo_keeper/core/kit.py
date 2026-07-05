"""Kit planner (pure) — Zoo as Deli Counter's `art/zoo` module library.

Deli Counter greyboxes a building and emits a `<name>.slots.json` swap
contract: every wall / doorway / window / breach slot with a transform, fit
dims, a role, and a size_mod. Its resolver looks for
`<type>_<theme>_<style>_w<cm>.glb` in the module library it names `art/zoo`
and instances that themed module at the slot instead of a greybox box; when a
module is missing it keeps the box, so the art pass is progressive.

Zoo IS that library. This plans exactly which modules Zoo must build to dress a
given building, honoring Deli Counter's naming law:

- wall remainders (size_mod 'end') -> ONE unit `wallEnd` module, scaled
  per-slot by Deli Counter (a single 1x1x1 module fits every remainder size);
  never themed, just solid filler.
- everything else -> exact-fit: one module per distinct (type, width), built at
  the authored size so themed art is instanced, never stretched.

Coordinates match Zoo's native space (Blender Z-up, meters; rot_y in degrees),
so a Zoo module drops onto a slot transform with no conversion.
"""
from __future__ import annotations


def slot_typename(role: str, size_mod: str) -> str:
    """Deli Counter's naming law: a wall remainder is its own 'wallEnd' type."""
    if role == "wall" and size_mod == "end":
        return "wallEnd"
    return role


def module_stem(typ: str, theme: str, style: int,
                width_cm: int = None, state: str = None) -> str:
    """The exact filename stem Deli Counter's resolver looks for:
    <type>_<theme>_<style:02d>[_w<cm>][_<state>]."""
    base = f"{typ}_{theme}_{style:02d}"
    if width_cm is not None:
        base += f"_w{int(round(width_cm))}"
    if state:
        base += f"_{state}"
    return base


def plan_kit(manifest: dict, theme: str = "delco", style: int = 1,
             roles=None, state: str = None) -> dict:
    """From a Deli Counter slots.json manifest, return the distinct Zoo modules
    needed to theme the building.

    roles: optional set to limit which slot roles are planned (e.g. {'wall'}).
    Returns {building_id, theme, module_count, slot_count, modules:[...]},
    where each module has: stem, type, width_cm, fit ('exact'|'unit'),
    dims [w, d, h], pivot, and count (how many slots it fills).
    """
    buckets = {}
    for s in manifest.get("slots", []):
        role = s.get("role")
        if role is None or (roles and role not in roles):
            continue
        fit = s.get("fit", {})
        dims = fit.get("dims")
        if not dims or len(dims) < 3:
            continue
        typ = slot_typename(role, s.get("size_mod"))
        exact = typ != "wallEnd"
        width_cm = int(round(dims[0] * 100)) if exact else None
        key = (typ, width_cm)
        b = buckets.get(key)
        if b is None:
            b = {
                "stem": module_stem(typ, theme, style, width_cm, state),
                "type": typ,
                "width_cm": width_cm,
                "fit": "exact" if exact else "unit",
                "dims": ([round(dims[0], 4), round(dims[1], 4),
                          round(dims[2], 4)] if exact else [1.0, 1.0, 1.0]),
                "pivot": fit.get("pivot", "center"),
                "count": 0,
            }
            buckets[key] = b
        b["count"] += 1
    modules = sorted(buckets.values(),
                     key=lambda m: (m["type"], m["width_cm"] or 0))
    return {
        "building_id": manifest.get("building_id"),
        "theme": theme,
        "style": style,
        "state": state,
        "module_size": manifest.get("module_size"),
        "module_count": len(modules),
        "slot_count": sum(m["count"] for m in modules),
        "modules": modules,
    }
