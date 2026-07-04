"""Optional LOD generation via a temporary Decimate modifier (no ops)."""
from __future__ import annotations

import bpy


def make_lods(obj, collection, ratios=(0.5, 0.25)):
    lods = []
    deps = bpy.context.evaluated_depsgraph_get()
    for i, ratio in enumerate(ratios, start=1):
        mod = obj.modifiers.new("ZooDecimate", "DECIMATE")
        mod.ratio = ratio
        deps.update()
        eval_obj = obj.evaluated_get(deps)
        mesh = bpy.data.meshes.new_from_object(eval_obj)
        obj.modifiers.remove(mod)
        lod = bpy.data.objects.new(f"{obj.name}_LOD{i}", mesh)
        collection.objects.link(lod)
        lods.append(lod)
    return lods
