# Changelog

## [0.44.0] - batch 1: the four painted-metal species

The first four species whose metal is unambiguously paint, taken from the
chroma measurement in 0.43.0:

    simple_car        chroma 0.64    9 styles
    helmet            chroma 0.57    3 styles
    vending_machine   chroma 0.48    8 styles
    queue_stanchion   chroma 0.32    5 styles

All four already pass `plan["material"]` straight into `make_material`, so no
recipe changed. This is genome data only.

### Changed
- Each species swaps `metal` for `metal_painted` in `materials.options`, in
  `materials.default` where that was `metal` (all but helmet, whose default is
  `plastic`), and in every style block whose `material` was `metal`.

`metal` is REMOVED from these four rather than left alongside `metal_painted`.
Left in, a prompt naming "metal" would resolve the theme-owned pack and ignore
the genome colour -- the exact defect this split exists to fix. Removed, that
prompt falls through to the species default, which is now the painted kind.

### Added
- `tests/test_material_options_closed.py`. It asserts, for ALL 53 genomes and
  not just these four, that every `styles[*].material` and the `default` are
  present in `materials.options`.

### Why that test is the point of this batch
`dna.resolve_plan` does this, with no warning:

    if material not in genome["materials"]["options"]:
        material = genome["materials"]["default"]

A style naming a kind missing from `options` is DISCARDED and the species
quietly renders in its default. So every species edit is two places, and the
failure mode is a render that looks untouched -- which is unfalsifiable by
eye. The first attempt at generating this patch hit exactly that class of bug
from the other side: a substring rewrite of `"metal",` also matched inside
`"material": "metal",`, so queue_stanchion had its styles rewritten and its
options list left alone. The genomes are byte-exact `json.dumps(indent=1)`
output, so the edit is now structural and the generated diff is asserted to
touch no line that does not mention metal.

### Still on plain `metal`
38 species. Eight are the remaining coloured ones: chair, filing_cabinet,
water_tank, flat_top_grill, shelving, atm, vault_door -- plus gold_bar, which
is chroma 0.61 but is BARE metal and wants `metal_bare`, not paint. The other
30 are already near-grey and correctly keep `metal`; ten of those are
architecture and must.

NOTE for batch 2: `shelving.json` is NOT byte-exact indent=1 round-trippable,
unlike every other genome checked. It needs an anchored edit or a deliberate
reformat, not a structural re-dump.

## [0.43.0] - two new kinds, and the measurement that scoped them

The skinned vending-machine render made the case: `plastic` trim took its own
red correctly, and the BODY came out galvanized grey, because the body is
`metal` and `metal` is theme-owned. Every ATM, HVAC unit, filing cabinet and
car body had the same defect -- 42 species sharing one grey.

Before splitting, the size of the problem was measured rather than assumed.
For each species that can wear `metal`, the chroma of every style colour whose
material is `metal`:

    chroma >= 0.25   5 species   simple_car 0.64, gold_bar 0.61, helmet 0.57,
                                 vending_machine 0.48, queue_stanchion 0.32
    0.10 - 0.25      7 species   chair, filing_cabinet, water_tank,
                                 flat_top_grill, shelving, atm, vault_door
    < 0.10          30 species   streetlight 0.038, hvac_unit 0.058, ...

Thirty species need no change at all: their metal colours are already grey, so
the theme's metal is a fair answer. Ten of those thirty are architecture --
wall, wallCorner, wallEnd, window, doorway, breach, prop, dress_cover, ceiling,
roof -- and MUST stay theme-owned. That is the measured reason the kind could
not simply be made tintable.

### Added
- `metal_painted` and `metal_bare` in `skins.KNOWN_KINDS`, `ROUGHNESS`
  (0.45 / 0.28) and `METALLIC` (0.0 / 0.90).

Two kinds and not one because METALLIC is a per-kind lookup. Paint is a
dielectric; bare metal is a conductor. Folding them together would have put a
metallic sheen on matte paint, or killed the specular on a gold bar.

`metal_painted` is written as an explicit 0.0 rather than left to the `.get()`
default, because that number is the entire reason the two kinds are separate
and a value that load-bearing should not be inferred from an omission.

