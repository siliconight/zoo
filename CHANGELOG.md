# Changelog

## [0.32.0] - Production kit index + missing-module gap report

### Added
- **Missing-module report**: `plan_kit(known_species=...)` routes slot
  roles the genome library cannot build into `missing_modules` (with
  reasons) instead of crashing at build time; `build_kit` passes the real
  genome list, warns, and persists the list in the kit index.
- **Kit index enrichment**: `*_kit.built.json` module entries now carry
  category, dims, pivot, forward (+Y authoring convention; the DC slot
  transform owns final facing), supported_slot_types, material_set,
  collision, lod, and validation status.
- tests/test_kit_missing.py; COORDINATE_CONTRACT.md (shared, ratified).

### Changed
- **Slot fit is authoritative**: genome prompt-era dimension ranges demote
  to warnings when an exact fit target exists (fit_* checks still gate
  hard) -- a DC building may legitimately need a 0.3 m wall return the
  prop ranges never anticipated. 199 tests pass.


## [0.31.0] - Branded sign faces from Pixelcoat sign packs

### Added
- **Sign-pack library** (`core.skins.find_sign_packs` / `pick_pack`): a
  ``signs_<theme>/`` (or ``signs/``) directory under ``--skins`` whose
  subdirs are Pixelcoat packs — point it straight at a Pixelcoat build
  --output. Selection is deterministic per anchor id: the pawn shop keeps
  its sign across every rebuild, and different storefronts spread across
  the library.
- **`materials.make_emissive_textured_material`**: the pack albedo drives
  Base Color AND Emission Color (glTF emissive texture) — the artwork is
  what glows. Names keep the ``_Face`` suffix so Lux's emissive binder
  kills branded signs on a power cut exactly like flat ones. EXTEND
  wrapping (a sign never tiles); pack roughness linked when present.
- **sign_box recipe**: branded face when the library has sign packs, with
  the face re-UV'd 0..1 across the panel (`_planar_uv_fit`) — cube-projected
  meter UVs would tile the artwork across any face wider than a meter.
  No packs -> the flat acrylic glow, byte-identical to v0.30.
- Fixtures build threads ``anchor_id`` into every species plan.
- `materials.get_skin_library()` getter.

### Notes
- Fixtures mode already accepted ``--skins``; this release is what makes it
  matter for signs. TOOL_VERSION bump re-keys per-fixture RNG as always.


## [0.30.2] - Run artifacts land in _runs\

- `tools/walkabout.ps1` write run folders and results zips under the factory's `_runs\`
  directory instead of the factory root — tool repos and the coordination
  files stay alone at the top level. No behavior change.

## [0.30.1] - Walkabout runner homed in-repo

### Added
- `tools/walkabout.ps1`: the fixture-pass verification runner (env audit,
  manifest discovery, pure plan, real-Blender fixture builds, built-index
  gates incl. the v0.30 `emitter_markers` check, results zip) now lives in
  the repo and derives every path from its own location — run it from
  anywhere. Results still land at the factory root as run artifacts.

### Notes
- TOOL_VERSION bump re-keys per-fixture RNG variation, as with any release.
  No builder logic changed.

## [0.30.0] - Emitter markers: fixture GLBs light themselves (pairs with lux v0.15.0)

### Added
- **`LuxEmit_<type>` emitter markers** (`core.fixtures.MARKER_PREFIX` +
  `marker_name()`): `build_fixtures` now exports one empty per PLACEMENT at
  the EMITTER point (the anchor pos itself — no mount lift), carrying the
  placement payload as glTF extras (`lux_type`, `lux_anchor_id`, `lux_slot`,
  `lux_reacts_to_alarm`). Godot imports extras as node metadata; Lux v0.15's
  `LuxFixtureSpawner` walks any scene for the prefix and spawns the matching
  lamp at each marker. Drag a fixtures GLB anywhere — Level Factory or by
  hand — and it lights itself, no manifest needed. Rows were expanded here,
  once: markers are per-lamp, the single source of placement truth.
- `.built.json` index gains `emitter_markers` (count) + `marker_prefix`.
- glTF export now sets `export_extras=True` (rides custom props out on every
  build; only marker empties define any).

