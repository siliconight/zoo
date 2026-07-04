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
    "collision": True,
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
