"""The hero vault door: a round door per state of Deli Counter's machine.

Pure tests first -- the portal, the passage the collision leaves, the swung
leaf, the lathe meshes, the slot-to-module planning -- then Blender tests at
the bottom (skipped without bpy) that build all four states at two wall
depths and hold them to the exact fit, the budget and zero coincident faces.

Earlier versions of this file tested the closed-only box door (a rectangular
leaf and hub in a jamb portal, with open reusing `doorway` and breached
`breach`). That species is replaced; see CHANGELOG 0.83.0.
"""
import math
import os
import sys

import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, kit, validate
from zoo_keeper.core import vault_forms as vf

APERTURE = {"kind": "vault", "width": 1.3, "height": 2.1, "sill": 0.0}
SLOT_DIMS = [3.6, 0.6, 3.3]
ALL_VAULT = {"locked": "vault_door", "unlocked": "vault_door",
             "open": "vault_door", "breached": "vault_door"}
#: Deli Counter's machine as shipped (interactives.py, read 2026-09-13).
DC_TODAY = {"locked": "vault_door", "unlocked": "vault_door",
            "open": "doorway", "breached": "breach"}


def _slot(dims=SLOT_DIMS, sg=ALL_VAULT, opening=APERTURE, sid="v0"):
    return {"slot_id": sid, "role": "vault_door", "size_mod": "full",
            "style": 1, "material": "concrete",
            "fit": {"dims": list(dims), "pivot": "center",
                    "openings": [dict(opening)] if opening else []},
            "interactive": {"id": "b:if:v", "kind": "vault_door",
                            "states": ["locked", "unlocked", "open",
                                       "breached"],
                            "default": "locked", "state_geometry": dict(sg)}}


def _v(dims=SLOT_DIMS, opening=APERTURE):
    return vf.plan_vault(*dims, opening=opening)


def _rect(v):
    """The authored aperture as an AABB through the whole slot depth."""
    op = v["opening"]
    return ((-op["width"] / 2.0, -v["d"] / 2.0, v["z_cut"]),
            (op["width"] / 2.0, v["d"] / 2.0, v["z_cut"] + op["height"]))


# --------------------------------------------------------------- the portal

def test_the_portal_circle_passes_through_the_apertures_corners():
    v = _v()
    op = v["opening"]
    for sx in (-1, 1):
        for zz in (v["z_cut"], v["z_cut"] + op["height"]):
            d = math.hypot(sx * op["width"] / 2.0, zz - v["zc"])
            assert abs(d - v["r"]) < 1e-9
    # at the flat cut the chord is exactly the authored width
    assert abs(2.0 * v["half_clear"] - op["width"]) < 1e-9


def test_required_size_is_what_a_slot_needs_to_build_unshrunk():
    need = vf.required_size(1.3, 2.1, 0.0)
    ok = vf.plan_vault(need["width"], 0.6, 3.3, APERTURE)
    assert ok["shortfall"] == 0.0
    tight = vf.plan_vault(need["width"] - 0.2, 0.6, 3.3, APERTURE)
    assert tight["shortfall"] > 0.09 and tight["r"] < tight["r_want"]


def test_deli_counters_current_vault_slot_is_reported_undersized_not_crashed():
    # DC today sizes a vault slot as wide as its opening: 1.4 m.
    v = vf.plan_vault(1.4, 0.3, 3.3, {"width": 1.4, "height": 2.3,
                                      "sill": 0.15})
    assert v["shortfall"] > 1.0
    assert v["r"] > 0.0
    assert vf.required_size(1.4, 2.3, 0.15)["width"] > 3.5


