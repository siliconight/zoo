"""One mesh per material, and the names that survive it.

Zoo shipped every part of every prop as its own MeshInstance3D, so a prop
cost one draw call per part. Measured on cold run 9062's card shop, read out
of the shipped glTF JSON: 1,602 visual meshes across 90 module GLBs carrying
274 distinct materials -- the pack wall alone 118 meshes for 4 materials and
1,592 triangles. Frame cost on that package tracked draw calls, not geometry
(1,730 calls -> 9.49 ms, 6,376 -> 25.59 ms, primitives flat near 1.4M
throughout).

`core.partnames` decides what merges with what; `bpylayer.merge` does the
geometry. These are the rules, and each one is here because something
downstream reads a name:

  * a COLLIDER never merges -- Godot's importer decides solidity from the
    node-name suffix, and `lot/site_collision.py`, `lot/site_ground.py`,
    `deli_counter/zfight_gate.py`, `patina/patina/mesh.py` and
    `deli_counter/.../nav_gate.gd` each re-implement that test;
  * a `Stock_*` part never merges with a non-stock one --
    `deli_counter/portable_building.py` filters those out of a module's
    measured extent, and its own comment records three 0.75 m desks reading
    1.12 m when they were left in;
  * a `_LOD` alternate never merges -- it stands in for a part, not beside
    it, and merged into the base it would draw twice;
  * parts whose UV/colour LAYERS differ never merge -- a part with no `Wear`
    colours folded into one that has them would be written black;
  * the merged name never ends in a collision suffix, or the thing stops
    being drawn;
  * and the whole plan is SORTED, so the same spec gives the same bytes.

MEASURED, so the family guard is priced rather than assumed: keying on the
part-name family costs nothing on cold run 9062's three buildings -- card
shop 1,602 parts -> 274 meshes by material alone and 274 with the guard,
country club 525 -> 175 and 175, market hall 532 -> 134 and 134.
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import partnames

#: The pack wall as shipped: 117 visual parts over 4 materials, one collider.
_PACK_WALL_MATS = {
    "PackWall_Back": "M_Skin_slatwall_delco_1997",
    "PackWall_Upright0": "M_Skin_metal_painted_delco_1997_ccc9c2",
    "PackWall_Upright1": "M_Skin_metal_painted_delco_1997_ccc9c2",
    "PackWall_Kick0": "M_Skin_slatwall_delco_1997",
    "PackWall_Box0_0_0": "M_Skin_paper_delco_1997_8c8578",
    "PackWall_Box0_0_1": "M_Skin_paper_delco_1997_8c8578",
    "PackWall_Art": "M_PackWall_PackWall_303x163_6c2c10d2_Art",
}
_SIG = (("UVMap",), (("Wear", "CORNER", "BYTE_COLOR"),))


def _parts(mapping, sig=_SIG):
    return [(name, mat, sig) for name, mat in mapping.items()]


def test_one_group_per_material_not_per_part():
    groups = partnames.group_parts(_parts(_PACK_WALL_MATS))
    assert len(groups) == 4, [g[0] for g in groups]
    # slatwall 2, painted metal 2, paper 2, the art plate 1.
    sizes = sorted(len(srcs) for _n, _k, srcs in groups)
    assert sizes == [1, 2, 2, 2]
    assert sum(sizes) == len(_PACK_WALL_MATS)


def test_collider_is_never_merged():
    parts = _parts(dict(_PACK_WALL_MATS))
    parts.append(("PackWall-colonly", None, _SIG))
    groups = partnames.group_parts(parts)
    merged = {s for _n, _k, srcs in groups for s in srcs}
    assert "PackWall-colonly" not in merged
    assert len(groups) == 4


@pytest.mark.parametrize("name", [
    "Wall-colonly", "Wall-convcolonly", "Wall-col", "Wall-convcol",
    "WALL-COLONLY", "Wall-colonly.001", "Wall-col.012",
])
def test_every_spelling_of_a_collider_is_recognised(name):
    # Godot matches the suffix case-insensitively and tolerates a `.001`
    # duplicate suffix (`lot/site_collision.py:225`).
    assert partnames.is_collision(name)
    assert not partnames.is_mergeable(name)


@pytest.mark.parametrize("name", ["Wall_Panel", "PackWall_Box0", "Colonly_Top",
                                  "Stock_Monitor", "Rail_Post_1"])
def test_a_visual_part_is_not_mistaken_for_a_collider(name):
    assert not partnames.is_collision(name)
    assert partnames.is_mergeable(name)


def test_lod_alternates_are_never_merged():
    parts = _parts({"Desk_Top": "M_Skin_wood", "Desk_Leg": "M_Skin_wood"})
    parts += [("Desk_Top_LOD1", "M_Skin_wood", _SIG),
              ("Desk_Top_LOD2", "M_Skin_wood", _SIG)]
    groups = partnames.group_parts(parts)
    merged = {s for _n, _k, srcs in groups for s in srcs}
    assert merged == {"Desk_Top", "Desk_Leg"}


def test_stock_never_merges_into_its_host():
    """`portable_building.py` measures a module's extent with `Stock_*`
    excluded; folded into the host's group that filter cannot fire."""
    parts = _parts({"Desk_Top": "M_Skin_wood", "Desk_Leg": "M_Skin_wood",
                    "Stock_Monitor": "M_Skin_wood", "Stock_Mug": "M_Skin_wood"})
    groups = partnames.group_parts(parts)
    assert len(groups) == 2
    for name, _key, srcs in groups:
        starts = {s.startswith(partnames.STOCK_PREFIX) for s in srcs}
        assert len(starts) == 1, (name, srcs)
        if starts == {True}:
            assert name.startswith(partnames.STOCK_PREFIX), name


