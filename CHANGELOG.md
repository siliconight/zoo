# Changelog

## [0.18.0] - teller_line: bank teller window (counter + bulletproof glass)
### Added
- New `teller_line` species (24 total: 17 props + 7 architectural modules). An
  interactive architectural module, center-pivot + fit-to-exact-dims: a solid
  COUNTER base (floor to waist) + two side POSTS and a HEADER framing the
  opening above it + a bulletproof GLASS barrier filling that opening with a
  central transaction PASS-SLOT (money slides through -> no collision there).
  The counter, frame and glass all block, so an intact teller line is a barrier.
  The counter + frame tile the exact (w, d, h) box; the glass sits inside, so
  fit-to-exact-dims holds (~84 tris). Glass panels reuse `arch.slab_parts` to
  frame the pass-slot. Plain structural pass; the tray, speaker grille, signage
  and cash drawer are a Delco art pass.
- Builds only the intact state. A teller slot's `shattered` state reuses this
  same species art, so Zoo defers it and the resolver falls back to the intact
  base until a shattered-glass art pass gives it distinct geometry (same deal as
  a broken window or unlocked vault). `collision_per_state` still tells the game
  intact blocks / shattered is passable.
- 3 new tests (127 total).
### Next
- `safe_deposit_boxes` (the vault box wall, locked/drilled), plus bank props
  (security_camera, queue_stanchion, drop_safe, gold_bar).
- Deli Counter: a `teller` opening kind so a bank spec emits teller_line slots +
  the interactive fixture (states intact/shattered), same as the vault kind.
- Delco art pass: shattered-glass variant, tray/grille/signage on the counter.

## [0.17.0] - vault_door: the first bank module (interactive hero portal)
### Added
- New `vault_door` species (23 total: 17 props + 6 architectural modules). An
  interactive architectural module: center-pivot, fit-to-exact-dims like the
  other modules, but its closed form is a heavy
  portal FRAME (thick jambs + header + a raised threshold lip) + a thick armored
  LEAF filling the opening + a wheel HUB (~120 tris). The frame defines the exact
  outer box; the leaf + hub sit inside, so fit-to-exact-dims holds at every size.
  Plain structural pass (armored metal); the wheel spokes / bolt work / branded
  face are a Delco art pass.
- The species builds ONLY the closed (locked/unlocked) door. Its other states
  come from the slot's interactive.state_geometry (INTERACTIVES.md): map
  `open -> doorway` (leaf gone, a passage) and `breached -> breach` (blown), and
  `unlocked` is identical art to `locked` today so the resolver falls back to
  the base. So a vault-door slot with
  `state_geometry {locked: vault_door, unlocked: vault_door, open: doorway,
  breached: breach}` builds `vault_door_<theme>_01_w140` (closed) +
  `..._open` (doorway geom) + `..._breached` (breach geom) at the vault's dims.
- core/arch.py: a `vault_door` void (heavy frame + threshold lip). 5 new tests
  (124 total).
### Next
- The rest of the bank vocabulary: teller_line (counter + bulletproof glass,
  intact/shattered), safe_deposit_boxes (locked/drilled), plus props
  (security_camera, queue_stanchion, drop_safe, gold_bar).
- Deli Counter: a `vault` opening kind so a bank spec emits vault_door slots +
  the interactive fixture (today it needs an authored interactive override).
- Delco art pass on the vault face (wheel, bolts, signage).

## [0.16.0] - Interactive fixtures: networked doors + breachable walls
### Added - state-machine art variants, network-solution-agnostic
- INTERACTIVES.md: the shared contract (copy into deli-counter too). An
  interactive fixture (door, breachable wall) is a replicable state machine
  `(stable_id, states[], default, transitions[])` - the ENTIRE networked
  surface. It describes STATE, never synchronization, so it maps onto any
  solution (server snapshot / event-RPC / lockstep / rollback) without
  committing. State lives in gameplay.json (netcode-owned); art variants live
  in art/zoo (the `_<state>` naming law); ownership stays on the existing art
  vs gameplay line. Stable ids must NOT be array-index (re-greybox would
  renumber and break references); advisory hints (authority/persist/reversible)
  are never instructions; mid-states + continuous motion are handled by the
  state set, not by adding networking concepts.
