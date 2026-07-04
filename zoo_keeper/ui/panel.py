"""Keeper: the in-Blender UI. Sidebar (N) > Zoo tab."""
from __future__ import annotations

import os

import bpy

from ..core import validate


class ZooProps(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty(
        name="Prompt", default="1990s office desk with two drawers")
    seed: bpy.props.IntProperty(name="Seed", default=0, min=0)
    collision: bpy.props.BoolProperty(name="Collision (-col)", default=True)
    lods: bpy.props.BoolProperty(name="LODs", default=False)
    save_blend: bpy.props.BoolProperty(name="Save .blend", default=False)
    out_dir: bpy.props.StringProperty(
        name="Output", subtype="DIR_PATH", default="//exhibits/")
    last_status: bpy.props.StringProperty(default="")


class ZOO_OT_generate(bpy.types.Operator):
    bl_idname = "zoo.generate_specimen"
    bl_label = "Generate Specimen"
    bl_description = "Compile the prompt into a validated, exported asset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from ..bpylayer import build
        p = context.scene.zoo_keeper
        out_dir = bpy.path.abspath(p.out_dir) or os.getcwd()
        try:
            result = build.build_specimen(
                p.prompt, out_dir, seed=p.seed,
                options={"collision": p.collision, "lods": p.lods,
                         "save_blend": p.save_blend,
                         "clear_scene": False})
        except Exception as exc:  # surface, don't crash the UI
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        status = result["report"]["status"].upper()
        p.last_status = f"{result['specimen_id']}: {status}"
        level = {"PASS": "INFO", "WARN": "WARNING"}.get(status, "ERROR")
        self.report({level}, validate.summarize(result["report"]))
        return {"FINISHED"}


class VIEW3D_PT_zoo_keeper(bpy.types.Panel):
    bl_label = "Zoo Keeper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Zoo"

    def draw(self, context):
        p = context.scene.zoo_keeper
        col = self.layout.column()
        col.prop(p, "prompt")
        col.prop(p, "seed")
        row = col.row()
        row.prop(p, "collision")
        row.prop(p, "lods")
        col.prop(p, "save_blend")
        col.prop(p, "out_dir")
        col.operator("zoo.generate_specimen", icon="MESH_MONKEY")
        if p.last_status:
            col.label(text=p.last_status)


_CLASSES = (ZooProps, ZOO_OT_generate, VIEW3D_PT_zoo_keeper)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.zoo_keeper = bpy.props.PointerProperty(type=ZooProps)


def unregister():
    del bpy.types.Scene.zoo_keeper
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