def test_a_family_keeps_its_prefix_so_patina_still_reads_it():
    """`patina/patina/surfaces.py` forces TRIM on a name carrying `rail`."""
    groups = partnames.group_parts(
        _parts({"Rail_Post_1": "M_Rail_metal", "Rail_Top_1": "M_Rail_metal"}))
    assert len(groups) == 1
    assert groups[0][0].lower().startswith("rail")


def test_parts_with_different_layers_do_not_share_a_mesh():
    """A part built `finish=False` carries no Wear colours; merged into one
    that has them it would be written with the layer's default, not white."""
    wear = (("UVMap",), (("Wear", "CORNER", "BYTE_COLOR"),))
    bare = (("UVMap",), ())
    groups = partnames.group_parts([
        ("Cig_Body", "M_Skin_metal", wear),
        ("Cig_Side", "M_Skin_metal", wear),
        ("Cig_Display", "M_Skin_metal", bare),
    ])
    assert len(groups) == 2
    by_size = sorted((len(s), sorted(s)) for _n, _k, s in groups)
    assert by_size[0] == (1, ["Cig_Display"])
    assert by_size[1] == (2, ["Cig_Body", "Cig_Side"])


def test_a_merged_part_is_never_named_like_a_collider():
    taken = set()
    name = partnames.merged_name("Wall", "M_Skin-col", taken)
    assert not partnames.is_collision(name), name


def test_names_are_unique_within_a_module():
    # Two families whose slugs collide must still get distinct names.
    groups = partnames.group_parts([
        ("Wall_A", "M_Skin_brick", _SIG),
        ("Wall_B", "M_Skin_brick", _SIG),
        ("Wall_Wall_brick", "M_Skin_brick", (("UVMap",), ())),
    ])
    names = [n for n, _k, _s in groups]
    assert len(names) == len(set(names)), names


def test_the_plan_is_sorted_not_hash_ordered():
    """Same spec, same bytes: shuffling the input must not move the output."""
    import random
    parts = _parts(_PACK_WALL_MATS)
    first = partnames.group_parts(parts)
    for seed in range(8):
        shuffled = list(parts)
        random.Random(seed).shuffle(shuffled)
        assert partnames.group_parts(shuffled) == first


def test_the_collision_suffixes_have_one_definition():
    """Two spellings of one contract drift. `bpylayer.export` reads the same
    tuple `bpylayer.merge` asks its question of."""
    pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import export
    assert export._COL_SUFFIXES is partnames.COL_SUFFIXES


def test_material_slug_strips_zoo_s_own_prefixes():
    assert partnames.material_slug("M_Skin_slatwall_delco_1997") \
        == "slatwall_delco_1997"
    assert partnames.material_slug("M_Rail_metal") == "Rail_metal"
    assert partnames.material_slug(None) == "unmatted"
    assert partnames.material_slug("") == "unmatted"


# --- the built article ------------------------------------------------------