def test_an_undersized_slot_is_built_whole_and_scaled_with_real_gaps():
    # DC's current vault slot: as wide as its 1.4 m opening
    op = {"width": 1.4, "height": 2.3, "sill": 0.15}
    s = vf.fit_scale(1.4, 0.3, 3.3, op)
    assert 0.3 < s < 0.4
    big = vf.plan_vault(1.4 / s, 0.3, 3.3 / s, op, unit=1.0 / s)
    assert big["shortfall"] <= 0.005
    # the gaps that keep faces apart come back out of the scale at real size
    assert abs(big["cut"]["frame"] * s - vf.CUT_FRAME) < 1e-12
    assert abs(big["cut"]["th_top"] * s - vf.THRESHOLD_TOP) < 1e-12
    assert vf.fit_scale(3.6, 0.6, 3.3, APERTURE) == 1.0


def test_depth_allocation_is_ordered_and_the_hinge_fits_the_wall():
    for t in (0.2, 0.3, 0.45, 0.6, 1.2):
        v = vf.plan_vault(3.6, t, 3.3, APERTURE)
        y = v["y"]
        chain = [y["back"], y["body_back"], y["y_leaf_back"], y["y_pan"],
                 y["y_outer"], y["y_door"], y["y_mid"], y["y_inner"], y["f"]]
        assert chain == sorted(chain), (t, chain)
        hg = v["hinge"]
        ring = vf.KNUCKLE * hg["r"]
        assert hg["y"] + ring <= t / 2.0 + 1e-9, t
        assert hg["y"] - ring >= -t / 2.0 - 1e-9, t


# ---------------------------------------------------- the passage it leaves

def test_the_passage_bands_hold_the_authored_rectangle():
    for dims, op in ((SLOT_DIMS, APERTURE),
                     ([4.2, 0.6, 3.6], {"width": 1.6, "height": 2.3,
                                        "sill": 0.1})):
        v = vf.plan_vault(*dims, opening=op)
        assert v["shortfall"] == 0.0
        bands = vf.passage_bands(v)
        assert abs(bands[0][2] - v["z_cut"]) < 1e-9
        assert bands[-1][3] >= v["z_cut"] + v["opening"]["height"] - 1e-9
        for x0, x1, za, zb in bands:
            if za < v["z_cut"] + v["opening"]["height"] - 1e-9:
                assert x1 >= v["opening"]["width"] / 2.0 - 1e-9
            for zz in (za, zb):          # every corner inside the circle
                assert math.hypot(x1, zz - v["zc"]) <= v["r"] + 1e-9


def test_open_frame_collision_never_enters_the_aperture_and_stays_in_slot():
    for state in ("open", "breached"):
        v = _v()
        rect = _rect(v)
        for lo, hi in vf.frame_collision(v):
            assert not vf.boxes_overlap((lo, hi), rect), (state, lo, hi)
            for i, half in enumerate((v["hw"], v["d"] / 2.0, v["hh"])):
                assert -half - 1e-9 <= lo[i] and hi[i] <= half + 1e-9


def test_a_closed_door_is_the_whole_slot():
    v = _v()
    for st in vf.CLOSED_STATES:
        assert vf.state_collision(v, st) == [
            ((-1.8, -0.3, -1.65), (1.8, 0.3, 1.65))]


def test_the_swung_leaf_stays_out_of_the_approach_and_off_the_floor():
    for dims in (SLOT_DIMS, [3.6, 0.3, 3.3]):
        v = _v(dims)
        op = v["opening"]
        approach = ((-op["width"] / 2.0, -v["d"] / 2.0, v["z_cut"]),
                    (op["width"] / 2.0, v["d"] / 2.0 + 3.0,
                     v["z_cut"] + op["height"]))
        for state in ("open", "breached"):
            boxes = vf.leaf_collision(v, state)
            assert len(boxes) == 4
            for b in boxes:
                assert not vf.boxes_overlap(b, approach), (dims, state, b)
                assert b[0][2] >= v["z_cut"] - 1e-6, (dims, state, b)