### Note
Nothing renders differently. No genome names either kind yet.

WATCH OUT when the genomes are edited. `dna.resolve_plan` does:

    if material not in genome["materials"]["options"]:
        material = genome["materials"]["default"]

silently. A style that says `"material": "metal_painted"` is DISCARDED unless
the kind is also added to that species' `materials.options`. Every species edit
is two places, and the failure mode is a render that looks unchanged.

## [0.42.1] - the export boundary was measured, so the note comes down

0.42.0 shipped `_tint_multiply` with an `### UNVERIFIED` block: the shader
graph gained a node between the image and Base Color, and the glTF exporter
was free to drop the resulting baseColorFactor silently. That was the honest
state of knowledge, and it is no longer the state of knowledge.

### Verified
`tools/tint_probe.py`, Blender 5.1.1 (hash b70da489d7f4), two materials built
from one tintable pack and read back out of the exported GLB:

    M_Probe_red   baseColorFactor [0.620, 0.140, 0.140, 1.000]  texture yes
    M_Probe_blue  baseColorFactor [0.140, 0.260, 0.550, 1.000]  texture yes

The genome colours to three decimals, both textures intact, and the two did
not collapse into one material. The pixel-bake fallback is not needed.

### Changed
- The docstring on `_tint_multiply` now records the measurement instead of the
  doubt, and says to re-run the probe on a Blender upgrade -- the fold is the
  exporter's choice, not a guarantee of the format.

## [0.42.0] - a pack can ask to be painted, and the mesh answers

`make_material`'s own docstring said it: "the genome's per-specimen color
rides only the flat path; textured paint jobs are the pack's job". Measured,
that means every object of a kind in a skinned build shares ONE cached
material, modulated only by COLOR_0, which carries greyscale wear. All 42
species that can wear `metal` collapse into one galvanized grey; simple_car's
police black, racing red and 1970s brown collapse with them.

That is correct for a brick wall and wrong for a bumper, and the distinction
is not the KIND -- `metal` serves a rusted storefront facade and 42 props.
It is the PACK. Pixelcoat 0.13 lets a grammar declare `tintable`; this reads
it.

### Added
- `skins.load_pack` surfaces `tintable`. Absent key -> False, so every pack
  written before Pixelcoat 0.13 -- which is all of them -- behaves exactly as
  it does today. Verified by `test_pack_written_before_0_13_defaults_to_not_tintable`.
- `materials._tint_key`: a pure 6-hex cache key, kept out of `make_material`
  so it can be tested without bpy.
- `materials._tint_multiply`: `albedo * tint` for a tintable pack only.
- `tools/tint_probe.py`: exports a specimen and reads `baseColorFactor` and
  `baseColorTexture` back out of the GLB.

### Changed
- A tintable pack's material cache key is now `(kind, theme, colour)` instead
  of `(kind, theme)`. A non-tintable pack still collapses to one material,
  which is the point for walls.

### UNVERIFIED
The shader graph now has one more node between the image and Base Color than
it had when `tools/wear_probe.py` verified the texture still exported. glTF
folds `baseColorFactor * baseColorTexture * COLOR_0`; the exporter may give up
on the extra multiply and drop the factor SILENTLY, which would render every
tinted prop in the pack's own near-white with no error anywhere. This is the
same failure shape that hid the flat wear for a whole art pass, so it is
written down as unknown rather than assumed working. Run `tools/tint_probe.py`
before mapping any tintable pack into a theme. If the factor is dropped, the
fallback is to multiply the tint into the loaded image pixels once per colour.

### Note
Nothing renders differently yet. No pack on disk sets `tintable`, and no theme
maps a kind that would.

## [0.41.0] - the car, rewritten after looking at it

The first `simple_car` had the right dimensions and the wrong assembly. A
0.64 m wheel and a 2.75 m wheelbase are both within a few centimetres of a
real sedan; rendered, it read as a toy pickup. Nothing here changes a
dimension.

### Fixed
- **The body was one unbroken slab**, full width from 0.27 to 0.94 m. It is now
  a rocker, a body and a shoulder. The rocker is narrow and low; the body is
  the widest point; the shoulder tapers in to meet the greenhouse. The bands
  overlap rather than butt, because an overlap is one solid after
  `shade_by_angle` and a butt joint is a seam that catches light along its
  whole length.
