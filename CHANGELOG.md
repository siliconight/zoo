## [1.74.0] - an Empty's TV antenna and satellite dish

The comps' rowhome has "a TV antenna on the roof", and the street has "the
odd early satellite dish". From across the road an Empty's roofline was a
flat parapet edge against the sky.

Deli Counter (>= 0.185.0) authors which houses have them. Patina (>= 0.29.0)
orders them on the roof, set back from the front parapet. Both are built
here, as two new covers.

- **`tv_antenna`** (`core.dressing.antenna_parts`), a 1990s VHF/UHF aerial
  on a mast:
  - a plate on the roof, and the mast up from it;
  - a boom across the mast's top, 40 % of it behind the mast;
  - an element about every 20 cm along the boom, tapering from 1.6 m at the
    back (the reflector) to 36 cm at the end that points at the
    transmitter, which is local +x, the order's tangent;
  - `size2` is [boom, mast];
  - drawn about twice real thickness, as the gutter's sheet is, so a 2 cm
    tube holds at street distance.
- **`sat_dish`** (`core.dressing.dish_parts`), an 18-inch DSS dish:
  - an oval 46 x 50 cm on a pole on a roof plate;
  - its bowl looks along the tangent, tilted up 41 degrees: Philadelphia's
    elevation to the DSS satellites at 101 W;
  - the recipe builds the head (bowl, feed arm, LNB) level and tilts it
    about the bowl's centre;
  - `size2` is [width, the bowl's height above the roof].
- **Both are `METAL_COVERS`**, the gutters' white aluminium. On a side that
  has a gutter, downspout or air conditioner, they merge into that side's
  metal mesh. Up-facing, each takes the side it stands nearest, which for a
  fixture set back from the front parapet is the front.

**Price, expected:** no new mesh where the front already has white metal,
which on every rowhome Empty it does (gutter and downspouts). To be measured
in the cold run.

**The cheaper choice, and what the other would buy:** a bare-aluminium
material would give the antenna a metallic sheen where a lamp catches it,
for one more surface per house.

## [1.73.0] - a house's own brick

The walker's South Philly photograph: "every house a different brick:
brown, red, orange". A theme holds one grammar per kind, so Pixelcoat
(>= 0.57.0) paints the brown and the orange as kinds of their own,
`brick_brown` and `brick_orange`. Deli Counter (>= 0.183.0) builds two of
its rowhome Empties in them.

- **`skins.KNOWN_KINDS` lists both.** `dna.resolve_module_plan` keeps a
  slot's material only when it is listed. A kind missing from the tuple
  builds in the genome's default and says nothing, which is how
  `carpet_club` once came out concrete.
- **`materials.ROUGHNESS` gives both a brick's 0.90.** `test_kind_vocabulary`
  holds the two tables to the same keys.
- **A wall in a house brick carries it in its name** (`_mbrick_brown`,
  `_mbrick_orange`). Two houses of one wall size in different bricks are
  different modules.

## [1.72.0] - an Empty's front door: painted per house, and an iron security door

The walker's photographs (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"):
- the South Philly row paints its doors house by house;
- one carries "a black iron security door with a grille".

Deli Counter (>= 0.182.0) authors each Empty's front-door finish and
security door. Patina (>= 0.28.0) orders the security door.

### Added
- **`core/doors.py`, `FINISHES`**: navy, oxblood, green, black, white,
  stained. Each is a skin kind and its tint: the paints are `metal_painted`,
  whose `metal_painted_neutral` pack is achromatic and tintable, and
  `stained` is the wood the leaf always wore. The order is the contract with
  Deli Counter's `empty_panes.DOOR_FINISHES`.
- **The finish rides in the module's name as `_e<finish>`** (`kit.module_stem`),
  after the pane's `_p`; `_d` is the depth's. `plan_kit` reads it only off a
  facade doorway and only when it is a known finish; `dna` carries it to the
  recipe. Two facade doorways of one size in different paints are different
  modules.
- **`_arch.build_slab` paints the leaf in it** (`doors.leaf_material`). A
  finish names its flat material for itself, so two painted doors built in
  one process cannot share the first one's colour through the material
  cache. No finish is the stained leaf, named as before.
- **`security_door`** (`dressing.security_door_parts`): hung in the
  doorway's reveal, 2 cm in front of the leaf and 2 cm behind the face.
  - Two stiles; three rails: top, bottom, and the lock rail at handle height.
  - Uprights about 11 cm apart, and a lock box.
  - In the bars' black iron (`IRON_COVERS`), so on a side with barred
    windows it merges into their mesh.

### Corrected
- **`FACADE_DOOR_COLOR`'s navy never showed.** It was the flat colour, and a
  skinned `wood_panel` takes no tint, so every Empty door rendered brown.
- **Cost:** a finish costs no draw. A doorway module is drawn once per
  placement either way. The comment that said per-house colour would have
  to be instance data now says why it is not.

## [1.71.0] - an Empty's stone lintels and sills

The walker's South Philly photograph (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"): "white stone lintels and
sills over and under every window". Patina (>= 0.27.0) orders a `lintel` at
every facade opening's head and a `window_sill` at every facade window's sill
line, and `dress_cover` builds them.

### Added
- **`lintel_parts`**: one block standing on the head.
  - 20 cm tall, bearing 10 cm into the brick past each jamb, 2.8 cm proud.
  - That keeps it behind the bars, whose uprights run up past the head
    3.1 cm off the wall.
- **`sill_parts`**: one block hung below the sill line, 7 cm deep and 6 cm
  proud so it reads as a ledge, 5 cm past each jamb.
  - The bars' feet and the air conditioner's brackets pass into it, as
    theirs are anchored in a real one.

Both stand 1 mm off the wall face.

- **In `plaster` (`STONE_TRIM_COVERS`).** Pixelcoat's `plaster_delco` is
  cream and matte, the nearest skin to the photograph's white stone that a
  cover already offers.
  - **Cost, to be priced:** one more material, so one more surface on each
    side of a building that has openings.
  - **The cheaper options:** the covers' own concrete (grey) or the gutters'
    painted white (semi-gloss) would merge at no draw.

## [1.70.0] - no groove at a storey seam

### Fixed
- **Short pale-then-dark dashes along the storey line of an Empty's wall.**
  Seen on the stone rowhome's end wall in cold runs 9153, 9154 and 9155, at
  regular spacing.
  - **Measured on 9155's own module GLB**
    (`wall_delco_1997_01_w200_h310_mstone_idrywall.glb`). The panel's ends
    are square: 0.81.1's butt planes. Its top and bottom edges still carried
    the style's 3 mm x 3 mm chamfer: vertices at +-1.547 against the face's
    +-1.550.
  - **Where it showed.** An Empty stacks storey on storey; Deli Counter
    0.175.2 gives gs_empty_rowhome_d's end wall 0.0-3.1 then 3.1-5.9. So two
    chamfers met as a V 6 mm wide and 3 mm deep along the whole seam.
  - **Why dashes.** The frames' camera is 65 degrees vertical at 1152 x 648,
    so a pixel 10-15 m away covers 18-26 mm and the groove is a quarter to a
    third of one. A sub-pixel line at a slight slope aliases into regular
    dashes. The up-facing facet caught the fill light and the
    down-facing one did not, hence pale-then-dark.

  It is the same groove 0.81.1 removed from a run's vertical joints, turned
  on its side.

### Changed
- **`arch.butt_planes(species, w, h)` takes the module's height.** A run
  module's butt planes are its two ends plus its top and bottom
  (`z = +-h/2`).
- **Why the top and bottom count as joints.** In Deli Counter's model they
  always meet something:
  - the next storey's module, flush, on an Empty;
  - the slab's edge on an enterable building (bank_tower_a02: 0.0-4.3, the
    slab, 4.6-8.9).

  The height is required, so a caller cannot silently keep the old pair.
  The corners a person can see keep their chamfer: a jamb's reveal, a sill,
  a header's underside.

### Corrected
- **`butt_planes` said the top and bottom of a face "are not on these
  planes and keep their chamfer"** as real corners.
  `test_butt_joints.py` pinned it twice:
  - the top edge "lies in neither";
  - the built wall "keeps its top".

  Both pins are reversed, and each says what it used to assert.

## [1.69.0] - an Empty's windows: an air conditioner, bars

The walker's window photographs (the factory root's
`docs/reference/EMPTIES_COMPS.md`, "Window comps"):
- "window air conditioners in nearly every photograph": a white or beige box
  in the lower sash, standing out of the wall, so geometry;
- bars "proud of the frame on bolted straps". They were painted into the
  pane.

Patina (>= 0.26.0) orders both from the slot Deli Counter (>= 0.181.0)
marks, and `dress_cover` builds them.

### Added
- **`ac_unit`** (`dressing.ac_parts`): a 1990s 6,000 BTU window unit,
  52 x 36 cm, standing on the sill.
  - It stands 30 cm out of the wall and reaches back through the reveal to
    the pane, 13 cm behind the face.
  - Parts: fins across its back, which is the side the street sees; louvres
    down its flanks; accordion panels closing the sash out to the jambs; two
    L brackets under the overhang.
  - White painted metal: the gutters' material and colour. Since 1.68.0
    merges a building's covers per side per material, a unit on a side with
    gutters adds no draw call.
- **`window_bars`** (`dressing.bar_parts`): 18 mm square uprights about
  12 cm apart, standing 4 cm off the wall and running past the head and the
  sill.
  - Two flat straps behind them reach past the jambs onto the brick, bolted
    on standoffs.
  - Black painted iron (`IRON_COVERS`): the same painted metal in a second
    colour, so one more surface on a side that has bars, however many
    windows they cover.

Every part of both stands at least 1 mm off the wall face, and touching
parts overlap rather than share a face.

### Changed
- **A barred pane paints only its room.** The bars are geometry now, 3.5 cm
  off the wall with the pane 13 cm behind it. Painted as well, they drew a
  second grid that slid against the real one as the eye moved. `lit_bars`
  and `dark_bars` keep their names (Deli Counter's mix and the module stems
  ride on them) and now paint exactly `lit`'s and `dark`'s rooms.
  `_bars` and `BAR_RGB` are gone.

### Corrected
- **`METAL_COLOR` said it was "the flat colour, used only with no skin
  library".** It is also the tint. `make_material` tints a tintable pack and
  names the material for it, which is the `_dbdbd4` on every shipped
  gutter. The bars' black works for the same reason.

### Cost, to be priced
- **The unit:** none expected on a side with gutters.
- **The bars:** one surface per barred side.
- **Not done:** the NYC bellied grille that takes a unit behind it, and the
  cage around a unit. No unit is placed behind flat bars (Deli Counter).

## [1.68.0] - a building's covers merge, one side at a time

Patina's covers -- curbs, base courses, edge strips, conduit, gutters and
downspouts -- reached the level as one mesh each: one draw call for every
visible cover. Measured on cold run 9154's package (roadmap 180):

- **Count:** 3,370 cover instances in gas_block_001, because the six rowhome
  Empties are placed 26 times.
- **Hiding them all:**
  - the worst view goes from 8,690 draws at 27.33 ms p95 to 5,571 at
    17.74 ms;
  - the median view drops 850 draws and 2.06 ms;
  - the control (the same package measured twice) moved 0 draws and 0.05 ms.

### Changed

- **`build_dressing` merges a building's covers, ONE SIDE OF THE BUILDING
  PER MATERIAL** -- through the same `merge.pack_by_material` every module
  goes through. On the rowhome that is 103 covers into at most 8 meshes.
  Never one mesh a building: the export culls by occlusion (1,407 box
  occluders on 9154), and one mesh holding a building's front and back
  covers keeps the back drawn whenever the front is seen. A side enters and
  leaves view together.
- **The side is decided in `core.dressing`, pure** (`cover_side`,
  `footprint`, `SIDES`, a `side` on every plan). Facings are Deli Counter's:
  N = +y, E = +x, S = -y, W = -x.
  - **A wall-facing cover** takes the side its normal leaves.
  - **An up-facing cover** -- a curb at the wall's foot, an edge strip on
    the roof, 60 of a rowhome's 103 -- has no side of its own. It takes the
    side it stands nearest, measured in units of the footprint's half-size,
    so a long building's end curbs go to its end and not its flank. Grouped
    by normal alone, every curb and roof edge of a building would have been
    one mesh the size of the building.
- **Covers are built in place.** Each cover's placement is baked into its
  vertices and its object is left at identity. The merge reads raw
  coordinates and leaves any object with a transform unmerged
  (`merge._identity`), so a placed cover could never have joined a group.
  The placement is a yaw and a translation; nothing it bakes changes a UV, a
  colour or a shading edge, all of which are written before placement.
- **The group is the name.** `dress_cover` names a cover
  `Cover<side>_<kind>`; `partnames.family` is everything before the first
  underscore, so the family is the side. A merged mesh is
  `Cover<side>_<material slug>`, e.g. `CoverN_concrete_delco_1997`.
- **`--no-merge-parts` reaches the dressing**, as it reaches kits: one
  build, the merge off, as the control. `build_dressing` reads
  `merge_parts` like `build_module`, and its result and index carry the
  merge's stats (`merge`) and the count a side (`sides`).

### Corrected

- **`build_dressing` said covers were "already handled downstream"**:
  Level Factory's `extract_meshes.gd` was to merge them "per visible chunk".
  It does not. That script belongs to the surface-clutter layer; the only
  Level Factory code naming `_dressing.glb` is the worldskin's tiling list,
  and the census showed every `Dressing/Cover_*` as its own MeshInstance3D
  (Patina notes on cold runs 9147 and 9152).
- **1.67.0's own cost note repeated it**: "Level Factory merges covers per
  visible chunk and per material". It was wrong for the same reason.
- **That comment's worry was right.** Welding opposite faces of a building
  into one bounding box trades their culling. It is why the unit is a side
  and not the building.

### Not done here, said so

- **`tools/dressing_in_nav.py`** at the factory root tested each
  `Cover_*` mesh's box. After this a mesh is a side, and the name no
  longer starts `Cover_`. That tool is changed in the same breath: its
  prefix matches both names, and it refuses to report a clean result when
  it found no cover at all.
- **The price is a cold run's**: draws and frame time at the same
  stations, A = 9154, B = the merged run, A2 = 9154 again. Also re-read:
  - the lights-per-object census, because a merged side is touched by more
    lights than one cover;
  - the lightmap bake.

## [1.67.0] - a gutter that reads as a gutter, a downspout, painted metal

The walker, 2026-10-04: "also we need rain gutters". Patina has ordered a
`gutter_run` under every roofline since its 0.18. Zoo built each one as a
solid box, 10 cm proud by 14 cm tall, centred ON the wall face -- so half of
it stood inside the wall -- in the concrete every other cover wears. From the
street that is a ledge, not a gutter. Patina 0.25.0 adds `downspout` orders,
which nothing built.

- **The gutter is an open trough off the wall face** (`gutter_parts`):
  - a back on the wall;
  - a floor;
  - a front a little lower than the back (`GUTTER_FRONT`);
  - a rolled bead along the front's top.

  Nothing spans the mouth, so street level sees a lip and its shadow. Every
  part runs the full span, so sections butt at module seams.
- **The downspout** (`downspout_parts`, `_COVER["downspout"]`):
  - a 3 x 2 inch leader on a 2 cm standoff;
  - two straps;
  - a cast boot at the ground, where a Philadelphia rowhouse's leader goes
    into the sewer.

  The boot also means no elbow kicking out across the sidewalk: non-collision
  geometry in walkable space is what panel fields were removed for.
  `strip_size` runs it up the wall like a conduit.
- **Both are painted metal** (`METAL_COVERS`): `dress_plan` gives them
  `metal_painted` when the `dress_cover` genome offers it, which it now does.
  `delco_1997` maps that kind to Pixelcoat's `metal_painted_neutral`. A
  genome that does not offer it keeps its default.
- **The metal split, for `dress_cover`.** `test_material_options_closed`
  holds that a species offering a split kind offers no raw `metal` and no
  style names it: raw `metal` resolves the theme's own pack (delco_1997's is
  rusted street metal) and ignores the genome colour. So:
  - `dress_cover` offers `concrete`, `plaster` and `metal_painted`, and is
    declared in that test's `PAINTED`;
  - the two styles whose every cover was raw `metal`, `center_city` and
    `industrial_flats`, move to `metal_painted`, since a metal facade trim is
    painted flashing.

  That is a look change in those two themes; `delco` and `delco_1997` covers
  stay concrete.

Both new shapes are pure part lists, as `frame_strips` is, tested without
Blender. Every other cover is built exactly as before.

**Cost.** The painted metal is a second cover material per building.
Level Factory merges covers per visible chunk and per material, so it can add
a draw per chunk that holds gutters. It is priced on the cold run that ships
it, against the run before.

`tests/test_gutters.py`:
- a gutter is an open trough standing off the wall (fails on 1.66.0);
- a downspout stands off the wall into a boot at the ground;
- `strip_size` runs it up the wall;
- gutters and downspouts are painted metal, and the rest are not;
- the control: a genome without the metal keeps its default.

## [1.66.0] - a painted pane shows its picture on both faces

Cold run 9151 shipped the painted windows (1.64.0, 1.65.0). They import
with emission and bind to Lux. But from the street every pane read as flat
beige and none glowed.

Measured by the factory root's `patches/lf_empties/pane_face_probe.gd` on
9151's walk copy, on the Empty at x 1.55:
- the face carrying the atlas cell has world normal (0, 0, +1), into the
  house;
- the face toward the street carries the frame point.

`_arch.build_slab` mapped the cell onto the pane's local +Y face on the
assumption "+Y is outdoors". That holds for a wall module through its
placement; for these windows as placed it does not.

Both big faces now carry the cell, so the answer no longer depends on how a
module is turned. Each face reads unmirrored from its own side: looking
along ``d`` with up +Z the viewer's right is ``d x up`` -- -X from the +Y
side, +X from the -Y side -- and ``u`` runs toward it on both. The thin
edges take frame paint.

The mapping is a pure function, `window_panes.face_uv`, with `frame_uv`, so
it is tested without Blender; `_arch` calls it per corner. The material, the
atlas, the states and the module names are unchanged.

`tests/test_window_panes.py`:
- both big faces carry the cell and the edges take frame paint, which is
  painted where the frame UV points (fails on 1.65.0: no `face_uv`; the
  behaviour it pins is the defect 9151 measured);
- each face reads unmirrored from its own side, and up is up on both.

## [1.65.0] - colour variation in the painted windows

The walker sent window photographs (a night facade of lit rowhouse and
tenement windows, three street rows by day) and said "color variation is
key". 1.64.0 painted every lit window one warm tungsten. The night
photographs show at least four room lights -- tungsten yellow, the deep
orange of a curtained room, a pale cool fluorescent, a pink lampshade -- and
as many coverings: blinds, a roller shade pulled past half with the light
below it, curtains. The day rows add the green roller shade, closed blinds
and a box fan in the lower sash.

`core/window_panes.py` now paints sixteen states on a 4x4 atlas, 192x320:

| | states |
|---|---|
| lit | `lit`, `lit_amber`, `lit_cool`, `lit_pink` |
| lit, covered | `lit_blind`, `lit_blind_cool`, `lit_curtain`, `lit_shade`, `lit_bars` |
| dark | `dark`, `dark_blind`, `dark_shade`, `dark_curtain`, `dark_bars`, `dark_fan` |
| vacant | `boarded` |

Still one image pair, one `M_Window_pane_Face` material, glow only where room
light shows: the variety is UVs and costs no submission.

The window air conditioner every photograph shows stands out of the window,
so it is geometry, and it is not painted here.

`tests/test_window_panes.py`: the atlas has sixteen states and at least four
room lights. The earlier tests hold unchanged.

## [1.64.0] - an Empty's window is painted: lit, dark, curtained, barred

Cold run 9150 put the rowhome Empties across a street with real walls, roofs
and shut doors. At night they read as a black mass outside the streetlight
pools: every window was one opaque `glass_facade` pane. The walker's comp
for this (a Vampire: The Masquerade -- Bloodlines street, 2026-10-04: "I
think its actually ok to have lights on in the windows at night to show
life") is read off in the factory root's `docs/reference/EMPTIES_COMPS.md`,
"LIT WINDOWS AT NIGHT": mixed per building, most dark, some lit warm, many
lit ones behind bars, curtains and blinds, no real lights.

`core/window_panes.py` paints ONE ATLAS of eight states:
- `lit`, `lit_blind`, `lit_curtain`, `lit_bars`;
- `dark`, `dark_curtain`, `dark_bars`;
- `boarded` -- the 1990s vacant rowhouse.

Each cell is a rowhouse window: a painted-wood frame, a double-hung sash
with a meeting rail, six-over-six muntins. It is painted twice:
- an albedo;
- an EMISSION image that is black wherever the room light does not show --
  frames, muntins, bars, plywood. Blind slats and curtain fabric let a
  little through.

Glow taken from the albedo would have lit the plywood and the curtains.

A facade window slot carrying `pane` (Deli Counter >= 0.179.0):
- is named `_p<state>`, keyed on it, and carries it to the plan;
- `_arch.build_slab` UV-maps the pane's street face to that state's cell;
- `materials.make_pane_material` makes `M_Window_pane_Face` from the two
  images, so Lux's emissive binder darkens every lit window in the power
  cut.

An enterable window, or a state the atlas does not know, is built exactly as
before.

**Cost.**
- Every Empty window wears the same material, so the variety is UVs and
  costs no submission. Each window was already its own mesh.
- One 192x160 atlas pair is packed into each painted window module.
- No light.
- A lit window glows by day too. That is accepted, the game being mostly
  night, and recorded here rather than solved.

`tests/test_window_panes.py`:
- the atlas is the same bytes every build;
- only lit cells glow;
- each state's UVs sit inside its own cell;
- two states of one window are two named modules (fails on 1.63.0);
- controls: an enterable window and an unknown state are named as before;
- the state reaches the build plan;
- under Blender, a painted pane wears `M_Window_pane_Face`.

## [1.63.0] - a module is grouped no finer than the name it is given

Cold run 9149 stopped at art on its first blocking `ZOO_STEM_COLLISION`.
The freight terminal's parapet tiles -- wall slots since Deli Counter
0.177.0, cut at millimetre-snapped lines -- were 4.514 and 4.515 m (and
4.909 against 4.910). `plan_kit` grouped exact-fit slots by dims to 0.1 mm
and named them in whole centimetres, so it made two modules under one name,
`wall_delco_1997_04_w451_mmetal`, and 1.62.0 refused the kit.

That refusal was correct by its own definition. The defect was one number
asked at two resolutions: Deli Counter 0.177.0 had moved its own name check
to centimetres for exactly these tiles, and this side's grouping had not
moved. A group finer than the name it is given is a collision by
construction.

`dims_key` is now whole centimetres. Two slots a millimetre apart are one
module, built to the first slot's dims; neighbouring parapet tiles meet
within a millimetre. A difference the name cannot carry at that resolution
-- 2.8 against 3.1 m without `fit.key_height` -- still collides and is still
refused.

`tests/test_bucket_at_name_resolution.py`:
- a millimetre apart is one module (fails on 1.62.0);
- the control: a real height difference collides unmarked and splits
  marked.

## [1.62.0] - a kit that gives two geometries one name is refused

`plan_kit` has detected a stem collision -- two modules planned with
different geometry under one filename -- since it was written, and printed
`STEM COLLISION ... one will overwrite the other`.

Cold run 9148 printed it in all six rowhome Empties' kit logs: 2.8 m and
3.1 m walls and windows under one name each. `--build-kit` exited 0, the
2.8 m module stood in every 3.1 m slot, and the frames showed a strip at each
storey line. 1.60.0 and Deli Counter 0.176.0 removed that collision. This
release makes the next one stop the run instead of shipping:
- `stem_collisions` goes into `<building>_kit.built.json` beside `n_fail`,
  and into the result;
- `zoo_cli --build-kit` exits 2 on a collision, as it does on a failed
  module (`kit_exit_code`), with a `REFUSED` line per stem.

Measured beforehand: on 9148's library, only the six Empty kits had any
collision. With Deli Counter 0.176.0, none do.

`tests/test_kit_refuses_collision.py`:
- the plan still names the collision;
- a collision fails the build (fails on 1.61.0);
- the controls: a clean kit passes, and a failed module still fails.

## [1.61.0] - an Empty's door is shut

Deli Counter 0.174.0 made an Empty's doors solid in collision. The doorway
module drew the frame and its trim and no leaf -- a leaf existed only for a
storefront door -- so every Empty showed an open doorway into a dark box,
and a player walked into it as an invisible wall. Cold runs 9146-9148's
`empties_one_front_*` frames show it.

Deli Counter 0.178.0 tags an Empty's doorway `glazing: "facade"`, the tag
its windows have carried since 0.80.0. `dna` already turns that tag into
`glazing_kind: "glass_facade"`, and `kit.plan_kit` keeps it in the module
key. `_arch.build_slab` now fills a doorway so tagged with `Doorway_Leaf`
(a part the doorway genome already names):
- **Look.** A painted panel door, `wood_panel` kind, navy -- one of the
  rowhouse comp's three door colours.
- **Placement.** Set back `FACADE_DOOR_SETBACK` 0.08 m from the street face,
  `FACADE_DOOR_THICK` 0.045 m thick.
- **No collision of its own.** The wall's box already holds.

An untagged doorway -- every enterable building's -- is unchanged.

**Cost.** One mesh and one material more per Empty doorway: two a house, 52
on cold run 9148's site, until the Empties are merged per material (roadmap
106, open). Per-house door colour is the next step, and it belongs in
instance data, not a material per colour.

`tests/test_shut_door.py`:
- a tagged doorway plans as a facade opening (runs anywhere);
- under Blender, a tagged doorway builds a `wood_panel` leaf and an untagged
  one builds none.

Proven through the pipeline's own path: `zoo_cli --build-kit` on
`gs_empty_rowhome_f`, before and after.

## [1.60.0] - a slot marked `fit.key_height` names its height

`module_stem` names a wall, doorway or window by its width alone. The
docstring gives the reason -- "its thickness and the storey height are
fixed, so `_w<cm>` is a complete key". Deli Counter 0.175.2's Empties are the
first buildings where that is false:
- their walls run the full 3.1 m storey where no slab sits above;
- under the roof they stop at 2.8 m.

Cold run 9148's kit for `gs_empty_rowhome_f` listed
`wall_delco_1997_01_w200_mbrick_idrywall` twice -- two buckets of 11 slots,
two heights, one file -- and the module on disk was 2.8 m. Every 3.1 m side
wall got a 2.8 m panel: a 0.3 m strip at each storey line, which the frames
showed. The buckets were already split by their exact dims; only the name
was shared, and the later build overwrote the earlier.

Of the library's buildings, only the 8 facade shells have a wall name
covering two heights. So height is not added to every wall: that would
rename every wall in every building to fix eight.
- Deli Counter (>= 0.176.0) marks each slot whose name covers two heights
  with `fit.key_height`.
- Here `height_cm` joins the name when the slot is marked.
- Unmarked, every name is as before.

`themed_tscn.resolve_themed_stem` in Deli Counter is the mirror and changes
in the same release.

`tests/test_key_height.py`:
- two marked heights build two named walls (fails on 1.59.0);
- the control: an unmarked wall keeps its name.

## [1.59.0] - a car's paint rides its vertices

Cold run 9141 priced the parking fields (Lot 0.94.0) on and off on one
package: 17 cars cost +33 draws a heading and +0.15 ms of median frame,
about 11 draws a visible car (`docs/cold_runs/cold_9141/NOTES.md`). A built
car was 10-12 meshes on 9-11 materials, and six to eight of those
materials were ONE pack, `metal_painted`, in as many colours -- the body's
paint, the brightwork, the head, tail and corner lamps, the plate, the
cladding, the grey bumper -- because a tintable pack makes one material per
colour (`materials.make_material`), and `merge.pack_by_material` packs
parts into one mesh per material, never across. That is the colour-only
variation `CLAUDE.md`'s draw-call rule names first, and 1.8.0's
`geometry.tint_wear` is the path that rule asks for.

`car_forms.paint_tints(form, body_kind)` names every painted part and its
colour: the body's paint (when the genome's body kind is `metal_painted`;
a `plastic` body is another pack and keeps its material), the cladding,
and `FIXED_PAINT` -- the brightwork, lamp, plate and bumper colours the
recipe used to pass `make_material`, moved here so a test holds them. The
recipe gives every one of those parts ONE material, `M_Car_painted` at
`car_forms.PAINTED` (white), and multiplies each part's colour into its
`Wear` attribute. A part whose `Wear` layer is missing is refused rather
than shipped white. Level Factory's import (`zoo_worldskin.
_vertex_colour_albedo`) already draws COLOR_0 as albedo on any material
some surface of which is not white, and glTF's base colour is
factor x texture x COLOR_0, so the product is the one the material's own
factor made.

MEASURED on the eight distinct cars of cold run 9141's site, built from its
own slots, skins and seed by 1.58.0 and by this
(`patches/zoo_car_paint/colour_check.py`):

    materials a car     9-11 -> 4  (paint, interior canvas, rubber, glass)
    meshes a car       10-12 -> 5
    triangles          identical, car by car
    base colour        every painted corner, matched by position (0 of
                       852-980 positions unmatched a car): worst
                       |delta| 0.0036, under one 8-bit step -- the tint
                       key's hex rounding
    control            the same cars read as if the tint never landed:
                       worst |delta| 0.9819

The first control written for this check whitened only VEC4 colours, the
exporter writes COLOR_0 as VEC3, and it read the same 0.0036 -- a check
that could not fail. Kept in the tool's comments above the one that
replaced it.

Paid, and said: a lamp lens now shares the paint's material, so a lamp
renamed to light at night (the recipe's note on `_Lens` suffixes) has to
leave it again; wear and tint now share COLOR_0 and cannot be told apart.
The price in a level is the next cold run's.

`tests/test_car_forms.py`: every painted part keeps the colour its own
material carried (literals); a plastic body keeps its own; the recipe
paints with one material, tints the wear, refuses a part with no `Wear`
layer, and every group a tint names is a group it builds.

## [1.58.0] - the dumpster

The walker, 2026-10-03, with two photographs of front-load containers
beside a gas station and a farm lane: "we should have some trash dumpsters
next to buildings (sides or back where its not in the way of where
customers would naturally walk into the building)". Zoo had no such
species; Deli Counter's cover vocabulary has named one since its first
level design and got a box.

`dumpster`: a steel tub whose front leans out toward the top and sits
lower than its back, a rim bar under the lids' front edge, a fork pocket
down each side, two black ribbed plastic lids sloping from the hinges to
the front, four casters (`core/dumpster_forms.py`). 1.83 x 1.10 x 1.30 m at
the genome's default, a 3-yard container. The front is -Y: the low edge,
the sticker, the side a body walks up to; the hinges and the wall it backs
onto are +Y. Lot 0.90.0 stands one against a building's back or side wall.

ONE ATLAS, ONE MATERIAL, ONE DRAW, 92 triangles. Every face is a quad on
one painted image (`recipes/_card_atlas.build_art`, the ATM's route): the
fleet colour, rust run down from the rim, grime risen from the ground,
chips to bare metal, the lids' ribs and the sky's streak across them are
paint. `variant` picks one of four invented Delco haulers and with it the
fleet colour -- DELCO DISPOSAL (green, "WE TAKE YOUR CRAP"), JAWN HAULERS
(blue, "ONE MAN'S TRASH. PERIOD."), MACDADE REFUSE (maroon, "YOUS FILL IT.
WE DUMP IT."), TINICUM TRASH CO (orange, "SMELLS LIKE HOME") -- each with a
555 number on a white sticker in the maker's face and a yellow CAUTION /
KEEP OFF label in the notice face. A second hauler's dumpster is a second
image, never a second material on one mesh. The four paints are chosen to
stand off asphalt, brick and painted block: a prop a body walks into reads
against what is behind it.

`tests/test_dumpster.py`: the genome and the kit stem; the slot filled and
centred with no two faces on one plane at 27 sizes and four haulers; every
quad wound out of the thing it closes; the front leaning and lower than the
back; one atlas and every tile present; every line of every tile setting at
every size; the paints distinct and none a grey; the names invented (the
poster, card, club and beer denylists, real haulers, and the two on the
reference photographs) and every number on the fictional exchange; and,
with Blender, one object and one material in the GLB.

## [1.57.1] - the heat lamp goes up under the hood, above the buns

The walker, 2026-10-03, on the first cut walked (the rod hung under the bun
shelf, a downlight on the dogs): "light should show the buns too, not
seeing those". A real one hangs under the hood's top, above the shelf; so
does this one now, `HEAT_LAMP_DROP` under the hood's top, clear of the buns'
crowns by 3 cm or more at every size, with the marker under it. Lux 0.63.0
makes the lamp an omni, so the buns under it and the dogs through the glass
shelf both get it. The forms' test holds the clearance over the buns and
over the dogs.

## [1.57.0] - the roller grill's heat lamp

The walker, 2026-10-03, on a frame of the grill walked at night: "can we
add a dim but warm warming light to bring a bit more light to the dogs".
A roller grill has an infrared element under its hood, and that is the
cause the light hangs on.

What ships: a red-orange rod the width of the pan under a chrome trough,
hung `HEAT_LAMP_DROP` below the bun shelf where there is one and below the
hood's top where there is not, over the middle of the roller bank
(`roller_grill_forms.heat_lamp`). The rod is the grill's one LIT FACE,
`M_Roller_Lamp_Face` (`HEAT_LAMP_RGB`, `HEAT_LAMP_GLOW` 3.0): an emissive
entry through `prim_mesh`, no wear, a white COLOR_0, and the `_Face` suffix
Lux's binder cuts with the power. The prim list's facts carry an
attachment, `LuxEmit_heat_lamp`, `HEAT_LAMP_EMIT` below the rod's axis;
`build_module` makes every attachment an empty, so the GLB carries the
marker by name and `LuxFixtureSpawner` stands the lamp on it, which Lux
0.63.0's loader tunes (`heat_lamp`: 1,900 K, a third of a fluorescent, the
hood's reach). The trough's floor sits `BURY` into the rod: a flush contact
is a coincident pair, an overlap is not. The genome names `Roller_Lamp`.

Cost: one surface and one light a grill, priced in Lux 0.63.0's changelog.
The grill is seven submissions where it was six.

Built in Blender 5.1 with the delco_1997 skins: `M_Roller_Lamp_Face` lit
at strength 3, `LuxEmit_heat_lamp` at (0, 0.41, 0.00) in the module, the
rod inside the hood over the dogs.

Tests: the rod hangs over the dogs under the shelf or the hood and inside
the hood at every size; its two prims wear `chrome` and `lamp`; the
attachment sits `HEAT_LAMP_EMIT` under the axis; the bpy suite expects
seven submissions, one lit face named for the lamp, and the marker.

## [1.56.0] - the crown carries the wind's handle

The walker, 2026-10-03, on the wind design at the factory root
(`docs/proposals/WIND_DESIGN.md`): "start with the crowns". A street tree's
crown sways and its wood does not, and what Zoo ships is the HANDLE, not
the motion: every corner of the crown carries, in a second UV set `Sway`
(TEXCOORD_1), a WEIGHT -- its height above the crown's foot over the
crown's height, squared, so the top sways and the branch tips barely -- and
a PHASE of its own leaf cluster, stepped round the circle by the golden
fraction as the branches step round the trunk, so no two neighbours flap
in step. Level Factory 0.130.0's import gives the crown's skin a vertex
stage that reads both against the level's wind; nothing in Zoo moves.

`tree_forms.sway_weight` and `tree_forms.cluster_phase` are the two pure
functions; `street_tree._cluster` and `_small_cluster` return the vertices
they made so `_sway_layer` can say which cluster a corner belongs to. The
layer is written after the last correction that moves a leaf and before
the finish, with `UVMap` made first so the finish's projection keeps
TEXCOORD_0. A weight is a fraction of the crown's own height, so the
re-centring and the fit that follow cannot stale it -- the roller grill's
pivots (1.55.0) were positions and went 0.7 m stale; the test here reads
the shipped file against its own vertices anyway. The `cards` crown (behind
a param, not ready) carries no layer. The recipe reports
`street_tree.sway_clusters`.

Built in Blender 5.1 with the delco_1997 skins, a 5 x 5 x 6.5 London
plane: the crown's 1,891 corners carry TEXCOORD_1, every weight within
0.001 of height squared read off the shipped POSITION, 67 cluster phases;
the wood and the grate carry no second UV set. The crown's material is
unchanged (`M_Skin_vegetation_delco_1997`): the import, not Zoo, decides
what moves it, and a crown an older import meets is a crown as before.

Tests: the weight is 0 at the foot, 1 at the top and bends upward; a flat
crown does not divide by zero; phases step round the circle and never
repeat nearby; the bpy suite reads the shipped crown's weights against its
own height and finds the layer on the crown alone.

## [1.55.0] - the rollers turn, the dogs ride them, the slush churns

The walker, 2026-10-02, on the design for small things that move
(`docs/proposals/MOVING_PARTS_DESIGN.md` at the factory root): "start with
the roller grill, and i want some motion on the slurpee stuff too". The
rule the design set: a thing moves because something drives it. Both of
these are motors in a store that is open.

**The roller grill.** The rollers are a kind of their own now,
`metal_bare_turn`, and the dogs `metal_painted_turn`: a part that moves on
its own needs a surface of its own (`merge.pack_by_material` packs a kind
into one mesh, and one mesh is one draw), so the grill is six submissions
where it was four. Each roller and each dog is a prim that `prims.turning`
marks with its AXLE -- the axis it was built on, not a guess from its
bounds -- and `prim_mesh` writes that into a second UV set, `Pivot`
(TEXCOORD_1, the slot the shutters' schedule uses), in Blender's own axes
and the prim's own coordinates. Whatever moves the vertices afterwards
moves the layer with them: `core.pivot.recentre` shifts it by the module's
re-centring, `geometry.fit_to` scales it about the same centre. Only at
export (`export.pivots_to_engine`, after the merge) does it become the
engine's: glTF is Y-up, Blender's (y, z) arrives as (z, -y), and the v is
written flipped because glTF reads 1 - v. The material's name carries the rate,
because the UV set has no room for one: `M_Roller_metal_bare_turn_x36` is
36 degrees a second about +X, `M_Roller_metal_painted_turn_xn36` the other
way. Level Factory 0.129.0's import reads both and turns the vertices on
the shader clock; nothing in Zoo moves.

The rates: `ROLLER_RPM` 6, a countertop grill's low setting by eye against
a store's (a dog goes round in ten seconds). A dog turns BECAUSE the
rollers under it do, the other way, at their surface speed: its rate is the
rollers' times `ROLLER_R` over its radius, derived in `turn_rates`. One
material for every dog means one rate at the mean radius of the four kinds
(12.5 mm, which happens to be the roller's, so the two rates are equal and
opposite); the eye cannot tell a quarter-turn a minute on a 12 mm dog.

The turning kinds take the FLAT material path past any skin library
(`skins.find_pack` finds no pack of these names): the import's vertex stage
reproduces a flat material -- albedo times the vertex colour, roughness,
metallic, the same numbers as `metal_bare` and `metal_painted` -- and
would have to carry a textured skin whole. A roller is smooth chrome; the
grease is its tint, as before.

**The frozen drink station.** The slush tile painted its churn bands and
they stood still. The tile is the flavour's base with the ice through it
now, and the bands are DRAWN MOVING by the import: a darkening pass over
the barrel's churn facets walks the same diagonal (three bands round, one
and a half up) round the barrel once every `CHURN_PERIOD_S` (6 s). The
facets say where they are round the barrel in a second UV set, `Churn`
(u by segment, v up the band, both 0..1); every other corner of the glow
surface carries v = 2, which the pass reads as not slush. Darkens only, so
a machine whose power is cut stays dark under it; the light band the tile
used to paint is what that costs, and what it buys is the churn turning.
Zero added draws for the tile; the pass itself is one draw a machine,
priced in Level Factory 0.129.0.

**Two refutations the first builds found, kept.** The pivots were first
written in the engine's axes at build time and compared with the forms'
numbers, and the test passed while the shipped rollers swept through the
air: `build_module` re-centres a module after the recipe returns, the
vertices moved 0.7 m and the pivots did not (measured in the shipped
scene: vertex y 0.24..0.32 against pivot y 0.95..1.00). The layer now
rides with the vertices and the bpy test compares the pivots with the
VERTICES as shipped -- every roller corner one radius from the axle it
carries -- rather than with the numbers the recipe meant. And
`merge.pack_by_material` built
a merged mesh's UV layers in the signature's SORTED order, which put
`Pivot` before `UVMap`; glTF writes TEXCOORD_n in layer order, so the
pivots went out as TEXCOORD_0 and the projection as TEXCOORD_1 (280
distinct "axles" for 14 rollers). The layers follow the source's order
now. Nothing shipped before this carried two UV sets through a merge (the
shutters are one object), so nothing shipped was affected.

Built in Blender 5.1 with the delco_1997 skins: the grill's two turning
primitives carry TEXCOORD_1 with fourteen distinct axles for fourteen
rollers, every roller vertex 0.0125 m from its own and every dog vertex at
its kind's radius; the slush's glow carries TEXCOORD_1 with (u, v) in 0..1
on its side facets and v = 2 everywhere else.

Tests: the rollers and the dogs turn about their own axles and nothing else
does; the dogs' rate is derived and opposite; the material name carries
axis and rate; the turning kinds match their flat tables; `turning` is set
on the final prim and refuses an axis nobody writes; the churn tile is the
flavour and its ice and no band; every churn corner says where it is round
the barrel; the re-centring moves a stand-in mesh's pivot layer with its
vertices; the bpy suite expects six submissions, TEXCOORD_1 on the turning
primitives only, and every shipped vertex one radius from its own axle.

## [1.54.0] - one price faces the customer

The walker, 2026-10-02, on a frame from cold run 9137 with the hump's
display crossed out: "i think we only need 1 set of numbers/face of the
price per register facing the customer". The till on the store and bar
counters (`counter_register`) showed the customer two prices -- the hump's
front and the pole over it.

### Changed
- **The hump's customer window is gone.** A till is two lit windows: the
  pole's, facing the customer, and the hump's back, facing the clerk. The
  hump's front is plastic. The display image carries two regions where it
  carried three.

### Cost
One quad fewer a till; the same two objects and materials on a counter.

## [1.53.0] - the roller grill: its panels drawn and lettered by owner

The last of the store's counter props in the pixel look (the walker,
2026-10-02). The warm-buns panel across the cabinet, the grill's control
panel and the tags on the rollers.

THE BRIEF. The buns panel is the shop's joke, printed on card and slid into
the cabinet's front: the shop's face, a dog each end, red rules. The control
panel and the tags are the grill maker's: dials with their scales, two
lamps, a switch, the kinds named on black tube tags. What is left out:
grease on the panel -- it is below the pan; the grease is on the rollers,
in their `Wear`, as it was.

### Changed
- **The hot dog in its bun is drawn** (`_dog_in_bun`): two halves of a bun,
  the dog between, a squiggle of mustard -- where it was a 12 x 6 bitmap.
- **The dials have scales and the lamps have lenses**: rings in curves, a
  tick every 45 degrees, a highlight on each lamp, a bevelled switch.
- **The lettering has owners** (`smooth_type.OWNERS`): NICE BUNS in the
  shop's face with a brown outline and WARM ALL DAY in the shop's copy
  face; the tags in the maker's. 1.17.0's `monogram` and `m5x7` are gone.
- The image is packed by `card_art.atlas` with gutters each tile bleeds
  into, and sampled with filtering. Same densities as before (`TEXEL` 400,
  `TAG_TEXEL` 800).

### Cost
The image for the 1.0 m grill is 395 x 401 px where it was 368 x 305: the
gutters. One material, now Linear; no draw changes (the four submissions of
1.17.0). Level Factory 0.128.0 ships a filtered texture VRAM-compressed.
Measured in a scratch Godot project, GL Compatibility, the 1.0 m grill built
at 1.52.0 and at this version, three cameras: 5 draws before and 5 after in
each (the scene's floor included).

## [1.52.0] - the frozen drink station: its mascot drawn, its lettering owned

The next of the store's props (the walker, 2026-10-02): the thing in the
corner that is "the most SATURATED object in a 1990s convenience store".

THE BRIEF. A printed panel across the stand's front and a lit topper over
the machine, both the brand's; an instruction panel and a flavour strip,
both the machine maker's; two barrels of churning slush. A printed mascot
is drawn with curves, not stamped from a bitmap. What is left out: wear --
the panel is behind the station's glass and the topper is a lit box.

### Changed
- **The mascot is drawn** (`_mascot`): the same frozen cup with a face --
  domed lid, slanted straw, black rim, two red bands, eyes with their
  lights, a grin with a tongue, pink cheeks, two feet -- in curves at the
  panel's size, where 1.15.0 stamped a 16 x 20 bitmap at a whole scale.
- **The lettering has owners**: FROZEN JAWN in the brand's bold sans with a
  red outline and its tag line in the printed italic; the three numbered
  steps and the six flavours in the machine maker's face
  (`smooth_type.OWNERS`). 1.15.0's `monogram` headline and `m5x7` lines are
  gone with the bitmap.
- **Three times the density** on the panel, the topper and the steps
  (`TEXEL_*` 480 where they were 160, 240 and 300); the rail keeps 600; the
  churn tile is 96 px square for the same pattern at the same scale.
- The image is packed by `card_art.atlas` with gutters each tile bleeds
  into, and sampled with filtering.

### Cost
The glow image for the 1.6 m station is 742 x 621 px (0.46 M px) where it
was 293 x 254 (0.07 M px): 6.2 times. One material, now Linear; no draw
changes (the three submissions of 1.15.0). Level Factory 0.128.0 ships a
filtered texture VRAM-compressed. Measured in a scratch Godot project, GL
Compatibility, the 1.6 m station built at 1.51.0 and at this version, three
cameras: 4 draws before and 4 after in each (the scene's floor included).
Frames in the root repo's `docs/findings/real_look_trial/`.

## [1.51.0] - the cooler wall: its products drawn in metres, lit from the sides, stocked by the case

The next of the store's props after the candy rack (the walker, 2026-10-02:
the cooler doors and their stock). The cooler's glow image was the least
dense art in the store -- 160 px/m, a door's panel 115 x 270 px, every
product a few pixel rectangles.

THE BRIEF. A reach-in cooler door: a white panel lit from inside by the
tubes down each mullion, five wire shelves, product faced out and stocked by
the case -- a shelf is filled a case at a time and a case is one drink. Who
sees it: a customer through glass, from the aisle; the price strip on each
shelf's edge is for them. What is left out: wear and dirt, because the glass
is between.

### Changed
- **Every product is sized in metres** (`SODA`, `CAN`, `JUG`, `CARTON`,
  `TWELVE`, `TALLBOY`, `LONGNECK`, `SPORTS`, `JUICE`) and painted with
  shading: a round thing lit from the sides, its shadow on the panel, a
  cap, a neck, a label. A 12-pack carries its brewer's name in that
  brewer's own face (`BEER_FACES`).
- **Stocked by the case** (`FACING`): three of one drink side by side
  before the next. Every bottle used to draw its own brand.
- **The panel is brightest at its sides**, where the tubes are, and each
  shelf's underside shades the head of the bay below it.
- **The sign band** is the shop's face (`smooth_type.owned("shop")`) where
  it was the pixel small caps.
- **`TEXEL` 160 -> 400**, sampled with filtering; the tiles are packed by
  `card_art.atlas` with gutters they bleed into, and the tube and dark
  blocks are 24 px squares where they were 6.

### Cost
The glow image for a 0.72 m door is 628 x 3400 px (2.1 M px) where it was
690 x 496 (0.34 M px): 6.2 times. One image a cooler run whatever its
length, as before; one material, now Linear; no draw changes (the three
submissions of 1.12.0). Level Factory 0.128.0 ships a filtered texture
VRAM-compressed. Not 768 px/m as the counter's machines are: a door is
behind glass and the whole wall is one image.

Measured in a scratch Godot project, GL Compatibility, a 5.2 m run built at
1.50.0 and at this version, three cameras: 4 draws before and 4 after in
each (the scene's floor included). The renderer's texture memory with the
run loaded rose 13.2 MB, uncompressed; what the compressed texture costs in
a level is not measured yet.

### Not changed, and said
The glow's strength (`GLOW_EMISSION` 1.0, set in 1.12.0 "to be judged on
the walk") flattens the painted shading: an emissive face is lit from
within, and the shadow a bottle throws reads faint through it. The walker
has not judged the strength; it is left where it was.

## [1.50.0] - the counter's candy rack: stocked by the box, each box under its header card

The walker, 2026-10-02: "yes, start with the candy tiers" -- the next of the
store's props still in the pixel look beside the repainted till, dispensers
and rack (cold run 9136's frames).

THE BRIEF. Three stepped shelves on a store counter's front, under its
overhang: wrapped bars faced out, sold from the cardboard display boxes they
ship in. Who touches it: the customer takes a bar; the clerk drops a new box
in when one empties. What it is for, to the room: it is at a child's eye
height and a queue's hand height, and it is colour. What follows: a box
holds ONE bar, so a brand is a run and not a slot; a box's lid folds up
behind its bars as a card, which is the brand's name at a size a wrapper
cannot carry; a wrapper is foil, crimped flat at both ends. What is left
out: wear, because stock turns over.

### Changed
- **A tier is stocked by the box** (`service_counter_forms.tier_brands`):
  three brands a tier, two facings each. Every slot used to draw its own.
- **Each box stands its header card**: the brand's full name in the brand's
  own face (`candy_brands.FACE`, eleven confectioners no longer sharing a
  type foundry) on its own colours, in the tier's shade.
- **A wrapper is painted as foil**: graded, a ribbed fin at each end, the
  room's light along its top edge and in one streak.
- **The shop's talker**, 2 FOR $1, once a metre on the top tier, in the
  shop's face. `candy_brands.SHELF_TALKER` had been written in 1.7.0 and
  never painted.
- **Twice the density** (`CANDY_TEXEL` 800), sampled with filtering. The
  counter's painted image is 800 x 636 where it was 400 x 286.
- **Gutters between the image's bands** (`BAND_GUTTER`), each filled with
  the neighbouring band's edge row, and half a gutter above the first band
  and under the last because the sampler repeats.

### Cost
No draw changes, measured: a 6 m counter built at 1.49.0 and at this
version in a scratch Godot project, GL Compatibility, three cameras on its
front -- 5, 8 and 9 draws before and 5, 8 and 9 after (each count includes
the scene's floor). The same one material, now Linear. The counter's painted
image is 4.4 times the pixels it was; Level Factory 0.128.0 ships a filtered
texture VRAM-compressed, and what it costs in a level is not measured yet.

### Known
The art repeats every metre along the counter, as it always has: on a 6 m
counter the same three boxes come round six times a tier. Twice the density
makes the repeat easier to see. Not changed here.

## [1.49.0] - the owner pass: every typeface belongs to somebody; a screen's letters are pixels again

The walker's font catalog (`docs/reference/CC0_FONTS_FOR_HUMAN_AUTHORED_GAMES.md`
in the root repo), 2026-10-02: "Assign a typeface to an owner." Everything
the real look had painted since 1.46.0 was Blue Highway -- a bank's ATM, a
cigarette maker's ad, the law's small print and a shop's price card in one
voice. The walker approved three more CC0 families the same day; Pixelcoat
0.55.0 vendors them.

### Added
- **Seven minted faces**: `aileron`, `aileron_bold` (Aileron SemiBold and
  Bold), `vegur`, `vegur_bold`, `oldstyle`, `oldstyle_bold`,
  `oldstyle_italic` (MFB Oldstyle, a revival of Century Oldstyle, 1909).
- **`smooth_type.OWNERS` and `owned(owner)`**: a painter names WHO is
  speaking and gets that owner's face. `shop` (a price card, a sticker,
  vinyl) is Blue Highway; `maker` (an institution, a machine's maker) is
  Aileron; `notice` (the law's strip, a warning label) is Vegur; `print`
  (advertising and packaging copy) is MFB Oldstyle; `display` is Minisystem.
- **`paint.Img.pixel_text`**: the factory's pixel face at the largest whole
  scale that fits, for a screen.

### Changed
- **Each cigarette brand has its own lettering** (`cigarette_brands.FACE`),
  on its pack and on its ad: a slim in an italic serif, a 100 in a roman, a
  menthol and a light in a grotesque. Twelve makers no longer share a type
  foundry. The slogan under a name is a printed italic; the law's strip and
  the Surgeon General's warning are Vegur; the price card stays the shop's.
- **The ATM**: TAKE CASH, RECEIPT, CARD, the keys and the topper are the
  maker's (Aileron); the surcharge sticker is the shop's (Blue Highway).
- **The ATM's and the video poker's TUBES are set in pixels.** 1.46.0 set
  them in the printed face. A CRT draws its characters on a grid: the pixel
  look was wrong on what is printed or moulded and right on a screen, and
  1.46.0 replaced it in both places. The marquee, the pay table and the
  buttons are printed and stay smooth.
- **The ATM's tube shows fewer lines, larger**: three where it showed four,
  in the regular pixel face at twice its size (`CRT_FACE`, `CRT_LINE_PX`).
  A pixel face only grows in whole steps; at 1.46.0's line depth it set at
  1x and the tube's text was half the height it had been. Seen on a frame.
- An ad's lettering is set in the height ABOVE the warning sticker where
  the sticker reaches under it. The first cut of this release ran the bolder
  warning over a slogan's second line; seen on a preview, not predicted.

### Not changed, and said
- The poker cabinet's marquee and pay table, the lottery tickets and the
  registers' key legends still name Blue Highway by hand. Each has one owner
  and that owner's face is defensible; they are not yet routed through
  `OWNERS`.

### Cost
None in a frame: the same images at the same sizes, different glyphs. The
seven face tables add 1.6 MB of Python source to the repo.

## [1.48.0] - the cigarette rack and the cigarette machine, repainted; the rack stocked in blocks

The walker, 2026-10-02: "yes, do the cigarette rack next". The rack over a
store counter and the pull-knob machine share their painters
(`cigarette_forms._pack`, `_ad`, `_row`, `_strip`), so both change.

### Changed
- **The display art is smooth type and painted shading, sampled with
  filtering.** Same density as before (`TEXEL` 700), so the images are the
  size they were; what changes is the lettering (Blue Highway where it was
  the pixel face) and what a pack is: a printed box in cellophane, with the
  flip-top's seam a quarter of the way down, the wrap catching the room
  along its top edge and in one streak, and a shadow on the backing. A row's
  head is in the shade of the shelf above it. No wear: a pack is new and the
  display is behind glass.
- **The counter's rack is stocked in BLOCKS** (`service_counter_forms.
  rack_facings`): two to four facings of a brand side by side, walking the
  lineup. Every slot used to draw its own brand, and 45 packs a row read as
  confetti. A clerk stocks by the carton.
- **A pack on an ad keeps a pack's proportions.** The ad sized its pack as a
  share of the sheet's WIDTH whatever its height, so the rack's long shallow
  header carried a pack five times as wide as it was tall. On such a sheet
  the name is also set on one line where it was two small ones.
- The band under the art that a display's other faces sample is 16 rows deep
  and full width (`DARK_ROWS`), where it was a 4 px patch: a filtered,
  mip-mapped sample of a patch bleeds the art into them.
- `paint.Img.diamond` and `tri_down`, for a pack's diamond and a display
  card's notch.

### Cost
No draw changes. Measured in a scratch Godot project, GL Compatibility, the
machine and a 6 m counter built at 1.45.0 and at this version, the same
cameras (`docs/findings/real_look_trial/` in the root repo): the machine 9
and 8 draws in its two views before and after, the rack 9, 4 and 3 in its
three before and after. The same two materials on each, now Linear. The
rack's image is 1652 x 282 (was 1652 x 272) and the machine's 403 x 617 (was
403 x 607). Level Factory 0.128.0 ships a filtered texture VRAM-compressed,
so both are smaller on a client than they were.

## [1.47.0] - the lottery dispensers, built to a brief; the store counter back to seven draws

Cold run 9135's frames put the real-look till beside three flat red boxes:
two looks in one room. The walker, 2026-10-02: roll the new look out to the
props around the machines, the lottery dispensers first. The same day they
handed over an art-direction guide (`docs/reference/HUMAN_AUTHORSHIP_GUIDE.md`
in the root repo) that asks for a brief before a surface is painted, a cause
for every detail, and quiet where nothing needs saying. This is the first
prop built to it.

### Changed
- **`core/counter_lottery.py`: an instant-ticket dispenser.** A clear acrylic
  case on a black foot, its face leaning back about five degrees toward a
  standing customer, a roll of tickets seen from the clerk's side. Three in
  a row beside each till, a DIFFERENT GAME IN EACH -- WOODER WINS $1, HOAGIE
  MONEY $2, FAT STACKS $5, invented -- in identical cases at identical
  heights (1.7.0 stepped each box a centimetre shorter than the last; nothing
  made them differ). The ticket is the loud part and the case is quiet: no
  grain, no grime, because acrylic by a till is wiped and a ticket is new.
  No transparency: the acrylic is painted as what is seen through it.
- **They are painted into the till's image** (`counter_register.paint_art`)
  and built into the till's object, so they ride in a draw the counter
  already makes.
- **The service counter has no `plastic` kind any more.** The tills' bodies
  (1.46.0) and these were its only users. `M_Counter_svc_plastic` is gone
  and the counter is SEVEN materials and seven draws again -- what it was at
  1.45.0, before either was painted.

### Measured
One 6 m service counter, built at 1.45.0 and at this version, a scratch
Godot project in GL Compatibility, the same three cameras
(`docs/findings/real_look_trial/` in the root repo):

| view | draws at 1.45.0 | draws at 1.47.0 |
|---|---|---|
| the dispensers from the customer's side | 7 | 7 |
| from the clerk's side | 7 | 7 |
| the counter from across the room | 9 | 9 |

(Each count includes the scratch scene's floor.) 1.46.0 alone read one more
in its own views of the till (6 to 7, 8 to 9); that draw is what this
release takes back. A dispenser is
32 triangles where it was 12.

### Not measured
- In a level. Run 9135's package predates this.
- The till's image is now 262 x 1111 px; `card_art.atlas` packs shelves to
  the widest tile and this one is tall for it. Level Factory 0.128.0 ships it
  VRAM-compressed, so nobody has priced the shape.

## [1.46.0] - the real look, trialled: the video poker, the ATM and both registers

The walker, 2026-10-02, on the screens-that-run frames: "this looks like it
is made with a 90s GPU, what can we do to make these things look
better/more real without destroying performance?" -- then "replace the retro
look, do the first three as a trial", and after the video-poker cabinet:
"yes, do the ATM and register the same way". The first three, none of which
needs a light, a post-process or a script:

1. **Art at three times the density, in a smooth face, sampled with
   filtering.** `core/smooth_type.py` sets anti-aliased type from CC0
   outline faces minted once into coverage tables (`tools/mint_smooth_type.py`
   from the fonts Pixelcoat 0.54.0 vendors: Blue Highway regular, bold and
   condensed, and Minisystem, a dot-segment display face).
2. **Shading painted in.** `core/paint.py`: a float image and the moves that
   make a flat tile read as a made thing -- graded panels, darkening where
   faces meet, a lit rim on a raised part, a streak of the room across
   glass, a display's bloom.
3. **The shape of a made thing.** `core/machine_parts.py`: chamfered
   corners, a toe kick set in, a sign proud of its head, a tube that bulges
   behind a surround sloping in to it, keys and buttons standing off a deck.

### Changed
- **`video_poker` and `atm`** are rebuilt from those parts. Same slots, same
  brands, same shutters, same three draws each.
- **`cash_register`** (the card shop's till): every face is painted into the
  register's one image. The four flat materials (case, trim, lock, paper)
  are gone, so the module is TWO draws where it was six. The pole's glass
  sits behind its head's face; the keys are bevelled and carry digits; the
  lock is painted on the drawer with the pull bar's shadow.
- **The register on the store and bar counters** (`counter_register.py`,
  the one a gas station stands): a chamfered putty body, a painted deck, a
  block of lettered keys at the clerk's end, a dark pole head. One painted
  image shared by every counter in a level.
- **The displays** are Minisystem with their strokes fattened
  (`register_forms.stroke`) and a bloom round them. The first cut set the
  face's own hairline and was THINNER AND DIMMER than the pixel digits it
  replaced -- seen on a frame, not predicted.
- `card_art.atlas(..., gutter=, bleed=)`, `materials.make_*_material(...,
  smooth=)`, `_card_atlas.build_art(..., smooth=)`, `shutters.over(...,
  proud=)`: each a default that leaves every other species as it was.
- `video_poker`'s triangle budget 120 -> 240. It is a regression detector,
  and the cabinet is 212.

### Measured
One of each, built before and after, imported into a scratch Godot project
in GL Compatibility under one lamp (`docs/findings/real_look_trial/` in the
root repo). Draws are the prop's own; texture memory is the renderer's own
figure with the prop loaded, uncompressed with mips.

| prop | draws | triangles | texture memory |
|---|---|---|---|
| video poker | 3 -> 3 | 68 -> 212 | 0.56 -> 4.18 MiB |
| ATM | 3 -> 3 | 62 -> 156 | +2.80 MiB |
| cash register | 6 -> 2 | 134 -> 182 | +2.42 MiB |
| service counter, two tills | 7 -> 8 | 108 -> 96 a till | +0.98 MiB |

**The store counter is one draw MORE.** Its tills' bodies rode in the
counter's shared plastic as flat boxes; painted, they are one more image.
What would take that back is one material whose emission is a mask over the
same image, so a till's body and its displays share a draw; it needs the
lit-face contract downstream to stop assuming a `_Face` material glows all
over. The bar counter is one FEWER by material count (two flat materials
became one image); that one was counted, not measured in Godot.

### Not measured
- Frame time. Draws are the budget this repo has measured to matter and
  three of four did not rise, but nobody has walked a level with these in it.
- Texture memory after Godot's import compression. The figures above are
  uncompressed; they are the cost if nothing is done about it.
- The trial is four props. Every other species still has the pixel look,
  and the two looks have not been seen side by side in one room.

### Known
- `counter`'s register displays have never had the 1.45.0-era flicker:
  Level Factory 0.127.0 matches `M_Register_*_Face`, and a counter's is
  `M_Counter_VFD_*_Face`. Left alone: the flicker is under 2 % on a frame
  and would cost each counter one more draw.

## [1.45.0] - screens that run: shutters over the ATM's and the video poker's CRTs

The walker, 2026-10-02, after walking cold run 9131: "there is a relatively
frozen/static feeling, where the lights in the atm, gambling machine, and
cash register are just fixed with nothing dynamic/alive about them". Of four
steps toward levels that feel alive, this is the first.

A SHUTTER (`core/shutters.py`) is a quad standing 3 mm proud of a lit
screen, over ONE PART of its picture, with a schedule: the fraction of a
period in which it is open. Closed, it hides that part behind the screen's
own background colour; open, it is not there. A screen's picture stays one
painted image and the shutters decide when each part of it shows.

  * THE VIDEO POKER DEALS: a shutter a card, opening one after another
    (8 %, 13 %, 18 %, 23 %, 28 % of an 8 s period), all closing at 92 %.
  * THE ATM TAKES TURNS: its greeting and INSERT CARD, half of 3 s each. A
    tube too small for two lines has no shutter.

WHAT SHIPS: one more object a machine (`ATM_Shutter`, `VideoPoker_Shutter`)
on a material whose name begins `M_Shutter_Screen`, exported fully
transparent with the closed colour as its base colour -- so a consumer that
knows nothing about shutters draws the screen exactly as it was. The
schedule is in two UV sets: UV (open from, open to), UV2 (period, phase).
THE CLOCK IS THE CONSUMER'S: Level Factory 0.127.0's import swaps the
material for a shader that reads them.

ONE DERIVATION, TWO READERS: `video_poker_forms.card_boxes` and
`atm_forms.crt_bands` are what the painter draws from and what the shutters
are placed from, so a shutter cannot drift off its card.

COST: one more draw a machine, 10 or 4 triangles, no texture. Three
materials a machine where there were two.

MEASURED in a scratch Godot project with 0.127.0's import, ten frames a
second apart (root repo, docs/findings/screens_that_run/): the poker's
screen empty, then Q, then Q Q J, then the hand, held, then empty; the ATM's
first line and second line alternating, never both, never neither.

WHAT THE FIRST CUTS GOT WRONG: a closed shutter was black, which is a hole
in the poker's blue tube (it is the tube's colour); the shutter mesh had no
`Wear` attribute and the build warned; alpha 0 on a blended material leaves
Blender's exporter as alphaMode MASK, not BLEND, which is as good.

KNOWN: the closed colour is unlit, so on a machine with its power cut a
closed shutter is its dark background where the dead screen round it is the
room's light on its picture.

Tests: `tests/test_shutters.py` (6 + 2 in Blender); `test_atm.py` and
`test_video_poker.py` learn the third object and material. Census: both
species "3 builds, 0 with coincident pairs".

## [1.44.0] - the video rack, revised from the walker's photographs

1.43.0 built the tape racks "from the era" with no references: every box
faced out, grey steel, printed genre boards, low islands. Cold run 9132 put
it in a level and the walker sent ten photographs (docs/SET_DRESSING_
REFERENCES.md, "The walker's video store references"): a cult store and a
chain store. This is both.

  * SPINES OUT. A shelf is a few blocks of tape spines, each a whole number
    of 25 mm tapes, uneven on top, a hand's gap here and there, showing its
    own stretch of its section's strip of forty painted spines. A 2.4 m wall
    is 493 tapes in 1,560 triangles; faced out it was 126 boxes in 2,028.
  * PAINTED UNITS. Purple, green, black or blue by the slot's variant, frame
    and shelves and all, in the `Wear` vertex colour -- no new material.
  * A FOURTH FORM, `display`: the chain store's new-release rack. Black,
    every box faced out and leaning back 12 degrees on its foot, three or
    four facings a title, NEW RELEASES across its head. NEW RELEASES is this
    form's alone; an aisle runs the other five sections.
  * SECTION BOARDS lettered as large as they set (scale 2 where the word
    fits), and on an ISLAND a yellow section sign on each end panel at the
    eye -- its face is the slot's end.
  * SHELF TAGS: a yellow or orange tag or two on every lip.

Still two submissions: one image, 240 x 946 (it was 240 x 508).

WHAT THE FIRST CUT GOT WRONG, each found by the planner's coincident-face
check before a frame was rendered: a tag's top was its lip's top; two tags
drawn anywhere on a lip overlapped face on face; an island's shelves stood 1
mm off its inset end panels.

NOT DRAWN: a tape leaning in a gap or lying flat on a row; round price
stickers on the display boxes; cut-out letters standing ON a unit (the board
is a board); the ceiling sign with arrows.

Census: "3 builds, 0 with coincident pairs, 0 that did not build".

Tests: `tests/test_video_rack.py` 48 -> 64 (+5 in Blender).

## [1.43.0] - the video store's tape racks, and its name over the door

The walker's queue, 2026-09-29: "a new building type: a VHS movie rental
store". Their calls, 2026-10-02: the store is MACDADE MOVIES; the curtained
back room, "suggestive only"; no references -- build from the era.

New species `video_rack` (`core/video_rack_forms.py`, `recipes/video_rack.py`,
its genome), three forms:

  wall    shopped from one side, its back board to the building's wall:
          shelves of VHS BOXES faced out, a GENRE BOARD across the head of
          each bay -- NEW RELEASES, ACTION, COMEDY, HORROR, DRAMA, SCI-FI, a
          bay each, from a start the slot's `variant` picks;
  island  both faces of a spine, low enough to see over, no boards;
  adult   the wall form for the back room: every board says ADULTS ONLY 18+
          and every box is the back room's.

A box is a 12-triangle sleeve, 0.105 x 0.19 x 0.03 m, three or four facings a
title. THIRTY-SIX INVENTED TITLES -- HOAGIE COP (and 2), FIST OF JAWN, IT ATE
NANA, LASER NANA, UNCLE VINNY, THE EL -- none a real film, studio or chain.
THE BACK ROOM IS SUGGESTIVE AND NEVER EXPLICIT: a plain box, a title (HOT TUB
4, TAN LINES), a pair of lips, an 18+ badge. No figure is drawn.

TWO SUBMISSIONS WHATEVER THE LENGTH, the snack gondola's two: the steel, and
every box and board on one 240 x 508 image. A 3 m wall is 126 boxes and
2,028 triangles; the genome's largest is 6,192.

`storefront_names`: a building whose identity says `video` is MACDADE MOVIES.

WHAT THE FIRST CUTS GOT WRONG: MUMMER is 41 px in m5x7 on a 40 px box (the
title is MOON STRUT); a shelf's lip stood 2 mm under its shelf and the kick
ended on the back board's face (the planner's check, both moved); the kick,
board and lip shared the frame's part name under their own tints and built
as `VideoRack_Frame.001` (each is its own part).

Registries: `test_coincident_faces` CENSUS_BUILDS 348 -> 351 ("3 builds, 0
with coincident pairs": 384 / 2,028 / 6,192 tris); `test_genome`;
`test_material_options_closed`; `test_theme_style_resolution` 90 -> 91.

Tests: `tests/test_video_rack.py` (48 + 4 in Blender).

## [1.42.0] - a bag is pinched flat at its seals and puffed between them

The walker, 2026-10-02, sent two tutorials on making a chip bag in Blender: a
flat sheet whose top and bottom rows are PINNED, inflated by a cloth
simulation's pressure, the pinned rows staying flat as the crimped seals.
A gondola's bag was `prims.pillow` stood on its back -- a box with a crowned
front, as deep at its edges as at its middle -- and read as a padded box.

`snack_gondola_forms.bag` now lofts four rings up the bag: the bottom seal's
edge (8 mm thick, full width), the belly's foot and head at 30% and 70% of
the height (the full thickness, 94% of the width -- a filled bag draws in),
the top seal's edge. Fourteen planar quads; the three toward -Y carry the
print, mapped by x and z as it was. The candy bags are the same shape.

THE SIMULATION IS NOT RUN, and that is the performance rule. A sheet dense
enough to wrinkle is thousands of triangles a bag and a 6 m gondola stands
two hundred. The cheap shape is 28 triangles where the pillow was 22. What
the simulation would have bought and this does not: wrinkles and creases, a
belly that curves rather than facets, a zigzag cut along the seal (the crimp
is painted), and no two bags alike.

MEASURED. 6.0 x 1.0 x 1.6, variant 1: 5,076 -> 5,868 triangles. The genome's
largest (14 x 1.5 x 2.2): 18,528 -> 20,676 to 21,660 by variant (the census
build is the higher), so its budget -- a regression
detector, not a frame cost -- goes 20,000 -> 22,000. Still two submissions.
Census: 3 builds, 0 with coincident pairs (852 / 5,868 / 21,660 tris).

Tests: `test_snack_gondola.py` +1 -- a bag is `SEAL_T` thick at its foot and
head and the full thickness across the belly, the seals on the belly's
mid-plane, every face planar and wound outward, 28 triangles.

## [1.41.0] - most posters are on plain paper, and one or two a cluster are loud

The walker, 2026-09-30, on cold run 9119's pole flyers and the posters so
far: "if anything its just too much color". Their palette guide says the
same: "a few bright flyers ... stand out more if neighboring posters use
cream or newsprint". Every bar bill, handbill and sale poster drew its paper
from a table three-quarters or more coloured, so a wrapped pole was a column
of equally loud sheets.

  * `poster_art`: a painter takes ``stock`` -- "loud" (the coloured papers
    it always had), "plain" (white, cream, newsprint; a sale poster's deal
    in red on white or navy on cream) or None (either, as before). The CLUB
    takes none: the walker liked its colour and its blacklight.
  * `poster_wall_forms.loud_sheets`: one sheet of a run is loud; two from
    six sheets; three from sixteen; spread along the run from a start its
    own name picks. Every tile names its stock.
  * `pole_flyers_forms`: ONE bill a pole is loud, the one its newest front
    sheet carries.
  * `card_art` hands a tile's stock to the painter.

No geometry, no material and no draw moves: the same sheets on the same one
image a run.

Tests: `test_poster_wall.py` +18 -- every stock of every family sets both
lines and passes the thumbnail, grayscale and blur tests; plain paper's
channels are within 35 of each other and loud paper's are not; a run of any
width is one to three loud sheets by its count; a club run names no stock
and paints what it painted. `test_pole_flyers.py` +3 -- one bill a pole is
loud and the newest layer shows it.

## [1.40.0] - the snack gondola sells more than chips

The walker's 90s snack references, 2026-09-29: "fruit snacks, lunch kits,
snack cakes on shelves, candy". And the walker's own first named brand
(docs/proposals/GAS_STATION_SHOP.md): "yummyjawns -- tastycake rip off", a
shelf of "flat rectangular cartons standing on edge, four to six of each
flavour side by side ... from two metres it reads as stripes of colour".

WHAT CHANGED (`core/snack_gondola_forms.py`). The -Y face stays the chip
aisle. The +Y face is SECTIONS, a bay each, cycling from a start the
gondola's own name picks: YUMMYJAWNS snack cakes (0.20 x 0.16 m cartons,
ONE flavour a shelf, the next shelf another -- the stripes), fruit snacks
and lunch kits (upright boxes, three facings a product) and bagged candy
(the counter rack's own `candy_brands`, in a bag). A carton is a
12-triangle box with its front on its tile. The end caps stay chips.

TEN NEW PRODUCTS (`core/snack_brands.BOXED`), invented: YUMMYJAWNS BUTTER
JAWNS, CHOCOLATE LOGS, CHERRY PIES, PEANUT BUTTER PUCKS and LEMON SQUARES;
GUMMY GEESE, FRUIT TAPE, JUICE BOMBS; HOAGIE KIT, PIZZA KIT. The snack-cake
makers (Philadelphia's own first), the lunch kit's and the fruit snacks'
join the denylists.

STILL TWO SUBMISSIONS. Every product is on the one image the bags were on,
grown from 240 x 128 to 240 x 310: 66 rects, 33 products.

MEASURED, before and after, at Deli Counter's three sizes x 4 variants: the
chip face and both end caps are the SAME prims, vertex for vertex, and the
chip tiles the same pixels. Triangles at 6.0 x 1.0 x 1.6: 5,164 -> 4,980 to
5,404 by variant (a carton is 12 where a bag is 22, and the small items
stand more to a shelf); at 10 x 0.9 x 1.8: 11,236 -> 10,656. Census: "3
builds, 0 with coincident pairs, 0 that did not build" (762 / 5,076 /
18,528 tris).

WHAT THE FIRST DRAFT GOT WRONG: BOMBS is 31 px in m5x7 and the small tile
was 32. `_set` raises on a word wider than its tile, so it failed before a
frame was shot; the tile is 36 x 48.

KNOWN. A lunch kit belongs in a cooler and stands on a shelf here: the
cooler's doors are a different species and the walker asked to see them. A
short shelf of 0.18 m boxes leaves air under the shelf above.

Tests: `tests/test_snack_gondola.py` 27 -> 31 (+5 in Blender, unchanged): a
stock item names its own front faces; no two tiles overlap; one face chips,
the other sections, the end caps chips; a shelf of cakes is one flavour and
its neighbour another; every boxed product invented and six letters or
fewer.

## [1.39.0] - the 1997 tavern video-poker cabinet

The walker, 2026-09-30: "actually put in 'PA Skill Games' ... into the level.
We would see them in convenient stores, bars, and strip clubs. High stool to
play" -- and, agreeing to the period push-back, the 1997 version: a boxy
upright with a CRT and the "for amusement only" sticker, not the 2010s curved
LCD. New species `video_poker`: `core/video_poker_forms.py`,
`recipes/video_poker.py`, its genome.

WHAT IS BUILT, the ATM's shape: a dark plinth; the black cabinet, its front a
painted belly glass (the jacks-or-better pay table, a coin door, a bill
slot); a button deck sloped to the player (five lit HOLD caps, BET, DEAL);
the head set back, a bezel round a recessed CRT showing JACKS OR BETTER, a
dealt hand and the credits; a lit marquee -- the brand, FOR AMUSEMENT ONLY.
Four invented Delco brands by variant: JAWN JACKPOT, PIKE DRAW, LUCKY HOAGIE,
DOWN THE SHORE DRAW. Never "Pennsylvania Skill".

TWO ATLASES, TWO MATERIALS, TWO DRAWS: cabinet, trim, belly and deck painted;
the CRT and the marquee backlit (`_Face`, emission 1.0, albedo 0.6 -- the
ATM's), so a power cut takes them. `card_art.paint` dispatches `vp_*`. 58
triangles; census 3 builds, 0 coincident pairs.

WHAT THE FIRST DRAFT GOT WRONG, each caught before shipping: HOLD on the
buttons and "10S" on a card did not set on the narrowest unit (the buttons
are plain lit caps, the ranks set in their suit's colour); JAWN POKER and PIKE
POKER tripped the card-brand denylist's POKE (a real card mark, held as a
substring), so no brand says POKER; and the genome had no `delco` style row,
which the theme test caught -- delco_1997 could not have resolved it.

Known: a hand's "10" sets at scale 1 where the single ranks set at 3 -- two
digits do not fit an 18 px card larger. Legible; noted.

Registries: `test_coincident_faces` CENSUS_BUILDS 345 -> 348;
`test_genome`; `test_material_options_closed` (painted);
`test_theme_style_resolution` 89 -> 90.

Tests: `tests/test_video_poker.py` (6 + 2 in Blender): the genome and the
stem; the slot at 27 sizes x 4 variants with no shared plane; every face's
direction; the glow on the CRT and marquee only; every line sets; every name
invented, none a real maker or the Pennsylvania mark; built, two objects, two
materials, one `_Face`.

## [1.38.1] - the remainders get the room face too

Cold run 9123 photographed the room face on every full segment and opening of
the gas station's stone walls, and stone still showing inside at its
remainders: a strip at the stockroom's frame, beside the sales floor's window,
at the walk-in cooler's corner. A remainder is the unit `wallEnd` Deli Counter
scales per slot, and 1.38.0 left it out on the guess that a scaled unit box
might not keep its room side. It does: Deli Counter's placement basis is
Ry(-t) x Scale_LOCAL, so a positive per-slot scale is applied in the module's
own frame before the turn and the unit box's -Y face (y = -0.5) is the room
side as a segment's is.

`kit.INNER_FACE_ROLES` and `_arch.build_slab`'s room-face roles gain
`wallEnd`; its stem gains `_i<kind>` (`wallEnd_delco_1997_01_mstone_idrywall`).
Deli Counter 0.166.1 stamps its remainders.

Tests: `tests/test_inner_face.py` -- a remainder is its own build; built, its
-Y face is the interior finish and its +Y face and ends are the wall's.

## [1.38.0] - a wall module with a room face

Cold run 9120's FLAPPHAS walk, finding 3: the gas station's exterior stone
on the inside of its exterior walls, behind the register, in the stockroom
and the office. A wall module wore its slot's one material on both faces,
and on purpose -- its relief is carved on both faces so it "needs no idea
which face is the street". Deli Counter 0.166.0 now says which: an exterior
wall in an outside-only finish (brick, stone, wood, siding: about 2,000
modules in 15 buildings) carries `material_in`, its building's interior
finish.

WHICH FACE IS THE ROOM was measured, not reasoned (the first round of
reasoning gave N/S and E/W opposite answers): a module's local +Y, pushed
through Deli Counter's `tscn_export.godot_basis` at the slot's rotation,
lands outdoors on all four facings; and `themed_tscn._fit_rotation` tries
the slot's own rotation first and keeps it on a tie, so a south wall stays
at 180 and is not turned inside out.

  * `kit.plan_kit`: a wall, window, doorway or breach slot's `material_in`
    (a known kind; anything else is dropped) is in the module key and the
    stem, `_i<kind>` after `_m<kind>` -- the one- and two-material walls are
    two builds. `INNER_FACE_ROLES`; Deli Counter's mirror has the same.
  * `dna.resolve_module_plan` carries it onto the plan.
  * `_arch.build_slab`: every structure face pointing -Y on the -Y half --
    the room face and its recessed relief fields -- takes the interior
    finish. Jambs, sill and head keep the wall's own. Not on storefronts.

THE COST is one more material, so one more draw, on each module it applies
to -- priced on cold run 9123's package against 9122's (see its notes).

Tests: `tests/test_inner_face.py` -- the room face is its own stem; an
unknown kind or a volume carries none; built, the -Y face is the interior
finish and the +Y face and an opening's jambs are the wall's (both Blender
cases fail without the `_arch` change).

## [1.37.1] - the named sign stops mirroring its own lamp

Cold run 9122 photographed the new door signs named, and two of the three
with a white blob mid-word (FLAPPHAS, TERMINAL A). Lux stands a sign's light
0.29 m in front of its face, and 1.37.0's face took the pylon's diffuse copy
(0.6) on the backlit material's 0.35 roughness -- right for a pylon with no
lamp before it, wrong for a sign with one.

MEASURED on 9122's walk copy, the gas station's fixtures rebuilt and swapped
in, one given station square to the sign, a fixed rectangle round it (8,000-
9,300 field pixels): the share of the sign's pixels clipped to white --

    9122 as shipped          26.5%   field (80, 153, 117)
    the same, re-shot        26.4%   (the control: the instrument's floor)
    roughness 1.0 only       26.2%   (the blob broader, as bright)
    roughness 1.0, copy 0.15 20.0%   field (78, 141, 110), the blob gone

So the specular theory was WRONG -- matte alone moved 0.3 points -- and the
diffuse copy was the blob. The rest of the 20.0% is the letters, which clip
at this emission whatever the lamp does. The first pass of that instrument
was blind: it deleted the GLB's import cache, did not re-import, and shot
four frames with no sign in them that agreed to the decimal.

`sign_box` builds the named face at `SIGN_ROUGHNESS` 1.0 and `SIGN_ALBEDO`
0.15; its glow is unchanged. `make_backlit_material` takes an optional
`roughness` (default 0.35, so every other backlit face -- ATM, pump, pylon,
posters -- is unchanged) and `build_art` passes one through when given.

Tests: the Blender sign test reads the face's `baseColorFactor` <= 0.15 and
`roughnessFactor` 1.0 from the GLB; it fails at the old 0.6.

## [1.37.0] - the sign over a door says who is inside

Cold run 9120's FLAPPHAS walk found the box over the gas station's door lit
and BLANK, and 9121 attributed it: not Lux (its spawner turns its own preview
quad off at fixture markers) but `sign_box`, which painted its face only from
a Pixelcoat sign pack -- and no theme ships one. So every sign Deli Counter
derives over a storefront door was a plain glowing panel: 102 across the
library, all three on club_block_014. The walker: "do the blank sign over the
door next". New: `core/storefront_names.py`.

WHO SAYS WHAT. Deli Counter 0.165.0 stamps every sign anchor with the
building's identity (`business`: `level_design.club_building_id`, its name and
recipe). `fixtures.plan` carries it on the placement and `build_fixtures`
into the recipe's plan. `storefront_names.sign_for` reads the KIND from the
identity's words and the NAME from that kind's list by the identity's crc32
-- Deli Counter's key and modulus for a club's `neon_sign`, so a club's door
says what its neon says. A gas station says FLAPPHAS in the pylon's variant-0
colours; banks, delis, pizza, pawn, pharmacy, clinic, market, card shop,
brewery, casino, funeral home and country club each have invented Delco
names; police, court, museum, rail, airport, arena and stadium say what they
are in plain words; anything else (apartments, mansions, offices, depots: 22
of the 102) shows a street number. Never blank: a sign with no `business` is
named from its anchor id, which no kind matches.

THE FACE. With no sign pack, the face is painted art -- one quad, its four
edges in the field colour -- in one backlit atlas (emission 1.4, albedo 0.6:
the pylon's), its material still `_Face` so a power cut takes it. A name sets
as large as it fits on one line or two, the lines stacked on the face's own
line height: the first render stacked them as `fit_text` does, on the trimmed
glyphs plus 1-2 px, and on a 0.6 m sign the two lines read as one.

THE CENSUS: `sign_box` 6 -> 0 coincident pairs. The face no longer has a back
lying on the cabinet's front, and the standoff arms run 2 cm into the cabinet
instead of ending on its back. The residue row retired; total 3003 -> 2997.

WHAT THE DENYLISTS CAUGHT: YOUSE CREDIT UNION (UNION is the city's soccer
club) is YOUSE CREDIT CO-OP. STADIUM is on the card-brand word list (a card
line); the civic kinds' plain words are asked every list but that one.

Tests: `tests/test_storefront_names.py` (13 + 1 in Blender): the kind of 32
library identities, a station is not a gas station, a club's door is its
neon's name (and `neon_sign`'s 24 variants are the table), FLAPPHAS in the
pylon's colours, a street number never a blank, every name sets on every
sign width the library derives (1.9-5.0 m), every name invented, the business
rides the anchor to the placement; in Blender, the face is named art in one
`_Face` material and the flat `SignBox_Face` is gone.

## [1.36.0] - the pump, drawn: a 1997 two-sided mechanical dispenser, two draws

The walker, 2026-09-30, after cold run 9120's FLAPPHAS walk found the
forecourt's pumps were the placeholder box `tools/new_species.py` minted on
2026-09-12: "pumps first". The reference is the walker's close-up in
docs/proposals/GAS_STATION_SHOP.md: three grades in colour-coded bodies
(silver, red, gold), mechanical price wheels to the nine-tenths above a
smaller sale wheel, a holstered nozzle and a coiled black hose, a stencilled
UNLEADED GASOLINE plate, grade buttons. New: `core/pump_forms.py`;
`recipes/pump.py` rewritten.

WHAT IS BUILT: a galvanised base frame, the slot's full footprint; a body
with three grade panels a face, each with a window recessed 15 mm on lit
price wheels ($/gal on black drums, the 9/10 stacked as printed, the sale
under it), the grade's name, the plate, a PUSH button and a louvred door; a
holster boot, the nozzle in it (spout, body, trigger guard) and a square-
section hose hung in a U from the nozzle's butt up the panel's edge to a
fitting under the window; a header with FLAPPHAS, lit. TWO-SIDED: the faces
are the slot's two LONG sides, whichever axis -- DC's gas stations author
1.0 x 1.2 (lanes either side in X), Lot's rotated sites hand Zoo 1.2 x 1.0 --
and the far face is the near one turned 180 degrees, so both read REGULAR,
PLUS, SUPER left to right, nothing mirrored.

THE PRICES AND BRAND ARE THE PYLON'S: grades, colours, store name, price sets
and colourways come from `price_pylon_forms` by the same variant, so the
pump agrees with the sign at the kerb (both variant 0 on club_block_014).

TWO ATLASES, TWO MATERIALS, TWO DRAWS: panels, base, nozzles, hoses painted;
price wheels and header backlit (`_Face`, emission 1.0, albedo 0.6 -- the
ATM's), so a power cut takes them. `card_art.paint` dispatches `pump_*`.

THE GENOME: width 0.5-2.0, depth 0.6-2.4, height 0.7-2.8 was the generic
prop range the placeholder was minted from, not a pump's; at its small corner
a grade panel is 17 cm wide and its words cannot set. Narrowed to 0.8-1.6 x
0.8-1.6 x 1.2-2.2. Every slot the library and Lot request (42 in six gas
station specs) is 1.0 x 1.2 x 1.4 or its rotation. Material `metal_painted`
(the pylon's and the ATM's); raw `metal` is no longer offered.

WHAT THE FIRST CUT GOT WRONG, each caught before shipping: the hose met the
body's end at a narrow slot and the trigger guard thinned to 1.75 mm (the
shared-plane sweep); the 9/10 and the plate did not set on most of the range
(every tile now records what it could not set); REGULAR was set at half
PLUS's size (one scale for every grade, the pylon's fix); the base read as a
black slab; and the hose -- first a cubic sampled evenly in its parameter --
folded through itself where the loop's bottom drew a 3.5 cm segment turning
69 degrees, and resampled evenly along its length the same curve had a
121-degree cusp. It is now a U: a drop, a semicircle and a climb, resampled
by arc length, its section framed on X with the tangent removed (`t x X`,
also first-cut, flipped sign at the loop's bottom).

Measured: 1152 triangles (budget 1200, was 200 for the box); the slot filled
centred at 48 sizes x 4 variants, no shared plane; census 3 builds, 0
coincident pairs, 1152 tris at each corner.

Tests: `tests/test_pump.py` (14 + 2 in Blender): discovery and the stems at
both authored orientations; the slot at every size; the faces are the long
sides and read left to right; every face points out of its part, the hose's
sides and caps included; the hose never folds (every joint's segments longer
than the inner side's cut-back) and clears the holster, the window and the
base; two atlases with the glow on the wheels and header only; every line
sets; the prices and brand are the pylon's; every name invented, none a real
fuel brand; in Blender, two objects, two materials, one `_Face`.
`test_material_options_closed` lists the pump as painted;
`test_coincident_faces` records its census.

## [1.35.0] - the ATM, redrawn: a 1990s surcharge unit, two draws

The walker, 2026-09-29: "Convenient stores should also have ATMs", with
photographs of late-'90s units; the queue kept a lit ATM topper, a
green-on-black CRT and a keypad. The species was a grey box with a dark glass
panel and a pale slab on top, in four materials, with six coincident face
pairs in the census residue. New: `core/atm_forms.py`; `recipes/atm.py`
rewritten.

WHAT IS BUILT: a dark plinth; the lower cabinet, its front a painted fascia
(cash slot, receipt slot, a yellow "NO FEE ATM THIS AINT" sticker); a keypad
ledge sloped toward the customer (a 4 x 3 key block, red / yellow / green
function keys, the card slot); the head set back, a bezel round a recessed
CRT; a lit topper -- ATM, and the network. Four networks by `variant`, every
name invented Delco slang: CASH JAWN, YO MONEY, QUIK KWIK CASH, MONEY BUCKET,
each with its own topper colours and screen greeting.

TWO ATLASES, TWO MATERIALS, TWO DRAWS. The cabinet, trim, fascia and keypad
are one painted atlas; the CRT and the topper are one backlit atlas
(`make_backlit_material`, emission 1.0, albedo 0.6 -- the cooler's), named
`_Face` so Lux's power cut takes them. `card_art.paint` dispatches the
`atm_*` tile kinds to `atm_forms.paint`.

WHAT THE FIRST CUT GOT WRONG, each caught before shipping: the screen
recess's four walls were wound inside out (a normal check); three of four
screens lost their greeting, because "WELCOME TO CASH JAWN" does not fit the
tube and `fit_text` drops what it cannot set -- the tiles now record any line
they could not set, the screen shows as many lines as its height holds
(greeting first), and the long greetings were shortened; RECEIPT did not fit
a 0.5 m unit's fascia. A Blender preview first showed four plain boxes: the
`-colonly` collision node, imported as a visible solid in front of the model,
which Godot hides.

Measured: 58 triangles; the slot filled centred at 27 sizes over the
genome's range, sign on and off, no shared plane; census 3 builds, 0
coincident pairs (was 6 -- the residue row retired, its total 3009 -> 3003).

Tests: `tests/test_atm.py` (7 + 2 in Blender): the genome and the stem; the
slot at every size; every face's direction; two atlases with the glow on
the screen and topper only; every line of every tile sets at every size; the
names invented and none a real ATM network's word; a built ATM is two
objects, two materials, one `_Face`.

## [1.34.0] - flyers on a pole: a sleeve of handbills, one draw

Cold run 9118 stood a flat 0.30 m alley bill on each 0.12 m pole, and it read
as a small sign. The walker sent six photographs of flyers on real poles --
a festival bill pasted twice, a single gig bill, columns up one side, poles
wrapped knee to head in layered torn paper with shreds at the foot -- and
their faded-'80s palette guide, "only if it helps, temper this". New species
`pole_flyers` (`core/pole_flyers_forms.py`, `recipes/pole_flyers.py`).

THE SHAPE. Sheets of `poster_art`'s alley handbills CURVED ROUND THE POLE:
each a strip of flat facets on a circle, a vertex every 15 degrees and at the
arc's ends, in four layers a paper's thickness (4 mm) apart. Width and depth
are the sleeve's outer diameter; the pole is not built. Three forms from the
photographs: `pair` (two sheets up the front, half the time the same bill
twice), `stack` (a column of three over an older sheet and a scrap), `wrap`
(courses all the way round, shreds at the foot). One atlas, one mesh, one
painted material: one draw a pole, however many sheets.

HISTORY, TEMPERED. The newest layer is printed as `poster_art` paints it;
the two older layers fade toward the palette guide's dusty newsprint
(#BDB39A), by 0.38 and 0.62, and the fade scales with each pixel's own value
-- bright ink goes first, a dark title holds. Only this species' older paper
fades: the club, bar and store posters are untouched. `card_art.paint`
applies a wall poster tile's `fade` when it has one.

LAYERS BY ALLOCATION, NOT ARITHMETIC. A first draft set each sheet's layer
by index and would have put overlapping sheets on one plane where a course
wraps round and where courses meet. Each sheet now takes the first layer in
its preference list where it overlaps nothing already there, in angle round
the pole and in height.

THE SLOT IS FILLED BY CONSTRUCTION, measured over the genome's whole range
(7 diameters 0.09-0.40 m x 8 bands 0.3-2.4 m x 3 forms x 4 variants, 672
plans): every one within Zoo's 2 cm on all three axes, centred, no two faces
sharing a plane. Two things the sweep found and fixed: a pair on a 0.30 m
wooden pole covered 118 degrees of it and fell 4 cm short of the slot's
width -- any cardinal side left bare now gets a faded scrap, as a real pole
has -- and paper on the INNERMOST layer at both ends of an axis sits 12 mm in
each side, 24 mm short, so side paper goes on layer 1 or above; a stack's
older sheet overshot a 0.3-0.5 m band and is clamped inside it.

Triangle budget 800, a regression detector and not a frame cost: measured
706 at the genome's corner (wrap, 0.09 m, 2.4 m).

Tests: `tests/test_pole_flyers.py` (26 + 3 in Blender): the genome and the
kit stem; every form fills, centred, with no shared plane, at 5 diameters and
3 bands in every variant, inside the budget; the paper curves round the pole
and faces out; only older paper fades; fading takes bright ink before dark;
a pair keeps paper on the back; determinism; a built pole is one object and
one material and emits nothing. Census (`tools/coplanar_census.py`): 3
builds, 0 with coincident pairs, 0 that did not build. The species
registries: 89 species, 345 census builds.

## [1.33.0] - the club posters under blacklight

Cold run 9115 hung the club posters and showed the club's dim coloured light
take their whites: measured at 2 m on the poster band, the painted near-whites
(~250) arrived at 92-127 luma and the band's median sat a few levels over the
wall. Offered three answers -- leave them dark, a blacklight treatment, a
warm wash on the poster walls -- the walker chose "blacklight treatment for
the club posters", with "if it looks bad, no light is also ok".

THE ART IS ITS OWN LIGHT. A club run's material is
`materials.make_backlit_material` on the same atlas: emission from the artwork
at 0.6, the diffuse copy at 1.0 so the paper still takes the room's light
(`poster_wall_forms.BLACKLIGHT`, by family; only the club is in it). Dark ink
stays dark and the bright inks glow, as fluorescent ink does under UV tubes.
The same atlas and the same one material a run: no texture, no draw and no
light added. Named `_Face` (was `_Art`), so Lux's emissive binder finds it
and a power cut takes the blacklight with the lights.
`_card_atlas.build_art` takes ``lit=(emission, albedo)``; None is paint, and
every other caller is unchanged.

JUDGED ON THE WALK before it shipped: the six club modules 9115 used,
rebuilt under their exact stems (same atlases, one mesh, one image each),
swapped into a copy of 9115's walk scene and shot at the same stations.
Poster band at 2 m, paper -> blacklight:

    station   p5          p95           max
    club S    0.5 -> 1.0  58.4 -> 192.4  126.5 -> 246.5
    club W    0.0 -> 0.0  29.2 -> 182.8   92.3 -> 237.2
    club E    3.4 -> 4.8  36.3 -> 130.5   91.9 -> 244.3

The whites come back and the blacks stay black; at 4 m the runs stand out of
the dark walls as the neon sign does (root repo
docs/cold_runs/cold_9115/blacklight_probe.png).

Tests: the built club run carries one `_Face` material emitting its texture
at `BLACKLIGHT`'s strength, and the other three families still emit nothing
(fails against 1.32.0's recipe, club only); only the club is blacklit.

## [1.32.0] - the club figure: three poses, curves, and the silhouette test

The walker, 2026-09-30: "fix the arm and legs, add the poses, then
placement", and "for the stripper, we want some thigh/waist curves, and a
little cleavage like in the duke nukem 3d comp"; with two more guides now in
the root repo's docs/reference/ -- drawing figures, and drawing clothing
layers. The club family only.

THE SILHOUETTE TEST (the figure guide: fill the figure black at poster size;
"if two shapes merge, change the pose"). It found 1.31.0's one pose merged
twice: the hand-on-hip elbow into the waist and the legs into one column (the
crossed free knee closed the wedge). Each pose now declares the gaps it keeps
(`pixel_figure.GAPS`) and `gaps()` measures them on the silhouette as drawn,
outline included -- the fraction of a band's rows the silhouette splits in.
Measured on 1.31.0's pose at 77 and 101 px: legs 0.10 and 0.31, the near arm
0.14 and 0.78. Every pose now: 1.0, at every height from 60 to 120 px,
mirrored or not. The pole is drawn behind the body and is not its silhouette,
so no gap can be the pole's.

THREE POSES (`pixel_figure.POSES`), chosen by the headline
(`poster_art.CLUB_POSES`, two a row where both fit): the hand behind the head
(1.31.0's, the elbow out and the shin angled away); the pole lean, the far
hand high on a brass pole, the near knee lifted out and its foot tucked to the
standing knee; hands on hips, both elbows out at different heights. A pole
starts under the headline and ends at the stage.

CURVES AND THE SWIMSUIT: a narrower waist, a wider pelvis and fuller thighs;
the bust as two masses over the ribcage with a near-black cleft between them
above the top -- a little cleavage, PG-13 by the walker's comp. The swimsuit
is built as clothing (the clothing guide): two cups and a gore, halter straps
to the neck, a bottom whose band follows the pelvis's tilt and ties at the
hips.

NOT EVERY EDGE THE SAME LINE (the figure guide: "lit edges can disappear"):
the outline stays near-black against a form's shadow side and softens to the
form's own second value where every form it touches is lit.

All 72 club sheets still pass the three poster checks at unchanged
thresholds. Mix: centred 44, diagonal 18, off-centre 10; performers 60
(pole 21, akimbo 21, behind the head 18), cocktails 12.

Tests: `tests/test_pixel_figure.py` rewritten for the poses (74): each pose's
gaps at five heights both ways round, a one-column figure that the gap
measure fails, the pole outside the silhouette, both value extremes, the
line round every body pixel and not one line everywhere, the swimsuit, the
straps, and the cleavage -- counted as a vertical run on the centre line,
because the bust's own core shadow puts 2-7 near-black pixels in that window
with no cleft drawn, and a pixel count passed it (measured: longest run 4-6
with the cleft, at most 2 without). `tests/test_poster_wall.py`: every
performer headline names real poses and the set shows all three.

## [1.31.0] - the club posters redrawn: a figure, three layouts, whites and blacks

The walker, 2026-09-30: "add silhouettes, keep it PG-13", with Duke Nukem 3D's
club dancer (1996) as the comp for how far suggestive goes, the art-direction
feedback on 1.30.0's atlas ("more color and depth"), two figure references
(Dingemans' "How to draw figures without a model"; Loomis's *Fun with a
Pencil*), "using whites and blacks for depth is essential", and the typography
guide. All five are indexed in the root repo's docs/reference/POSTER_GUIDES.md.
The club family only; bar, alley and store are still 1.30.0's recipe.

THE FIGURE (`core/pixel_figure.py`, new, pure Python). A hand-authored joint
table -- contrapposto, eight heads, the weight over the standing leg, the free
knee crossing in -- then the three masses on it as shaded capsules and
ellipsoids lit from the upper left, banded into five values a ramp with a
near-black core and a near-white specular, the far limbs a step darker, then
a pixel outline round the whole. Swimwear and a pose, no more. Two earlier
cuts are recorded in its docstring: flat blobs read as a lump, a hand-typed
sprite as a doll.

THREE LAYOUTS (`poster_art.club`), from the feedback's library: a lit cream
marquee ringed with bulbs (centred), a stepped diagonal headline with the lamp
hung below it (diagonal), a gold information strip beside the figure
(off-centre). A spotlight from its lamp to the stage is the eye path; the
stage throws a white pool; the ground goes near-black below the stage. The
drink rows show a cocktail standing in the pool instead of the performer.

A LAYOUT MUST SET ITS TITLE AT DISPLAY SIZE. The typography guide: "Do not
solve every fit problem by shrinking the type." A layout is a sheet's only
when its whole headline sets at scale 2 of `CLUB_FACE`; a title one asymmetric
layout cannot hold tries the other before the marquee (straight to the
marquee made two thirds of the set centred). Measured against 1.30.0: 12 of
72 club titles set at 7 px caps, smaller than their own punchlines. Two
headlines fitted no layout in any face and were rewritten, the guide's first
fix: CHAMPAGNE ROOM is BUBBLY ROOM, SHOWGIRLS is SHOW GIRLS.

ONE DISPLAY FACE: monogram italic (`CLUB_FACE`), the walker's pick from all
eight. Pixel Operator Bold, the shop signs' face, was the first pick; at its
display size (scale 2, 18 px caps) AMATEUR, BIRTHDAY and OPENING are 110, 120
and 104 px against a 102 px marquee.

MEASURED, NOT ASSUMED, by `poster_checks` at unchanged thresholds: all 72 club
sheets (12 rows x 6 keys) pass title contrast, focal step and mass spread.
Lessons kept in the code where they were learned: saturated colour is not
light value (brighter grounds cut title contrast and barely moved the blur);
a beam behind the letters cost them contrast (2.995 against 3.0); the dark end,
not the light one, held the diagonal sheets under 85 (their darkest twentieth
blurred to 39-43 luma until the floor went near-black).

Mix at 72 sheets: 44 centred, 18 diagonal, 10 off-centre -- reported, not
floored.

Removed: the 1.30.0 club motifs on a burst (`GLAMOUR`: heel, lips, pole), which
the figure replaced; the martini stays as the drink rows' focal.

Tests: `tests/test_pixel_figure.py` (new, 12): both value extremes present,
each ramp two value groups wide, the outline rings the figure, the height
asked for, mirrored is the same figure, the swimsuit across chest and hips at
every size, determinism. `tests/test_poster_wall.py`: a club title sets at
display size (fails on 1.30.0's art, 12 of 72), every layout is used, the
club's face and its small-line fallback carry every glyph.

## [1.30.0] - poster walls: four families, the three tests, one draw a run

The walker, 2026-09-29: posters to "appropriately fill out certain walls" --
strip club interiors, bar interiors, exterior alley walls and poles, store
windows and walls -- by three guides now in the root repo's docs/reference/
(POSTER_GUIDES.md indexes them). Measured against those guides the card
shop's posters failed five checks of seven. This release is the Zoo half:
the art, the copy, the checks and the species. Nothing places it yet.

THE COPY (`core/poster_copy.py`): twelve rows a family, invented Delco copy,
PG-13, suggestive and never explicit -- a promise, a double meaning, a
deflating line (the lewd guide's shape). A table, never generated. Held
against a denylist of real businesses, bands and brands and against the
factory's other lists, each applied the way its owner applies it (the card
shop's whole-word list as whole words: PRO is a card brand, not a crime inside
PROBABLY; WINGS is a team, and HOT WINGS NITE became HAPPY HOUR). Phone
numbers are in the 555-01xx block reserved for fiction.

THE ART (`core/poster_art.py`), a family a layout rule: `club` brash faux
glamour on an airbrushed ground with a gold rule and one motif on a burst;
`bar` a photocopied gig bill, the band reversed out of a black bar, a crude
1-bit image, the date; `alley` a day-glo handbill, the headline reversed out
of a black band, a picture chosen by what the bill is about, tear-off tabs and
tape; `store` a day-glo sale poster, the deal across the top, a burst, the
fine print on a white strip. ONE FLAW WITH A CAUSE each: the club's gold one
pixel off its rule, the copier's specks and drum streak, the handbill's
pocket fold, the store window's sun-fade.

THE THREE TESTS (`core/poster_checks.py`), the art guide's section 1 as
measurements: the headline's WCAG contrast at the size it covers on the walk
camera at 5 m (held to 3:1, WCAG's large-text minimum); the focal image's luma
off the ground under it (half a value group, stated as a choice); the blurred
poster's spread (one value group). They found real defects on the first run
and every one was fixed in the art, not the threshold: dark-on-dark club
posters (focal 29-41, blur 42-59), text-only handbills that blurred to an
even field, red on orange measuring 1.6:1, a black outline that made club
titles WORSE at distance (reverted, recorded), a thin guitar that was mostly
paper. One was the instrument's: measuring the picture against a ring round
it read a neighbouring title band as ground, and tightening the box made the
figure smaller -- it now measures against the ground the painter laid.
Every row of every family passes, at four seeds.

THE SPECIES (`poster_wall`, `core/poster_wall_forms.py`): a run of posters
as ONE module -- every sheet a tile of one atlas, one mesh, one painted
material, one draw however many sheets (a card-shop `poster` is up to four
draws and a texture each). No sheet repeats in a run while the copy lasts.
The family is `params.form`, stemmed `_f<family>`. The slot is filled by
construction and never stretched: the end sheets stand at the run's ends, the
band's top and foot are reached; overlapping sheets stand `LAYER` (4 mm)
apart, alternating rather than accumulating (stepped by index, a 32-sheet
collage stood 12 cm off the wall). Depth 4 mm to 2 cm: a run is paper on a
wall and Zoo's fit check holds depth to 2 cm. No collision, no light.
Coplanar census: 3 builds, 0 with pairs (4 / 6 / 24 tris).

Tests: `tests/test_poster_wall.py` (40 in Blender); the species registries
(`test_genome`, `test_coincident_faces` 339 -> 342, `test_theme_style_
resolution` 87 -> 88).

## [1.29.0] - a 1990s cooler: soda, sports drinks, milk, beer

The walker, 2026-09-29: "Bottled water wasn't really a thing in the 1990s in
USA ... so we should prioritize, soda, gatorade (sports drink), milk, beer",
with reference photographs of a lager can and bottle, 90s soda cans, a
sports-drink bottle and a half-gallon milk carton -- references for the look;
every name on the shelf stays invented.

`LINEUP` is now COLD SODA, SPORTS DRINKS, DAIRY, COLD BEER, ICE COLD DRINKS,
JUICE & TEA. BOTTLED WATER is gone, word and door (`door_water`), and SPORTS
DRINKS takes its index in `SECTION_WORDS`, so the other sign regions keep
theirs. An 8 m run of ten doors is soda, sports drinks, dairy, beer and cans;
the four-door run in gas_station_a02's food-service room, soda and sports.

SPORTS DRINKS (`door_sports`): 20 oz bottles, an orange cap, the liquid
through clear plastic in `SPORTS_LIQUIDS` (fruit punch, orange, lemon-lime,
cool blue, grape), a dark green label and an orange bolt. DAIRY adds
half-gallon gable-top cartons -- white, red or blue print, a fin and a gable
-- on alternate shelves between the gallon jugs. COLD BEER adds a shelf of
long-neck bottles, green or amber glass, a crown, a cream label in the
brand's band colour, beside the 12-packs and tallboys.

COST: unchanged -- no light, no material, three submissions a run; the glow
image keeps its size (690 x 522 at a 0.72 m door): water's panel and sign row
became the sports drink's.

Tests: `test_the_lineup_is_the_walkers_order` and
`test_no_bottled_water_anywhere_in_a_1990s_cooler` (both fail on 1.28.0).

## [1.28.0] - the cooler wall sells soda, beer and milk, each behind its own sign

The walker, 2026-09-29: "there should be fridges of cold sodas, beer, milk,
etc, with glowing lights too". `cooler_run` already glowed; it did not sell
beer, and it did not sell what its signs said.

THE DEFECT. A run's sign words were drawn by one hash and each door's stock by
another, so a DAIRY band could stand over soda bottles and the five words
included no beer. Now `LINEUP` -- COLD SODA, COLD BEER, DAIRY, BOTTLED WATER,
ICE COLD DRINKS, JUICE & TEA -- is read left to right, two doors a section,
and every door carries its section's stock (`SECTION_STOCK`). An 8 m run of
ten doors is soda, beer, dairy, water and cans; the 3.28 m run in
gas_station_a02's food-service room is soda and beer. The seed chooses among
approved options; it no longer decides whether the sign is true.

BEER (`door_beer`): 12-pack cartons two high on alternate shelves, tallboys on
the rest, in `BEER_COLOURS` -- the six invented beers of the window neon
(`club_names.WINDOW_NAMES`), one table sold in two places and held equal by
an assert at import. WATER (`door_water`): clear blue bottles in three cap
and label colours; the first cut used one and `test_cooler_run` read the
panel as four colours, flat.

COST: no light, no new material, still three submissions a run (built test).
The glow image grows with two more door panels and a sign row: 690 x 522 at a
0.72 m door, RGB about 1.1 MiB before mips. NOT BUILT, named: its sign rows
use half the width; packed two across, the image would be about a quarter
smaller.

Tests: three new in `test_cooler_run.py` (8 cases, failing on 1.27.0).

## [1.27.0] - a beer sign hung in a store's window; the counter accent's hardware

The walker, 2026-09-29: "add the warm counter accent and the window sign
next", from their 1990s lighting reference on the convenience store at night
-- a small red or blue window sign as an accent against the fluorescent
interior, and a warmer accent at the counter.

THE WINDOW FORM: `neon_sign` takes `params.form` ("wall", "window"; the
genome lists wall first, so every sign already placed builds as it did --
`MAIN_DIGESTS` and 120 wall plans compared byte for byte). A window sign says
a beer from `club_names.WINDOW_NAMES` (WOODER ICE, JAWN LITE, YOUSE BREW,
SHOOBIE SUDS, SCRAPPLE STOUT, COLD ONE HON -- held against `DENYLIST` and a
new `BEER_DENYLIST` of real beers, the local ones first) in red on blue or
blue on red (`WINDOW_PALETTES`). Its tubes stand on the same standoffs in
front of a CLEAR SHEET (`M_NeonSign_acrylic`, see-through at
`SHEET_OPACITY` 0.12, storefront glass's value), which stops `HANG_FRAC`
(12%) short of the slot's top; two `NeonSign_Chain` rods rise from it to the
top, where the sign hangs. The chains share the standoffs' material: the
form adds a part and no material. The kit stems it `_fwindow_n<k>`.

REFUTED, kept in `neon_forms.py` above the rule that replaced it: the first
draft dropped the backer and stood the tubes in the slot's middle plane.
`fit_exact` maps the prims' bounds onto the slot per axis, so a sign with
nothing but tubes across its depth would have been stretched ~3x into the
slot's 6 cm -- flat ovals that pass a fit check. The sheet fills the depth
the way the wall form's can does, and every window plan fits at a scale of 1
(`overshoot_m` 0).

THE COUNTER ACCENT'S HARDWARE: `fixtures.FIXTURES["counter_accent"]` is the
pendant's -- `pendant_fixture`, mount above, the bulb point is the anchor.
Deli Counter (>= 0.160.0) derives the anchor, Lux (>= 0.59.0) lights it.

Tests: `tests/test_window_sign.py` (20, every one failing on 1.26.0);
`test_club_bpy.py` builds the window form at two corners, passes the fit and
plane checks and exports the sheet as the only BLEND material.

## [1.26.0] - the price pylon is 3.4 m wide

The walker, 2026-09-29: "yes, make the pylon bigger", after 1.25.0 measured
the limit of a 2.4 m face: eight 5-wide letters across it cannot carry a
stroke over ~5 cm, so FLAPPHAS read as a word to about 12-14 m and as a green
block beyond.

The genome's default, which Lot reads (`site_furniture.SPECIES`, pinned
equal by Lot's own test), and `DC_SIZES`: 2.4 x 0.5 x 6.5 -> 3.4 x 0.7 x 9.0,
the width the range's top and the rest in proportion (x1.42, the height at
the range's top). THE WIDTH IS WHAT READS: the name fits at 5 texels a stroke
where it fitted at 3 (80 px/m: 3.75 -> 6.25 cm) and the dollars at 4 where
they were 3 -- and 3.75 cm read as a word at 12 m on cold run 9108's walk
copy, so the same frame should carry the name about 20 m. The species built
at this size since 1.19.0 (the range's top was a built test case); census 3
builds, 0 pairs, 132 tris each.

`tests/test_price_pylon.py`: at Lot's size the name sets at scale 5 or more
and the dollars at 4 or more, and the genome's default is `DC_SIZES`.
Without the change it fails.

## [1.25.0] - the pylon's name and prices are set as large as the face allows

The walker, 2026-09-29: "do the pylon brand sign at night next", after cold
run 9102's note that the green FLAPPHAS cabinet barely read at night.

MEASURED FIRST, and the premise was half right. On cold run 9107's walk copy
(the pylon rebuilt with Zoo exactly as Lot's cover kit asks for it, swapped
in with the shipped texture import settings, a camera 12 m out square to
the face; the rebuilt control reproduced the shipped frame to the decimal):
the brand FIELD reads at night, luma 125 against the price panel's 251. What
reads at neither time of day is any LETTER -- FLAPPHAS a smear, the prices a
blank white panel (90% of it clipped at night). 1.19.0 fitted the name and
the dollars by one integer scale to their width: the name 0.26 m tall in a
1.4 m face, the dollars 0.18 m in a 0.5 m row, 2-3 texels a stroke, on a
184-texel face drawn about 110 px wide and softened by the frame.

THE CHANGE (`price_pylon_forms`): the name keeps its width-fitted scale and
is stretched in whole rows to fill half its face's height (`NAME_FILL`,
21 -> 42 px); the dollars start after the widest grade label and may take
40% of the face (`DIGITS_AT`, `DIGITS_W`), which sets them at scale 3 where
they were 2, stretched to their row where it fits. Same image size, same two
submissions.

    at 12 m, luma mean / standard deviation (the detail)
                        1.19.0          1.25.0
    brand, night        125 / 48        157 / 59
    brand, noon         143 / 26        162 / 33
    prices, night       251 / 10        250 / 11
    prices, noon        231 / 11        229 / 12

The name now reads as a bold word at 12 m, day and night. The digits still
do not resolve there: under this frame a stroke has to be about a tenth of a
metre to survive at 12 m, and a 0.5 m row cannot hold digits that bold. THE
LIMIT, stated so nobody tunes against it: eight 5-wide letters across a
2.3 m face cannot have a stroke over ~5 cm, so FLAPPHAS on this pylon reads
as a word to about 12-14 m and as a green block beyond. At 20 m every
variant measured read as coloured blocks.

MEASURED AND NOT SHIPPED: a TRANSMITTED glow -- the lit face's emission the
square root of its artwork in linear light (a translucent face seen by day
through its colour twice, by night once) -- brightened the field 125 -> 222
and washed the name out against it (detail 48 -> 17), and brightened the
sign at noon 143 -> 196, because a lit face glows in daylight too.

`tests/test_price_pylon.py`: the name fills at least 35% of its face inside
the rules (1.19.0: 19%); the dollars at least half their row (1.19.0: 14 of
40 px); the dollars set at scale 3 or more and, with the 9/10, fit between
the widest grade label and the face's edge. Without the change both fail.

## [1.24.0] - only a storefront-lit room's plate tiles stay apart

The walker, 2026-09-29: "yes, narrow it to the storefront rooms".

1.23.0 stopped merging EVERY floor and ceiling. It restored the room it was
for -- gas_station_a02's carpet seen through the glass 16.9 -> 20.5 on cold
run 9106 -- and cost the whole library: draws 71,802 -> 77,139 summed over
the 53 headings (+4 to +230 at 51 of them), median p95 4.76 -> 5.1-5.2 ms,
and 7 -> 10-11 stations over the provisional budget, because every room over
8 m in every building split and interiors have no occlusion culling.

THE CHANGE: the rule moves from a family to a flag. A plate slot carrying
`light_budget_tiles` -- Deli Counter (>= 0.157.0) sets it on the floor and
ceiling of a room lit from outside through storefront glass, where the budget
was measured to bind -- is planned under its own name (`_lbt`, after the
glazing; `kit.LIGHT_BUDGET_STEM`, in the key too, so a flagged and an
unflagged floor of one footprint are two builds), reaches the plan
(`dna.resolve_module_plan`), and `_arch.build_slab` names its tiles with
`partnames.LIGHT_BUDGET_MARK`, which `is_mergeable` refuses. Only floor and
ceiling roles honour it (`kit.LIGHT_BUDGET_ROLES`). Every other floor and
ceiling merges again exactly as before 1.23.0; `LIGHT_BUDGET_FAMILIES` is
gone, recorded as superseded above `LIGHT_BUDGET_MARK`.

`tests/test_merge_by_material.py` (1.23.0's tests replaced): a marked tile is
not mergeable and unmarked floor, ceiling and roof tiles are; six marked
tiles plan no group where six unmarked plan one; the flag rides the stem and
the key on plates (a flagged and a plain floor are two modules) and a wall
ignores it. Built: a flagged 23 x 12 m floor and ceiling export six marked
tile meshes each -- without the recipe's mark, one (`Floor_carpet`) -- and
the controls, an unflagged 23 x 12 m floor, a 6 x 5 m floor and a roof, are
as before 1.23.0.

## [1.23.0] - a floor's and a ceiling's tiles ship as their own meshes

The walker, 2026-09-29: "yes, split the floor and ceiling tiles".

`arch.tile_parts` has cut every room-sized plate into tiles no larger than
`PLATE_TILE` (8 m) since roadmap 54, so each is its own per-mesh light budget
-- GL Compatibility lights at most `max_lights_per_object` (8) positional
lights per MESH. 1.1.0's merge-by-material then packed those tiles straight
back into one mesh per material, and every room-sized floor and ceiling in the
library reached Godot as one object again. Nothing noticed until it was
visible: on cold run 9105, gas_station_a02's 23 x 12 m sales floor shipped as
one floor mesh and one ceiling mesh with 20 light claimants each (the
storefront spills took them from 16), the engine's choice of eight moved, and
the room lost some of its own lamps -- the carpet seen through the glass
19.7 -> 16.9, and 20.1 with the cap raised to 64 on the same build.

THE CHANGE: `partnames.LIGHT_BUDGET_FAMILIES` ("Floor", "Ceiling") --
`arch.root_name` of the two species -- are not mergeable, so each tile is
exported as itself, as floors were before 1.1.0. Not by tile index: every
plate numbers its own tiles, so two `_t0_0`s can lie either side of a
stairwell, and a floor cut around a void is several plates. A floor or ceiling
no larger than one tile is its one `Panel`, byte-identical. A ROOF is a plate
too and stays merged: it is seen from outside and above and a large one is
dozens of tiles, the draw-call side of the same trade, to be priced on its
own.

COST, stated before it is measured: a draw call per tile beyond the first on
every floor and ceiling over 8 m on a side -- the sales floor's two go from 2
submissions to 12 when the room is in view. The cold run that ships it prices
it in draws and frame time against 9105, with the per-mesh census.

`tests/test_merge_by_material.py`: the families are the floor and ceiling
roots and a subset of the plate species'; floor and ceiling tiles are not
mergeable and a roof tile and a pack wall are; six floor tiles plan no group
where six roof tiles plan one. Built: a 23 x 12 m floor and ceiling each
export six tile meshes (without the change: one, `Floor_carpet`); a 6 x 5 m
floor is its one `Floor_Panel`, and a 23 x 12 m roof's visual is still one
merged mesh.

## [1.22.0] - a storefront's spill is light with its hardware elsewhere

The walker, 2026-09-29: "do the outward spill next". Deli Counter (>=
0.156.0) derives `storefront_spill` anchors outside a storefront whose
room's ceiling row reaches the glass, and Lux (>= 0.57.0) bakes them from
the manifest -- the store's own light thrown out through the glass onto the
pavement. Nothing here builds anything for one: a spill has no hardware of
its own, because what a player sees it come from is the lit room, whose
troffers the `fluorescent` row already builds. `core.fixtures` records that
as `HARDWARE_ELSEWHERE["storefront_spill"]`, the canopy wash's standing, so
the plan skips it with that reason instead of "no fixture species", and the
type-coverage test (`tests/test_fixture_type_coverage.py`, which fails at
commit when Deli Counter emits a type Zoo has not decided about) is decided
BEFORE Deli Counter emits it.

`tests/test_fixture_type_coverage.py`: the spill is hardware-elsewhere and
not a FIXTURES row; a plan of one places nothing and skips it naming the
troffers. Without the entry it fails.

## [1.21.0] - a storefront row's reach rides its markers

The other half of Lux 0.56.0 ("yes, do the glass first then the troffer
reach", the walker, 2026-09-28). Deli Counter (>= 0.155.0) stamps `reach` on
a ceiling row walled by storefront glass -- the horizontal metres from the
row to the glass -- and Lux derives the lamp's range to the floor there. The
marker path is how lights ship, so the number has to be on the marker the way
`drop` is (v0.50): `core.fixtures.plan` carries it on every per-lamp
placement (0.0 where the anchor has none), and `build_fixtures` stamps
`lux_reach` on a marker ONLY when it is above zero, so every other building's
markers and fixture GLB are as they were; Lux reads an absent key as 0.

`tests/test_fixtures.py`: reach rides every lamp of a storefront row and is
0.0 on the control row; built, the GLB's two sales-floor markers carry
`lux_reach` 6.0 and the stockroom's carries none. Without the change both
fail (KeyError 'reach'; no marker carries it).

## [1.20.0] - a storefront is clear glass

The walker, 2026-09-28, after cold run 9103's night frames showed the sales
floor brightening and the street not seeing it: "yes, do the glass first then
the troffer reach".

A storefront's panes wore the theme's `glass` -- delco_1997's `glass_delco`,
0.38 opaque over a dark teal, which is a house window's -- so a third of a lit
shop floor stopped at the pane. They are now clear float glass:
`arch.SF_GLASS_OPACITY` 0.12, from the ~88% visible transmission of clear
6 mm float glass, not tuned by eye. The panes keep the theme's glass SURFACE
(its albedo and roughness) under their own material,
`M_Skin_glass_<theme>_storefront`, through a new `own=` on
`materials.make_see_through_material`: the caller's opacity replaces even an
authored see-through pack's, under the pack's name with `_<own>` appended.
Every other caller of that helper, and every window, is unchanged.

MEASURED FIRST on cold run 9103's walk copy at night (look_shots, the
player's graded frame; the panes' opacity set at runtime, everything else as
shipped; the control reproduced 9103's own figures, 8.8 / 6.2 / 4.2):

    through the storefront      mean 6.2 -> 9.0     p95 31 -> 48
    inside the sales floor      mean 8.8 -> 9.4
    the storefront from 15 m    4.2 -> 4.4  (that camera stands behind a
                                pump island; it is not a view of the store)

COST: none in submissions. A storefront module had one glass material and
still has one; the library gains one material.

`tests/test_storefront.py`: SF_GLASS_OPACITY is clear glass's; every pane of
a built storefront wall and door (leaves and transom included) is the
storefront material at that opacity -- which fails without the recipe change
('M_Skin_glass_delco_1997' where '..._storefront' was wanted) -- and the
control, a plain window built against the same library, keeps the theme's
material at 0.38.

## [1.19.0] - the gas station's price pylon

New species `price_pylon`. The walker, 2026-09-28: "do the price pylon
next". The references: "A pylon sign at the road. Tall, freestanding, at the
kerb where a driver reads it before the building ... the one a player sees
from three streets away. Owner: Zoo (a species) plus Lot (at the frontage,
facing the road)" (docs/SET_DRESSING_REFERENCES.md), and the pumps'
"dollars-per-gallon to the nine-tenths ... the 9/10 fraction is the detail
that reads as 1997 at a glance" (docs/proposals/GAS_STATION_SHOP.md).

WHAT IS BUILT (`core/price_pylon_forms.py`): a concrete plinth and two steel
posts; a brand cabinet -- FLAPPHAS, the store's own name, in the coffee
sign's colourways so the store's two signs are one brand; a price cabinet,
REGULAR / PLUS / SUPER each with its grade's colour (the pump reference's
silver, red, gold) and a 1997 price to the nine-tenths, 1.19 9/10 by
default; and an OPEN 24 HRS strip. Every cabinet's two faces are lit from
ONE backlit image, `M_Pylon_<art>_Face` (Lux's power cut takes it), at 1.4
-- over the cooler wall's 1.0, since this one is read from three streets
away -- and the back face maps u reversed, so the sign reads from both
directions along the road. Headline in `monogram`, the slush machine's
reason. One scale for every grade's name (fitted each alone, REGULAR set at
half PLUS's size).

TWO SUBMISSIONS: painted steel and concrete (colours in `Wear`), the glow.
Census 3 builds, 0 pairs (132 tris each; budget 400); `CENSUS_BUILDS` 336 ->
339; audited genome count 86 -> 87.

NOT YET PLACED: Lot stands it at the frontage (its placement is a Lot
change, planned in docs/proposals/PRICE_PYLON_PLACEMENT.md); until then the
species exists and nothing in a level asks for it.

## [1.18.0] - a storefront is see-through glass

The walker, 2026-09-28, with six photographs of convenience stores at night
-- "the 'glow' of the gas station at night, coming through the glass doors
... glass see-through door" -- and, asked whether the storefront itself
should be see-through: "yes, make the storefront see-through glass".

MEASURED FIRST on cold run 9099's package, gas_station_a02: the entry
"doors" were no doors -- `doorway` is an open frame, so each was a
1.56 x 2.2 m hole between bronze jambs under a 1.7 m opaque header, with the
closed state's collider and no leaf -- and every glass-facade wall panel
was opaque. That was deliberate (0.36.0, `dna.OPAQUE_FOR`): a see-through
structural slab is "a wall you scout enemies through". The walker has now
decided shop fronts are the exception, and only shop fronts.

A STOREFRONT is a wall or door slot Deli Counter tags `glazing:
"storefront"` (Deli Counter 0.153.0: a `storefront_glass` wall on an
enterable building). It builds (`arch.storefront_parts`, `_arch.build_slab`):

  * a WALL as a kick plate (0.45 m), a header from 3.0 m (or 0.4 m under the
    top), a 0.05 m mullion at each end -- two modules meet in a 0.10 m
    mullion -- and one see-through pane between, buried 5 mm in the frame;
  * a DOOR as its jambs, a head rail, a transom pane and a header, and in
    every state but "open" two framed glass leaves with a push bar across
    both faces. The open state is its own module without them: `plan_kit`
    asks for that state's art on storefront doors only
    (`STOREFRONT_STATE_ART`), so no other door in the library gains a module.

THE COLLIDER IS UNCHANGED: collision still comes from `slab_parts`, so the
glass stops a body and a door's closed state still blocks. The panes take
the window's own `M_Window_glass` and the theme's see-through `glass` pack.
`OPAQUE_FOR` and every other glazed wall -- banks, towers, clubs -- stay
opaque; `test_opaque_structure` is untouched and passes.

THE NAME: `_gstorefront` after the material (`kit.module_stem`,
`STEM_GLAZINGS`), because a storefront wall and a plain glass-facade wall of
one width were two geometries under one name. `facade` stays out of the
name, so every facade-window module keeps its name. Deli Counter's
`themed_tscn.module_stem` is the mirror.

MEASURED: the frame tiles as `slab_parts` does -- touching boxes, opposite
faces inside the frame -- and no pane lies on any frame face, at six sizes
(a test). Built: panes blend on the see-through pack, the frame is
structure, a closed door has leaves and an open one none.
`tests/test_storefront.py`. NOT MEASURED: draw calls in a level (each
storefront module is two submissions, frame and glass, as a window is) and
how the interior reads from the street at night -- the next cold run.

## [1.17.0] - the hot dog roller grill

New species `roller_grill`. The walker, 2026-09-28: "do the roller grill
next", with three photographs: two store stations (zones of one kind split
by dividers, a black tube tag naming each, a printed panel across the
front, a warm-buns drawer below, a glass guard) and a countertop
merchandiser (rollers across the width with three columns of dogs in the
grooves, a black control panel with two dials, two lights and a switch, a
glass case with a shelf of buns). The proposal's own words: "a slanted bank
of chrome rollers turning under a clear hood ... grease darkening the
rollers toward the back, and a printed 'Buns' panel across the front of
the cabinet below". Not `flat_top_grill`, which is kitchen equipment.

HOW THE DOGS LIE, a refutation kept in `core/roller_grill_forms.py`: the
store photographs read for a moment as rollers running front to back with
the dogs across them; the countertop photograph settled it -- rollers
across the width, each dog in the groove between two, parallel, which is
what turns it. "Laid across them" is laid ON the bank.

WHAT IS BUILT: a counter-height bun cabinet with a printed NICE BUNS panel;
a steel pan with the printed control panel and two knobs; rollers across the
width climbing gently toward the back (7 degrees, less when the hood is low)
each greasier than the one in front (the front at 1.0 of the chrome, the
back at 0.45); columns at least 0.26 m wide -- three at the default 1.0 m,
the photograph's count -- one kind each (BIG JAWN, CHEEZY, HOT LINK,
TAQUITO: deep red, pale, red, tan, each its own thickness), a dog in every
groove but where one was sold, chrome dividers between columns and a black
tag in each column's front groove; a glass hood on four posts, open at the
lower front to reach in with tongs, and a glass shelf of buns when the hood
stands 0.42 m or more over the pan.

FOUR SUBMISSIONS: chrome, painted (cabinet, knobs, dogs, buns -- colours
and the grease in the `Wear` vertex colour), glass, and one painted image.
Nothing glows. The genome offers `metal_bare` and glass only; the painted
kind is a constant in the recipe, as the counter's brass is.

MEASURED: the planner's check found cheeks on the pan's side planes, hood
panes 1-2 mm off the posts and each other, the control panel's buried back
on the cheeks' fronts, and a bun 2 mm into its shelf; `pillow`'s crown is
metres, and at 0.4 the first buns stood 150 mm out of the slot; at 1.4 x
0.8 x 1.2 the full climb put the back cheek 36 mm through the top. Each
fixed at its source; a control proves the check sees a pair here. Census 3
builds, 0 pairs (916 / 1,564 / 2,496 tris; budget 3,000); `CENSUS_BUILDS`
333 -> 336; audited genome count 85 -> 86. "hot dog grill" now resolves to
this species rather than the flat top; "grill" alone stays the flat top's.

## [1.16.0] - the registers on the counters have their green display

The walker, 2026-09-28, with photographs of a beige Fujitsu, a Sharp XE-A207
and a TEC MA-1595: "I also want the cash registers in these buildings (where
we have cash registers) to have that glowing green/black screen" -- "I've
mentioned this before". 1.0.0's `cash_register` species has it, but it
stands only as the card shop's till. The registers the stores and bars
actually stand -- the service counter's (1.7.0) and the club bar's (0.92.0)
-- were three beige boxes and no screen, and the bar's own comment promised
"a display on a stalk" that was never built.

ONE REGISTER, BOTH COUNTERS (`core/counter_register.py`): `station` is what
`back_bar_forms.counter_fitout` and `service_counter_forms.fitout` both call
now; they each spelled the same three boxes. The register's dimensions move
there, re-exported from `back_bar_forms`.

WHAT IS BUILT at a station: the beige body; the KEYPAD at the clerk's end and
the display HUMP at the customer's -- until now it was the other way round,
keys toward the customer and the hump's blank back to the clerk, which none
of the photographs stands as; a lit OPERATOR display on the hump's clerk face
("1  9.95", count then amount, the Fujitsu's); a lit CUSTOMER display on its
customer face; and a POLE DISPLAY, a stalk and a dark head with its window to
the customer. A window on a +Y face maps u from x1 to x0, or its digits read
mirrored from the clerk's side; a test holds both sides.

THE LOOK IS THE TILL'S: `register_forms.paint_screen`, `VFD_INK` on
`VFD_GROUND`, `SCREEN_EMISSION` 1.0 -- the strength 1.0.0 picked for this
screen by measured saturation -- so a card-shop till and a store register
read as one make. All three windows of every register on a counter are ONE
object on ONE image, `M_Counter_VFD_<art>_Face` (Lux's power cut takes it);
the price is `register_forms.pick_price`'s, by stem and variant.

COST: one submission a counter that carries registers, whatever their
count. The service counter ships 7 (was 6); `test_bpy_seven_materials_...`
says so, and `test_bpy_only_the_rack_header_and_the_registers_glow` names the
second lit surface. The pole and stalk go into the counter's existing
plastic. 96 triangles a register. Two parts are new, `Counter_RegisterPole`
and `Counter_RegisterHead` (a part built from two keys came back from
Blender as `Counter_RegisterPole.001`), and `Counter_RegisterScreen`.

MEASURED: the station shares no plane with itself or the service counter's
fit-out; the counter census is unchanged at its recorded residue (6 pairs
over 3 builds, body/top/base, the default form, which builds no register).
`tests/test_counter_register.py`. NOT MEASURED: frame cost in a level --
that is the next cold run's pricing.

## [1.15.0] - the frozen drink station

New species `slush_machine`. The walker, 2026-09-28: "do the slush machine
next". The references (docs/proposals/GAS_STATION_SHOP.md): a twin-hopper
slush dispenser with clear barrels showing the product -- one red, one blue,
visibly churning -- a branded topper, a cartoon mascot on the front panel, a
pull tap per hopper and a tube of stacked cups; the second adds a six-bottle
syrup rail with a labelled pump per flavour, a numbered "1 select cup size,
2 add flavor, 3 pull to fill" panel, a drip tray and a straw caddy.

WHAT IS BUILT (`core/slush_machine_forms.py`, pure, tested without Blender),
left to right as a customer reads it: a counter-height stand with the lit
mascot panel across its front; two clear cup tubes, large and medium, cups
stacked up out of them, and a straw caddy; the syrup rail -- six bottles,
each pump head in its flavour's colour, a lit strip naming each flavour
under its bottle, the lit instruction panel above -- when the station is
1.52 m or wider; and the machine: tower, base, two clear barrels (three at
1.80 m or wider) of slush, lids, a tap with a pull handle in the flavour's
colour over a drip tray, and the lit FROZEN JAWN topper. Always a red and a
blue barrel, by variant the order and the third flavour.

THE SLUSH GLOWS. It is on the backlit image with the topper and panels: a
churn-striped tile per flavour wrapped once round each barrel, behind the
see-through glass. The barrels are what a dark shop has to catch the eye;
real machines light them from the lid, and emission stands in for that at
no light's cost. Lux's power cut takes it (`M_Slush_<art>_Face`).

THREE SUBMISSIONS whatever the width: painted steel (every opaque part, its
colour in the `Wear` vertex colour), glass, glow. Parts are built named for
their key (`Slush_Barrel_glass`, `Slush_Barrel_white`) -- the coffee island's
rule; the first build came back with `Slush_Barrel.001`.

THE BRAND IS INVENTED: FROZEN JAWN, FLAPPHAS's own, "FREEZE YOUR JAWN OFF"
on the topper and "COLDER THAN YOUR EX" under the mascot. The headline face
is `monogram`, not `bold`: bold's N is its H with a three-pixel diagonal and
under the red outline the first render read "FROZEH JAWH".

MEASURED: the planner's coincidence check reported 0 pairs on the first cut
at every corner, so it was proven first -- a box 1 mm over the counter top
reports 2, the tower buried to the base's depth reports 1 (the control is a
test). Census 3 builds, 0 pairs (2,540 / 4,160 / 4,560 tris; budget 5,000);
`CENSUS_BUILDS` 330 -> 333; audited genome count 84 -> 85.

## [1.14.0] - a stack of milk crates, for the walk-in coolers

New species `milk_crate_stack`. Deli Counter 0.149.0 stops furnishing walk-in
coolers as kitchens (a grill in gas_station_a02's walk-in) and gives them a
cold-storage recipe of backstock racks, cartons, pallets and milk crates; its
first commit was refused by its own gate because `test_furnish` holds every
furnished piece to a species -- "a generated piece that routes to nothing is
a grey box, which is the defect furnishing exists to reduce". So the crate is
Zoo's to grow, per the gap protocol, rather than swapped for a carton.

WHAT IS BUILT (`core/milk_crate_forms.py`): hollow, open-topped crates -- a
bottom plate and four walls -- in a grid a layer at a nominal 0.34 x 0.34 x
0.28 m, each sitting 4 mm into the one below as real crates nest. One
submission: one plastic material, the stack red, blue, orange or green by
variant, in the `Wear` vertex colour. 60 triangles a crate.

MEASURED: single layers were clean at once; stacking put each upper crate's
plate 2 mm off the lower crate's inner walls and exactly on its front and
back walls' tops. The plate stands 30 mm inside its walls and those walls stop
8 mm under the rim; every other layer steps in 6 mm and neighbouring crates
leave 6 mm. Census 3 builds, 0 pairs; `CENSUS_BUILDS` 327 -> 330; audited
genome count 83 -> 84.

## [1.13.0] - the island snack gondola

New species `snack_gondola`. The walker, 2026-09-28: "do the snack gondolas
next"; the reference asks for "gondola shelving, four or five shelves of chip
bags faced out, end caps stacked with more chips".

WHAT IS BUILT (`core/snack_gondola_forms.py`, pure, tested without Blender):
a dark kick, a pegboard spine, steel uprights at every bay (1.22 m at most)
and end panels, a top rail; on both faces, shelves up the height with white
price strips; chip bags faced out on every shelf, stocked in pairs of
facings a brand; end caps at both ends of a run 2.2 m or longer, three
shelves facing down the aisle. The +Y face and the +X end cap are the -Y
ones turned half round, and a test checks every bag's printed front points
away from the gondola on all four sides.

A BAG IS A BAG, NOT A PICTURE OF ONE -- the walker's standing preference for
real structure over printed cards. Each is a `prims.pillow` stood on its
back: a puffed front and flat, planar sides, 22 triangles. Its front maps to
its brand's tile and every other face to its brand's colour, all on ONE
image (`bag_art`). Twelve invented Delco snack brands in a new table,
`core/snack_brands.py` -- DELCO DUST, SCRAPPLE CRISPS, JAWN CHIPS, YO CHEEZ
... -- denylisted against Pennsylvania's own chip and pretzel makers first
and the nationals after, lettered in the m5x7 face.

TWO SUBMISSIONS WHATEVER THE LENGTH: painted steel with each part's colour in
the vertex, and the bags. `test_bpy_two_submissions`.

MEASURED: the planner's coincident check found 3-6 pairs a build first --
the kick, spine, top rail and an end cap's back plate all ending in one
12 mm end panel at depths 2 mm apart, the top rail sharing the panels' top,
and the end cap's back plate standing 8 mm OUTSIDE the panel it was meant
to bury into. The end panels are 20 mm now and every part has its own depth
4 mm or more from its neighbours. Census: 3 builds, 0 pairs (840 / 5,164 /
18,876 triangles; the bags are most of it); `CENSUS_BUILDS` 324 -> 327;
audited genome count 82 -> 83. Deli Counter 0.150.0 routes the stores'
aisles to it.

## [1.12.0] - the reach-in cooler wall, glowing

New species `cooler_run`. The walker, 2026-09-28: "do the cooler wall next",
then "we also want glowing fridge lights"; the reference is the store's
"full back wall of glass-door reach-in coolers (drinks, milk jugs, juice),
lit from inside, with a sign band above".

WHAT IS BUILT (`core/cooler_run_forms.py`, pure, tested without Blender): a
run of glass doors on black frames with handles, steel shelves behind each,
a product panel a door (soda, cans, milk, juice and tea -- every drink an
invented brand from `core/brands.py`), a fluorescent tube down every
mullion and both ends, and a sign band across the header, one section a
pair of doors ("ICE COLD DRINKS", "DAIRY", "BOTTLED WATER", "JUICE & TEA",
"COLD SODA") lettered in `small_caps_bold` -- the first recipe to letter in
one of 1.10.0's faces. Deli Counter's `cooler_run` volume is 2.8 m deep
against a cabinet's 0.9, so the cabinet is the front of the slot and the
walk-in's plain body fills the rest: the slot is filled exactly.

GLOWING WITHOUT A LIGHT. The products, the tubes and the sign band are ONE
backlit material (`M_Cooler_<art>_Face`, Lux's power cut takes it) on ONE
image, at emission 1.0 -- double the cigarette rack's measured-faint 0.5,
to be judged on the walk. It costs no light and nothing the eight-lights
rule counts. Light SPILLING onto the floor would need real lights and is
not built; it is priced separately when asked for.

THREE SUBMISSIONS WHATEVER THE LENGTH: painted steel (colour in the vertex),
the glass, the glow. `test_bpy_three_submissions_and_the_glow_is_the_lit_one`.

MEASURED ON THE WAY: the planner's coincident-face check found 15 pairs a
build on the first cut -- the carcass's parts all ending at one back plane,
the header and kick sharing the end posts' outer planes, door rails 1 mm off
the kick and header, the tubes and panels meeting the mullions and end posts
face to face, the shelves 2 mm off the tubes -- and each was fixed at its
source, not by moving the probe. The first cut also stood the handles 5 cm
proud of the slot, which fails a fit: the door plane is set back so the
handles end exactly at its front. Census: 3 builds, 0 pairs (488 / 1,564 /
3,288 triangles); `CENSUS_BUILDS` 321 -> 324; audited genome count 81 -> 82.

A render at 20 degrees showed each door's products in its right two
thirds; square-on they fill it. That is the 0.55 m between the glass and the
panel, parallax, as a real cooler has -- recorded so nobody "fixes" it.

## [1.11.0] - m5x7 and monogram: nine pixel faces

Pixelcoat 0.53.0 vendors two more CC0 families beside Pixel Operator --
`m5x7` (Daniel Linssen) and `monogram` with its italic (datagoblin) -- and
the mint now mints them: `m5x7`, `monogram`, `monogram_italic` join
`pixel_type.FACES`. The walker approved the three downloads, 2026-09-28.

THE MINT ADDRESSES A FACE BY FAMILY FOLDER under Pixelcoat's
`assets/fonts/` (`pixel_operator/PixelOperator-Bold.ttf`), and credits each
family's designer in the minted header from `FAMILIES`. For Pixel Operator
the header is word for word what it was, so all six existing tables re-mint
unchanged.

MEASURED, not taken from the pages: m5x7's page says 16 px and monogram's
says nothing, and both are on/off, whole-advance and kern-free at 16 px and
at no other size from 6 to 31. Every character the factory letters is in
both character maps. They are the compact faces: "FLAPPHAS 75¢" is 71 px
wide on a 9-row line in m5x7 and 72 on a 10-row line in monogram, against
93 on 13 rows in Bold.

Still nothing letters in them. Choosing which label takes which face is a
recipe's change, judged on a frame.

## [1.10.0] - six pixel faces, and a mint that refuses a missing glyph

docs/proposals/CC0_FONTS.md, steps A and B. The walker, 2026-09-28: "start
on the font proposal as well, i read it and it's good".

A, A FACE PARAMETER. `tools/mint_pixel_type.py` has a `FACES` table -- file,
the pixel grid it is drawn on, the module it mints to -- and mints one face
(`--face`) or all (`--all`). `pixel_type`'s `width`, `ink_width`, `render`,
`wrap` and `fit_scale` take ``face=``, with `line`, `ascent` and `descent`
for a face's metrics. ``None`` is Pixel Operator Bold, so the ten modules
that letter with it are untouched: `pixel_type_glyphs.py` re-mints BYTE-
IDENTICAL to what was committed (27,192 bytes; the mint prints 27,191 because
it counts characters, and ¢ is two bytes).

THE FACES are the rest of the Pixel Operator family Pixelcoat already
vendors, CC0, so nothing was downloaded: `regular`, `small_caps`,
`small_caps_bold`, `mono`, and `small` (PixelOperator8, an 8 px face with
an 8-row line against Bold's 13 -- the small print). Every one was measured
through the mint's own checks rather than assumed: all 96 characters in its
character map, pure on/off at its grid, whole-pixel advances, and -- new in
`tests/test_pixel_faces.py` -- NO KERNING, a PIL-set string equal to the
face's glyphs laid at their advances on five samples, which is what makes a
table of bitmaps lossless. Pixel Operator HB is not vendored and not here.

B, A MISSING GLYPH IS REFUSED. PIL draws a character a font lacks as its
`.notdef` box, and the mint never noticed: a face without ¢ would have minted
a box and passed. The mint now reads the font's own `cmap` table
(`cmap_codepoints`, formats 4 and 12, no fontTools -- it is not installed and
a documented table is not worth a dependency) and exits naming every
character the face lacks. The two instruments are checked against each
other: a snowman the map lacks renders the same box as a private-use point.

NOTHING LETTERS IN A NEW FACE YET. This is the capability; which sign or
label takes which face is each recipe's change to make, and a frame the
walker judges. Steps C to F of the proposal (BDF and PNG-sheet readers, an
outline mode for script, VFD and hand-lettered faces, neon from any face)
are not started, and the next faces worth fetching (m5x7, monogram) need a
download the walker has not yet approved.

## [1.9.1] - a couple of carafes on the burner row

The walker, on 1.9.0's one-a-brewer render: "lets have a couple on the
warmers (not on top of the drip king)". The burner row along each long edge
now carries one carafe a face for every two stations -- on Deli Counter's
3 m island one each side, 4 -> 6 carafes; on the 4 m one 8 -> 12 -- on the
station the pair's parity picks for that face (`front_row_carafe`), -Y
regular and +Y decaf. The brewers' hood warmers stay empty.
`test_no_carafe_stands_on_a_brewers_hood_and_the_burner_row_has_a_couple`
holds both halves. Census re-run: 3 builds, 0 pairs, corners at 3,796 /
4,692 / 10,836 triangles; genome budget 10000 -> 12000.

## [1.9.0] - the convenience store's coffee island

New species `coffee_island`. The walker, 2026-09-28: "do the coffee counter
next", then four photos of a 1985 pour-over brewer and its carafes -- "a good
look for the carafe at least" -- and one of a later commercial three-warmer
model.

WHY A SPECIES. Deli Counter places the piece as a free-standing volume,
`coffee_island` 3.0 x 2.0 x 1.1 in five store specs and `coffee_food_island`
4.0 x 3.0 x 1.0 in `gas_station_a02` (the store club_block_014 stands) and
`fuel_stop_heist`. Its prop-species table routed both to `counter` by the
word `island`: the first built as a bare counter, the second -- deeper than
the counter genome's 2.0 m -- as the plain `prop` box, which is what cold run
9095 shipped. People walk round it, so both long faces are served. Deli
Counter 0.147.0 routes `coffee` here.

WHAT IS BUILT (`core/coffee_island_forms.py`, pure, tested without Blender):
a recessed kick, a wood body and a steel top that IS the slot; brewer pairs
back to back down the spine, the +Y one the -Y one turned half round so the
woodgrain column is on the viewer's right from either side; a steel burner
row along each long edge when the island is deep enough; cup towers and lid
stacks at +X, syrups with pumps, creamer and stirrers at -X; a round
double-sided FLAPPHAS COFFEE sign on a post over the middle, reading the
right way from both sides.

THE BREWER is the walker's 1985 photos: a stainless hood with two warmers on
it, two rocker switches each beside a red lamp, a plaque; a woodgrain column
down the right; a base plate with a warmer in the open bay under a hanging
funnel. The photos' plaque is a real maker's mark, so the plaque says DRIP
KING. The commercial model (black panel, red faucet, stepped three-warmer
deck) is not built; it is the obvious second form.

THE CARAFE is the photos' too: a squat glass bulb, a collar band in the lid
colour (orange decaf, black regular), a spout, a hooked handle, the coffee
inside. Its shape is a new `lathe` primitive here, a closed solid of
revolution from a (z, r) profile.

ONE CARAFE A BREWER. The first render filled every warmer -- 20 carafes on
a 3 m island -- and the walker: "we can have 20% as many carafes". Each
brewer now holds the one it is brewing, in its bay; the two on its hood and
the burner row stand empty, as one in the photo does. That is exactly a
fifth of the warmers on both of Deli Counter's sizes. Decaf is the odd
stations', so both lids are always there.

FIVE SUBMISSIONS WHATEVER THE SIZE, designed in rather than merged after
(1.8.0 was the lesson): every part belongs to one of four surface kinds
with its colour in the `Wear` vertex colour, the glass is one see-through
material, and the sign and every badge share one painted image. Held by
`test_bpy_five_submissions_five_materials`.

FOUND ON THE WAY, and fixed: `make_see_through_material` returns any
material already carrying its name, and `prim_mesh.build` had just made an
opaque one of the same name -- the carafes exported solid. The glass now
builds under a placeholder name and takes the see-through material after.

MEASURED: coincident-face census 3 builds, 0 pairs (3,796 / 4,132 / 9,156
triangles at the genome's corners; `CENSUS_BUILDS` 318 -> 321). Genome
count 80 -> 81 in `test_theme_style_resolution`.

NOT MEASURED YET: the look in a package, and whether the glass reads as
glass there. The preview renders it milky -- that is the flat fallback
material, and a themed build uses Pixelcoat's see-through glass pack.
Cold run 9096 is where it is walked.

## [1.8.0] - the service counter is six submissions, not fifteen

The walker, 2026-09-28: "do the atlas merge on the counter". 1.7.0 shipped
`counter` form `service` as 15 visual meshes over 14 materials, and cold run
9094 priced it at +13 draws where it is in view. Five of those materials
differed from another in nothing but colour -- the first thing CLAUDE.md's
draw-call rule forbids -- and four painted images could have been one.

    1.7.0   15 submissions, 14 materials   (9094's shipped counter)
    1.8.0    6 submissions,  6 materials   laminate, plastic, painted metal,
                                           one painted atlas, the rack's
                                           display, the rack's lit header

`tests/test_service_counter.py::test_bpy_six_materials_six_submissions_and_no_colour_only_twins`
holds it, and fails on 1.7.0's code (15 against 6).

ONE MATERIAL PER SURFACE KIND, THE COLOUR IN THE VERTEX. The recipe builds
one material per kind (`service_counter_forms.KIND_BASE`) and multiplies each
part's colour, divided by that base, into its `Wear` attribute
(`geometry.tint_wear`, new); `merge.pack_by_material` then packs every part
of a kind into one mesh. This is the path the pennant row's 1.1.0 note named
and did not take. Its price is the one that note gave: wear and tint share
COLOR_0 and cannot be separated again.

VERIFIED THAT THE COLOUR SURVIVES THE MOVE, by a headless Godot 4.7 readback
of both builds through `GLTFDocument` rather than assumed. Godot imports
COLOR_0 as the linear values written (file mean 0.4474, imported 0.4453 on
the merged plastic), flags it `vertex_color_is_srgb = false`, and the shader
reads it as linear; the material factor arrives as its sRGB spelling (linear
0.86 -> albedo 0.9357) and is converted back. So a register's beige lands on
the same albedo from either side, which is glTF's own
`factor * texture * COLOR_0`.

THE SAME READBACK CAUGHT TWO RESTYLES before they shipped. The first draft
made the kick base near black and the staff shelves a shade grey. 1.7.0's
kick was the SLOT's drywall skin at a wear mean of 0.73 -- light grey, and an
accident, but what shipped -- and its shelves were the body's white. Both are
matched (`BODY_TINT`); a merge is not a restyle. TWO LOOKS DID MOVE, on
purpose, and small: the two 16 mm rack posts are painted silver where they
were bare chrome (to share the rack's kind), and the checker squares are
50 mm where they were 45.

ONE PAINTED ATLAS for the trim and the three candy tiers
(`paint_atlas`, `atlas_v`): the bands stacked in one image one metre of art
wide, u repeating along the counter, each part's v mapped into its own band
inset half a pixel so a nearest sample on a band's edge never reads the next.
For both to repeat cleanly in one image the checker had to fit the metre a
whole number of times: `CHECK` 0.045 -> 0.05 (20 squares) and `CANDY_TEXEL`
350 -> 400 so a square is 20 whole pixels. The rack keeps its own image --
its display clamps and its header must stay a separate `_Face` material for
Lux's power cut.

NOT MEASURED YET in a package: the draw counts in view. Expected -9 at
`attacker_spawn_11` against 9094; cold run 9095 is where it is read.

## [1.7.0] - the convenience store's service counter: trim, candy, registers, lottery, the cigarette rack overhead

`counter` FORM ``service``. The walker, 2026-09-27: "start with the service
counter, cigarette overhead and candy rack", from the 1990s photograph of
the store's service island (docs/SET_DRESSING_REFERENCES.md, 2026-09-15):
white laminate, checkerboard trim top and bottom, the candy rack on the
customer face, beige registers, the cigarette rack behind.

A FORM, NOT A SPECIES. Deli Counter's `gas_station` preset already stands a
`register_counter` (6.0 x 0.9 x 1.1) that `intent` resolves to `counter` by
keyword and whose ``form`` `kit.honour_dressing` carries; `bar` (0.92.0) is
the precedent. Deli Counter 0.146.0 writes `"form": "service"` on it.

WHAT IS BUILT (`core/service_counter_forms.py`, pure Python, tested without
Blender):

  * TRIM: two bands on the customer face, painted with a tiling checker
    (`checker_canvas`, 64 px, two squares -- a 2 x 2 image would blur to
    grey under bilinear sampling), 6 mm proud so they read in profile.
  * THE CANDY RACK between the bands: three tiers, the lowest proudest, each
    a painted strip of wrapped bars (`core/candy_brands.py`, eleven invented
    Delco bars and gums, denylisted against the national AND the
    Philadelphia makers -- two names lasted one test run each: JAWN CHEWS
    is Goldenberg's word, DELCO CRUNCH is a national bar's). The strip's art
    is one metre wide and its UVs repeat it.
  * THE RACK STAYS INSIDE THE SLOT. First measured reaching 30 mm past the
    slot's front on Deli Counter's counter. A walk-into solid sits inside
    its collision and the module's collision is the counter's box, so the
    tiers reach no further than the top's overhang: 63 mm on a 0.9 m
    counter, a shallow rack under the lip.
  * REGISTERS at every station the recipe reserves, the bar's own; up to
    three LOTTERY dispensers beside each, red, on the customer edge.
  * THE CIGARETTE RACK OVERHEAD on two chrome posts from the service edge,
    2.4 m wide at most, three rows of packs faced to the CUSTOMER over the
    clerk's head (the pull-knob machine's own pack painter and brands),
    under a header lit at the machine's measured strength
    (``M_Counter_CigRack_<art>_Face``, Lux's power cut takes it). A post
    through a register measured as one coincident plane at 6.0 x 0.9; the
    rack now centres where its posts clear every station, shrinks in 0.1 m
    steps to find one, and on a counter too short for the narrowest rack
    to clear its till (0.8 m, a kiosk) is not built at all.
  * WHITE LAMINATE, whatever the slot said: a Deli Counter prop arrives as
    `wood` and would have built a brown counter with a checker band on it.

MEASURED: 216-396 triangles of fit-out across the genome's corners, 544 for
the whole module at Deli Counter's size; no two faces of the fit-out share a
plane; the budget (7,000) is unchanged.

TWO CONTRACT CHANGES, both small. `materials.make_painted_material` takes
``tile`` (REPEAT instead of clamped; the glTF exporter writes no sampler for
repeat because it is the format's default, which the first test got wrong
by looking for one). `kit.honour_dressing` honours a variant beside a FORM:
the service form draws its wrappers and packs from the variant, so
"variant without stock changes nothing but wear noise" is no longer true
when a form is asked, and Deli Counter's crc32 variant now gives two
counters two lineups.

NOT YET: the lottery towers are red blocks with no ticket face; the header
is a cigarette brand's ad rather than a store's; nothing is skinned by
Pixelcoat in the preview (flat style colours); and no cold run has carried
it -- that is the next thing.

## [1.6.0] - an anchor that already has a lamp does not get another

Lot 0.79.0 derives each site `streetlight` light anchor from the POLE
`site_furniture` stands, so pole and light are coincident by construction
instead of 24.93 m apart (the median measured on cold run 9087's walk copy;
0 of 54 lights had a pole within a metre). That makes
`FIXTURES["streetlight"]` a hazard rather than a service: given the same
manifest, a site-level fixture job would stand a second pole inside the
first.

The manifest now says so per anchor -- `"hardware": "slot:cover_12"` -- and
`plan` skips it with that reason recorded. It is a fact about ONE ANCHOR, not
a rule about a type: `HARDWARE_ELSEWHERE` already covers the type case, and a
`streetlight` anchor without the tag still gets its pole, which is what a
building's own anchors want.

`tests/test_streetlight_lens_drop.py` is new and is the other half of the
coupling: Lot places its light 0.175 m below the top of an exact-fit
streetlight module, which is where `recipes/streetlight.py` puts the emissive
lens (pole top at `h/2 - 0.18`, head filling the last 0.18, lens protruding
to `h/2 - 0.175`). It is a SOURCE check on those literals, not a measurement,
and it reads `../lot/lot.py` for the matching constant when the factory
workspace is around it -- so moving the lens fails here rather than silently
burying a site's street lighting inside 48 shoeboxes.

## [1.5.0] - the canopy's grid is built, and `size` stops meaning two things

COLD RUN 9081 EXPORTED A PACKAGE WITH NO CANOPY LIGHT IN IT, and said so
plainly in `zoo_fixtures_build.gas_station_a02`'s own report:

    {'id': 'canopy_roof_lights', 'type': 'canopy_lights',
     'reason': 'no fixture species for this type'}

Level Factory turned that into a validation finding with the count, the type
names and the owner -- `ZOO_CAPABILITY_GAP: 4 light anchor(s) of type
canopy_lights, canopy_wash ... owner=zoo`. NOTHING WAS SILENT. The finding was
raised and nobody read it, because a run prints "0 blockers, 58 findings" and a
new capability gap is one of the 58.

TWO PROBLEMS WORE ONE MESSAGE, and they needed opposite answers:

  * `canopy_lights` HAS had a species since 1.4.0 and was missing its
    `FIXTURES` row -- the defect the `pendant` row above it already records in
    its own comment, "every basement was silently dark".
  * `canopy_wash` has no hardware and never will. It is a light POSITION, the
    way `club_wash` is a pool, so "no fixture species for this type" was a
    truth about the table and a lie about the anchor. It joins
    `HARDWARE_ELSEWHERE` with a reason that says where its light actually
    comes from.

The canopy row carries `marker: False` for the reason the club rows do,
arrived at from the other end: a marker makes `LuxFixtureSpawner` put a LAMP at
the anchor, the grid holds 12 to 24 of them, and every one would reach the
forecourt ground mesh against a `max_lights_per_object` of 8.

`size` MEANT TWO THINGS AND ONLY ONE WAS WRITTEN DOWN. `plan` has copied an
anchor's `size` onto every placement since signs needed it, and the builder has
read it as width x HEIGHT -- correct, because every sized placement until now
was a sign panel. A canopy's size is a FOOTPRINT. Read as a height, a 13 m deck
clamps to the genome's 0.5 m and builds a fixture nobody meant. The row now
says which it is (`sized: True` -> `size_is_footprint` on the placement) and the
builder branches on that rather than on luck. Measured on the real manifest:
`gas_station_a02`'s deck arrives as [22.0, 13.0] and the species lays a 6 x 4
grid instead of its genome default.

FOUND BY WRITING THE TEST FIRST AND BEING WRONG. The new coverage test's first
assertion was that a non-canopy placement carries no `size` at all. It does,
and always has; the test failed, and the collision above is what the failure
was pointing at. The assertion now pins what the code actually does.

`tests/test_fixture_type_coverage.py` is the guard that would have saved the
run: every anchor type Deli Counter emits must be accounted for by a `FIXTURES`
row, a `DAYLIGHT` entry or a `HARDWARE_ELSEWHERE` entry. A fourth state, where
nobody chose, builds nothing and reads on screen as a dark room. It fails at
commit time rather than reporting at run time, and it skips rather than guesses
when there is no `deli_counter/build` beside the checkout.

## [1.4.0] - a fuel canopy gets its lights

MEASURED FIRST. Cold run 9080's package, read 2026-09-26: the forecourt canopy
is 22 x 13 m on six columns with three pump islands under it, and of the 20 Lux
fixture holders within 45 m every one sits on the SHOP between world x 58.7 and
81.3. The canopy spans 81 to 103. Nothing was over it -- Zoo had
`pendant_fixture`, `fluorescent_fixture`, `club_fixture` and `sign_box`, and no
species that goes on a canopy soffit. Lux lit what it was given; this was never
a Lux defect.

In every reference the walker supplied the canopy IS the light source for the
forecourt, and the tarmac is lit by it rather than by street lighting.

ONE PROP FOR THE WHOLE GRID, WHICH IS THE DESIGN AND NOT AN OPTIMISATION. A
fixture species placed once per anchor costs two draw calls per lamp, a lens
and a housing, so the authored 24 x 10 m deck would submit 42. `canopy_lights`
takes the deck's FOOTPRINT as its dimensions and lays every lamp inside one
pair of meshes: 21 lamps, 2 draw calls. That is this repo's own merge rule
applied to a thing whose parts are always seen together -- a soffit is looked
at as one surface or not at all.

    span 24.0 m -> 7 units, pitch 3.43 m    the authored canopy_roof size_x
    span 10.0 m -> 3 units, pitch 3.33 m    its size_y
    span 22.0 m -> 6 units                  the canopy measured on 9080
    span 13.0 m -> 4 units
    span  4.0 m -> 2 units                  the floor: never one lonely lamp

Pitch is derived from the span at one unit per 3.5 m, not chosen.

NO LIGHTS IN IT, AND THAT IS THE WALKER'S CALL. `max_lights_per_object` is 8 on
GL Compatibility and a literal 12-20 fixture grid would put every one of them
on the forecourt ground mesh -- the surface that fills the frame when a player
stands under it. The three options were put to the walker with their costs
stated; the answer was "emissive soffit and a few lights". So the lenses are
emissive geometry costing no light at all, and the real illumination will come
from a handful of wash anchors placed separately.

THE LENS IS 2 cm PROUD of the soffit plane. A lit face flush with the deck it
sits in is a coplanar pair by construction, and cold run 9080's package already
carries a `PRESENTATION_ZFIGHT` finding. There is a test pinning it.

COOL, NOT WARM: emissive (0.80, 0.95, 0.88). Every night reference reads
green-cyan, which is what metal halide and fluorescent look like on film. A
warm canopy would date the forecourt wrong as surely as a digital pump display.

CENSUS RUN, NOT ASSUMED. `blender -b --python tools/coplanar_census.py --
--species canopy_lights` on Blender 5.1.1 (b70da489d7f4): "3 builds, 0 with
coincident pairs, 0 that did not build", measuring 224 / 1176 / 3024 tris at
min / default / max. `CENSUS_BUILDS` moves 315 -> 318 on the strength of that
run rather than on arithmetic, which is what the constant's own comment demands.

THE BUDGET CAME FROM THE CENSUS, and the first guess was wrong. `tris_lod0` was
authored at 900 from an estimate of 504 -- 42 boxes at 12 triangles -- and the
census measured 1176 at the default because `bm_to_object` bevels. Set to 1300:
a regression detector at the authored size with headroom, NOT a cap, because
this species' triangle count scales with the deck it covers. A max-size deck
exceeds it and that is the species working.

Registered in `genome/minted.json`, and its material options are `metal|plastic`
to match `fluorescent_fixture` -- the sibling species, the same object outdoors
-- rather than offering a split metal kind the recipe never uses.

## [1.3.0] - the wet variant gets a chooser

Pixelcoat has written `wet_albedo`, `wet_roughness` and `wetness` into every
ground pack since 0.47.0 and nothing has read them: `MAP_KEYS` is a fixed
allow-list and the wet names are not in it. `--wet` is the chooser.

WHERE THE CHOICE IS MADE, and it is the smallest place that works. At
RESOLUTION time: `load_pack(dir, wet=True)` returns a pack whose `albedo` and
`roughness` POINT AT the wet files. `bpylayer/materials.py` is untouched --
the tint path, the see-through path, the UV scaling and the normal wiring all
carry on reading `maps["albedo"]` and `maps["roughness"]`, and the exporter
bakes the wet textures into the GLB exactly as it bakes the dry ones.

THAT IS WHAT KEEPS THE DRAW-CALL PROMISE. Level Factory 0.110.0 measured a wet
`next_pass` at 2.27-4.29 us per ADDED draw call, +8.05 ms at the worst station
of a real package, because a second pass re-rasterises the same triangles. A
variant swaps which image a material samples: the resolved MAP COUNT is
unchanged, so no extra texture slot, no extra material, no extra submission.
A test asserts the count; the measured half -- a rebuilt package whose draw
calls read the same as dry -- needs Level Factory to turn this on and is not
in this release.

A PACK WITH NO WET MAPS IS UNAFFECTED, asked or not, and that is what makes a
whole-build flag safe. Walls, glass and interiors carry none, so `--wet`
dresses the ground and leaves the rest alone without anybody listing which is
which. Which surfaces are wet is the grammar's decision and restating it here
would be a second place to get it wrong.

THE MATERIAL NAME CARRIES THE VARIANT, and it has to. `make_material` caches
on `M_Skin_<kind>_<theme>`, so without a suffix a wet and a dry build in one
process would collide and the second would silently get the first's material.
The name also travels into the GLB, where Level Factory's greybox-skin gate
reads it. Wet materials are `M_Skin_<kind>_<theme>_wet`, and only a pack that
actually substituted something is renamed -- a wet build does not rename every
wall it left dry.

A wet map NAMED in a manifest but absent from disk is not substituted; the dry
map stands. Same rule the dry maps already follow, same reason.

`tests/test_wet_chooser.py`, 11 tests, all 11 failing against the unfixed
resolver. Suite 2,513 passing.

## [1.2.0] - a pack texture is one file, not sixty copies

Cold run 9066's shipped package carries **961 embedded images across 215 GLBs,
25.69 MiB of payload of which 1.41 MiB is unique** -- 58 distinct pictures, so
94.5% of it is a copy. One wood texture is embedded 77 times over 60 files.
That was known. What nobody had measured is what it costs once the engine has
it, and the answer is the whole reason this release exists.

### Godot does not deduplicate. Twenty GLBs, one control, one floor

Godot 4.7, GL Compatibility, twenty single-quad GLBs each carrying one 512x512
RGBA image, counted by distinct texture RID in the loaded scene tree and by
`RENDERING_INFO_TEXTURE_MEM_USED` against an empty-scene baseline:

    twenty GLBs, IDENTICAL embedded bytes    20 textures   27,962,000 B
    twenty GLBs, DIFFERENT embedded bytes    20 textures   27,962,000 B
    twenty GLBs -> one external PNG           1 texture     1,398,100 B
    one GLB instanced twenty times            1 texture     1,398,100 B

The first two rows are the finding: byte-identical and distinct payloads cost
**exactly the same**, to the byte. The second row is the control and it is
what makes the first row mean anything -- an instrument that reported 20 for
both without it could simply have been counting nodes. So a texture embedded
sixty times is sixty textures resident, uncompressed, on somebody else's
machine, every frame.

### What changed

`core/gltf_textures` rewrites a GLB's embedded images to `images[].uri`
references and writes the pixels to `_tex/` beside the file, named
`<image>_<sha1[:8]>.png`. `bpylayer.export.export_glb` runs it on every module
it writes (`share_textures=True`, a keyword so the two states stay measurable
against each other from one build, exactly as `merge_parts` is). Blender's GLB
writer embeds unconditionally and offers no setting for this, so it is a pass
over the file it just wrote.

The bytes are **copied, not re-encoded**: the PNG beside the GLB is the PNG
that was inside it. Nothing resizes, recompresses or reformats, which is what
lets the look argument below be about the importer and not about this module.

STANDALONE IS PRESERVED, which is the rule that decided the shape. A GLB plus
a relative texture folder is ordinary glTF 2.0 -- Blender, Godot and three.js
all open it with none of these tools present. A Zoo-supplied import script
would not have been, and was not considered for long.

### Measured on the real package, not only on the controls

Cold run 9066's `LF_club_block_005.portable-godot`, every GLB externalised,
loaded in Godot 4.7 on GL Compatibility and counted the same way:

    distinct texture resources      1,841  ->    157     -91.5%
    texture memory            332,867,236  ->  47,090,266 B    -85.9%
    video memory              348,897,688  ->  63,120,718 B    -81.9%
    scene load                   2,383.8   ->  1,592-1,856 ms  -22% to -33%
    package on disk                45.43   ->    23.45 MiB     -48.4%
    import cache                   89.28   ->    38.37 MiB     -57.0%

Load is given as a range because it is the one figure here that moved between
runs of the same build; texture memory did not move at all, reading
47,090,266 B on two separate imports, so it is quoted exactly.

961 embedded images became 145 files in 7 folders -- one per directory the
GLBs sit in, because a relative URI cannot reach across the package. Hoisting
those 145 to the 58 distinct pictures is a further 4-ish MiB and it belongs to
whoever lays the package out, not here.

Draw calls did not change and are not claimed to: this moves where texels
live, not how many submissions are made.

### The look did not move, and it took two instruments to say so

The frame comparison alone could not answer it. Six stations chosen by the
scene graph (51%-100% non-black, so not the 99.7%-black frames that once
reported "pixel-identical" in this repo), and the SAME build rendered twice
already differs in 87.110% of pixels at mean |delta| 3.5529 -- something in
the presentation layer is animated. Against that floor:

    before vs before (noise floor)          87.110%   mean 3.5529
    before vs after (this change)           87.142%   mean 3.5560
    before vs VRAM-compressed (control)     87.874%   mean 4.2646

The control moves the mean by +0.71 and this change by +0.003, so the change
sits in the noise of a build compared with itself while the instrument is
demonstrably able to register one. That is suggestive and it is not proof, so
the question was asked again of the texels themselves -- the decoded level-0
RGBA8 of the same source through each import path:

    embedded, gltf/embedded_image_handling=3     0.000% differ, max delta 0
    external PNG, lossless + fix_alpha_border    0.000% differ, max delta 0
    external PNG, VRAM compressed (control)    100.000% differ, max delta 255

Byte-identical, with a control that shouts. Two instruments, one answer.

### The two engine defaults that would have changed it quietly

A PNG beside a GLB is imported by Godot's *texture* importer, whose defaults
are not the GLTF importer's. Both of these were found by measuring rather than
by reading, and either one alone breaks the guarantee above:

  * `compress/mode` defaults to **2, VRAM compressed** -- 100% of pixels
    differ. Same call as `gltf/embedded_image_handling=3`: roadmap 89 is a
    compression setting silently changing a shipped build's look.
  * `process/fix_alpha_border` defaults to **true** and rewrites RGB under
    transparent texels -- **7.755% of pixels differ, max channel delta 255**,
    which is not a rounding artefact. With it off, 0.000%.

Pinning them is Level Factory's job because the sidecars are written at export;
see its 0.99.0. **Zoo's output alone is not sufficient** -- a consumer who
imports these GLBs with engine defaults gets VRAM-compressed textures with
altered alpha borders, and that is a real gap in this release rather than a
detail. It is the price of the standalone rule: a module cannot ship import
settings without shipping tooling.

### What VRAM compression would have bought, since it was measured anyway

On the same package: texture memory 47,090,266 -> 21,504,802 B, video memory
65,250,910 -> 37,535,254 B, load 1,856 -> 1,440 ms. A further 25.6 MiB and 400
ms, for a texture that is no longer the one Pixelcoat drew. Not taken, per the
standing call on roadmap 89, and recorded here so the next person can reopen
it with numbers instead of starting over.

### Mipmaps, and a claim this release found to be wrong

It has been said in this repo that a shipped package has no mip chain. On cold
run 9066's package it is **false**: `zoo_worldskin.gd`'s import-time pass
already builds one, and 1,402 of 1,841 textures carry mips as shipped. The 439
that do not are the slots that pass does not visit -- emission, metallic, ORM.
After this change 145 of 157 do, from the importer, and the 12 that do not are
Level Factory's own textures, untouched before and after.

That pass is also why the mip setting is not optional downstream: it rebuilds
each texture as its own `ImageTexture`, which would undo the sharing. With the
chain already present it is a no-op and the textures stay shared -- measured,
every texture in the after package is a `CompressedTexture2D`, none rebuilt.

Mips are **free** in resident memory on this renderer, which was not expected:
a 512x512 RGBA8 texture reads 1,398,100 B with a mip chain and 1,398,100 B
without -- exactly 4/3 of its base size either way, so the chain is allocated
whether or not it is filled. Turning mips on costs nothing and leaving them
off wastes the allocation.

## [1.1.1] - the pennant row cannot be a MultiMesh, and the engine is why

1.1.0 left a choice open under its own merge result: the pennant row is
"colour variation wearing materials", and "a MultiMesh would also reach 2
draw calls for the whole row with per-instance colour, which is Lot's
dressing pattern one shelf along. Left for the walker to choose rather than
decided here." It was chosen. It does not work, and nothing in this repo had
measured the thing that stops it.

**Godot 4.7 does not implement `EXT_mesh_gpu_instancing`** -- the only way a
.glb can express instancing -- and it discards it without a word. The
instancing node keeps its mesh and loses its instance table, so every
instance after the first stops existing. Three instances of one triangle,
exported by Blender 5.1.1 with `export_gpu_instances=True`:

    the GLB      extensionsUsed ['EXT_mesh_gpu_instancing'], one node
                 "Row", 3 instances, TRANSLATION/ROTATION/SCALE
    runtime      GLTFDocument.append_from_file -> MeshInstance3D,
                 1 surface, 3 verts, 1 triangle
    editor       load("res://probe.glb") -> the same, 3 verts
    the binary   the string "EXT_mesh_gpu_instancing" does not occur in
                 the engine executable at all

Three instruments, one answer. On a 44-pennant row that would be **43
pennants deleted** from a file that still validates, still censuses at 892
triangles and 11 materials, and still opens -- because the loss happens on
import, downstream of every gate Zoo owns.

### SO THE ROW SHIPS EXACTLY AS 1.1.0 SHIPPED IT

`pennant_row_14809a.glb` at w400 builds **byte-for-byte identical** to the
1.1.0 build, 100,064 bytes: 11 mesh nodes, 11 materials, 11 submissions,
892 triangles. No geometry moved, no collider changed, no pixel differs,
because nothing was built. Draw calls per row before and after: **11 and
11.** There is no frame measurement here and there should not be one -- a
change that writes the same bytes cannot move a frame, and a station sweep
reporting "below the noise floor" would be dressing a zero up as a result.

### TWO CORRECTIONS THE ATTEMPT TURNED UP

  * **It would have been 3 draw calls, not 2.** A pennant wears TWO team
    colours -- `colours[i]` is a (primary, secondary) pair, the felt takes
    the first and the hoist band the second -- so per-instance colour buys
    one MultiMesh per colour ROLE, not one per row: batten + felt + band.
    Reaching 2 needs the band's colour in `INSTANCE_CUSTOM` and a shader to
    choose between them, which is a custom material on a prop that has
    none, on the renderer packages ship.
  * **The capability is not Zoo's to grow.** A MultiMesh reaches Godot in
    this factory as .tscn TEXT, written by
    `level_factory/packages/exporting/dressing_scene.py` as a
    `[sub_resource type="MultiMesh"]` block with a `PackedFloat32Array`
    buffer, over meshes `level_factory/assets/godot/extract_meshes.gd`
    pulls out of Zoo's GLBs into `.res`. That is where Lot's 4,107
    instances in 4 draw calls actually live. Zoo's half would be to emit
    ONE pennant worth instancing; the instancing is the composer's. Per
    `USING_THE_FACTORY.md`'s gap protocol that makes instanced pennants a
    Level Factory capability. Note that path writes `transform_format`,
    `instance_count` and `buffer` and has **no `use_colors`**, so
    per-instance colour does not exist there yet either -- the row needs
    both halves built, not one.

### THE INSTRUMENT, AND WHY IT HAS A POSITIVE CONTROL

`tools/instancing_probe.py` builds the N-instance file and censuses any
GLB; `tools/instancing_probe.gd` loads one both ways Godot can and prints
the tree it got. They are kept because the question will be asked again the
next time somebody reads the MultiMesh rule.

The census counts submissions per (node, primitive) and not per mesh, which
is the trap the whole question sits on: three nodes sharing one mesh are
three draw calls, and a census counting `meshes` would report 1 and read
like instancing had worked on a file carrying none.

Two controls, because an instrument that can only report absence cannot
tell "Zoo does not emit this" from "the probe cannot see it":

  * the same probe on the same Blender DOES report instancing when it is
    there -- `claims_instancing True`, 3 instances, TRANSLATION/ROTATION/
    SCALE;
  * the same .gd on a hand-written `.tscn` carrying a real MultiMesh reads
    `MULTIMESH instances=3 use_colors=true`, so its `MeshInstance3D verts=3`
    on the instanced GLB is a reading and not a blind spot.

And one control on the control: with the flag set but the instances left as
scene-root SIBLINGS rather than children of one parent, Blender writes no
extension at all -- 3 ordinary nodes, 3 submissions. Blender emits the
extension only for objects sharing a parent, and writes it onto that parent.
So "I turned instancing on" is not evidence that a file has it.

### Tests

`tests/test_gpu_instancing.py`, 6 of them: the census arithmetic, the
extension reported when present and not invented when absent, both controls
above, and the rule on the built article -- **no GLB Zoo exports may claim
`EXT_mesh_gpu_instancing`**, asked of `pennant_row`, the module that would
have carried it. It is a data-loss switch on this engine, and the loss is
invisible to every instrument that reads the GLB rather than the scene
Godot made of it.

Suite under Blender 5.1.1: **2,739 passed, 40 skipped, 1 xfailed** (1.1.0:
2,733 / 40 / 1, plus these 6). Plain Python beside the sibling repos: 2,488
passed, 285 skipped, 1 xfailed unchanged at 1.1.0, and 3 of the 6 run
there.

## [1.1.0] - one mesh per material per module, and the draw calls that buys

Zoo shipped every part of every prop as its own object, so a prop reached
Godot as one `MeshInstance3D` per part and cost one draw call per part. The
pack wall is the extreme of it: **118 meshes for 4 materials and 1,592
triangles**, which is 13.5 triangles per submission. Across
`card_shop_a01`'s 90 module GLBs on cold run 9062, 1,602 visual meshes
carried 274 distinct materials between them.

That is what the frame was paying for, and the evidence is that frame cost
tracked DRAW CALLS and not geometry. Walking the camera on that package:
1,730 calls -> 9.49 ms, 2,482 -> 8.69 ms, 6,376 -> 25.59 ms, 6,065 -> 27.48
ms, while primitives stayed near 1.4M throughout and render-CPU ran about
twice GPU. A second lap over the same ground was no faster, so it was not
shader compilation either.

`bpylayer/merge.py` packs a module's visual parts into one mesh per material
at export time. `core/partnames.py` owns the decisions, in pure Python, so
they can be tested without Blender.

### THE CHUNK IS THE MODULE, AND NO LARGER

Every part of one pack wall enters and leaves view together, so merging
inside a module costs no culling granularity. Merging ACROSS modules would
cost exactly that, and is deliberately not done -- `build_dressing`,
`build_roof_props` and `build_fixtures` pass `merge_parts=False` and each
carries the line saying why: those collections are a whole BUILDING's covers,
each already transformed to its own anchor, and packing them by material
would weld geometry from opposite faces of the building into one bounding box
that is never off-screen.

The cost of the granularity that IS given up was measured rather than waved
at. Primitives submitted per frame, six fixed stations, before -> after:
50,180 -> 49,782; 273,828 -> 273,330; 221,468 -> 222,300; 251,218 ->
252,046; 33,186 -> 33,238; 86,576 -> 88,130. **The worst is +1.8%**, at the
station standing closest to a wall, and three of the six went down.

### What it did, on `card_shop_a01`'s 90 modules

    visual mesh nodes    1,602  ->  274      5.85x
    all glTF nodes       1,682  ->  354
    collision nodes         62  ->   62      untouched, by name
    visual triangles    30,130  -> 30,130    asserted, not assumed
    collision triangles  1,224  ->  1,224

    prop_pack_wall   ..._w240_d50_h255_n2    117 ->  4   4 materials  1,580 tris
    prop_pennant_row ..._w400_d8_h30_n3       89 -> 13  13 materials    892 tris
    prop_display_case..._w240_d60_h100_n2     84 ->  6   6 materials  1,108 tris
    prop_filing_cabinet..._w90_d60_h105       18 ->  1   1 material     792 tris

### The frame, at six fixed stations

1280x720, GL Compatibility, vsync off, 300 frames after 120 discarded, on the
composed package with the other two buildings standing. The stations are
derived from the card shop's own world AABB and the box was printed on every
run -- `pos=-72.175003,-0.250000,-14.345000 size=20.350002,8.000000,18.729599`
to six decimals on all of them, so the camera provably stood in the same
place rather than assumedly.

    station        draw calls        mean frame        change
    exterior_ne    2,574 ->   874    6.85 -> 2.51 ms   -63%
    exterior_sw    7,154 -> 5,454   22.06 -> 17.53 ms  -21%
    interior_c     5,253 -> 4,635   16.19 -> 14.28 ms  -12%
    interior_x     6,014 -> 4,970   18.67 -> 15.52 ms  -17%
    interior_z     1,791 ->   572    4.28 -> 1.76 ms   -59%
    wall_close     1,177 ->   932    3.18 -> 2.63 ms   -17%

Each figure is the mean of two independent runs whose spread was under 3.7%.
The first version of the probe reported 6.067 ms at four of six stations;
1000/6.067 is 164.8, which is the display's refresh rate and not the scene's
cost, and it hid the entire result at every cheap station. The numbers above
are with vsync disabled.

### THE PICTURE MOVES, BY THIS MUCH, AND HERE IS THE NOISE FLOOR IT MOVES IN

It does move, and the honest thing is the figure. Same package, same
stations, same lighting rig, only the module GLBs swapped -- pixels changed
by more than 8/255:

    station       merge    1 mm of camera, before    1 mm of camera, after
    exterior_ne   0.004%   3.767%                    3.768%
    exterior_sw   0.008%   3.659%                    3.660%
    interior_c    0.021%   4.757%                    4.725%
    interior_x    0.555%   3.740%                    3.717%
    interior_z    0.517%   8.572%                    8.606%
    wall_close    0.015%   6.481%                    6.499%

Rendering the same build twice changes **0.000%**, so the renderer is
deterministic and the middle column is not noise in the instrument -- it is
the picture's own sensitivity to a movement nobody can make on purpose.
The merge's difference is between a seventh and a nine-hundredth of it, and
at the two stations where it changes pixels in the thousands rather than the
dozens, 87% and 77% of them are inside the set a millimetre already flips.
The jitter figure itself is unchanged before and after, to three decimals,
so **the merge neither creates nor removes z-fighting**.

What the difference IS: the wood-panelled wall's texture slides by about one
texel. The textures filter GL_NEAREST, the surfaces are world-projected, and
`zoo_worldskin._uv_density` decides the projection scale by measuring ONE
surface and keeping the first it meets -- so a module whose parts were
re-packed hands it a different surface to measure. On kit modules the scale
moves by at most 0.011%; at 72 m from the world origin that is still most of
a texel, and with nearest filtering most of a texel is a whole one.

The estimator was already unstable before any of this: on `card_shop_a01`,
12 of 132 materials that appear on more than one surface in a module get
readings that disagree with each other by more than 1%, the widest being the
display case's art plate at 1.5974 against 1.7455. Which of them is installed
is decided by traversal order. That is a `level_factory` defect, not a Zoo
one, and it is reported rather than patched here -- but it was CONFIRMED
rather than argued: swapping `_uv_density` for a density accumulated over
every triangle carrying the material, which is invariant to how triangles are
split across surfaces, halves the merge's pixel difference (`interior_z`
0.517% -> 0.261%, `exterior_sw` 0.008% -> 0.000%). The other half is ordinary
resampling in pixels that are already unstable.

A refuted lead is kept because it cost a cycle: Godot's per-mesh LOD
generation looked like the obvious culprit, since a 1,580-triangle merged
mesh gets a decimation chain where 117 tiny ones get nothing. Turning
`meshes/generate_lods` off in all 90 sidecars and re-importing changed the
figures by less than 0.005 points. It is not LOD.

### What is never merged, each because something downstream reads a name

  * a COLLIDER -- Godot's importer has no collision field and decides from
    the node-name suffix, and `lot/site_collision.py`, `lot/site_ground.py`,
    `level_factory/packages/validation/glb_collision.py`, `patina/patina/
    mesh.py` and Deli Counter's `nav_gate.gd` each re-implement that test.
    62 collision nodes in, 62 out, name for name, 1,224 triangles either way;
  * a `Stock_*` part, which `deli_counter/portable_building.py` filters out
    of a module's measured extent -- its own comment records three 0.75 m
    desks reading 1.12 m when the stock was left in;
  * a `_LOD` alternate, which stands in for a part rather than beside it and
    merged into the base would draw twice;
  * parts whose UV or colour LAYERS differ, because a part with no `Wear`
    colours folded into one that has them is written black, not white;
  * anything carrying a transform, or a colour attribute on a domain this
    does not know how to copy. Those are REFUSED and reported, not merged
    and quietly flattened.

Markers are empties and so were never in the mesh pool -- `ATT_tray` and the
`LuxEmit_*` fixtures ride out in the export set as the same objects, with
their glTF `extras` intact.

Emissive parts stay separate for free, which is the argument for keying on
the material rather than on anything else: the vending machine's lit
`_Face` and `_Lens` are their own materials, so they are their own meshes,
and Lux still cuts them with the building's power.

### A GROUP OF ONE IS NOT A MERGE

A part that is the only one carrying its material is exported AS ITSELF. One
surface in, one surface out -- re-packing it removes no draw call, and it
would cost the part the name `portable_building`, patina and
`tools/glb_nodes.py` read it by.

This was not foresight. The first version copied every group into a new mesh,
and `wall_pack` at the `min` genome corner fell over: it names a part
`WallPack_Lens` and paints it `M_WallPack_Lens`, so the merged name built
from family plus material slug WAS the part's own name, and because this pass
is non-destructive the part was still there. Blender resolved it by appending
`.001`, which would have gone into the glTF node name and made the export
non-reproducible. The guard that catches a Blender rename refused to build
the module rather than ship the `.001`, and four `test_coincident_faces`
species failed with it -- which is the guard doing its job and is why it is
there. `group_parts` now also takes the names already spoken for.

### Determinism, and the control

Sorted merge order throughout, never hash or link order: the plan is built
from `sorted(buckets)` and every group's sources are sorted by name. Two
independent 90-module builds came back **90 of 90 byte-identical**, and
shuffling the input to `group_parts` eight ways leaves the plan unmoved.

`--no-merge-parts` keeps the pre-1.1.0 packing. It is the measurement
control, not a shipping mode: every figure above is an A/B whose only
difference is that flag, same seed, same skins, same commit.

### Non-destructive, and what that buys

The merged objects live in a throwaway collection torn down before
`export_glb` returns. `gather_facts` still runs first and measures the parts
a recipe built -- its `fit_names` and `dressing` filters match literal part
names, so a merge that ran before it would have silently widened every
module's measured dimensions. `save_blend` still writes the parts, and every
recipe test that asserts on object names still sees them. `tris`, `parts`,
`materials`, `dimensions`, `center` and `has_collision` are asserted equal
with the flag on and off.

One consequence is worth saying out loud because an instrument depends on it:
`tools/check_coplanar.py` finds z-fighting by looking for coplanar
overlapping faces drawn from DIFFERENT mesh nodes and skips a plane group
that comes from one node, so parts merged into one mesh stop being visible to
it. The geometry is unchanged -- nothing here creates or removes a coincident
pair -- but that gate goes quiet about intra-module pairs. Zoo's own
`tools/coplanar_probe.py` compares every triangle against every other
regardless of which object it came from and runs on the Blender objects
before this, so the coverage still exists upstream.

### Still on the table: the pennant row is colour variation wearing materials

89 meshes, 892 triangles, and **13 materials that differ in nothing but
`baseColorFactor`** -- same texture, same everything else. It is 1 batten
plus 44 felts at 12 triangles and 44 bands at 8.

Merging alone takes it 89 -> 11..13, one mesh per colour, and that is what
ships here. Moving the tint into the `Wear` colour attribute the parts
already carry would collapse all 13 materials into one and take it **89 ->
1**; `zoo_worldskin._vertex_colour_albedo` already draws `COLOR_0` as albedo
on non-kit GLBs, so the machinery exists. The price is that wear and tint
then share one channel and cannot be separated again, and that the "all-white
is left off" rule in that pass stops firing for pennants. A MultiMesh would
also reach 2 draw calls for the whole row with per-instance colour, which is
Lot's dressing pattern one shelf along. Left for the walker to choose rather
than decided here.

### Tests

`tests/test_merge_by_material.py`, 30 of them, every rule above with the
reason in the docstring. The pure half runs anywhere; the built half asserts
on real geometry -- collider names on the export set, the marker empty and
its `extras`, one material per merged object, the triangle total, the
singleton keeping its own name, and `gather_facts` unmoved.

Suite under Blender 5.1.1: **2,733 passed, 40 skipped, 1 xfailed**. 1.0.0
run in the same harness for the control: 2,704, 39, 1 -- so the delta is
exactly 30, the new file, and not one test anywhere else moving.

## [1.0.0] - the card shop's register is a register now, and its display is lit

The walker photographed `card_shop_a01`'s counter on cold run 9062 and what
stands on it is "a brown box with a white post and a smaller box on top -- it
reads as a mistake, not a register". ATTRIBUTED BEFORE ANYTHING MOVED, because
the brief that arrived with the frame said the register comes from
`_surface_stock` and it does not: `_surface_stock` has no register in any of
its seven flavours, and neither does the `cards` flavour the card shop's play
tables use. What draws it is `display_case_forms._register`, inside the
showcase counter species itself, and it is exactly four boxes:

    DisplayCase_Till       0.34 x 0.36 x 0.15   BODY   the slot's own material
    DisplayCase_TillKeys   0.26 x 0.12 x 0.012  STOCK  (0.55, 0.52, 0.47) paper
    DisplayCase_TillStem   0.035 sq x 0.18      METAL  mill aluminium
    DisplayCase_TillHead   0.16 x 0.05 x 0.08   BODY   the slot's own material

48 triangles, no artwork, nothing lit. In a wood-panelled shop BODY is the
wood, so the box and the head are brown and the stem is a white post. The
walker's sentence is a correct reading of what the tool built.

A second thing was wrong the same way and is worth recording: there is another
register inside `counter.py`'s `bar` form, three more boxes in
`back_bar_forms.counter_fitout`. That one is the club's and is untouched here.

### `cash_register`, and it stands on its own slot

`core/register_forms.py` (the whole shape, pure), `recipes/cash_register.py`
(the build), `genome/species/cash_register.json`,
`tests/test_cash_register.py`. 0.40 x 0.42 x 0.46 m by default, 0.32-0.52 x
0.34-0.52 x 0.38-0.56 over the genome. From the walker's photograph: a squat
moulded body on a DEEPER cash drawer with a full-width pull bar and a round
lock barrel, a raised CUSTOMER display on a short post, a reflective operator
panel tipped toward the clerk, a receipt printer with a curl of paper in it,
and a keypad in a raised well.

The top face is three lanes, and that is the one structural decision:

    -Y  [ pole lane ][ keypad (operator's right) | printer / panel ]  +Y

-Y is the CUSTOMER side, so the operator stands at +Y and THEIR right hand
points toward -X. The reference photograph was taken from the operator's side
-- it shows the keypad and the drawer's pull -- so its "keypad on the right,
printer on the left" is that frame, and the lanes are laid out in it.

### The budget was set before the layout was drawn: 200 triangles

For scale, in the package this ships into: `crt_tv` bracket form 168,
`poster` framed 78, `vending_machine` 464. It builds **134**, and it builds
134 at every one of the 27 genome corners and for every price in the table --
one number, because every part is a box or a fixed-segment cylinder and no
style asks for a bevel.

    Register_Drawer   12   Register_Pull    12   Register_Lock    20 (6-gon)
    Register_Body     12   Register_Keypad  12   Register_Keys     2 (art)
    Register_Printer  12   Register_Paper   12   Register_OpBezel 12
    Register_OpLcd     2 (art)              Register_Stem        12
    Register_Bezel    12   Register_Screen   2 (art)        total 134

The keypad is the line item that decided it. Twenty modelled keys are 240
triangles on their own, more than the whole rest of the register, so the keys
are PAINTED into the atlas on one quad and the raised well around them is real
geometry. That is `card_art`'s own call one shelf along -- "a figure is a blob
and a rules box is a run of dashes, because at this size that is what a figure
and a rules box ARE". What the modelled version would buy is a key's own
shadow at arm's length, which is nearer than any player stands to a shop
counter; reopen it the day somebody is meant to use one.

### The green display, which is the point

"Cash registers in the 90s had this green font on a black screen." The
customer display is the artwork's own light: ONE image, two materials --
`M_Register_<art>_Face` is backlit (the pole screen) and
`M_Register_<art>_Panel` is painted (the operator's LCD and the keypad). The
`_Face` suffix is what Lux's emissive binder cuts with the building's power,
and `params.lit` 0 is a register with its plug pulled, the switch
`vending_machine` has carried since 0.87.0.

IT IS A MATERIAL AND NOT A LAMP. Compatibility allows `max_lights_per_object`
8 and this package already ships 84 lights, so nothing in the recipe makes a
Light3D and a test reads the recipe's source to say so.

THE TYPE IS THE FACTORY'S OWN FACE. `pixel_type` -- Pixelcoat's Pixel Operator
Bold at 16 px -- which is what `card_art`'s letterer sets every card-shop sign
in and what `vending_forms.paint_display` already sets a LIT PRICE READOUT in.
The other face in this repo, `neon_forms.FONT_5X7`, is not a raster where it
is used: `glyph_runs` turns a glyph into the skeleton of a bent glass tube and
the recipe builds rods from it. A fourth table of glyphs -- a true
seven-segment set -- was not minted, and what it would have bought is the
slanted, broken-stroke silhouette of a real VFD. Said rather than narrowed
quietly; reopen it the day a second species wants segment digits.

The digits set at the largest whole scale the window fits, and holding that at
2 across the whole genome was a measurement rather than a preference:
`POLE_BEZEL_F` was 0.46, which gave the SHORTEST slot a 28 px window against
the 26 px a scale-2 line needs plus 2 px of margin each side. One pixel short,
and the display halved its digits for it. At 0.55 the slack is 3 px at every
width, and a test holds the scale at all 27 corners. The result is 35.2 mm of
green at the default slot and 52.7 mm at the tallest.

WHAT IT READS AT, measured in `tools/preview_specimen.py` frames at customer
eye height over a 1.0 m counter, 960 x 640, style 4 delco_1997: crisp at 1.2 m
and 2.5 m, clearly legible at 4 m, still readable as a price at 6 m -- which
is longer than any card shop this library builds.

### The glow was A/B-ed, and the rule that picked the other two did not decide it

Four builds of the same register, 1.6 m straight on, Cycles CPU 40 samples,
world 0.55. Screen pixels are the green-dominant ones; "pinned" is any channel
>= 250, "white" all >= 235; saturation is (max - min) / max.

    strength        0.6     1.0     1.5     2.5
    luma          145.1   159.3   172.8   180.8
    saturation    0.479   0.411   0.357   0.311
    pinned %          0       0       0       0
    white %           0       0       0       0

NOTHING PINS AT ANY OF THEM, so "the highest strength with no pinned and no
white pixel" -- the rule `vending_forms` and `crt_forms` each chose by -- does
not decide this one, and taken literally here it picks 2.5. What moves is
SATURATION: the artwork's own is 0.77 and the screen has lost a third of it by
1.5. The walker's word was "bright green". 1.0 keeps 0.41 at 159 luma; the
extra 8 % of luma at 1.5 costs 13 % of the green.

WHAT IS NOT MEASURED, said rather than implied: this is Cycles under a sun,
not `gl_compatibility` under Heavy Rain and delco_summer_afternoon with Lux
post, which is what the other two lit species carry and the only measurement
that describes a client. Re-run it there before moving the number.

### The texture, which is the whole cost

ONE image per register, stacked rather than packed side by side: the screen is
wide and short and the keypad tall and narrow, and beside each other they
leave 84 x 133 px of filler -- 91 KiB decoded against 37. At the default slot
the atlas is **84 x 151 px, 37.2 KiB** decoded RGB8 (0.5 KiB as PNG); at the
widest corner 112 x 195, 65.5 KiB. For scale, the card shop's flat art is
2.392 MiB across 18 images.

The screens are drawn at `vending_forms.LABEL_TEXEL` (512 px/m) because a
GLYPH needs it -- `pixel_type`'s line is 13 px tall whatever the metres are.
The keypad is drawn at `card_art.TEXEL` (256, the factory's 4 mm pixel)
because a key face is a rectangle: 44 x 64 px instead of 88 x 128, which is
24 KiB of the atlas. And the keypad's per-key shade is keyed on the GRID and
not on the module's stem, so two counters in one shop share one image instead
of paying another 37 KiB for a 3 % grey nobody can see.

### Exact, and no two faces in a plane

Exact on every axis at every corner with no scaling: the drawer is the full
width and reaches the back plane, the pull bar's face IS the front plane, the
drawer's underside IS the bottom and the bezel's top IS the top. Extents land
on the slot to 0.0, not to a tolerance.

`tools/coplanar_census.py` on `cash_register` and `display_case`, min /
default / max: **0 pairs, 6 of 6 builds**. Three real ones were found and
fixed on the way, and each was an overlap rather than a tolerance:

  * the keypad island ran the full depth of the top and shared its base plane
    with the pole stem -- 5.7 cm2, measured, which is what `POLE_LANE` exists
    for;
  * the keypad's side plane sat 1.6 mm from the operator bezel's;
  * the receipt was modelled at the 1.6 mm a receipt is, so its own two faces
    were inside the 2 mm window. It is 4 mm now: a solid thinner than the
    probe's window cannot exist here, and that is the probe's number rather
    than a stationer's.

### Two things only a frame could have caught

Both were invisible to every other check in the file, which is the argument
for rendering one.

  * THE OPERATOR PANEL WAS SET UPSIDE DOWN AND MIRRORED -- both axes
    backwards, which is a 180 degree rotation. `_UV` puts vertex 0 at the
    tile's bottom-left, and for a clerk standing at +Y "up" is the -Y edge and
    "right" is -X, so vertex 0 has to be the (+X, +Y) corner. `_top_art` is
    that one decision, in one place, for both face-up quads.
  * THE RECEIPT read as a flat white card at 24 degrees off upright, because
    at that angle it foreshortens to nothing in the clerk's own frame. 15
    degrees now, and 3.2 x the printer's height rather than 2.2.

### `display_case` gained `params.till`, and what Deli Counter has to do

Default 1: **nothing changes for anybody who does not ask**. A placer that has
not learned to stand a `cash_register` still gets a shape in the right place,
which is better than a bare counter.

MEASURED AT EVERY SHIPPED WIDTH before it was claimed: at 1.8, 2.4 and 3.6 m,
flat and L, turning the till off leaves every non-till primitive and the item
count identical and removes exactly 48 triangles. Only on the genome's
narrowest case (0.9 m) does the till's keep-out cost anything, and there it is
one storage item, 32 against 33.

WHY A SLOT AND NOT A BETTER BOX INSIDE THE CASE. A till built inside
`display_case_forms` cannot carry an atlas, cannot be lit, and cannot stand on
a deli counter, a pharmacy counter or a bank teller line. It is the same
hand-authoring the gap protocol forbids downstream, one layer up.

WHAT DELI COUNTER WOULD CHANGE, stated here because this repo does not touch
that one:

  1. a `_piece("cash_register", ((0.40, 0.42, 0.46),), "pair", front=True,
     variants=4, collision="none", ...)` -- `pair` for the reason `back_bar`
     and `display_case_end` are: it belongs to a counter and nothing should
     place one on its own;
  2. a row in `prop_species.PROP_SPECIES` before any broader keyword:
     `(("cash_register", "register", "till"), "cash_register")`;
  3. `card_shop_counters` stands one per showcase counter at that counter's
     till station, the way it already stands a pack wall behind one, and lifts
     it to the counter's top;
  4. `params.till: 0` on the `display_case` it stands it on, in the same
     breath. All four, or none: a case with its till off and no register
     standing is a bare counter.

### And an ATM is not a cash register

`atm`'s keyword list held "cash register", and on 0.99.0
`intent.parse("cash register")` returned `atm`. It is off the ATM now; `atm`,
`cash machine` and `cashpoint` still resolve to it. A sweep over every keyword
of every species in the library is a test now: four resolve elsewhere and all
four are deliberate shared words that predate this release.

### Tests

`tests/test_cash_register.py`: 171, of which 165 are pure and 6 need Blender.
Every corner for fit, budget, coplanarity and type scale; every price for the
denylist; the winding of both face-up quads and of the lit one; the atlas's
cap and its name; the `till` switch on both settings.

Three library-wide counters moved, each because a species landed rather than
because anything is wrong: `CENSUS_BUILDS` 312 -> 315 (and the census was
actually run, which is the thing that comment exists to promise),
`test_theme_style_resolution`'s styled count 79 -> 80, and
`test_material_options_closed`'s PAINTED set, which `cash_register` joins
because its `industrial_flats` style is enamelled sheet steel.

Suite **2,295 -> 2,465 passed**, 271 -> 278 skipped, 1 xfailed. Both figures
are with Pixelcoat beside this repo; in a `git worktree` under `scratchpad/`
it is not, two `test_club_species` / `test_vending_machine` cases skip instead
of passing, and the same suite reads 2,293 -> 2,463 / 273 -> 280. Worth
writing down because the difference looks like a regression and is a path.

## [0.99.0] - a taller bay carries more shelves, and the cap that says how many is arithmetic now

Deli Counter 0.140.0 took `card_shop_a01`'s pack walls from 2.2 m to 2.70 m
because the walker's verdict on cold run 9061 was that the shop reads as a
hall, and reference property 1 in `docs/SET_DRESSING_REFERENCES.md` is
"product goes to the ceiling, not to waist height -- the top shelf is as
full as the bottom". Deli Counter's own note records what it got for the
half-metre: nothing. MEASURED here first, against `pack_wall_forms.plan` at
0.98.0, depth 0.5, variant 0, over Deli Counter's palette widths:

    width   2.20    2.55    2.70    3.20
      1.2    720     720     720     720
      2.4  1,416   1,416   1,416   1,416
      3.6  2,112   2,112   2,112   2,112
      8.0  4,896   4,896   4,896   4,896

Not close -- IDENTICAL, at every width and every height in the genome's
range. `n_shelf` was `min(CAPS["shelves_per_bay"], int(room / SHELF_CLEAR))`
and `CAPS` won everywhere: at 2.2 m the fit term is already 10.8. So the
height bought a re-spacing of the same six shelves and nothing else. On a
2.4 m bay the pitch went 0.259 (h=2.2) -> 0.331 (2.70) -> 0.401 (3.2), over
a booster box 0.092 m tall. A frame of it is in this release's notes and the
white underside of a shelf plank is the biggest thing in it.

### The count is the height now, and the cap is two budgets

`max_rows` replaces `CAPS["shelves_per_bay"]`. A bay takes as many product
rows as its own height fits, `int(room / SHELF_PITCH_MIN)`, and the cap is
derived from what a row costs against what a bay may spend:

    a faced product  14 tris   a box (12) and its art quad (2)
    a shelf plank    12        one box
    a bay's frame    38        kick, base, header, header art
    a module's frame 12 + 12 a bay edge   the slatwall back and the uprights

`bay_tris` and `module_tris` price the row mix the planner actually builds,
including that one row in `PEG_EVERY` is hung blister packs and carries
`pegs_per_row` rather than `boxes_per_shelf` -- and `PEG_EVERY` is read by
the planner and by the pricing, one quantity with one spelling.
`test_a_bay_costs_what_the_cap_assumes_it_costs` holds the model against the
planner at every genome corner and every variant, the way `pennant_row`'s
does, because a cap whose arithmetic has gone stale is a comment.

### THE MODULE BUDGET IS NOT WHAT HOLDS THIS SPECIES, and that is the finding

6,000 (`budgets.tris_lod0`) bounds one module. At 3.6 m it would pay for
NINETEEN shelves a bay. A cap derived from it alone is a cap that cannot
fire, which is indistinguishable from no cap at all (0.95.0's own rule, one
layer up).

What binds is the ROOM, because a pack wall is the one species a room stands
eight of. Deli Counter 0.140.0's `_PIECES` allows four wall runs (`most` 4,
worst palette size 3.6 m, three bays each) and two islands (`most` 2), each
`twin` and therefore two modules of 2.4 m, two bays each: twenty bays. Its
room budget is `_CARD_SHOP_ROOM_TRIS` = 24,000, which is one `cubicle_bank`
-- the figure THIS changelog offered for scale in 0.95.0. The rest of that
room's worst case is 8,192 and the eight modules carry 432 of frame, so:

    24,000 - 8,192 - 432 = 15,376, over twenty bays = 768 a bay

That is `budgets.tris_per_bay`, new, and it is the one dial. Both caps are
load-bearing and each bites where the other does not: lift BOTH at the
genome's largest slot (8.0 x 0.6 x 3.2) and the module draws 7,486 against
6,000; lift only the bay budget and the module budget still holds 8.0 m --
seven bays share it -- but a 3.6 m run goes to ten shelves a bay and the
room goes to 29,704. `test_both_pack_wall_caps_are_load_bearing_and_neither
_alone_is_enough` asserts both, and it is the test 0.95.0's entry claimed
this species had: the "removing the cap BLOWS the budget" test written then
was `display_case`'s. `pack_wall` never had one.

### What it draws now, and what it cost

Depth 0.5, variant 0; triangles / shelves a bay:

    width   1.60        2.20        2.55        2.70        3.20
      1.2    528/4       720/6       802/7       802/7       802/7
      1.8  1,032/4     1,416/6     1,580/7     1,580/7     1,580/7
      2.4  1,032/4     1,416/6     1,580/7     1,580/7     1,580/7
      3.6  1,536/4     2,112/6     2,358/7     2,358/7     2,358/7
      4.8  2,040/4     2,808/6     3,136/7     3,136/7     3,136/7
      8.0  3,552/4     4,896/6     5,470/7     5,470/7     5,470/7

Worst bay 766 of 768; worst module 5,470 of 6,000. The card-shop room goes
from 22,304 to 23,944 of 24,000 -- 93 % to 99.8 % -- and the cap is what
lands it there rather than luck: an eighth shelf is 862 a bay and puts the
room at 25,864.

**h = 2.2 IS BYTE-IDENTICAL.** 72 of the 360 plans in the corner sweep are
unchanged prim for prim, and they are exactly the 2.2 m ones -- the height
Deli Counter shipped before 0.140.0, and the height the 0.95.0 measurements
were taken at. Nothing that was standing at 2.2 m moves.

### What the cheap version loses, said rather than quietly narrowed

ONE EXTRA SHELF IS ALL THE ROOM CAN BUY, and at 3.2 m a bay still reads
airy. Held at `SHELF_PITCH_MIN` at every height -- which is what the
reference actually shows -- a bay takes eight shelves at 2.70 m (pitch
0.257) and ten at 3.2 m (0.256), costs 1,054 a bay, and puts the room at
25,864 (108 %) and 29,704 (124 %). The expensive frame is in this release's
notes beside the shipped one and it is the better picture: the shipped bay
at 2.70 m pitches at 0.289 against the expensive one's 0.257. The standing
call is performance over look when the two compete (CLAUDE.md), there is
still no runtime telemetry from a real session, and `tris_per_bay` is the
dial to turn when there is. What is missing is 192 triangles a 2.4 m module.

A SHORT BAY LOSES TWO SHELVES AND GAINS ITS BLISTER ROW. At 1.6 m, 0.98.0
drew six shelves at a 0.173 pitch; 0.99.0 draws four at 0.242. That is the
second half of the same defect and it is worth naming separately.

### `SHELF_CLEAR` was measured off the wrong product

`BOX_H + 0.075`. The tallest thing a row stands is the hanging blister pack,
`PEG_H` = 0.145, which is 53 mm taller than a box -- so the count said a row
fitted where it did not, and the peg row's own MEASURED-clear check (0.95.0,
written because peg tops ran into the shelf above by 2.14 mm) quietly
dropped it instead. MEASURED over the genome's corner set: 0.98.0 draws ZERO
blister rows at sixteen of them, every one of the 1.6 m corners. It is
`max(BOX_H, PEG_H) + 0.075` now, the 0.075 reach-in kept exactly as it was
written, and `SHELF_PITCH_MIN` adds the plank -- which `int(room /
SHELF_CLEAR)` never did either, because it produced `room / (n + 1)` and not
`SHELF_CLEAR`. The cap hid both at every height in the range.

The two guards under it, `BOX_H + 0.020` and `PEG_H + 0.025`, now sit 50 mm
below the pitch the count derives, so no threshold is asked of two spellings
of one quantity and the guards are a backstop rather than the plan.

### One for Deli Counter, with the numbers

`test_card_shop._WORST_TRIS` pins `pack_wall` at 2112 with the comment
"HEIGHT DOES NOT MOVE IT" and `pack_wall_island` at 1416. Both are 0.98.0
readings and both are stale: at any height at or above 2.55 they are 2,358
and 1,580, and `test_the_room_budget_is_zoo_s_only_real_one_and_the_caps_fit
_under_it` asserts `worst == 22304`, which is 23,944. The caps themselves
still fit -- 23,944 of 24,000, and one more island is still over it -- so
this is a re-reading, not a re-capping. `test_the_measured_module_costs_are
_still_zoo_s` is the test that will say so first, which is what it is for.

### The 0.95.0 `CAPS` comment's triangle figures do not reproduce

Found while re-measuring to set `tris_per_bay`, and kept in the file above
the numbers that replaced them. `pack_wall_forms.CAPS` has carried, since
0.95.0 and unchanged by any commit since, "caps lifted to 99: 406 items,
5,684 tris", "these caps: 287 items, 4,046 tris" and "578 triangles a bay",
all at 8.0 x 0.5 x 2.4. Re-run against 0.98.0's own planner: the ITEM count
is right (287) and NOT ONE of the triangle figures is. That slot draws
**4,896**, which is 684 a bay, and the lifted-cap case draws **637 items and
10,300** -- 172 % of the module budget, not the 95 % the comment implies.

578 travelled, which is why it is worth an entry rather than a quiet fix. It
is in this species' own genome note beside the correct 4,896, in a sentence
that disagrees with itself (4,896 over seven bays is 699), and it is in Deli
Counter's `_PIECES` as "578 triangles a bay against 6,000" -- a figure that
was read as headroom while deciding how tall to build a pack wall.

### Tests

Five, all in `tests/test_card_shop.py`, all failing on 0.98.0:
`test_the_shelf_count_follows_the_bay_s_height`,
`test_the_shelf_pitch_takes_the_tallest_product_the_row_stands`,
`test_a_bay_costs_what_the_cap_assumes_it_costs`,
`test_both_pack_wall_caps_are_load_bearing_and_neither_alone_is_enough`,
`test_the_bay_budget_is_the_one_dial_that_makes_a_gondola_denser`. The whole
suite is 2,293 passing, and the corner tests every interior species keeps --
exact extents, no two faces within 2.2 mm of a plane, deterministic, budget
at every corner -- pass unchanged at the new pitches.

## [0.98.0] - the flat art, which is two triangles and a texture

The walker walked cold run 9061's `card_shop_a01` and sent the frame back:
"the card shop should feel saturated with posters, ads, playmats, content,
fantasy, ect ect." `docs/SET_DRESSING_REFERENCES.md` splits that into five
properties the room lacks; this is Zoo's cheap half of three of them --
things hang, posters live above the shelving, and the play tables carry
printed surfaces. Four species and one path through `_surface_stock`.

    poster           framed / bare / tilted       78 / 14 / 14 tris
    hanging_banner   cloth on a rod, two straps   62 tris
    ceiling_hanger   a painted board on a chain   52 tris
    aisle_sign       a hand-lettered section sign 88 tris
    _surface_stock   the playmat is PRINTED now   14 tris a mat, was 36

### The density costs 948 triangles and 2.4 MiB, and here is the arithmetic

The walker asked for MORE and the standing call is performance over look, so
the only honest way to ship a density pass is with the figure attached.
`tools/flat_art_cost.py` (new) stands a saturated card shop -- eight posters
in the three forms, three banners, four ceiling hangers, three aisle signs
and the two play tables' mats -- through `kit.plan_kit` and
`build.build_module`, the road a kit build takes, and reports what the scene
holds. Blender 5.1.1, 2026-09-16, theme delco_1997, style 1:

    20 placements, 19 modules built     the kit builds one module per
                                        distinct species+dims+variant
    114 mesh objects, 1,408 triangles   948 of them the flat art; the rest
                                        is the two folding tables
    18 art images, 2.392 MiB            decoded RGB8, the figure that is
                                        spent on every client
    18 art meshes for 25 art quads      one mesh and one material per
                                        module, however many quads it has

948 triangles against the 10,664 the shipped card shop measured is 8.9% for
every poster, banner, hanger and sign in the room. One `cubicle_bank` is
budgeted 24,000, so the whole set is 4% of one of those. Geometry is not
where flat art costs anything and the caps on these four genomes are not
what will hold the room back.

THE TEXTURE IS WHERE IT COSTS, and 2.4 MiB is a real number on a low-end GL
Compatibility client. Two things hold it down and both are measured rather
than asserted:

  * ONE ATLAS PER MODULE (`recipes/_card_atlas.py`, 0.95.0's argument). 25
    art quads arrive as 18 meshes carrying 18 materials, not 25 and 25 --
    a two-sided hanging sign is one tile on two quads in one mesh, and a
    play table's mats are one mesh however many are on it.
  * THE ATLAS IS NAMED BY A DIGEST OF ITS OWN PIXELS, so two placements
    whose art is identical share one image. The room stands eight posters
    and holds seven poster images.

WHAT THE EXPENSIVE VERSIONS WOULD BUY, in figures, so they can be chosen
later rather than argued about:

  * A SHARED ATLAS ACROSS MODULES would take the 18 texture binds to 1. It
    saves almost no bytes -- the same pixels are packed either way -- and it
    needs a building-wide paint pass, which is a `kit` change and not a
    species one. Named here; not built.
  * 512 px/m INSTEAD OF `card_art.TEXEL` (256) would put a poster 1:1 with
    the screen at three metres. It quadruples every poster tile: 1.18 MiB of
    poster art becomes 4.70 MiB, +3.52 MiB for the room, and nothing else
    moves. See the reading arithmetic below.
  * A DIE-CUT HANGER -- an alpha-tested silhouette instead of a rectangular
    board -- is what the reference's dragon and kraken actually are. The
    pipeline has the kind (`foliage`, the tree crown cards) so it is
    reachable; it costs a transparency pass on a mesh hanging over the
    middle of the room, which is exactly the shape this repo has refused
    before. Not built, and the hanger is honestly a painted BOARD.

### Reads as art at three metres, a coloured rectangle at ten

That was the brief's gate and it is arithmetic about a display, not a taste.
One metre at distance z subtends `2*atan(0.5/z)`; on 1920 px across a 70
degree horizontal FOV that is 27.43 px per degree, so one metre is 519
screen px at 3 m and 157 at 10 m. `flat_art.reads_at` is that arithmetic and
`tests/test_flat_art.py` holds the numbers.

At `card_art.TEXEL` -- 256 px/m, the factory's 4 mm pixel -- a 0.6 m poster
is a 154 px tile shown across 313 screen px at three metres (magnified 2.03
to 1, so blocky, which is the house look and not a defect) and across 94 at
ten metres (minified 1.63 to 1, which is the coloured rectangle, and comes
free). The frames were rendered at 2.17 m and 7.23 m rather than 3 and 10,
because `preview_specimen`'s 40 mm lens on a 960 px render is 19.81 px per
degree against the target's 27.43 -- a factor of 1.384, and rendering at the
nominal distance would have shown a poster 38% bigger than the game does.

### What a thing hangs from, which nothing here had ever answered

Three candidates, checked in order:

  1. THE CEILING GRID'S OWN GEOMETRY. There is none. A dropped ceiling is a
     `ceiling` slot built by `recipes/ceiling.py` into ONE solid
     `Ceiling_Panel`, and the grid is a Pixelcoat `ceiling_tile` skin on its
     underside. No T-bars, no runners, no tile edges in the mesh.
  2. A DELI COUNTER LIGHT ANCHOR. `core/fixtures.py` has exactly the
     mechanism -- `mount: "hang"`, added in 0.94.0 after a club can was
     built inside the slab, TOP at the emitter and body below. But its input
     is a `<building>.lights.json` and every row in `FIXTURES` is a lamp; a
     painted dragon on that manifest makes Lux spawn a Light3D at it.
  3. A PROP SLOT, HUNG. This is the one, and it already ships.
     `level_design._piece`'s `under` is the gap between a piece's top and
     the ceiling PLANE and `_piece_lift` turns it into a centre height --
     `_clear_height(spec) - under - h/2`. `pennant_row` has hung from it
     since 0.95.0, and Deli Counter's own test says why it is `under` and
     not a fixed lift: "a fixed 2.95 would have been right at the card
     shop's 3.4 m storey and 0.6 m inside the slab at the strip club's
     3.6 m one".

So Zoo's side of the contract is one sentence: THE TOP OF THE SLOT BOX IS
THE CEILING PLANE. A `ceiling_hanger`'s chain starts at z = h and the board
hangs below it. Deli Counter needs one `_piece(..., under=_CEILING_AIR)` row
per species and nothing else.

HEADROOM, DERIVED AND NOT CHOSEN. Both hanging genomes top out at 0.60 m.
`deli_counter/agent_contract.json` clearances.min_headroom_m is 2.0 (read
2026-09-16); `_clear_height` is the storey less the thicker slab less
`_CEILING_AIR`; the piece's own `under` spends that air again. At the
library's shortest storey: 3.0 - 0.3 - 0.05 - 0.05 - 2.0 = 0.60.
`flat_forms.hang_max_height()` is that formula and the test asks the genomes
for it. A THICKER SLAB MAKES IT SMALLER and Zoo cannot see the slab, so this
is a genome cap and not a guarantee -- the placement is Deli Counter's.

### The poster's layout, which a fourth reference corrected mid-build

The first three poster references read as a title block along the BOTTOM,
and that is what the first draft painted. The walker then sent a framed
magazine cover -- silver frame, red fabric mat, a green horned ogre filling
the plate and looking out of it, a small armoured figure held against its
chest, burning sky and a castle behind -- and it settles the layout the
other way: TITLE AT THE TOP, over the art, in a serif; the only thing at the
bottom is a small publisher mark in a corner.

`tests/test_flat_art.py` holds that as a PIXEL measurement rather than a
reading of the source -- it paints the plate again with the title's ink
removed, then again with the maker's, and asks where the pixels moved. The
title's are all above 30% of the plate; the mark's are all below 85% and
right of the middle.

A FRAMED POSTER IS THREE RECTANGLES. "The mat is what makes it read as
framed rather than taped to the wall", so it is a ring of geometry that
drops the art 4 mm behind the frame, not a border painted into the tile. It
costs 64 of the framed form's 78 triangles; the `bare` form does not want
them and does not get them.

And the walker's own words on sending it are now the standing arrangement
for every reference in that file: "obviously we can't copy this intellectual
property, but it is comps of what it could look like." The composition
travels; the content does not. Every string these species paint comes from
`core/card_brands.py`, which is invented, and `AISLE_SAYS` (new -- what a
sign over an aisle says, a separate table from `SHOP_SAYS` because that is
read at 0.15 m and this across a room) goes into `card_art.painted_strings`
so the same denylist test walks it. The first draft of that table said
"SELECT SINGLES"; SELECT is a real card brand and `DENY_WORDS` caught it.

### Four boxes cannot make a ring, and one mesh can

A frame is a rectangular ring and the obvious way to build one is four
rails. Every variation of that fails the same measurement: wherever two
rails overlap they share the ring's own outer silhouette -- x = +/- w/2 is a
face of the left rail AND of the top rail over the top rail's depth, whatever
inset either is given -- and wherever they butt they meet face to face.
Measured on the first draft, 8 pairs per poster at 0.00 mm, 4.4 cm2 apiece.

One mesh has none, because its four front trapezoids are coplanar but
ADJACENT: they share edges and overlap in zero area. It is also cheaper --
32 triangles against a box ring's 48. Its winding is hand-written, so a test
steps a millimetre out of every face along its own normal and checks the
point has left the solid.

THE DEPTH LADDER IS FRACTIONAL, and that is the one decision in `flat_forms`
worth arguing with. An absolute ladder is what a real frame has -- a 3 mm
mat is 3 mm wherever it hangs -- but a plan has to fill its slot's depth
exactly, so an absolute ladder gets squeezed by `fit_exact` and every
separation moves with it. Fractions scale instead, the worst case is the
genome's minimum depth, and there is exactly one place to check it: at the
poster's 0.02 m minimum the closest rung is 3.2 mm against a 2.2 mm window.

### The playmat is printed, which was recorded as a limit in 0.95.0

`_surface_stock`'s own docstring said it: "NOT TEXTURED, and that is a limit
rather than a choice: `prim_mesh.build_stock` has no textured path, so a mat
is a colour with a border and not art." That path exists now. A flavour may
return `tiles` beside its prims and `build_stock` sends the prims that name
one through `_card_atlas` into one mesh with one material, so a table's mats
are one extra draw however many are on it. The two `Stock_MatEdge` slabs
that stood in for a printed border are gone -- the border is in the print,
where a real one is -- which is 22 triangles back per mat.

A FLAVOUR WITH NO TILES TAKES EXACTLY THE OLD ROAD, and that matters more
than the new one: `tiles` is empty for office, bar, kitchen, vault, storage
and bar_dense, so the atlas is never built and the "card_art" stream is
never drawn from. The `cards` flavour's own LAYOUTS do move, because
`_playmat` now draws one number from the stock stream to pick its game.

### Three defects the frames caught and the tests did not

The 0.96.0 entry's lesson, repeating. 65 tests passed over geometry that had
all three of these in it.

  * THE CREATURE'S HEAD FLOATED. Head centred at 0.30 of the sub-frame and
    the torso starting at 0.46 left ten pixels of sky between them on a
    154 x 230 plate. The shoulder line is DERIVED from the head now -- three
    quarters of a head-radius below its centre -- so the two overlap at any
    aspect.
  * THE HORNS FLOATED TOO, and for a measurable reason: three blocks a side
    at 0.70, 1.02 and 1.34 head-radii out and 0.85 up, against a skull whose
    ellipse is 0.38 radii wide at that height. All six were clear of the
    head and read as antennae. The sweep starts inside the ellipse now and
    each step overlaps the one below.
  * "YOUSE VS. THEM" RENDERED AS "YOUSE VS_ THEM". `_serif` widened the top
    and bottom row of every inked column, and a full stop's ink IS both its
    own top row and its own bottom row, so it came out three pixels wide. A
    serif is a foot on a STEM: only a column whose ink spans half the line
    gets one.

A fourth was caught by a test doing the same job -- asking where the pixels
went rather than whether a function was called. The maker's mark was stamped
into a band `pt.LINE // 2` tall, which is 8 rows for a face whose capitals
trim to 11, and `card_art._stamp` paints NOTHING rather than a smear when
the ink does not fit. Every poster shipped with no mark at all and nothing
said so -- the same shape of mistake `_stamp`'s own docstring records for
the booster-box fronts, "0 of 12 lettered, then 12".

### The gates

`tools/coplanar_census.py`, Blender 5.1.1, 2026-09-16, the four new species
at min/default/max: **12 builds, 0 with coincident pairs, 0 that did not
build**. `tests/test_coincident_faces.py`'s `CENSUS_BUILDS` goes 300 -> 312
and `RESIDUE` does not move.

Two library-wide gates caught genome defects before any of this was looked
at, and both are the kind that would have shipped silently:

  * `test_species_by_name` -- `ceiling hanger` resolved to `ceiling` (a
    shorter keyword at the same start) and `aisle sign` matched nothing at
    all. Every keyword list carries both spellings now.
  * `test_material_options_closed` -- the poster's frame was offered raw
    `metal`, which is theme-owned, so a building's pack would have repainted
    the reference's SILVER frame. It is `metal_bare` (object-owned, the mesh
    supplies the hue); the two hung species' chains are a `metal_bare`
    constant in the recipe.

`card_art.paint` also learned to fail properly: an unknown kind used to
raise `KeyError('game')` from the line below the dispatch, which is a
failure that names the wrong thing.

Suite: 2,288 passed, 273 skipped.

## [0.97.0] - the stop sign's back faces, and a census of every other one

A coincident face pair is two faces of one prop on one plane, overlapping,
with nothing between them: the depth test decides per pixel and the pixel
flickers. Zoo has said since 0.84.0 that an interior species ships none of
them and `tools/coplanar_probe.py` measures it. `stop_sign` predates that
rule and nothing gated it, so it shipped THREE pairs at 0.00 mm at every
genome corner -- on the one prop that stands at every stop-controlled
approach in every level.

    OPP  gap 0.00 mm  2394.15 cm2  StopSign_Border <-> StopSign_Face
    OPP  gap 0.00 mm  1436.49 cm2  StopSign_Border <-> StopSign_Face
    OPP  gap 0.00 mm   177.12 cm2  StopSign_Border <-> StopSign_Post

### Three rows, two defects, and one of them is the instrument

Before patching a gate's output, account for every item in it. The first two
rows are ONE defect: the red face's back cap lying on the white border's
front cap, over the whole inner octagon, 3830.64 cm2 of it. The probe splits
it in two because its aggregation key carries `normal_of_a` -- the outward
normal of whichever of the pair's two triangles sorted first.

This was reasoned about once and then printed, because a float question that
survives one round of reasoning should be printed rather than reasoned about
again. The first answer was "the two offsets are the same float to the last
bit, so the sort ties". They are not. After `geometry.fit_to` the border's
front cap sits at -0.03228921778311645 and the red face's back cap at
-0.03228922012972646 -- two nanometres apart, and the twelve triangles of the
two fans interleave down the sorted list, so `normal_of_a` comes out +Y for
five eighths of the overlap and -Y for three. A tie would have produced ONE
row; what produced two is that there is no tie.

`core/prims.coincident_pairs`, the
pure port, keys the same pair WITHOUT the normal and reports it as one row.
Neither is wrong and they do not disagree about the geometry, but a count
compared across the two instruments is not comparable, and this entry's
numbers are the bpy probe's throughout.

The third row is a second defect of the same shape: the border's back cap on
the post's front face. `FACE_PROUD` separated the red face's FRONT, which is
the relief you can see, and nothing separated any back cap -- the recipe's
own docstring claimed "no legend face shares a plane with any face of the
sign", which was true of the legend and of nothing else.

### AND THEY WERE NOT VISIBLE. The frames are the same picture

The brief this came from said every stop-controlled approach in every level
stands one of these, which is true, and that they z-fight, which the frames
do not support. Rendered at 3 m, 8 m and 20 m from a 1.7 m eye, before and
after, the sign is identical: no speckle, no white through the red.

Coplanar is not visible. A pair on one plane can only be argued over by a
depth buffer where a viewer can reach it, and all three of these sit INSIDE
the sign: the red plate's own front cap stands 4 mm in front of the first
two, and the border's 15 mm body in front of the third. So
`tools/coplanar_census.py` (new) adds what the probe does not measure --
after probing a build it casts a ray out of each pair along its normal, both
ways, and reports `cover`, the distance to the first surface it meets.

    cover 0.00 mm            the pair is on the outside of the prop. The
                             depth test decides it at every distance.
    cover > 0                buried. It fights only once the depth buffer
                             stops resolving `cover`.

On a 24-bit fixed-point depth buffer at Godot's `Camera3D` defaults (near
0.05, far 4000, classic non-reversed z -- what the GL Compatibility target
gets), the separation a buffer can still resolve at distance z is
`z^2 * (f - n) / (f * n * (2^24 - 1))`, so a cover of `s` metres survives out
to `sqrt(s * 838871)` metres. The stop sign's worst cover is 2.70 mm at the
genome's smallest size: it would have started fighting at about 48 m, which
is further than a stop sign is read from.

**So this change is made because the rule is the rule and because it costs
nothing, not because a frame showed it.** 372 triangles before and 372 after.
Saying otherwise would be exactly the substitution this repo keeps catching:
a cheap observable standing in for the expensive truth with nothing recording
the substitution.

### The fix is a ladder, and the rung is derived

`core/sign_blade_forms.py` solved this geometry for `sign_post` in 0.96.0 and
its rule is the one applied here: eleven parallel planes stack up behind a
sign face, every one overlaps every other in projection, so the rule binds on
all pairs at once and a solid is pushed THROUGH its neighbour rather than
laid on it. `stop_sign` now has eight planes and its closest two are 3.5 mm
apart:

    -53.0 mm  legend front        -41.5 mm  face back
    -49.0 mm  face front          -37.5 mm  legend back
    -45.0 mm  border front        -30.0 mm  post front
                                  -26.5 mm  border back
                                  +30.0 mm  post back

`SEP` is derived rather than picked, and its derivation is a test rather than
a comment. `geometry.fit_to` scales the recipe's authored 83 mm of depth into
the slot's, which at the genome's smallest depth (0.056) is a factor of
0.675, so an authored rung reaches the probe multiplied by that. The probe
reports anything within 2 mm and floats land ON that number
(`0.0020000000000000018 > 0.002`, 0.91.0), which is why the pure tests have
asked 2.2 mm since `test_card_shop.py`. `0.0022 / 0.675 = 3.26 mm`, so 3.5 mm
is the next half-millimetre up and leaves 2.36 mm in the smallest built sign.
Narrow it to 3.0 and the min corner has 2.02 mm, inside the cushion; a test
asserts both halves of that.

**From the front nothing moved; from behind the blade is 3.4 mm thicker, and
that is a real change rather than a rounding.** The red face still stands
4 mm proud of the border and the legend 4 mm proud of the red face, and the
front-view frames are the same picture to 42 pixels in 614,400. But the
border's back cap is the blade's back, it is visible from behind everywhere
except over the pole's own 6 cm, and the only way to get it off the post's
front plane while the blade still TOUCHES the post is to push it through:
14.5 mm of white rim at the default size becomes 17.8 mm. Measured at 1.6 m
from a rear three-quarter, 3920 pixels of 614,400 differ by more than 8
codes.

The two alternatives were priced and are worse. Pulling the blade forward
instead leaves 3.5 mm of daylight between sign and pole -- the defect cold
run 9048 reported in mirror image. Thickening the POST to 63.5 mm so its
front face clears the blade's back is arguably more correct (a 3 lb/ft
u-channel really is 2.5 in, which is what `sign_blade_forms.POST_W` uses) and
it changes the collider and makes the pole's section rectangular, which is a
bigger change than a white rim nobody is measuring. What the expensive
version would buy is the rim held at exactly 14.5 mm, and it costs a
re-derivation of `LEGEND_BURY` and `BLADE_T` together because the legend's
back cap is pinned to half the blade -- worth doing the day somebody objects
to the rim, and not before.

A prism's triangle count does not depend on its thickness, which is why none
of this costs a triangle.
`ATT_face` is now written as `red_front` rather than as an offset from the
plate's centre, which is the same coordinate it always was and stops being so
the moment the plate's thickness is not `FACE_PROUD`.

### mailbox was the same cause, and its census row went 15 -> 6

The census found the identical shape on `mailbox`: the collection box's lip
had its back cap exactly on the body's front face (0.00 mm over 117-238 cm2)
and the door's back cap 0.5 mm behind it, 0.46 mm once the depth was
squeezed. Both are now pushed through the face -- `BACK_BURY` 2.5 mm for the
door, twice that for the lip so the two back caps do not land on each other
either. Its squeeze is NOT the stop sign's (0.9245, because it is the lip
that stands proud of the slot), so it derives its own rung and a shared
constant would have been wrong in both places. 264 triangles before and 264
after.

`mailbox` is gated at its remaining TWO pairs and not at zero, named by part:
the lid's foot on the body's top face and the legs' tops on its underside,
164 mm and 220 mm inside a closed solid. Those are BUTT JOINTS, a different
cause, and this release does not touch that cause anywhere -- fixing it on
one species and nowhere else would be the fix that does not generalise.

### The census: every species, every corner

`tools/coplanar_census.py`, Blender 5.1.1, 2026-09-16. Every species with a
genome, at its min, default and max corner, planned through `kit.plan_kit`
and built through `build.build_module` -- the path a `zoo_kit_build` takes --
then probed at the probe's own defaults (2 mm, 1 mm^2, normal 1e-3). A
species whose NAME is a role (`wall`, `floor`, `doorway` ...) is planned
under that role, because a `prop` slot asking for `wall` gets a slab.

    300 builds
      3 did not build      boots, KeyError 'shaft_h' at all three corners.
                           A different defect; not this release's, and
                           recorded rather than skipped.
     38 built clean
     61 reported pairs     3027 of them

Split by whether a viewer can reach the pair. The head of each half, with the
full table in `tests/test_coincident_faces.py`:

**Exposed (cover 0.00 mm) -- 24 species, 973 pairs.** These fight at every
distance and are the ones worth a triangle. `stop_sign` is not among them.

    species              pairs  SAME   OPP  exposed   largest cm2
    safe_deposit_boxes     884   822    62      411        1169.8
    cubicle_bank           583   290   293      127        8315.9
    stair_rail             162   162     0      100         148.4
    glass_shard            118    64    54      118         258.0
    teller_line            114    31    83       25        3882.2
    flat_top_grill          92    69    23       60       15163.2
    bus_shelter             87    66    21       30         469.4
    street_tree             39    22    17        6      437884.4
    pin_oak                 31    21    10        7      391635.0
    cheesesteak             29     4    25       20           0.2
    red_maple               28    17    11        9      235404.6
    callery_pear            26    11    15        5      116580.0
    london_plane            21    10    11        4      350560.2
    honey_locust            19    10     9        7      113356.1
    cash_stack              16    16     0       16          28.9
    hvac_unit               13     7     6        7       96445.4
    vault_door              12     4     8        1          43.5
    parking_meter            9     3     6        3         781.2
    club_fixture             7     3     4        3        1323.6
    water_barrel             6     6     0        6        4652.1
    rubble_frag              3     2     1        3          53.4
    payphone                 2     2     0        2           2.4
    weed_tuft                2     2     0        2           2.4
    security_camera          2     1     1        1          55.9

**Buried -- 37 species, the rest.** Ordered by the thinnest cover, which is
what decides the distance at which each starts to fight:

    species           pairs   min cover   fights beyond
    soda_cup              7      0.21 mm          13.3 m
    litter_scrap          1      0.34 mm          16.9 m
    mailbox              15      0.95 mm          28.3 m   (now 6, see above)
    stop_sign             9      2.70 mm          47.6 m   (now 0)
    ladder              110      5.00 mm          64.8 m
    newspaper_box         7     10.77 mm          95.1 m
    desk                182     15.75 mm         114.9 m
    filing_cabinet       83     18.00 mm         122.9 m
    ...
    bench                18     40.00 mm         183.2 m
    floor/ceiling/roof   40      8.00 m          2590.6 m

The shapes the part names show, which is a reading of the table and not a
measurement of the recipes: many instances of one flat piece landing on one
plane (`glass_shard`, `rubble_frag`, `weed_tuft`, `litter_scrap`, the
cheesesteak's seeds); one shape built as a pile of separate boxes with their
internal walls facing each other at nil separation, which is exactly what
`sign_blade_forms`' second note warns about (`cubicle_bank`'s caps,
`safe_deposit_boxes`, `stair_rail`, `teller_line`, `bus_shelter`,
`flat_top_grill`'s splash guards); tree crowns whose lobes intersect
(`street_tree` and the four named species, the largest overlaps in the
library at 11-44 m2); a thin band or rim laid on a body (`cash_stack`,
`soda_cup`); and butt joints between closed solids, which is nearly all of
the buried half.

**None of that is fixed here and none of it is a verdict.** It is a named,
measured residue with a test that holds each species to the count it shipped
at, so a species that gets fixed -- or that gets worse -- turns the suite red
and says by how much.

### What this does and does not move

Nothing in the interventions-per-level number. No level needed a hand-patch
for a stop sign and none will. What it closes is one species' distance from a
rule the library already states, and what it ADDS is the first instrument in
this repo that distinguishes a coincidence a player can see from one buried
in a solid -- 3027 rows that read as one problem are two problems in a 973 /
2054 split, and before the census there was no way to say which was which.

A strict xfail was tried on the residue first and was the wrong instrument:
asked at the default corner it went XPASS on six species that are dirty at
one corner only (`ceiling`, `floor`, `roof`, `payphone`, `security_camera`,
`vault_door`). The count replaced it. One strict xfail is kept, on the claim
that the whole library keeps the rule, so that the claim is red on the board
rather than true in a paragraph.

THE SUITE, both ways. Without Blender: 2209 passed, 269 skipped, 1 xfailed
(0.96.0: 2196 / 202). Inside Blender 5.1.1, where the bpy half runs:
2443 passed, 35 skipped, 1 xfailed. The gate was run against 0.96.0 with
THIS release's probe and census copied in, so that the only difference
between the two sides is the recipe -- six failures, three stop signs and
three mailboxes, each naming the pairs it found.

`tools/coplanar_probe.py` gained one optional argument, `samples`, default 0,
which records points inside each row's overlap for the census to cast rays
from. With it off the rows are what they always were, which is why the census
and the probe cannot drift apart: there is still one pairing implementation
and the tests exec it rather than re-implementing it.


## [0.96.0] - a post with something on it

The walker, cold run 9060, on a screenshot of the sidewalk beside
`office_stepped`: "no signs on the stop signs here anymore?" That turned out
to be two things with one word on them. Lot 0.73.0 measured the first and
closed it: the site has NO stop sign because none of its three junction legs
is stop-controlled -- `docs/STREET_RULES.md` working, not failing. The poles
in the photograph were `sign_post`, which `tools/new_species.py` minted as a
placeholder on 2026-09-12 and nobody had drawn: a 0.10 x 0.10 x 2.40 m
galvanised pole with nothing on it. That is the half this release is.

WHETHER IT MOVES THE DELIVERABLE. Not by itself, and not in the way the
metric counts: nobody's intervention-per-level number changes because a post
grew a sign. What it does close is a gap of the OTHER kind the repo file
names -- "works" and "good" are different gates, and this was a defect only
the second gate could see. No instrument in the toolchain reported it. A
person looked at a screen. That is the third of three, and the tally is
tracked as roadmap item 18.

### Three blades, and the standard each one is

`core/sign_blade_forms.py` plans the post and the blade in pure Python;
`recipes/sign_post.py` builds it with `bpylayer.prim_mesh`. The `form` is the
slot's dressing (`kit.DRESSING_FIELDS`), and Lot 0.73.0 already names one on
every post it stands.

| form | what it is | tris (pure = plan; built = in the GLB) | budget |
| --- | --- | --- | --- |
| `no_parking` | **MUTCD R8-3a**, the SYMBOLIC No Parking sign: a square white sign with a black border and a black P inside a red circle with a red slash through it (FHWA MUTCD, Figure 2B-17 long description). At a junction corner, where parking is prohibited within 30 ft of a signal or stop sign (75 Pa.C.S. 3353) | 272 pure, 368 built | 900 |
| `ped_crossing` | **MUTCD W11-2** Pedestrian warning -- a yellow diamond, black border, black walking figure -- over the **W16-7P** diagonal downward arrow plaque, which the Manual requires under a post-mounted W11-2 placed at the crossing point | 184 pure, 280 built | |
| `bus_stop` | the stop's flag: a 12 x 18 in vertical flag, BUS over STOP in white on a transit field. NOT a MUTCD sign -- no part of the Manual governs a transit agency's flag, so this is the one blade here that is a design rather than a standard | 576 pure, 672 built | |
| (none) | the bare u-channel, which is what the species was and what a slot with no form still gets | 36 pure, 132 built | |

The budget was set at 900 BEFORE the blades were planned, against
`club_fixture` (900) and `pennant_row` (900) rather than against `stop_sign`
(450), because a lettered flag was expected to be the expensive one and it
is: 516 of the bus stop's 576 are the seven glyphs. The two that carry a
PICTOGRAM cost a third of that. Every count is at every genome corner and a
test holds them there; zero coincident faces at `tools/coplanar_probe.py`'s
own defaults, measured on the built GLBs and not only in the pure port.

### The slot is the sign's size plus its mounting height

A sign's size and where it is mounted are the standard; the module's box is
what they add up to. That is arithmetic and it is written down twice --
`sign_blade_forms.MODULE_DIMS` here, `lot/site_furniture.BLADE_DIMS` there,
each pinned to literals by its own repo's test, because neither can import
the other.

    no_parking     0.3048 x 0.060 x 2.4384    12 in sign, bottom at 7 ft
    ped_crossing   1.0776 x 0.060 x 3.2112    30 in diamond over a 24 x 12
                                              plaque, bottoms at 7 ft and 5 ft
    bus_stop       0.3048 x 0.060 x 2.5908    12 x 18 in flag, bottom at 7 ft

Mounting is MUTCD Section 2A.18: 7 ft to the bottom of a major sign in a
business, commercial or residential area where parking or pedestrian
movements occur, 5 ft to a plaque under it. **A 30 x 30 in diamond is a 30 in
SQUARE stood on its point**, so it needs 30 * sqrt(2) = 42.43 in of box --
which is why the crossing sign is 1.08 m across and 3.21 m tall where the
parking sign is 0.30 by 2.44. A pedestrian crossing sign really is that much
bigger than a parking sign, and a street where the two came out the same size
is a street nobody looked at.

`SPECIES["sign_post"]`'s 0.10 x 0.10 x 2.40 was the PLACEHOLDER's box. Lot
now writes the blade's box as the slot and keeps the pole as the plan
footprint, the way `FOOTPRINT["traffic_signal"]` has kept an 8 m mast arm off
the sidewalk since 0.72.0 -- so no station moves and no census changes. Had
the slot stayed the pole's, `fit_exact` would have squeezed a 1.08 m diamond
to ten centimetres across: the same defect as no blade at all, and harder to
see.

### The landing order, which is the part that could have gone wrong

Three mirrors construct this name and none of them parses it. TWO OF THEM
ALREADY SPELLED `_f<form>`: `core/kit.module_stem` and
`deli_counter/themed_tscn.module_stem` have carried it since 0.84.0 and
needed no change for this at all -- checked, not assumed
(`resolve_themed_stem` on a sign-post slot returns
`prop_sign_post_delco_1997_01_w30_d6_h244_fno_parking` on Deli Counter 0.138.0
untouched). Only `lot.cover_module_stem` lacked it.

Lot 0.73.0 held it back on the argument that spelling it against a genome
listing no forms would resolve a name Zoo had not built. That was right and
it was half the picture: landing THIS release first breaks it the other way
round, because `plan_kit` then builds only the dressed name while Lot still
asks for the plain one. Either single-repo order sends every post on the site
to greybox -- which is worse than the bare pole it replaces.

So the order is not a sequence of safe steps, and pretending it is would be
the mistake. **Lot goes first, and it goes first carrying a fallback.** Lot
0.74.0's `cover_module_refs` asks for the dressed name and then the plain one
-- the ladder `deli_counter.themed_tscn.resolve_slot_choice` already climbs --
so against a Zoo that cannot draw the blade the post keeps the pole it has
today, and against this one it gets the sign. With that rung in, the window
between the two releases costs nothing and the order stops being load-bearing.
Measured end to end on `central_vault`, `septa_station` and
`warehouse_district` (12, 8 and 10 posts, all three blades between them): the
stems Zoo plans and the stems Lot resolves are the same list, with no species
fallbacks and no dressing fallbacks.

### Two defects the tests did not catch and a frame did

1. **EVERY BARE POST IN THE LIBRARY BUILT A NO PARKING SIGN.**
   `dna._default_params` takes a list param's FIRST entry as its canonical
   default -- which is why every other species with forms lists `auto` first,
   and `resolve_module_plan`'s own comment says so in as many words. The
   genome here listed the three blades and nothing else, so an undressed
   module took `no_parking` and drew a 12 in sign squeezed into a 0.1 m
   pole, under a stem that said `w10_d10_h240` with no `_f` on it. Sixty-five
   tests passed over it, because every one of them called `plan` directly;
   the preview frame showed it in one look. `auto` is first in the list now,
   it means NO BLADE here rather than "read the dims", and
   `test_an_undressed_post_is_still_a_bare_pole` goes through `dna`.
2. **A QUARTER OF THE POST WAS ZERO-AREA TRIANGLES.** Every `sign_post`
   style carries bevel 0.006, and a 6 mm bevel on an 8 mm u-channel flange
   collapses its corners: 32 of the post's 132 triangles came out degenerate
   on the no-parking module and 28 on the other two, drawing nothing on every
   client, every frame. Nothing counts them -- `prims.tri_count` counts the
   plan and not the bevel, and `build_module`'s own tally counts them as
   triangles. The only signal was `tools/coplanar_probe.py` reporting FEWER
   triangles than the GLB has, because it skips a degenerate normal, and that
   gap was noticed while writing the table above. `post_bevel` caps the bevel
   at a quarter of the thinnest section (2 mm); the post is still 132
   triangles and 0 of them are zero-area.

### The look, and what the cheap version costs

**The faces are geometry, not texture, and that was priced rather than
assumed.** A pictogram painted into an atlas is two triangles and this one is
128 (the ring) or 76 (the walking figure). What geometry buys back is no
image: a textured blade would add a unique PNG and a material per form, on a
prop a street carries a dozen of, and Zoo has no atlas that street furniture
already shares -- `_card_atlas`'s argument is that MANY quads share ONE
image, which is not the shape of this problem. `stop_sign` made the same call
for the same reason in 0.78.0. The expensive version is worth reopening when
there is runtime telemetry from a real session and a street-furniture atlas
to put it in; the budget it would free is about 200 triangles a post.

**No glyph was added to `recipes/_legend`, and that is the result rather than
an omission.** The set leaves out K M N V W X Y Z because a diagonal stroke
does not fit a three-by-five grid whose only cut is a stroke-square corner --
`_legend`'s docstring has said so since 0.82.0, and it is a decision, not a
gap. Drawing R8-3a instead of R7-1's NO PARKING ANY TIME and W11-2 instead of
a word keeps it one: sixteen letters become one glyph and none, and BUS STOP
spells out of the stop sign's own four glyphs plus the B and U the container
stencil added. A test asserts both halves, so the next person to want a
lettered blade finds the constraint rather than the workaround.

**A blade's borders and its legend gaps have a floor, and the floor is the
probe's own tolerance.** `border_of` will not draw a border thinner than
2 x 2 mm, because the border IS the perpendicular gap between the blade's rim
wall and the coloured field's -- at the genome's 0.09 m corner the plaque's
field stood 1.11 mm inside its blade and the probe reported the pair.
`min_width` is the same argument for the flag: `_legend` puts 0.08 of the
legend height between two letters, the legend is 0.26 of the flag's width, so
two letters meet the tolerance at 0.096 m and the floor is 0.097. Lot's flag
is 0.3048, three times over, and a test says so rather than leaving the floor
to be an excuse for not measuring.

### Left standing and named

  * **`stop_sign` has three coincident face pairs at nil separation**, and
    they are not new: `tools/coplanar_probe.py --species stop_sign --dims
    0.75 0.08 2.85` reports StopSign_Border against StopSign_Face over
    2,394 cm2 and 1,436 cm2, and StopSign_Border against StopSign_Post over
    177 cm2, all at 0.00 mm. `FACE_PROUD` puts the red face's BACK exactly on
    the white border's front, and the border's back exactly on the post's
    front. That is z-fighting on the face of every stop sign in the game and
    it predates the interior-species rules the new species keep. Not fixed
    here: it is a change to shipped geometry with its own frames to shoot,
    and folding it into this release would have made the residue after the
    next run unreadable.
  * **The W16-7P arrow points down and to the driver's left, and that is a
    choice this repo is making rather than reading.** The Manual's plaque
    comes in a left and a right; Lot's `BLADE_AT_PATH` says only that the
    post stands at a footpath cut. Down-left aims it at the carriageway the
    crossing runs across. When Lot passes the side, `_arrow` takes it.
  * **Nothing has walked one.** The frames are `tools/preview_specimen.py`
    against a ground plane and the 0.117 m ruler, not a site and not the
    shipped walk package. Four posts, four forms, built and looked at; a
    street of them is the next thing to see.

### Tests

`tests/test_sign_post.py` keeps its two original assertions and adds the
interior species' four measurements over every form at every genome corner
(clamped to each form's own `min_width`, because this genome spans a bare
pole at 0.09 m and a diamond at 1.08 m and its minimum is not a size every
form can be), plus the MUTCD arithmetic, the ranges Lot's dims have to sit
inside, the collider, the `auto` default through `dna`, the bevel cap, the
ladder of y offsets, and the stem both repos construct. Suite 2,194 passing,
204 skipped.

## [0.95.0] - a 1990s card shop, and a kind that reached no mesh

The walker, 2026-09-15, naming the next two building types and sending nine
photographs of the first: "a 90s Trader Card Shop (Fake Pokemon, Fake Magic,
Fake sports trading cards)". The photos are written up in the factory's
`docs/SET_DRESSING_REFERENCES.md` under "The walker's trading card shop
references"; this is the first slice of what that section says Zoo owes --
the four species that define the room, and the invented brand table every
one of them paints from.

This does not reduce interventions-per-level by itself. It is the walker's
next room, answered in the tool that owns the props, and until Deli Counter
writes the names at the end of this entry no generated shop gets any of it.
The half of it that might is the second section: a material kind that
reached no mesh and said nothing has now got a line that says so, which is
the third time that exact defect has shipped.

### Five species (planned in pure Python, built vertex for vertex)

| species | planner | what it is | tris (pure = built; no bevel) | budget |
| --- | --- | --- | --- | --- |
| `display_case` `flat` | `core/display_case_forms.py` | the shop's centrepiece: a glass-top, glass-front, aluminium-framed showcase counter -- toe kick, laminate deck, framed panes on mullions, two or three glass shelves, sliding doors on the staff side, and a register and towers of white card-storage boxes on top | 1,108 at DC's 2.4 x 0.6 x 1.0; 578 at 0.9 x 0.45 x 0.85 | 3,000 |
| `display_case` `L` | same | the same case turned at one end: ONE L-shaped glass top over two runs, the corner run glazed on two adjacent faces through a single corner column | 1,564 at 3.6 x 2.4 x 1.05, 1,600 at 6.0 x 3.0 x 1.25 | |
| `pack_wall` | `core/pack_wall_forms.py` | a gondola bay of booster displays in tight rows under a coloured header sign naming the game, on a `slatwall` back with a row of hanging blister packs | 706-720 a bay; 2,752 for a 4.8 m run of four, 4,896 at the genome's 8.0 m | 6,000 |
| `pennant_row` | `core/pennant_forms.py` | the strip of angled felt pennants along a wall top, overlapping, in the invented local clubs' colours | 892 at 6.0 x 0.10 x 0.35 -- the cap's own arithmetic, see below | 900 |
| `folding_table` `bare` / `cloth` | `core/folding_forms.py` `plan_table` | the play area's banquet table, on two splayed leg frames or under a black cloth to the floor, dressed with `_surface_stock`'s new `cards` flavour | 312-384 built with `cards` at 3.0 x 0.9 x 0.8; 108-132 of geometry | 600 |
| `folding_chair` | same, `plan_chair` | a moulded seat pan on four splayed legs, a raked back on two posts under a cap rail; a variant is one back panel or two slats | 180 (panel), 192 (slats) | 500 |

Recipes: `recipes/display_case.py`, `pack_wall.py`, `pennant_row.py`,
`folding_table.py`, `folding_chair.py`, and `recipes/_card_atlas.py` for the
two that carry art. Every planner keeps the interior species' rules -- exact
extents, parts overlapping by millimetres, no two faces within 2 mm of one
plane, deterministic -- and the tests hold them at every genome corner, both
forms and every variant. MEASURED in Blender on the built GLBs with
`tools/coplanar_probe.py`: 0 pairs on all five, at 2.0 mm.

**THE ROOM-LEVEL NUMBER, because a species budget is not a room.** One L
case, four pack-wall bays, one pennant row a wall, three tables and eight
chairs, every one at its WORST genome corner and worst variant:

    display_case L at 6.0 x 3.0 x 1.25        1,600
    pack wall, four bays in one 4.8 m module  2,808   (as four 1.2 m
                                                       modules: 2,880)
    pennant_row x4 at 14.0 m                  3,568
    folding_table x3 at 3.0 x 0.9, with stock 1,152
    folding_chair x8                          1,536
                                             ------
                                             10,664   (10,736)

For scale, one `cubicle_bank` is budgeted 24,000 and the club's `back_bar`
8,500. The densest thing in the room is the PENNANTS, at a third of it --
which is the opposite of where the cost was expected, and is the reason
their cap is derived from the budget rather than chosen (below).

### Where the cost was made to go away

  * **STOCK IS BOXES WITH A TEXTURE**, never modelled cards. A booster box
    is a box and its face is ONE QUAD carrying a tile out of the specimen's
    atlas; a pile of loose packs is one box; a graded slab is a box with a
    quad on top. `recipes/_card_atlas.py` joins every art quad of a module
    into ONE mesh with ONE material -- a display case stocked to its caps
    plans 78 of them, and as separate objects that is 78 draws of two
    triangles each on every client every frame.
  * **CAPPED BY COUNT, NOT BY FIT**, and the cap is load-bearing rather than
    decorative. MEASURED at `display_case`'s largest slot (6.0 x 3.0 x 1.25,
    form L): the caps lifted to 99 -- "as many as fit" -- draws 209 items
    and 3,434 triangles, which is 114 % of the budget; `CAPS` draws 78 and
    1,600. A test asserts that removing the cap BLOWS the budget, because a
    cap that is not the thing holding the number is a comment.
  * **AND THE FIRST CAPS WERE TOO TIGHT.** They drew 47 items and 1,166 --
    39 % of budget -- and were loosened, because the reference's shelves are
    FULL and a half-stocked case is the wrong kind of cheap. What a further
    raise buys is in `CAPS`: about 21 triangles an item.
  * **`pennant_row`'s cap is DERIVED from its budget**: `max_pennants` is
    `(budget - 12) // 20`, 20 being what a pennant costs (a triangular prism
    of 8 and a hoist band of 12, and a test asserts it still is). Raising
    the genome budget is the one dial that makes a strip denser, and nothing
    else has to move with it.
  * **The legs are rotated boxes, not tubes.** `prims.rod` at eight segments
    is 48 triangles a leg; a box is 12. A play area carries eight chairs and
    three tables, so that is 8 x 4 x 36 = 1,152 triangles of section nobody
    can see at play distance.

### What the cheap version loses, said rather than quietly narrowed

  * **A playmat is a colour with a printed border, not art.**
    `prim_mesh.build_stock` has no textured path -- the same limit
    `bar_dense` recorded for its bottle labels in 0.92.0 -- so the `cards`
    stock flavour is flat. The expensive version is one more atlas per host
    and about two triangles a mat; it is not built because nothing else in
    `_surface_stock` is textured and making one flavour the exception is how
    a rule stops being one.
  * **A card face carries no type at any size**, and a test asserts
    `card_art.card_face` never grows any. At `TEXEL` a card is 16 px.
  * **A pennant carries no type at all.** Its ink would be under two pixels,
    so it is a colour and a band, which is what a pennant at ceiling height
    reads as.
  * **The case's stock is invisible without a glass PACK.** Zoo does not
    decide opacity -- the pack does, through `import_hints.transparency`
    (`skins.SEE_THROUGH`) -- so on the flat fallback the shelves, the slabs
    and the tins are all behind an opaque pane. That is the pipeline's own
    division and not a defect here, but it means a card shop is only a card
    shop once delco_1997 ships a `glass` pack, and it is worth knowing
    before somebody looks at a frame and reports an empty case.
  * **`prims.rod` sections and a true folding-chair X frame** were not
    built, and the chair reads a little more dining-chair than folding
    chair as a result. 192 triangles against 500 says the budget was not
    what stopped it; the silhouette at play distance was judged good enough,
    and a frame of it is in this release's notes.

### `TEXEL` is 256, and the pixel face is why

REFUTED, kept: 160 px/m first, on the argument that nothing in a card shop
is read closely. It is not the reading distance that sets this, it is the
FACE. `pixel_type`'s glyphs trim to 11 rows at scale 1, so at 160 px/m a
0.18 m booster-box front had 29 rows to spend and could not carry its game's
name over its figure at all -- MEASURED on the contact sheet, 0 of 12
lettered. At 256 the same box is 46 rows and all twelve carry it, and the
atlas a whole pack wall needs is still one 303 x 259 PNG.

A second thing came out of the same sheet and is worth recording because it
was invisible in the code: the four card FRAMES the reference names --
monster, wizard, sci-fi, sport -- were drawn as three vertical tapers and a
figure, and all three tapers read as the SAME MOUND on a panel about as wide
as it is tall. The frame colour was carrying the entire difference. The
silhouettes are four families now (a horned lump, a robe under a tall cone,
a hull ACROSS the frame, a player over a colour chip), and the fix came from
looking at the picture rather than from reading the function.

### The brands: `core/card_brands.py`, `core/card_art.py`

TWELVE INVENTED GAMES in one table beside `brands.py`,
`cigarette_brands.py`, `liquor_brands.py` and `club_names.py`, because a box
on a pack wall, a sealed box in a case and a header over a bay must carry
the same game without a second list drifting from this one: JAWN BEASTS
("Collect the Whole Jawn."), WOODER WIGGLERS ("They Live in the Crick."),
SCRAPPLE HORRORS ("Nine Parts. No Questions."), HEXES & HOAGIES ("Cast It,
Hon."), NANA'S GRIMOIRE, BLUE ROUTE 2099 ("The Merge Never Ends."), ORBIT
ESSINGTON, DELCO DIAMOND LEAGUE ("Six Innings and a Hoagie."), PIKE GRIDIRON
'97, YOUSE VS. THEM, MACDADE MIDNIGHT and TINICUM TROOPERS. Six invented
printers (PIKE PRESS, WOODER WORKS, DELCO DECK CO., SCRAPPLE PRESS, NANA'S
ATTIC, HOAGIE MOUTH CARDS), sixteen invented local clubs for the pennants
and the sports cards, and six things a shop says on a hand-lettered sign.

A DENYLIST test holds every PAINTED string -- not the table, which is a
different set the moment somebody letters something new -- against the card
games, publishers, graders, leagues, clubs and players a writer reaches for:
whole words for the ones that are also English (SCORE, LEAF, CLASSIC, ULTRA,
PRO, UNION) and anywhere for the rest. THREE NAMES WERE CHANGED and the
module keeps them as the record: FOLSOM FLYERS became FOLSOM FLOUNDERS (the
denylist caught it); the monster game's first slogan was the national
monster game's own tagline with a Delco word stapled on; and MACDADE MYSTICS
became MACDADE MIDNIGHT, which the denylist did NOT catch -- a WNBA club
founded the year after this game is set, so no 1997 reader would have taken
it that way and every reader since would. A guard is a floor, not the
decision.

### `wood_panel` and `slatwall`, and a kind that reached no mesh

Pixelcoat 0.44.0 shipped `wood_panel_delco`, `slatwall_retail` and
`carpet_tournament`. Read through this repo by that release: `KNOWN_KINDS`
had neither `wood_panel` nor `slatwall`, and `dna.resolve_module_plan` keeps
a slot's material ONLY when it is listed there. A card shop asking for its
own panelling would have built whatever the genome defaulted to and said
nothing -- which is exactly what `carpet_club` did for a release after
Pixelcoat 0.42.0, and `tar`, `gravel` and `vegetation` before it.

Both kinds are in `skins.KNOWN_KINDS` and `materials.ROUGHNESS` now (the
vocabulary's two homes, and `test_kind_vocabulary` is what keeps them in
step). `wood_panel` is 0.52: a printed hardboard panel's sheen is its
factory lacquer's and not its grain's, so it sits beside `wood_stained`
(0.50) rather than bare `wood` (0.65). `slatwall` takes `laminate`'s 0.55
exactly -- it IS melamine-faced board, and it is a separate kind so it can
resolve its own pack, not because it reflects differently.
`carpet_tournament` needs no kind: a pack directory is `<kind>_<theme>`, so
it is `carpet` under a `tournament` theme.

**AND THE SILENCE IS GONE.** `kit.plan_kit` collects every slot material no
kind in the vocabulary matches, prints one loud line a kind, and returns
them as `unknown_materials`. The fallback STAYS -- older manifests carry
kinds this vocabulary never had and failing a building that is otherwise
fine would be worse -- so what changed is that a material reaching no mesh
no longer looks like success. It is the same shape as the STEM COLLISION
line beside it, and for the same reason.

Proven end to end rather than added to a list: `card_shop.slots.json` builds
a `wood_panel` wall and a `wood_panel` display case and two `slatwall` pack
walls, and the stems carry `_mwood_panel` and `_mslatwall`.

### `_surface_stock` flavour `cards`

The play table's dressing, and the seventh flavour: a playmat with a printed
border, stacks of cards, deck boxes and dice, planned once per SIDE of the
top so two players' worth face each other across it. `desk`, `table`,
`counter` and `filing_cabinet` take it too, as they take the other six.

A HALF-SIZE PLAYMAT, and it had to be. A full one is 0.61 x 0.356; two face
to face need 0.71 m; a folding table is 0.76 deep, and after the module's own
`EDGE` and the host's region inset the half a player gets is 0.318 m. So a
full mat NEVER fit and `_place_group` quietly drew card piles instead --
MEASURED as zero mats in the frame, which is how it was found, by rendering
the table and looking at it. It is 0.56 x 0.27 now, and 0.27 rather than 0.28
because the module turns every item off square by up to `JITTER_K / size`
degrees: 3.57 for a 0.56 m mat, which is 35 mm of depth the first arithmetic
had not counted. The mat is also 9 mm thick against a real 2, because this
module's rule is that no face of an item lands between the host's top and
`SINK` + 4 mm above it, and at a true thickness its top face sat 1.0 mm over
the table on every seed.

### What the probe found, and what it changed

`prims.coincident_pairs` at 2.2 mm over every genome corner, both forms and
every variant, was run before anything was believed, and it decided eleven
constants in this release. The ones worth carrying forward:

  * **A quad's offset must come from the item's OWN face**, not from the
    surface it stands on. A box that sinks `SINK` into a shelf has its top
    `SINK / 2` lower than that arithmetic assumes, so a 3.5 mm art offset
    measured 2.0 -- the tolerance exactly -- on every faced-out product.
  * **Two parts inset by the SAME number meet on every plane their other
    two ranges share.** On one 2.4 m pack wall that was 28 pairs from four
    collisions of one inset, and the fix is the `X_IN` / `Y_IN` ladders:
    every part has its own number and they step by `JOIN`.
  * **An L's glass top is THREE quads, not two.** Two quads cancel a shared
    side face only when they share the WHOLE edge; with two, one ring's
    short side lay inside the other's long one over the corner -- measured
    as `Top` against `Top`, 0.0096 m2, which is `TOP_T` times the case
    depth, the corner joint exactly.
  * **The outside corner of an L is a POST**, because two glazed faces'
    frames otherwise occupy the same square. Trimming both back to one
    column is also what an extruded showcase frame does. Its rails run one
    `JOIN` into that column and its panes two -- MEASURED the other way
    round first, and the two rails then reached past each other's 30 mm
    depth and met inside it, which is a worse pair for the same reason.
  * **A variant has to move geometry.** Four variants of a FLAT display case
    built three distinct shapes, because the variant turns an L's corner and
    a flat case has no corner to turn; four variants of a pennant row built
    ONE, because only its colours moved. The case's stock is nudged by
    variant now (clamped, so a nudge cannot push a box off the shelf it
    stands on -- which it did at 0.9 x 0.45, 1.9 mm from the shelf's end),
    and the pennant row phases its tilt.

### Tests

  * `tests/test_card_brands.py`, 11: the tables are well formed, every card
    frame is stocked, no painted string carries a real mark, the denylist
    can actually fire, the three changed names stayed changed, every painted
    string is spellable in the factory face, the atlas is deterministic and
    named from its own pixels, every tile kind paints and fills its box, all
    twelve box fronts are lettered at ship size, a card face is not, and the
    game and team orders rotate.
  * `tests/test_card_shop.py`, 55: each species discovered, validating and
    planning through the kit; 0 coincident pairs, exact slot fit, the
    triangle budget, and colliders inside bounds at every genome corner,
    form and variant; the variants are different modules; the plan is
    deterministic; the L is ONE case with one top mesh and one corner
    column, and its collision leaves the inside of the corner open; the
    stock cap is what holds the budget; a 4.8 m pack wall is four bays with
    four different games; the pennant cap is the budget's arithmetic and a
    pennant costs what that arithmetic assumes; overlapping pennants are
    never in one layer; the pennant row declares no collision and its genome
    agrees; and a playmat fits the half of a folding table it has to.
  * `tests/test_kind_vocabulary.py`: the two card-shop kinds are in both
    homes, and an unknown slot material is REPORTED rather than dropped in
    silence. Both fail on 0.94.0.
  * `test_genome.py`, `test_material_options_closed.py` and
    `test_theme_style_resolution.py` (75 species) name the five.
  * Host suite 2,130 passed / 203 skipped (0.94.0 in this worktree:
    2,027 / 198).

Built: `card_shop.slots.json` through `--build-kit`, nine modules, 0 failed,
every one PASS -- two display cases (flat and L, one in `wood_panel`), two
pack walls in `slatwall` (a 1.2 m bay and a 4.8 m run of four), a 6 m pennant
row, two folding tables with `cards` stock, a chair, and a `wood_panel` wall.
`tools/coplanar_probe.py` on the built GLBs: 0 pairs on all of them.
Frames shot with `tools/preview_specimen.py` (Blender 5.1.1, Cycles CPU) of
all five, plus the table with its stock.

### Not done

  * **Deli Counter writes none of these names yet**, so no generated shop
    gets any of it. The stems are at the end of this entry.
  * The rest of the reference's list is unbuilt: `slatwall` / `pegboard` as
    a species of its own, `booster_box_stack`, `framed_jersey`,
    `curio_cabinet`, and the hand-lettered banner over the back wall.
  * The `cards` flavour has no textured path (above), and no Pixelcoat
    `glass` pack exists for delco_1997, so a display case reads as an opaque
    box on the flat fallback.
  * NOT MEASURED: what any of this costs in a real frame. Every number here
    is triangles, which is what a budget is written in and is not the same
    thing as milliseconds on somebody else's machine. There is still no
    runtime telemetry from a real session, so the budgets are conservative
    on purpose and can be reopened when there is.

### The stems Deli Counter has to ask for

    prop_display_case_<theme>_<style:02d>_w<cm>_d<cm>_h<cm>[_f<flat|L>][_n<0..3>][_m<kind>]
    prop_pack_wall_<theme>_<style:02d>_w<cm>_d<cm>_h<cm>[_n<0..3>][_m<kind>]
    prop_pennant_row_<theme>_<style:02d>_w<cm>_d<cm>_h<cm>[_n<0..3>][_m<kind>]
    prop_folding_table_<theme>_<style:02d>_w<cm>_d<cm>_h<cm>[_f<bare|cloth>][_s<cards>][_n<0..1>][_m<kind>]
    prop_folding_chair_<theme>_<style:02d>_w<cm>_d<cm>_h<cm>[_n<0..1>][_m<kind>]

built by `card_shop_probe` at delco_1997 style 01:

    prop_display_case_delco_1997_01_w240_d60_h100_fflat_n2
    prop_display_case_delco_1997_01_w360_d240_h105_fL_n1_mwood_panel
    prop_pack_wall_delco_1997_01_w120_d50_h240_n3_mslatwall
    prop_pack_wall_delco_1997_01_w480_d50_h240_n1_mslatwall
    prop_pennant_row_delco_1997_01_w600_d10_h35_n2
    prop_folding_table_delco_1997_01_w180_d76_h74_fcloth_scards_n1
    prop_folding_table_delco_1997_01_w180_d76_h74_fbare_scards
    prop_folding_chair_delco_1997_01_w46_d50_h85_n1

## [0.94.0] - the porthole is a lamp, not a sun, and the club's light has hardware

The walker, 2026-09-16, walking cold run 9060 with two frames of the strip
club. Standing 4.15 m from `back_bar_r1d196568_2`: "we can soften/diffuse
this back bar light a bit. it looks like a sun, we just want a soft glow".
And on the main floor, a warm pool and a matching wash on the ceiling above
it, both circled: "awesome lighting in the strip club, but it doesn't look
like that light is coming out of any viewable light fixtures".

Both are this release's. The spill half of the first is Lux 0.40.0's, and the
two were measured together on the same walk; Level Factory 0.90.0 grew an
instrument for the second so it cannot go three releases unseen again.

This does not reduce interventions-per-level. It is a look defect a person
found by playing the level, fixed in the tools that own the geometry -- and
the second half of it shipped an instrument, which is the part that might.

### The porthole: `core/back_bar_art.py`, `core/back_bar_forms.py`

0.92.0 built the niche's lit face as one flat emissive n-gon: 16 segments,
colour (1.0, 0.78, 0.52) linear at strength 1.6. MEASURED at the walker's own
station (Heavy Rain, Godot 4.7, GL Compatibility, RTX 2060, 1600 x 900,
`tools/look_shots.py`), the 0.74 m disc:

    mean luma 200.8, 1.330% of it pinned at 250 or more, channel peak 255,
    and its brightest pixels reading (250, 250, 250) -- WHITE, with the
    tungsten gone.

ATTRIBUTED BEFORE IT WAS PATCHED, because two things light that disc. Killing
Lux's back-bar omni alone, same scene, same station, took the same patch to
mean 121.5 with nothing above 239 -- so the omni owned the clipping and the
FLAT EMISSIVE owned a hard white 239 disc on its own. That second half is
this file's, and no change to the spill would have fixed it.

`back_bar_art.paint_niche` paints the lit face instead: a 64 px square raster,
the colour held flat over the inner 18% of the radius and smoothstepped to
zero at the rim of the inscribed circle. The falloff is applied in LINEAR
light and encoded to sRGB afterwards (`_srgb_byte`) -- fading the bytes would
hold the mid-tones up and draw the disc edge this exists to dissolve -- and
the encode is also what makes the texture decode back to the same linear
colour the glTF `emissiveFactor` used to carry. `niche_art` names the image
from its own pixels, the way `label_atlas` does, so the same colour gives the
same bytes and the same material name in every build.

The disc carries UVs now (`_disc`), mapping its BOUNDING SQUARE onto that
raster so the inscribed circle is exactly the geometry and the raster's
corners fall off the mesh. The recipe builds it through `_uv_object` with
`materials.make_backlit_material` -- backlit rather than plain emissive, so
the face is dimmed as albedo too (`NICHE_ALBEDO` 0.22): a lamp behind glass
is not a mirror of the room, and a porthole with the power cut is a dark
glass hole in a dark cabinet. The name keeps the `_Face` suffix, so Lux's
power cut still takes it.

Three numbers came down with it, and none may drift back without a frame:

  * `NICHE_STRENGTH` 1.6 -> 1.2, and it is the PEAK of a gradient now rather
    than the value of a flat face. 1.2 x the preset's 0.95 exposure sits just
    over Heavy Rain's 1.1 glow threshold, so the core alone blooms and the
    rest of the disc does not -- a glow with an edge to it.
  * `BULB_STRENGTH` 2.0 -> 1.5. A pygmy lamp may be the brightest thing on
    the shelf; it may not be WHITE, and at 2.0 the brightest channel and the
    dimmest both landed on the dither's 239 step. It is a 4.4 cm sphere
    either way.
  * `NICHE_SEGMENTS` 16 -> 32. 16 put a visible facet every 22.5 degrees
    round a 0.74 m disc read at 4 m. Belt and braces now that the rim is
    black; 16 more triangles against a unit that already carries 8,100.

In the frame, control -> 0.94.0 + Lux 0.40.0 (the two are not separable in a
picture): the disc goes mean 200.8 -> 114.8, peak (250,255,255) ->
(234,228,228), and the share of it pinned at 250 or more goes 1.330% -> 0.000%.
The whole frame keeps 25 pixels at 250+ where it had 123. The bottles in
front of it go 54.6 -> 84.4.

### `club_fixture`: `core/club_fixture_forms.py`, the genome, the recipe

Lux 0.37.0 wrote the club set -- `club_wash`, `stage_light`, `neon`,
`room_ambient`, and 0.39.0's `back_bar` -- with "no hardware and no marker
today" in its own docstring, while every older anchor type has had a Zoo
fixture at it since v0.28. Two of the five are a LAMP and can have one; the
other three already do or cannot, and `FIXTURES` now says which is which
instead of reporting all five as "no fixture species for this type":

  * `neon` IS its sign, and `sign_box` builds it;
  * `back_bar` is the bar's own bulbs and porthole, built above;
  * `room_ambient` is a ReflectionProbe with nothing to hang.

FORM `can` -- a surface-mounted downlight for a `club_wash`: a trim collar, a
barrel, a dark cast baffle in the mouth and a lit disc seated in the throat.
FORM `par` -- a PAR can for a `stage_light`: a wider barrel, a yoke of two
arms and a clamp, four barn doors round the mouth, and a lit lens.

THE LENS WEARS THE POOL'S OWN COLOUR. `GEL` is a second copy of Lux's
`CLUB_PALETTE`, and being a second copy it is a contract: the names are
Lux's, the values are the palette's own sRGB multipliers, and an unknown name
falls back to a warm lamp rather than guessing -- a club still builds, one
lens is tungsten where it should have been chartreuse, and no build fails
over it. A white-hot lens under a magenta pool is the disagreement the walker
photographed, so the copy earns its keep.

A PAR CAN POINTS AT ITS TARGET. `rot_y` on a `stage_light` is the ROW's axis,
not the barrel's; the anchor carries a `target`, and `tilt_for` derives the
bearing and the tilt off plumb from it, per lamp point. This is only sound
because Zoo builds from the PER-BUILDING manifest, where `pos` and `target`
are in one frame: Lot's merge transforms `pos` and copies `target` verbatim,
which is the defect Lux 0.40.0 now refuses a light over. A target at or above
the fixture clamps to 90 degrees rather than swinging the barrel over the
top -- a stage light that has to aim up is a manifest error, and clamping
says so without refusing the build.

### Two things in `core/fixtures.py` and `bpylayer/build.py` that are not the club

`marker: False` on a FIXTURES row. Every row before this emits a `LuxEmit`
empty and `LuxFixtureSpawner` puts the lamp there, which is how lights ship.
The club rows must not: the spawner hands `LuxLightLoader.rig_for_anchor`
only {type, id, drop}, so a wash would lose its zone colour and pool radius
and take a hash pick instead, and a stage light would lose its target and be
refused outright. Their light stays on the manifest bake, which has the whole
anchor -- and a marker here would DOUBLE every club light rather than replace
it. `markerless_fixtures` is written into the index and `emitter_markers` is
no longer a copy of `fixtures_built`: measured on the shipped club, 25
fixtures and 18 markers.

Mount `hang`: body below the emitter with its TOP at it, and unlike `below`
it does not stretch the fixture to grade. THE FIRST BUILD USED `above` AND IT
WAS WRONG -- a club anchor's `pos` IS the ceiling plane, so bottom-at-the-
emitter put the whole can inside the slab and left its lens recessed in a
throat nobody on the floor can see. Caught by shooting the walker's own
station and LOOKING at it: two par cans visible, five wash cans not. The same
frame set `LENS_SEAT`, which moved the lit disc from the top of the baffle to
under half of it so the disc is in view from about 60 degrees off the axis.

A placement may also carry `params` (the can's form) and a `tilt_deg`, and
`build_fixtures` composes the mount as `T(pos) @ Rz @ Ry(-tilt) @ T(lift)` so
a fixture that aims tilts about its MOUNTED POINT. At tilt 0 that is the line
it replaces to the bit, so every fixture built before this lands where it did.

### Tests
- `tests/test_back_bar.py`: the diffuser's core, rim, monotone falloff and
  stable name; the disc's uvs on its own bounding square; both strengths held
  under what clipped. All fail on 0.92.0.
- `tests/test_fixtures.py`: the two new rows build, the forms they take, the
  mount, the absent marker, the par's bearing and tilt from its target, the
  no-target and aim-up cases, the gel and its fallback, and the three club
  types whose hardware is built elsewhere saying so.
- `tests/test_genome.py` and `tests/test_theme_style_resolution.py`: 70
  species.
- Host suite 2013 passed / 193 skipped; in-Blender suite (Blender 5.1.1)
  2178 passed / 28 skipped.

### Not done
- The can is a black cylinder from across a dark room, because a can is not
  lit by its own lamp and nothing else in the club lights the ceiling. It
  reads as hardware over a pool, which is what was asked for; making it read
  as a fixture from every angle is a lighting question, not a geometry one.
- The `can`'s lit disc is `LENS_SEAT` x the baffle up its throat and Lux
  hangs a club wash's lamp 0.25 m below the anchor, so the lamp is a hand's
  width under the mouth rather than at the disc. That is the same offset the
  fluorescent troffer has carried since v0.28, and the co-location gate's
  0.25 m tolerance is written for it.

## [0.93.0] - a cubicle bank, which is not a desk

The walker, cold run 9060, standing 2.68 m from `office_stepped`'s
`cubicles_w_0_col`: "these desks are too close to each other?" -- a raft of
desk tops butted edge to edge with no aisle, filling a rectangle.

He was looking at a desk, and the desk was right. Ten volumes in Deli
Counter's 132-spec library carry `cubicle` in their name -- `cubicles_w_0`
through `cubicles_e_2` in `office` and `office_stepped`, every one
8.0 x 6.0 x 1.2 m, every one `drywall` -- and `prop_species` routed all ten
to `desk`. The desk genome takes width to 12.0 and depth to 6.0 (opened in
0.84.0 for exactly these, whose notes call them "a cubicle block, rows of
desks back to back"), so the slot FIT. It did not fall back to a box: it
built as desk geometry at 8 x 6 m -- four 8 m work surfaces, one per
`row_max` row, butted along the depth. Which is a raft.

A cubicle bank is not a desk. It is rows of workstations inside partition
screens with an AISLE between the rows, and the aisle is the whole point.

### `cubicle_bank`: `core/cubicle_forms.py`, `recipes/cubicle_bank.py`

Minted by `tools/new_species.py` from `desk` and shaped the same day.
Reference in the genome's licence notes: a 1990s panel system (Herman Miller
Action Office, Steelcase 9000) -- fabric-faced acoustic screens on levelling
feet, a painted frame with a top trim cap, work surfaces cantilevered off
the panel rails, a drawer pedestal under each, an overhead binder bin where
the panel reaches over one.

BANDS along the depth, BAYS along the width. Two pod bands back to back with
an aisle between them when the depth carries both -- `row_min` 1.7 for a
band (a spine screen, a 0.75 m surface and a knee) plus `aisle_min` for the
gap -- and one band filling the depth when it does not. A band is capped at
`row_max` 2.4 and every surplus metre goes to the aisle, because a 3 m deep
cubicle is not a thing and a wide aisle is. The library's 8.0 x 6.0 slot
therefore builds two 2.4 m bands and a 1.2 m aisle. Bays come from `_bays`
at `bay_max` 2.0: four 2.0 m workstations across 8 m, equal and never a
sliver. A cross screen stands on every bay boundary and both ends, running
`CROSS_F` 0.62 of the band's depth inward from the spine -- the pod is open
to the aisle, which is what a cubicle is.

`aisle_min` 1.1 IS DERIVED, not chosen: it is Deli Counter's
`agent_contract.clearances.min_corridor_width_m`, read 2026-09-16, itself
`2 * nav_bake.agent_radius_m (0.4) + 0.3` body margin. So a bank wide enough
for two bands carries an aisle this pipeline's own body fits down, and one
that is not stays a single band rather than shipping an aisle nobody can
use. The spine screens stand on the bank's own outer edges at every depth,
so the built bounds are the slot's exactly -- which `validate.fit_*`
measures to 2 cm and `core.pivot` re-centres from.

THE SCREENS ARE CLOTH WHATEVER THE SLOT SAYS. `dna.UPHOLSTERED` gains
`cubicle_bank: "cloth"`. All ten library volumes are authored `drywall` --
the building's own partition surface -- and the screens are the bank's
entire mass, so without that row a cubicle farm would be a lump of wall
standing in a room made of the same wall. The slot's kind names the FRAME,
exactly as `wood` on a sofa names its legs. delco_1997 dresses `cloth` as
`linen_neutral`. The frame, caps, feet, rails, handles and bins are
`metal_painted` and the work surfaces, pedestals and drawer fronts
`laminate`: the species' own palette, because those are what make it read as
a cubicle rather than as whatever the slot happened to say.

COLLISION IS PER PART. Spine and cross screens, work surfaces, pedestals and
bins declare their own -- 28 boxes on the library's slot -- and drawer
fronts, handles, rails, caps and levelling feet declare none, each sitting
inside or under something that already does. The aisle and the knee space
under every surface declare nothing at all. Deli Counter 0.138.0's half of
this is that its greybox stops drawing the volume's convex box, which was
the only thing a body ever met.

EVERY SCREEN IS SHADED FLAT (`smooth_angle=1.0`). A spine is the slot's full
width -- 8 m on every one of the library's banks -- and `bm_to_object`'s own
docstring records what the default crease does to a panel that size: the
chamfer is smoothed into the face, a box face has no interior vertices to
hold the middle flat, and the panel shades as a dome with a diagonal wedge
across it. That is the defect `wall_delco_01_w200` was measured with, and a
cubicle screen is a wall panel by every dimension that matters here.

VARIANTS AND STOCK. `module_variants` 4: which end of a bay the pedestal
takes, how many drawers it has, and which bays carry a bin where one fits.
`stock` defaults to `office`, so `_surface_stock`'s monitors, paperwork and
phones stand on every work surface facing that band's sitter -- a cubicle
with nothing on the desk is not one.

BINS ARE A HEIGHT, NOT A TOGGLE. A binder bin needs a panel that reaches
over it (`BIN_Z + BIN_H` = 1.34), so the library's 1.2 m banks have none and
a 1.7 m one does. That is the reference's own rule.

### Tests

`tests/test_cubicle_bank.py`, 12, pure: the species is discovered and
validates; it plans at the dims all ten library volumes are authored at; the
library slot carries a 1.2 m aisle; the bands fill the slot depth exactly at
nine depths from 1.6 to 12.0; a depth below 4.5 gets one band rather than an
aisle a body does not fit down; the screens resolve to cloth from a
`drywall` slot; four bays, none a sliver; no bin at 1.2 m and one at 1.7;
the built plan fills the slot box exactly; NOTHING the species builds stands
in the aisle; the collision it declares is 28 per-part boxes of four kinds
and none of them in the aisle; and the four variants are four different
banks.

## [0.92.0] - the club's back bar, lit, and a bar top with something on it

The walker, 2026-09-15, with three photos of a lounge bar and the
bartender's side of one: "in the strip club there should be a bar with lots
of bottles like this". THE CLUB'S BAR, NOT THE DIVE BAR -- the same day:
"this will be different from the dive bar species we make later" -- so the
species is parameterised by FORM and by STYLE, and nothing here is the
neighbourhood dive's. The brief is written up in the factory's
`docs/SET_DRESSING_REFERENCES.md` under "The walker's club bar reference";
Deli Counter 0.137.0 places all of it and Lux 0.39.0 lights it.

This does not reduce interventions-per-level by itself. It is the walker's
next look at a club, answered in the tool that owns the prop -- and one
piece of it is more than dressing: a back bar only makes sense with a
working aisle behind the counter, which is Deli Counter's half.

### `back_bar`: `core/back_bar_forms.py`, `core/back_bar_art.py`

The lit wall unit behind a bar. A recessed plinth, a lower CABINET RUN at
counter height with two doors and a brass handle to a bay and a worktop
carrying the working bottles and a tower of rocks glasses; above it TIERED
GLASS SHELVES crowded with bottles in rows and stemware on the top tier,
each shelf with a brass edge rail; PILASTERS dividing an ODD number of bays
(odd because the reference's mirror and porthole are in the CENTRE bay, and
an even run has no centre bay); a cornice over them.

FORMS `straight` (a mirror in the centre bay) and `niche` (a round lit
porthole -- the first photo's), `auto` taking the porthole wherever the
centre bay can hold one. A VARIANT is another rotation of the liquor table
across the shelves, another stage of label wear, and the worktop's towers
and bottles swapped bay for bay.

WARM BULBS BEHIND THE SHELVES, one to a bay to a tier -- 1997, so bulbs and
not an LED strip: small emissive spheres at the back panel under each shelf,
`M_BackBar_bulb_Face`, and the porthole's disc `M_BackBar_niche_Face`. The
`_Face` suffix is what Lux's emissive binder cuts with the room's power, so
a club that loses its power loses its back bar with it. A lit material
lights nothing round it under GL Compatibility; the spill is Lux 0.39.0's
`back_bar` anchor, which Deli Counter writes at each unit.

BOTTLES ARE SIZED TO THE SHELF, not pinned: the tier pitch is the shelf
zone over the tiers plus one (the top tier needs headroom too) and a bottle
is `pitch - BOTTLE_HEADROOM`, held to 0.16-0.34 m. A pinned 0.30 m bottle is
right at one unit height and through the shelf above at another, and every
back bar in the library is a different height.

THE PITCH IS THE BUDGET'S once the budget bites. A 6.0 x 3.0 m unit has 18 m
of bottle shelf, which at the row pitch is 171 bottles and 16,876 triangles
-- nearly twice the heaviest thing in the genome. `MAX_BOTTLES` and
`MAX_STEMS` multiply the pitch instead, so a wide unit thins its rows:
measured over 80 builds (ten sizes, both forms, four variants),
1,892-8,112 triangles against a budget of 8,500.

NO TWO FACES SHARE A PLANE, and this species had to be taught that in four
places at once -- the first plan measured 18 coincident pairs on ONE size:

  * parts that MEET overlap by `JOIN`, never butt;
  * things that STAND on a surface sink `SINK` into it, as `_surface_stock`
    does;
  * parts reaching the same wall or the same end are STEPPED (`BACK_INSET`,
    `SIDE_INSET`). Two parts flush to one plane are coplanar with each
    other however carefully each is joined to its neighbours, and
    overlapping by `JOIN` leaves their SIDE faces sharing a plane over
    exactly that overlap -- the cabinet and its worktop are both `w` wide.
  * and where a plane is parallel to another BY CONSTRUCTION -- a
    pilaster's face and a shelf's row of label quads -- the distance is
    DERIVED (`PILASTER_CLEAR`) and not chosen. A chosen 0.6 of the shelf's
    depth put the two within 1.5 mm at two of the nine sizes then measured;
    a fixed pair of fractions has sizes where they meet, and the sweep
    finds them one size at a time.

`tests/test_back_bar.py` runs `prims.coincident_pairs` at 2.2 mm over ten
sizes, both forms and four variants: zero pairs, and the extents are exactly
the slot's.

A LABEL IS ONE QUAD and its plane is parallel to nothing: the bottles are
hexagonal prisms drawn with `phase = pi / 6`, which puts a VERTEX toward the
room and every facet at 30 degrees or more off the label's plane. With a
facet facing the room instead, it sat 2 mm behind the quad -- inside the
probe's window.

### The labels: `core/liquor_brands.py`, painted

One atlas a unit, 96 x 128 px a label -- about 0.78 mm a pixel on the glass,
so the 13-row Pixel Operator face at scale 1 stands 10 mm and is legible at
1.5 m, which is the walker's frame for the shelves. Ground, foil bands, the
mark at the largest whole scale that fits, a rule, the slogan wrapped, the
proof on the bottom band, and deterministic grime by variant.

FOURTEEN INVENTED BRANDS in one table beside `brands.py` and
`cigarette_brands.py`, because a bottle on a shelf, a bottle in a speed rail
and a bottle on a counter must be able to carry the same label: MACDADE GOLD
("Aged Since Last Tuesday"), WOODER SHINE ("Cut With Wooder. Allegedly."),
JAWN ROYALE, YOUSE FIRST ("Youse First. No, Youse."), CHESTER CREEK RYE
("Straight. Mostly."), HOAGIE MOUTH, NANA'S CORDIAL ("Two Fingers and a
Nap."), PIKE SILVER ("Worm Sold Separately."), RIDLEY DARK, TINICUM TRIPLE
SEC ("Orange-ish."), BOOTHWYN BARREL ("Barrel Aged in a Basement."), CRUM
CREEK CREAM ("Curdles With Attitude."), DELCO DEVIL ("Burns Twice. Sorry.")
and ESSINGTON EEL ("Tastes Like the Airport Smells."). A denylist test holds
every PAINTED string -- not the table, which is a different set the moment
somebody adds a word to the art -- against the national spirits, the
Pennsylvania distillers a Delco bar would actually stock (Rittenhouse, Dad's
Hat, Bluecoat, Kinsey, Publicker), the brewers and the local marks. Two
candidates were cut while writing it and are kept in the module as the
record.

THE BLOCK FITS ITS BOX, and each line fitting the WIDTH is not that:
CHESTER CREEK RYE takes three lines at scales 1, 2 and 3 -- every one inside
the margins -- and stood 62 rows in a 56-row box, running "RYE" through
"STRAIGHT. MOSTLY.". The tallest line gives up a step until the block fits.
A slogan that will not wrap into the space under the mark RAISES rather than
truncating: five of the fourteen were being cut mid-word at the first
`LOGO_BOTTOM`.

### `bar_dense`: the club bar's TOP (`recipes/_surface_stock.py`)

LANES, not clusters, and that is why it is a new flavour rather than a
denser `bar`. The reference is a liquor row along the WHOLE top with towers
of rocks glasses and cocktail glasses among it and a speed rail of spouted
bottles on the service run; a cluster planner cannot draw a row, and making
`bar` dense would have moved every cocktail table and stage rail in the
library, which the same photo is not about. `bar` is untouched.

Three lanes from the SERVICE side (+Y -- a counter's top overhangs the
customer side): the speed rail, the liquor row, and the glass lane nearest
the customer, plus a magnum standing forward of the rows where there is
room. A top too shallow for all three keeps the ones that fit. A REAL SPEED
RAIL HANGS UNDER THE COUNTER'S SERVICE LIP; this planner owns the top and
nothing else, so the rail stands on the service edge of it -- the bottles,
the spouts and the reach are the photo's, the shelf they sit on is not.

`DENSE_MAX_ITEMS` multiplies every pitch once the run is long enough to
blow it: measured before, a 4.0 m bay drew 96 items and 8,176 triangles, six
times what `bar` puts on the same top; after, 72 items and 5,132 at 4.0 m
and 78 and 6,124 at 8.0 m. A LABEL is a coloured ring 4 mm proud of the
glass in the brand's own ground colour -- flush, its facets lay in the
bottle's -- and the words are not painted here: `prim_mesh.build_stock` has
no textured path and a 60 mm label read across a bar is a colour. The back
bar's own labels are painted, and they are the ones a player reads.

The four hosts (`desk`, `table`, `counter`, `filing_cabinet`) all offer the
flavour, as they offer the other five.

### `counter` form `bar`: the bartender's side

A brass FOOT RAIL on posts along the customer front, BEER TAP TOWERS with
two handles each along the service edge, and a 1997 REGISTER at each
`ATT_register` station. PARTS, not stock, and the difference is what each
one is: stock is what is left out on a top and is jittered off square by
`_surface_stock`'s own rule, while a foot rail is a continuous straight tube
bolted to the front and a tap tower is plumbed at a fixed pitch. A jittered
foot rail is not a foot rail.

The rail lives INSIDE the slot, under the top's customer overhang where a
real one is; the taps and the register are returned as `dressing_objects`,
so they stand ON the top without moving the module's fit bounds -- the same
rule that lets a monitor stand on a desk without failing `fit_height`. A TAP
TOWER DOES NOT STAND ON THE TILL: the registers are placed first and a tap
whose column falls inside one is skipped. Measured the other way round, the
third tap of a 4.0 x 0.8 counter landed inside the register and the two
shared their base plane. 128 triangles inside the slot and 372 above it;
BUDGET 1600 -> 7000 for the dense top the club's counters now carry.

`auto` and `straight` build exactly what this recipe always built, and a
counter without the form or the flavour is byte for byte what it was.

### Where the counter's fit-out lives

In `core/back_bar_forms.counter_fitout`, not in `recipes/counter.py` where
it was first written: the recipe imports `bpy` at module scope, so a test of
it cannot run in the suite that runs without Blender -- which is the suite
that measures whether a foot rail is inside its slot. Moving it exposed a
second thing worth writing down: the counter's own `FORMS` tuple came with
it and rebound this module's, so `back_bar.plan` refused every `niche` it
was asked for and quietly built a mirror. The centre-bay test in the same
run caught it, which is the only reason it is a footnote and not a frame.

## [0.91.0] - a dartboard with the game in chalk, and a cigarette machine by the door

The walker, 2026-09-15, with two photos: "we also need dart boards in the
strip clubs. The kind where you use chalk to keep your score". And, with
three more: "we need retro cigarettes' machines in the strip club. (Maybe
we'll put em in other buildings too, it was the 1990s where smoking in
public was still legal in PA)". Two species, planned and painted in pure
Python, built vertex for vertex. Deli Counter 0.136.0 places them.

This does not reduce interventions-per-level by itself: it is the walker's
next look at a club, answered in the tool that owns the prop.

### `dartboard`: `core/dartboard_forms.py`, `core/dartboard_art.py`

The bar's wall cabinet. Top and bottom boards overhanging the sides, a back
panel, a lip inside the opening; teal felt; a 40-sided bristle board 451 mm
across with a steel number ring standing 3 mm proud; two doors on brass
hinge knuckles, their top edges one gentle arch; a chalkboard panel inset on
each door's inside, with a dart rail and three darts (point, barrel, shaft,
crossed flights) along its bottom when the doors are open; a tray under the
cabinet standing out past the doors, with two or three sticks of chalk and
an eraser.

FORMS `open` (the default, and `auto` at 0.9 m wide or more) and `closed`.
THE SLOT IS THE OPEN FOOTPRINT: the doors' free edges are the slot's sides
and front. `solve` picks the cabinet's width, its depth and the doors' angle
that fill it -- a variant's preferred angle as the tiebreak, then Newton on
the measured bounds -- and `prims.fit_exact` takes the rest: under 0.5 % on
every axis at every corner of each form's range (`FORM_RANGES`; the genome
is their union) and at Deli Counter's two sizes, where it takes nothing. At
1.1 x 0.36 x 0.9 the doors stand 128-130 degrees open on a 0.64-0.65 m
cabinet. REFUTED FIRST, kept here: a search over the cabinet's width alone
left corners of the first range 1.5-9 % off in depth and width; open at 0.95 x 0.28 cannot be
filled by any cabinet 0.56 m or wider, and the range starts at 1.0 x 0.30.

THE BULL IS THE SLOT'S CENTRE HEIGHT, by construction: the arch rises over
the cabinet exactly as far as the tray drops under it (`MARGIN_FRAC` of the
slot's height), so a consumer hangs a regulation board by lifting the slot's
centre to 1.73 m. `ATT_bull` marks it. COLLISION IS THE CABINET BOX ONLY --
the doors, tray and darts are visual; a body is stopped by the cabinet on
the wall, not by a door in mid-air.

THE BOARD is a 400 px raster at the regulation radii (bull 6.35, outer bull
15.9, trebles 99-107, doubles 162-170, edge 225.5 mm) in the regulation
order from 20 clockwise; black and cream singles, red trebles and doubles on
a black sector and green on a cream one; a one-pixel silver spider; the
numbers upright in the black band; the brand along the bottom of the rim;
radial sisal grain; and pocks where a bar throws -- treble 20, the singles
beside it, the bull, treble 19 -- with the sisal greying round them on the
later variants. THE CHALK is both doors' panels on one raster, 512 px/m: a
painted frame, the brand and its tag, HOME / AWAY (even variants) or 01 /
01, boxed numbers 20 to 15 and a bull; and a game in chalk, drawn from the
variant (`CHALK_STAGES`): `wiped` (ghosts of old games, smudges),
`first_rounds` (a few slashes), `mid_game` (slashes, X's, circled closes,
points in the margin, "x2") and `late_game` (many numbers closed, the
scores run up, two erased patches). Chalk is grainy, broken and hand-
jittered; paint is solid. The two doors keep different games.

A VARIANT is a different board: another brand (`brand_order` of the stem
without `_n`, so a slot's four variants are four brands), another stage of
the game, stained wood (`wood_stained`) or black paint (`metal_painted`),
other flights, and 0-2 darts stuck in the board instead of on the rails
(always six in all; none when closed -- a dart in the board keeps the doors
from shutting).

THE BRANDS ARE INVENTED (`dartboard_art.BRANDS`): DOUBLE DELCO / BRISTLE,
MACDADE BRISTLE / CO., THE JAWNBOARD / PRO, YOUSE THROW / LIKE MY NAN,
BALTIMORE PIKE PRO / TOURNAMENT, WOODER ICE HOUSE / LEAGUE. A denylist test
holds every painted string against the dart makers a writer reaches for
(Harrows, Winmau, Unicorn, Bottelsen, Nodor, Target, Viper, Arachnid, Halex,
Red Dragon, ...), their product lines, and the local brands and teams.

The painted faces are a new `materials.make_painted_material`: the image as
Base Color at full strength, nearest filter, clamped, its own roughness, no
emission. `make_backlit_material` at strength 0 was not used for it -- it
dims the art to 0.35 and sets roughness 0.35, a backlit panel's numbers.
1,416-1,440 tris (open), 912 (closed), against 2,000.

### `cigarette_machine`: `core/cigarette_forms.py`, `core/cigarette_brands.py`

The floor-standing pull-knob machine of the 1970s-1990s. A near-black body
on four splayed black legs with pads; woodgrain (`wood_stained`) side panels
standing 4 mm proud of the front; a chrome top cap with a brass strip and a
round key lock; the chrome FRAME, one closed solid over a cell grid (the
vending machine's door) with the display and the delivery tray cut through
it; the DISPLAY insert behind it; two chrome knob shelves with a PULL KNOB
per pack column -- shaft and cap, real geometry, chrome or amber by variant;
a coin plate with its slot, a return plate with its button and mouth; the
tray's drawer front and handle. The knob caps are the slot's front, the
splayed pads its sides and the rear pads its back: exact, `fit_exact`
taking nothing at Deli Counter's sizes and the genome's corners. Collision
is the cabinet box.

THE DISPLAY is one raster at 700 px/m: the HEADER ad (the brand's gradient,
a big pack, the logo, the slogan, a taped price card "$3.50 / QUARTERS
ONLY", and the Surgeon General's warning sticker -- the statutory text, not
a mark), two ROWS of packs faced out, one pack a knob, over black backing or
cream display cards with black notches (variants 1 and 2), each over a strip
"SALES OF CIGARETTES TO MINORS ARE FORBIDDEN BY LAW"; between the rows a
second brand's ad (form `pull_knob`, the default) or the black panel that
says CIGARETTES (form `pull_knob_split`). REFUTED FIRST, kept: the middle
ad was the stem's sixth brand whatever the variant, and the first contact
sheet showed one brand there on all four; it walks the variant now. The first column of the top row
sells what the header does. The header is lit and nothing else: the
insert's front is two quads, the header's `M_CigMachine_<art>_Face`
(`make_backlit_material`, Lux's power cut takes it) and the rest
`M_CigMachine_<art>_Display` (painted). 1,456-1,976 tris against 2,500.

TWELVE INVENTED BRANDS in one table beside `brands.py`: DELCO REDS, MACDADE
MENTHOL, BLUE ROUTE LIGHTS, MARCUS HOOK 100s, NANA'S SLIMS, JAWN KINGS,
WOODER FILTERS, BOULEVARD BUTTS, DOWN THE SHORE 120s, HAVERTOWN HAZE, DARBY
DARKS, BALTIMORE PIKE MILDS -- each with a PG-13 slogan ("Smoke 'Em If Youse
Got 'Em.", "She Quit. Twice.", "Low Tar. High Hopes.") and a plain pack
design (band, split, stripe, disc, diamond, bars). A denylist holds names
against real marks as whole words (Kool, Salem, Camel, Merit, More, Eve,
True, Kent, Basic, Doral, Misty, Capri, Now, Winston, Newport, Marlboro, ...)
and anywhere (Virginia, Benson, Hedges, Pall Mall, Chesterfield, Old Gold,
American Spirit, Philip Morris, ...), and designs against real trade dress
(the red roof chevron, the spinnaker, the camel, a crest). ONE SUGGESTED
NAME WAS CHANGED, recorded in the module: CHESTER 100s became MARCUS HOOK
100s -- "Chester" is the first seven letters of a national brand sold in
1997, and a 100 in a red-and-white pack would read as it.

HOW BRIGHT THE HEADER IS: 0.5, set faint and then measured. `strip_club_a01`'s
two machines (variants 1 and 3) built at 0, 0.5, 1.0 and 1.5 and swapped
into a scratch copy of `_runs/walk_9057_rain` (Heavy Rain as shipped),
Godot 4.7 gl_compatibility, `tools/look_shots.py` 1600 x 900, a camera 1.5 m
in front of each; the knob read back from every GLB (factor 0.5 and 1.0,
then factor 1 with `KHR_materials_emissive_strength` 1.5), and the
constant built byte-identical to the sweep's 0.5 -- before the middle ad
was made to follow the variant (below), which moves no header pixel. Header pixels
are those that brighten by more than 8 codes from 0 to 1.5; 8-bit sRGB after
tonemap and Lux post, Rec.709 luma:

                  strength       0      0.5     1.0     1.5
    main floor    luma        21.8     47.6    61.2    84.3   (18,697 px)
    VIP wing      luma        14.9     45.8    58.8    77.4   (19,105 px)
    both          pinned %       0        0       0       0
                  white %        0        0       0       0

0.5 is 2.2 - 3.1 x the unlit header and nothing pins even at 1.5. Not
measured: the summer preset.

### Tests

`tests/test_dartboard.py` and `tests/test_cigarette_machine.py`: the slot
filled exactly at every corner and Deli Counter's sizes, the bull at the
centre height, 0 coincident pairs at a 2.2 mm window, every primitive wound
outward, the budget, collision the cabinet box, the knobs one a column and
the slot's front, the board at regulation radii and order, the chalk
stages, the display's bytes and what it says, the brands and the denylists,
and in Blender: PASS and fit, `tools/coplanar_probe.py` 0 rows, only genome
parts, the collider and the bull, the painted materials in the file and
nothing else lit (the machine's header only, at its strength), COLOR_0
white on the art, two builds byte-identical, four variants four arts.
REFUTED, kept: the lock's back stood 2.0 mm off the top cap's face, which
the pure probe passed (float: 0.0020000000000000018 > 0.002) and Blender's
failed; the pure tests now use 2.2 mm. `test_genome.py`,
`test_material_options_closed.py` (both on `metal_painted`; the machine
no longer also offers `metal_bare`) and `test_theme_style_resolution.py`
(68 species) name the two.

1896 passed / 192 skipped plain (0.90.0 in this worktree: 1783 / 174).
In Blender 5.1.1 the whole suite 2061 passed / 27 skipped; after the middle
ad's fix and two unused imports removed, `test_dartboard.py` and
`test_cigarette_machine.py` again in Blender, 119 passed.

Frames: `strip_club_a01` kit-built from Deli Counter 0.136.0's build (67
modules, 0 failed), composed with 0 greybox fallbacks and swapped into a
scratch copy of `_runs/walk_9057_rain`: the three boards at 1.5 and 4 m and
the two machines at 1.5 m.

## [0.90.0] - the bar TV is on, and it is showing the game

The walker, after walking cold run 9057's strip club: "I also want the CRTs
in the Strip club to have a light/glow from the screen as if they are
on...but we dont have to have a clear image on them...it would be a
football or baseball game tho". 0.88.0 lit the bracket set's glass a flat
(0.10, 0.17, 0.26) x 0.35, which read as a dead tube. And 0.88.0 recorded,
without fixing, that the stand set failed `fit_depth` at every size and hid
its screen inside its body. Both are closed here.

This does not reduce interventions-per-level by itself: it is the walker's
second look at a club, answered in the tool that owns the prop. Deli
Counter 0.135.0 is the other half (the light the screen throws), and Deli
Counter does not yet write a `variant` on its TVs -- see the last section.

### The picture: `core/crt_screens.py`

A 224 x 168 raster (4:3) painted in plain Python, the vending panel's
pattern (`vending_forms.Canvas` and its PNG writer, `pixel_type` for the
lettering), and the same bytes every build -- host Python and Blender's
paint `hoag_wit` to one CRC.

  * FOOTBALL from the press box: mowing bands, yard lines converging on a
    vanishing point above the frame, hash marks, the stands over the far
    sideline, two teams of blobs either side of a line of scrimmage. Scene
    `line` is midfield; `goal_line` has an end zone in the home colour.
  * BASEBALL: `pitch` is the centre-field camera, the pitcher's back and
    number in the foreground, batter, catcher and umpire in the dirt round
    home, base paths running out of frame; `wide` is the high-home shot of
    the diamond with the fielders, a batter and sometimes a runner.
  * A SCORE BUG top left: a team colour chip, abbreviation and score per
    row, the period beneath. Teams are invented and Delco: `YOU` (youse),
    `JAWN`, `WDR` (wooder), `SCR` (scrapple), `HOAG`, `WIT`, `MUD` (MacDade
    mud), `SHOR` (down the shore). The eight bugs:
    `YOU 14 / JAWN 10 / 4TH 2:07`, `HOAG 21 / WIT 17 / 2ND 0:48`,
    `JAWN 3 / MUD 7 / 3RD 9:15`, `SHOR 0 / YOU 6 / 1ST 11:32`,
    `WDR 3 / SCR 2 / TOP 7`, `MUD 5 / SHOR 4 / BOT 9`,
    `SCR 1 / HOAG 0 / TOP 3`, `WIT 8 / WDR 6 / BOT 5`. A denylist test
    holds every token against real NFL, MLB, NBA and NHL abbreviations of
    the period, the Philadelphia teams and nicknames, the local colleges,
    the leagues, and the networks and stations that carried the games.
  * NOT A CLEAR IMAGE, measured: the scene blurred twice and the frame once
    ([1 2 1]), every other row x 0.80, a vignette (corner 0.47 - 0.63 of the
    centre) and a cold phosphor cast. No two horizontal neighbours differ by
    more than 96 codes (the bug's white type on navy is 224 crisp).

WHICH GAME is the module's variant: the genome's `module_variants` is 4, and
`pick_game` walks `game_order(stem without _n)`, which alternates the
sports -- so variants 0 and 1 of one slot are always a football and a
baseball game, and the two TV sizes Deli Counter places open on different
games. `params.game` names one outright.

### The face: `crt_forms.screen_prim`

The glass is a 4:3 grid of 48 quads bulged 14 mm toward the room at the
centre with its corners 4 mm behind the bezel, so the bezel cuts it to a
tube's rounded outline; a flat back and four side strips close it. It
carries its own UVs (`uvs`, per face corner): the picture edge to edge on
the front, the vignette's darkest pixel everywhere else. `recipes/crt_tv.py`
builds it outside `prim_mesh` for those UVs, with
`materials.make_backlit_material` as `M_CRT_Screen_<art>_Face` (Lux's power
cut), albedo 0.35, and COLOR_0 white (Level Factory's worldskin leaves it
undimmed). 404 tris against 4000; exact fit and 0 coplanar pairs at the
genome's corners and Deli Counter's two sizes.

### How bright: 1.5, measured

The two TV modules of `strip_club_a01` (the stems cold run 9057 built)
rebuilt at 0, 0.5, 1.0, 1.5, 2.0 and 3.0 and swapped into two scratch copies
of `_runs/walk_9057_rain` with this release's club rigs and Deli Counter
0.135.0's screen neons baked -- Heavy Rain as shipped, and the same copy on
delco_summer_afternoon -- Godot 4.7 gl_compatibility, RTX 2060,
`tools/look_shots.py`, a camera 2 m in front of each of the club's three
sets. The knob was read back from every GLB before any frame was trusted
(`emissiveFactor` 0.5 at 0.5, `KHR_materials_emissive_strength` 1.5, 2 and 3
above 1.0), and the committed constant builds byte-identical to the sweep's
1.5. Screen pixels are those that brighten by more than 8 codes from 0 to 1;
ranges over the three sets:

                  strength    0      0.5     1.0     1.5     2.0     3.0
    rain   luma            12-59  51-80   70-93  103-119 130-142 169-177
           saturation      .46-.90 .40-.52 .37-.45 .33-.38 .30-.33 .24-.25
           pinned %           0      0       0       0       0    .06-.11
           white %            0      0       0       0     0-.01  .86-1.43
    summer luma            14-66  62-92  84-108 121-138 150-163 191-200
           pinned %           0      0       0       0    .10-.69 11.2-17.3
           white %            0      0       0     0-.05  .45-.88 5.4-7.6

1.5 is the highest strength with no pinned pixel in either preset, 2.0 to
8.6 x the unlit screen's luma in the rain. Its 0.05 % white under the summer
sun is the bug's type. KEPT, the stricter reading and the first value: 1.0
is the highest with neither pinned nor white anywhere (the vending panel's
rule); frames of both were shot.

### The stand set fits its slot and shows its glass

`crt_forms.stand_layout` is the stand set's parts, pure. MEASURED on 0.89.0
in Blender, kit path: 0.522 m deep for a 0.500 slot, 0.642 for 0.620, 0.372
for 0.350 (`fit_depth` FAIL), the knobs 22 mm past the front and the screen
box 10 - 30 mm behind the body's face. Now the body's front stands 18 mm
inside the slot, the knobs fill that depth to the front plane (buried 6 mm),
the glass stands 10 mm proud of the body, and the feet are buried 6 mm into
its underside. Every fit check passes at the sizes measured and the coplanar
probe finds nothing. The stand set's screen is still dark glass: a set on a
surface is off. `test_club_bpy`'s pinned digests for the stand set are
0.90.0's now; 0.86.0's are kept beside them.

### Tests

`tests/test_crt_screens.py`, 89 (16 of them bpy): the picture's bytes, PNG
and 4:3; soft, scanlined and vignetted; a ballgame on grass under a bug;
both sports and all four scenes; the denylist; no green jersey; the genome's
four variants honoured by the kit; variants alternate sports and never
repeat; the pick by stem and variant; the bracket set's exact fit, face and
UVs at the corners; the bulge and the sunk corners; the stand layout exact
at the corners with 0, 2 and 4 knobs; and in Blender: both forms pass fit
with 0 coplanar pairs, the stand's glass in front of its body, the screen
the only lit object with white COLOR_0 and an emissive texture at
`SCREEN_EMISSION` in the GLB, the same GLB twice, four variants four games.
On 0.89.0 the file does not import (`crt_screens` does not exist); the
behaviour it pins was measured failing there, as written above.
`test_club_bpy.py`: the flat-colour screen case removed (the picture is
tested here) and the stand digests re-pinned.

Host suite 1781 passed, 176 skipped. In Blender 5.1.1 the whole suite 1931
passed, 26 skipped, at strength 1.0; after the move to 1.5,
`test_crt_screens`, `test_club_bpy` and `test_club_species` in Blender, 379
passed, 1 skipped.

### Not done, and why

  * DELI COUNTER CANNOT WRITE A TV VARIANT YET. On Zoo 0.89.0 a `variant`
    on `crt_tv` is outside `module_variants` and `honour_dressing` drops
    all three fields -- measured: `form` `bracket` with a `variant` built a
    STAND set. Until this release is what Deli Counter's hook reads, every
    TV of one size in a building is variant 0, the same game:
    `strip_club_a01`'s three sets show two games, both football
    (`shor_you`, `jawn_mud`). Deli Counter's `wall_tv` piece can take
    `variants=True` once Zoo 0.90.0 is on main.
  * Deli Counter's screen neon puts a specular highlight in the middle of
    the glass (the omni stands 0.25 m in front of it; roughness 0.35). It
    reads as glare in the frames; nothing measures it.
  * The kit for the frames used the e2e delco_1997 skin library, not cold
    run 9057's: 307 of 323 embedded images differ from 9057's kit, while
    every module's glTF but the two TVs is identical. The before/after sheet
    carries that confound; the sweep, which moved only the TV modules inside
    one walk, does not.

## [0.89.0] - the club's five defects, and the material in the name

0.88.0 built the club and recorded what it found and did not fix: the
tablecloths rendered as gold burlap, every stool seat the plastic pack's
red-orange, a `wood` slot built a wood sofa, two slots differing only in
material shared one filename, a club floor could not ask for Pixelcoat
0.42.0's carpet, and the neon sign read as double vision. Each is closed
here, with a test that failed against 0.88.0 first
(`tests/test_club_fixes.py`, 26 tests, 22 of them failing before), and
each was measured before it was believed. Pixelcoat 0.43.0 is the other
half: `velvet`, `leather`, `canvas` and `plastic` are tintable in both
delco themes and there is a `cloth` for tablecloths.

This does not reduce interventions-per-level by itself. Deli Counter still
writes none of the club species' names, and it must mirror one naming
change below before a kit built by this release resolves.

### The material is in the stem: `_m<kind>`

`kit.module_stem` takes ``material`` and writes ``_m<kind>`` after the
dressing (`_f`, `_s`, `_n`) and before the void and opening hashes and the
state, so a dressed interactive slot's states each carry the same
material:

    <type>[_<species>]_<theme>_<style:02d>[_w<cm>][_d<cm>][_h<cm>][_f<form>][_s<stock>][_n<variant>][_m<material>][_v<hash>][_o<hash>][_<state>]

It is present when the slot's material is a known kind
(`skins.KNOWN_KINDS`) that is not the species' own for the theme -- the
theme style block's material, walking the theme family, or the genome
default: `kit.species_default_material`, the ONE definition the stem and
`dna.resolve_module_plan` are measured against. Absent, unknown, or equal
to the species' own, it adds nothing and every name built before it is
unchanged. `plan_kit` keys its buckets on that tag rather than the raw
slot material, so a slot with no material, one naming an unknown kind and
one naming the species' own all dress one module; the kit index and every
plan module carry `material_tag`, and the STEM COLLISION check stays for
the axes the key still has that the stem does not.

THE MIRROR, for Deli Counter's `themed_tscn.module_stem`: the same
keyword, the same position, and `resolve_themed_stem` asks for the
`_m<material>` name first when the slot carries a material and falls back
to the name without it -- exactly how it already resolves the dressing.
Deli Counter cannot read a genome to learn the species default, and does
not need to. Measured on what changes: a `wood` sofa slot names
`prop_booth_seat_delco_1997_01_w200_d90_h85_fsofa_n1_mwood`; a rockay
wall zone in drywall names `wall_rockay_03_w200_mdrywall` where the style
already kept it apart; a vault door cut from a concrete partition names
`vault_door_delco_1997_01_w360_mconcrete_o<hash>`, because the slot's kind
lands on the plan even though the leaf's recipe reads the style's
metal_painted and ignores it (asserted in `test_vault_door.py`) -- one
build, one name, still. `dna.resolve_module_plan`'s fallback stem (a
module with no `stem`) now passes height and species too; it had only
ever been reached by walls.

### Upholstery is not the slot's to override

`dna.UPHOLSTERED` is the one table of upholstered species and their soft
kind: `booth_seat` None (the genome's own material IS the upholstery --
leather, canvas or plastic), `club_chair` velvet, `bar_stool` plastic
(the planner says per variant). On these a slot's material is the FRAME's
unless the genome material is the upholstery and the slot names one of
its kinds. `resolve_module_plan` writes ``plan["upholstery"]`` --
`material`, `frame`, `color` -- and `booth_seat` reads it: the frame kind
replaces the wood of the panels, kick, cap and feet in their own colours,
the upholstery keeps its kind and the genome colour. The club walk's couch,
built from Deli Counter's `wood` slot, reads back as leather
(`M_Skin_leather_delco_1997_420d12`, the genome's 0.26/0.05/0.07) on
`M_Skin_wood_delco_1997` legs. `club_chair` and `bar_stool` always took
the slot material on feet and column; the table is the contract, not a
patch list.

### The club kinds, and a seat and a cloth by variant

`skins.KNOWN_KINDS` and `materials.ROUGHNESS` take `carpet_club` (0.95),
`wallpaper_club` (0.66), `wood_stained` (0.50), `paint_block` (0.88) and
`cloth` (0.85); a floor slot asking for `carpet_club` builds in it.

`club_forms.SEATS` is ``(rgb, kind)`` -- red and black vinyl (`plastic`),
plum and oxblood velvet -- and `plan_stool` takes ``variant``:
``SEATS[variant % 4]``, so `_n2` is the same stool in every kit.
`CLOTHS` is dark red and white on the `cloth` kind, ``CLOTHS[variant %
4]`` in `plan_table`; two colours, not four, because a club's tables are
dressed alike. The chair's velvet is still the seed's.
`test_seeds_change_what_the_seed_is_for` says which is which.

### The neon sign's tubes sit a finger off the can

0.88.0 put the tubes at the slot's front and a 25 mm backer at its back:
on Deli Counter's 0.10 m sign the glass stood 66 mm proud of the face it
was mounted on (measured off the GLB: tube back at z 0.0406, backer face
at -0.0250). Under a light every word threw a dark copy of itself onto the
backer, offset by that gap. It was NOT geometry -- `plan_sign` draws no
dark lettering -- and it was not settled in the walk: at the `tables`
station the backer 1-4 px from the tubes measures 38 luma against 49 at
8-13 px in 0.88.0, in this release, and with the twelve `shadow_enabled`
lights of `lux.applied.tscn` switched off, whose frames matched to 0.1
luma across five stations. That dial was never confirmed: the basement's
pendants are Lux runtime rigs (`lux_area_light_rig.gd`), not those nodes,
and a symmetric band is not a shadow. So a two-sign lab: one omni lamp
above and in front, the 0.88.0 sign and this one side by side, GL
Compatibility, shot with the lamp's shadow on and off. The 0.88.0 backer
held 12,576 pixels darker than its median by 20 with the shadow on and 3
with it off; this release's held 0 either way, in the same frame under
the same lamp.

`neon_forms.TUBE_STANDOFF` 0.02 m: the tubes keep the slot's front, the
can's face is one standoff behind their backs (20 mm off the GLB) and the
can is everything from there to the wall; a slot shallower than tubes plus
standoff plus `BACKER_T_MIN` shortens the standoff first. `BACKER_T` is
gone with its use. Same 2448 tris, `coplanar_probe` 0 pairs.

### Not this release's, measured on the way

  * **The vending machine writes COLOR_0 as it should.** Asked whether
    0.87.0's machine reached cold run 9054's walk with no "draw vertex
    colour" line. The machine in 9054 is not 0.87.0's: its kit index says
    Zoo 0.86.0 (`bank_branch_a04_kit.built.json`), its meshes are the
    pre-0.87.0 Body/Glass/Panel/CoinSlot/Tray in `M_Skin_*` kinds, its
    status is `fail` (`fit_depth` 0.795 m against 0.750), and its COLOR_0
    is tinted on all five primitives (min 0.791). A 0.88.0-recipe machine
    built here and imported by Level Factory's current `zoo_worldskin.gd`
    prints "3 material(s) draw vertex colour, 2 all-white left off, 0 with
    a surface lacking colours": the two whites are `_Face` and `_Lens`
    (COLOR_0 exactly 1.0 on every vertex, the backlit contract), the other
    eleven primitives carry 0.63-0.99. No 9054 walk import log survives in
    the workspace to say why no line was printed there; the file itself
    would have earned one. Nothing changed.
  * `plan_stool` and `plan_table` keep their ``rng`` for what the seed is
    still for; the neon standoff rods are shorter, not fewer.

### Seen

Godot 4.7, GL Compatibility, RTX 2060, `tools/look_shots.py` on scratch
copies of the club walk at five given stations, before (0.88.0's kit, the
old packs) and after (this kit, Pixelcoat 0.43.0's delco_1997 library):
dark red and white cloths, red and black vinyl and plum velvet seats, the
couch leather on wood legs, the chairs velvet through the pack. Readback
of the imported materials: `albedo_color` is the genome colour exactly
(plum 0.12/0.03/0.12 linear reads 0.381/0.190/0.381 sRGB), albedo texture
means 0.61-0.65 linear, vertex colour drawn on every one of the twelve
fabric materials the readback listed (velvet, cloth, leather, canvas, the
stool vinyl) and, by the import's own lines, on every wear-carrying material
of the fourteen rebuilt props.

Suite: 1709 passed, 160 skipped in plain Python (0.88.0: 1683 / 160);
80 passed in Blender 5.1.1 for `test_club_bpy.py` and
`test_interior_bpy.py`. `coplanar_probe` 0 pairs on the rebuilt stool,
table, sign, both sofas and the chair.

## [0.88.0] - a strip club is a stage, a bar, a sofa and a name in neon

The walker, with two GTA IV Triangle Club frames: "strip clubs should have a
dingy lived in feel, dark with colored lights, couches and bars". Then a local
comparison for layout only -- a one-storey 1990s neighbourhood club with two
bar areas whose poles stand inside the bar, and several TVs -- and a
correction: the game is 1997, so the PRE-renovation club: CRTs on brackets,
nothing that reads as a refit, the only light in the furniture a plain warm
rope light. Deli Counter's library has three strip clubs
(`strip_club_a01..a03`); today their `stage` (8 x 4 x 0.8, 7 x 3.5 x 0.8) and
bar volumes route to no species and ship as grey boxes.

This is the Zoo half. It does not reduce interventions-per-level by itself:
until Deli Counter writes the names below, no generated club gets any of it.

### What the library had, measured first

`booth_seat` form `sofa` is the couch (reused, not duplicated). `table`,
`counter` and `_surface_stock`'s `bar` flavour already set bottles, pints on
coasters, ashtrays and napkins on a top; `stair_rail`, `sign_box`,
`_legend.py` and `crt_tv` exist. What did not: a stage of any kind, a small
round table, a tub chair, a bar stool, a neon sign, a TV that is not on a
surface. `_legend`'s cell grid cannot draw a diagonal stroke (K M N V W X Y Z
are left out of it on purpose), so it cannot spell a club name; Pixelcoat's
built-in 5 x 7 bitmap (`signage._FONT`) can.

delco_1997's packs (cold run 9052's Pixelcoat build, read): `leather`
(brown), `canvas` (beige), `carpet` (dusty mauve), `wood` and `plastic`
(red-orange) are NOT tintable; only `laminate`, `paper`, `metal_bare` and
`metal_painted` take the mesh's colour. A velvet colour cannot ride any kind
Zoo had.

### Five species and a form (planned in pure Python, built vertex for vertex)

| species | planner | what it is | tris (pure = built; no bevel) | budget |
| --- | --- | --- | --- | --- |
| `club_stage` `round` | `core/club_forms.py` `plan_stage` | an ellipse filling the slot behind its steps: recessed wood fascia, overhanging lip, worn carpet top, rope light under the lip and on every step nosing, padded rail on brass posts and collars open where the steps come up, chrome pole with floor and ceiling flanges | 1348 at 2x2x0.45, 1388 at DC's 8x4x0.8, 2896 at 3.6x4.6x3.6, 4128 at 14x8x5 | 5000 |
| `club_stage` `runway` | same | a platform along the slot's long axis with a round far end, the pole there, steps at the near end, no rail on the square end | 708 at 8x4x0.8, 2160 at 8x4x3.6, 2888 at 14x8x5 | |
| `club_stage` `bar_stage` | same | an oval bar round a raised deck: kick, fascia, bar top ring, padded armrest, brass foot rail on brackets, deck lip, carpet and rope light a hand above the bar top, one pole or two along the deck | 2424-2996, plus up to 1664 of `bar` stock on the straight runs | |
| `cocktail_table` `cloth` / `bare` | `plan_table` | a floor-length cloth over a round top that flares to a folded hem (CLOTHS: burgundy, black, green, stained cream), or a bare wood top on a black cast base | 240 / 268, plus up to 448 of stock | 1400 |
| `club_chair` | `plan_chair` | a barrel-backed tub chair: short wood feet, upholstered drum, a D-shaped crowned seat, a back that wraps the sides and falls to the arm fronts, piping on the crown; VELVETS oxblood, plum, teal, bottle green | 992 | 1200 |
| `bar_stool` | `plan_stool` | domed chrome base, column, footring on three spokes, black pan, padded vinyl seat (red, black, plum) | 762 | 900 |
| `neon_sign` | `core/neon_forms.py` `plan_sign` | glass tube lettering and a cut-corner border tube on a dark backer, on standoffs | 1776 (LIVE GIRLS) to 4856 (BOTTOMS UP ON BALTIMORE PIKE) | 5000 |
| `crt_tv` form `bracket` | `core/crt_forms.py` `plan_bracket` | a tube set with a deep bezel, tapered housing, lit screen and knobs, strapped to a black shelf with a lip on an arm and brace off a wall plate, tipped 8 degrees toward the room | 168 | (4000) |

Recipes: `recipes/club_stage.py`, `cocktail_table.py`, `club_chair.py`,
`bar_stool.py`, `neon_sign.py`, and `crt_tv.py` `_bracket`. Every planner
keeps the interior species' rules -- exact extents, parts overlapping by
millimetres, no two faces within 2 mm of one plane, deterministic -- and the
tests hold them at every genome corner.

**The stage's heights follow the slot** (`stage_heights`): a slot up to 0.9 m
IS the platform (Deli Counter's 0.8 m volume builds today, no rail, no pole);
up to 1.16 m the platform is the slot less the 0.36 m rail; taller, the
platform is 0.8 m -- DC's own stage height, so its collider and the deck
agree -- and the pole runs to the slot's top. **Author the volume to the
ceiling** to get the pole. **Steps are derived**: the fewest (1-3, 0.34 m
treads) that keep a ramp over them at or under 44 degrees, because a ramp is
what a body walks and `floor_max_angle` is 45 (0.45 m: 2 steps, 33.5 deg;
0.6: 2, 41.4; 0.8: 3, 38.1; 0.9: 3, 41.4). `auto` is `round` up to 1.4 : 1
after the steps, `runway` past it, never `bar_stage`. Zoo does not decide the
walkable surface (README): the stage's colliders are bands inscribed in its
outline, the steps and short boxes along the rail, not the pole.

**The lettering is the factory's.** `neon_forms.FONT_5X7` is a copy of
Pixelcoat 0.41.0's `_FONT` (Zoo does not import Pixelcoat, which needs numpy
and PIL inside Blender); a test compares the copy with the Pixelcoat source,
read as text, when that repo is beside this one or `GABAGOOL_FACTORY` names
it. A glyph is turned into its skeleton -- lit pixels joined across edges, and
diagonally only where the corner between is dark -- merged into maximal
straight runs, each run one eight-sided rod. One to three lines, whichever
gives the largest pitch.

**The names are one table**, `core/club_names.py` `NAMES`: 24 invented,
PG-13, Delco -- THE JAWN ROOM, MACDADE MAGIC, LIVE GIRLS, BOTTOMS UP ON
BALTIMORE PIKE, NANA'S NOT HERE, YOUSE BEHAVE, MOM THINKS I'M AT BINGO,
CHEEKS ON CHESTER PIKE, THE WOODER HOLE, SHAKE YOUR SCRAPPLE, ROUTE 291
REVUE, DOWN THE SHORE LOUNGE, CASH ONLY CABARET, NO TOUCHIN' HON, THE MARCUS
HOOK-UP, GLENOLDEN GLOW, DARBY DOLLS, THE PRETZEL TWIST, OPEN TIL 2 AM,
DOLLAR DRAFTS - LIVE DANCERS, FOLSOM FOXES, GO-GO ON 291, TIPS APPRECIATED,
YO! SHOWGIRLS. `neon_sign`'s `module_variants` is the table's length and the
variant IS the index. `DENYLIST` (the local comparison's name first, then
regional and national club names, local brands and teams) is a guard a test
holds every name against -- not a search of any business register.

### Light, and what happens to it downstream

`prim_mesh.build` takes `(name, colour, "emissive", strength)` for a lit key:
`make_emissive_material`, no bevel, no wear, no ambient, so COLOR_0 is white.
Every lit material is `M_*_Face`, the suffix Lux's emissive binder cuts with
the power: `M_ClubStage_rope_Face` (1.0, 0.62, 0.28) x 1.0,
`M_NeonSign_<hex>_Face` in `club_names.PALETTES` x 1.2, `M_CRT_Screen_Face`
(0.10, 0.17, 0.26) x 0.35.

Level Factory 0.86.0's `zoo_worldskin.gd` (21,136 bytes, read, not changed)
leaves props alone except turning vertex colour on for materials whose COLOR_0
is tinted. Imported into a scratch walk copy with that script, it printed
"all-white left off" for exactly the lit materials (stage 1, CRT 1, neon 2),
and a headless Godot 4.7 probe of the imported scenes read every one back
with emission on at the energy above and `vertex_color_use_as_albedo` false.
**Level Factory needs no change for the emission.**

REFUTED, each by a frame, each kept at its constant: the rope light at 3.0
and the neon at 4.0 clipped in the walk's dark basement (brightest rope
pixels 250,250,250; the pink-and-blue sign's 226,247,252, white); after, the
sign's most saturated pixels read 164,96,144 (pink) and the rope 200,198,183.
The CRT screen at (0.32, 0.42, 0.55) x 1.2 rendered as a blank panel in
Cycles, and at (0.10, 0.17, 0.26) x 1.0 as a pale flat screen in Godot.

### A new kind: `velvet`

`skins.KNOWN_KINDS` and `materials.ROUGHNESS` (0.96). No theme has a velvet
pack, so a club chair renders flat in its VELVETS colour with its wear -- the
progressive art pass. When Pixelcoat authors one it must be tintable, or
every chair turns one colour. Pixelcoat's `_ZOO_KINDS` mirror in
`cli/main.py` does not list it (nor `stone`, `siding`, `shingle`, `tar`,
`metal_bare` or `metal_painted`).

### Refutations kept in the files

  * Stage: the first step on the floor laid its bottom in the fascia's bottom
    plane (one SAME pair at every size); brass posts at phase 0 put a rail
    segment's end cap 0.44 mm from a post facet on a runway's round end;
    a runway always along x gave a 2 x 8 m slot a 3.5 m end radius; a
    bar_stage pole only past deck + 0.5 left a 1.5 m slot 0.32 m short and
    the fit stretched it 27 %.
  * Chair: a seat ellipse inside the barrel stood 33 mm short of the slot's
    front (fit stretched the chair 4 %); piping 4 mm under the crown stood
    4 mm over the slot.
  * Table: a column bottom exactly 2.0 mm over the base plate passed the pure
    probe and failed Blender's (float32); one stock region per top carried
    one group on 12 of 12 seeds, two halves carry two on 9 of 12 at 0.75 m.
  * CRT bracket: drawn at slot size and fitted, the tip put it 24-60 mm over
    (now four corrections against the tipped bounds, overshoot under 1e-4 m);
    the arm 1 mm under the plate's bottom; a `plastic` housing rendered as a
    red box because delco_1997's plastic pack is red-orange and not tintable
    (painted metal now).

### What already shipped is unchanged, measured

Built from a `git archive` of 0.86.0 and from this branch, kit path,
delco_1997: `crt_tv` stand at 0.55x0.5x0.42 and 0.9x0.62x0.7, `booth_seat`
sofa and booth, `pool_table`, `table` and `counter` with bar stock -- same
digest over object names, vertices, Wear and material names, pinned in
`tests/test_club_bpy.py`. The stand path returns before `bracket` is read.

### Tests

`tests/test_club_species.py` (249, pure): genomes, contract names and forms,
keyword routing (and that chair, stool, table, couch, tv and lit sign still
route where they did), dressing fields honoured and all-or-nothing dropped,
DC's current stage volumes fit, exact extents and zero coincident pairs and
colliders inside bounds at every genome corner of every form, budgets with
worst stock, the neon budget is the longest name, determinism, seeded colour
coverage, stage heights, step pitch, auto form, poles to the slot top, the
rail gap over the steps, rope light on every step, bar_stage anatomy, stock
inside the round top, cloth vs bare, chair back profile, footring height,
name table = variants, names spelled from the font and on no denylist, font
parity with Pixelcoat, every glyph skeleton covers exactly its lit pixels,
line breaking, every name clean at four sign corners, bracket TV fit and
tip. `tests/test_club_bpy.py` (43 in Blender 5.1.1): PASS, fit to 1 mm,
budget, genome parts, `coplanar_probe` 0 pairs at min/default/max of every
form, two builds identical, lit materials exactly where promised with white
COLOR_0, emission in the exported GLB, bar stock present and measured apart,
the 0.86.0 digests, no collider on a sign. Against 0.86.0 both files fail at
collection (no `club_forms`, no genome).

### Not Zoo's, found on the way, not changed

  * **A sofa slot's material makes its upholstery that kind.**
    `dna.resolve_module_plan` takes a slot's `material` when it is a known
    kind, and `booth_seat` uses `plan["material"]` for upholstery. Deli
    Counter writes `wood` on its booth volumes: a sofa built with it carried
    only `M_Skin_wood_delco_1997` and `M_Skin_canvas_delco_1997`, no leather.
    The same stem with and without the field names one file, so a kit holding
    both writes whichever was built last.
  * `crt_tv` stand fails `fit_depth` on the kit path at every size measured
    (0.522 m against 0.500): its knobs stand 22 mm proud of the front. Its
    screen box sits inside the body. Both on 0.86.0 too.
  * The walk copy's own `zoo_worldskin.gd` is 12,121 bytes, older than Level
    Factory 0.86.0's; the frames re-imported only the club GLBs with the
    current script.

### What Deli Counter must add (not done here)

  1. `prop_species` rows ahead of the rows that claim the words:
     `("club_stage", "stage", "pole_stage", "runway")` -> `club_stage`;
     `("cocktail", "club_table", "highboy")` -> `cocktail_table` before
     `table`; `("club_chair", "tub_chair", "lounge_chair")` -> `club_chair`
     before `chair`; `("bar_stool", "barstool", "stool")` -> `bar_stool`
     before `chair` (whose keywords include `stool`); `("neon", "club_sign")`
     -> `neon_sign`; `("bar_tv", "wall_tv")` -> `crt_tv` with form `bracket`.
  2. Strip club rooms: the stage volume authored FLOOR TO CEILING (3.6 m) with
     form `round` or `runway` -- at 0.8 m it builds a platform with no rail or
     pole; a bar area as `club_stage` form `bar_stage` with stock `bar`;
     `cocktail_table` 0.75x0.75x0.74 stock `bar` with two `club_chair`
     0.78x0.75x0.78 each; `bar_stool` 0.42x0.42x0.76 at bar fronts instead of
     `chair_set`, material `metal_bare` (a `wood` slot builds a wood column);
     sofas with material `leather` (see above); `neon_sign` 1.4x0.1x0.6 on a
     wall at about 2.2 m, `variant` = crc32(building) % 24; `crt_tv`
     0.55x0.62x0.5 form `bracket` at about 2.1 m near the bars. `variant` =
     crc32(slot_id) % 4 elsewhere.
  3. Lux: the club is dark only if a preset makes it so; the frames are under
     the walk's basement light.

### Seen

Godot 4.7 (gl_compatibility) frames through the factory's `tools/look_shots.py`
of a scratch copy of the vault-surface walk with a club corner in
bank_branch_a02's east basement room -- a round stage with its pole, two
clothed tables with tub chairs, a couch, three stools, THE JAWN ROOM in pink
and blue, a bracket TV -- at five given stations; and a Cycles contact sheet of
every species, form and all 24 names built with delco_1997's packs. Not
checked: the bar_stage in Godot; a level Deli Counter generates; anything
under a Lux club preset.

Suite: 1612 passed, 142 skipped in plain Python with `GABAGOOL_FACTORY` set
(1611 / 143 without it: the font-parity test skips) against 0.86.0's
1344 / 94; 1729 passed, 25 skipped inside Blender 5.1.1 (0.86.0: 1419 / 19).
The first full Blender run failed one test of this release's own: the
emission check had a fixed floor of 0.35 written before the screen was
dimmed to 0.35 strength; it now compares with the declared colour and
strength.

## [0.87.0] - the vending machine glows, and sells WOODER

The walker, with a frame of a modded Deus Ex vending machine: "vending
machines should glow", and "we want fake products that are funny and a bit
crass ... Delco themed". The reference is a tall machine whose whole front is
a backlit panel carrying one loud brand, a column of lit selection buttons, a
coin panel with a small lit display, a dark delivery flap, and the panel's
colour on the floor beside it.

**What 0.86.0 shipped, measured before anything moved.** Built through
`plan_kit` + `build_module` at Deli Counter's `vending` size (0.85 x 0.75 x
1.83, style 4) with cold run 9052's delco_1997 Pixelcoat output: a body box, a
"glass" slab, a side panel, a coin slot and a tray, 220 triangles, three
materials, nothing emissive -- and FAIL, `depth=0.795m != exact target
0.750m`, because the coin slot's front stood 45 mm in front of the body. The
same FAIL Deli Counter's furnish agent reported from `country_club_a01`'s kit
log (`prop_vending_machine_delco_1997_04_w85_d75_h183`, x2). The genome's
`lit` param was declared and read by nothing.

**The recipe is rebuilt** (`recipes/vending_machine.py`; every size, the brand
and every pixel of the artwork in the new pure `core/vending_forms.py`). A
1990s soda machine, front toward -Y:

  * the cabinet, the slot's full width, height and back, and a door hung on
    its face `REVEAL` (8 mm) inside its sides and top;
  * the door is ONE closed solid over a grid of cells with three apertures
    left out -- the backlit panel, the selection column and the delivery flap
    -- so it has no internal faces;
  * the backlit panel; in the column a dark plate, the price display (bezel
    and lit lens), the coin mech with a coin slot, a bill mouth and a reject
    button, six lit selection buttons, the coin return and a T-handle lock;
    a dark bin behind a tilted flap; a recessed kick plate.

Fourteen parts, every edge hard, 464 triangles at every size (budget 600),
genome version 2. THE SLOT IS EXACT with nothing scaled: the door's front is
the slot's front plane and every column part is recessed into its aperture,
the frontmost 4 mm behind it. Every insert is buried 6 mm (three times the
coplanar probe's window) past the planes it meets.

**The brands** are one table, `core/brands.py`, so shelf stock, cans and cups
can sell the same drinks later: WOODER, JAWN JUICE, IGGLES TEARS, SCRAPPLE
SODA, MACDADE MUD, SHORE THING, HOAGIE SWEAT, YOUSE GRAPE, NANA'S BASEMENT,
BLUE ROUTE BACKUP, CHESTER GOLD and WIT OR WITOUT, each with its drink, its
slogan, a button label, a palette, an emblem and a cabinet paint. Two of the
starting names were changed and the module keeps why: BLUE ROUTE BLAST (one
word from a national lemon-lime's flavour line) and WIT WIZ (the "Wiz" is a
processed-cheese trademark). `FORBIDDEN_WORDS` is a tripwire for the obvious
real names, and a test reads every row against it.

A machine's brand is drawn from its stem WITHOUT the variant suffix, and the
variant indexes that draw -- so the four variants of one slot are always four
brands. The genome now declares `module_variants: 4`, which `plan_kit`
already honours (`_n1`.. `_n3`); an explicit `params.brand` wins. The six
buttons are the brand and five others. The cabinet wears the brand's paint
unless the prompt asked for a colour.

**The lettering is the factory's typeface.** Pixelcoat sets every shop sign in
Pixel Operator Bold (CC0, vendored in Pixelcoat). Blender's Python carries no
PIL, so `tools/mint_pixel_type.py` reads that TTF once into
`core/pixel_type_glyphs.py` and `core/pixel_type.py` lays it out in pure
Python. Nothing is lost by the table, measured with PIL before it was
written: at 16 px every glyph is 0 or 255, at 32 px exactly the 16 px bitmap
doubled (0 of 64,000 pixels on "IGGLES TEARS"), and a string equals its glyphs
at their advances (no kerning). A test re-mints the table from Pixelcoat's TTF
and compares four strings against Pixelcoat's own `_render_ttf`, identical.
The artwork -- dithered gradient, emblem, logo, drink, slogan band, six
labels and a red 75¢ -- is painted into one PNG per machine at 256 px/m (the
labels and display at 512), written by a deterministic encoder, packed into
the .blend and embedded in the GLB.

Found on the way and fixed: the glTF exporter names an image after its FILE,
not `Image.name`, so the first build shipped an image called `zoo_a3xvb95d`
from `mkstemp` -- a different GLB every build. `materials.image_from_png`
writes `<name>.png` in a fresh directory. Two builds in two Blender processes
now write byte-identical GLBs.

**The glow.** `materials.make_backlit_material`: the artwork drives Emission
Color and, times `PANEL_ALBEDO` 0.35 (folded into `baseColorFactor`), Base
Color -- a backlit panel is not a mirror of the room. Panel `M_Vending_<art>
_Face`, buttons and display `M_Vending_<art>_Lens`, so Lux's emissive binder
finds them. In the GLB: `emissiveTexture`, `emissiveFactor` [1,1,1],
`baseColorFactor` 0.35. Level Factory's `zoo_worldskin.gd` leaves the machine
alone ("not a kit module"); Godot 4.7's import, read back headless in the walk
copy: `emission_enabled` true, energy as exported, emission texture the same
Texture2D as albedo, 8 mips.

REFUTED, kept: `lit` 0 as "Emission Strength 0". With the texture still linked
the exporter drops `emissiveFactor` and keeps `emissiveTexture`, and Godot 4.7
imports that as emission ON at energy 1.0, colour white (readback) -- frames
at strength 0 and 1 matched to the decimal. A dark face now links no emission
at all, and `lit` 0 is a machine with its plug pulled.

**The strength is measured, not chosen.** Two scratch copies of the vault-room
walk (Godot 4.7, gl_compatibility, RTX 2060, `tools/look_shots.py`): three
machines against the basement's east wall and one in the lobby under the
walk's Heavy Rain preset, and one outdoors south of the bank under the theme's
`delco_summer_afternoon`, the brightest light this level has (the Heavy Rain
lobby is darker than the basement: frame means 46 and 70). The same GLBs at
strengths 0, 1.0, 1.5, 2.0 and 3.0; panel pixels are those brightening by more
than 8 codes from 0 to 1:

    basement (Heavy Rain)    luma  28.9 / 110.8 / 142.5 / 165.5 / 194.2
                             sat   0.63 /  0.54 /  0.49 /  0.45 /  0.36
                             white%   0 /     0 /     0 /  2.85 /  8.03
    outdoors (summer)        luma  47.5 / 120.6 / 149.8 / 172.1 / 201.2
                             pinned%  0 /     0 / 68.52 / 70.46 / 90.33

(white: every channel >= 235; pinned: any channel >= 250.) 1.0 is the highest
strength with nothing pinned or white in either preset: 3.8 x its unlit luma in
the basement, the art's own saturation (0.81-0.89 in the PNG) kept in the sun.
2.0, the first value (the fixtures' lenses), washed every panel toward pastel
under Heavy Rain and pinned 70 % outdoors. `PANEL_EMISSION` and
`LENS_EMISSION` are 1.0 with the table beside them.

GL Compatibility DOES render the Environment's glow here: at 3.0 a ring 3-24 px
outside the panel brightens by 12.0 codes with Heavy Rain's glow on and -0.4
with it off. At 1.0 the ring moves 0.3, because that preset's
`glow_hdr_threshold` is 1.1. A halo is the preset's lever.

**Light on the floor is NOT done here, and it is not Zoo's alone.** Measured
on a scratch copy with an OmniLight3D per basement machine in its panel's mean
colour (energy 0.8, range 2.5 m, no shadow, 0.35 m in front of the panel at its
centre height): coloured pools on the floor and wall as the reference shows,
the 5 m frame's mean +2.3 codes, up to +51 on the floor and +142 on the wall
beside them. Shipping it needs: a Zoo marker (`LuxEmit_vending` with the
colour in its payload -- not added, because `LuxFixtureSpawner` would skip a
type it has no rig for); a `vending` row in Lux's `LuxLightLoader._rig_for`
that reads that colour; and Level Factory counting those lights in the
package's `max_renderable_lights`, against Lux's per-mesh budget of eight.

**Two machines side by side are only two brands if Deli Counter asks.** A
stem is a file: two slots of one size and style instance one GLB. Deli
Counter's `vending` piece has `variants=False` and `most=1`, so today every
vending machine of one size in one building is the same brand. `variants=True`
there (its crc32 % 4 already matches `module_variants`) is the change.

**Seen.** `look_shots` frames before (0.86.0) and after at seven given
stations -- basement close, 5 m and three-quarter, lobby close and 5 m,
outdoors close and 5 m -- and the after set again under summer afternoon. At
about 4.7 m the logos and the scale-2 slogans read; the scale-1 slogans
("Delco Tap Wooder. Now With Bubbles.") do not, a 4 px cap against 9 px. At
Deli Counter's 0.85 m machine the panel's width is that limit; the slogan band
is 30 % of the panel so that at its 1.0 m machine 11 of the 12 slogans set at
scale 2 (5 at 26 %), and the 0.85 m GLBs photographed are byte-identical
either side of that change. A Blender contact sheet of all twelve.

**Numbers.** `tools/coplanar_probe.py --species vending_machine` at five
corners: 464 tris, 0 coincident pairs each.

`tests/test_vending_machine.py`, 89 tests: the genome and parts; the layout
exact at eight sizes and 30 random ones; nothing proud of the door; the door's
apertures and the triangle count; the brand table complete, invented,
legible (slogan contrast >= 4.5, labels >= 3, every label fits its button,
every brand lays out on the narrowest panel); variants four brands, 40 styles
at least eight; the artwork byte-stable and a real PNG; the glyph table
against Pixelcoat's TTF; and in Blender the fit at eight sizes, the glow on
the three lit parts and in the GLB, `lit` 0 dark in the file, two builds one
GLB and four variants four images, and 0 coplanar rows at six sizes. Run inside
Blender against 0.86.0's code, 87 fail and 1 passes (that DC's two sizes lie
inside the genome; the glyph test skips there, Blender having no PIL). Suite:
1416 passed, 111 skipped in plain Python (0.86.0: 1344 / 94); 1507 passed, 20
skipped inside Blender 5.1.1 (0.86.0: 1419 / 19).

## [0.86.0] - the vault door is painted, and the breached one is the same file twice

Two defects in 0.83.0's `vault_door`, both found on bank_branch_a02's door
(3.6 x 0.3 x 3.3 slot, 1.3 x 2.1 aperture) as built for the vault-room walk
copy: its Godot 4.7 frames, and a rebuild of the breached state.

**1. The streaks.** The frames showed the square surround and the leaf covered
in long horizontal black streaks where the walker's references show a clean
riveted painted-steel face. The kit that walk carries was built by Zoo 0.84.0
against cold run 9052's delco_1997 Pixelcoat output; rebuilt from this repo at
0.85.0 with those packs, the locked GLB came back byte-identical, and unlocked
and open identical in every mesh with only the embedded albedo PNG encoded at
another size (11,795 against 8,340 bytes, the same pixels; breached is defect
2) -- so the measurements below are on the path the walk took. In order:

  * UVs, NOT the cause. A per-triangle probe over the locked and open GLBs
    (the 2 x 2 map from each triangle's own frame to UV, its singular values)
    found every part at 1.000 UV units per metre along both in-plane axes and
    0 m2 of triangles with a singular value under 0.25. No stretched, no
    degenerate projection; Level Factory's `zoo_worldskin.gd` leaves
    `vault_door` alone ("not a kit module").
  * The pack. Every vault part was `metal_bare`, which delco_1997 skins with
    `metal_bare_neutral`: a 128 px tile per metre whose roughness map is two
    values in horizontal bars, 42 and 85 of 255 (0.165 and 0.333, the glossy
    bars 27% of the tile; row-mean std 14.3 against column-mean 2.8), under
    `METALLIC["metal_bare"]` 0.9. A glossy conductor mirrors the room, and in
    the vault room the room is dark.
  * Proved at the station. The same four GLBs with ONLY that map's green
    channel flattened to its mean (73), photographed through
    `tools/look_shots.py` at the same given station in a scratch copy of the
    walk, lost every streak. On the surround above the frame (vault_front,
    x 600-960, y 230-320, Rec.709 luma on the 8-bit output) mean |dY/dy| fell
    from 22.30 to 6.80 against |dY/dx| 7.71 and 6.09.

The pack's grain is Pixelcoat's to judge, and it is not changed here. What Zoo
got wrong is the finish: a vault door's plate is PAINTED. The genome's kind is
now `metal_painted` in every style (options `metal_painted`, `concrete`), and
the recipe keeps the hand-worn and machined hardware bare -- the wheel, the
dial and pull, the extended bolts, the boss bolts and the brass bolt heads --
with `vault_forms.HARDWARE_KIND` a constant, as the hydrant's chains are.
`vault_forms.HARDWARE_PARTS` is the table, and the recipe asserts every part
it emits against it. Built after, the same station reads |dY/dy| 5.78 against
|dY/dx| 5.54, the plate's luma std 33.9 -> 9.9, mean 104.7 -> 110.9 beside a
wall at 90.4. Bare metal on the locked door at 0.3 m: 52.3 m2 -> 1.7 m2; the
widest single bare polygon over all four states at 0.3 and 0.6 m: 3.618 m (a
surround triangle) -> 0.440 m (the U pull's bar).

The rest of the library on the same finish, each species once through
`build_specimen` at its genome defaults with flat materials: 18 species carry
`metal_bare`, and 13 of them a bare polygon at least 0.5 m across, where the
pack's bars would show -- stop_sign (post, 2.45 m), sign_post (2.40), shelving
(12.3 m2 in such polygons), the six street trees' grates (1.70 m, 3.0 m2 each),
water_tank (15.8 m2), flat_top_grill (8.4 m2), furnace (flue and plenum,
2.6 m2) and payphone (0.75 m). None was photographed and none is changed: the
galvanised posts, the shelving and the grill ARE bare metal, and whether that
pack should read as black bars on them is Pixelcoat's question. The hosts'
`steel` surface stock (`_surface_stock`) was not in the sweep.

**2. The breached state was not repeatable.** Two builds of `_breached` from
the same inputs wrote different GLBs. Measured in Blender 5.1.1, three builds
per process and two processes: `VaultDoor_Shards` came back with the same 272
vertices (sorted digest equal) in a different order each time, and so with a
different COLOR_0; every other part and every other state was identical. The
cause is in `bpylayer/geometry.py`: `subdivide` returned `list(set)` and
`fracture` handed `bisect_plane` a `list(set)` of BMVerts and returned
another, and a BMVert hashes by identity, so a set of them iterates in address
order. Both now return the verts in the bmesh's own storage order
(`_in_storage_order`).

The helpers are shared, and the other callers were worse. `glass_shard`
changed order only; `rubble_frag` (fracture, then `displace_lobes`, one draw
per vertex) and `litter_scrap` (subdivide, then one draw per vertex) changed
GEOMETRY from build to build, because the draws landed on other vertices.
After the change all three and the vault repeat within a process and across
two. Their shapes now differ from any earlier build, which no earlier build
could promise either.

NOT FIXED, found on the way: `pebble` still writes a different COLOR_0 order
each build with identical vertices and colours per vertex. It is not Zoo's
code -- `bmesh.ops.create_uvsphere` itself returns its faces in a different
order each call in Blender 5.1.1 (four calls, four face-order digests, one
vertex digest; `create_cube` and `create_cone` are stable). `add_ellipsoid`
and `add_hemisphere` wrap it, so bollard, cheesesteak, exhaust_fan, helmet,
pebble, pendant_fixture, satellite_dish and soda_cup are exposed. Sorting the
faces after the op is the obvious fix and is not made here.
`add_hemisphere` also feeds `bisect_plane` a `list(set(...))`; not measured.

**Numbers.** The kit rebuilt through `tools/zoo_cli.py --build-kit` against
the vault slot alone: all four states PASS, 6,696 / 6,696 / 7,736 / 7,686
triangles, and `tools/coplanar_probe.py --glb` reports 0 coincident pairs on
each. Rebuilt in a second process, all four GLBs are byte-identical to the
first; at 0.85.0 the same comparison differed on `_breached`.

**Seen.** Godot 4.7 (gl_compatibility, RTX 2060) frames through the factory's
`tools/look_shots.py` of scratch copies of the vault-room walk, one per build,
at five given stations (vault_front, vault_wide, vault_side, vault_back,
vault_inside) with the locked, open and breached node shown in turn: the
before copy reproduces the original frame to the decimal (plate mean 104.7,
std 33.9). After, the surround, straps, frame and leaf read as flat grey paint
with the rivets and bolt rings picked out, and the wheel and dial darker bare
metal. The breached scorch round the lock was not checked against the paint.

`tests/test_vault_door.py`: a pure test that the genome and every style are
`metal_painted` and the finish table covers every genome part with no plate
part bare; a bpy test that no bare polygon on any state at 0.3 or 0.6 m is
0.5 m wide or more (and that only `HARDWARE_PARTS` are bare); a bpy test that
three builds of each state write the same GLB; and a bpy test that
`glass_shard`, `rubble_frag` and `litter_scrap` build the same vertices three
times. `tests/test_material_options_closed.py` moves `vault_door` from BARE to
PAINTED. Run inside Blender against 0.85.0's code, 6 fail: the finish test,
the plan's style material, the painted list, the bare-polygon test (on the
missing table; the same walk as a probe measured 3.618 m there), the
same-file test (3 digests for `_breached`) and the helper test (on
`glass_shard`). Suite: 1344 passed, 94 skipped in plain Python (0.85.0:
1343 / 91); 1419 passed, 19 skipped inside Blender 5.1.1 (0.85.0: 1415 / 19).

## [0.85.0] - a fire hydrant that is a fire hydrant

The walker, in the walk copies: what are the "white boxes at the foot of the
stop signs"? Measured by Level Factory in `_runs/walk_9052_rain`, they are
`cover_81`, Lot's `fire_hydrant_37`, the one hydrant on that site.

**What 0.79.0 shipped, measured before anything moved.** The walk's
`cover/prop_fire_hydrant_delco_1997_01_w35_d35_h75.glb` (cold run 9052's site
kit job): one visual part, `FireHydrant_Body`, 44 tris -- the minting
placeholder's 6 mm bevelled box -- a 12-tri collider, one material,
`M_Skin_metal_painted_delco_1997_807d75`, the tintable `metal_painted` pack
times the genome's grey. Rebuilt from this repo at 0.83.0 through
`build_module` with that job's Pixelcoat output, the GLB came back
byte-identical, so every measurement below is on the path the walk took.

**What Lot asks for, kept.** `site_furniture.SPECIES["fire_hydrant"]` is
(0.35, 0.35, 0.75), the genome default; the slot is centre-pivot, exact fit,
`metal_painted`, collision the full box. The stem is unchanged, the module
fits the slot to the 0.1 mm the facts are rounded to, its bounds are centred
on the origin, and the collider is still the slot's box.

**The recipe is rebuilt** (`recipes/fire_hydrant.py`, every size and colour
in the new pure `core/hydrant_forms.py`). An American dry-barrel hydrant,
pumper outlet toward -Y (the species convention for a front), hose outlets
toward +X and -X:

  * a ground collar, the traffic flange with six hex nuts, a lower barrel
    tapering from 90 to 84 mm apothem, the upper barrel flange with six nuts
    and the nozzle section;
  * two 2 1/2 in hose outlets and a 4 1/2 in pumper outlet, 0.477 m to the
    centre at Lot's slot, each a stub, a cap with a chain lug and a
    pentagonal nut, and a hanging chain from the lug to an eye on the
    nozzle section;
  * the bonnet flange with five nuts, a faceted four-ring dome, a hold-down
    disc and the pentagonal operating nut.

Ten parts (`FireHydrant_Collar`, `_Barrel`, `_Nuts`, `_HoseNozzles`,
`_PumperNozzle`, `_HoseCaps`, `_PumperCap`, `_Bonnet`, `_OperatingNut`,
`_Chains`), every round part a 12-sided prism with a face toward each axis,
every edge hard. Genome version 2, attachments `ATT_top` and `ATT_pumper`.

THE SLOT IS EXACT AND NOTHING IS SCALED PER AXIS: a barrel stretched on one
axis is an ellipse. One scale comes from the tightest axis and the slack goes
to the part that can be longer -- the hose stubs take X, the pumper stub -Y,
the lower barrel Z. At Lot's slot the scale is 1.0 and the stubs are 20 and
43 mm. Any positive slot fits: the uniform scale leaves every axis at least
its nominal slack, which a first draft's two ValueErrors did not know (no slot
could raise them; they are asserts now, and a test holds the bound on three
slots outside the genome). The long corner is honest about it: at
0.297 x 0.42 x 0.9 the pumper stub is 159 mm.

**Paint by seed** (a `hydrant_paint` stream off the module stem), from the
period's common municipal patterns: NFPA 291 chrome yellow with the bonnet and
caps coded by flow class (AA light blue, A green, B orange, C red), yellow
with a white top, red with a white, silver or black top, and aluminium with a
coded or red top. CHOSEN, not surveyed -- nothing here is checked against a
1997 Delaware County photograph or says which authority painted which. The
collar is the body's paint at 0.45, the chains tinted `metal_bare`. A prompt
colour paints the body. Kit style 1, which every current Lot site asks for,
draws `red_black`, so every hydrant the walker sees today is a red body with a
black top; across 40 styles the draws are 13 yellow_coded, 7 yellow_white,
6 red_silver, 6 silver_red, 3 red_black, 3 red_white, 2 silver_coded.

**Wear** is the existing pass (`geometry.wear_colors`: concavity, seeded
grime, the style's ambient) with a grime ramp 0.25 m off grade on top. Level
Factory 0.86.0's `zoo_worldskin.gd`, importing a scratch copy of the walk,
prints "4 material(s) draw vertex colour" for this module.

REFUTED on the way, each kept in the file it was found in:
- a 10 mm chain lug and a 12 mm eye. The end link runs straight into both
  along the outlet, so its sides stood 1.25 mm off theirs and the probe
  reported four SAME pairs on every build;
- a 7.5 mm link on 2.8 mm wire. A chain hanging in one vertical plane gives
  every link a side along the same horizontal, so neighbours' faces stood
  (W - T) / 2 apart: 1.99 mm at the genome's smallest slot, four SAME pairs.
  8.5 on 2.5 mm leaves 2.55 mm there, and `chain_side_gaps` is tested;
- aluminium at (0.46, 0.47, 0.47) rendered as white paint on the pack's
  near-white grain. It is (0.34, 0.35, 0.35) now and still reads pale in
  Cycles; no walk frame has shown it, since style 1 is not silver;
- the bonnet's nuts in body paint read as red dots on a black bonnet; they
  are painted with the bonnet.

**Numbers.** `tools/coplanar_probe.py`'s own `probe` over 214 builds -- min /
default / max and the mixed corners at styles 1 and 2, 40 random slots at
styles 1 and 2, 60 more at styles 3 and 5 -- found 0 SAME and 0 OPP pairs,
every build PASS. It can fail: the pumper cap duplicated in place reports 18.
Triangles are `hydrant_forms.triangles` exactly (1,212 plus 12 per chain
link; a bpy test holds it equal to the build): Lot's slot 1,416; the worst
corner, 0.42 x 0.42 x 0.637, 1,680, where the stubs and so the chains are
longest; over 40,000 random slots in the genome, 1,416 to 1,680. Budget
200 -> 1,700. One hydrant stands per crossing (walk 9052_rain has one); six
on a street cost about 8,500 tris, under three of this kit's cars.

**Seen.** Cycles renders through `tools/preview_specimen.py --slot` (the
worktree's `zoo_keeper` printed as the one imported) from 1.6 m at front,
three-quarter and side, and three more schemes. Then Godot 4.7 frames through
the factory's `tools/look_shots.py` of two scratch copies of walk 9052_rain,
each with Level Factory 0.86.0's import script and a fresh import, differing
only in this module: four given stations round `cover_81` under the walk's
rain preset. The grey box is a red hydrant with a black bonnet and caps, the
chains visible from 1.2 m; frame means move by under 0.5 of 255.

NOT ZOO'S, and not changed: Lot stands every hydrant at `yaw = road angle`
(`site_furniture.py`, the per-cut loop), and by `plate_facing` a module's -Y
points toward the road only on an L kerb. `cover_81` is on road 1's R kerb,
so in walk 9052_rain the pumper faces the buildings. Turning an R-kerb
hydrant 180 degrees, as `_bus_stop` turns its shelter, is Lot's change.

`tests/test_fire_hydrant.py` is rewritten: pure tests over Lot's dims and the
nominal layout, exact extents over the corners and 30 random slots, stub and
barrel minimums, undersized slots, outlet height and clearance, facing, taper
and bury, nuts on their flanges and off the 12-gon's face directions, chain
gaps and floor, the triangle count at the worst corner, scheme weights,
determinism, variety, flow-coded tops, a prompt colour and the genome's
parts; and bpy tests for fit, parts, budget, triangle formula and collider at
eight slots, the pumper cap as the -Y face and the hose caps as the X faces,
the same vertices every build, and zero SAME pairs at seven slots at two
styles. The file was run inside Blender 5.1.1 for this release: 85 passed.

## [0.84.0] - the rooms get what was missing: five interior species, and stock on the tops

The walker, in the `wine_cellar` basement of `country_club_a01` (walk copy of
cold run 9052): "need a lot more species for this room, its just a bunch of
chairs and tables with nothing on it, boring". What was there, read off that
walk copy: `lot/country_club_a01/art/zoo` holds its chairs and tables as five
modules at five sizes, and one chair module is referenced 57 times across the
walk copy's scenes. The room (`objective_room` `wine_cellar`) matches none of
Deli Counter's furniture keywords, so it got
`level_design._FURNITURE_DEFAULT`, a low table and a chair. Zoo's side of that
is two gaps: the species a basement, a bar or a stockroom is made of did not
exist, and nothing ever set anything on a top -- `table.py`'s
`ATT_surface_center` and the desk, counter and filing cabinet sockets were
read by nobody.

This release is the Zoo half. It does not reduce interventions-per-level by
itself: until Deli Counter writes the names and fields below, no generated
room gets any of it. That DC change is described at the end and not made
here (Deli Counter is mid-release).

### Five species, planned as the geometry that ships

Every one is planned in pure Python -- `core/carton_forms.py`,
`furnace_forms.py`, `drape_forms.py`, `pool_table_forms.py`, `booth_forms.py`
-- as vertex and face lists (`core/prims.py`) that `bpylayer/prim_mesh.py`
turns into bmesh faces vertex for vertex, so the unit tests measure what is
exported (before bevel, which only cuts corners inward). `prims.coincident_pairs`
is a pure port of `tools/coplanar_probe.py` at its defaults.

| species | what it is | built tris (kit path, delco_1997) | budget |
| --- | --- | --- | --- |
| `carton_stack` | kraft cartons (tape, labels) and banker's boxes (lids, hand holes) in seeded columns, upper boxes set in and turned 1-3 degrees | 36 at 0.4x0.3x0.3, 132 at 0.9x0.6x1.0, 1104 at 1.2x0.8x1.4, 1824 at 1.6x1.2x1.8 | 2400 |
| `furnace` `form` furnace | almond cabinet, blower and louvred burner doors, galvanised plenum and trunk stub, inducer and flue to the slot's top, black-iron gas line with drip leg and shut-off, return drop when wide | 532 at 0.9x1.0x2.4 and 1.2x1.2x3.0 | 1200 |
| `furnace` `form` water_heater | faceted tank, dome, burner cover, gas valve and knob, EnergyGuide sticker, relief valve and discharge pipe, copper lines with unions, draft hood and flue | 596 at 0.6x0.6x2.4 and 0.5x0.5x1.4 | 1200 |
| `dust_sheet` | a cloth over a hidden profile drawn from the seed -- chest, armchair, sofa, stack, table (legs showing), lump -- folded skirt, pooled corners, turned hem | 352-360 at chair/chest sizes, 540 at 2.0x0.9x0.85, 678 at 3.2x1.6x2.2 | 1000 |
| `pool_table` | 1990s coin-op bar table: castings, rails with sights, angled cushions, cloth in one of three bar colours, cabinet on corner posts, coin slide, ball return, balls and (65 % of seeds) a cue | 1360 at 2.0x1.14x0.79, 1468 at 2.8x1.6x0.84 | 1600 |
| `booth_seat` `form` booth | wood end panels, recessed kick, vinyl seat, channel-tufted back leaning 5-9 degrees, cap rail; back to back on one spine at 1.05 m deep or more | 740 at 1.8x0.75x1.15, 1428 at 2.4x1.4x1.2, 2384 at 4.0x1.6x1.4 | 2600 |
| `booth_seat` `form` sofa | turned feet, skirted base, rolled arms, crowned seat and back cushions, throw pillow on 70 % of seeds | 650-764 | 2600 |

Budgets are the largest genome size measured, not a guess: rooms carry many of
these. `furnace` form `auto` is the water heater for a squarish footprint no
more than 0.8 m on its long side; `booth_seat` `auto` is the booth at 1.0 m
tall or more. Furnace and water heater stand on a concrete pad that is the
slot's footprint and run the flue to the slot's top, so the volume should be
authored to the ceiling. Every genome carries `delco`, `1990s`, the three
theme styles and keywords (`intent.parse("water heater")` is `furnace`,
`"couch"` is `booth_seat`, `"phone booth"` is still `payphone`).

### Surface stock: `recipes/_surface_stock.py`

`_shelf_stock.py`'s twin for a top. `desk`, `table`, `counter` and
`filing_cabinet` gain a `stock` param -- `none` (the default), `office`,
`bar`, `kitchen`, `vault`, `storage` -- and `module_variants: 4`. The host
calls `prim_mesh.build_stock` once per bay of its top (a desk per row and bay,
facing that row's sitter and stopping short of the transaction ledge; a
counter keeping 0.22 m round every `ATT_register`), from its own "stock"
stream.

  * **office**: CRT with its keyboard in front, folders with forms, desk
    phone, mug, pencil cup. **bar**: bottles in a knot, pints on coasters, an
    ashtray with butts, napkin holder. **kitchen**: ketchup, mustard, salt and
    pepper, a tray with soda cups, cups, napkins. **vault**: strapped cash in
    columns, deposit bags, ledgers. **storage**: a carton or banker's box
    (`carton_forms`' own), a clipboard, forms.
  * Clusters: about one per 0.22-0.45 m^2 of top, each a group about one
    anchor. Off kilter by rule: an item turns off its cluster's line by up to
    `min(15, 2.0 / size_m)` degrees; stacked items turn at least 1 degree
    from the one below so no two sides are parallel.
  * No overhang (every vertex inside the top less 2 cm); footprints keep 12 mm
    apart; lowest faces sink 3 mm into the top and no part has a face between
    the top and 4 mm above it. A body finish takes whichever of its candidate
    colours contrasts most with the host top, and holds a luminance ratio of
    1.4 against every style of all four hosts.
  * Built tris with stock (kit path): desk 504-1236 at 1.6x0.8x0.75 (bare
    396), table 292-716 at 1.2x0.8x0.74, counter 272-780 at 2.2x0.8x1.05 and
    508-1364 at 8.0x0.9x1.05, filing cabinet 828-1100 at 0.9x0.5x1.4.
    `counter`'s budget goes 500 -> 1600 for that; the others had room.

**A host with `stock` none is byte-identical to 0.80.0.** Measured, not
argued: seven host modules (desk x2, table x2, counter, filing cabinet x2)
built through the kit path from a `git archive` of main and from this branch
give the same sha1 over object names, vertices to 0.1 mm and Wear colours;
`tests/test_interior_bpy.py` pins those digests. The mechanism is that
`build_stock` returns before touching `streams` when the flavour is `none`.

### The contract: `kit.DRESSING_FIELDS` -- `form`, `stock`, `variant`

A prop slot may carry `stock` (a flavour), `variant` (0 to the species'
`module_variants` less one) and `form`. `kit.honour_dressing` keeps them only
when the species the slot is BUILT as honours all of them, and drops all three
otherwise, reported in the plan's and the kit index's `dressing_fallbacks` and
printed as `[zoo] DRESSING FALLBACK`. All or nothing is the contract: Deli
Counter cannot read a genome, so its resolver can try only the name with every
field it wrote and the name with none. `variant` on a host without `stock` is
dropped (it would change nothing but wear noise).

`kit.module_stem` gains `form=`, `stock=`, `variant=`:
`<type>[_<species>]_<theme>_<style>[_w][_d][_h][_f<form>][_s<stock>][_n<variant>][_v][_o][_<state>]`.
Absent, `stock` "none", `form` "auto" and `variant` 0 add nothing, so every
existing name is unchanged (`test_a_slot_without_the_fields_plans_what_it_always_did`).
The fields are in the bucket key, `dna.resolve_module_plan` puts the honoured
ones into `params` and `module`, and a module's streams are seeded by its stem
-- so the variant index is the seed.

### Stock is measured apart from the slot

REFUTED FIRST: stock built into `objects` like any part. All 15 of the first
stocked host renders built with status FAIL (`fit_height`, `fit_pivot`):
`build._recentre` centred the host on host-plus-stock, which for a 0.75 m desk
under a 0.37 m monitor is, by arithmetic, 18.5 cm into the floor where Deli
Counter places it. Recipes now also return the stock as `dressing_objects`;
`_recentre` and `export.gather_facts(..., dressing=)` leave those out of the
bounds and centre (they still count toward tris and parts). An empty
`dressing` measures as before.

### Refutations kept

  * `prim_mesh` first built nothing beveled: `bmesh.faces.new` leaves face
    normals zero until `normal_update`, and `bevel_edges` selects by the angle
    between normals -- the first furnace built at exactly its pre-bevel 372
    tris.
  * carton_stack: GAP 6 mm put two tapes back to back at 0.0 mm (30 of 240
    seeded stacks); banker's lids turned a degree swung 5 mm into the
    neighbour's gap (0.6 mm pair); a label flush with a carton's side lay
    1.9 mm from it; a lid rising 4 mm left the box above 1 mm from the body
    below. All in `carton_forms.py` above what replaced them.
  * water heater centred on its pad: the gas valve knob stood 3 cm past a
    0.6 m pad and `fit_exact` squeezed the heater 10 % (`overshoot_m` 0.0315).
  * dust_sheet: 8 cm skirt room rendered a 2 m sheet as a box in a
    tablecloth; a lump peaked between grid points up to 23 cm under h; a lump
    at 1.8 m rendered as a spike. pool_table: a 4.5 cm cloth drop left balls
    8 mm over the castings; butt and shaft of the cue overlapping at the
    joint lay on one cone. booth_seat: channels leaning about their foot
    went through a back-to-back spine; parts buried to one depth in the end
    panels shared end planes; seat and channel end planes coincided where
    both runs split at x = 0. Each kept at its fix.
  * surface stock: a workstation's anchor drawn over the whole top so rarely
    fit a 0.8 m desk that the first renders had monitors with no keyboard;
    a small cabinet top that drew the workstation stayed bare. Anchors are
    drawn where the group fits, a failed group gives way to another, and a
    group sheds its last member every 12 tries.

### Verification

  * `tests/test_interior_species.py` (149): dims contract, overshoot <= 12 mm
    before `fit_exact`, colliders inside bounds, zero coincident pairs, budget
    before bevel, determinism, seeds differ, every profile drawn, keyword
    routing, forms through the kit -- over each genome's min/default/max
    corners, render sizes and both forms.
  * `tests/test_surface_stock.py` (80): no overhang, no shared plane with
    another item or the host top (5 flavours x 6 tops x 10 seeds), gaps,
    determinism, off-kilter, keep-out, contrast against every host style,
    and the slot-field contract.
  * `tests/test_interior_bpy.py` (37, skipped without Blender; run inside
    Blender 5.1: 37 passed): main's host digests, 20 stocked hosts keep status
    and pivot with no SAME-facing stock pair, 10 species builds pass within
    budget with zero coincident pairs by `coplanar_probe.probe`, rebuilt
    identically.
  * A 60-module Blender sweep (species at 20 sizes/forms/variants, 4 hosts x
    5 flavours x 2 sizes): 0 SAME-facing coincident pairs, all deterministic,
    no fallbacks, every stocked host carries stock. The new species also
    have 0 OPP pairs; the hosts' OPP rows are their own existing contacts
    (legs under tops, drawer fronts on pedestals), not stock.
  * `tools/preview_specimen.py --species S --dims W D H [--stock --variant
    --form]` renders the module the kit would ship, standing on the ground,
    and prints where `zoo_keeper` was imported from. Renders of every
    species and of desk, table and counter with each flavour were looked at.
  * Suite: 1146 passed, 61 skipped (plain Python); 1188 passed, 19 skipped
    inside Blender 5.1.

### What Deli Counter must add (not done here)

  1. **Slot fields** on every prop slot `deli_counter.py` emits: `stock`,
     `variant`, `form` (None, 0, None when unset) from new `Volume` fields.
  2. **`themed_tscn.module_stem`** mirrors `kit.module_stem` exactly: the
     three keywords, suffixes `_f<form>`, `_s<stock>`, `_n<variant>` after
     `_h`, "none"/"auto"/0 adding nothing. `resolve_themed_stem` passes the
     slot's fields for volume roles; `resolve_slot_ref` tries the slot, then
     the slot with the three fields cleared, then the box.
  3. **`prop_species.PROP_SPECIES`** rows, ahead of the rows that would claim
     the names first: `("carton", "banker", "file_box", "box_stack")` ->
     `carton_stack` before the `None` row (whose `stack` would take
     `box_stack`); `("dust_sheet", "sheeted", "draped", "covered_")` ->
     `dust_sheet` before chair and table; `("pool", "billiard")` ->
     `pool_table` before `table`; `("booth", "banquette", "sofa", "couch",
     "settee", "loveseat")` -> `booth_seat` before the chair row (whose
     `seat` would take `booth_seat`); `("furnace", "boiler", "water_heater",
     "heater")` -> `furnace` before `tank`.
  4. **Names and fields to write** (`level_design._FURNITURE`): utility and
     basement rooms `furnace` 0.9x1.0x storey and `water_heater` 0.6x0.6x
     storey against a wall (form `water_heater`); storage, stock and cellar
     rooms `carton_stack` 0.5-1.6 x 0.3-1.2 x 0.3-1.8 and `dust_sheet` over a
     table-sized floor volume; bar, lounge, tavern and game rooms
     `pool_table` 2.0x1.14x0.79 on the floor, `booth` 1.8x0.75x1.15 on a wall,
     `counter_bar` with stock `bar`; lobby and waiting `sofa` 2.0x0.9x0.85;
     every desk `stock` office, `table_work` in a vault or count room `stock`
     vault, kitchen and deli counters `stock` kitchen, supply cabinets
     `stock` storage; and a cellar or a room matching no row gets cartons and
     a dust sheet rather than the table-and-chair default. `variant` =
     crc32(slot_id) % 4. `_prop_material`: `furnace`, `heater` -> metal.
  5. **Height advisory**: `portable_building.verify_placement` compares the
     module's visual height with the slot's; a stocked host measures up to
     about 0.4 m over (a monitor), past its 0.25 m tolerance. Advisory only,
     but it will warn unless `Stock_` nodes are left out of that height.

Rebased onto 0.83.0 (the entry was written against 0.80.0). Four files
conflicted because 0.81.0 and 0.83.0 had grown the same seams, and both
features are kept whole:

  * `core/kit.py` `plan_kit`: 0.83.0's `state_art` cache and
    `state_geometry_notes` sit beside this entry's `dressing_fallbacks`; the
    dressing fields are honoured before `slot_variants(..., state_art=_art)`
    runs, so a module stem carries `_f/_s/_n` before `_v/_o` and the state
    suffix last. Both lists are returned.
  * `bpylayer/export.py` `gather_facts(collection, root_name, fit_names=None,
    dressing=())`: dressing is set aside first, the envelope is the named fit
    objects among what remains, and `overhang` stays the bounds of every
    visual mesh. `bpylayer/build.py` `_recentre` measures `fit_objects` (or
    all objects) less `dressing_objects`, `build_module` passes both, and the
    kit index carries `state_geometry_notes` and `dressing_fallbacks`.
  * `tools/preview_specimen.py`: 0.81.0 already parsed `--dims` (after `--`)
    and `--style`; the branch's second `--dims` parse is dropped, and its
    `--stock/--variant/--form`, fallback lines and delco_1997 default theme on
    the kit path join 0.81.0's `--style` and 0.83.0's `--slot/--state/--flank/
    --target-z`. The import line is 0.83.0's (version and folder).
  * Not a textual conflict: `tests/test_interior_bpy.py` loaded
    `coplanar_probe.py` by cutting the source at its last `main()`, which
    0.83.0 put under `if __name__ == "__main__":` -- all 30 of its build tests
    failed with an IndentationError inside Blender until the whole file was
    loaded as a library instead.

After the rebase: 1277 passed, 74 skipped in plain Python (0.83.0 1031/32,
this branch 1146/61, 0.80.0 900/19: exactly the union); 1332 passed, 19
skipped inside Blender 5.1.1 (0.83.0 1049/14, this branch 1188/19, 0.80.0
905/14). The seven stock-less host digests still match, so a host without
stock is unchanged by 0.81.0-0.83.0 as well. A kit build of the four vault
states, a desk with office stock variant 2, a water heater, a cargo container
and a waiting-chair row validates PASS with 0 SAME-facing coincident pairs on
every GLB by `coplanar_probe.probe`, and each module's geometry digest equals
the one its own side builds alone -- except `_breached`, whose
`VaultDoor_Shards` comes back in a different vertex order from run to run on
0.83.0 by itself (three runs, three digests, one sorted vertex set); its
sorted vertex set matches, and every other part matches in order and wear.

Unverified: the survey's "272 of 691 library rooms hit the default" was not
re-derived here. Textured (Pixelcoat) looks were not rendered -- every render
is the flat path, and the contrast rule is against genome colours, not
against a non-tintable pack. The DC side above is untested because it is not
written.

## [0.83.0] - the bank vault is a round door, in every state the machine names

The walker, on walk 9052 (bank_branch_a02 basement): "the bank vault should
absolutely be a hero piece". What stands there is Deli Counter's 5 x 5 x 3 m
`VAULT` box volume, a `prop` slot with no species. What Zoo had for a vault
OPENING was a closed-only box -- a rectangular leaf and a hub cylinder in a
jamb portal -- whose open and breached states reused `doorway` and `breach`,
and whose unlocked state was deferred as identical art. Nothing shipped used
it: of the specs in `deli_counter/specs`, only `bank.json` has a `vault`
opening and that building is not modular, so no `slots.json` in
`deli_counter/build` carries a `vault_door` slot.

**`vault_door` (genome v2) builds a round bank vault door per state.** A
riveted steel surround in a strap grid; a stepped round frame with a stepped
jamb through the wall and a ring of brass bolts; a thick stepped leaf with an
eight-spoke wheel in a riveted ring, five locking bars to keepers, a
combination dial with a spoked handle and a U pull; two hinge barrels with
knuckles, pins, plates and arms on the viewer's left. `unlocked` turns the
wheel a sixteenth and draws the bars out of their keepers; `open` swings the
leaf 100 degrees on its hinge axis with 16 bolts standing off its edge, bolt
ports in the lining and a boltwork boss on its back; `breached` over-swings
it to 122 degrees and leans it 13 degrees off its hinges, blows the dial out
into a torn-plate rosette on both faces, drops the wheel on the floor, shears
the bars and leaves their blocks in the keepers, scorches the lock side and
scatters shards under the 0.1025 m unassisted step. Delco_1997 skins it with
the tintable `metal_bare` pack in four tints (steel, bright, dark, brass).

Measured on 3.6 x 0.6 x 3.3 and 3.6 x 0.3 x 3.3 slots with a 1.3 x 2.1 m
aperture: every state validates PASS, fits its slot to 1 mm (the frame, for
the swung states), 6,600 to 7,736 triangles against a 9,000 budget -- a hero
budget, one per bank, beside a desk's 8,000 -- and `tools/coplanar_probe.py`
reports 0 coincident pairs of either facing on all eight GLBs.

**`core/vault_forms.py` (pure) decides every position.** THE PORTAL
CIRCUMSCRIBES THE AUTHORED APERTURE: the circle runs through the rectangle's
corners and is cut flat at the sill, where its chord is exactly the authored
width, so the round door never narrows a passage Deli Counter gated. A slot
too small for the circle, the frame and the hinges (`required_size`: 3.58 x
2.66 m for 1.3 x 2.1) builds the whole door at a slot that is big enough and
scales it uniformly across and up to the real one (`fit_scale`), with every
face-separating gap authored in real millimetres, and prints
`[zoo] VAULT_PORTAL_UNDERSIZED` with the clear width left. Deli Counter's
current vault slot, 1.4 m wide round a 1.4 x 2.3 aperture, builds PASS at
x0.360 with 0.50 m clear and 0 same-facing pairs, and looks like what it is:
a porthole at the foot of a steel column. REFUTED, kept: shrinking only the
portal inside the real slot left the wheel and bars at their minimum sizes
and built that slot 3.499 m tall in 3.3 m. One flat-cut lathe
(`cut_lathe`) builds every ring and the stepped leaf as a single closed
solid, because stacked discs cut at one plane lay their bottoms in that plane.
Collision per state follows `interactives.py`'s advice: locked and unlocked
are the slot box; open and breached are the slot less six passage bands
inscribed in the circle -- the bottom band exactly the authored width, the top
at the authored head height -- plus four boxes round the swung leaf, which
tests hold clear of the approach in front of the aperture.

**`kit`: a species may draw its own states.** `slot_variants` deferred every
state mapped to the default species as identical art. A genome's `state_art`
now names the states it builds itself, and those are built. A slot mapping
such a state to another species is honoured and reported in
`state_geometry_notes` and the kit index, printed as `[zoo] STATE GEOMETRY`
-- Deli Counter's shipped machine maps `open` to `doorway` and `breached` to
`breach`, so both are reported until it maps them to `vault_door`.

**`build`: a module may declare what fits.** A leaf swung out of its frame
cannot fit a wall slot and must not drag the frame off the slot centre. A
recipe's `fit_objects` are what `_recentre` and `gather_facts` measure; the
full reach is reported as `facts["overhang"]` and written to the module meta
as `overhang_bounds`, with the vault's portal and shortfall beside it.

**`tools/preview_specimen.py --slot <slot.json> [--state s]`** plans one Deli
Counter slot and builds the chosen state's module through `build_module`,
stands it on the ground, and prints which `zoo_keeper` it imported. `--flank`
stands a wall either side, `--target-z` aims the camera, `--world` sets the
environment strength (bare metal mirrors a black world as black).
`coplanar_probe.py` runs `main()` only as `__main__`, so a test can import
`probe`.

REFUTED on the way, each kept in the file it was found in:
- the first render was a mirror image. From the face, +x is the viewer's
  LEFT; the hinges were built at -x and hung on the right;
- the passage bands topped out at `zc + 0.8 R`, 6 cm under the aperture's
  head;
- the hinge arm's back (`f - 1.5 rb` = 0.0777) landed 0.28 mm from the
  frame's buried face plane (`y_pan - 0.012` = 0.0780), one of nine
  coincident pairs from offsets picked where each part was written. They now
  come from one table with 4 mm spacing;
- a 0.3 m slot built 0.332 m deep (knuckle rings past both faces), then
  0.3056 (keeper bolt heads past the face whenever u < 0.175) -- both inside
  `validate`'s 2 cm tolerance, both caught by the 1 mm test;
- fracturing shards in the shared bmesh left the verts the cuts made at the
  module origin: black spikes in the doorway;
- a scorch of 0.65 R reached the export (lock hardware COLOR_0 0.26 against
  0.83 open) and could not be seen. At 1.0 R the frame's lock side measures
  0.334 against 0.606 on the hinge side;
- the genome said 8 degrees, 14 bolts, 0.12 m while `vault_forms.DEFAULTS`
  said 13, 16, 0.16, and module builds read the genome. A test now holds them
  equal.

`tests/test_vault_door.py` is rewritten. It has 22 pure tests (portal,
bands, collision, swing, lathes, planning, genome agreement, budget) and 2
bpy tests that build all four states at 0.6 and 0.3 m and assert PASS, a
1 mm fit, the budget and zero coincident faces. The bpy tests were run inside
Blender 5.1.1 for this release (2 passed), and the check was shown able to
fail: duplicating one part in place reported 10 pairs.

NOT BUILT: the barred day gate from the third reference.

Merged onto 0.82.0: `tools/preview_specimen.py` keeps both 0.81.0's `--dims`/`--style` and this entry's `--slot`/`--state`/`--flank`/`--target-z`, and its framing drops collision shapes by suffix as well as hidden ones.

## [0.82.0] - a cargo container that is a shipping container

The walker, walk 9052_rain, looking at the overlay's `CargoContainer` under
`cover_136`: "this needs some more love to look like a cargo container". The
references were a red 40 ft door end, a weathered grey-blue 20 ft with rust at
the rails and fork pockets, and a clean orange 20 ft at 6.06 x 2.44 x 2.59 m.

**What 0.80.0 shipped, measured before anything moved.** The walk's
`cover/prop_cargo_container_delco_1997_01_w244_d606_h259.glb` (cold run 9052's
site kit job): one visual part, `CargoContainer_Body`, 44 tris -- the minting
placeholder's box with a 6 mm bevel -- and a 12-tri collider, on one material,
`M_Skin_metal_painted_delco_1997_807d75`. That is the delco_1997
`metal_painted_neutral` pack (Pixelcoat 0.16.0: 128 px, 1.2 m a tile, albedo
232..255 in every channel, `tintable`) times the genome's grey. There was no
corrugation in the mesh or in the texture, and the only variation on a 6 m
face was per-vertex wear noise over 48 vertices -- the "plain flat box with a
blotchy green-grey noise skin".

**What Lot asks for, kept.** `site_cover.COVER_SPECIES` parks
`("cargo_container", 2.44, 6.06, 2.59)`, the genome defaults, at yaw 0 or 90;
`lot.cover_module_refs` resolves the stem above; the module is centre-pivot,
exact-fit, length along +Y, collision the full box. None of that changes, and
the stem Lot looks for is the stem this builds.

**The recipe is rebuilt** (`recipes/cargo_container.py`, decisions in the new
pure `core/container_forms.py`). Door end at -Y, blind end at +Y:

  * eight ISO 1161 corner castings are the envelope, their apertures painted
    on the slot's faces; corner posts; top and bottom side rails; top and
    bottom rails across the blind end; door header and sill;
  * trapezoidal corrugated sides and blind end (300 mm pitch, 40 mm deep, a
    39 degree flank -- slightly coarser than a real panel's 280 / 36 so each
    flank is a facet wide enough to shade) and a corrugated roof (420 / 20);
    every sheet edge runs into the frame member beside it;
  * two door leaves, each a frame ring and a pressed infill with four
    channels under a flat top band; four locking bars with cam keepers top
    and bottom, two guides each, handles and retainers; four hinges a leaf; a
    dark seam backer;
  * fork pockets (360 x 115 mm) in the bottom side rails of 10 and 20 ft
    boxes, 2050 mm apart on a 20 ft (900 on a 10 ft is chosen, not tabled);
  * ISO 6346 markings from `_legend`'s faceted glyphs, flat and cut at every
    rib break so each piece lies on its own crest, flank or valley: owner
    code, serial and a boxed check digit (the ISO algorithm; the standard's
    CSQU 305438 3 is a test) on the right leaf and both sides, the size-type
    code (12G1 / 22G1 / 42G1 / 45G1 / L5G1 from the slot's length and
    height), a GROSS / TARE block, a CSC plate, a warning triangle, and on 55%
    of boxes an invented carrier name down each side (SEAHOLT, PORTALIS,
    TRADEPAC, GALEOTA, ALBATROS; leasing prefixes DCR, BFA, HLS, CGT, CFR --
    none checked against the BIC register);
  * paint from a period palette by the module's seed (red, maroon, orange,
    blue, grey-blue, green, grey, a dirty white that takes dark lettering);
    rust streaks hanging off the top rail and blooming off the bottom rail,
    never over a marking; a primer or darker touch-up patch on some walls.

Size class comes from the slot: nearest of 10, 20, 40, 45 ft by length, so a
Lot slot at 6.06 builds a 20 ft box with pockets and a 12.19 slot a 40 ft
without. The genome's ranges were the minting tool's (depth to 12.12, which a
40 ft box at 12.192 is outside); they are now ISO's -- width 2.30..2.50,
depth 2.90..13.80, height 2.40..2.95 -- with the defaults unchanged. Genome
version 2, attachments `ATT_top` and `ATT_doors`.

**`_legend` carries a stencil alphabet.** A B C D E F G H I L R U and 0-9 join
S T O P, on the same grid under the same rule (a cut corner is only a stroke
by stroke cell); letters with a diagonal stroke do not fit it and are left
out, and a test holds every carrier, prefix and code to the set. A space in
`legend()` advances and emits nothing. The stop sign's word is unchanged.

**Refuted in the build, kept in `container_forms.FORM_SHADE`.** The first
module photographed in a scratchpad copy of walk 9052_rain (Godot 4.7, GL
Compatibility, the rain preset) showed the corrugation almost gone: under an
overcast sky every facet of a rib gets the same light. The same module under
a sun in Blender read strongly. The shade was first baked into the `Wear`
colour; the GLB carried it (walls' COLOR_0 median 0.863 -> 0.515) and the
frame did not move (patch-free strip of the side wall, mean luma 47.4 -> 47.1,
3 px column step 3.32 -> 3.07). The dial was dead: every surface of the
imported container, car and box truck in that walk has
`vertex_color_use_as_albedo = false`. Crests, flanks and valleys are now
separate surfaces on the paint at 1.0 / 0.80 / 0.66
(`CargoContainer_Walls` + `_Doors`, `_RibFlanks`, `_RibValleys`): mean luma
47.1 -> 43.7, column step 3.07 -> 3.93, and the ribs and door channels read
at 7 and 20 m in the frames.

NOTE, not Zoo's: that measurement means no cover module's wear or ambient
vertex colour is drawn in a walk today (Level Factory's `zoo_worldskin.gd`
prints `not a kit module, left alone` for them). Also noted and not isolated:
in the rain frames the narrow up-facing strips -- rail tops, the sill,
keeper tops -- carry a bright dashed highlight; Lux's rain runtime has no
wetness or splash shader, so it is not a rain decal. And
`tools/preview_specimen.py`'s specimen path stands a centre-pivot species half
under its ground plane (only `build_module` recentres); the container was
judged from kit-path renders.

**Numbers.** `tools/coplanar_probe.py`'s own `probe` over 118 builds (min /
default / max of every axis at two styles, the ISO nominal sizes at three
styles, 40 random slots) found one SAME pair: a glyph edge 0.3 mm from a rib
break cut into a 0.3 mm sliver, reported at 1.63 mm because a triangle that
thin has no trustworthy normal. `split_at` now snaps a vertex within 1 mm of a
break onto it. Since then 394 builds over three sweeps (100 more random
slots): 0 SAME, 0 OPP, every fit, pivot, collision, UV and wear check passing.
Triangles by class over those sweeps: 10 ft 2,488..3,308; 20 ft 2,650..3,766;
40 ft 2,858..3,910; 45 ft 3,105..4,022 (a carrier name is most of the spread).
Lot's slot builds 2,814. Budget 200 -> 4,500: a street carrying five
containers costs about what five of 0.79.0's cars do.

`tests/test_cargo_container.py`: every ISO nominal size inside the genome and
Lot's slot at its defaults; class, size-type code and pockets per length;
the ISO check-digit example; corrugation fills its span and ends on crests;
door channels leave the top band flat; a painted polygon cut at the ribs
loses no area and no piece straddles a break or is a sliver; form shades
ordered; every marking spelled from existing glyphs; the palette; a box is
the same box every build and 40 styles give 40 codes and at least 5 paints;
a prompt colour wins; white paint takes dark lettering; rust never lands on a
marking and stays on crests; patches avoid markings; nothing on the door end
stands outside the castings; details clear the probe on a flank. The bpy half
builds the six nominal sizes (fit, pivot, collision, parts, budget) and runs
the coplanar probe on 20 ft, 20 ft at Lot's dims and 40 ft at two styles; it
is skipped without Blender and was run inside Blender 5.1 for this release.

## [0.81.1] - a run of walls has no groove at its joints

Walk 9052, delco_1997, an interior partition: "you can see the seams here", a
thin vertical line at every 2.00 m -- bright from an oblique eye 3.2 m away,
dark from a metre square on.

**MEASURED BEFORE ANYTHING MOVED**, on the walk copy's own `site.tscn` and
module GLBs, every consecutive pair of modules in every `ext_*` / `int_*` run
of all three buildings (a module's visual AABB under its node transform, in
the building frame, metres):

    joints                     434  (strip_retail_a02 52, bank_branch_a02 205,
                                     country_club_a01 177)
    gap along the run          0.000 mm at all 434
    depth-face offset          0.000 mm at all 434
    V-groove 6.00 x 3.00 mm    300 (a 3 mm chamfer on both sides)
    V-groove 0.8 - 6.8 mm      134 (at least one side a wallEnd, the unit
                                     box Deli Counter scales per slot)

Deli Counter lays the run flush and coplanar, so it is not Deli Counter's.
World-triplanar was on and the texture ran continuous across the joint in
the frame, so it is not Level Factory's. What each joint carried was the
style's bevel twice: `wall_delco_1997_02_w200` is a box whose faces stop at
x = +/-0.997 with a 45-degree chamfer out to +/-1.000, and two of those meet
as a V. It is the groove 0.50-era plate tiles lost (`recipes/_arch.py`,
"PLATE TILES ARE UNBEVELED"), kept on walls because "their chamfers sit on
real corners". A wall's END edges sit on the plane its neighbour shares.

**`arch.butt_planes(species, w)`** names those planes, x = -w/2 and +w/2, for
the species a run is made of (`arch.RUN_SPECIES`: wall, wallEnd, doorway,
window, breach). `geometry.bevel_edges` leaves an edge sharp when both its
ends lie on the SAME one of them (`arch.edge_on_butt_plane`, 0.1 mm); a
full-width edge touches both planes and lies in neither, so the top and
bottom chamfers stay, and so do a jamb's reveal, a sill and a header. Plates
declare none (already unbevelled). `prop` shares the slab builder and
declares none: a desk's ends are corners.

MEASURED AFTER, strip_retail_a02's kit rebuilt from this tree (seed 9052,
cold run 9052's slot contract and skin library) and dropped into a scratch
copy of the walk, windows left as shipped:

    wall_delco_1997_02_w200    96 verts / 44 tris -> 48 / 28; x only +/-1.000
    doorway jamb, outer end    +/-0.625 only (was 0.622 / 0.625)
    doorway jamb, reveal       +/-0.505 / 0.508 kept
    joints with a groove       52 -> 4 (the 4 are the untouched windows)

In `look_shots.py` frames at the walker's station (Godot 4.7, GL
Compatibility, Lux Heavy Rain), a per-column line score -- the median over
the wall's rows of |L(x) - mean(L(x-3), L(x+3))|, Rec.709 codes -- put the
four joint columns at 22.4-29.7 against a column median of 4.3; after, the
largest column anywhere in the band is 6.3, the texture's own. One metre
from the joint: 28.2 -> 4.6. No brightness step replaced the line, so per-mesh
light binding (roadmap 83) is not drawing a seam on this wall.

CONTROL: the same kit built from 0.80.0 reproduces the shipped GLBs' vertex
positions exactly (wall, wallEnd, doorway and exterior wall checked), so the
before and after differ by this change and not by the rebuild. The final
tree's 20 run modules are identical to the ones photographed, and its 10 prop
modules are identical to 0.80.0's.

Not changed, and worth knowing: a building's outside corner where a run ENDS
now shows a sharp 90-degree edge instead of a 3 mm chamfer. No frame of one
was taken. Every kit GLB of the five run species changes bytes, so the next
cold run rebuilds them.

`tests/test_butt_joints.py`: the planes per species (runs, plates, prop), the
edge rule (an end edge is a butt edge; a top edge, a reveal and a chamfered
vertex are not), `_arch.py` passing the planes on every bevelled part and
`bm_to_object` passing them to the bevel, and two bpy builds that read the
mesh -- a wall with no vertex inside its end chamfer and its top chamfer
intact, a doorway with its reveal chamfer and without its end one. The suite
skips the two without Blender; run inside Blender 5.1 all 18 pass. Against
0.80.0 the 17 written before the prop case all failed, the bpy two on the
chamfer vertices themselves (+/-0.997, +/-0.622). 916 passed, 21 skipped (0.80.0: 900, 19).

# Changelog

## [0.81.0] - a waiting chair's back is not the wall's face, and a row is four chairs

Walk 9052, `bank_branch_a02` lobby: "z fighting on the [chairs] on the steel"
(the walker), a 2.4 m row of four wooden waiting chairs against the bronze
ribbed `glass_facade` wall. The walk's GLB is the 9052 `zoo_kit_build` output
byte for byte (md5 db0a20e0...), built by Zoo 0.79.0 from a recipe unchanged
since 0.72.0.

**Which of four it was, measured.**

1. *Coincident faces inside the module:* tools/coplanar_probe.py on the
   shipped GLB -- 26 pairs, every one OPP at 0.00 mm (seat end against the
   neighbouring seat, back on seat, leg under seat). Interior contacts; none
   can be seen. Not the report.
2. *Neighbouring placed pieces overlapping:* the four chairs are ONE module
   (`chair_waiting_rcce455f7_{1,4,7}`, one node each), and no other prop's box
   comes within 5 cm of any of the three rows. Refuted.
3. *The back on the wall plane:* the walk copy's `site.tscn` reassembled in
   Blender (chair nodes plus the wall modules behind them) and probed across
   nodes -- each row's four back panels lie SAME-facing, gap 0.00 mm, on the
   wall's inner face: 1.04 m2 for `chair_waiting_rcce455f7_4`, 3.09 m2 over
   the three rows. An EEVEE frame of the placement shows the backs torn into
   patches of wall. THIS WAS IT.
4. *Texture moire:* the wood and wall samplers do export NEAREST /
   NEAREST_MIPMAP_NEAREST at 256 px, and Level Factory's import fix is its own;
   but the pattern the walker saw sits on the one face that is coplanar with
   the wall, not on the seats. Not only that.

**Why the back sat on the wall.** Deli Counter 0.127.0's
`level_design._wall_slots` stands a piece's back plane 0.12 m from the wall
centreline (lines 847 and 864); the wall is `wall_thick` 0.30, so its inner
face is at 0.15 and every wall-slotted prop is buried 0.03 m. The chair's back
panel was 0.03 m thick and flush with the module's back plane, so its front
face landed exactly on the wall face. The cabinet and both service counters in
the same lobby are buried the same 0.03 m and probe 0 SAME pairs: nothing of
theirs faces the room at that depth. The burial is Deli Counter's (not changed
here); the coincidence was Zoo's.

**`recipes/_chair_row.layout`** is the chair's boxes, pure, and `chair.py`
builds exactly them:

* the back panel stands `BACK_INSET` 6 mm in front of the module's back plane,
  so its front face is 6 mm proud of a wall face at 0.03 m and its rear 6 mm
  off a wall a corrected slot would put flush; the seat still reaches the back
  plane, because `build_module` re-centres on the visual bounds and a module
  that stopped short would have the inset halved and pushed onto the front;
* neighbouring chairs stand `BAY_GAP` 12 mm apart (seat and back), the outer
  bays keeping the row's exact width, so a row reads as four chairs and not as
  one plank with seams where the texture restarts;
* legs, arm posts and the back run `SEAT_BURY` 5 mm into the seat, the back
  `BACK_SIDE_INSET` 4 mm narrower than its seat at each end, and the arm post
  narrower than its rail, so no two faces share a plane.

Probed after, in Blender 5.1: the rebuilt 2.4 x 0.6 x 0.9 module is 1,056
tris, 0 coincident pairs (26 before, the same recipe rebuilt from this tree
before the change matching the shipped GLB), visual bounds exactly
+/-1.2 x +/-0.45 x +/-0.3, status pass; the 0.5 m and 0.55 m single chairs
the same lobby places, a 5.0 x 2.0 x 0.6 row and the genome minimum
0.38 x 0.38 x 0.5 also probe 0. Put back in the three 9052 placements
it has 0 SAME pairs with the walls; what remains is 24 OPP contacts, each rear
leg's back face against the wall face (hidden), and the wall modules' own end
seams.

**`tools/preview_specimen.py --dims W D H [--style N]`** with `--species`
plans one prop slot through `kit.plan_kit` and builds it with
`build.build_module` -- a 2.4 m row could not be previewed through a prompt --
and every run prints the `zoo_keeper` version and folder it imported.

`tests/test_chair_row.py`: across the genome's min/default/max, the 9052 rows
and the library's row shapes, with 3 and 4 legs and with and without arms, no
two box faces share a plane inside the probe's 2 mm window; the extents are
the slot; no room-facing face lies within 2 mm of a wall face flush or at
Deli Counter 0.127.0's 0.03 m; neighbours stand 12 mm apart; and the recipe
builds the layout. Four of the six fail against the 0.80.0 geometry.

NOTE, unchanged and not this release: an arm rail stands at seat + 0.22 m,
which rises above a chair shorter than about 0.69 m.

## [0.80.0] - a see-through kind that resolves opaque says so

Walk 9050, delco_1997: `M_Skin_glass_delco_1997` exported alphaMode OPAQUE on
12 GLBs -- the 7 window modules, the teller line, the bus shelter, the
newspaper box, the parking meter and the car. The pane recipes asked for the
right kind (`_arch.py` and `window_broken.py` glaze `glass` unless the slot is
a hollow facade; the teller line, shelter and skylight make `glass`), and
`_textured` blends whenever a pack declares `import_hints.transparency`. The
delco_1997 `glass` pack declared none. That is Pixelcoat's to fix and
Pixelcoat 0.40.0 fixes it; what was Zoo's is that the build log said
`skin: glass <- glass_delco` and nothing else while it happened.

**`skins.SEE_THROUGH_KINDS` and `skins.is_see_through(pack)`.** The kinds a
person sees through (`glass`, the same set `dna.OPAQUE_FOR` swaps out of a
structural slab, and a test holds the two equal), and the one reading of the
hint: opacity below 1, not a scissor cutout. `_textured` and
`make_see_through_material` both decide blend-or-not through it now, where
they had two hand-written conditions. `load_pack` gives a bare legacy pack
`transparency: None` rather than no key.

**`make_material` warns** when a see-through kind resolves a pack that is not
see-through, once per material: `[zoo] WARNING: glass is a see-through kind
and pack glass_delco declares no blended import_hints.transparency -- every
'glass' surface of theme delco_1997 exports OPAQUE`. It does not override the
pack. Rebuilding walk 9050's glass modules against cold run 9050's own library
prints it in all four kit builds that make `glass`, and against Pixelcoat
0.40.0's prints nothing.

**The car's glass is the theme's glass again.** With every theme's `glass`
pack authored see-through, `make_see_through_material` takes its first branch
on a themed build; delco_1997's pack is at 0.38, which is the car's own
opacity, and the rebuilt car GLB carries `M_Skin_glass_delco_1997` BLEND alpha
0.38 on its 6 panes. The forced and flat branches stay for a library with no
`glass` pack. REFUTED in its docstring and kept there: "Godot imports that as
BaseMaterial3D transparency ALPHA, which also keeps the pane out of the shadow
pass". Godot 4.7 imports BLEND at transparency 4, ALPHA_DEPTH_PRE_PASS, which
casts a shadow as solid as an opaque pane (GL Compatibility: 0.463 of open
ground under the pane either way, 1.000 with it hidden). Level Factory 0.84.0's
import script moves blended materials to ALPHA.

**Hollow facades stay opaque**, measured rather than assumed: a bank window
slot tagged `glazing: "facade"` builds its pane in
`M_Skin_glass_facade_delco_1997`, OPAQUE in the GLB and transparency 0 in
Godot. The mechanism is `kit.plan_kit` keeping the slot's `glazing` ->
`dna.resolve_module_plan` setting `glazing_kind` -> `_arch.build_slab`. NOTE,
not Zoo's: nothing emits that tag today. Deli Counter added it in 501c9db
(its 0.80.0) and a later commit that also calls itself 0.80.0 (f54ebfe)
removed the five lines; the two facade shells in `deli_counter/build` have 0
window slots, so no shipped pane is affected yet.

`tests/test_see_through_glass.py`: the declaration round-trips through
`load_pack`, `is_see_through` over eight hints, both material paths read it,
every building pane recipe asks for a see-through kind, an enterable window
plans `glass` and a facade window `glass_facade`, and a broken window has no
pane (remnants rise 0.14 and hang 0.09 of the opening, no `_Glass` object).
Three bpy tests build `window`, a facade `window` and `window_broken` against
stub packs and read the Blender materials; the suite skips them without
Blender, and they were run inside Blender 5.1 for this release (3 ok; against
an opaque stub pack the window and broken-window cases fail, the facade case
passes). `test_car_forms` pins `skins.is_see_through(pack)` in place of the
condition it replaced.

## [0.79.0] - cars with glass you can see through, a cabin behind it, and a body style

The walker, after walking a generated street: "we need our cars to upgrade
quite a bit. missing a lot of detail, side windows, transparency, etc etc".
The references were a 1991 Ford Explorer, a 1990s Geo Metro three-door and a
lot of 90s sedans.

**What 0.78.0 built, measured before anything moved.** The shipped
`cover/prop_simple_car_delco_1997_01_w175_d430_h145.glb` of walk 9048: 11
visual parts, 888 tris, a cabin box on a slab. The side panes were built
inside the tapered cabin solid, so the only side glass a camera could reach
was a sliver along the top edge -- "no side windows". The glass material was
`M_Skin_glass_delco_1997`, alphaMode OPAQUE: the delco `glass` pack
(`glass_delco`, Pixelcoat 0.16.0) carries no `import_hints.transparency`, so
`materials._textured` never blends it, and its albedo is #2b3a3d -- the
"opaque green-grey windshield band". The rockay glass packs do carry the hint
(`glass_wavy`: blend, 0.5). The buildings' windows are opaque for the same
reason -- measured on the same walk,
`lot/auto_shop_a02/art/zoo/window_delco_1997_01_w130_ob0bdca.glb` glazes
`Window_Glass` in `M_Skin_glass_delco_1997`, OPAQUE. That is Pixelcoat's
`profiles/materials/glass_delco.json`, and it is not changed here.

**The car is rebuilt, one recipe, four body styles.** `core/car_forms.py`
holds the styles as fractions of the slot, read off the cars named: `sedan`
(Corsica / Taurus: three boxes, wheelbase 0.575, windshield base a third
back, trunk a sixth), `hatchback` (Metro: wheelbase 0.62, 0.19 h tyres, big
glass, a near-upright hatch), `suv` (Explorer: 0.19 h ground clearance, roof
to the tailgate, roof rack, two-tone cladding) and `coupe` (kept, because
the prompt rules always offered it). Each car is:

  * a lower body lofted from cross-sections -- rocker, vertical door skin,
    shoulder roll, crowned hood and deck -- with a wheel WELL notched over
    each axle so the arches are in the silhouette, and inside the cabin an
    open tub: door walls, a floor, wheel tubs;
  * a greenhouse that is not a solid: a hull (windshield plane, side planes
    with tumblehome, rear plane), a roof slab that is the hull, pillars 3 mm
    inside it, and one pane per opening 7 mm inside -- windshield, a pane per
    door per side, quarter glass where the style has it, backlight (6 or 8
    `Car_Glass_*` objects, named by `car_forms.pane_names`);
  * an interior: dashboard, instrument hood, steering wheel on the driver's
    side (+X; the nose is -Y), front seats with headrests, a rear bench
    between the wheel tubs, door cards, floor mat;
  * shaped two-band bumpers, a grille with bars, headlamps and amber corner
    lamps in a dark housing, tail lamps in a housing with a reverse lamp,
    a rear plate and its frame (Pennsylvania plates the rear only), mirrors,
    handles, door seams, side moulding, wipers; SUV roof rack and cladding
    with a pinstripe; hubcap, steel or five-spoke alloy wheels on tyres with
    a sidewall.

Paint is a 1990s palette per style (dark green, teal, maroon, navy, white,
silver, tan, red, black, and the Metro's sky blue), drawn from its own
stream. A prompt colour wins; the `1970s`, `1980s`, `police` and `racing`
style blocks now say `"paint": "fixed"` and keep theirs. Materials stay on
the skin system: paint, cladding, lamps, plate and grey steel wheels on
tintable `metal_painted`, trim and tyres on `rubber`, seats on `canvas`.
Brightwork and headlamps were `metal_bare` first and rendered brown in
Godot's Compatibility renderer (metallic 0.9 with only the ground to
reflect); they are dielectric now. Lamps are unlit and their materials do
not end `_Lens` / `_Diffuser` / `_Face`, so Lux's emissive binder leaves them.

**Glass is see-through whatever the pack says.** New
`materials.make_see_through_material`: a pack authored see-through is used
as it is; an opaque pack keeps its albedo under `M_Skin_glass_<theme>_
see_through`, blended at the car's 0.38 opacity (the building's opaque glass
material is untouched); no pack gives a flat tinted blended pane. Measured
in Godot 4.7 on a scratch copy of walk 9048 with the new car under the same
stem: the GLB writes alphaMode BLEND, baseColorFactor alpha 0.38, texture
kept; Godot imports every pane as BaseMaterial3D transparency 4
(ALPHA_DEPTH_PRE_PASS, the importer's mapping of BLEND), albedo alpha 0.380,
cull disabled; every opaque part imports at transparency 0. `look_shots.py`
frames from given stations at the parked car show the seats, steering wheel
and far-side glass through the near door glass.

**How a style is chosen.** `params.body_style` is now `auto` by default
(`sedan`, `hatchback`, `suv`, `coupe` by name, or by prompt keyword). A kit
build takes param defaults, so `auto` picks from the styles whose natural
(depth, height) window holds the slot, from a `car_style` stream seeded by
the module stem: 3.8 x 1.40 is always a hatchback, 4.7 x 1.73 always an SUV,
4.8 x 1.42 always a sedan, and Lot's 1.75 x 4.30 x 1.45 slot a sedan or a
hatchback. Proportions, doors (`doors` 0 lets the style draw), quarter
glass, rack, cladding, wheels, bumpers and paint vary by seed within a style.
The pivot, the exact-fit dims (mirror heads are the width, bumpers the
depth, roof or rails the height), the +Y length axis, the two collision
boxes and the three attachments are what they were; `ATT_driver_seat` moved
to +X, the driver's side of a car whose nose is -Y (it was on the
passenger's side).

A Lot street still gets ONE car: every parked car is one slot shape at
style 1, so one stem, one module, one seed. That is Lot's to change, below.

**No coincident faces.** Measured with `tools/coplanar_probe.py`'s own
`probe()` on `plan_kit` + `build_module` builds: every style forced at the
genome's min, default and max dims with slot styles 1-8 (96 builds), and 550
more at random slot sizes inside the genome's ranges, random style or
`auto`: 646 builds, 0 SAME and 0 OPP pairs, every `fit_*` check passing. The
grid alone is not enough and read clean first: the probe's `--glb` mode on
an exported 1.60 x 3.80 x 1.40 hatchback found a door card's face 0.29 mm
from the rear hub disc (SAME, 193 cm2), a size the grid never built. Getting
there, each kept in the code above the fix: a pinstripe's buried face 2.0 mm from the cladding's
(SAME, 14.66 cm2); grille bars' back face 2.0 mm in front of the nose face
(OPP, 152 cm2); corner pillars cornered at `e - t*a - t*b`, which on planes
that are not square to each other left twisted quads 1.85 mm off the roof
slab's side (SAME, up to 24 cm2) -- the corner is now `e - t/(1+a.b)*(a+b)`;
that fix then exposed the A-pillar's inner face folding into a bow-tie on a
raked windshield (OPP, 0.00 mm, 7-20 cm2), and the first clamp against it
compared Y at the wrong height, never bound, and changed nothing -- the null
result was the wiring, and the clamp now reads the edge at the corner's
height; a moulding ending 0.31 mm from a door seam (OPP, 10.56 cm2); door
cards running over the rear wheel tub (the hub disc above); a reverse lamp's
buried face exactly 2 mm off the tail-lamp housing, counted on 19 of 150
random sizes -- every one under 4.0 m, where float rounding put 2 mm inside
the probe's window (OPP); a front seat 1.66 mm off the wheel-tub ledge on
1.85 m hatchbacks (OPP, 3 of 250).

**Tris, per style, the largest of those 646 builds:** sedan 3,100, hatchback
2,884, SUV 3,328, coupe 3,004 (means 2,857 / 2,781 / 3,149 / 2,846). 1,344 of
the first SUV's 2,980 were the body loft; dropping two stations that bought
no shape (hood and deck are linear between their ends) and stepping the
arches at 45 degrees instead of 30 took about 200 off. The budget goes from
12,000 (never measured against anything) to 3,400. For scale: a street tree
in walk 9048 is 2,220-2,652 tris, and that street parks 19 cars -- 19 x 3,300
is about 63,000 tris of car against 42,500 of its 18 trees, where the 0.78.0
car was 17,000. Godot's import generates LODs for these meshes
(`meshes/generate_lods=true` in the walk project's import settings). Nodes
per car: 15-19, from 12.

`plan["bevel"]` is no longer applied to the car: the chamfers it reads by are
modelled, and `bevel_edges` is what made 0.78.0's 12-tri boxes 44.

**`tools/preview_specimen.py`** takes `--azimuth`, `--eye` and `--dist`, each
overriding only itself: the auto camera stood at 3.2 m for a car, a
first-floor window rather than a sidewalk.

**What Lot would change to get a street of different cars (not done here).**
`site_parking.CAR` is one (1.75, 4.3, 1.45) and `lot.write_site_slots`
writes `"style": 1` on every slot, and `cover_module_refs` resolves every
piece at the site's one style. To park a mix: choose a shape per bay from a
small table -- e.g. hatchback 1.60 x 3.80 x 1.40, sedan 1.75 x 4.80 x 1.42,
SUV 1.80 x 4.70 x 1.73, all inside a 6.0 m bay and the genome's ranges --
and a style int per bay from the same bay hash, written on the slot and used
by the stem. Zoo needs nothing more: the shape picks the style, the stem
seeds the paint and trim. The cover planner's `MIN_COVER_HEIGHT` of 1.3
holds for all three. `plan_parking` also gives both kerbs one yaw
(`road.angle_deg + 90`), so the cars on one side face against the traffic;
with the nose at -Y, one side wants that yaw plus 180.

What a render cannot show: Cycles ray-traces and no frame shows z-fighting;
the coincident-face result is the probe's. Whether 19 cars at 15-19 nodes
and about 3,000 tris each cost frame time on the walker's machine has not been
measured.

Tests: `test_car_forms.py` (style selection deterministic per seed and
bounded by the slot's proportions, doors read, trim varies, palette and
fixed paint, one pane per opening and the recipe's panes named from it, the
see-through material blending on every branch, the layout holding the exact
dims at every style and size with and without a rack, the genome interface
Lot parks by, stand-offs above the probe's window, the measured matrix
within budget) and `test_car_wheels.py` rewritten onto the layout. Six
deliberate breakages -- skin depths 2 mm apart, panes given the trim
material, an opaque forced pack, the body side moved 1 cm, WHEEL_TUCK 0, a
hatchback window stretched to 4.9 m -- each failed its test first.

## [0.78.0] - a word on the stop sign, stock on the shelves, wheels out of the body's plane

Three more from the walker's walk copy, each measured before it was changed
and re-rendered after. The measuring instrument is new:
`tools/coplanar_probe.py` lists every pair of faces, across all visual parts
of a built prop, that lie within 2 mm of one plane and overlap -- SAME when
both face the same way (whatever sees one sees the other), OPP when they are
back to back. Zoo's materials export `doubleSided: true` (measured on
`verify/*.glb`), so OPP pairs are not culled either; they are hidden only
when both solids are closed around them.

**Simple car: "these wheels jitter when I walk past them".** Probed on the
1.75 x 4.30 x 1.45 module cold run 9049 shipped (Zoo 0.76.0; the recipe did
not change in 0.77.0): each tyre's outer cap lay EXACTLY in `Car_Body`'s side
plane, both facing out, gap 0.00 mm, 1475 cm2 of overlap per wheel -- the
part of the cap above the body's lower edge. There is no separate hub; the
suspected hub-versus-tyre fight does not exist. `WHEEL_INSET` was documented
as the body's overhang past the tyre, and was in fact half the tyre's width,
so the overhang was zero. The refuted comment is kept above the constant.
`WHEEL_TUCK` now puts the tyre face 2 cm inside the body side. After, at the
genome's minimum, default and maximum sizes: no SAME pairs. Two OPP pairs
remain and are left: body top / shoulder bottom (6.96 m2) and shoulder top /
cabin bottom (3.04 m2) are butt joints the recipe's comment said were
overlaps; both lie inside closed solids behind the bevel's V-groove. The
comment now says what the numbers say.

**Stop sign: no legend.** The red octagon carries a white STOP: four faceted
glyphs from the new `recipes/_legend.py`, a small cell grid per letter where
a cell is full, empty or a 45-degree corner cut -- the octagonal O and angular
S of a low-poly Highway Gothic. One third of the sign's width tall and
centred (MUTCD R1-1: 10 in on 30 in), 0.77 of the width wide; letter width,
stroke and spacing are chosen, not taken from the sign tables, and say so.
Each glyph is a closed solid whose front stands `LEGEND_PROUD` (4 mm, the
FACE_PROUD argument) in front of the red face and whose back runs through it
to the middle of the border. Half-way into the red face's 4 mm was tried
first and left the back cap 1.93 mm from both its planes (1.35 mm at the
smallest sign, squeezed by `fit_to`) -- enclosed, but inside the probe's
window; the border's middle is 7.5 mm from everything. The plate
still hangs in front of the pole. 108 tris to 372; the budget goes 150 to
450. The border/face and border/post OPP contacts 0.77.0 introduced are
unchanged and occluded.

**Shelving: "nothing in the cabinets".** Every shelf but the top one is now
stocked -- corrugated boxes, banker's boxes, ring binders, cloth ledgers,
coffee cans -- planned by `recipes/_shelf_stock.py` from a new "stock" RNG
stream, so the frame's wear noise is what it was. Nothing overhangs the
uprights, the board's front edge or the back panel; items sit 3 mm into what
they stand on, keep 4 mm between neighbours, and a stacked item steps in at
least 6 mm on every side, so no two faces share a plane. Every finish is a
tintable kind (paper, plastic, metal_painted) and clears a 1.4 luminance
ratio against every style's board and frame grey; the first tan ledger
measured 1.29 against the frame and was darkened.

The probe found the shelf's own structure worse than its contents: 24
coincident pairs on the 2.0 x 0.4 x 1.9 module cold run 9049 shipped. The
back panel ran full height, so its top lay in the top board's top (113.6 cm2,
both facing up, visible from above a low unit) and its bottom in the bottom
board's; boards and back panel stopped exactly at the uprights' faces. They
now bury into the uprights (the back panel by half as much as the boards),
the back panel runs board-middle to board-middle and stands 4 mm in from the
uprights' rear, and the board stack stops 3 mm short of the uprights' top and
bottom. After, at six sizes from 0.6 x 0.3 x 0.9 to 16 x 1.4 x 4.4: zero
pairs, stock included. The same arithmetic found an unreported gap: a board
spanned `bx +/- (bw/2 - up)`, which reaches an END upright but stops 25 mm
short of a SHARED one, so on every multi-bay run the middle uprights stood
free of their boards. Spans now come from the uprights' faces.

Tris: 308 to 876 on that module, 2688 on a three-bay 6 m aisle; the budget
goes 900 to 3000. A seven-bay 16 m run builds 6372 and warns, as its frame
alone (about 2800) already did.

What a still cannot show: Cycles ray-traces, so no render here shows
z-fighting before or after. The car and shelf fixes are evidenced by the
probe's numbers; whether the jitter is gone in Godot needs a walk.

Tests: `test_stop_legend.py`, `test_shelf_stock.py`, `test_car_wheels.py`,
each run against a deliberately broken copy first to see it fail.

## [0.77.0] - three recipes the walker saw wrong in a walk copy

From the walker's second in-game round (roadmap 155), each measured from the
recipe's own numbers before it was changed, and each re-rendered after.

**Stop sign: the pole stood in front of the plate.** The post is 0.06 m deep
centred on y = 0; the whole 15 mm blade sat inside that depth, so the post's
front face was 19 mm in front of the red face. The blade now hangs on the
post's front, and the red face stands 4 mm proud of the white border so the
two never share a plane. The STOP legend is still missing and is not in this
release.

**Drop safe: the dial and handle flickered.** Both sat inside the door slab
with their front faces coplanar with the door's, and coplanar faces z-fight.
The door now stops 25 mm short of the front and the dial and handle stand
proud of it to the front; the bounding box is unchanged.

**Traffic signal: no red, no green.** The docstring said the lenses are red,
amber and green; the code put all six lenses on one emissive material in one
orange. Each lens row is now its own mesh and material: red, amber, and a
1990s signal's blue-green.

All three build through the kit at their Lot slot sizes and pass validation.

## [0.76.0] - a desk fills a deep slot, and a tall one grows a transaction top

The walker: the outside is coming along, what about the props inside. The
first measurement said the species were missing; that was WRONG and is kept
here because it sent an hour the wrong way. Zoo has 83 recipes and every
species the building library asks for by name exists. `minted.json` is a
24-entry list of what the street work minted, not the catalogue, and reading
it as the catalogue is the shape of mistake CLAUDE.md's first rule is about:
name what produced an artefact before concluding from it.

WHAT IS ACTUALLY TRUE, measured over the 328 named prop slots in the 130
built shells: 285 fell inside their species' declared ranges and 43 did not,
and 30 of the 43 were `desk`. Not 30 problems -- two:

    27  height 1.1 or 1.2, against a 1.0 max     a reception desk
    15  depth 1.3 to 1.6, against a 1.2 max      a desk with a return
    10  depth 6.0                                a CUBICLE BLOCK

ROWS. `bay_max` already divides a wide slot into desks butted together.
`row_max` does the same to the DEPTH and faces alternate rows opposite ways,
which is what back-to-back cubicles are: a 6.0 m slot at `row_max` 1.5 is
four rows of 1.5. `row_max` absent means one row and every existing species
behaves exactly as it did.

A TRANSACTION TOP. A 1.2 m "desk" is a reception desk: the work surface is
still at sitting height and a raised ledge stands over its back edge. Above
`DESK_TOP_MAX` the top stops at `DESK_WORK_H` and the remainder becomes that
ledge -- and the top slab is still built AT the slot height below it,
because `fit_height` is an exact check and lowering a 0.80 m desk to a
0.78 m work surface failed validation on the first build. That is what
`DESK_TOP_MAX` is for and it was found by building, not by reading.

Ranges: depth 0.5-6.0, height 0.65-1.3. The library's named prop slots go
285 fit / 43 miss to 314 / 14. Built through Blender at all three shapes:
8 x 6 x 1.2 is exact to size, pivot centred, 5,896 tris against an 8,000
budget, ten checks pass.

Three tests in `test_bays.py` asserted the old answers and are updated with
what they superseded. A 5 x 1.6 x 1.2 "boss desk" was a COUNTER by the
alternate rule, and a 8 x 6 m cubicle block was "a region, not a thing";
both were the range being too tight rather than the name being wrong. A
casino floor's `gaming_tables` is still a region, because tables stand apart
with room to walk between them and no amount of tiling one table fixes that.

## [0.75.0] - stone, siding and shingle enter the kind vocabulary

The walker's art direction names them and Pixelcoat mints them: local
fieldstone as the county's visual ballast, and vinyl or aluminium lap siding
over brown asphalt shingle as the layer the late 1990s put on older
buildings. A theme mapping alone changes nothing -- `find_pack` is only ever
asked for kinds in `KNOWN_KINDS`, so the packs would be built into every
library and reach no surface. `stone` had exactly that problem for the length
of one commit.

Roughness, each derived against a neighbour already in the table:

    stone     0.94   above concrete (0.92) and brick (0.90): a broken,
                     unpolished face, and a stone wall that catches a
                     highlight reads as wet plastic
    siding    0.66   beside wood (0.65), not plastic (0.45): extruded vinyl
                     leaves the factory with a low sheen and chalks within
                     a decade
    shingle   0.93   beside concrete: stone granule bonded to felt is a
                     MINERAL surface; tar (0.90) is the binder underneath,
                     not what light hits

None is metallic, so all three stay out of `METALLIC` by omission.

## [0.74.0] - the forecourt clutter

The walker's Call of Duty frames: what a forecourt carries is CLUSTERS of
cheap objects -- four blue drums by a fence, stacked pallets, a concrete
barrier dragged across a lane, banded bollards at every column base. None
is a hero asset; each is one simple shape and the grouping is what sells
it.

`jersey_barrier` (the profile is the object: a wide foot, a steep lower
slope, a near-vertical face to a narrow top -- 124 tris), `water_barrel`
(a 55-gallon drum whose two rolling hoops are what stop it reading as a
tube -- 480), `bollard` (a pipe on a concrete foot with a domed cap and
two painted bands, the bands geometry so the read survives an unskinned
build -- 550) and `pallet_stack` (two pallets, a wrapped load, a strap --
704). Every budget is its measured build plus a tenth. All four collide:
they exist to break a sightline at knee-to-waist height, and cover a body
can walk through is the defect this pipeline keeps measuring for.

## [0.73.0] - a tree of tracery, and autumn

The walker's reference frames ("trees comps", 2026-09-13): a clear trunk,
then MANY thin branches, and the leaf mass in many small clumps with sky
through it -- not six blobs on sticks -- and adjacent trees differing in
colour.

A THIRD ORDER OF BRANCHING. Every form gains `twiglets`: each twig forks
into finer shoots, each with its own small mass. Branch counts rise (a red
maple to 8, a callery pear to 10), twigs to three or four, and the masses
shrink to a fifth of the crown's width. A branch's own tip keeps the
three-box mass that carries the silhouette; everything else -- the fork,
the twig tips, the twiglet tips -- is ONE tapered box.

AND THE TWIGS ARE THIN BOXES IN THEIR OWN UNBEVELLED MESH. Measured: with
twigs as cylinders the five trees came to 8,952 / 6,960 / 5,448 / 8,076 /
7,200 tris, which no level would spend on a street prop; as bevelled boxes
a red maple was 5,184 against a derived 2,880, because a bevel on a box
costs 32 triangles and a crown carries eighty of them. A twig two
centimetres across needs neither a cylinder nor a bevel. The trunk and the
branches keep both. The five now build 2,208 / 2,640 / 2,880 / 3,216 /
3,552, and `tree_forms.tri_count` -- now the pieces, each with its own
price -- reproduces every one exactly.

THE LEAF COLOUR RIDES THE STYLE INDEX (`tree_forms.LEAF_PALETTE`: high
summer, gold, orange-red, a late green). A module is built once per stem
and instanced, so every tree of one style shares a leaf; the style index
is already part of the stem, so a row that differs is a row Lot planted at
more than one style.

## [0.72.0] - 2026-09-13

The 1990s American street kit. The walker: "the streets should look like
America in the 1990s -- USPS mailboxes, stop signs, traffic lights."

Six species, each shaped rather than a placeholder box: `stop_sign` (a
30-inch octagonal blade, red with a white border, on a galvanised
u-channel post -- the shape is read before the word), `traffic_signal` (a
pole with a mast arm over the near lanes, a three-lens head at its end, a
second head on the pole, and a cobra-head luminaire arm the other way),
`mailbox` (the blue collection box: boxy body on short legs, domed lid,
pull-down door with a lip), `newspaper_box` (a coin-operated rack: hopper,
pedestal, a sloped window where the front page shows), `parking_meter`
(one head on one post per space, which is the decade's meter) and
`payphone` (the open half-hood, not the glass booth). Nothing reproduces
anybody's markings: a collection box is a blue box and a news rack's
window is empty. Lenses are emissive at a low strength and WHICH lens is
lit is not baked -- a signal whose state is baked is wrong half the time.

THE POLE IS THE SIGNAL'S CENTRE, and the luminaire arm is why. A mast arm
alone would put the module's centre out over the carriageway and Lot's
greybox box with it; the second arm is both what those poles carry in
Pennsylvania and what makes the slot symmetric about the pole.

`geometry.fit_to(objs, size, boxes)` scales a built piece about its centre
so its bounds are exactly the slot's, and moves the collision boxes with
it. All six failed `fit_depth` the first time they built -- a mailbox
0.740 m deep against a 0.700 m slot, a payphone 0.450 against 0.500 --
because a door or a visor sits a centimetre proud of a face, which is what
the object looks like. Tuning each detail until the sum comes out even is
arithmetic nobody can maintain; measuring what was built and fitting it is
one line. Budgets are each piece's measured build plus a tenth (108 tris
for the stop sign, 1,152 for the signal).

`sign_post` gives up the keyword "stop sign" to `stop_sign`: it is the
generic street-sign post, a blade nobody has drawn on a u-channel.

## [0.71.0] - 2026-09-13

The five street trees are species of their own, and the canopy fills.

`red_maple`, `pin_oak`, `honey_locust`, `london_plane` and `callery_pear`
are minted species sharing `street_tree`'s builder -- each recipe module
re-exports it, each genome names its row of `core.tree_forms` in
`params.form` and carries its own slot dims, because a callery pear is
3.0 m across at planting and a London plane 5.0 m, and that difference is
the point of naming them. Deli Counter's keyword table can route "pin
oak" or "sycamore" to one; Lot plants one species per road.

A leaf mass now sits where each branch's twigs fork, on its outer third:
the tips alone hang every cluster on the crown's envelope and leave the
inside empty, which at 4 m across read as scattered chunks rather than a
canopy (measured on a five-species contact sheet).

THE TRIANGLE BUDGET IS DERIVED, NOT CHOSEN. A tree is one grate box, one
limb per trunk/leader/branch/twig and one cluster per tip: 12 + 72 per
limb + 36 per cluster. Read off the exported glTF for all five species,
`84 + 108 * tips` reproduces every build exactly -- before the mid-branch
mass (1,812 / 2,136 / 2,352 / 2,460 / 2,784) and after it (1,992 / 2,352 /
2,532 / 2,712 / 3,072) -- so each genome's `tris_lod0` is that count plus
one fork's headroom, and a warn against it means the piece count or the
bevel moved.

## [0.70.0] - 2026-09-13

`street_tree` is GROWN, by species. The walker, on cold run 9032's frames:
"trees usually have multiple branches that stem from the trunk and those
branches have twigs and depending on what species of tree determines how
that looks." `core.tree_forms` tables the street trees a Delaware County
street plants -- red maple (the default), pin oak, honey locust, London
plane, callery pear -- each as where the first branch leaves the trunk,
how far the leader runs, how many primary branches, their angles from
vertical low/mid/high, twigs per branch, the leaf clusters' size and the
crown envelope (oval, pyramid, vase, flat). The recipe grows a tapered
trunk and leader, branches spiralling up by the golden angle at the
species' angles, twigs off each branch's outer half, and a faceted leaf
cluster at every tip in the same low-poly style as the cars and the
shelter; the SKELETON is fitted to the slot per axis first and the
clusters placed at the fitted tips, so they keep their shape (the first
build fitted the whole tree after and pressed the clusters into plates),
then a last small correction makes the extents the slot's exactly. A
cluster is a quarter taller than wide with a full-width middle band:
measured on the second build, two frustums as wide as tall read as flat
gems from the sidewalk, which is where the eye is. The genome names the
species (`params.form`); `params.crown = "cards"` keeps the crossed
cutout cards of 0.69.2. Budget 2,200 tris (a red maple builds 2,136).

## [0.69.3] - 2026-09-13

`street_tree` ships the faceted crown again. The walker, on cold run
9032's frames: the low-poly volume "looked nice in its own retro way" and
the cutout cards are "not fully baked" -- their thin side faces show as
hairlines and the canopy reads as a different art style from the cars and
the shelter beside it. The genome names the crown (`params.crown`):
`volume` (default: two frustums in the vegetation grammar) or `cards`
(four crossed cutout cards, one foliage tile each). The card path and the
`foliage` kind stay in the tool for the day they are ready; nothing ships
with them until the genome asks.

## [0.69.2] - 2026-09-13

`street_tree`'s crown is four vertical cards and one foliage tile each.
Cold run 9031's frames: the tile repeated 2.7 times across a card and the
two horizontal cards read as shelves, so the crown was a square lattice.
The axis-aligned pair is the slot's width and the diagonal pair is that
times root two (every card's extents are the slot's); the crown's UVs are
cube-projected about the crown's own centre (`uv_offset`), so each card's
UVs run -0.5..0.5 across one tile of Pixelcoat 0.32.1's foliage pack,
authored at the card's width with an elliptical cutout -- the card's edge
is the canopy's. Local kit build: PASS at the slot's dims.

## [0.69.1] - 2026-09-13

`weed_tuft` spans its own width whatever the seed. The blades' bases and
leans are drawn, and a draw where they all lean one way from a tight root
built a clump narrower than the genome's floor: cold run 9030 (seed 9030)
measured 0.028 m against a 0.050 m minimum, the habitat FAILED and the
package was refused. The clump is now spread in plan, about its root,
until it fills nine tenths of the plan's width and depth -- never shrunk.
Rebuilt at seed 9030: PASS.

## [0.69.0] - 2026-09-13

`street_tree`'s crown is cutout cards: four vertical planes crossed at
45 degrees and two horizontal ones, each the slot's width, wearing the new
`foliage` kind -- Pixelcoat 0.32.0's leaf-cluster pack whose alpha is a
cutout. `materials._textured` honours a pack's `alpha_mode: scissor`: the
albedo's alpha is fed through a Math > Greater Than 0.5 into the
Principled Alpha, which is the node the glTF exporter's `detect_alpha_clip`
reads as alphaMode MASK (measured on Blender 5.1.1: the tree's foliage
material exports MASK, double-sided), and Godot imports MASK as alpha
scissor. `foliage` joins KNOWN_KINDS and ROUGHNESS. Without a foliage pack
the cards are flat green planes.

## [0.68.1] - 2026-09-13

`bench` and `bus_shelter` carry their own triangle budgets (300, 400): the
minter copies `prop`'s 200, and a slatted bench (220 tris) and a glazed
shelter (352) built as `warn` rows against it -- which Lot 0.63.0 read as
"not pass" and kept the boxes for. Measured on a local kit build before
cold run 9027.

## [0.68.0] - 2026-09-13

Three species for the waiting places (roadmap 153), minted by
`tools/new_species.py` and shaped: `bus_shelter` (four posts under a flat
roof, glazed back and ends from a knee-high sill, open along the kerb;
posts and panes collide, the roof does not), `bench` (three slats on two
cast end frames, no back, the whole block collides), and `street_tree` (a
tapered trunk from a 1.2 m iron grate at grade, a two-frustum crown in the
vegetation grammar filling the slot's width at its waist; ONLY THE TRUNK
collides -- a body walks under a crown). All centre-pivot at exactly the
slot's dims. The tree is the honest first state of the alpha-cutout
foliage the contract names: a faceted volume, not cards.

## [0.67.3] - 2026-09-13

`streetlight` fits its slot when the plan is an exact fit. The recipe
floats its head above the lamp point it puts at +h/2 for the light-anchor
pipeline, which places the pole top at the anchor -- so as a kit module it
was 6.18 m against a 6.00 m slot, failed `fit_height`, and Lot 0.63.0
stood 13 green boxes on cold run 9025's sidewalks where the lamps go. On
an exact-fit plan the head's top is now +h/2 and the lamp point sits under
the lens 0.18 m lower; the fixtures pipeline builds exactly what it built.

## [0.67.2] - 2026-09-13

`simple_car`'s bumpers sit within its length: they stood 0.03 m proud at
each end, so the built module was 4.36 m against a 4.30 m slot and failed
`fit_depth` on cold run 9024's site kit (Lot stood it anyway; it resolves
by file, which is its next thing to fix). The bumper's outer face is now
the car's length. `streetlight` fails the same check by 0.18 m for a
different reason -- its recipe floats the head above the lamp point it
puts at +h/2 on purpose -- and is left for the contract conversation with
Lux rather than moved in a hurry (roadmap 153).

## [0.67.1] - 2026-09-13

`sign_post` is bare metal in every style, not raw `metal` with `metal_bare`
offered beside `metal_painted` -- 0.67.0 shipped with its own material
tests red, which is the wrong way round. A species is one kind.

## [0.67.0] - 2026-09-13

Three kerb-line species minted for the street (roadmap 153): `fire_hydrant`
(0.35 x 0.35 x 0.75, painted), `litter_bin` (0.6 x 0.6 x 1.0, painted),
`sign_post` (0.1 x 0.1 x 2.4, bare metal). Placeholder boxes at their
authored dims, centred, with collision, the real thing described in each
genome's reference. Lot 0.62.0 places them along every sidewalk band with
the existing `streetlight`, and the site kit builds them like any prop.

## [0.66.2] - 2026-09-12

The pivot check judges slot-fit modules only. Cold run 9020, the first
build on 0.66.1: the site's box truck came out centred (y -1.40 .. 1.40)
and every clutter species failed -- pebble, rubble_frag, litter_scrap,
weed_tuft are built base-up on purpose, to sit on the ground Patina
scatters them over, and a missing pivot claim had defaulted to "center".
`fit_pivot` and the re-centre now read the resolved plan's own `pivot` (a
kit module's is "center"; a habitat plan has none) and leave a surface
species where its recipe put it.

## [0.66.1] - 2026-09-12

The pivot is enforced, not declared.

Cold run 9019's site kit, measured off the GLBs: `box_truck` and
`cargo_container` (minted) spanned z 0 .. h and `simple_car` z 0.01 .. 1.45,
while the kit index said `"pivot": "center"` for each -- it repeats the
plan's claim, and nothing measured it. Deli Counter and Lot place a
module's origin at the slot's centre, so those three stood h/2 in the air.
Three changes: the minting template and the three minted recipes (`pump`
too) build centred; `build_module` re-centres whatever a recipe returns
(`core.pivot.recentre` -- geometry, collision boxes and attachments move
together, and the offset is recorded); and `gather_facts` reports the
bounds' centre so `validate` can fail `fit_pivot` on a module that is off
it. `simple_car` is centred by the enforcement rather than the recipe.

## [0.66.0] - 2026-09-12

Two street species minted for the site's cover: `box_truck` (2.4 x 6.0 x
2.8) and `cargo_container` (2.44 x 6.06 x 2.59), both `metal_painted`, both
with collision, both placeholder boxes at their authored dims with the
real thing described in the genome's reference. Roadmap 22: Lot 0.59.0
places its cover as species-shaped slots -- a box truck, a container, a car
(`simple_car`, already drawn) -- and this kit builds them exact-fit like any
building's props. A truck that is a box is the honest state of a truck
nobody has drawn; a truck that stands six metres across a lane with
collision is already cover.

## [0.65.0] - 2026-09-12

The teller line has a window per station.

### Changed
- `recipes/teller_line.py` builds in bays (`bay_max` 2.0, width to 12.0,
  depth to 1.2): the counter and the header run the full line, a post
  stands at every station boundary, and each station's glass carries its
  own service opening -- a pass-through at the counter, tray-wide -- with
  a tray attachment per station. Drawn from the walker's references (a
  Chase branch line, a bank service window, a teller window under
  construction); the recipe's docstring says what it is a drawing of.
  Built through Blender: a 12 x 0.8 x 2.4 line, seven posts, six windows,
  PASS; a 3.2 x 1.2 x 2.4 bank-tower teller; an 8 x 0.8 x 1.0 teller
  still at counter height falls to `counter` (`ALTERNATE_SPECIES`).
- `tools/new_species.py new --reference "..."`: what the real thing looks
  like, written into the genome beside the mint, so the recipe starts from
  a description and not from a box; without it the genome says so.

## [0.64.0] - 2026-09-12

The 179 that still fell back, and a style for a theme that has none.

### Changed
- Tables and seating run in bays (`bay_max` 2.4 and 0.6): a 4 x 2 count
  table is two tables under one top, a 5 x 2 x 0.6 waiting bench a row of
  joined seats whose seat height follows the authored height. Ranges opened
  by measurement over the 179 placements that still fell back on
  2026-09-12: shelving to 20 x 1.4 x 4.5 (warehouse racks 14-16 m, 4.0-4.4
  tall; server rack clusters 1.4 deep), table 8 x 2.0 x 0.95, chair 12 x
  2.0 from 0.5 tall, drop_safe 1.2 x 1.0 x 1.5 (office and count safes),
  water_tank 3 x 3 x 4.5 (rooftop tanks), desk 1.2 deep (executive desks),
  counter 2.0 deep (coffee islands).
- `plan_kit` tries an ALTERNATE of the same family before the box:
  `desk` -> `counter`. Twenty-one "desks" in the specs stand 1.1-1.2 m
  tall -- front desks, check-in desks, manager desks -- and are counters
  by any name; each is reported in the plan's and the index's
  `species_alternates`, and printed. What stays a box is a region wearing
  a furniture name: an 8 x 6 cubicle block, 12 x 6 of gaming tables.
- `tools/new_species.py style <theme> [--write] [--like] [--species]
  [--material/--wear/--ambient/--color]` (roadmap 150, the style half):
  which species resolve a theme to the uncoloured `default` (14 of 57 for
  `delco_1997`), and with `--write` a style row under the theme's own
  name, copied from the ancestor each resolves to or from `--like`, with
  overrides. A copied row is the ancestor's look under a new name, which
  is the honest state of a style nobody has tuned.
- `water_tank` under `fit_exact` builds its cylinder with sixteen segments
  so its extents are the slot's (a 14-gon's flat width is 0.975 x 2r; the
  first 3.0 m tank came out 2.925 and failed `fit_width`). Built through
  Blender: a 4 x 2 count table, a 5 x 2 x 0.6 waiting bench, a front desk
  that became a counter, a 16 x 1.4 x 4.4 rack, a 3 x 3 x 4.4 tank, a
  1.2 x 1.0 x 1.5 safe, the minted pump; 7 of 7 pass.

## [0.63.1] - 2026-09-12

- `tools/new_species.py new` says whether the theme (`--theme`, default
  `delco_1997`) has a Pixelcoat profile for the species' material, and
  prints the `pixelcoat/tools/new_material.py` command when it does not
  -- a minted prop with no pack is a flat box, and the two mints are one
  request (roadmap 150).

## [0.63.0] - 2026-09-12

A new person can mint a species.

Roadmap 150, from the walker: "new people can walk up to this level factory
and make a good looking level and mint the necessary props, textures,
styles to fulfil the request." For props the owning tool is Zoo, and
growing it meant reading five recipes, a genome schema and a test file.
Measured 2026-09-12 over Deli Counter's 129 built manifests: 511 prop
slots carry no species hint, and the names say what they are -- `pump` 42,
`pump_island` 21, `canopy_col` 42, `aisle` 19, `display_case` 11, `stall`
10, `lift` 8, `planter_box`, `forecourt_pad`, `canopy_roof`.

### Added
- `tools/new_species.py report`: the request queue -- placement names with
  no species hint, most common first; hints to species that do not exist;
  and hinted slots that exist but did not fit (a range or a bay, not a
  mint). `tools/new_species.py new <species> --width --depth --height
  [--like prop] [--material] [--keywords]` writes a genome from the
  template with the dims as defaults and a 0.5x..2.0x range, a placeholder
  recipe (a solid box of the plan's exact dims, one named part, collision,
  a top attachment, a docstring that says where the drawing goes), a test,
  and a line in `genome/minted.json`, which `test_genome` unions into its
  known set. It prints the one line Deli Counter's keyword table needs.
  Refuses to overwrite. `tests/test_new_species.py`.
- `pump`, the first minted species (1.0 x 1.2 x 1.4, metal), routed by
  Deli Counter 0.118.0's `pump` keyword; `pump_island` stays a box. Its
  recipe is the placeholder; a pump that is a box is the honest state of a
  pump nobody has drawn, and it is now counted as one.

## [0.62.0] - 2026-09-12

A run species fills a run, in bays.

Roadmap 44, step 3. Measured 2026-09-12 over the 1,443 placements: of the
721 that name a species, 579 are longer than any single unit of it, and
every `teller_counter` (38) is a 1.0 m counter that no `teller_line`
barrier (2.0 m minimum) could be. Deli Counter authors runs; Zoo built
units.

### Changed
- `recipes/_bays.py`: `bays(width, bay_max)` divides a width into equal
  bays of at most `bay_max`, never a sliver. `counter`, `shelving`,
  `filing_cabinet` and `desk` declare `bay_max` in their genome params
  (4.0 / 2.4 / 0.5 / 2.2) and open their width to 12.0 (4.0 for the
  cabinet): a counter run is one body and top with a shelf and a register
  attachment per bay; a shelf run shares an upright at every bay boundary
  with boards and back per bay; a cabinet bank runs one body and base with
  a drawer stack per bay; a desk row is one top on a leg set, pedestal and
  modesty panel per bay. One bay is the unit each recipe always built.
- Ranges opened to what the specs author, by measurement: counter depth
  1.4 and height 1.2 (nurse stations, bars); shelving depth 1.2 and height
  3.5 (double-sided gondolas, warehouse racks); filing_cabinet depth 0.9
  and height 2.1 (lockers); desk height 1.0; hvac_unit 4.0 x 3.0 x 1.5
  (rooftop units); table height 0.8 (card tables). `tests/test_bays.py`
  plans the measured shapes verbatim with no fallback.
- `filing_cabinet` under `fit_exact` gives the body up to the 0.05 m its
  drawer fronts and pulls stand proud, so a locker bank is its slot's
  depth (the first 3.0 x 0.8 x 2.0 bank came out 0.840 and failed
  `fit_depth`). Built through Blender: an 8 m counter (two shelves, two
  registers), a 6 x 1.0 shelf run (three bays, four uprights), a 3 m
  locker bank (six drawer stacks), a 4.4 m desk row (two desks under one
  top), a 4 x 3 rooftop unit; 5 of 5 pass.
- Deli Counter 0.118.0 routes `teller` and `workbench` to `counter`, adds
  `chair`, and records a hinted volume long side first (turned 90 when its
  long side is y), so a 1.0 x 6.0 aisle plans as a 6.0 m run.

## [0.61.0] - 2026-09-12

A hinted volume is built as what it is, when it fits.

Roadmap 44. Deli Counter 0.117.0 stamps `species` on each prop slot from
the placement's name. `plan_kit` checks the hint against the species'
genome ranges (`_species_fit`, width along x, depth along y, height) and
plans that species at the slot's exact dims when it fits -- the existing
`build_module` path already loads the genome of `module["species"]` and
the recipe builds to `plan["dimensions"]` -- else the `prop` box, with
every fallback and its reason in the plan's new `species_fallbacks`
("width 8.00 outside 1.00..5.00", "would fit turned 90 degrees", "no
genome"). `module_stem` carries the species (`prop_desk_delco_01_...`),
the mirror of Deli Counter's, so a desk and a crate of one size are two
files. Unhinted slots plan byte for byte as before.
- Built through Blender on a three-slot probe (desk 1.6 x 0.8 x 0.75,
  counter 2.0 x 0.65 x 0.95, an 8 m teller run): the desk is a desk (top,
  legs, pedestal, drawers), the counter a counter with its register
  attachment, the run the box. The counter FAILED `fit_width` at 2.040 m:
  `recipes/counter.py` gave the top a 2 cm lip past the body on a
  free-standing prop; under `fit_exact` the lip now comes out of the body
  and the top is the slot's width. `build_kit` writes `species_fallbacks`
  into the built index and prints each one (`[zoo] SPECIES FALLBACK ...`).

## [0.60.0] - 2026-09-11

The corner module can be asked for.

Roadmap 64: `wallCorner` had a recipe and a genome since 2026-07-14 and
nothing had ever requested one. Two of the three preconditions the item
measured are paid here; the third (the gap report armed) closed under
roadmap 62 in 0.58.0.

### Fixed
- `wallCorner`'s genome declared height 2.0-4.5 m, which excluded 252 of the
  988 corners in the shipped library (storeys of 4.7, 5.1, 5.2, 5.7 and
  6.2 m). Measured 2026-09-11 over 128 manifests: 950 corner posts across 17
  (thickness, height) pairs, 0.25/0.30/0.35 m thick, 2.7-6.2 m tall. Height
  is 2.0-6.5 and width/depth reach down to 0.25; the ranges and their
  measurement are written into the genome.
- `kit.plan_kit` keyed a corner on width alone, and a corner's width IS the
  wall thickness -- so `wallCorner_<theme>_<style>_w30` would have named
  fourteen different solids and one file would have won. `CORNER_ROLES`
  keys it on all three axes, like a prop: `_w30_d30_h330`. Deli Counter
  0.114.0 mirrors it in `themed_tscn.module_stem`; the same literal is
  pinned in both suites.

### Not done here
- Deli Counter still seats a `wallEnd` unit post at every corner (its
  0.102.0 answer to roadmap 58, zero new modules). Promoting those slots to
  `wallCorner` costs one exact module per (thickness, height) per building
  and buys nothing visible until the corner has art a post does not -- so
  it waits for that art, as the item said it should.

## [0.59.0] - 2026-09-11

The stamp says which tool wrote the file; the seed does not move with it.

### Fixed
- `zoo_keeper.TOOL_VERSION` was the literal `"0.31.0"` since July while the
  tool went to 0.58.0, so `zoo.tool_version` in every kit, fixture, dressing
  and habitat index -- 37 kit indexes across 13 workspaces on 2026-09-11 --
  named a version 27 releases stale. It is read from `VERSION` now.
- It could not simply be corrected, because the same string is folded into
  every specimen's root key (`seeding.root_key`, `habitat.habitat_id`,
  `variants.family_id`) and correcting it would have re-rolled every asset in
  every workspace. The two meanings are split (roadmap 136): `SEED_EPOCH`,
  frozen at `"0.31.0"`, is what the seeds read; `TOOL_VERSION` is what the
  stamps carry. No vertex moves: the ids Zoo built that morning on cold run
  9005 (`pebble_bb64e4`, `habitat_a49078`, theme `delco_1997`, seed 9005)
  reproduce exactly under `SEED_EPOCH`, and a test pins them. A static test
  refuses any seed call that reads the stamp.

### Seen, not touched
- `bl_info["version"]` is `(0, 20, 0)`; it is Blender's add-on registry
  entry and nothing in the pipeline reads it.

## [0.58.0] - 2026-09-11

A species the library cannot build is said, in one shape, on both paths.

### Fixed
- `zoo_cli.py --kit` never passed `known_species` to `kit.plan_kit`, so the
  dry plan -- the pre-build gate Level Factory runs -- planned an unknown
  species as if it would build. It is armed with `genome.list_species()`
  now, as `build.build_kit` has been since 0.32.0. Roadmap 62 recorded the
  CLI as the planner's ONLY caller; it was the only UNARMED one.
- `build_kit` returned `n_fail` to its caller and never wrote it into the
  index. Level Factory's `ZOO_PARTIAL_BUILD` finding reads the index, so it
  never fired: measured 2026-09-11 over 37 shipped kit indexes, 98 modules
  with status `fail` (90 in `lot-demo-ws`, 8 in `unlit-3b-ws`, none in any
  cold run), zero findings. `n_fail` and `n_missing` are in the index now.

### Added
- `kit.capability_gaps(plan)`: one `CAPABILITY_GAP` line per missing module
  -- what was asked, the nearest species the library does carry
  (`difflib`, so a typo names its neighbour and a new species names none),
  and the owner -- printed by the dry plan and the Blender build alike, so
  the two cannot drift on what a gap looks like. `missing_modules` entries
  carry `nearest` and `owner` for the reader that wants the fields.
- `tests/test_capability_gap.py`, six cases, including the CLI against the
  real genome library.

### Seen, not touched
- `zoo_keeper.TOOL_VERSION` is the literal `"0.31.0"` and stamps every
  index as `zoo.tool_version`. It is also a component of every seeding root
  key, so correcting it re-rolls every asset Zoo builds; that is a decision,
  not a typo fix, and it is not made here.

## [0.57.0] - 2026-09-09

A theme name reaches the style a species already carries.

### Fixed
- `build.py` asked `if theme in genome["styles"]` at both prop sites and took
  a miss as "no style at all", so a theme Zoo did not carry VERBATIM produced
  nothing and the prop came out flat. The prompt path never had that problem:
  `dna._pick_style` has resolved era, then style tags, then default, since it
  was written. `dna.theme_style` gives the theme path the same courtesy --
  exact name, then the name minus a trailing qualifier, then that qualifier
  read as a decade -- and returns None rather than guessing, so the caller
  keeps whatever `resolve_plan` chose.

  WHAT IT COST, measured on cold run 9003. Zoo carries `delco` on 39 of 56
  species and `1990s` on 14. `delco_1997` is those two axes in one string, a
  place and a period, and it resolved on ZERO of 56 -- the look was authored,
  only the spelling was missing. With the resolver: 53 of 56, 39 through
  `delco` and 14 through `1990s`, from content that was already there.

### Added
- `delco` styles for `boots`, `condiment_bottle` and `helmet`, taking
  `delco_1997` to 56 of 56. These three were a real gap rather than the other
  axis: they carried `center_city`, `industrial_flats` and `rockay` and
  neither `delco` nor `1990s`, so the resolver had nothing to reach.
  `condiment_bottle` is the pointed one -- the brief that exposed all of this
  is a restaurant row. Each follows the shipped pattern (same material, a
  darker colour, wear raised 0.10-0.15 over default) and each material is
  inside the species' own `materials.options`.

- `tests/test_theme_style_resolution.py` -- resolution order, the None cases,
  a corpus check that every species reaches `delco_1997`, and a regression
  guard that every shipped style name still resolves to itself, so this cannot
  move a theme that already had an exact match.

### Not done, deliberately
- The other 14 species carry no `delco` style, and that is NOT a gap. Every
  one of them carries `1990s` instead: the library splits place props
  (`delco`) from period and interior props (`1990s`), and after the three
  additions above every species carries one or the other. Authoring `delco`
  onto the 14 would flatten a distinction their authors made on purpose. The
  resolver is what bridges the two axes.

## [0.56.0] - 2026-09-06

Quiet geometry. `CONTRAST_DIRECTION.md`'s step 0, run and answered.

### Changed
- `genome/species/wall.json` style `delco` `relief`
  `{pier: 0.1, reveal: 0.04, base: 0.45, cap: 0.12, bay: 1.0}` ->
  `{reveal: 0.0}`, which is the form `rockay` already ships.

  THIS IS STEP 0 OF A WRITTEN PLAN, not a preference. That document opens its
  ordering with: "`relief: {reveal: 0}` on one archetype's style, rebuild,
  look at it. Zero code. It is the A/B that tells us whether 'quiet geometry,
  loud texture' is the right direction BEFORE we build anything to support it.
  If the plain walls look worse, everything below changes." They did not look
  worse. The reporter compared the interior station in both builds and
  preferred the flat one.

  WHAT IT COSTS THE GEOMETRY. `wall_delco_01_w200.glb` drops from 8 meshes and
  2064 VEC3 to 2 and 336. Across `precinct_yard_001`, kit surfaces fall
  3554 -> 1002 on 543 exterior and 142 interior wall instances, and the kit
  GLB payload 10.57 -> 10.26 MB. Package size is unchanged at 19 MB.

  WHAT IT COSTS THE LOOK, and the honest number is smaller than the geometry
  suggests. Above `shot_diff`'s 8/255 visible threshold: elev_W 0.00%,
  elev_E 0.09%, elev_N 3.43%, spawn 2.11%, and the interior station 28.50%.
  More than 90% of pixels move in EVERY frame, but by at most 7 codes on the
  west elevation -- the relief was doing something everywhere and almost
  nothing visibly at facade distance. Figure-ground is untouched:
  `tools/shot_contrast.py` reads 0.529 -> 0.532, and `tools/texel_density.gd`
  confirms density held at 0.500 / 1.000 at 1.0x, so nothing else moved.

  IT SUPERSEDES 0.54.0's DIRECTION AND THAT IS WORTH SAYING PLAINLY. That
  release raised `pier` 0.02 -> 0.1 and `reveal` 0.015 -> 0.04 because "the bay
  rhythm was geometrically correct and 1.3 pixels wide". The rhythm was real
  and the fix was right for the problem as posed; what this measurement adds is
  that even at five times the depth it moves a facade by less than one visible
  step at the distance the elevations frame. If the bay rhythm is wanted back,
  the evidence says it should come from the texture, not the mesh.

### Known: this is half a change by design
The same ordering says step 3 -- "separated value clusters ... an explicit
bevel band set (edge / field / seam / recess / highlight) so a surface can
express depth" -- "is what pays back step 0's geometry, and without it step 0
just produces flatter flat walls." Nothing in Pixelcoat expresses a bevel band
today; 22 of 51 grammars have all their value mass in a single contiguous run.
So this ships a cheaper, quieter wall and does NOT yet ship the depth that is
supposed to replace the relief.

## [0.55.0] - 2026-09-06

Every architectural surface shipped 1.2x finer than the density the art
direction targets, and the multiplier doing it was in this repo.

### Changed
- `recipes/_arch.py` `texel` 1.2 -> 1.0, on both the main part builder and the
  glass pane. `_arch.py` is the shared builder for wall, wallEnd, window,
  doorway, breach, ceiling, floor, roof and prop, so this is every
  architectural surface in every building.
- `recipes/dress_cover.py` `texel` 1.2 -> 1.0, swept in the same pass.

  THE ARITHMETIC, and it closes exactly. `cube_project_uv` lays UVs down as
  world-metres x `texel`, and `bpylayer/materials.py` drives the Mapping node
  at `1 / meters_per_tile`, so on-screen density is
  `size x texel / meters_per_tile`. At the shipped settings that was
  `256 x 1.2 / 2.0 = 153.6` px/m against the 128 px/m target
  `pixelcoat/docs/CONTRAST_DIRECTION.md` 6.3 sets. At `texel=1.0` it lands on
  128.0. Measured on the re-exported `precinct_yard_001` with
  `tools/texel_density.gd`: concrete, metal and drywall read `uv1_scale` 0.500
  and glass 1.000 -- every skin exactly 128 px/m, worst mismatch 1.0x.

  WHY BOTH FILES MOVED TOGETHER. That document flagged `dress_cover.py`'s 1.2
  for putting covers at 20% higher density than the wall behind them, and
  asked for a sweep of other non-1.0 values. The walls carried the same 1.2,
  so they in fact MATCHED -- moving only the architecture to 1.0 would have
  created the break the document was describing.

  WHAT IT MEANS DOWNSTREAM. `meters_per_tile` now means what it says: a
  grammar authored at 2.0 m repeats every 2.0 metres in world space. It
  repeated every 1.67 m before this and every 0.83 m before Level Factory
  0.58.0, so three separate defects were stacked on that one number. This was
  the last of them and the only one living in Zoo.

  IT IS ALSO THE 1.2 FROM THE PROJECTION WORK. Level Factory roadmap 88 and
  104 both turn on a measured UV density of 1.2 that appeared on every skin
  regardless of its `meters_per_tile`, and both wrote it down as "Zoo's texel
  constant" without locating it. A mesh built here at `texel=1.2` reports
  |dUV|/|dPOS| = 1.2 whatever the material asks for, which is exactly what
  `zoo_worldskin.gd` measures. 104's fix is unaffected.

  A LIBRARY-WIDE ART CHANGE, shipped as one. Every architectural surface in
  every level is 20% coarser. `CONTRAST_DIRECTION.md` argues for that
  direction -- "the library is authored 1.3-16x finer than the aesthetic calls
  for", against Quake II reference points of 32 / 64 / 128 px/m -- and the
  result was walked and approved before this landed. Full geometry rebuild on
  `precinct_yard_001`, structural checks passed, `portability-test` PASS.

## [0.54.0] - 2026-08-29

The bay rhythm was geometrically correct and 1.3 pixels wide.

### Changed
- `wall.json` delco `relief.pier` 0.02 -> 0.1 and `reveal` 0.015 -> 0.04.

  0.53.0 gave the facade a uniform pilaster every 1.0 m with no width
  discontinuity at module seams. MEASURED on the shipped elevation, that
  rhythm carries spectral power 500 against a 1836 peak -- present, and far
  too quiet to do the cohesion job it exists for. The reason is scale, not
  correctness: `look_shots` frames this building at 66.7 px/m, so a 2 cm pier
  is 1.3 PIXELS and a 1.5 cm reveal casts a shadow below what reads as an
  edge at street distance. delco was running at about a seventh of `RELIEF`'s
  own defaults (`pier: 0.14`, `reveal: 0.05`).

  Full-width end piers are what made a large pier dangerous before -- size
  showed up only at seams, so the bigger the pier the louder the module grid.
  0.53.0 removed that coupling, so the pier can now be sized for legibility
  instead of for damage control. At 0.1 it is 6.7 px in the same frame.

  Geometry checked before shipping: a 2.00 m module gives piers 0.05 / 0.10 /
  0.05 and two 0.90 m fields, seam total 0.10 exactly equal to the interior
  pier; `w30` still fails `min_field` and stays a flat panel; the bbox is
  still exactly (w, d, h) and collision still comes from `slab_parts`.

### Measured
- The 2 m module signature has three contributors, separated by holding one
  variable at a time on the north elevation (P = spectral power at that
  period, wall band only):

      bay 2.4, full piers, vertex colour ON    P(2m) 1548
      bay 1.0, half piers, vertex colour ON    P(2m) 1044
      bay 1.0, half piers, vertex colour off   P(2m)  278

  Relief geometry alone is a 33% reduction. The vertex-colour layer alone is
  a 73% reduction -- about 2.2x the geometry's effect.

  ROADMAP 84 CONSEQUENCE. The shipped build is the vertex-colour-off row;
  `--vertex-colors force` is a probe. Turning that layer on as currently
  baked MULTIPLIES the module signature by 3.8x, because the wear is baked
  per module and so repeats per module by construction. 84 is still real --
  the layer is dead weight today -- but it cannot be switched on as baked.

  The fourth cell (old geometry, vertex colour off) was not built, so the
  relief change's effect in the SHIPPED configuration is not on record.

## [0.53.0] - 2026-08-29

The relief that exists to disguise the module grid was drawing it.

### Fixed
- `relief_parts` end piers are HALF WIDTH. Two abutting modules each put a
  full-width pier inside their shared edge, so every module seam carried a
  double-width strip and no other line on the wall did -- a vertical rhythm
  at exactly the module pitch, in a width that appears nowhere else on the
  facade. At half width the two halves sum to precisely one interior pier,
  and a seam is geometrically indistinguishable from a bay line.

  Flushness is unchanged and still tested: nothing overhangs into the
  neighbouring module, so the 6 cm pilaster bug stays fixed. The outer bbox
  is still exactly `(w, d, h)`, and collision still comes from `slab_parts`,
  so no collider on any previous build moves.

### Changed
- `wall.json` delco `relief.bay` 2.4 -> 1.0. THE PARAMETER WAS INERT. Every
  wall module this facade builds is `w200` (2.00 m) or `w30` (0.30 m), and
  `n = max(1, round(w / bay))` with `bay: 2.4` is 1 for both -- so no wall in
  any build ever got an interior pier, and the relief could only ever trace
  the module outline. At 1.0 a 2.00 m module gets two bays and a real pier at
  its midpoint; `w30` still falls through `min_field` to a flat panel.

  Together these give a uniform 2 cm pilaster every 1.0 m along a run, with
  no width discontinuity marking where one mesh ends. The 2 m module grid
  reads as a 1 m authored rhythm.

### Known
- `RELIEF`'s own default `bay` is still 2.4, so `center_city` and
  `industrial_flats` -- which declare no `relief` block and inherit the
  defaults -- remain inert in the same way, at `pier: 0.14`. Not changed
  here: it moves the look of themes this pass was not measured against.
- Articulation is still module-periodic BY CONSTRUCTION. `relief_parts` sees
  only `(w, d, h)`; it never learns where the module sits in the run, so it
  can change the rhythm's frequency but never its phase. Breaking that needs
  the slot index to cross the Deli Counter -> Zoo boundary. Roadmap 79.

## [0.52.0] - 2026-08-29

A flat wall was being shaded as a dome, on every instance, by a 3 mm chamfer.

### Fixed
- `bm_to_object` takes a `smooth_angle`, and `recipes/_arch.py` passes 0.0 --
  every architectural module now shades flat.

  `bevel_edges` cuts a one-segment chamfer sitting ~45 degrees off each face
  it touches; `SMOOTH_ANGLE_DEG` is 50, so the chamfer was SMOOTHED INTO the
  face. On a prop that is the highlight roll-off the bevel exists for. On a
  wall panel it is ruinous, because a box face has no interior vertices -- so
  every normal the face owns is a corner, every corner is splayed toward the
  chamfer, and nothing holds the middle flat.

  MEASURED on the shipped `wall_delco_01_w200.glb`: of the 15 vertices on the
  front face, NONE carried the face normal. Every one sat 28.9 degrees off it,
  at (+/-0.342, -0.876, +/-0.342) -- each pointing at its own corner. The panel
  shades as a cushion, and interpolating that across the quad's two triangles
  draws a diagonal wedge that repeats identically on all 66 placements because
  it is baked into one shared mesh.

  This is the artefact four other investigations failed to explain the same
  day: it survives world-space triplanar (it is normals, not UVs), survives
  `wear: 0.0` (not vertex colour -- that layer never reaches the renderer at
  all, roadmap 84), and survives deleting every fixture light (it is the sun).

  Scoped to `_arch.py` on purpose. Cylinders still need the 50-degree default:
  a 14-segment water tank at 25.7 degrees per segment reads as a dodecagon
  without it.

## [0.51.0] - 2026-08-29

Walked a themed level and it read as machine-made Lego. The relief was
drawing the bricks.

### Changed
- `genome/species/wall.json`: the `delco` style now carries its own
  `relief` block -- `pier` 0.14 -> 0.02, `reveal` 0.05 -> 0.015, plinth
  and cornice unchanged.

  WHY, measured rather than guessed. Deli Counter tiles every solid span
  into whole modules of `DC_MODULE` (default 2.00 m) and puts the
  remainder in a `wallEnd` (`deli_counter.py:756`, `_wall_span`); the
  shipped art directory for `bank_block_001` seed 7003 confirms it from
  the other end, containing exactly two wall meshes, `wall_delco_01_w30`
  and `wall_delco_01_w200`. So a 20 m facade is ten copies of one panel.

  `relief_parts` puts a pier flush with each module edge, which is
  correct -- centring one on the edge would double it at every seam. But
  two flush 0.14 m piers meet at each seam, so what the eye actually gets
  is a 0.28 m wide, 3.03 m tall, full-depth strip standing 0.05 m proud
  of the field, repeating at EXACTLY the module pitch, all the way along
  the building. The articulation meant to break up a facade was instead
  drawing its module grid in relief. At 0.02 that seam strip is 0.04 m
  and 0.015 m proud: present, no longer the loudest line on the wall.

  Base and cap are deliberately kept. They are the same height on every
  module, so they run continuous ACROSS the seams -- horizontal bands
  are the cue that reads as one building, and they cost nothing here.

  Nothing structural moves. The stem (`kit.module_stem`) does not carry
  relief, so Deli Counter's resolver sees the same filenames; the
  collider is built from `slab` and not from `visual` (`recipes/_arch.py`),
  so no collision box changes; and `relief_parts` guarantees the outer
  bbox stays exactly (w, d, h), so exact-fit still passes. Only the GLB
  bytes change.

  This is a first reading, not a settled value. `{"reveal": 0.0}` (what
  `rockay` uses) flattens the wall to a single panel and removes the
  plinth and cornice with it; the numbers here keep them.

### Known, not fixed here
- Every instance of a stem is byte-identical art: the wear RNG is keyed
  on the stem with a hardcoded seed 0 (`bpylayer/build.py:187`), and
  Pixelcoat builds one texture pack per material kind per MISSION, so
  every `concrete_delco_albedo.png` in a level is the same file. Relief
  cannot touch this -- there is one GLB per stem and it is instanced, so
  no build-time knob can vary two instances of it. `cube_project_uv`'s
  `uv_offset` is NOT the fix it looks like for the same reason: it would
  shift all instances together. The per-instance mechanisms that do exist
  (Patina `--slot-variation` + `instances.json`; Pixelcoat gen-7
  `variations`) are both implemented and neither is wired in.

## [0.50.0] - 2026-08-24

The marker path is the shipping path. Lux's fixture spawner -- not the
manifest bake -- is how every interior light reaches a composed site, and
two facts got lost on the way there: DC's new `drop` (the lamp's distance
to its room's floor) never rode the markers, so every fluorescent fell to
the range fallback and the arena's 5.6 m hall had a lit ceiling over a
pitch-black floor; and DC's new `pendant` type had no fixture species, so
it was skipped -- and a skipped anchor emits NO marker, which means every
basement and vault room was silently dark.

### Added
- `pendant_fixture`: the below-grade bare bulb (genome + recipe + the
  FIXTURES row). Cord from the slab, socket, faceted low-poly bulb; mount
  'above' puts the bulb exactly at DC's anchor (0.6 m below the ceiling)
  and the cord rises the rest of the way. Bulb carries `M_Pendant_Lens`,
  so the emissive binder and `set_fixtures_powered` treat it like every
  other lamp face.
- Every per-lamp placement (and its exported marker) carries the anchor's
  `drop` as `lux_drop` (core/fixtures.py `plan()`, bpylayer/build.py).
  Lux >= 0.21 reads it on the spawn path; a pre-0.97 manifest without
  drop stamps an honest 0.0 (the rig's fallback), never a guess.
- `tests/test_fixtures.py`: pendants get hardware not a skip; drop rides
  every lamp of a row; dropless manifests stay at 0.0.

### Fixed
- Plate visual tiles are UNBEVELED (`recipes/_arch.py`). Every box edge
  got a chamfer from the style bevel, and where two tiles abut the two
  chamfers form a V-groove that catches light differently than the flat
  face -- the thin bright/dark lines walked on the arena ceiling
  2026-08-24, at tile boundaries the census had already cleared of any
  budget defect. A flat plate's chamfer carries no information (its rim
  meets walls and parapets); walls and opening modules keep theirs --
  their chamfers sit on real corners. Proven in-session: 20 x 12 ceiling
  and 52 x 32 roof rebuild to pure 8-vert tile boxes, roof collision
  still one box.

## [0.49.0] - 2026-08-23

Roadmap item 54 -- one mesh should not span a room. Godot's GL Compatibility
renderer budgets positional lights PER MESH (`max_lights_per_object`, engine
default 8), and a plate module is one mesh: a 52 x 32 m roof was one light
budget for a whole building. Measured across lot_demo_001's five buildings as
111 meshes over 8 (worst at 36), which is the entire reason level_factory
ships a per-object light cap and its shader cost. Walls never had the
problem -- 2 m modules sit at 6 lights or fewer -- so plates now follow the
same law: no visual mesh wider than a light budget's reach.

### Added
- `core/arch.PLATE_TILE` (8.0 m) and `core/arch.tile_parts`: cut any plate
  part wider than the tile (x or y) into a grid of equal cells -- never
  fixed strides, so there is no sliver tile at an edge (item 41's
  fragmentation counter-pressure, answered rather than traded into).
  Interior cut lines snap to whole millimetres so the house 6-decimal
  rounding of each tile's center and size is lossless: neighbours meet at
  the same coordinate and `parts_bbox` still returns the authored dims
  exactly. Parts already inside the tile pass through byte-identical, name
  included -- every wall, jamb and small plate in the library is untouched.
- `recipes/_arch.build_slab` runs the plate VISUAL through `tile_parts`
  (genome `plate_tile` overrides the default). VISUAL ONLY: collision keeps
  coming from the untiled `plate_parts` list -- the same structure/visual
  split the wall path already makes for relief -- so no collision box on
  any existing build moves. Proven in-session on the arena-class case: a
  52 x 32 m roof with the bank-branch ladder void builds as 43 tiles, every
  edge <= 7.429 m, 4 collision boxes exactly as before, outer bbox exact,
  ladder column open.
- `tests/test_plate.py`: the tiling section -- budget edge, area and bbox
  conservation, byte-identical pass-through (small plate, holed plate,
  exactly-tile-sized plate), no slivers, stairwell stays open, unique
  deterministic names, shared edges at 6 decimals, collision from the
  untiled plate, tile <= 0 disables.

The tile size is a starting value the per-mesh light census
(`tools/mesh_light_census.py`, factory root) has to confirm; the item closes
when the census shows zero meshes over the engine default of 8 and
level_factory deletes `PER_OBJECT_CEILING`.

## [0.48.0] - 2026-08-22

### Added
- `glass_shard`: cosmetic glass debris for the breakable-glass destructible
  pattern -- flat angular fragments cut by `geometry.fracture` from plates at
  pane thickness, ONE OBJECT PER SHARD. Litter and rubble merge their chunks
  into a single mesh; a game that flings debris needs each piece addressable
  (the lasertag addon wraps every shard mesh in its own rigid body and gives
  it a seeded impulse). Kind `glass`, so the SAME Pixelcoat pack that skins a
  window module's pane lands on every shard at uniform world density; the
  genome tints match `window.glass_color`, so the flat fallback matches too.
  Collisionless by construction, like the rest of the dressing debris.
- `window_broken`: the broken STATE of a window slot per INTERACTIVES.md --
  same slab, jambs, sill and header at the same dims (the void is
  `arch.void_for`'s answer for `window`, deliberately, so the hole cannot
  move between states), the pane replaced by clean remnant strips in the
  frame. Declared on a slot as `state_geometry {"intact": "window",
  "broken": "window_broken"}` and built as
  `window_<theme>_<style>_w<cm>_broken.glb`; the resolver falls back to the
  intact window until the variant is built. Clean strips on purpose: breach
  ships the clean cutout, and the jagged shatter edge is the same later art
  pass.
- `tests/test_glass_debris.py`: the prompt door, kit expansion (mirroring
  the breachable-wall tests slot for slot), the module plan at exact slot
  dims, and the shard/pane kind + tint agreement.

### Fixed
- `floor` and `ceiling` genomes no longer claim `collision: true`. The plate
  recipe deliberately emits no collision boxes (Deli Counter's holed trimesh
  slab underneath stays authoritative -- the stairwell rule), so the claim
  was a mirror the validator believed: `build_module` reads its collision
  expectation from the genome, and every floor/ceiling module in every kit
  build has FAILED its collision check since plates stopped emitting.
  Measured on cr_deli: 28 of 70 modules failed, exactly the building's 14
  floor + 14 ceiling plates, every one of whose slots declares
  `collision: "none"`; after the genome edit the same build is 0 failed,
  with plates at WARN on the pre-existing thin-height advisory. `roof` is
  the plate that DOES collide and keeps `collision: true`.
- `build_roof_props` crashed with NameError at its first placement: a v0.30
  copy of build_fixtures' LuxEmit marker block referenced `fixtures_mod`
  without importing it, and roofprops placements carry none of the keys the
  block reads (type / anchor_id / slot / reacts_to_alarm). The block is
  REMOVED rather than repaired: an HVAC unit or a water tank is hardware
  that emits no light, so there is no emitter point for Lux here -- that
  contract lives on the lights.json -> build_fixtures path, which keeps it.
  Reproduced before the fix (NameError, build.py:507, first placement) and
  rebuilt after it (18 props on a 20x15 test roof). Because the block could
  never have completed one placement, no shipped GLB ever contained these
  markers and no output changes.

### Notes
- The species rosters in `tests/test_genome.py` grew deliberately:
  `glass_shard` joins DRESSING_SPECIES, `window_broken` joins ARCH_SPECIES.
- `window_broken` carries the keyword "window broken" so the species' own
  name resolves through the prompt door; the prompt-unreachable set stays
  exactly {wallCorner, wallEnd}.
- Consumed by lasertag's `LT_Destructible` (`debris_scenes` + the `_broken`
  state visual): the game owns the state machine and its replication; these
  species own only what a break looks like, per the ownership table in
  INTERACTIVES.md. Zoo stays offline and deterministic.

## [0.47.0] - 2026-08-21

### Added
- `tests/test_recipe_reads_its_genome.py` sweeps every recipe module and fails
  when one builds materials but never reads a `material` key -- the defect that
  made `flat_top_grill`'s genome inert. `cheesesteak` is exempt with a written
  reason, and the test also fails if an exempt recipe starts reading its genome,
  so the exemption cannot go stale unnoticed.

### Corrected
- The 0.45.0 entry states that with `ensure_ascii=False` all 53 genomes
  round-trip. That is wrong. 49 of 53 do; `litter_scrap`, `pebble`,
  `rubble_frag` and `weed_tuft` do not. The selftest that measured it was
  written after that entry was published. The 0.45.0 text is left standing and
  corrected here, matching how the batch-1 note was corrected in 0.45.0 itself.

### Notes
- Measured, not assumed: 53 recipe modules, 79 `make_material` calls. Exactly
  one recipe (`cheesesteak`) never consults its genome. Every inert genome
  offers a single option, so nothing renders wrong today; the exposure is that
  a second option would be ignored in silence.
- An earlier pass flagged 7 literals as shadowing their genome. 6 were false
  positives: the body already passed `plan["material"]` and the literal was a
  sub-part with its own fixed colour -- a bottle cap, a safe's trim, the paper
  boat under the fries. Replacing those would have tinted the boat with the fry
  colour. Sub-part literals are correct and this test says nothing about them.
- Ten material kinds became resolvable this release via pixelcoat 0.16.0: canvas,
  carbon, dirt, gravel, laminate, leather, paper, rubber, tar, vegetation. All
  ten resolve through `skins.find_pack` in all five built themes.

## [0.46.0] - two modules with one filename now say so

`plan_kit` builds its bucket key from (type, width, state, species, glaze,
style, MATERIAL, dims, voids, openings). `module_stem` builds the filename
from everything in that list EXCEPT material. So two buckets can be two
distinct modules with one stem: they build differently, because
`dna.resolve_module_plan` reads `module["material"]` as an override, and one
overwrites the other on disk.

Measured over 280 manifests: 19 stems across 17 buildings, every one floor or
ceiling.

### Added
- `plan_kit` returns `stem_collisions` and prints one line per collision.

### THIS DOES NOT FIX THE COLLISION, and adding material to the stem would have been the wrong fix
Six hypotheses were tested before this landed. The root cause is upstream in
Deli Counter: `carpet`, `tile` and `ceiling_tile` are absent from every
spec's `materials` list, so `skin_style.style_for` falls through to
`default_material` and hands all of them one style. 410 of 574
(building, plate material) pairs resolve to style 1.

Style is what selects the Pixelcoat pack AND what goes in the filename. So
`_m<material>` in the stem would have separated 1,677 filenames while leaving
a carpet floor still wearing concrete's skin -- fixing the visible 3% and
entrenching the other 97%. What was wrong was never the naming law.

Ruled out along the way, each by reading rather than reasoning: manifests
predating per-slot style (all 1,677 plate slots carry one); `skin_style`
never written (it exists); `style_for` never called (floors.py:231, :240,
roofs.py:81); the wiring being incomplete (it is complete).

## [0.45.0] - batch 2: the rest of the coloured metal, and two inert genomes

Eight species off raw `metal`. Three take paint, five take bare metal --
which is NOT the 7/1 split the batch-1 notes predicted, because that grouping
ranked by chroma rather than by what the material is.

    metal_painted   filing_cabinet  putty/beige office steel   chroma 0.150
                    chair           warm brown frame                  0.216
                    atm             dark cool housing                 0.104

    metal_bare      gold_bar        gold                              0.610
                    water_tank      warm brown -- that is RUST        0.120
                    flat_top_grill  bright cool -- stainless          0.111
                    shelving        cool grey-blue steel              0.106
                    vault_door      cool steel                        0.100

The hue decides it, not the magnitude. `flat_top_grill` at
[0.677, 0.723, 0.787] is the blue cast of stainless, not a colour anyone
chose; `filing_cabinet` at [0.450, 0.420, 0.300] is unmistakably paint; and
`water_tank`'s warm brown is weathering, so painting it would have been
wrong in a way no test would catch.

### Fixed -- two genomes that were INERT
- **`flat_top_grill.py` passed the literal `"metal"` to all three of its
  `make_material` calls.** Its genome's `materials.default`, `options` and
  every style's `material` were read by nothing. Editing that genome changed
  NOTHING, silently, and would have looked like the split failing.
- **`vault_door.py` hard-coded only its hub.** The body read `plan["material"]`
  already, so the moment the genome moved off `metal` the door would have
  rendered across two material kinds.

Both now pass `plan["material"]`, and
`test_recipes_no_longer_hardcode_the_kind` asserts the literal is gone.

### Corrected
The batch-1 notes recorded `shelving.json` as the one genome that is not
byte-exact `json.dumps(indent=1)` round-trippable, needing an anchored edit.
That was wrong. It carries an em dash in `notes`, and the CHECK used the
default `ensure_ascii=True`, which escapes it to `\u2014`. With
`ensure_ascii=False` all 53 genomes round-trip and every edit here is
structural.

### Changed
- `tests/test_material_options_closed.py` now tracks PAINTED and BARE sets
  rather than a single batch list, asserts no species offers both (one
  object, one metal), and keeps the all-53 sweep of the options invariant.

### Still on plain `metal`
30 species, every one of them measured at chroma < 0.10 -- already near-grey,
so the theme-owned kind is the right answer. Ten are architecture and must
keep it.

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
