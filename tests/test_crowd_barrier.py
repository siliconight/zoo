"""crowd_barrier (1.118.0): a steel crowd-control barricade, one interlocking panel on its flat feet.

Factory roadmap 267, the walker's look review of 2026-10-20: arena_a02's four barriers -- 3.0 x 0.8 x 1.2 m boxes --
are to be "Crowd rails (a new model)". `core.crowd_barrier_forms` is the plan, drawn from a slot's box alone; the
recipe builds the same lists through `bpylayer.prim_mesh`. Pure: nothing here needs Blender. Every test here fails on
1.117.0, which has no such species.
"""
import itertools
import math

import pytest

from zoo_keeper.core import crowd_barrier_forms as F
from zoo_keeper.core import genome, kit, prims

IN = 0.0254
#: arena_a02's barrier volumes, as Deli Counter writes them (long side first, `prop_species.long_axis_first`)
ARENA = (3.0, 0.8, 1.2)
SIZES = list(itertools.product((1.8, 2.0, 2.286, 2.5, 3.0, 3.2), (0.45, 0.61, 0.8, 0.9), (0.95, 1.092, 1.2, 1.25)))


def test_crowd_barrier_is_discovered_and_validates():
    assert "crowd_barrier" in genome.list_species()
    g = genome.load_species("crowd_barrier")
    assert genome.validate_genome(g) == []
    assert g["collision"] is True
    assert g["parts"] == [F.PART]
    assert g["materials"] == {"default": "metal_bare", "options": ["metal_bare"]}


def _arena_plan(material):
    return kit.plan_kit({"building_id": "arena_a02", "slots": [{
        "slot_id": "barrier_0", "role": "prop", "size_mod": "full", "style": 4, "material": material,
        "species": "crowd_barrier", "kit_axis": "material",
        "transform": {"translation": [-15.0, -6.0, 0.6], "rot_y": 0.0, "scale": [1.0, 1.0, 1.0]},
        "fit": {"dims": list(ARENA), "pivot": "center", "openings": [], "collision": "convex"}}]},
        theme="delco_1997", style=1)


def test_arena_a02s_barrier_plans_as_the_species():
    """arena_a02's slot as Deli Counter 0.242.0 writes it -- in the species' own kind, `metal_bare` -- plans as the
    species at the theme the levels build in, with no fallback and no `_m` in its stem: the galvanised grey is the
    genome's. The kit KEEPS a slot's known kind that the genome does not offer, as `dna.resolve_module_plan` says, so
    the spec's old `metal` would have planned the `_mmetal` module, in the theme's metal pack: why Deli Counter
    writes the species' own kind (its `level_design._PROP_MATERIALS`, the dartboard's rule)."""
    plan = _arena_plan("metal_bare")
    assert plan["species_fallbacks"] == []
    (m,) = plan["modules"]
    assert m["species"] == "crowd_barrier"
    assert m["stem"] == "prop_crowd_barrier_delco_1997_04_w300_d80_h120", m["stem"]
    assert _arena_plan("metal")["modules"][0]["stem"].endswith("_mmetal")


def test_the_defaults_are_the_reference_panel():
    g = genome.load_species("crowd_barrier")["dimensions"]
    # 7.5 ft long, 43 in tall, on 24 in feet
    assert math.isclose(g["width"]["default"], 90 * IN, abs_tol=1e-3)
    assert math.isclose(g["height"]["default"], 43 * IN, abs_tol=1e-3)
    assert math.isclose(g["depth"]["default"], 24 * IN, abs_tol=1e-3)
    # 1-1/2 in legs, 1-1/4 in rails, 3/4 in pickets; fourteen pickets to the 7.5 ft panel
    assert (round(2 * F.LEG_R / IN, 3), round(2 * F.RAIL_R / IN, 3), round(2 * F.PICKET_R / IN, 3)) == (1.5, 1.25, 0.75)
    assert F.plan(g["width"]["default"], g["depth"]["default"], g["height"]["default"])["facts"]["pickets"] == 14
    # and the genome's ranges hold arena_a02's slot
    for v, k in zip(ARENA, ("width", "depth", "height")):
        assert g[k]["min"] <= v <= g[k]["max"], (k, v)