def _pack_wall_module():
    return {"building_id": "t", "slots": [{
        "slot_id": "s0", "role": "prop", "size_mod": "full", "style": 13,
        "species": "pack_wall",
        "fit": {"dims": [2.4, 0.5, 2.55], "pivot": "center",
                "collision": True}}]}


def _build(merge_parts):
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import kit
    plan = kit.plan_kit(_pack_wall_module(), theme="delco", style=13)
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        return build.build_module(
            plan["modules"][0], d, theme="delco", style=13,
            options={"save_blend": False, "merge_parts": merge_parts})


def test_merging_does_not_change_the_facts_a_module_reports():
    """`gather_facts` runs BEFORE the merge and measures the parts a recipe
    built -- its `fit_names` and `dressing` filters match literal part names,
    so a merge that ran first would silently widen every module's measured
    dimensions."""
    pytest.importorskip("bpy")
    a = _build(False)["facts"]
    b = _build(True)["facts"]
    assert a["tris"] == b["tris"]
    assert a["parts"] == b["parts"]
    assert a["materials"] == b["materials"]
    assert a["dimensions"] == b["dimensions"]
    assert a["center"] == b["center"]
    assert a["has_collision"] == b["has_collision"] is True


def test_a_collider_reaches_the_export_set_under_its_own_name():
    """Counts are not enough: Godot's importer reads the NAME, so a collider
    that survived as an object but lost its suffix would import as a visual
    and the module would stop being solid. Measured on the built article
    rather than on a descriptor list."""
    pytest.importorskip("bpy")
    import bpy

    from zoo_keeper.bpylayer import merge
    from zoo_keeper.bpylayer import build as build_mod
    from zoo_keeper.core import kit, partnames

    plan = kit.plan_kit(_pack_wall_module(), theme="delco", style=13)
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        build_mod.build_module(plan["modules"][0], d, theme="delco", style=13,
                               options={"save_blend": False,
                                        "merge_parts": False})
        coll = [c for c in bpy.data.collections
                if c.objects and any(o.type == "MESH" for o in c.objects)][-1]
        col_before = sorted(o.name for o in coll.objects
                            if partnames.is_collision(o.name))
        assert col_before, "the fixture must carry a collider to prove this"
        packed = merge.pack_by_material(coll)
        assert packed is not None
        col_after = sorted(o.name for o in packed.objects
                           if partnames.is_collision(o.name))
        assert col_after == col_before
        # And nothing merged acquired a collision suffix on the way.
        merged = [o.name for o in packed.objects if o.name not in
                  {x.name for x in coll.objects}]
        assert merged
        assert not [n for n in merged if partnames.is_collision(n)]
        packed.discard()


def test_every_non_mesh_rides_out_untouched():
    """`LuxEmit_*` and `ATT_*` are EMPTIES that `lux_fixture_spawner.gd` and
    the attach points read, and their glTF `extras` with them. They are not
    in the mesh pool, so the export set must carry them through unchanged
    rather than merely not break them."""
    pytest.importorskip("bpy")
    import bpy

    from zoo_keeper.bpylayer import merge
    from zoo_keeper.bpylayer import build as build_mod
    from zoo_keeper.core import kit

    plan = kit.plan_kit(_pack_wall_module(), theme="delco", style=13)
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        build_mod.build_module(plan["modules"][0], d, theme="delco", style=13,
                               options={"save_blend": False,
                                        "merge_parts": False})
        coll = [c for c in bpy.data.collections
                if c.objects and any(o.type == "MESH" for o in c.objects)][-1]
        marker = bpy.data.objects.new("ATT_probe", None)
        marker["zoo_test"] = "kept"
        coll.objects.link(marker)
        try:
            packed = merge.pack_by_material(coll)
            assert packed is not None
            out = [o for o in packed.objects if o.name == "ATT_probe"]
            assert len(out) == 1, [o.name for o in packed.objects]
            assert out[0] is marker
            assert out[0]["zoo_test"] == "kept"
            packed.discard()
        finally:
            bpy.data.objects.remove(marker, do_unlink=True)


