# Zoo

Offline procedural game asset compiler. Plain-text prompt in, Godot-ready
asset out:

```
prompt -> Asset Intent Spec -> Genome -> DNA BuildPlan -> Blender geometry
       -> validation -> .glb + .blend + meta.json
```

**Tooled procedural construction, not AI mesh generation.** No cloud, no
scraping, no copyrighted source meshes. Construction knowledge is
CC0-derived and every specimen carries its license metadata in its
`meta.json` sidecar.

## Glossary

| Term | Meaning |
|---|---|
| Genome | Per-species construction knowledge (`zoo_keeper/genome/species/*.json`) |
| DNA | Recipes that turn a plan into geometry (`zoo_keeper/recipes/`) |
| Species | An asset type — 29 so far: 21 props + 8 architectural modules |
| Specimen | One generated instance |
| Keeper | The Blender UI panel |
| Habitat | A themed collection of species (roadmap) |
| Exhibit | Output folder / demo scene |

## Low-poly heroes (PS1/N64)

Beyond hard-surface props, Zoo builds simple *low-poly* heroes — chunky,
faceted, deliberately retro. The organic look comes from three primitives,
not sculpting:

- `add_ellipsoid` — faceted blobs (buns, produce)
- `jitter_verts` — deterministic per-vertex offset (organic irregularity)
- `core.scatter` + `geometry.place` — deterministic piles (steak, fries,
  onions: one chunk, duplicated, randomized, joined)

`cheesesteak` is the flagship: a jittered roll, a scattered meat pile, draped
cheese, onion bits — ~2k tris, PS1 detail, fully deterministic. `soda_cup`
shows the tapered-cylinder cup. Sculpted high-detail heroes remain out of
scope (hand-model those to the same standards).

## Dressing a greybox (Deli Counter / Lot integration)

Zoo is designed to be [Deli Counter](https://github.com/siliconight/deli-counter)'s
`art/zoo` module library. Deli Counter greyboxes a building and emits a
`<name>.slots.json` swap contract — every wall / doorway / window / breach slot
with a transform, fit dims, and a role — and its resolver looks for
`<type>_<theme>_<style>_w<cm>.glb` in `art/zoo`, instancing that themed module
at the slot (falling back to greybox when a module is missing, so the art pass
is progressive). Same coordinate space (Blender Z-up, meters), so a Zoo module
drops onto a slot with no conversion.

Plan the modules a building needs (pure, no Blender):

    python tools/zoo_cli.py --kit path/to/<name>.slots.json --theme delco

It reads the slot contract and reports the distinct modules to build, honoring
Deli Counter's naming law (wall remainders collapse to one scaled `wallEnd`
unit; everything else is exact-fit per width). A real 128-slot building needs
only ~9 modules — that's the whole art-pass workload.

**Build** those modules straight into an output folder (needs Blender):

    blender --background --python tools/zoo_cli.py -- \
      --build-kit path/to/<name>.slots.json --theme delco --out art_zoo

Each module is a **center-pivot** slab built to the slot's **exact** dims and
named by the resolver's law (e.g. `wall_delco_01_w200.glb`,
`doorway_delco_01_w110.glb`, `wallEnd_delco_01.glb`), with a
`<building>_kit.built.json` index. Copy the folder into your game's `art/zoo/`,
rebuild the greybox with `theme=delco`, and the resolver swaps them in for the
grey boxes — missing modules keep the box, so the art pass stays progressive.

> The current module look is a plain **structural pass** (generic industrial
> concrete + steel frames). Doorways/breaches are open passages; the door leaf,
> mullions, and a blown/rough breach are Delco look-passes still to come.

**Interactive fixtures** (doors, breachable walls) whose state all players must
agree on are handled as replicable state machines — see
[`INTERACTIVES.md`](INTERACTIVES.md). A slot's `interactive` block expands into
per-state art variants (`wall_delco_01_w200` + `_breached`), so a breachable
wall is the *breached state of a wall slot*, not a separate module. The state
machine + replication live in `gameplay.json` / the game, network-solution
agnostic; Zoo only builds the art each state points at.

