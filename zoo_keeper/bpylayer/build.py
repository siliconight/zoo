"""Specimen build orchestrator.

prompt -> Intent -> Genome -> BuildPlan -> recipe geometry -> collision /
markers / optional LODs -> validation -> GLB + .blend + meta.json.
"""
from __future__ import annotations

import os

import bpy

from .. import TOOL_VERSION
from ..core import dna, genome as genome_mod, intent as intent_mod
from ..core import kit as kit_mod
from ..core import arch as arch_mod
from ..core import meta as meta_mod, seeding, validate, connect
from .. import recipes
from . import collision, export, lods, markers

DEFAULT_OPTIONS = {
    "collision": None,      # None = use the genome's per-species default
    "lods": False,
    "save_blend": True,
    "clear_scene": False,   # True for headless CLI on a fresh file
}


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)


def build_specimen(prompt: str, out_dir: str, seed: int = 0,
                   options: dict | None = None) -> dict:
    opts = dict(DEFAULT_OPTIONS)
    if options:
        opts.update(options)

    intent = intent_mod.parse(prompt, seed=seed)
    if intent.species is None:
        known = ", ".join(genome_mod.list_species())
        raise ValueError(
            f"Couldn't tell what to build from: '{prompt}'. "
            f"Mention one of: {known}.")

    genome = genome_mod.load_species(intent.species)
    # resolve collision: explicit option wins, else the genome's per-species
    # default (pickups like cash default to no collision), else True.
    if opts["collision"] is None:
        opts["collision"] = bool(genome.get("collision", True))
    root = seeding.root_key(intent.prompt_norm, intent.species, seed,
                            TOOL_VERSION)
    streams = seeding.RNGStreams(root)
    plan = dna.resolve_plan(intent, genome, streams, TOOL_VERSION)

    specimen_id = f"{intent.species}_{seeding.short_hash(root)}"
    if opts["clear_scene"]:
        clear_scene()

    coll = bpy.data.collections.new(specimen_id)
    bpy.context.scene.collection.children.link(coll)

    result = recipes.get(intent.species)(plan, streams, coll)
    root_name = intent.species.title().replace("_", "")

    if opts["collision"] and result.get("collision_boxes"):
        collision.collision_from_boxes(root_name, result["collision_boxes"],
                                       coll)
    for name, loc in result.get("attachments", {}).items():
        markers.add_marker(name, loc, coll)
    if opts["lods"]:
        for obj in list(result["objects"]):
            lods.make_lods(obj, coll)

    facts = export.gather_facts(coll, root_name)
    report = validate.evaluate(facts, genome, plan, opts)

    os.makedirs(out_dir, exist_ok=True)
    base = os.path.join(out_dir, specimen_id)
    files = {"glb": f"{specimen_id}.glb", "meta": f"{specimen_id}.meta.json"}
    export.export_glb(base + ".glb", coll)
    if opts["save_blend"]:
        files["blend"] = f"{specimen_id}.blend"

    meta = meta_mod.build_meta(TOOL_VERSION, intent, plan, genome, report,
                               files, specimen_id)
    meta["connectors"] = connect.build_connectors(
        genome, result.get("attachments", {}), plan.get("dimensions"))
    meta_mod.write_meta(base + ".meta.json", meta)
    if opts["save_blend"]:
        export.save_blend(base + ".blend")

    return {"specimen_id": specimen_id, "out_dir": out_dir,
            "files": files, "report": report, "facts": facts,
            "plan": plan}