- **The cabin sat on the body with a 12.3 cm step per side.** The shoulder now
  tapers to 0.93 of the width and the cabin starts at 0.90, so the step is
  **2.6 cm** and reads as a beltline instead of a box balanced on a plank.
- **The greenhouse is tapered**, 0.90 of the width at the beltline to 0.88 at
  the roof, using the new `geometry.taper_z`. Stacking two boxes would leave a
  90-degree step that `shade_by_angle` correctly keeps sharp -- so it would
  read as two boxes.
- **Wheels sat 4 cm inboard of the widest point with no arch.** They are now
  tucked 11 cm under an overhanging shoulder. **That IS the wheel arch**: there
  is no boolean and none is needed. A wheel under an overhang reads as arched;
  a wheel flush with the side does not, whatever else is true about it.
- **The cabin was centred**, so hood and deck were the same length and every
  body style read as a cab-over truck. `CABIN` now shifts it rearward:
  **hood 1.38 m against a 0.77 m deck** on the default sedan.
- **Glazing stood proud of the cabin faces**, which reads as a sticker. It is
  now inset 1.5 cm and the side glass is shortened to leave pillars.

### Added
- **`geometry.taper_z(verts, top_scale, bottom_scale=1.0)`** -- scale X and Y
  by height, giving a frustum from any primitive in one call. Manufactured
  things are rarely prisms: a greenhouse narrows to the roof, a bin tapers so
  it stacks, a dumpster's sides lean so the lid clears. Operates on the verts
  `add_box` / `add_cylinder` return, matching `jitter_verts` and
  `flatten_base`. A flat vert set is left alone rather than divided by zero.

### Changed
- Material assignment matches on a name PREFIX rather than hunting for
  `"Body" in name`. The body is four objects now, and a substring match would
  have quietly handed the rocker and the shoulder to the rubber material.
- Collision is still two boxes -- body shell and cabin -- so the gameplay
  volume a car brings is unchanged in kind, and now matches the art it is
  under rather than a slab that was wider than the silhouette.

### Notes
- Triangle cost is a few hundred against a 12,000 budget. Three extra boxes.
- **This is a silhouette and assembly pass, not a detail pass.** No wheel
  arch cut, no door lines, no lights, no mirrors. Those are the next tier, and
  the honest place for most of them is texture rather than geometry.
- Everything above is judged from renders of the previous build. There is no
  `_skins` pack in this tree, so the car has still never been seen with a
  Pixelcoat texture on it.

## [0.40.0] - Zoo shades its geometry

Every mesh Zoo has ever built was flat-shaded. `bm_to_object` ran bevel ->
recalc normals -> UV -> wear and stopped; there is no `shade_smooth`, no
auto-smooth and no weighted-normal step anywhere in `bpylayer`. So a
14-segment water tank read as a dodecagon and every bevel bought geometry
without buying shading, which is most of what a bevel is for.

### Added
- **`geometry.shade_by_angle(bm, angle_deg=SMOOTH_ANGLE_DEG)`** -- smooth
  shading with hard creases, decided per edge from the geometry: smooth every
  face, then mark an edge sharp when its two faces disagree by more than the
  threshold. Called from `bm_to_object` after `recalc_face_normals` (it reads
  face normals) and before the UV projection (which does not care).

- **`SMOOTH_ANGLE_DEG = 50.0`, and the number is arithmetic rather than
  taste.** `bevel_edges` runs `segments=1`, so a chamfer on a 90-degree corner
  meets each neighbour at exactly 45 degrees. The usual hard-surface default
  of 30 would have marked every chamfer sharp and this whole change would have
  done nothing. 50 sits above 45 and well below 90, so:

      fold                                smooth?
      coplanar                    0 deg   yes
      24-segment wheel side      15 deg   yes
      14-segment cylinder      25.7 deg   yes
      10-segment cylinder        36 deg   yes
      1-segment chamfer          45 deg   yes
      just over threshold        51 deg   no
      box corner                 90 deg   no
      boundary edge (1 face)         --   no

  Every one of those was checked against the function before it shipped.

