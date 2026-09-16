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
