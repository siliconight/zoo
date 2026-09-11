"""Zoo Keeper — offline procedural game asset compiler for Blender.

Plain-text prompt -> Asset Intent Spec -> Genome -> DNA BuildPlan ->
validated Blender asset -> Godot-ready GLB + .blend + meta.json.

Tooled procedural construction, NOT AI mesh generation. No cloud, no
scraping, no copyrighted source meshes.
"""

import os as _os

#: THE SEED INPUT, FROZEN. `seeding.root_key`, `habitat.habitat_id` and
#: `variants.family_id` fold a version string into every specimen's root key,
#: so the string decides every asset's geometry. Until 2026-09-11 that string
#: was TOOL_VERSION, which had been the literal "0.31.0" since July while the
#: tool went to 0.58.0 -- so every index stamped a version 27 releases stale,
#: and correcting the stamp would have re-rolled every asset (roadmap 136).
#: The two meanings are split: this is the one the seeds read, and it does
#: not move when the tool does. Change it only to re-roll the library on
#: purpose, and say so in the changelog.
SEED_EPOCH = "0.31.0"


def _read_tool_version() -> str:
    """The version the STAMPS carry: `VERSION` at the repo root ("Zoo 0.58.0"
    -> "0.58.0"). Read at import so `zoo.tool_version` in every index and
    meta.json is the tool that wrote it, which is what a reader comparing an
    artifact to a checkout needs. Falls back to the frozen epoch only when the
    file is not there (a vendored copy without the repo root)."""
    here = _os.path.dirname(_os.path.abspath(__file__))
    try:
        with open(_os.path.join(here, "..", "VERSION"), encoding="utf-8") as fh:
            text = fh.read().strip()
    except OSError:
        return SEED_EPOCH
    return text.split()[-1] if text else SEED_EPOCH


TOOL_VERSION = _read_tool_version()

bl_info = {
    "name": "Zoo Keeper",
    "author": "GabagoolStudios",
    "version": (0, 20, 0),
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