### Notes
- Names dedupe in Blender (`.001`) and Godot swaps the dot for an
  underscore — consumers MUST match by prefix and prefer metadata over
  name-parsing for the type.
- Manifest bake path (Lux "Bake Lights") is unchanged and remains the path
  for daylight (window/sun) anchors, which have no hardware and no markers.


## [0.29.0] - Facade hardware: sign_box + wall_pack (pairs with DC v0.75.0, lux v0.14.0)

### Added
- **Two facade species** for DC's lights.json 1.1 anchors: `sign_box`
  (emissive acrylic face at the anchor plane, cabinet + standoff arms
  hanging back toward the wall at -X local; face sized by the anchor's
  `size`, clamped to the genome range) and `wall_pack` (wedge body above
  the emitter, emissive lens on the underside, arm back to the wall).
  Both collision-free (above head height).
- **`mount: center`** in the fixture planner — the anchor IS the body's
  centre (sign faces); joins `above`/`below`. Anchor `size` now rides
  through placements; `core.fixtures.clamp_dim` bounds DC-supplied panels.
- **Emissive naming contract**: lit faces are `M_*_Lens` / `M_*_Diffuser` /
  `M_*_Face` — exactly what lux v0.14.0's emissive binder keys on, so
  cutting the building power kills sign glow with the lamps.
- 4 new pure tests (190 total).

## [0.28.0] - Light fixtures: hardware for the light-anchor pipeline

Light comes from the sun or from physical fixtures — never from nowhere.
DC/Lot already say WHERE light belongs (`.lights.json`) and Lux spawns the
lamps; this release bakes the visible hardware at the SAME anchors, making
the manifest a two-consumer contract with zero drift.

### Added
- **`--fixtures <lights.json>`** — build physical light fixtures from a
  Deli Counter `<building>.lights.json` or a Lot-merged site manifest
  (same schema, either scope). Exports `<scope>_fixtures.glb` +
  `.built.json`; drop it into the scene alongside the building/site and
  Lux's Bake Lights puts the lamps at the same anchors. Without Blender,
  prints the pure fixture plan as JSON. `--fixture-types` filters anchor
  types (e.g. streetlights only, out of a site manifest whose interiors
  are baked per-building).
