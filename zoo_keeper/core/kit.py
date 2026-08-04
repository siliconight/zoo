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
- INTERACTIVE slots (doors, breachable walls) carry an `interactive` block and
  expand into per-state module variants (`_<state>` suffix), so each networked
  state has art to show. Zoo builds the art; the state machine + replication
  live in gameplay.json / the game. See INTERACTIVES.md for the shared contract.

Coordinates match Zoo's native space (Blender Z-up, meters; rot_y in degrees),
so a Zoo module drops onto a slot transform with no conversion.
"""
from __future__ import annotations


def _void_key(voids):
    """A hashable, order-independent identity for a plate's holes."""
    return tuple(sorted(
        (round(float(v["x0"]), 4), round(float(v["y0"]), 4),
         round(float(v["x1"]), 4), round(float(v["y1"]), 4))
        for v in (voids or ())))


#: Roles built as a horizontal PLATE. Their footprint varies on BOTH axes, so
#: width alone does not identify a module -- see :func:`module_stem`.
PLATE_ROLES = ("floor", "ceiling")


def void_tag(voids) -> str | None:
    """A short, stable tag for a plate's hole set, or None when it has none.

    Two rooms of identical footprint with stairwells in DIFFERENT places are
    different geometry, and the module key already knows that. The filename did
    not: `security_office` and `count_room` are both 22x16, planned as two
    modules, and both were named `floor_rockay_01_w2200_d1600`. One file wins
    and one room gets the other's holes -- the same class of collision the
    depth suffix fixed, one level down.

    Formatted, not hashed with repr: both repos compute this and float repr is
    not a contract. Order-independent, so the same holes listed differently are
    the same tag.
    """
    import hashlib
    if not voids:
        return None
    parts = sorted("%.4f,%.4f,%.4f,%.4f" % (float(v["x0"]), float(v["y0"]),
                                            float(v["x1"]), float(v["y1"]))
                   for v in voids)
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:6]


def slot_typename(role: str, size_mod: str) -> str:
    """Deli Counter's naming law: a wall remainder is its own 'wallEnd' type."""
    if role == "wall" and size_mod == "end":
        return "wallEnd"
    return role


def module_stem(typ: str, theme: str, style: int,
                width_cm: int = None, state: str = None,
                depth_cm: int = None, voids_tag: str = None) -> str:
    """The exact filename stem Deli Counter's resolver looks for:
    ``<type>_<theme>_<style:02d>[_w<cm>][_d<cm>][_<state>]``.

    ``depth_cm`` IS ONLY FOR PLATES, and only because width alone stopped
    identifying a module. A wall varies on one axis -- its width -- while its
    thickness and the storey height are fixed, so ``_w<cm>`` is a complete key
    and every existing wall/doorway/window filename is unchanged. A floor or
    ceiling varies on both: a 44x24 room and a 44x16 room both planned as
    ``floor_rockay_01_w4400``, one won the name, both rooms resolved to it, and
    the shorter room got a slab eight metres too deep.

    Deli Counter's ``themed_tscn.module_stem`` is the mirror of this function.
    NEITHER SIDE PARSES the stem -- both construct it from the same slot -- so
    the two must be changed together and there is no back-compatibility to
    preserve beyond leaving non-plate names alone, which this does.
    """
    base = f"{typ}_{theme}_{style:02d}"
    if width_cm is not None:
        base += f"_w{int(round(width_cm))}"
    if depth_cm is not None:
        base += f"_d{int(round(depth_cm))}"
    if voids_tag:
        base += f"_v{voids_tag}"
    if state:
        base += f"_{state}"
    return base


def slot_variants(slot: dict, typ: str, global_state: str = None):
    """Which (build_species, state, stem_state) a slot needs.

    A plain slot needs one module. An INTERACTIVE slot (an `interactive` block
    with `states` + `default`) is a small replicable state machine — see
    INTERACTIVES.md — and needs the DEFAULT state's art (the base stem) plus a
    variant per non-default state WHOSE GEOMETRY DIFFERS. Which species backs a
    state comes from the slot's `interactive.state_geometry` map (state ->
    module species; unmapped -> the slot's own type). A non-default state that
    resolves to the SAME species as the default is identical art today, so it's
    deferred: Deli Counter's resolver falls back to the base module (the art
    pass differentiates it later). This keeps a breachable wall as the
    `breached` STATE of a wall slot (built with breach geometry, named
    `wall_..._breached`), not a standalone module.

    Yields ``(build_species, state, stem_state, deferred)`` — deferred entries
    are reported, not built.
    """
    inter = slot.get("interactive")
    if not inter:
        yield (typ, None, global_state, False)
        return
    states = inter.get("states") or []
    default = inter.get("default") or (states[0] if states else None)
    sg = inter.get("state_geometry", {})

    def species_for(st):
        return sg.get(st, typ)

    default_species = species_for(default)
    # default state -> base stem (carries any whole-kit global_state suffix)
    yield (default_species, None, global_state, False)
    for st in states:
        if st == default:
            continue
        sp = species_for(st)
        # same species as default => identical art today => resolver fallback
        yield (sp, st, st, sp == default_species)


