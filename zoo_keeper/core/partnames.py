"""What a part's NAME means, and how parts group when they are merged.

Pure: no Blender. `bpylayer.merge` does the geometry; this file owns the
decisions, so they can be tested without Blender and read without bmesh.

TWO CONSUMERS READ A VISUAL PART'S NAME, and both are the reason
`group_parts` keys on more than the material:

  * `deli_counter/portable_building.py` (`STOCK_NODE_PREFIX = "Stock_"`)
    filters surface-stock nodes out of a module's measured extent before
    `verify_placement` judges it. Its own comment records three office desks
    0.75 m authored reading 1.12-1.13 m, and five spurious height advisories,
    when the stock was left in.
  * `patina/patina/surfaces.py` forces `SurfaceRole.TRIM` on a mesh whose
    name carries `trim`, `rail`, `counter`, `ledge`, `sill` or `molding`.

Keying on the part-name FAMILY keeps both readable after a merge, because
every source in a group then shares the prefix its merged name is built from.

A THIRD READER IS THE ENGINE ITSELF. Godot's glTF importer has no collision
field: it decides from the node name's suffix. Six places re-implement that
test (`lot/site_collision.py`, `lot/site_ground.py`,
`level_factory/packages/validation/glb_collision.py`, `patina/patina/mesh.py`,
`deli_counter/.../nav_gate.gd`, and Zoo's own `bpylayer.export`), and
`level_factory/.../glb_collision_flag.py` turns collision ON by renaming a
node. So the suffix is the contract, `COL_SUFFIXES` is Zoo's spelling of it,
and a merged visual part is checked against it rather than trusted.
"""
from __future__ import annotations

#: Godot's collision name-suffix conventions. Any of these on a mesh node
#: makes it a static collision shape on import and drops the visual.
COL_SUFFIXES = ("-colonly", "-convcolonly", "-col", "-convcol")

#: Surface dressing set ON a host module -- a desk's monitor, a counter's
#: stock. Counts toward the host's triangles, never toward its envelope.
STOCK_PREFIX = "Stock_"

#: Substring marking a level-of-detail alternate rather than a part.
LOD_MARK = "_LOD"

#: THE LIGHT-BUDGET MARK (1.24.0): a part whose name ends with it is never
#: merged. `arch.tile_parts` cuts a room-sized plate into tiles no more than
#: `PLATE_TILE` (8 m) on a side so each is its OWN light budget -- GL
#: Compatibility lights at most `max_lights_per_object` (8) positional lights
#: per MESH (roadmap 54) -- and 1.1.0's merge packs them back into one mesh per
#: material. `_arch.build_slab` marks a floor's or ceiling's tiles with this
#: when its module asks for `light_budget_tiles`, which Deli Counter (>=
#: 0.157.0) sets on the plates of a room lit from outside through storefront
#: glass -- where the budget was measured to bind.
#:
#: SUPERSEDED, kept above what replaced it: 1.23.0 made EVERY floor and
#: ceiling unmergeable (`LIGHT_BUDGET_FAMILIES = ("Floor", "Ceiling")`), the
#: walker's "split the floor and ceiling tiles". It restored the room it was
#: for -- gas_station_a02's carpet seen through the glass 16.9 -> 20.5 on cold
#: run 9106 -- and priced library-wide at draws 71,802 -> 77,139 summed over
#: the 53 headings (+4 to +230 at 51 of them), median p95 4.76 -> 5.1-5.2 ms
#: and 7 -> 10-11 stations over the provisional budget, because every room
#: over 8 m in every building split and interiors have no occlusion culling.
#: The walker, 2026-09-29: "yes, narrow it to the storefront rooms".
LIGHT_BUDGET_MARK = "_lbt"

#: Material-name prefixes stripped when naming a merged part. Zoo names every
#: skinned material `M_Skin_<pack>` and every flat one `M_<what>`.
_NAME_STRIP = ("M_Skin_", "M_")


def family(name):
    """The part-name family: everything before the first underscore.

    `PackWall_Box0_3_2` -> `PackWall`; `Stock_Monitor` -> `Stock`. The same
    split `tools/glb_nodes.py` groups its node census by.
    """
    return name.split("_", 1)[0]


def is_collision(name):
    """Whether Godot would import this name as collision.

    Case-insensitive, and a `.001` duplicate suffix is stripped first --
    `lot/site_collision.py:225` documents both, and a check that missed
    either would call a collider a visual.
    """
    low = name.strip().lower()
    while len(low) > 4 and low[-4] == "." and low[-3:].isdigit():
        low = low[:-4]
    return low.endswith(COL_SUFFIXES)


def is_mergeable(name):
    """A visual part: not a collision proxy, not a LOD alternate, not a
    light-budget tile (`LIGHT_BUDGET_MARK`)."""
    return (not is_collision(name) and LOD_MARK not in name
            and not name.endswith(LIGHT_BUDGET_MARK))


def material_slug(material_name):
    """A merged part's name-tail, taken from the material it carries."""
    if not material_name:
        return "unmatted"
    slug = material_name
    for pre in _NAME_STRIP:
        if slug.startswith(pre):
            slug = slug[len(pre):]
            break
    return slug or "unmatted"


def merged_name(fam, material_name, taken):
    """A deterministic name for one merged group. ``taken`` is not mutated."""
    slug = material_slug(material_name)
    base = slug if slug.startswith(fam) else "%s_%s" % (fam, slug)
    # A merged VISUAL part whose name ended in `-col` would import as a
    # collider and stop being drawn. Nothing produces this today; it costs
    # one branch and one test to make sure nothing ever does.
    if is_collision(base):
        base += "_visual"
    name = base
    n = 2
    while name in taken:
        name = "%s_%d" % (base, n)
        n += 1
    return name


def group_parts(parts, taken=()):
    """Plan a merge. Descriptors in, groups out.

    ``parts``: an iterable of ``(name, material_name, layer_signature)``, one
    entry per (object, material slot) pair that actually carries faces.
    ``layer_signature`` is any hashable describing the mesh's UV and colour
    layers. Parts whose layers differ cannot share a mesh without inventing
    values for whichever layer is missing -- a part with no `Wear` colours
    merged into one that has them would be written black -- so the signature
    is part of the key rather than something reconciled afterwards.

    ``taken``: names already spoken for, which a merged name must avoid.
    MEASURED, not defensive. `wall_pack` at the `min` corner names a part
    `WallPack_Lens` and paints it with `M_WallPack_Lens`, so the merged name
    built from family plus material slug is the part's own name -- and
    because the merge is non-destructive the part is still there. Blender
    resolved it by appending `.001`, which would have gone into the glTF
    node name and made the export non-reproducible; `bpylayer.merge` asserts
    against exactly that and refused to build the module. Seeding this set
    with the module's own object names is what keeps the two apart, and it
    stays deterministic because the seed is the module's parts and nothing
    else.

    Returns ``[(merged_name, key, [source_name, ...]), ...]`` ordered by key,
    each group's sources sorted by name. Sorted, not hash- or link-ordered,
    so the same spec builds the same bytes.
    """
    buckets = {}
    for name, mat, sig in parts:
        if not is_mergeable(name):
            continue
        buckets.setdefault((family(name), mat or "", sig), []).append(name)
    out = []
    used = set(taken)
    for key in sorted(buckets, key=lambda k: (k[0], k[1], repr(k[2]))):
        fam, mat, _sig = key
        name = merged_name(fam, mat or None, used)
        used.add(name)
        out.append((name, key, sorted(buckets[key])))
    return out
