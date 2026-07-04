"""Zoo Keeper — offline procedural game asset compiler for Blender.

Plain-text prompt -> Asset Intent Spec -> Genome -> DNA BuildPlan ->
validated Blender asset -> Godot-ready GLB + .blend + meta.json.

Tooled procedural construction, NOT AI mesh generation. No cloud, no
scraping, no copyrighted source meshes.
"""

TOOL_VERSION = "0.5.0"

bl_info = {
    "name": "Zoo Keeper",
    "author": "GabagoolStudios",
    "version": (0, 5, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar (N) > Zoo",
    "description": "Prompt-driven offline procedural asset compiler "
                   "(Godot-ready GLB output)",
    "category": "Add Mesh",
}

try:
    import bpy  # noqa: F401
    _HAS_BPY = True
except ImportError:  # pure-python test / CLI dry-run context
    _HAS_BPY = False


def register():
    if not _HAS_BPY:
        return
    from .ui import panel
    panel.register()


def unregister():
    if not _HAS_BPY:
        return
    from .ui import panel
    panel.unregister()