## Connectors (Lego-style anchoring)

Every asset exports named `ATT_*` markers and now carries a typed **connector**
block in its `meta.json`, so props snap onto players and levels the way a Lego
stud only fits an anti-stud:

- an asset's **anchor** = how it attaches (its type: `head`, `feet`, `grip`,
  `surface`, `floor`, ...).
- an asset's **sockets** = where other things attach to it (a table declares
  `ATT_surface_center` as type `surface`).
- they connect only when the types are **compatible** (a `grip` anchor fits a
  `hand_l`/`hand_r` socket; a `cup`/`surface` anchor rests on a `surface`; a
  `head` anchor will NOT sit on a table).

Declare connectors in the genome (pack-friendly, no code):

    "connectors": {
      "anchor":  {"type": "head"},
      "sockets": {"ATT_surface_center": "surface"}
    }

Sockets have a **shape**, so a connection can be one spot or a whole region:

- `point` (default) — one exact spot: a helmet on a head, a lid on a cup.
- `area` — a surface region (e.g. a tabletop): place the prop anywhere on it.
  Declare with `"shape": "area"` and a `"size"` or `"size_rel"` (a fraction of
  the asset's width/depth, so it scales per specimen).
- `grid` — Lego studs: a repeating grid; snap to the nearest cell. Declare a
  `"size"` and a `"cell"` spacing.

    "sockets": {"ATT_surface_center":
                {"type": "surface", "shape": "area", "size_rel": [0.85, 0.85]}}

In Godot's Snap, tick **Free placement** to drop a prop wherever you left it on
a surface (keeps X/Z, matches the surface height) instead of jumping to the
exact point — a cup can sit anywhere on the table.

**Attach to a player:** add empties to your character rig following Zoo's
socket convention — `ATT_head`, `ATT_hand_l`, `ATT_hand_r`, `ATT_back`,
`ATT_hip`, `ATT_feet`, `ATT_chest`. A helmet (anchor `head`) snaps to
`ATT_head`, a briefcase (`grip`) to a hand.

**Attach to a level:** give modules `surface`/`floor`/`wall` sockets; props
snap onto them.

**Snap in Godot:** with the Zoo Importer dock, select the prop, Ctrl-click the
socket (`ATT_*` node), and hit **Snap** — the prop's anchor aligns to the
socket.

## Organizing a collection (exhibits: zoo / museum)

Point Zoo at a folder of built or ingested GLBs and it lays them out into a
browsable **exhibit** — the game-dev "asset zoo" pattern (Gyms/Zoos/Museums by
Robin-Yann Storm). It reads each asset's `meta.json` footprint and computes an
organized layout so you see scale and everything at a glance. Pure — no
Blender needed to plan the layout.

    # knolled grid + a 1.8m / 1m scale reference
    python tools/zoo_cli.py --exhibit exhibits --scheme zoo

    # each asset on a labelled pedestal (name + size)
    python tools/zoo_cli.py --exhibit exhibits --scheme museum --cols 6

Writes `<folder>_<scheme>.exhibit.json`. Import it with the Zoo Importer dock
in Godot: members drop in at their computed spots, and the dock spawns
pedestals, `Label3D` placards, and scale markers natively. Works on generated
and ingested assets alike — one place to see your whole prop library.

## Adopting external assets (ingest)

Zoo can also *condition* assets it didn't generate — drop in an itch.io pack,
take what you want, and get Zoo-standard GLBs out. Same normalization every
generated asset gets: pivot bottom-center on Z=0, applied transforms, optional
scale-to-size, optional bbox collision, a provenance `meta.json`, Godot-ready
GLB. Formats: glb/gltf/fbx/obj/dae/stl/ply.

List what's importable in a pack (works without Blender):

    python tools/zoo_cli.py --ingest pack.zip --list

Ingest one, scaled to a species' real-world size from its genome:

    blender --background --python tools/zoo_cli.py -- \
      --ingest pack.zip --pick models/chair.fbx \
      --as-species chair --as-name diner_chair --out exhibits

Or scale to an explicit height, or leave as-is (assumed already meters):

    ... --target-height 0.9        # scale overall height to 0.9m
    ... --license "CC0 (Kenney)"   # recorded in the meta.json

Zoo records provenance but grants no rights — confirming the asset's license
is on you. The output GLB drops into Godot exactly like a generated one.

## Adding a species (Knowledge Packs)

A species is self-describing — adding one needs **no edits to the engine**:

1. **Drop a genome** at `zoo_keeper/genome/species/<name>.json`. Besides the
   dimensions/parts/styles, it carries its own:
   - `"keywords"`: the prompt words that select it (longest match at the
     earliest position wins, so `"soda machine"` beats `"soda"`).
   - `"prompt_rules"` (optional): declarative keyword logic, e.g.
     `{"any": ["mustard"], "set": {"color": [0.86,0.72,0.12]}}` or
     `{"any": ["police","brim"], "set": {"params.brim": 1}}`. Keys can be
     `color`/`material`/`style` or `params.<x>`.
   - `"collision"` (optional bool): per-species default.
2. **Drop a recipe** at `zoo_keeper/recipes/<name>.py` exposing
   `build(plan, streams, collection)`. It's auto-discovered by filename.

That's it — the genome is globbed, the keywords and rules are read from it,
and the recipe is imported by name. The only thing still requiring code is a
*computed* dimension (e.g. boots deriving height from shaft length), which
lives as a small hook in `core/dna.py` `_SPECIES_EXTRAS`.

## Species

**Props (21):** `desk`, `chair`, `helmet`, `boots`, `simple_car`, `filing_cabinet`, `table`, `crt_tv`, `atm`, `vending_machine`, `briefcase`, `cash_stack`, `soda_cup`, `cheesesteak`, `flat_top_grill`, `condiment_bottle`, `french_fries`, `security_camera`, `queue_stanchion`, `drop_safe`, `gold_bar`

**Architectural modules (8):** `wall`, `wallEnd`, `doorway`, `window`, `breach`, `vault_door`, `teller_line`, `safe_deposit_boxes` — Deli Counter wall-slot dressing (`vault_door` is an interactive hero portal: closed frame+leaf+hub; open/breached states reuse doorway/breach). Built center-pivot at exact slot dims and named by the resolver's law; see [Dressing a greybox](#dressing-a-greybox-deli-counter--lot-integration). Buildable standalone too (`--prompt "a wall"`).

## Install (Blender 4.2+ / 5.x)

The add-on is the `zoo_keeper/` folder in this repo. Two ways to install:

- **From the repo (dev):** Edit > Preferences > Add-ons > Install from Disk
  and point at `zoo_keeper/` — or drop the folder in your Blender addons
  path. No zip needed when you already have the repo cloned.
- **Redistributable zip:** run `.\tools\build_addon.ps1` to produce
  `dist\zoo_keeper_blender_addon_v<version>.zip` (package at the zip root, as
  Install from Disk expects). This is a build artifact — attach it to a
  GitHub Release; it is gitignored, not committed.

Legacy `bl_info` and an extension `blender_manifest.toml` are both included.

The Keeper panel lives in the 3D Viewport sidebar: press **N**, pick the
**Zoo** tab, type a prompt, hit **Generate Specimen**.

## Headless CLI

Full build (PowerShell):

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
    --background --python tools\zoo_cli.py -- `
    --prompt "1990s office desk with two drawers" --out exhibits
```

Dry run — resolved Intent + BuildPlan as JSON, no Blender needed:

```powershell
python tools\zoo_cli.py --prompt "1990s office desk with two drawers" --plan
```

Flags: `--seed N`, `--count N`, `--collision` / `--no-collision` (force on/off; default is the per-species genome default), `--lods`, `--no-blend`,
`--species-list`.

Variants — one prompt, a cohesive family across seeds `base..base+N-1`
(shared style/material/palette, unique proportions and wear):

```powershell
blender --background --python tools\zoo_cli.py -- `
    --prompt "1990s office chair" --count 30 --out exhibits
```

Each sibling is a full specimen (own glb/blend/meta) and is reproducible on
its own with `--seed`; a `<family_id>.family.json` index lists them all.
`--count N --plan` previews the family without building.

Habitats — one theme, a set of *different* species that share a look
(the theme is prepended to each species' prompt, so cohesion is automatic):

```powershell
blender --background --python tools\zoo_cli.py -- `
    --prompt "1990s office" --habitat office --out exhibits
```

`--habitat` takes a named set (`starter` = all five, `office` = desk+chair,
`gear` = helmet+boots) or a comma list (`desk,chair`). A
`<habitat_id>.habitat.json` index lists the members; `--habitat X --plan`
previews without building.

## Outputs per specimen

- `<species>_<hash>.glb` — meshes with UVs, vertex wear colors (COLOR_0),
  flat Principled materials, `-colonly` collision sibling (imports as collision-only), `ATT_*` attachment
  empties, optional `_LOD1/_LOD2`
- `<species>_<hash>.blend` — editable source (optional)
- `<species>_<hash>.meta.json` — intent, plan, genome version, license,
  validation report. Timestamp-free by design.

## Determinism

Same normalized prompt + species + seed + tool version = byte-identical
plan and geometry. Every subsystem draws from its own SHA256-derived RNG
stream, so adding a subsystem never disturbs existing randomness.

## Godot import notes

- Collision: on by default per species (pickups like `cash_stack` default to none; force with `--collision` / `--no-collision`). When present, the `-colonly` sibling becomes a static collision shape on
  import automatically, with no visible mesh (collision-only).
- Wear: on the imported material enable **Vertex Color > Use as Albedo**
  to multiply the baked grime into the base color.
- Units: real-world meters, +Y-up handled by the glTF exporter.

## Validation

Every build is checked: dimensions vs genome range, tri budget (warn),
UVs, wear colors, materials, named parts, collision presence, applied
transforms. Status PASS / WARN / FAIL is printed and stored in the
sidecar.

## Development

Pure-Python core (`zoo_keeper/core/`) has zero bpy imports and is fully
unit-tested: `python -m pytest tests`. The bpy layer
(`zoo_keeper/bpylayer/`, `recipes/`) uses bmesh + data API only; the only
`bpy.ops` calls are the two background-safe exporters.

## Godot (Phase 3)

A Godot 4.x editor plugin that imports family/habitat manifests into a scene
lives in `godot/addons/zoo_importer/` — see `godot/README.md`.

## Roadmap

Phase 0 desk prototype (done) -> Phase 1 five species (done) -> Phase 2
variant families + habitat batch (done) -> Phase 3 Godot importer (in
progress: `godot/addons/zoo_importer/`) -> more habitats -> knowledge packs
-> deeper Godot editor integration.

## License

MIT (c) 2026 GabagoolStudios

## Dressing (Patina facade covers)

Patina (v0.11+) places facade dressing and skins it, then hands Zoo the
geometry to build:

```bash
# Patina emits <building>.dressing.json + a trim atlas
python tools/zoo_cli.py --dress gs_corner_station.patina.dressing.json --theme delco --out art/zoo
```

Zoo reads the per-anchor build orders (roof edges, base courses, curbs, conduit
runs), builds a thin proud cover strip per order oriented by the anchor normal,
and writes one `<building>_dressing.glb`. **Covers carry no collision** — they
are visual only, so the Deli Counter greybox collision stays authoritative.
Theme resolves to the same `delco` style the kit uses, so covers match the
building. See Patina's `docs/DRESSING_CONTRACT.md` for the manifest shape.