def build_family(prompt: str, out_dir: str, base_seed: int = 0,
                 count: int = 1, options: dict | None = None) -> dict:
    """Build a cohesive family: one prompt across seeds base..base+count-1.

    Each sibling is a full specimen (own glb/blend/meta). A single
    `<family_id>.family.json` index is written alongside them.
    """
    from ..core import variants as variants_mod

    intent = intent_mod.parse(prompt, seed=base_seed)
    if intent.species is None:
        known = ", ".join(genome_mod.list_species())
        raise ValueError(
            f"Couldn't tell what to build from: '{prompt}'. "
            f"Mention one of: {known}.")
    species = intent.species

    seeds = variants_mod.variant_seeds(base_seed, count)
    results = [build_specimen(prompt, out_dir, seed=s, options=options)
               for s in seeds]

    plan0 = results[0]["plan"]
    shared = {"style": plan0["style"], "material": plan0["material"],
              "color": plan0["color"]}
    specimens = [{"seed": s, "specimen_id": r["specimen_id"],
                  "dimensions": r["plan"]["dimensions"],
                  "status": r["report"]["status"], "files": r["files"]}
                 for s, r in zip(seeds, results)]

    fid = variants_mod.family_id(intent.prompt_norm, species, base_seed,
                                 count, TOOL_VERSION)
    manifest = variants_mod.build_family_manifest(
        TOOL_VERSION, fid, prompt, species, base_seed, count, shared,
        specimens)
    manifest_file = f"{fid}.family.json"
    meta_mod.write_meta(os.path.join(out_dir, manifest_file), manifest)

    n_fail = sum(1 for r in results if r["report"]["status"] == "fail")
    return {"family_id": fid, "out_dir": out_dir, "count": count,
            "manifest_file": manifest_file, "shared": shared,
            "n_fail": n_fail, "results": results}


def build_module(module: dict, out_dir: str, theme: str = "delco",
                 style: int = 1, options: dict | None = None) -> dict:
    """Build ONE architectural module GLB, named by Deli Counter's law.

    ``module`` is a ``core.kit.plan_kit`` entry. The GLB is a center-pivot slab
    built to the slot's exact dims and written as ``<stem>.glb`` (e.g.
    ``wall_delco_01_w200.glb``) so Deli Counter's resolver instances it at the
    slot with no scaling. Skips the intent/dna sampling path entirely.
    """
    opts = dict(DEFAULT_OPTIONS)
    opts["clear_scene"] = True
    if options:
        opts.update(options)

    species = module["type"]
    build_species = module.get("species", species)
    genome = genome_mod.load_species(build_species)
    if opts["collision"] is None:
        opts["collision"] = bool(genome.get("collision", True))

    plan = dna.resolve_module_plan(module, genome, theme, style, TOOL_VERSION)
    stem = plan["module"]["stem"]

    if opts["clear_scene"]:
        clear_scene()
    coll = bpy.data.collections.new(stem)
    bpy.context.scene.collection.children.link(coll)

    streams = seeding.RNGStreams(
        seeding.root_key(stem, build_species, 0, TOOL_VERSION))
    result = recipes.get(build_species)(plan, streams, coll)
    root_name = arch_mod.root_name(build_species)

    if opts["collision"] and result.get("collision_boxes"):
        collision.collision_from_boxes(root_name, result["collision_boxes"],
                                       coll)
    for name, loc in result.get("attachments", {}).items():
        markers.add_marker(name, loc, coll)

    facts = export.gather_facts(coll, root_name)
    report = validate.evaluate(facts, genome, plan, opts)

    os.makedirs(out_dir, exist_ok=True)
    base = os.path.join(out_dir, stem)
    files = {"glb": f"{stem}.glb", "meta": f"{stem}.meta.json"}
    export.export_glb(base + ".glb", coll)
    if opts["save_blend"]:
        export.save_blend(base + ".blend")
        files["blend"] = f"{stem}.blend"

    meta = meta_mod.build_module_meta(TOOL_VERSION, plan, genome, report,
                                      files, stem)
    meta_mod.write_meta(base + ".meta.json", meta)

    return {"stem": stem, "out_dir": out_dir, "files": files,
            "report": report, "facts": facts, "plan": plan}


