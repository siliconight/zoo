"""Attachment markers: empties exported as glTF nodes for wearables,
mount points, and gameplay anchors (ATT_* naming)."""
from __future__ import annotations

import bpy


def add_marker(name, location, collection, size=0.08):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = size
    empty.location = location
    collection.objects.link(empty)
    return empty