### Why this is safe to apply to all 57 species at once
- **Triangle count is unchanged.** Nothing here adds a face, so
  `validate.evaluate`'s `budgets.tris_lod0` check is untouched. The exported
  VERTEX count usually falls, because smooth shading lets a corner share one
  normal where flat shading needed three.
- **Blender 4.1 removed `mesh.use_auto_smooth`** and replaced it with an
  operator that adds a Smooth-by-Angle modifier. Zoo builds headless,
  deterministically, with no operators and no modifier stack, so neither was
  available. Doing it on the bmesh needs neither and bakes into the export.
- A boundary or non-manifold edge is left hard. There is no second face to
  average with, and smoothing against a normal that is not there is how you
  get a seam that looks like a crack.

### Changed
- `tools/preview_street_solids.ps1` picks up a Pixelcoat pack from
  `zoo/_skins` when one exists, matching `preview_floor_ceiling.ps1`, and says
  so when it does not. **There is no `_skins` directory in this tree**, so
  every preview so far -- dressing included -- has been flat style colour plus
  baked vertex wear, judging silhouette and shading alone. Worth knowing before
  judging an asset.

### Not done
- **Weighted normals.** The modifier weights a corner normal by face area so a
  narrow bevel strip stops dominating. There is no bmesh equivalent, and adding
  a modifier stack to a build that has deliberately avoided one is a bigger
  decision than this. With `segments=1` bevels the overlap with correct
  sharp-edge marking is large; revisit if bevels ever go multi-segment.
- **Bevel segments stay at 1.** Two would give a rounder roll-off and roughly
  double bevel geometry, against budgets that are already checked and were
  already exceeded once by a pebble.

## [0.39.1] - a preview can name its species, and street solids get a preview

### Added
- **`tools/preview_street_solids.ps1`** -- the sibling of
  `preview_dressing.ps1`, for the species that could stand in for a gameplay
  solid outdoors: `simple_car`, `prop`, `hvac_unit`, `water_tank`,
  `vending_machine`, `sign_box`, `streetlight`. Builds, renders and measures
  each one.

  **It asks one question the dressing preview does not need to.** Surface
  dressing is collisionless by definition; these exist BECAUSE of the volume
  they occupy. So the script reads the collision back out of every built GLB
  and prints it beside the shape metrics, using
  `level_factory/packages/validation/glb_collision.py` -- which walks the
  container and the node tree and needs neither Blender nor Godot. Zoo ships
  collision as a `-colonly` sibling mesh (`bpylayer/collision.py`), so this is
  Zoo's own output read back through an independent implementation rather than
  trusted from the build log.

### Changed
- **`tools/preview_specimen.py` accepts `--species`.** `build.build_specimen`
  has taken a `species=` argument since 0.38.0 -- "the door a program uses" --
  and this tool was still knocking with a prompt. `core.intent.parse` is blunt
  about the cost: two species in the library could not be reached through a
  prompt at all, and a prompt that resolves today does so because no better
  keyword match exists yet, which is a coincidence rather than a contract. A
  preview script naming seven species by prompt is seven coincidences waiting
  on the next species to be added.

  The prompt still rides along for material, colour, wear, size and era, so
  styling is unchanged. `--prompt` alone behaves exactly as before.

- The build line now prints which way it was asked --
  `species='simple_car'` or `prompt='weathered sedan'` -- so the console says
  whether keyword matching was involved.

### Notes
- A car already ships with collision: `recipes/simple_car.py` returns two
  `collision_boxes` (body and cabin), not a triangle hull and not a crude
  bounding box. That is the "art mesh does not introduce unnecessarily complex
  collision" rule already satisfied, one asset at a time.
- Nothing here places anything. These are assets and a way to look at them.

## [0.39.0] - a prop's filename now names every axis a prop is free on

The plate bug, one axis further on, found while surveying for the outdoor
proxy work and measured before it was believed.