@pytest.mark.parametrize("w,d,h", SIZES)
def test_the_extents_are_exactly_the_slots(w, d, h):
    lo, hi = prims.bounds(F.plan(w, d, h)["prims"])
    for a, (want_lo, want_hi) in enumerate(((-w / 2, w / 2), (-d / 2, d / 2), (-h / 2, h / 2))):
        assert math.isclose(lo[a], want_lo, abs_tol=1e-9) and math.isclose(hi[a], want_hi, abs_tol=1e-9)


@pytest.mark.parametrize("w,d,h", SIZES)
def test_no_face_lies_on_another(w, d, h):
    assert prims.coincident_pairs(F.plan(w, d, h)["prims"]) == []


def test_the_coincidence_check_can_see_a_pair():
    """The control: a picket laid with its facet on a leg's, unturned, is a pair the probe reports."""
    a = prims.cyl(F.PART, F.MAT, (0.0, 0.0), F.LEG_R, 0.0, 1.0, segments=F.SIDES)
    b = prims.box(F.PART, F.MAT, (F.LEG_R * F.FLAT, -0.004, 0.2), (F.LEG_R * F.FLAT + 0.01, 0.004, 0.8))
    b = prims.rotate_z(b, math.pi / F.SIDES, about=(0.0, 0.0))
    assert prims.coincident_pairs([a, b])


def _boundary_loops(p):
    """The open ends of a primitive: its edges used by one face, chained into loops."""
    count = {}
    for f in p["faces"]:
        for a, b in zip(f, f[1:] + f[:1]):
            k = (min(a, b), max(a, b))
            count[k] = count.get(k, 0) + 1
    nxt = {}
    for (a, b), n in count.items():
        if n == 1:
            nxt.setdefault(a, []).append(b)
            nxt.setdefault(b, []).append(a)
    loops, seen = [], set()
    for start in nxt:
        if start in seen:
            continue
        loop, prev, cur = [start], None, start
        seen.add(start)
        while True:
            cand = [v for v in nxt[cur] if v != prev]
            if not cand or cand[0] == start:
                break
            prev, cur = cur, cand[0]
            if cur in seen:
                break
            seen.add(cur)
            loop.append(cur)
        loops.append(loop)
    return loops


def _half_spaces(p):
    """``p`` as a convex solid: each face's plane and each open end's, every normal away from its centroid."""
    vs = p["verts"]
    c = [sum(v[a] for v in vs) / len(vs) for a in range(3)]
    out = []
    for loop in [list(f) for f in p["faces"]] + _boundary_loops(p):
        pts = [vs[i] for i in loop]
        n = [0.0, 0.0, 0.0]
        for (x0, y0, z0), (x1, y1, z1) in zip(pts, pts[1:] + pts[:1]):
            n[0] += (y0 - y1) * (z0 + z1)
            n[1] += (z0 - z1) * (x0 + x1)
            n[2] += (x0 - x1) * (y0 + y1)
        ln = math.sqrt(sum(x * x for x in n))
        n = [x / ln for x in n]
        dd = sum(n[a] * pts[0][a] for a in range(3))
        if sum(n[a] * c[a] for a in range(3)) > dd:
            n, dd = [-x for x in n], -dd
        out.append((n, dd))
    return out


@pytest.mark.parametrize("w,d,h", [ARENA, (2.286, 0.61, 1.092), (1.8, 0.45, 0.95), (3.2, 0.9, 1.25)])
def test_no_open_end_shows(w, d, h):
    """Every tube end left open lies strictly inside another member: a leg's foot in its plate, a rail's ends in the
    legs, a picket's on the rails' centre lines, a hook's arm in its leg and its drop."""
    ps = F.plan(w, d, h)["prims"]
    solids = [_half_spaces(p) for p in ps]
    opened = 0
    for i, p in enumerate(ps):
        for loop in _boundary_loops(p):
            opened += 1
            for vi in loop:
                v = p["verts"][vi]
                assert any(all(sum(n[a] * v[a] for a in range(3)) - dd < -1e-7 for n, dd in solids[j])
                           for j in range(len(ps)) if j != i), (i, v)
    # two legs, two rails (both ends), each picket (both ends), two arms (both ends)
    assert opened == 2 + 4 + 2 * F.plan(w, d, h)["facts"]["pickets"] + 4