def test_the_open_leaf_swings_out_toward_the_approach_on_the_hinge_side():
    v = _v()
    m = vf.leaf_matrix(v, "open")
    # the leaf's far edge (-x, the lock side) ends up in front of the wall
    far = vf.mat_apply(m, (-v["rd"], v["y"]["y_door"], v["zc"]))
    assert far[1] > v["d"] / 2.0 + 1.5
    assert far[0] > 0.0                      # on the hinge (+x) side
    assert vf.leaf_matrix(v, "locked") == vf.mat_identity()


def test_bolt_ports_keep_out_of_the_passage():
    v = _v()
    y_bolt = v["y"]["y_leaf_back"] + 0.75 * (v["y"]["y_door"]
                                             - v["y"]["y_leaf_back"])
    ports = vf.port_angles(v, y_bolt)
    assert len(ports) >= 8
    rr = vf.lining_radius_at(v, y_bolt) - 0.006
    for t in ports:
        px, pz = rr * math.cos(t), v["zc"] + rr * math.sin(t)
        disc = ((px - 0.042, -1.0, pz - 0.042), (px + 0.042, 1.0, pz + 0.042))
        for x0, x1, za, zb in vf.passage_bands(v):
            assert not vf.boxes_overlap(disc, ((x0, -1.0, za), (x1, 1.0, zb)))


# ---------------------------------------------------------------- the mesh

def _edge_check(verts, faces):
    directed = {}
    for f in faces:
        assert len(set(f)) == len(f), "degenerate face %r" % (f,)
        for i in range(len(f)):
            e = (f[i], f[(i + 1) % len(f)])
            directed[e] = directed.get(e, 0) + 1
    assert all(n == 1 for n in directed.values()), "edge used twice one way"
    assert all((b, a) in directed for a, b in directed), "open edge"


def test_the_lathes_are_closed_and_consistently_wound():
    for t in (0.3, 0.6, 1.0):
        v = vf.plan_vault(3.6, t, 3.3, APERTURE)
        _edge_check(*vf.cut_lathe(vf.frame_profile(v), v["zc"],
                                  v["z_cut"] + vf.CUT_FRAME, 40))
        _edge_check(*vf.cut_lathe(vf.leaf_profile(v), v["zc"],
                                  v["z_cut"] + vf.CUT_LEAF, 40, closed=False))
    # uncut: a ring and a solid disc
    _edge_check(*vf.cut_lathe([(0.2, 0.0), (0.3, 0.0), (0.3, 0.1),
                               (0.2, 0.1)], 0.0, -9.0, 16))
    _edge_check(*vf.cut_lathe([(0.0, 0.0), (0.3, 0.0), (0.3, 0.1),
                               (0.0, 0.1)], 0.0, -9.0, 16, closed=False))


def test_the_cut_lathe_has_a_flat_bottom_exactly_on_the_cut():
    v = _v()
    z_min = v["z_cut"] + vf.CUT_FRAME
    verts, _faces = vf.cut_lathe(vf.frame_profile(v), v["zc"], z_min, 40)
    assert min(p[2] for p in verts) == z_min


def test_a_profile_straddling_the_cut_is_refused():
    with pytest.raises(ValueError):
        vf.cut_lathe([(0.5, 0.0), (2.0, 0.0), (2.0, 0.1), (0.5, 0.1)],
                     0.0, -1.0, 16)


def test_the_surround_is_a_horseshoe_when_the_portal_meets_the_floor():
    outer, holes = vf.surround_outline(1.8, 1.65, -0.6, 1.3, -1.65)
    assert holes == [] and vf.polygon_area(outer) > 0
    outer, holes = vf.surround_outline(1.8, 1.65, -0.4, 1.3, -1.5)
    assert len(holes) == 1


# ------------------------------------------------ slot -> module planning