### Fixed
- **`prop` modules collided on filename.** `module_stem` keyed non-plate roles
  on width alone, justified at the time by an argument about walls: *"a wall
  varies on one axis -- its width -- while its thickness and the storey height
  are fixed, so `_w<cm>` is a complete key."* True for a wall. `prop` was added
  later and `recipes/prop.py` describes it as *"a vault, a teller counter, a
  desk, a cabinet, a crate stack"* -- free on all three axes. It inherited an
  argument that was never about it.

  `plan_kit` bucketed correctly (its key carries `dims_key`), so the planner
  saw two distinct modules and named them the same file. One won; the other
  was built over it and every slot resolved to the survivor.

  **Measured over 52 of the 136 shipped `slots.json` manifests: 15 buildings
  (28%) planned two or more distinct prop modules onto one filename, 48 of
  1,486 modules affected.** Worst case `cr_gas`, where `prop_delco_04_w90` was
  claimed by both `[0.9, 10.0, 1.8]` and `[0.9, 0.9, 1.0]` -- a 9.1 m
  difference in depth between a long counter and a small cube.
  `cbp_town_finale` had one stem claimed by four distinct modules.

- **`VOLUME_ROLES = ("prop",)`** joins `PLATE_ROLES`. Volumes take `_d<cm>` and
  `_h<cm>`; plates keep `_d<cm>` and gain nothing; walls, doorways and windows
  are untouched. Verified against the corpus: exactly 84 filenames change
  across the sampled buildings, and every one has `role == "prop"` -- asserted
  in the check, not assumed.

### Changed
- `module_stem` gains a trailing `height_cm` argument. The stem is now
  `<type>_<theme>_<style>[_w][_d][_h][_v][_o][_state]`.
- **`deli_counter/themed_tscn.py` changes in the same patch.** Its
  `module_stem` is a deliberate mirror and its docstring says the two "must be
  changed together"; neither side parses a stem, both construct it. Checked
  over every slot in the corpus: **9,185 of 9,185 slots produce identical
  stems on both sides.**

### Tests
- `tests/test_volume_stem.py` -- 11 tests, including a pair differing ONLY in
  height. Every real collision in the sample differed on depth as well, so
  adding `_d<cm>` alone would have separated all of them and looked complete.
  The key names every axis rather than the ones that happened to be measured.
- Mutation-tested: removing the height key, emptying `VOLUME_ROLES`, never
  computing height, and leaving depth plate-only. All four die.

### Notes
- **Already-built `prop` GLBs stop resolving and fall back to greybox** until
  rebuilt. That is the progressive art path working as designed, and it is
  visible rather than silent -- unlike the defect it replaces.
- **A SECOND collision is NOT fixed here and is reported separately.** Plates
  with identical dims and different materials share a filename:
  `floor_delco_01_w2700_d3200` is claimed by both a `tile` and a `concrete`
  floor. `dna.resolve_module_plan` reads `module["material"]` as an override,
  so those build differently. Fixing it renames far more files and is a
  decision, not a cleanup.

## [0.38.0] - A species can be asked for by name

The only way to request a species was to describe it in a prompt and hope
keyword matching landed on the right one. That is the right interface for a
person and the wrong one for a program, and it had already failed twice
without anything noticing.

### Added
- **`intent.parse(prompt, species=...)`, `build.build_specimen(..., species=...)`
  and `zoo_cli --species`.** Naming the species skips keyword matching. An
  unknown name raises and lists the alternatives, because a program asking for
  a species that does not exist has a bug that should surface at the call
  rather than as a quietly different asset three stages later.
  The prompt is still parsed for material, colour, wear, size and era, so a
  caller can have the species it requires with the styling it wants:
  `--species pebble --prompt "wet mossy"`.
  With no prompt the species name becomes the prompt, so repeated requests for
  one species hash to one `seeding.root_key` instead of inheriting whichever
  empty string the caller passed.
- **`Intent.species_source`** — `"keyword"` or `"explicit"`, carried into
  `to_dict()`. A specimen's provenance should record whether a human's words
  or a program's argument chose the species.
- **`tests/test_species_by_name.py`** (10 tests), including a round trip over
  every species in the library.