def plan_kit(manifest: dict, theme: str = "delco", style: int = 1,
             roles=None, state: str = None, known_species=None) -> dict:
    """From a Deli Counter slots.json manifest, return the distinct Zoo modules
    needed to theme the building.

    roles: optional set to limit which slot roles are planned (e.g. {'wall'}).
    state: an optional WHOLE-KIT state suffix (e.g. build every module as a
    'night' variant) — distinct from per-slot interactive states, which come
    from each slot's `interactive` block (see INTERACTIVES.md).

    known_species: optional collection of species names the library can
    actually build. When given, any planned module whose backing species is
    unknown lands in ``missing_modules`` (the production gap report the
    Production Package requires) instead of crashing at build time.

    Returns {building_id, theme, module_count, slot_count, modules:[...],
    deferred_variants:[...], missing_modules:[...]}, where each module has:
    stem, type (the slot's
    base/role type — drives the filename), species (the geometry actually
    built — differs from type only for state variants like a breached wall),
    state (the interactive state this variant is, or None), width_cm,
    fit ('exact'|'unit'), dims [w, d, h], pivot, and count.
    """
    buckets = {}
    deferred = {}
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
        # Plates vary on both axes; everything else is identified by width.
        depth_cm = (int(round(dims[1] * 100))
                    if exact and typ in PLATE_ROLES else None)
        vtag = void_tag(fit.get("voids")) if typ in PLATE_ROLES else None
        # Per-slot SKIN STYLE + MATERIAL (Deli Counter >= 0.88): the slot's
        # own material-driven style wins over the kit-level default, so one
        # building demands one module family PER MATERIAL ZONE (concrete
        # exterior, drywall interiors, glass curtain wall, metal service)
        # instead of funnelling every surface through a single style. Slots
        # without a style (older manifests) keep the global default --
        # nothing changes for them.
        slot_style = int(s.get("style") or style or 1)
        slot_material = s.get("material")

        for species, st, stem_state, is_deferred in slot_variants(s, typ,
                                                                   state):
            stem = module_stem(typ, theme, slot_style, width_cm, stem_state,
                               depth_cm, vtag)
            if is_deferred:
                d = deferred.get(stem)
                if d is None:
                    d = {"stem": stem, "type": typ, "state": st,
                         "would_be_species": species,
                         "reason": "same geometry as default state; Deli "
                                   "Counter falls back to the base module "
                                   "until the art pass differentiates it",
                         "count": 0}
                    deferred[stem] = d
                d["count"] += 1
                continue

            # Facade-shell windows carry glazing="facade" (opaque glass); keep it
            # in the key so they never merge with see-through window modules, and
            # thread it onto the module for build_module to swap the glass kind.
            glaze = s.get("glazing")
            # The full dims are in the key ONLY when the fit is exact. For a
            # wall that changes nothing -- same width implies same thickness
            # and storey height -- and for a plate it is the difference between
            # one module and two. `voids` likewise: two rooms of identical
            # footprint with stairwells in different places are different
            # geometry.
            #
            # A UNIT module must not key on dims, and that is a guarantee, not
            # an oversight. A wallEnd is one 1x1x1 box that Deli Counter scales
            # per slot, so remainders of 0.30 m and 0.45 m are the SAME module;
            # keying them on their slot dims split one unit module into two
            # identical ones. `test_plan_collapses_to_distinct_modules` caught
            # it, and it was right to.
            dims_key = (tuple(round(float(v), 4) for v in dims[:3])
                        if exact else None)
            key = (typ, width_cm, st, species, glaze, slot_style,
                   slot_material, dims_key, _void_key(fit.get("voids")))
            b = buckets.get(key)
            if b is None:
                b = {
                    "stem": stem,
                    "type": typ,
                    "species": species,
                    "state": st,
                    "width_cm": width_cm,
                    "depth_cm": depth_cm,
                    "voids_tag": vtag,
                    "voids": list(fit.get("voids") or ()),
                    "style": slot_style,
                    "material": slot_material,
                    "fit": "exact" if exact else "unit",
                    "dims": ([round(dims[0], 4), round(dims[1], 4),
                              round(dims[2], 4)] if exact else [1.0, 1.0, 1.0]),
                    "pivot": fit.get("pivot", "center"),
                    "glazing": glaze,
                    "count": 0,
                }
                buckets[key] = b
            b["count"] += 1

    modules = sorted(buckets.values(),
                     key=lambda m: (m["type"], m.get("style", 1),
                                    m["width_cm"] or 0, m["state"] or ""))
    missing = []
    if known_species is not None:
        known = set(known_species)
        buildable = []
        for m in modules:
            if m["species"] in known:
                buildable.append(m)
            else:
                missing.append(dict(m, reason=(
                    f"no '{m['species']}' species in the genome library — "
                    f"the building cannot be fully dressed until it exists")))
        modules = buildable
    return {
        "building_id": manifest.get("building_id"),
        "theme": theme,
        "style": style,
        "state": state,
        "module_size": manifest.get("module_size"),
        "module_count": len(modules),
        "slot_count": sum(m["count"] for m in modules),
        "modules": modules,
        "deferred_variants": sorted(deferred.values(), key=lambda d: d["stem"]),
        "missing_modules": missing,
    }
