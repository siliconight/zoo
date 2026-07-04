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
| Species | An asset type — 12 so far (desk, chair, atm, vending_machine, briefcase, ...) |
| Specimen | One generated instance |
| Keeper | The Blender UI panel |
| Habitat | A themed collection of species (roadmap) |
| Exhibit | Output folder / demo scene |

## Species

`desk`, `chair`, `helmet`, `boots`, `simple_car`, `filing_cabinet`, `table`, `crt_tv`, `atm`, `vending_machine`, `briefcase`, `cash_stack`

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

Flags: `--seed N`, `--count N`, `--no-collision`, `--lods`, `--no-blend`,
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

- Collision: the `-colonly` sibling becomes a static collision shape on
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
