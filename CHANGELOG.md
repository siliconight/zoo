# Changelog

## [0.10.0] - Ingest: adopt external assets
### Added - Zoo can now condition assets it didn't generate
- New ingest pipeline: take a random external asset (or a .zip of them, e.g.
  an itch.io pack), normalize it to Zoo's standard (pivot bottom-center on
  Z=0, applied transforms, optional scale-to-size, optional bbox collision),
  and export a Godot-ready GLB + provenance meta.json — same output shape as a
  generated specimen, so the importer treats them identically.
- Pure core (core/ingest.py, tested): archive scan, target-height resolution
  (explicit or from a species' genome), provenance meta, name cleaning.
- Blender side (bpylayer/ingest.py): import glb/gltf/fbx/obj/dae/stl/ply,
  normalize, export. WRITE-BLIND — needs a Blender test pass.
- CLI: --ingest <file|zip> [--list | --pick <inner>] [--as-species X |
  --target-height M] [--as-name N] [--license "..."]. Inventory works without
  Blender. Zoo records provenance but grants no rights.
- 6 new tests (67 total).

## [0.9.0] - Phase 4: Knowledge Packs
### Changed - species are now self-describing (add one with no engine edits)
- Keywords moved from a hardcoded table in intent.py into each genome
  ("keywords"); the parser reads them from the genomes. Tie-break is now
  position-then-keyword-length ("soda machine" beats "soda", "cash machine"
  beats "cash"), with an optional "match_priority".
- Keyword-driven hooks (desk/chair/helmet/simple_car/condiment_bottle) moved
  from Python into declarative genome "prompt_rules" (any-word -> set
  color/material/style/params.x). Only computed hooks (boots, cash_stack
  derived dimensions) remain as code.
- Recipe registry auto-discovers modules by filename via importlib (no more
  hardcoded if/elif chain). Dropping recipes/<name>.py registers it.
- Net: adding a species = drop a genome JSON + a recipe module. 61 tests.

## [0.8.5]
- Cheesesteak simplified for a cleaner low-poly read (fewer + bigger beats
  many + small): filling is now ONE lumpy jittered meat mound instead of a
  12-chunk scatter, ONE draped cheese sheet instead of two, and the sesame
  seeds are a small set PROJECTED onto the crust surface (analytic ellipsoid
  skin) so none float. Dropped the noisy onion bits. ~600 tris (was 3400);
  budget 1500. Open seeded-roll silhouette kept.
- Establishes the low-poly hero pattern: spend geometry on silhouette, use
  single jittered forms over scatter-of-many, keep tiny detail flush/minimal.

## [0.8.4]
- Cheesesteak reworked toward the real Philly reference: it's now an OPEN
  seeded hoagie. The roll is a bottom + two crust walls forming a channel; the
  meat pile is cradled low in the groove with cheese draped over it; and
  sesame seeds are scattered across the crust (Steak_Seeds). Warmer golden
  crust color. Reads as a split seeded roll, not a blob with toppings.

## [0.8.3]
- Look pass on the two food heroes after first Godot view: toppings were
  stacking into a floating tower instead of nestling. french_fries: shallower
  wider 6-sided boat, pile pulled down and compacted (layer_rise 0.004->0.0025,
  base 0.85->0.6). cheesesteak: meat mound nestled into the roll and compacted
  (layer_rise w*0.05->w*0.018, base lowered), cheese dropped onto the meat,
  onions lowered. No floating filling.

## [0.8.2]
- Fixed the two habitat-build validation FAILs (same protruding-part class as
  boots/soda-cup): flat_top_grill splash guards rose above the declared height
  (restructured so guards define the top and the cooktop sits at counter
  height; height range now overall 0.98-1.15m); french_fries pile stacked
  ~12cm over the boat (tamed the mound and widened the genome footprint).

## [0.8.1]
- Fixed soda_cup validation FAIL from the first Blender run: the straw
  protruded 18cm so the specimen measured 0.34m vs the cup-only height range.
  Trimmed the straw to a realistic ~8cm and widened height to [0.12, 0.32] to
  honestly include it.
- Verified in Blender: the 0.7.0 low-poly toolkit works — cheesesteak (ellipsoid
  + jitter + scatter) PASSED; soda_cup builds clean.

## [0.8.0]
### Added - cheesesteak-shop kitchen batch (17 species)
- flat_top_grill: steel cabinet, cooktop, splash guards, grease trap, knobs,
  legs (hard-surface, proven primitives).
- condiment_bottle: tapered squeeze bottle + cap + nozzle; DNA hook colors it
  by flavor (ketchup/mustard/mayo/hot sauce/oil from the prompt).
- french_fries: paper boat + scattered jittered fry sticks (scatter showcase;
  pickup, no collision).
- New cheesesteak_shop habitat (grill + table + cheesesteak + fries +
  condiment + soda). 4 new tests (56 total).

## [0.7.0]
### Added - low-poly (PS1/N64) hero capability
- New geometry primitives for chunky organic form: add_ellipsoid (faceted
  blobs), jitter_verts (deterministic per-vertex irregularity), cylinder
  radius_top (cones/cups), and geometry.place. New pure core.scatter for
  deterministic 'pile' placement (one chunk -> duplicate -> randomize -> join).
- Two new hero species (14 total): cheesesteak (flagship - jittered roll +
  scattered meat pile + draped cheese + onions, ~2k tris) and soda_cup
  (tapered cup, lid, straw). Both default to no collision (pickups).
- New 'diner' habitat (table + chair + cheesesteak + soda_cup).
- 6 new tests (52 total). Sculpted high-detail heroes still out of scope.

## [0.6.1]
- Collision is now per-species and tri-state. Genomes can declare a collision
  default; the build resolves explicit flag > genome default > on. cash_stack
  defaults to OFF (loot/pickup). CLI gains `--collision` alongside
  `--no-collision`; with neither, the genome default is used. Keeper panel's
  Collision control is now Auto / On / Off.

## [0.6.0]
### Added - heist prop pack (6 species, 12 total)
- Six new hard-surface species for a 1990s Philly/Delco heist setting:
  table, crt_tv (tube TV), atm, vending_machine, briefcase, cash_stack
  (banded bill straps; count with "N stacks of cash").
- Two new habitats: `corner_store` (vending_machine + atm + table + crt_tv)
  and `score` (briefcase + cash_stack + atm).
- New "paper" material; cash_stack DNA hook writes real stack height to plan.
- 4 new tests (45 total). Cheesesteak / chip-bag deliberately NOT added:
  soft organic forms unsuited to the procedural box/cylinder toolkit.

## [0.5.2]
- Zoo Importer: human-readable names in the scene tree. Instances are named by
  species ("Desk", "Chair", "Filing Cabinet") instead of the specimen hash;
  the hash is kept in node metadata (zoo_specimen_id) for traceability. The
  container is named from the theme/prompt ("Zoo 1990s Office"). Names are set
  after add_child (reliable Godot idiom). Plugin-only — no GLB rebuild.

## [0.5.1]
- Zoo Importer: footprint-aware layout. Instances are now packed edge-to-edge
  in rows using each asset's real AABB (wrapping past ~8 m), so nothing spawns
  on top of anything else regardless of size. The spacing control is now a
  gap-between-assets (default 0.5 m). Plugin-only change — no need to rebuild
  GLBs; re-copy the plugin and re-import.

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