def build_kit(manifest: dict, out_dir: str, theme: str = "delco",
              style: int = 1, roles=None, state: str | None = None,
              options: dict | None = None) -> dict:
    """Plan + BUILD every module a Deli Counter building needs, into ``out_dir``.

    Plans the kit from a ``slots.json`` manifest (pure), then builds each
    distinct module to a correctly-named GLB and writes a
    ``<building>_kit.built.json`` index. Copy ``out_dir`` into the game's
    ``art/zoo/`` and Deli Counter swaps them in for the greybox boxes.
    """
    plan = kit_mod.plan_kit(manifest, theme=theme, style=style, roles=roles,
                            state=state,
                            known_species=genome_mod.list_species())
    counts = {m["stem"]: m["count"] for m in plan["modules"]}
    results = [build_module(m, out_dir, theme=theme, style=style,
                            options=options)
               for m in plan["modules"]]

    # Kit index entries carry the full module contract the Production Package
    # requires: name, category, dimensions, pivot, forward, slot types,
    # material set, collision, LOD, validation status. Orientation note:
    # modules are authored center-pivot with their face normal along +Y;
    # the Deli Counter slot transform (rot about up) owns final facing.
    modules = [{"stem": r["stem"],
                "type": r["plan"]["module"]["type"],
                "category": _module_category(r["plan"]["module"]["type"]),
                "species": r["plan"]["module"]["species"],
                "state": r["plan"]["module"]["state"],
                "width_cm": r["plan"]["module"]["width_cm"],
                "fit": r["plan"]["module"]["fit"],
                "dims": r["plan"]["module"].get("dims"),
                "pivot": r["plan"]["module"].get("pivot", "center"),
                "forward": "+Y",
                "supported_slot_types": [r["plan"]["module"]["type"]],
                "material_set": r["plan"].get("material"),
                "collision": bool(r["facts"].get("collision")
                                  or r["facts"].get("has_collision")
                                  or any("col" in str(f).lower()
                                         for f in r["files"].values())),
                "lod": bool((options or {}).get("lods",
                            DEFAULT_OPTIONS.get("lods", False))),
                "count": counts.get(r["stem"], 1),
                "status": r["report"]["status"],
                "files": r["files"]}
               for r in results]

    building_id = plan.get("building_id")
    index = {
        "zoo": {"tool_version": TOOL_VERSION},
        "building_id": building_id,
        "theme": theme,
        "style": int(style),
        "state": state,
        "module_library": "art/zoo",
        "module_count": plan["module_count"],
        "slot_count": plan["slot_count"],
        "modules": modules,
        "deferred_variants": plan.get("deferred_variants", []),
        "missing_modules": plan.get("missing_modules", []),
    }
    index_file = f"{building_id}_kit.built.json"
    meta_mod.write_meta(os.path.join(out_dir, index_file), index)

    n_fail = sum(1 for r in results if r["report"]["status"] == "fail")
    n_missing = len(plan.get("missing_modules", []))
    if n_missing:
        print(f"[zoo] WARNING: {n_missing} module(s) MISSING from the genome "
              f"library (see missing_modules in {index_file}) — the building "
              f"cannot be fully dressed")
    return {"building_id": building_id, "out_dir": out_dir, "theme": theme,
            "style": int(style), "modules": modules, "n_fail": n_fail,
            "n_missing": n_missing,
            "missing_modules": plan.get("missing_modules", []),
            "deferred_variants": plan.get("deferred_variants", []),
            "results": results, "index_file": index_file}


def _module_category(typ: str) -> str:
    """Semantic category taxonomy for the kit index (spec's kit-index field)."""
    return {
        "wall": "architecture/wall",
        "wallEnd": "architecture/wall",
        "doorway": "architecture/doorway",
        "window": "architecture/window",
        "breach": "architecture/breach_state",
        "roof": "architecture/roof",
        "skylight": "architecture/roof",
        "vault_door": "secure/portal",
    }.get(typ, f"module/{typ}")


