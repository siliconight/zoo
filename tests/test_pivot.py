"""A module's pivot is measured, not declared.

The kit index repeats the plan's `"pivot": "center"` per row, and Deli
Counter and Lot place a module's origin at its slot's centre. Cold run 9019's
site kit (2026-09-12): the minted placeholders and `simple_car` were built
base-up, z 0 .. h, under that claim -- a consumer placing them by it stood
them h/2 in the air. `gather_facts` now reports the bounds' centre and
`fit_pivot` fails a module whose centre is off the origin; `build_module`
re-centres what a recipe returns before either looks.
"""
from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, kit, validate


def _plan(species, dims):
    g = genome.load_species(species)
    p = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "s0", "role": "prop", "size_mod": "full", "style": 1,
        "species": species, "fit": {"dims": list(dims), "pivot": "center"}}]},
        theme="delco", style=1)
    return g, dna.resolve_module_plan(p["modules"][0], g, "delco", 1, TOOL_VERSION)


def _facts(plan, center):
    return {"dimensions": dict(plan["dimensions"]), "center": center, "tris": 12,
            "parts": ["BoxTruck_Body"], "has_uvs": True, "has_wear_colors": True,
            "materials": ["M_BoxTruck_metal_painted"], "has_collision": True,
            "unapplied_transforms": []}


def test_a_base_up_box_fails_fit_pivot_by_half_its_height():
    g, plan = _plan("box_truck", [2.4, 6.0, 2.8])
    report = validate.evaluate(_facts(plan, [0.0, 0.0, 1.4]), g, plan, {"collision": True})
    (c,) = [c for c in report["checks"] if c["id"] == "fit_pivot"]
    assert c["level"] == "fail" and "1.400m" in c["msg"]
    assert report["status"] != "pass"


def test_a_centred_box_passes():
    g, plan = _plan("box_truck", [2.4, 6.0, 2.8])
    report = validate.evaluate(_facts(plan, [0.0, 0.0, 0.0]), g, plan, {"collision": True})
    (c,) = [c for c in report["checks"] if c["id"] == "fit_pivot"]
    assert c["level"] == "pass"


def test_facts_without_a_centre_are_not_judged_on_it():
    """Older gatherers and the fit tests build facts without one."""
    g, plan = _plan("box_truck", [2.4, 6.0, 2.8])
    f = _facts(plan, None)
    del f["center"]
    report = validate.evaluate(f, g, plan, {"collision": True})
    assert not any(c["id"] == "fit_pivot" for c in report["checks"])


def test_the_recentre_moves_geometry_collision_and_attachments_together():
    """`core.pivot.recentre` without Blender: objects are stand-ins with
    `.data.vertices[i].co.x/y/z`, the same attributes a bpy Vector has."""
    from zoo_keeper.core import pivot

    class _Co:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class _V:
        def __init__(self, x, y, z):
            self.co = _Co(x, y, z)

    class _Mesh:
        def __init__(self, pts):
            self.vertices = [_V(*p) for p in pts]

    class _Obj:
        type = "MESH"

        def __init__(self, pts):
            self.data = _Mesh(pts)

    o = _Obj([(-1.2, -3.0, 0.0), (1.2, 3.0, 2.8)])
    res = {"objects": [o], "collision_boxes": [((-1.2, -3.0, 0.0), (1.2, 3.0, 2.8))],
           "attachments": {"ATT_top": (0.0, 0.0, 2.8)}}
    out = pivot.recentre(res, {"module": {"pivot": "center"}},
                         (-1.2, -3.0, 0.0), (1.2, 3.0, 2.8))
    assert out["recentred_by"] == [0.0, 0.0, 1.4]
    assert sorted(v.co.z for v in o.data.vertices) == [-1.4, 1.4]
    assert out["collision_boxes"] == [((-1.2, -3.0, -1.4), (1.2, 3.0, 1.4))]
    assert out["attachments"] == {"ATT_top": (0.0, 0.0, 1.4)}
    # already centred: untouched, no offset recorded
    out2 = pivot.recentre({"objects": [], "collision_boxes": [], "attachments": {}},
                          {"module": {"pivot": "center"}}, (-1, -1, -1), (1, 1, 1))
    assert "recentred_by" not in out2
