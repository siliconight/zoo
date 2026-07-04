# Zoo Importer (Godot 4.x plugin)

Phase 3 — the Godot side of Zoo. Reads the `.family.json` / `.habitat.json`
manifests the Blender tool emits and instances the referenced GLBs into the
open scene. Collision (`-colonly`) and attachment (`ATT_*`) nodes come in
through Godot's native glTF import, so this plugin only places the pieces.

## Install

1. Copy `godot/addons/zoo_importer/` into your Godot project's `addons/`
   folder (so it lives at `res://addons/zoo_importer/`).
2. Project > Project Settings > Plugins > enable **Zoo Importer**.
3. A **Zoo** dock appears (bottom-right by default).

## Use

1. Copy a family/habitat build into your project — the `.glb` files **and**
   the `.family.json` / `.habitat.json` manifest — e.g. into `res://models/`.
2. Open a 3D scene.
3. In the Zoo dock, **Browse** to the manifest, set a grid spacing, and hit
   **Import into scene**.

Every member is instanced under one container node (`ZooFamily_*` /
`ZooHabitat_*`), laid out in a grid. Each instance keeps its `-colonly`
collision and `ATT_*` markers from import.

> The manifest and its GLBs must sit in the same folder inside the project —
> the importer resolves each GLB relative to the manifest's location.

## Status

New in Zoo 0.5.0 and not yet hardened against every Godot edge case — if the
dock errors, grab the message from the Output/Debugger panel and iterate.