def _orient_matrix(normal):
    """A rotation placing a local +Z-up strip so its 'proud' (+Y) axis points
    along ``normal``. For up-normals (roofline/curb) the strip stays flat; for
    outward horizontal normals (wall base/conduit) it faces out from the wall.
    """
    import math

    import mathutils

    n = mathutils.Vector(normal)
    if n.length < 1e-6:
        return mathutils.Matrix.Identity(4)
    n.normalize()
    up = mathutils.Vector((0.0, 0.0, 1.0))
    if abs(n.z) > 0.99:
        # normal is (roughly) vertical: strip lies flat, no rotation needed.
        return mathutils.Matrix.Identity(4)
    # rotate local +Y (the proud axis) to the horizontal normal about Z.
    yaw = math.atan2(n.y, n.x) - math.pi / 2.0
    return mathutils.Matrix.Rotation(yaw, 4, "Z")


def build_dressing(manifest: dict, out_dir: str, theme: str = "delco",
                   options: dict | None = None) -> dict:
    """Build non-collision facade covers from a Patina dressing manifest.

    Reads Patina v0.11 ``<building>.dressing.json`` (via ``core.dressing``),
    builds one thin cover mesh per order at its anchor pos/orientation, and
    writes them into a single ``<building>_dressing.glb`` plus a
    ``<building>_dressing.built.json`` index. Never emits collision: covers are
    visual only, so the DC greybox collision stays authoritative.
    """
    import mathutils

    from ..core import dressing as dressing_mod

    opts = dict(DEFAULT_OPTIONS)
    opts["clear_scene"] = True
    if options:
        opts.update(options)

    genome = genome_mod.load_species("dress_cover")
    plan = dressing_mod.plan_dressing(manifest, genome, theme, TOOL_VERSION)
    building_id = plan["building_id"] or "building"

    if opts["clear_scene"]:
        clear_scene()
    coll = bpy.data.collections.new(f"{building_id}_dressing")
    bpy.context.scene.collection.children.link(coll)

    built = 0
    for i, cplan in enumerate(plan["plans"]):
        order = cplan["order"]
        streams = seeding.RNGStreams(
            seeding.root_key(f"{building_id}_cover_{i}", "dress_cover",
                             order["seed_offset"], TOOL_VERSION))
        result = recipes.get("dress_cover")(cplan, streams, coll)
        # place: orient by the anchor normal, then translate to its position.
        rot = _orient_matrix(order["normal"])
        trans = mathutils.Matrix.Translation(mathutils.Vector(order["pos"]))
        m = trans @ rot
        for obj in result["objects"]:
            obj.matrix_world = m @ obj.matrix_world
        # covers carry no collision boxes by contract -> no -colonly proxy.
        built += len(result["objects"])

    os.makedirs(out_dir, exist_ok=True)
    stem = f"{building_id}_dressing"
    base = os.path.join(out_dir, stem)
    export.export_glb(base + ".glb", coll)
    files = {"glb": f"{stem}.glb"}
    if opts["save_blend"]:
        export.save_blend(base + ".blend")
        files["blend"] = f"{stem}.blend"

    index = {
        "zoo": {"tool_version": TOOL_VERSION},
        "building_id": building_id,
        "theme": theme,
        "source": "patina-dressing/1",
        "trim_sheet": plan["trim_sheet"],
        "space": plan["space"],
        "collision": "none",
        "cover_count": plan["cover_count"],
        "counts": plan["counts"],
        "files": files,
    }
    index_file = f"{stem}.built.json"
    meta_mod.write_meta(os.path.join(out_dir, index_file), index)

    return {"building_id": building_id, "out_dir": out_dir, "theme": theme,
            "cover_count": plan["cover_count"], "counts": plan["counts"],
            "covers_built": built, "files": files, "index_file": index_file}


