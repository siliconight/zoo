"""A GLB may not claim GPU instancing, because this engine deletes it.

`pennant_row` was nominated as the first customer for CLAUDE.md's "MultiMesh
the large repeated sets" rule. It cannot be, and the reason is not a Zoo
decision: **Godot 4.7 does not implement `EXT_mesh_gpu_instancing`**, and it
does not implement it SILENTLY. Measured 2026-09-21, Blender 5.1.1 exporter
against Godot 4.7-stable-win64, three instances of one triangle:

    the GLB        extensionsUsed ['EXT_mesh_gpu_instancing'], one node
                   "Row", 3 instances, TRANSLATION/ROTATION/SCALE
    runtime        GLTFDocument.append_from_file -> MeshInstance3D,
                   1 surface, 3 verts, 1 triangle
    editor         load("res://probe.glb") -> the same
    the binary     the string "EXT_mesh_gpu_instancing" does not occur in
                   the engine executable; of the 267 EXT_/KHR_ names in it
                   the glTF ones are KHR_lights_punctual,
                   KHR_materials_{emissive_strength,pbr*,unlit},
                   KHR_texture_{transform,basisu}, KHR_animation_pointer
                   and KHR_node_visibility

The instancing node keeps its mesh and loses its instance table, so N-1
instances stop existing with no error and no warning. On a pennant row that
is 43 of 44 pennants deleted from a file that still validates, still opens,
and still reports a sensible triangle count in every census this repo owns.

THAT IS THE RULE THIS FILE HOLDS. Not "do not use the flag" as a style
preference -- `export_gpu_instances` is a data-loss switch on this engine,
and the loss is invisible to every instrument that reads the GLB rather than
the scene Godot built from it.

THE POSITIVE CONTROL IS PART OF THE RULE, because a test that only ever
asserts an absence cannot tell "Zoo does not emit this" from "the probe
cannot see it". `test_the_exporter_emits_the_extension_when_it_is_asked_to`
is that control: it proves the same instrument, on the same Blender, DOES
report instancing when instancing is there. Without it the rest of this file
would pass just as happily against a census that always returned False.

WHERE THE CAPABILITY ACTUALLY LIVES, so nobody re-derives this: a MultiMesh
reaches Godot in this factory as `.tscn` TEXT, written by
`level_factory/packages/exporting/dressing_scene.py` (a `[sub_resource
type="MultiMesh"]` block with a `PackedFloat32Array` buffer), fed by meshes
that `level_factory/assets/godot/extract_meshes.gd` pulls out of Zoo's GLBs
into `.res` files. Zoo's output is the mesh; the instancing is the composer's
to do. Per USING_THE_FACTORY.md's gap protocol that makes instanced pennants
a Level Factory capability, not a Zoo one.
"""
from __future__ import annotations

import os
import tempfile

import pytest

from tools import instancing_probe


# --- the pure half: the census counts submissions the way a frame pays -----

def test_a_shared_mesh_costs_one_submission_per_node():
    """Three nodes pointing at one mesh are three draw calls, not one.

    This is the trap the whole question sits on. A census that counted
    `meshes` would report 1 for the flat three-node file and read like
    instancing had worked, on a file carrying no instancing at all.
    """
    doc = {
        "nodes": [{"name": "A", "mesh": 0}, {"name": "B", "mesh": 0},
                  {"name": "C", "mesh": 0}],
        "meshes": [{"primitives": [{"indices": 0, "material": 0}]}],
        "accessors": [{"count": 3}],
        "materials": [{"name": "M_One"}],
    }
    got = instancing_probe.census(doc)
    assert got["mesh_defs"] == 1
    assert got["mesh_nodes"] == 3
    assert got["submissions"] == 3
    assert got["materials"] == 1


def test_the_census_reports_an_instanced_node_and_its_count():
    doc = {
        "extensionsUsed": [instancing_probe.EXT],
        "nodes": [{"name": "Row", "mesh": 0, "extensions": {
            instancing_probe.EXT: {"attributes": {"TRANSLATION": 1}}}}],
        "meshes": [{"primitives": [{"indices": 0}]}],
        "accessors": [{"count": 3}, {"count": 44}],
    }
    got = instancing_probe.census(doc)
    assert got["claims_instancing"] is True
    assert got["instanced_nodes"] == [
        {"node": "Row", "instances": 44, "attributes": ["TRANSLATION"]}]


def test_a_file_without_the_extension_is_not_reported_as_instanced():
    doc = {"nodes": [{"name": "A", "mesh": 0}],
           "meshes": [{"primitives": [{"indices": 0}]}],
           "accessors": [{"count": 3}]}
    got = instancing_probe.census(doc)
    assert got["claims_instancing"] is False
    assert got["instanced_nodes"] == []


# --- the built half -------------------------------------------------------

def _probe_glb(flat):
    d = tempfile.mkdtemp()
    path = os.path.join(d, "probe.glb")
    instancing_probe._write(path, not flat, 3)
    return instancing_probe.census(instancing_probe.read_glb(path))


def test_the_exporter_emits_the_extension_when_it_is_asked_to():
    """THE POSITIVE CONTROL. Proves this instrument, on this Blender, can
    see GPU instancing -- so the absences asserted below are findings about
    the files and not about a probe that never answers yes.

    It also pins the shape of the thing: Blender writes the extension ONTO
    THE PARENT and collapses the children into it, so the exported file is
    one node and one triangle where the scene had three of each.
    """
    pytest.importorskip("bpy")
    got = _probe_glb(flat=False)
    assert got["claims_instancing"] is True
    assert got["instanced_nodes"][0]["instances"] == 3
    assert got["mesh_nodes"] == 1
    assert got["triangles"] == 1


def test_without_a_shared_parent_the_flag_does_nothing():
    """The control's control. Flat siblings sharing one mesh -- the obvious
    way to author a row of pennants -- export as N ordinary nodes with the
    flag set, so "I turned instancing on" is not evidence that a file has
    it, and `claims_instancing` is the only thing that answers the question.
    """
    pytest.importorskip("bpy")
    got = _probe_glb(flat=True)
    assert got["claims_instancing"] is False
    assert got["mesh_nodes"] == 3
    assert got["submissions"] == 3


def test_zoo_s_own_export_never_claims_gpu_instancing():
    """The rule, on the built article. `pennant_row` is the module that
    would have carried it, so it is the one asked.

    A module that claimed instancing would reach a level with all but one
    of its repeated parts missing, and every count in this repo would keep
    reporting the file it shipped rather than the scene Godot made of it.
    """
    pytest.importorskip("bpy")
    import glob

    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import kit

    module = {"building_id": "t", "slots": [{
        "slot_id": "s0", "role": "prop", "size_mod": "full", "style": 13,
        "species": "pennant_row",
        "fit": {"dims": [4.0, 0.08, 0.3], "pivot": "center",
                "collision": False}}]}
    plan = kit.plan_kit(module, theme="delco", style=13)
    with tempfile.TemporaryDirectory() as d:
        build.build_module(plan["modules"][0], d, theme="delco", style=13,
                           options={"save_blend": False, "merge_parts": True})
        found = glob.glob(os.path.join(d, "**", "*.glb"), recursive=True)
        assert found, "the build wrote no GLB to assert against"
        for path in found:
            got = instancing_probe.census(instancing_probe.read_glb(path))
            assert got["claims_instancing"] is False, (
                "%s claims %s, which Godot 4.7 discards along with every "
                "instance after the first" % (os.path.basename(path),
                                              instancing_probe.EXT))
            assert got["instanced_nodes"] == []
