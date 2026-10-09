"""Attachment markers: empties exported as glTF nodes for wearables,
mount points, and gameplay anchors (ATT_* naming), and Lux's emitter markers
(`LuxEmit_*`) where a recipe stands its own lamp."""
from __future__ import annotations

import bpy


def add_marker(name, location, collection, size=0.08, props=None):
    """An empty at ``location``. ``props`` (1.89.0) become its custom
    properties, which the glTF export writes as the node's ``extras``
    (`export._export_selection`, ``export_extras=True``) and Godot imports as
    its ``extras`` metadata -- where `LuxFixtureSpawner.marker_payload` reads a
    lamp's ``lux_type`` and ``lux_drop``. `build.build_fixtures` stamps its
    markers the same way."""
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = size
    empty.location = location
    for key, value in (props or {}).items():
        empty[key] = value
    collection.objects.link(empty)
    return empty