def test_the_feet_stand_proud_of_a_floor_skin():
    """1.118.1: Deli Counter lays a room's floor finish as a 2 cm skin over the slab and stands a prop on the slab under
    it (its `floors.SKIN_THICK`), so a foot under 2 cm is buried -- the factory's cold run 9359 framed 1.118.0's 9.5 mm
    feet out of sight, the legs planted in the carpet. A foot's top clears that skin by a centimetre or more, at every
    size. FAILS ON 1.118.0."""
    skin = 0.02
    assert F.FOOT_T - skin >= 0.01
    for w, d, h in SIZES:
        feet = [p for p in F.plan(w, d, h)["prims"] if len(p["faces"]) == 6]
        assert len(feet) == 2
        assert all(max(v[2] for v in p["verts"]) - (-h / 2) >= skin + 0.01 for p in feet)


def test_an_open_end_is_narrower_than_what_hides_it():
    assert F.RAIL_R < F.LEG_R * F.FLAT and F.PICKET_R < F.RAIL_R * F.FLAT and F.ARM_R < F.HOOK_R * F.FLAT
    assert F.LEG_R < F.FOOT_W / 2 and 0 < F.SINK < F.FOOT_T


@pytest.mark.parametrize("w,d,h", SIZES)
def test_every_clear_gap_between_pickets_is_equal_and_inside_the_clear(w, d, h):
    x_lo, x_hi, _x_drop = F.frame_x(w)
    x0, x1 = x_lo + F.LEG_R, x_hi - F.LEG_R
    xs = F.picket_xs(x0, x1)
    edges = [x0] + [e for xc in xs for e in (xc - F.PICKET_R, xc + F.PICKET_R)] + [x1]
    gaps = [b - a for a, b in zip(edges[::2], edges[1::2])]
    assert max(gaps) <= F.PICKET_CLEAR + 1e-9 and min(gaps) > 0.0
    assert max(gaps) - min(gaps) < 1e-9


def test_the_hooks_would_drop_over_the_next_panels_leg():
    x_lo, x_hi, x_drop = F.frame_x(ARENA[0])
    assert F.HOOK_CLEAR > 2 * F.LEG_R
    # their opening, the +X leg's face to the drop's inner face, is HOOK_CLEAR
    assert math.isclose((x_drop - F.HOOK_R) - (x_hi + F.LEG_R), F.HOOK_CLEAR, abs_tol=1e-9)
    assert x_drop > x_hi > x_lo


def test_one_material_one_part_one_submission_inside_the_budget():
    budget = genome.load_species("crowd_barrier")["budgets"]["tris_lod0"]
    worst = 0
    for w, d, h in SIZES:
        got = F.plan(w, d, h)
        assert {p["mat"] for p in got["prims"]} == {F.MAT}
        assert {p["part"] for p in got["prims"]} == {F.PART}
        worst = max(worst, got["facts"]["tris"])
    assert worst <= budget, (worst, budget)


@pytest.mark.parametrize("w,d,h", [ARENA, (1.8, 0.45, 0.95), (3.2, 0.9, 1.25)])
def test_the_collision_is_the_panel(w, d, h):
    (lo, hi), = F.plan(w, d, h)["collision"]
    assert math.isclose(lo[2], -h / 2) and math.isclose(hi[2], h / 2)
    assert math.isclose(hi[1] - lo[1], 2 * F.LEG_R, abs_tol=1e-9)
    assert -w / 2 <= lo[0] < hi[0] <= w / 2


def test_a_box_too_small_for_the_frame_is_refused():
    with pytest.raises(ValueError):
        F.plan(0.12, 0.6, 1.1)
    with pytest.raises(ValueError):
        F.plan(2.3, 0.6, 0.3)
    with pytest.raises(ValueError):
        F.plan(2.3, 0.02, 1.1)