### Fixed
- **`wallCorner` and `wallEnd` were unrequestable.** `intent.parse("wall
  corner")` returns species None — their keyword sets never covered their own
  names — and a prompt was the only door in. Both have been in the library,
  passing `test_genome`, and impossible to build for their whole lives. They
  are reachable now by name, and
  `test_two_species_are_unreachable_by_prompt` pins the set so the number
  cannot grow quietly. Their keyword sets are left alone deliberately: this
  release adds the door, and rewriting matching rules is a separate change
  with its own blast radius.

### Notes
- This is the first piece of the Layer 3 placement chain
  (`docs/SURFACE_DRESSING.md` §2). A placement layer must be able to ask for
  `pebble` several thousand times per site and get a pebble every time;
  `parse("pebble")` happened to work, but only because no other keyword
  currently beats it. Patina's manifest producer, the level_factory job, and
  the Presentation consumer are still to come.

## [0.37.0] - Layer 3 shapes that are measured, and the vocabulary nobody was checking

The first surface-dressing kit was reviewed from four renders and shipped. A
render can show that something looks wrong; it cannot say why, and every
explanation offered for these was a guess. So this release starts with a ruler
and then follows what the ruler said.

### Added
- **`tools/shape_metrics.py`** — measures the SHAPE of a built GLB, not just
  its size, with no Blender and no dependencies. Per specimen: sorted extents
  and Zingg class, bbox occupancy, `normal_regions_80` (how many facing
  directions cover 80% of the surface), up-facing area share, plan-view
  silhouette, `base_contact_ratio`, welded open/non-manifold edge counts. Per
  patch: Clark-Evans R, which is `docs/SURFACE_DRESSING.md`'s "no obvious
  uniform scatter pattern" as a number. `--selftest` includes falsification
  cases: a sphere must not score like a cube, a square lattice must give
  R = 2.000, removing one triangle must open exactly three edges.
  It also reads POSITION accessor min/max — the height measurement
  `glb_nodes.py` could never make, since that tool reads NODE translations and
  a dressing GLB has one node at the origin.
- **`geometry.subdivide` / `displace_lobes` / `fracture` / `flatten_base` /
  `add_blade` / `zingg_radii`** — operations that ADD faces rather than move
  them, because irregularity is bounded above by face count.
- **`tests/test_kind_vocabulary.py`** — asserts `KNOWN_KINDS` and `ROUGHNESS`
  agree, and that every material kind any genome names is in them. Reads
  `materials.py` with `ast` instead of importing it, since that module imports
  bpy and this suite runs without Blender — which is precisely why the check
  never existed.
- **`preview_specimen.py --view patch`** plus a ground plane and a 0.117 m
  scale post in every frame.

### Fixed
- **`tar` was in neither kind list.** The `roof` species has declared it since
  it shipped, so every roof fell through to `make_material`'s 0.6 default
  roughness and could never resolve a skin pack. Nothing failed; it was
  quietly wrong for the life of the species. `gravel` and `vegetation` had
  drifted the same way. All three are now in both lists and the new test holds
  them there.
- **`status=WARN` on the dressing kit was never about triangles.**
  `validate.py` reads `budgets["tris_lod0"]`, defaulting to 0; five genomes
  declared `tris_max`, so their budget resolved to zero and any triangle count
  exceeded it. Swept across all 53 species: 48 `tris_lod0`, 5 `tris_max`
  (the four dressing species and `dress_cover`, whose 400-triangle budget had
  therefore never been enforced). Renamed in those five.
- **`test_genome.test_all_species_load_and_validate` was red**: it asserts
  exact equality against the species folder and the four dressing species were
  never declared. Added as `DRESSING_SPECIES`, a third category alongside
  PROP and ARCH — neither modelled props nor slot-driven modules.