def test_all_four_states_plan_as_vault_door_modules():
    plan = kit.plan_kit({"building_id": "b", "slots": [_slot()]},
                        theme="delco_1997")
    by_state = {m["state"]: m for m in plan["modules"]}
    assert set(by_state) == {None, "unlocked", "open", "breached"}
    assert all(m["species"] == "vault_door" for m in plan["modules"])
    base = by_state[None]["stem"]
    assert base.startswith("vault_door_delco_1997_01_w360_o")
    for st in ("unlocked", "open", "breached"):
        assert by_state[st]["stem"] == base + "_" + st
    assert plan["deferred_variants"] == []
    assert plan["state_geometry_notes"] == []


def test_deli_counters_current_mapping_is_honoured_and_called_out():
    plan = kit.plan_kit({"building_id": "b",
                         "slots": [_slot(sg=DC_TODAY)]})
    by_state = {m["state"]: m["species"] for m in plan["modules"]}
    assert by_state == {None: "vault_door", "unlocked": "vault_door",
                        "open": "doorway", "breached": "breach"}
    notes = {(n["state"], n["mapped_to"]) for n in plan["state_geometry_notes"]}
    assert notes == {("open", "doorway"), ("breached", "breach")}


def test_a_species_without_state_art_still_defers_identical_states():
    assert kit.state_art_for("doorway") == frozenset()
    door = {"role": "doorway", "size_mod": "full",
            "fit": {"dims": [1.2, 0.3, 2.2], "pivot": "center"},
            "interactive": {"states": ["closed", "open"], "default": "closed",
                            "state_geometry": {"closed": "doorway",
                                               "open": "doorway"}}}
    plan = kit.plan_kit({"building_id": "b", "slots": [door]})
    assert [m["state"] for m in plan["modules"]] == [None]
    assert [d["state"] for d in plan["deferred_variants"]] == ["open"]


def test_the_module_plan_carries_the_aperture_state_and_exact_fit():
    plan = kit.plan_kit({"building_id": "b", "slots": [_slot()]},
                        theme="delco_1997")
    m = next(x for x in plan["modules"] if x["state"] == "open")
    g = genome.load_species("vault_door")
    bp = dna.resolve_module_plan(m, g, "delco_1997", 1, TOOL_VERSION)
    assert bp["pivot"] == "center" and bp["fit_exact"] is True
    assert bp["target_dims"] == {"width": 3.6, "depth": 0.6, "height": 3.3}
    assert bp["module"]["state"] == "open"
    assert bp["params"]["opening"]["width"] == 1.3
    # the concrete partition's kind lands on plan["material"]; the recipe
    # builds from the style's steel, which is what the genome says
    assert bp["style_block"]["material"] == "metal_painted"


#: The parts a person sees as plate: the surround, its straps and rivets, the
#: frame, the leaf and everything painted onto it.
PLATE_PARTS = ("Surround", "Straps", "Rivets", "Frame", "Threshold", "Hinges",
               "Keepers", "Leaf", "FaceRing", "Bars", "Boss", "BoltPorts",
               "TornPlate", "Char", "Shards")


def test_the_door_is_painted_steel_and_only_its_hardware_is_bare():
    """0.83.0 skinned every part `metal_bare`, and in Godot the surround and
    the leaf wore that pack's glossy roughness bars as long black streaks
    (vault_forms, above HARDWARE_KIND). The references are painted plate."""
    g = genome.load_species("vault_door")
    assert g["materials"]["default"] == "metal_painted"
    for name, style in g["styles"].items():
        assert style["material"] == "metal_painted", name
    assert vf.HARDWARE_KIND == "metal_bare"
    assert set(vf.HARDWARE_PARTS) == {"BoltHeads", "LeafBolts", "Hardware",
                                      "BossBolts", "Bolts", "Wheel"}
    assert not set(vf.HARDWARE_PARTS) & set(PLATE_PARTS)
    genome_parts = {p.split("_", 1)[1] for p in g["parts"]}
    assert genome_parts <= set(vf.HARDWARE_PARTS) | set(PLATE_PARTS)