def build_habitat(theme: str, habitat: str, out_dir: str, seed: int = 0,
                  options: dict | None = None) -> dict:
    """Build a themed set of different species that share a look.

    The theme string is prepended to each species' prompt, so cohesion falls
    out of the normal parser. One specimen per species, plus a
    `<habitat_id>.habitat.json` index.
    """
    from ..core import habitat as habitat_mod

    known = genome_mod.list_species()
    species_list = habitat_mod.resolve_species(habitat, known)

    results, members = [], []
    for sp in species_list:
        r = build_specimen(habitat_mod.species_prompt(theme, sp), out_dir,
                           seed=seed, options=options)
        results.append(r)
        members.append({"species": sp, "specimen_id": r["specimen_id"],
                        "status": r["report"]["status"], "files": r["files"]})

    hid = habitat_mod.habitat_id(theme, species_list, seed, TOOL_VERSION)
    manifest = habitat_mod.build_habitat_manifest(
        TOOL_VERSION, hid, theme, species_list, seed, members)
    manifest_file = f"{hid}.habitat.json"
    meta_mod.write_meta(os.path.join(out_dir, manifest_file), manifest)

    n_fail = sum(1 for r in results if r["report"]["status"] == "fail")
    return {"habitat_id": hid, "out_dir": out_dir, "species": species_list,
            "manifest_file": manifest_file, "members": members,
            "n_fail": n_fail, "results": results}


