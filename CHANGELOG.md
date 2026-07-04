# Changelog

## [0.5.0]
### Added - Phase 3: Godot importer (editor plugin)
- New Godot 4.x editor plugin godot/addons/zoo_importer/: a dock that reads a
  .family.json or .habitat.json manifest and instances every member GLB into
  the open scene, laid out in a grid under one container node.
- Relies on Godot's native glTF import for -colonly collision and ATT_*
  markers; the plugin only resolves + places the pieces.
- Install: copy godot/addons/zoo_importer into res://addons/ and enable it.
- NOTE: GDScript, not exercisable in the Python test suite — first run in
  Godot 4.7 is the real smoke test.

## [0.4.0]
### Added - filing cabinet species (6th species)
- New species `filing_cabinet`: a 2-5 drawer vertical file (body box, stacked
  proud drawer fronts with bar pulls, recessed kick base). Reuses the desk's
  drawer/handle construction. Metal/office styling, ATT_top_center marker.
- Parser keywords: "filing cabinet", "file cabinet", "filing", "cabinet".
- Added to the `office` habitat (desk + chair + filing_cabinet) and `starter`.
- New genome + recipe + 4 tests (41 total).

## [0.3.1]
- Collision now exports as `-colonly` (was `-col`): Godot imports it as a
  static collision shape with NO visible mesh, so the proxy no longer renders
  over the asset in-game. Export/validation detect any Godot collision suffix.
- Helmet brim now triggers for police / bobby / peaked / trooper / ranger
  helmets (and "brim"/"cap"), not only hard hats. Motorcycle stays brimless.

## [0.3.0]
### Added - Phase 2: habitats
- Habitat batch: build a themed set of different species that share a look.
  The theme string is prepended to each species' prompt, so era/palette/
  material cohesion falls out of the normal parser - no shared-state plumbing.
- Named sets (starter = all five, office = desk+chair, gear = helmet+boots)
  or a comma list (desk,chair). `<habitat_id>.habitat.json` indexes members.
- CLI `--habitat NAME` (build) and `--habitat NAME --plan` (preview, no
  Blender). Keeper panel gains a Habitat field + Generate Habitat button.
- New pure-core module zoo_keeper/core/habitat.py; 7 new tests (36 total).

## [0.2.0]
### Added - Phase 2: variant families
- Variant generation: one prompt built across seeds base..base+N-1 as a
  cohesive family. Style, material and palette are shared (seed-independent);
  dimensions and wear vary per sibling. Each variant is a full specimen and
  reproducible standalone with --seed.
- `<family_id>.family.json` manifest indexes every sibling (shared look +
  per-specimen seed/id/dimensions/status/files). Timestamp-free/deterministic.
- CLI `--count N` (build) and `--count N --plan` (preview the family without
  building). Keeper panel gains a Variants count + Generate Variants button.
- New pure-core module zoo_keeper/core/variants.py; 5 new tests (29 total).

## [0.1.3]
- Boots validation FAIL fixed. The validator now scales genome dimension
  ranges by a per-axis plan `dim_scale`, so a mirrored pair validates
  against its true footprint (~2.3x boot width) while the genome stays
  honest about a single boot.
- Widened boots genome height to [0.18, 0.50] m so its own "tall" combat
  shaft is in range; DNA now writes the real sole+foot+shaft height back
  into the plan (meta.json no longer under-reports boot height).
- Boot construction constants (shaft/sole/foot/gap) live once in the DNA
  layer and travel in the plan; the recipe executes them verbatim.

## [0.1.2]
- Fixed UV projection crash on first real Blender run: BMLoopUV coords
  must be written via loop[uv].uv, not slice assignment (TypeError:
  'BMLoopUV' object does not support item assignment).

## [0.1.1]
- simple_car: added windshield, rear and side window panes (Car_Windows)
  with tinted glass material — TDD required part / acceptance criterion.
- Added "glass" to the material property table and simple_car genome.

## [0.1.0]
### Added — Starter Habitat MVP
- Rule-based offline prompt parser -> Asset Intent Spec (species, era,
  style tags, material, color, wear, size hint, counted parts; number
  words and digits; unknowns fall back to genome defaults).
- Genome layer: five species JSONs (desk, chair, helmet, boots,
  simple_car) with dimension ranges, params, era/style blocks, tri
  budgets, attachment lists, and CC0 construction-knowledge license
  metadata.
- DNA plan resolver: deterministic BuildPlan from intent + genome via
  SHA256-derived named RNG streams (seed + version stable).
- bpy geometry layer: bmesh-only recipes (no context-dependent ops),
  deterministic cube-projection UVs, concavity + seeded-noise vertex wear
  ("Wear" COLOR_0), edge bevels, glTF-safe flat Principled materials.
- Godot conventions: `-col` collision siblings, `ATT_*` attachment
  empties, optional `_LOD1/_LOD2` decimated LODs, meters, Y-up export.
- Validation report (dims/tris/UVs/materials/parts/collision/transforms)
  with PASS/WARN/FAIL, printed and embedded in the timestamp-free
  `meta.json` sidecar alongside `.glb` and optional `.blend`.
- Keeper panel (3D Viewport > N > Zoo) and dual-mode headless CLI
  (`tools/zoo_cli.py`): full build inside Blender, `--plan` dry run under
  plain Python.
- 22 pytest unit tests over the pure core, including the Build 0.1
  acceptance prompt "1990s office desk with two drawers".
