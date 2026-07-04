"""Collision meshes using Godot's import-time naming convention.

A sibling mesh named '<Root>-colonly' becomes a static collision shape on
Godot glTF import and the visual mesh is discarded — so the proxy provides
collision without rendering in-game. Zero manual cleanup.
"""
from __future__ import annotations

import bmesh
import bpy

from . import geometry


def collision_from_boxes(root_name, boxes, collection):
    """boxes: list of ((min_xyz), (max_xyz)) tuples in meters."""
    bm = bmesh.new()
    for lo, hi in boxes:
        center = tuple((a + b) / 2 for a, b in zip(lo, hi))
        size = tuple(max(0.01, b - a) for a, b in zip(lo, hi))
        geometry.add_box(bm, center, size)
    obj = geometry.bm_to_object(bm, f"{root_name}-colonly", collection,
                                finish=False)
    obj.display_type = "WIRE"
    obj.hide_render = True
    return obj