def test_the_merged_set_is_one_object_per_material_group():
    """The whole point, asserted on geometry rather than on a plan: the pack
    wall ships 117 visual parts over 4 materials."""
    pytest.importorskip("bpy")
    import bpy

    from zoo_keeper.bpylayer import merge
    from zoo_keeper.bpylayer import build as build_mod
    from zoo_keeper.core import kit, partnames

    plan = kit.plan_kit(_pack_wall_module(), theme="delco", style=13)
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        build_mod.build_module(plan["modules"][0], d, theme="delco", style=13,
                               options={"save_blend": False,
                                        "merge_parts": False})
        coll = [c for c in bpy.data.collections
                if c.objects and any(o.type == "MESH" for o in c.objects)][-1]
        visual = [o for o in coll.objects if o.type == "MESH"
                  and partnames.is_mergeable(o.name)]
        packed = merge.pack_by_material(coll)
        assert packed is not None
        made = [o for o in packed.objects
                if o.name not in {x.name for x in coll.objects}]
        # Fewer meshes out than parts in, or this bought nothing.
        assert len(made) == packed.stats["merged"]
        assert packed.stats["meshes_out"] == (packed.stats["merged"]
                                              + packed.stats["passed_through"])
        assert packed.stats["meshes_out"] < len(visual)
        assert packed.stats["parts_in"] == len(visual)
        # Each merged object carries exactly one material, which is what
        # makes it one draw call.
        for o in made:
            assert len(o.data.materials) <= 1, (o.name, len(o.data.materials))
            assert len({p.material_index for p in o.data.polygons}) == 1
        packed.discard()


def test_a_group_of_one_keeps_its_own_object_and_name():
    """Re-packing a lone part removes no draw call and costs it the name
    three consumers read it by. `wall_pack` is the case that found this:
    it names a part `WallPack_Lens` and paints it `M_WallPack_Lens`, so the
    merged name was the part's own name, Blender appended `.001`, and the
    build refused."""
    pytest.importorskip("bpy")
    import bpy

    from zoo_keeper.bpylayer import merge
    from zoo_keeper.bpylayer import build as build_mod
    from zoo_keeper.core import genome

    if "wall_pack" not in genome.list_species():
        pytest.skip("wall_pack not in the library")
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        build_mod.build_specimen("", d, species="wall_pack",
                                 options={"save_blend": False,
                                          "clear_scene": True,
                                          "merge_parts": False})
        coll = [c for c in bpy.data.collections
                if c.objects and any(o.type == "MESH" for o in c.objects)][-1]
        before = {o.name for o in coll.objects}
        assert "WallPack_Lens" in before, sorted(before)
        packed = merge.pack_by_material(coll)
        assert packed is not None
        out = {o.name for o in packed.objects}
        # The lone lens keeps its name exactly -- no `.001`, no `_2`.
        assert "WallPack_Lens" in out, sorted(out)
        assert not [n for n in out if n.endswith((".001", ".002"))], sorted(out)
        assert packed.stats["passed_through"] >= 1
        packed.discard()


def test_a_merged_name_avoids_names_already_spoken_for():
    """The pure half of the same rule: given a part already called
    `WallPack_Lens`, the planner must not hand a group that name."""
    sig = (("UVMap",), ())
    groups = partnames.group_parts(
        [("WallPack_Lens", "M_WallPack_Lens", sig),
         ("WallPack_Lens2", "M_WallPack_Lens", sig)],
        taken={"WallPack_Lens", "WallPack_Lens2"})
    assert len(groups) == 1
    assert groups[0][0] not in ("WallPack_Lens", "WallPack_Lens2")
    assert groups[0][0].startswith("WallPack")


def test_the_merge_leaves_the_scene_it_was_given():
    """Non-destructive: `save_blend` runs after `export_glb` and must still
    write the parts, and every recipe test asserting on object names must
    still see them."""
    pytest.importorskip("bpy")
    import bpy

    from zoo_keeper.bpylayer import export, merge
    from zoo_keeper.core import kit
    from zoo_keeper.bpylayer import build as build_mod

    plan = kit.plan_kit(_pack_wall_module(), theme="delco", style=13)
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        build_mod.build_module(plan["modules"][0], d, theme="delco", style=13,
                               options={"save_blend": False,
                                        "merge_parts": False})
        coll = [c for c in bpy.data.collections
                if c.objects and any(o.type == "MESH" for o in c.objects)][-1]
        before = sorted(o.name for o in coll.objects)
        packed = merge.pack_by_material(coll)
        assert packed is not None
        assert len(packed.objects) < len(before)
        packed.discard()
        assert sorted(o.name for o in coll.objects) == before
        assert export.gather_facts(coll, "PackWall")["parts"]