def build_roof_props(slots_manifest: dict, out_dir: str, theme: str = "delco",
                     options: dict | None = None) -> dict:
    """Build rooftop prop species from a DC slots.json (v0.25).

    Plans the scatter with ``core.roofprops.scatter`` (pure, deterministic),
    then builds each placement with its normal species recipe, lifts it onto
    the roof slot's top surface, and exports a single
    ``<building>_roofprops.glb`` + ``.built.json`` index. Species with
    ``collision: true`` genomes get ``-colonly`` proxies (players walk roofs
    in a heist game; an HVAC unit is cover, not a hologram).
    """
    import json
    import mathutils

    from ..core import roofprops as roofprops_mod

    opts = dict(DEFAULT_OPTIONS)
    opts["clear_scene"] = True
    if options:
        opts.update(options)
    seed = int(opts.get("seed", 1999))

    plan = roofprops_mod.scatter(slots_manifest, seed,
                                 density=float(opts.get("density", 1.0)))
    building_id = plan["building_id"] or "building"

    if opts["clear_scene"]:
        clear_scene()
    coll = bpy.data.collections.new(f"{building_id}_roofprops")
    bpy.context.scene.collection.children.link(coll)

    built = 0
    for i, p in enumerate(plan["placements"]):
        species = p["species"]
        genome = genome_mod.load_species(species)
        intent = intent_mod.parse(species.replace("_", " "), seed=seed)
        streams = seeding.RNGStreams(seeding.root_key(
            f"{building_id}_roof_{i}", species, p["seed_offset"],
            TOOL_VERSION))
        sp_plan = dna.resolve_plan(intent, genome, streams, TOOL_VERSION)
        if theme in genome.get("styles", {}):
            style = genome["styles"][theme]
            sp_plan["style"] = theme
            sp_plan["material"] = style.get("material", sp_plan["material"])
            sp_plan["color"] = list(style.get("color", sp_plan["color"]))
            sp_plan["wear"] = style.get("wear", sp_plan["wear"])

        before = set(coll.objects)
        result = recipes.get(species)(sp_plan, streams, coll)
        if bool(genome.get("collision", True)) and result.get("collision_boxes"):
            collision.collision_from_boxes(
                species.title().replace("_", "") + str(i),
                result["collision_boxes"], coll)
        new_objs = [o for o in coll.objects if o not in before]

        # recipes build centered: lift by half the resolved height onto the
        # roof surface, spin by the scatter's rot_z, then translate.
        half_h = sp_plan["dimensions"]["height"] / 2.0
        rot = mathutils.Matrix.Rotation(
            __import__("math").radians(p["rot_z"]), 4, "Z")
        trans = mathutils.Matrix.Translation(mathutils.Vector(
            (p["pos"][0], p["pos"][1], p["pos"][2] + half_h)))
        m = trans @ rot
        for obj in new_objs:
            obj.matrix_world = m @ obj.matrix_world

        # Emitter marker (v0.30): an empty at the EMITTER point — the anchor
        # pos itself, NOT the lifted hardware centre — named by the LuxEmit
        # contract, payload in custom props (exported as glTF extras; Godot
        # imports them as node metadata). Lux spawns the lamp here.
        mk = bpy.data.objects.new(fixtures_mod.marker_name(p), None)
        mk.empty_display_type = "PLAIN_AXES"
        mk.empty_display_size = 0.15
        mk["lux_type"] = p["type"]
        mk["lux_anchor_id"] = p["anchor_id"]
        mk["lux_slot"] = p["slot"]
        mk["lux_reacts_to_alarm"] = p["reacts_to_alarm"]
        coll.objects.link(mk)
        mk.matrix_world = mathutils.Matrix.Translation(
            mathutils.Vector(p["pos"])) @ rot
        built += 1

    os.makedirs(out_dir, exist_ok=True)
    base = os.path.join(out_dir, f"{building_id}_roofprops")
    files = {"glb": f"{building_id}_roofprops.glb"}
    export.export_glb(base + ".glb", coll)
    if opts.get("save_blend"):
        files["blend"] = f"{building_id}_roofprops.blend"
        export.save_blend(base + ".blend")

    index = {"tool_version": TOOL_VERSION, "building_id": building_id,
             "theme": theme, "seed": seed, "space": plan["space"],
             "counts": plan["counts"], "props_built": built,
             "placements": plan["placements"], "files": files}
    index_file = base + ".built.json"
    with open(index_file, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return {"building_id": building_id, "theme": theme, "counts": plan["counts"],
            "props_built": built, "out_dir": out_dir, "files": files,
            "index_file": index_file}


def build_fixtures(lights_manifest: dict, out_dir: str, theme: str = "delco",
                   options: dict | None = None) -> dict:
    """Build physical light fixtures from a ``.lights.json`` (v0.28).

    The light-anchor pipeline's hardware leg: DC/Lot say where light comes
    from, Lux spawns the lamps — this bakes the fixtures the light appears
    to come from at the SAME anchors. Plans with ``core.fixtures.plan``
    (pure, deterministic; rows expand centered exactly like Lux's rigs),
    builds each lamp point with its species recipe, aligns it vertically by
    mount (``above``: bottom at the anchor — fluorescent housings fill DC's
    ceiling gap; ``below``: top at the anchor — streetlight poles stretch to
    grade), and exports one ``<scope>_fixtures.glb`` + ``.built.json``.
    Works on a per-building DC manifest or a Lot-merged site manifest.
    Species with ``collision: true`` genomes get ``-colonly`` proxies
    (players bump into poles; ceiling troffers stay collision-free).
    ``options['types']``: iterable of anchor types to build (default all).

    v0.30: every placement also exports a ``LuxEmit_<type>`` empty at the
    EMITTER point (anchor pos, no mount lift) carrying the placement payload
    as glTF extras — Lux's LuxFixtureSpawner spawns the matching lamp at
    each marker, so the GLB lights itself wherever it's instanced.
    """
    import json
    import math
    import mathutils

    from ..core import fixtures as fixtures_mod

    opts = dict(DEFAULT_OPTIONS)
    opts["clear_scene"] = True
    if options:
        opts.update(options)
    seed = int(opts.get("seed", 1999))

    plan = fixtures_mod.plan(lights_manifest, types=opts.get("types"))
    scope = plan["scope_id"]

    if opts["clear_scene"]:
        clear_scene()
    coll = bpy.data.collections.new(f"{scope}_fixtures")
    bpy.context.scene.collection.children.link(coll)

    built = 0
    for i, p in enumerate(plan["placements"]):
        species = p["species"]
        genome = genome_mod.load_species(species)
        intent = intent_mod.parse(species.replace("_", " "), seed=seed)
        streams = seeding.RNGStreams(seeding.root_key(
            f"{scope}_fixture_{i}", species, p["seed_offset"], TOOL_VERSION))
        sp_plan = dna.resolve_plan(intent, genome, streams, TOOL_VERSION)
        if theme in genome.get("styles", {}):
            style = genome["styles"][theme]
            sp_plan["style"] = theme
            sp_plan["style_block"] = dict(style)
            sp_plan["material"] = style.get("material", sp_plan["material"])
            sp_plan["color"] = list(style.get("color", sp_plan["color"]))
            sp_plan["wear"] = style.get("wear", sp_plan["wear"])
        if p["mount"] == "below":
            # Stretch to reach grade: pole top at the anchor, base at z=0.
            sp_plan["dimensions"]["height"] = fixtures_mod.pole_height_for(
                p["pos"][2], genome["dimensions"]["height"])
        if p.get("size"):
            # DC sized the panel (signs): width x height, clamped to genome.
            sp_plan["dimensions"]["width"] = fixtures_mod.clamp_dim(
                p["size"][0], genome["dimensions"]["width"])
            sp_plan["dimensions"]["height"] = fixtures_mod.clamp_dim(
                p["size"][1], genome["dimensions"]["height"])
        # Recipes with per-anchor resolution needs (sign pack picks) key on
        # the anchor id — stable across rebuilds, unique across the site.
        sp_plan["anchor_id"] = p["anchor_id"]

        before = set(coll.objects)
        result = recipes.get(species)(sp_plan, streams, coll)
        if bool(genome.get("collision", True)) and result.get("collision_boxes"):
            collision.collision_from_boxes(
                species.title().replace("_", "") + str(i),
                result["collision_boxes"], coll)
        new_objs = [o for o in coll.objects if o not in before]

        # Recipes build centered. Mount 'above': bottom (-h/2) at the anchor
        # -> lift +h/2. Mount 'below': top (+h/2) at the anchor -> drop -h/2.
        # Mount 'center': the anchor IS the centre (sign faces) -> no lift.
        half_h = sp_plan["dimensions"]["height"] / 2.0
        lift = {"above": half_h, "below": -half_h,
                "center": 0.0}[p["mount"]]
        rot = mathutils.Matrix.Rotation(math.radians(p["rot_z"]), 4, "Z")
        trans = mathutils.Matrix.Translation(mathutils.Vector(
            (p["pos"][0], p["pos"][1], p["pos"][2] + lift)))
        m = trans @ rot
        for obj in new_objs:
            obj.matrix_world = m @ obj.matrix_world

        # Emitter marker (v0.30): an empty at the EMITTER point — the anchor
        # pos itself, NOT the lifted hardware centre — named by the LuxEmit
        # contract, payload in custom props (exported as glTF extras; Godot
        # imports them as node metadata). Lux spawns the lamp here.
        mk = bpy.data.objects.new(fixtures_mod.marker_name(p), None)
        mk.empty_display_type = "PLAIN_AXES"
        mk.empty_display_size = 0.15
        mk["lux_type"] = p["type"]
        mk["lux_anchor_id"] = p["anchor_id"]
        mk["lux_slot"] = p["slot"]
        mk["lux_reacts_to_alarm"] = p["reacts_to_alarm"]
        coll.objects.link(mk)
        mk.matrix_world = mathutils.Matrix.Translation(
            mathutils.Vector(p["pos"])) @ rot
        built += 1

    os.makedirs(out_dir, exist_ok=True)
    base = os.path.join(out_dir, f"{scope}_fixtures")
    files = {"glb": f"{scope}_fixtures.glb"}
    export.export_glb(base + ".glb", coll)
    if opts.get("save_blend"):
        files["blend"] = f"{scope}_fixtures.blend"
        export.save_blend(base + ".blend")

    index = {"tool_version": TOOL_VERSION, "scope_id": scope,
             "theme": theme, "seed": seed, "space": plan["space"],
             "counts": plan["counts"], "fixtures_built": built,
             "emitter_markers": built,
             "marker_prefix": fixtures_mod.MARKER_PREFIX,
             "skipped": plan["skipped"], "placements": plan["placements"],
             "files": files}
    index_file = base + ".built.json"
    with open(index_file, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return {"scope_id": scope, "theme": theme, "counts": plan["counts"],
            "fixtures_built": built, "skipped": plan["skipped"],
            "out_dir": out_dir, "files": files, "index_file": index_file}