def test_the_genome_and_the_forms_agree_on_every_default():
    g = genome.load_species("vault_door")
    assert set(g["state_art"]) == {"unlocked", "open", "breached"}
    for k, dv in vf.DEFAULTS.items():
        assert g["params"][k]["default"] == dv, k
    assert set(g["params"]) == set(vf.DEFAULTS)


def test_the_budget_is_a_hero_budget_and_says_so():
    g = genome.load_species("vault_door")
    budget = g["budgets"]["tris_lod0"]
    # one per bank; the heaviest room props (desk 8000) sit near it
    assert 8000 <= budget <= 10000


def test_a_validated_open_frame_passes_on_the_frame_not_the_leaf():
    """What `build_module` hands `validate` for a swung state: dims and centre
    from the fit objects, the leaf's reach as overhang only."""
    plan = kit.plan_kit({"building_id": "b", "slots": [_slot()]},
                        theme="delco_1997")
    m = next(x for x in plan["modules"] if x["state"] == "open")
    g = genome.load_species("vault_door")
    bp = dna.resolve_module_plan(m, g, "delco_1997", 1, TOOL_VERSION)
    facts = {"dimensions": {"width": 3.6, "depth": 0.6, "height": 3.3},
             "center": [0.0, 0.0, 0.0], "tris": 7400, "parts": ["a"],
             "has_uvs": True, "has_wear_colors": True, "materials": ["m"],
             "has_collision": True, "unapplied_transforms": [],
             "overhang": {"min": [-1.8, -0.3, -1.65],
                          "max": [2.9, 2.9, 1.65]}}
    report = validate.evaluate(facts, g, bp, {"collision": True})
    assert report["status"] == "pass", validate.summarize(report)


# ------------------------------------------------------ bpy: built states

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _coplanar_pairs():
    import bpy
    import mathutils
    sys.path.insert(0, os.path.join(_ZOO, "tools"))
    import coplanar_probe
    objs = coplanar_probe._visual_meshes(bpy, bpy.context.scene)
    rows, _n = coplanar_probe.probe(bpy, mathutils, objs, 0.002, 1e-6, 1e-3)
    return rows


def _bpy_states(depth):
    import tempfile
    from zoo_keeper.bpylayer import build
    budget = genome.load_species("vault_door")["budgets"]["tris_lod0"]
    out = tempfile.mkdtemp(prefix="vault_door_")
    plan = kit.plan_kit({"building_id": "b",
                         "slots": [_slot(dims=[3.6, depth, 3.3])]},
                        theme="delco_1997")
    seen = set()
    for m in plan["modules"]:
        res = build.build_module(m, out, theme="delco_1997",
                                 options={"save_blend": False})
        rep = res["report"]
        assert rep["status"] == "pass", validate.summarize(rep)
        dims = res["facts"]["dimensions"]
        assert abs(dims["width"] - 3.6) < 1e-3
        assert abs(dims["depth"] - depth) < 1e-3, dims
        assert abs(dims["height"] - 3.3) < 1e-3
        assert res["facts"]["tris"] <= budget, res["facts"]["tris"]
        rows = _coplanar_pairs()
        assert rows == [], (m["state"], depth, rows[:4])
        if m["state"] in ("open", "breached"):
            assert res["facts"]["overhang"]["max"][1] > depth / 2.0 + 1.0
        else:
            assert "overhang" not in res["facts"]
        seen.add(m["state"])
    assert seen == {None, "unlocked", "open", "breached"}


def test_bpy_every_state_fits_is_in_budget_and_has_no_coincident_faces():
    pytest.importorskip("bpy")
    _bpy_states(0.6)


def test_bpy_a_thin_partition_builds_the_same_contract():
    pytest.importorskip("bpy")
    _bpy_states(0.3)


