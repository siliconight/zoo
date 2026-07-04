"""Specimen build orchestrator.

prompt -> Intent -> Genome -> BuildPlan -> recipe geometry -> collision /
markers / optional LODs -> validation -> GLB + .blend + meta.json.
"""
from __future__ import annotations

import os

import bpy

from .. import TOOL_VERSION
from ..core import dna, genome as genome_mod, intent as intent_mod
from ..core import meta as meta_mod, seeding, validate
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