- **`core/fixtures.py`** (pure, no bpy): the planner. Anchor `pos` is the
  emitter; rows expand **centered** along `rot_y` with LuxFluorescentRig's
  exact `start = -(count-1)/2 * spacing`, so every housing lands on its
  lamp. Per-kind mounting: `fluorescent` hangs ABOVE the emitter (housing
  fills DC's 0.1 m ceiling gap, diffuser face at the anchor);
  `streetlight` hangs BELOW (pole top at the anchor, height stretched —
  clamped to the genome range — so the base reaches grade at z=0, matching
  Lot's pole-top-at-6 m anchors). `window`/`sun` are daylight/preset — no
  hardware; unknown types are reported in `skipped`, never guessed.
- **Two species**: `fluorescent_fixture` (sheet-metal troffer over an
  emissive prismatic diffuser; collision: none — it's ceiling hardware)
  and `streetlight` (base plate, pole, shoebox head, emissive sodium lens
  floated just above the pole top so the lamp point sits in clear air;
  collision: pole box → `-colonly` proxy, players bump into poles).
- **`materials.make_emissive_material(name, color, strength)`** — self-lit
  faces export as glTF emissive (+ KHR_materials_emissive_strength), which
  Godot imports as StandardMaterial3D emission. Lux's LEVEL role keeps
  imported standard materials, so lenses glow under any preset and feed
  LightmapGI on the pc2000 path. Lit faces are painted wear=0 (a lens
  doesn't grime; white COLOR_0 keeps the albedo multiply neutral).
  `make_material`'s signature is untouched.
- Per-theme lens tinting rides the genome **style block**
  (`emissive_color` / `emissive_strength`) — data, not code.
- 12 pure tests (186 total): centered row expansion, rot_y direction
  convention, mount mapping, daylight/unknown skips, type filter, site
  scope, pole-height clamping, determinism, alarm-flag passthrough,
  manifest rejection.

### Notes
- Pairs with **lux v0.13.1**, which centers LuxStreetlightRig's row the
  same way (it previously extended from the anchor instead of centering
  on it — Lot writes path-midpoint anchors, so uncentered rows lit half
  the path and overshot the end).
- Standing caveat: the bpy builder needs a Blender walk
  (`build_fixtures` follows `build_roof_props` verbatim, but no bpy wheel
  installs in the dev container).

## [0.27.0] - Skin stage: Pixelcoat packs on compiled assets

### Added
- **`--skins DIR`** — point any build mode (specimen, habitat, kit, dress,
  roof props) at a folder of Pixelcoat texture packs and materials of a
  matching kind become image-textured: albedo (Closest interpolation —
  pixel art stays pixel art) + normal (OpenGL Y+) + stepped roughness
  [+ emissive]. Kinds without a pack stay flat vertex color — the art
  pass is progressive, same philosophy as DC's greybox fallback.
  `make_material`'s signature is unchanged, so **zero recipes were
  touched**; the skin decision lives entirely in the material factory.
- **`core/skins.py`** (pure, no bpy): resolver + library report.
  Resolution: `<kind>_<theme>/` then `<kind>/`; a pack dir holds a
  `*.pack.json` (Pixelcoat >= 0.2, `pixelcoat-pack/1`) or bare
  `*_albedo.png` (Pixelcoat 0.1 output). Manifest naming a missing albedo
  raises (broken presence is loud); empty dir is a quiet miss. Without
  Blender, `--skins` alone prints the resolved library as JSON and exits.
- **Density contract**: mesh UVs are already world meters × texel
  (`cube_project_uv`), so tiling packs land at uniform physical density on
  every part of every species with zero per-species work. The pack's
  `meters_per_tile` becomes a UV Mapping scale (exports as
  KHR_texture_transform, which Godot 4 reads); per-part `texel` stays a
  relative density knob.
- Wear still exports as COLOR_0 and multiplies the albedo texture at
  runtime per the glTF spec; the in-Blender wear-preview mix is skipped on
  textured materials so the exporter's texture detection stays unambiguous.
- 8 pure tests (174 total): theme-dir precedence, kind fallback, quiet
  miss, optional-map dropping, corrupt-manifest error, legacy albedo dirs,
  meters_per_tile passthrough, library report.

### Notes
- Consumes **Pixelcoat v0.2.0** packs (which added the material-map stage
  and the `.pack.json` manifest for exactly this).
- Standing caveat applies: the textured-material node graph needs a
  Blender walk (no bpy in the build container) — smoke it with
  `--prompt "vault door" --skins <dir>` and check the GLB in Godot.

## [0.26.0] - Facade kit: frames, gutters, pilasters

### Added
- **Three cover kinds** completing the architectural-depth bucket (Patina
  v0.18 `--frames` / `--gutters` / `--pilasters`):
  - `frame` — four thin strips (head, sill, two jambs; butt joints, head
    and sill overhang the jambs) around a doorway/window opening. Sized by
    `size2` = the exact opening rect from DC's `fit.openings`;
    `frame_width` rides the order. Geometry contract lives in the pure,
    tested `core.dressing.frame_strips`.
  - `gutter_run` — a horizontal eave run spanning its wall module exactly
    (never rescaled; sections join at module seams).
  - `pilaster` — a vertical proud strip at a module seam, sized by `size2`
    = [width, wall height].
- `dress_plan` passes `frame_width` through. Covers stay `collision: none`.

### Notes
- Pairs with **Patina v0.18.0**. gs_corner_station: 13 frames, 70 gutters,
  70 pilasters.

## [0.25.0] - Rooftop pack: break up the roofline

### Added
- **Six rooftop prop species** (silhouette breakers — the flat roofline was
  the last 0% bucket of the geometric-detailing list): `hvac_unit` (curb /
  cabinet / fan cowl / grille / conduit), `water_tank` (legs / tank /
  stepped cap), `vent_stack` (`profile` param: round flue or square brick
  chimney), `exhaust_fan` (curb / drum / hemisphere dome), `skylight`
  (curb + glass slab), `satellite_dish` (pole / arm / flattened-ellipsoid
  dish / feed, visual-only).
- **`core/roofprops.py`** — pure, fully-tested scatter planner: reads a DC
  slots.json, finds `roof` slots, lays a deterministic non-overlapping
  scatter per roof plane (density scales with area; tanks and dishes hug
  edges, skylights stay central; edge margin + clearance respected; same
  manifest + seed = same roofscape). gs_corner_station: 18 props.
- **`build_roof_props`** (bpylayer) + **`--roof-props <slots.json>`** CLI
  (`--density`, `--seed`, `--theme`): builds each placement with its normal
  species recipe, lifts it onto the roof's top surface, exports
  `<building>_roofprops.glb` + `.built.json`. Species with collision
  genomes get `-colonly` proxies — players walk roofs in a heist game; an
  HVAC unit is cover, not a hologram.
- `roof` joins the connect vocabulary as a world anchor type.

## [0.24.0] - Panel fields: the wall-scale dressing cover

### Added
- **`panel_field` cover kind** (Patina v0.17 `wall_panel` orders): one thin
  proud plate (3cm) per order, sized exactly by the order's new `size2` =
  [face width, face height] — panel grids are laid out by Patina per wall
  slot, so cells are never rescaled here. The field effect comes from many
  orders in a grid; the gaps between plates are where a flat greybox facade
  gets its shadow lines. Same collision as ever: covers stay
  `collision: none`, the DC greybox stays authoritative.
- `dress_plan` passes `size2` through; `strip_size(cover, size_hint, size2)`
  gains the optional third argument (existing covers unaffected). Orders
  without `size2` fall back to a square plate from the scalar size.

### Notes
- Pairs with **Patina v0.17.0** (`--panel-fields`). A gs_corner_station run
  emits ~509 panel orders across 70 exterior wall slots.

## [0.23.0] - Roof species: fill the modular roof slot
### Added
- **`roof` species** (`genome/species/roof.json` + `recipes/roof.py`) — a flat
  capping slab built to a Deli Counter roof slot's exact dims (wide/deep, thin).
  Same slab construction as `wall`, added to `_SOLID` so it builds without a
  void. delco style is dark tar. This fills the roof slot DC emits under
  `DC_MODULAR=1` (the "always emit the roof as an art-pass swap-slot when
  modular" behaviour), which previously crashed `--build-kit` with
  `No genome for species 'roof'` and left the roof face empty/black in-engine.
- 32nd species; registered in tests. 152 tests green.


## [0.22.1] - Ambient: framed for Lux composition
### Changed
- Documented the directional ambient's role relative to Lux: it is a *gentle,
  view-independent form* cue (the depth a surface has before any light), not a
  second key light. Lux's sun does the runtime directional lighting; the baked
  ambient (delco 0.35) stays subtle so it reads as form under Lux's banded
  diffuse rather than doubling the sun. Behaviour unchanged; see Patina's
  `docs/LOOK_PIPELINE.md` for the full cross-tool cue ownership.


## [0.22.0] - Directional ambient: form before the art pass
### Added
- **Directional ambient** baked into architectural-module vertex colour
  (`geometry.wear_colors(..., ambient=)`): a cool-from-above / warm-fill-below
  tint multiplied into the `Wear` layer per face, so modules read with soft
  form before any external light — the geometry-side companion to Patina
  v0.12's depth cues (Arne Jansson's "cool up / warm down" ambient). Godot
  already reads `Wear` as an albedo multiply, so it shows with no shader change.
  - Driven by a style-block `ambient` (0..1); the `delco` style on wall /
    wallEnd / doorway / window / breach sets `0.35`. `ambient=0` (every other
    style) keeps the original grayscale wear — byte-identical.
  - Threaded style -> `dna.resolve_module_plan` -> `_arch.build_slab` ->
    `bm_to_object` -> `wear_colors`.

### Notes
- Geometry build needs Blender; the pure logic (`_ambient_tint`: cool up, warm
  down, white at strength 0) is verified. 152 tests green.


## [0.21.0] - Dressing: build Patina's facade covers
### Added
- **`--dress <building>.dressing.json`** — build the non-collision facade covers
  Patina v0.11 places. Patina emits a trim atlas + per-anchor build orders
  (roof edges, base courses, curbs, conduit); Zoo builds the geometry. This is
  the Zoo half of Patina's dressing contract.
  - `core/dressing.py` (pure): reads a `patina-dressing/1` manifest, converts
    Patina's baked Y-up to Blender Z-up when needed (DC-aligned manifests are
    already Blender Z-up and pass through), resolves theme -> style
    material/color/wear via the `dress_cover` genome, and drops any order whose
    `collision` isn't `none`.
  - `recipes/dress_cover.py` + `genome/species/dress_cover.json` (30th species):
    a thin proud cover strip per order, oriented by the anchor normal, UV-region
    carried from the order. **Returns no collision boxes** — covers are visual
    only, so the DC greybox collision stays authoritative.
  - `bpylayer/build.build_dressing`: builds every cover into one
    `<building>_dressing.glb` + a `<building>_dressing.built.json` index.
  - 13 new tests (152 total, pure planner). The geometry build needs Blender
    (the standing in-engine walk).
### Next
- In-engine walk: confirm covers render correctly over DC's collision in Godot.
- UV assignment to the atlas region is carried in the order; wiring it to the
  exported mesh UVs is the remaining recipe detail to verify in Blender.


## [0.20.0] - Bank props: camera, stanchion, drop safe, gold bar
### Added
- 4 new props (29 species: 21 props + 8 architectural modules) — the loose
  bank dressing, all bottom-center props with connectors (not wall modules):
  - `security_camera` — wall-mounted CCTV (mount plate + arm + body + lens +
    LED), `wall` anchor so it snaps to a wall; collision (shootable).
  - `queue_stanchion` — a rope/belt queue post (weighted disc base + slim post +
    finial + belt hook), `floor` anchor + a top `ATT_belt` grip socket so a belt
    can link to the next stanchion.
  - `drop_safe` — a small floor safe (body + proud door + combo dial + lever
    handle + drop slot), `floor` anchor; the body sits back 6cm so the proud
    details reach the nominal front without pushing the bbox past the depth
    range at any sampled size.
  - `gold_bar` — a gold ingot, `surface` anchor, no collision (a pickup, like
    cash_stack). Placed in bulk by the level.
- All prompt-buildable (`--prompt "a security camera"`). 8 new tests (139 total).
### Next
- Deli Counter / Lot can scatter these via placements; the camera also pairs
  with DC's `camera_socket` marker.
- Delco art pass across the bank set (shattered glass, drilled boxes, blown
  breach, plus signage/labels/wear on the props).

## [0.19.0] - safe_deposit_boxes: the vault-room box wall
### Added
- New `safe_deposit_boxes` species (25 total: 17 props + 8 architectural
  modules). An interactive architectural module, center-pivot + fit-to-exact-
  dims: a solid metal BACKING slab (rear of the depth) + a bordered GRID of
  raised DIVIDERS on the front, so the compartments between them read as the
  little numbered boxes. The backing defines the exact (w, d, h) box on
  width/height/rear, the dividers reach the front; the wall is solid (one
  collision box). Cheap by construction — (cols+1) vertical + (rows+1)
  horizontal dividers, not a box per cell — and the grid is capped (default
  16x16) so even a 5 m wall at a tiny cell size stays ~420 tris.
- Builds only the intact state; a `drilled` state reuses this art (resolver
  falls back to the base) until a drilled-boxes art pass. Numbers, handles and
  keyholes are a Delco art pass.
- 4 new tests (131 total).
### Next
- Bank props (security_camera, queue_stanchion, drop_safe, gold_bar) — these
  are bottom-center props with connectors, not wall modules.
- Deli Counter: `teller` and `safe_deposit` opening kinds so a bank spec emits
  those slots + interactive fixtures (states intact/shattered, intact/drilled),
  same as the `vault` kind. Pending a fresh DC zip.
- Delco art pass: shattered-glass / drilled-box variants, box numbers + handles.

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