- kit.plan_kit reads each slot's `interactive` block and expands it: default
  state -> base module; each non-default state whose geometry DIFFERS ->
  a `_<state>` variant, built with its `state_geometry` species at the slot's
  exact dims; same-geometry states -> deferred_variants (resolver falls back to
  base, so the art pass stays progressive). kit.slot_variants (pure) is the
  expansion. Modules now carry `species` (geometry built) distinct from `type`
  (the slot's base type, which drives the filename) + `state`.
- This makes a breachable wall the `breached` STATE of a wall slot:
  `state_geometry {"intact":"wall","breached":"breach"}` builds
  `wall_..._w200` (wall) + `wall_..._w200_breached` (breach geometry at the
  wall's dims) - not a standalone module.
- build.build_module builds by the state's geometry species; build_kit records
  species/state per module + the deferred list in <building>_kit.built.json.
  CLI --kit / --build-kit show state variants and deferrals.
- breach genome height envelope widened to 4.5m (a breached wall inherits the
  wall's height).
- 8 new tests (119 total).
### Next
- Deli Counter: assign stable interactive ids + emit the two blocks.
- Delco art direction per state (door leaf for `closed`, blown/rebar breach) -
  which turns today's deferred same-geometry states into real variants.

## [0.15.0] - Architectural module species: a planned kit becomes real GLBs
### Added - the five wall-slot modules Deli Counter swaps in
- 5 new species (genome + recipe): wall, wallEnd, doorway, window, breach.
  These are a *different kind* of species from Zoo's props - they dress a Deli
  Counter greybox's wall slots, so they follow two extra rules:
  - CENTER pivot (not bottom-center): geometry is centered on the origin in all
    axes, so DC drops a module onto a slot transform with no conversion.
  - fit-to-EXACT-dims (not sampled): built at the slot's authored w/d/h; DC
    instances at that size and NEVER scales it.
- core/arch.py (pure, tested): decomposes a center-pivot slab into axis-aligned
  boxes around an optional passable void. Guarantees the union's outer bbox
  equals (w, d, h) exactly - jambs always reach +/-w/2 at full height and every
  box spans full depth - so exact-fit validation passes by construction. A
  doorway/breach is a hole to the floor (jambs + lintel, no sill); a window is a
  mid-height opening (jambs + sill + header) plus a thin non-colliding glass
  pane; the void gets no collision, so passages are walk/shoot-through.
- dna.resolve_module_plan (pure): a fit-to-exact-dims, center-pivot BuildPlan
  straight from a kit entry - no size_hint, no jitter. Carries target_dims,
  pivot, and the DC module contract (type/theme/style/width/stem).
- validate: exact-fit checks (fit_width/depth/height) fire when a plan carries
  target_dims - the built size must equal the slot size, not just the envelope.
- bpylayer/build.py: build_module (one named GLB, e.g. wall_delco_01_w200.glb)
  and build_kit (plan + build every module a building needs into art/zoo/, plus
  a <building>_kit.built.json index).
- CLI: --build-kit <slots.json> [--theme delco] [--style N] [--out DIR] builds
  the module GLBs (needs Blender). --kit still does the dry plan.
- materials: concrete + plaster roughness.
- 18 new tests (111 total). This is the plain STRUCTURAL pass (generic
  industrial concrete + steel frames); Delco-flavored look-passes come next.
### Next
- Delco art direction per module (materials, trim, door leaf vs open frame,
  window mullions, blown/rough breach with rebar + rubble, grime).
- Verify build in Blender + swap into a real Deli Counter building in Godot.

## [0.14.0] - Greybox integration: Zoo as Deli Counter's art/zoo library
### Added - plan the module kit that dresses a Deli Counter greybox
- core/kit.py (pure, tested): reads a Deli Counter <name>.slots.json swap
  contract and computes the distinct Zoo modules needed to theme the building,
  honoring Deli Counter's naming law (<type>_<theme>_<style>_w<cm>; wall
  remainders collapse to one scaled 'wallEnd' unit; everything else exact-fit
  per width). Validated against a real 128-slot building -> 9 modules.
- CLI: --kit <slots.json> [--theme delco] [--style N] prints the kit plan and
  optionally writes <building>_kit.json. Pure - no Blender.
- 5 new tests (93 total).
### Next
- Architectural module species (wall/doorway/window/breach/wallEnd) with
  fit-to-exact-dims + center pivot, exported into art/zoo/ with the resolver's
  naming, so a planned kit becomes real GLBs Deli Counter swaps in.

## [0.13.1]
- Added an Unsnap button (the counterpart to Snap): detaches the selected prop
  by reparenting it back to the scene root while keeping its world position, so
  it becomes free-standing again. Snap attaches, Unsnap releases. Plugin-only.

## [0.13.0] - Socket shapes: point / grid / area
### Added - connectors are no longer just single points
- Sockets now have a shape: point (one spot, the default), area (a surface
  region you can place anywhere on), or grid (Lego studs - snap to nearest
  cell). core/connect.py: resolve_socket_offset + grid/area math, snap_pose
  takes a hit point for area/grid placement. Fully tested.
- Genome socket declarations can be objects with shape + size / size_rel
  (scales to the specimen) + cell. build_connectors sizes area sockets from
  the specimen's dimensions. table/desk surfaces are now 0.85x area sockets.
- Godot Snap gains a "Free placement" toggle: drop a prop wherever it sits on
  a surface (keep X/Z, match surface height) vs exact point-snap. Plugin-only
  Godot change; grid/area-from-meta cursor placement is a further step.
- 6 new tests (88 total).

## [0.12.2]
- Reworked Snap after playtest feedback (the old one-shot placement felt
  fragile). Now: select the prop + the HOST (its root), and Zoo auto-finds the
  ATT_* socket inside the host (no more digging into the GLB or accidentally
  moving the socket). New "Attach" checkbox (default on) parents the prop under
  the host so it moves with it — a real attachment, not a one-time drop.
  Plugin-only.

## [0.12.1]
- Fixed a Godot 4.7 plugin compile error: in _local_aabb the loop var is
  Variant, so `var rel := inv * mi.global_transform` couldn't infer a type and
  failed the whole script (which broke exhibit import + Snap). Typed it as
  `var rel: Transform3D`. Plugin-only.

## [0.12.0] - Connectors: Lego-style anchoring
### Added - typed sockets/anchors so props snap to players and levels
- New connector system (core/connect.py, pure + tested): every asset has a
  typed ANCHOR (how it attaches: head/feet/grip/surface/floor/...) and typed
  SOCKETS (where things attach to it). They connect only when compatible
  (grip<->hand, cup/surface<->surface, head won't sit on a table). Includes
  snap-pose math (align anchor to socket, with a 'butt' mode for level modules)
  and find_matches (which host sockets a prop fits).
- Genomes declare connectors as data ("connectors": {"anchor":..,"sockets":..})
  — pack-friendly, no code. Declared on 11 species.
- Build injects the connector block into each specimen's meta.json (recipe
  attachment positions + genome types).
- Godot importer: a Snap section — select prop, Ctrl-click a socket (ATT_*
  node), Snap; the prop's anchor aligns to the socket transform.
- Documented socket convention for character rigs (ATT_head/hand_l/hand_r/
  back/hip/feet/chest) and levels. 8 new tests (82 total).

## [0.11.0] - Exhibits: organize a scene full of GLBs
### Added - the "asset zoo" pattern (Gyms/Zoos/Museums)
- New exhibit system: point Zoo at a folder of built/ingested GLBs and it
  reads their meta.json footprints and lays them out into a browsable scene.
  Two schemes: 'zoo' (knolled uniform grid + 1.8m/1m scale reference, no names
  needed) and 'museum' (each asset on a labelled pedestal with name + size).
- Pure core (core/layout.py + core/exhibit.py, tested): footprint-based
  layout, category grouping + size sort, scan generated OR ingested meta.json,
  write <folder>_<scheme>.exhibit.json. No Blender needed to plan a layout.
- CLI: --exhibit <folder> --scheme zoo|museum [--cols N] [--exhibit-name X].
- Godot importer extended: places exhibit members at computed positions and
  spawns pedestals (BoxMesh), placards (Label3D), and scale markers natively.
- 8 new tests (74 total).

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