### Changed
- **The four Layer 3 species are rebuilt.** Measured before and after, same
  tool, same seed:

  | species | tris/budget | regions | base contact | closed |
  |---|---|---|---|---|
  | pebble | 334/260 -> 192/260 | 12 -> 15 | 0.000 -> 0.31 | yes |
  | rubble_frag | 176/320 -> 76/320 | 7 -> 8 | 0.001 -> 0.98 | yes |
  | weed_tuft | 60/300 -> 154/300 | 6 -> 3 | 0.785 -> 0.43 | yes |
  | litter_scrap | 24/200 -> 96/200 | 4 -> 2 | 0.929 -> 0.55 | yes |

  `rubble_frag` is built by slicing with half-space planes and capping the
  cuts, because broken rock IS an intersection of half-spaces; jittering a
  cube's eight corners only ever produced a parallelepiped. `weed_tuft` blades
  have stations along their length so they can curve, which a cone cannot.
  `pebble` draws its three extents as a proportion (Zingg 1935) instead of
  independently, so the population lands where real gravel lands rather than
  defaulting to equant lumps.
- **`pebble` and `rubble_frag` bevel to 0 in every style.** Measured on
  pebble, the bevel cost 238 of 430 triangles and changed `normal_regions_80`
  by zero — it was spending 55% of the budget on edges that carry no
  silhouette at two metres.

### Notes
- `validate.py` still defaults a missing triangle budget to 0. Whether an
  unbudgeted species should warn or hard-fail is a policy call and is left
  open rather than decided silently here.
- `dim_width` printing `0.045m within [0.050, 0.300]m` as a PASS is the
  `tol = 0.02` grace at `validate.py:21`, not a broken check. The message is
  what misleads. Left alone.

## [0.36.0] - Plates, modules, honest cover UVs, and three visual themes

NUMBERING. This jumps 0.31.0 -> 0.36.0. Tags `v0.32.0` through `v0.35.0`
exist and point at real releases -- `v0.32.0` is the enriched kit index
and slot-fit authority, `v0.33.0` is the Phase 1 structural species
(stair_rail, ladder, wallCorner, shelving, counter) -- but their
CHANGELOG entries did not survive a version reset that took VERSION
backwards to 0.31.0. Today's work therefore starts above all of them
rather than landing on numbers that already mean something. The two
entries written on 2026-08-14 under 0.32.0 and 0.33.0 are both here.

### Themes
- **center_city** (polished commercial: low wear, cooler/lighter, clean
  materials) and **industrial_flats** (port/works: high wear, desaturated
  iron tones, metal-first) join **delco** in every species genome (46) --
  deterministic derivations of each species' anchor style, resolved through
  the standard _pick_style_tag/resolve_module_plan path. 205 tests green.

### Changed
- **Floor and ceiling skins build as plates**, carrying the slab's holes in
  them (`a03617a`).
- **Openings cut the slot's authored aperture** instead of genome fractions,
  and tag it in the stem (`b919677`). The authored number is the one someone
  decided; a fraction of a genome is one nobody did.
- **Facade relief carves into the wall module** instead of standing boxes
  proud of it (`56a1fc6`).
- **A prop species is a solid themed box at a DC volume's exact dims**
  (`13b8b2a`), and `test_genome` treats prop as an ARCH species -- DC
  slot-driven, not a modelled prop (`0b61689`).
- **A structural slab is never see-through**, and the planned glazing kind is
  delivered to the pane rather than assumed (`d2a8ff3`).
- **Theme styles resolve by family prefix**, and the rockay wall relief is
  quieted (`cf8c3e8`).
- **`panel_field` proud 0.03 -> 0.012** (`5f7b898`).

### Fixed
- Covers orient by the anchor tangent, not the normal alone (`e2c6160`).
- Dressing carries ambient from the style block into the cover build
  (`f7ee3e2`).
- Skinned covers exported `COLOR_0` as flat white (`26728c7`).
- The wear layer was computed and never exported (`c26670a`).
- Every cover projected its UVs from the same local box (`3f18b6a`).
- Conduit span still scaled a hint that had become a measurement (`ad9b111`).

### Docs
- `dress_cover` claimed its UVs came from `uv_region`; they come from a cube
  projection (`ebdb924`).
- README points at `PIPELINE_MAP.md` and states what this repo owns
  (`abbe1db`).

Assembled on 2026-08-14 from this repo's own commits, seventeen of them since
VERSION last moved, after `verify-manifest` reported zoo STALE. One commit in
that range is not represented above: `5bbe380`, "checkpoint: uncommitted
working tree", which says nothing about itself. It is the same shape that is
currently holding `pipeline` at STALE.

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