def _build_state(state, depth=0.3, out=None):
    """Build one state of bank_branch_a02's vault slot; return the GLB bytes."""
    import tempfile
    from zoo_keeper.bpylayer import build
    out = out or tempfile.mkdtemp(prefix="vault_door_")
    plan = kit.plan_kit({"building_id": "b",
                         "slots": [_slot(dims=[3.6, depth, 3.3])]},
                        theme="delco_1997")
    m = next(x for x in plan["modules"] if x["state"] == state)
    build.build_module(m, out, theme="delco_1997",
                       options={"save_blend": False})
    with open(os.path.join(out, m["stem"] + ".glb"), "rb") as fh:
        return fh.read()


#: The widest single polygon of bare metal the door may carry, in metres
#: (its largest vertex-to-vertex span). The metal_bare pack is a 1 m tile of
#: horizontal roughness bars on a metallic 0.9 surface; a plate a metre across
#: shows them as streaks, a bolt or a spoke does not. Measured after the
#: change over all four states at 0.3 and 0.6 m: 0.440 (`VaultDoor_Hardware`,
#: the U pull's 0.44 m bar). Before it: 3.618, a `VaultDoor_Surround`
#: triangle, with the leaf at 2.445 and the straps at 3.583.
BARE_POLYGON_MAX = 0.5


def test_bpy_no_bare_metal_plate_wide_enough_to_streak():
    bpy = pytest.importorskip("bpy")
    import itertools
    worst = (0.0, None)
    for depth in (0.3, 0.6):
        for state in (None, "unlocked", "open", "breached"):
            _build_state(state, depth)
            for o in bpy.context.scene.objects:
                if (o.type != "MESH" or o.name.endswith("colonly")
                        or not o.data.materials):
                    continue
                mat = o.data.materials[0]
                bsdf = next(n for n in mat.node_tree.nodes
                            if n.type == "BSDF_PRINCIPLED")
                if bsdf.inputs["Metallic"].default_value <= 0.0:
                    continue
                part = o.name.split("_", 1)[1]
                assert part in vf.HARDWARE_PARTS, (state, depth, o.name,
                                                   mat.name)
                vs = o.data.vertices
                for p in o.data.polygons:
                    span = max((vs[a].co - vs[b].co).length for a, b in
                               itertools.combinations(p.vertices, 2))
                    if span > worst[0]:
                        worst = (span, (state, depth, o.name))
    assert worst[1] is not None, "no bare metal read: nothing was measured"
    assert worst[0] < BARE_POLYGON_MAX, worst


def test_bpy_every_state_is_the_same_file_every_build():
    """The breached door's `VaultDoor_Shards` came back in a different vertex
    order each build (so a different COLOR_0 and a different GLB): the shard
    fracture iterated a set of BMVerts, which hash by address
    (`geometry._in_storage_order`)."""
    pytest.importorskip("bpy")
    import hashlib
    for state in (None, "unlocked", "open", "breached"):
        digests = {hashlib.sha1(_build_state(state)).hexdigest()
                   for _ in range(3)}
        assert len(digests) == 1, (state, sorted(digests))


def test_bpy_the_other_species_on_the_shard_helpers_repeat_too():
    """The same two helpers build `glass_shard` (fracture), `rubble_frag`
    (fracture, then a draw per vertex) and `litter_scrap` (subdivide, then a
    draw per vertex). Before the fix the last two came back as different
    GEOMETRY from one build to the next, not only in another order."""
    bpy = pytest.importorskip("bpy")
    import tempfile
    from zoo_keeper.bpylayer import build

    out = tempfile.mkdtemp(prefix="shard_helpers_")

    def snapshot(sp):
        build.clear_scene()
        build.build_specimen("", out, seed=7, species=sp,
                             options={"save_blend": False})
        return {o.name: [tuple(round(c, 6) for c in v.co)
                         for v in o.data.vertices]
                for o in bpy.context.scene.objects if o.type == "MESH"}

    for sp in ("glass_shard", "rubble_frag", "litter_scrap"):
        first = snapshot(sp)
        assert first, sp
        for _ in range(2):
            assert snapshot(sp) == first, sp
