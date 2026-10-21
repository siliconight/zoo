"""stanchion_run (1.119.0): one straight run of retractable-belt queue stanchions, posts and belt.

Factory roadmap 267, the walker, 2026-10-20: "stanchion or stanchions are likley more common for banks and indoor
common areas", "metal barriers are for outdoor concerts or riot protection from police", "retractable belt stanchion",
and a photo of a queue lined with them. `core.stanchion_run_forms` is the plan, drawn from a slot's box alone; the
recipe builds the same lists through `bpylayer.prim_mesh`. Pure: nothing here needs Blender. Every test here fails on
1.118.1, which has no such species.
"""
import itertools
import math

import pytest

from zoo_keeper.core import genome, intent, kit, prims
from zoo_keeper.core import stanchion_run_forms as F

IN = 0.0254
#: lengths either side of each place a run takes another post (d 0.356: 2.642, 4.928, 7.214 ...), and the genome's ends
WIDTHS = (1.1, 1.5, 2.64, 2.65, 4.6, 4.92, 4.94, 9.0, 12.0)
SIZES = list(itertools.product(WIDTHS, (0.3, 0.356, 0.42), (0.9, 0.97, 1.05)))


def test_stanchion_run_is_discovered_and_validates():
    assert "stanchion_run" in genome.list_species()
    g = genome.load_species("stanchion_run")
    assert genome.validate_genome(g) == []
    assert g["collision"] is True
    assert g["parts"] == [F.PART]
    assert g["materials"] == {"default": "metal_painted", "options": ["metal_painted"]}


def test_its_keywords_are_its_own_and_move_no_other_species(monkeypatch):
    """A prompt resolves by keyword (`intent._find_species`), so a new genome whose words overlap an old one's would
    quietly change what that prompt makes -- `queue_stanchion`'s "belt barrier" and "queue stanchion" in particular.
    Every one of this genome's words resolves to it, and every other genome's word resolves as it did without it."""
    words = dict(intent._species_keywords())
    mine = words["stanchion_run"][0]
    assert mine and all(intent._find_species(k) == "stanchion_run" for k in mine)
    others = [k for sp, (keys, _p) in words.items() if sp != "stanchion_run" for k in keys]
    with_it = [intent._find_species(k) for k in others]
    without = {sp: v for sp, v in words.items() if sp != "stanchion_run"}
    monkeypatch.setattr(intent, "_species_keywords", lambda: without)
    assert [intent._find_species(k) for k in others] == with_it
    # the probe can see a move: a word that extends an old one takes that one's plural
    assert intent._find_species("queue stanchions") == "queue_stanchion"
    monkeypatch.setattr(intent, "_species_keywords", lambda: dict(without, x=(["queue stanchions"], 0)))
    assert intent._find_species("queue stanchions") == "x"


def _plan_slot(material, dims=(4.6, 0.356, 0.97)):
    return kit.plan_kit({"building_id": "arena_a02", "slots": [{
        "slot_id": "queue_run_0", "role": "prop", "size_mod": "full", "style": 10, "material": material,
        "species": "stanchion_run", "kit_axis": "material",
        "transform": {"translation": [0.0, 0.0, dims[2] / 2], "rot_y": 0.0, "scale": [1.0, 1.0, 1.0]},
        "fit": {"dims": list(dims), "pivot": "center", "openings": [], "collision": "convex"}}]},
        theme="delco_1997", style=1)


def test_a_slot_in_its_own_kind_plans_as_the_species():
    """A run as Deli Counter writes one -- in the species' own kind, `metal_painted`, the dartboard's rule -- plans as
    the species at the theme the levels build in, with no fallback and no `_m` in its stem."""
    plan = _plan_slot("metal_painted")
    assert plan["species_fallbacks"] == []
    (m,) = plan["modules"]
    assert m["species"] == "stanchion_run"
    assert m["stem"] == "prop_stanchion_run_delco_1997_10_w460_d36_h97", m["stem"]


def test_the_defaults_are_the_reference_stanchion():
    g = genome.load_species("stanchion_run")["dimensions"]
    # a 38 in post on a 14 in base; the default run is two belts' reach
    assert math.isclose(g["height"]["default"], 38 * IN, abs_tol=0.01)
    assert math.isclose(g["depth"]["default"], 14 * IN, abs_tol=1e-3)
    # a 2-1/2 in post, a 2 in belt, 7-1/2 ft of it, the base 2 in high
    assert (round(2 * F.POST_R / IN, 3), round(F.BELT_W / IN, 3), round(F.BELT_MAX / IN, 3),
            round(F.BASE_H / IN, 3)) == (2.5, 2.0, 90.0, 2.0)
    assert F.plan(g["width"]["default"], g["depth"]["default"], g["height"]["default"])["facts"]["posts"] == 3
    # the belt's centre at waist height, about 36 in up
    assert abs(g["height"]["default"] - F.BELT_DROP - 36 * IN) < 0.03


@pytest.mark.parametrize("w,d,h", SIZES)
def test_the_extents_are_exactly_the_slots(w, d, h):
    lo, hi = prims.bounds(F.plan(w, d, h)["prims"])
    for a, (want_lo, want_hi) in enumerate(((-w / 2, w / 2), (-d / 2, d / 2), (-h / 2, h / 2))):
        assert math.isclose(lo[a], want_lo, abs_tol=1e-9) and math.isclose(hi[a], want_hi, abs_tol=1e-9)


@pytest.mark.parametrize("w,d,h", SIZES)
def test_no_face_lies_on_another(w, d, h):
    assert prims.coincident_pairs(F.plan(w, d, h)["prims"]) == []


def test_the_coincidence_check_can_see_a_pair():
    """The control: two belts a span, end to end, put their end faces on one plane inside the middle head -- the pair
    one belt through every head removes -- and the probe reports it."""
    xs = F.post_xs(4.6, 0.178)
    a = prims.box(F.PART, F.MAT, (xs[0], -F.BELT_T / 2, 0.4), (xs[1], F.BELT_T / 2, 0.45))
    b = prims.box(F.PART, F.MAT, (xs[1], -F.BELT_T / 2, 0.4), (xs[2], F.BELT_T / 2, 0.45))
    assert prims.coincident_pairs([a, b])


@pytest.mark.parametrize("w,d,h", SIZES)
def test_the_posts_are_as_few_as_keep_every_belt_within_its_reach(w, d, h):
    xs = F.post_xs(w, d / 2)
    spans = [b - a for a, b in zip(xs, xs[1:])]
    assert max(spans) <= F.BELT_MAX + 1e-9
    assert max(spans) - min(spans) < 1e-9
    # one post fewer and a belt would be past its reach
    assert (xs[-1] - xs[0]) / max(1, len(spans) - 1) > F.BELT_MAX or len(spans) == 1
    # the end bases' rims are the run's ends, and no two bases touch
    assert math.isclose(xs[0] - d / 2, -w / 2) and math.isclose(xs[-1] + d / 2, w / 2)
    assert min(spans) - d >= F.MIN_BELT - 1e-9


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


def _inside(v, solid):
    return all(sum(n[a] * v[a] for a in range(3)) - dd < -1e-7 for n, dd in solid)


@pytest.mark.parametrize("w,d,h", [(4.6, 0.356, 0.97), (1.1, 0.3, 0.9), (12.0, 0.42, 1.05), (2.65, 0.356, 0.97)])
def test_no_open_end_shows(w, d, h):
    """Every end left open lies strictly inside another member -- a post's foot in its base, its top in its head --
    but a base's underside, which is the floor's: it lies on the slot's bottom face."""
    got = F.plan(w, d, h)
    ps = got["prims"]
    solids = [_half_spaces(p) for p in ps]
    inside = on_floor = 0
    for i, p in enumerate(ps):
        for loop in _boundary_loops(p):
            if all(math.isclose(p["verts"][vi][2], -h / 2, abs_tol=1e-12) for vi in loop):
                on_floor += 1
                continue
            inside += 1
            for vi in loop:
                assert any(_inside(p["verts"][vi], solids[j]) for j in range(len(ps)) if j != i), (i, p["verts"][vi])
    posts = got["facts"]["posts"]
    assert (on_floor, inside) == (posts, 2 * posts)


@pytest.mark.parametrize("w,d,h", [(4.6, 0.356, 0.97), (1.1, 0.3, 0.9), (12.0, 0.42, 1.05)])
def test_the_belt_runs_through_every_head_and_ends_inside_the_end_ones(w, d, h):
    got = F.plan(w, d, h)
    ps = got["prims"]
    (belt,) = [p for p in ps if len(p["faces"]) == 6]
    heads = [p for p in ps if len(p["faces"]) == 2 + F.SIDES]
    assert len(heads) == got["facts"]["posts"]
    blo, bhi = prims.bounds([belt])
    for head in heads:
        hlo, hhi = prims.bounds([head])
        # inside every head's height, its 6 mm inside a head's flats
        assert hlo[2] < blo[2] and bhi[2] < hhi[2]
        assert bhi[1] < F.HEAD_R * F.FLAT
    # its two end faces inside the end heads
    end_heads = [_half_spaces(heads[0]), _half_spaces(heads[-1])]
    for v in belt["verts"]:
        if math.isclose(v[0], blo[0]) or math.isclose(v[0], bhi[0]):
            assert any(_inside(v, s) for s in end_heads), v
    assert math.isclose((blo[2] + bhi[2]) / 2, h / 2 - F.BELT_DROP, abs_tol=1e-9)


def test_an_open_end_is_narrower_than_what_hides_it():
    assert F.POST_R < F.HEAD_R * F.FLAT and F.POST_R < F.BASE_TOP_R * math.cos(math.pi / F.BASE_SIDES)
    assert 0 < F.SINK < F.BASE_H and F.SINK < F.HEAD_H
    assert F.BELT_T / 2 < F.HEAD_R * F.FLAT and F.BELT_W < F.HEAD_H


def test_the_base_stands_proud_of_a_floor_skin():
    """Deli Counter lays a room's floor finish as a 2 cm skin over the slab and stands a prop on the slab under it (its
    `floors.SKIN_THICK`): the crowd barrier's 9.5 mm feet were buried whole (Zoo 1.118.1). A base clears that skin by a
    centimetre or more, at every size."""
    skin = 0.02
    for w, d, h in SIZES:
        bases = [p for p in F.plan(w, d, h)["prims"] if len(p["faces"]) == 1 + F.BASE_SIDES]
        assert len(bases) == F.plan(w, d, h)["facts"]["posts"]
        assert all(max(v[2] for v in p["verts"]) - (-h / 2) >= skin + 0.01 for p in bases)


def test_one_material_one_part_one_submission_inside_the_budget():
    budget = genome.load_species("stanchion_run")["budgets"]["tris_lod0"]
    worst = 0
    for w, d, h in SIZES:
        got = F.plan(w, d, h)
        assert {p["mat"] for p in got["prims"]} == {F.MAT}
        assert {p["part"] for p in got["prims"]} == {F.PART}
        worst = max(worst, got["facts"]["tris"])
    assert worst <= budget, (worst, budget)


@pytest.mark.parametrize("w,d,h", [(4.6, 0.356, 0.97), (1.1, 0.3, 0.9), (12.0, 0.42, 1.05)])
def test_the_collision_is_the_posts_and_the_belt_line(w, d, h):
    """Each post base to head, and the belt line end post to end post: a body cannot walk through a run, and a shot
    above or below the belt passes."""
    got = F.plan(w, d, h)
    boxes = got["collision"]
    posts, (belt_lo, belt_hi) = boxes[:-1], boxes[-1]
    assert len(posts) == got["facts"]["posts"]
    xs = F.post_xs(w, d / 2)
    for (lo, hi), x in zip(posts, xs):
        assert math.isclose(lo[2], -h / 2) and math.isclose(hi[2], h / 2)
        assert math.isclose((lo[0] + hi[0]) / 2, x, abs_tol=1e-9)
        assert math.isclose(hi[1] - lo[1], 2 * F.POST_R, abs_tol=1e-9)
    assert math.isclose(belt_lo[0], xs[0]) and math.isclose(belt_hi[0], xs[-1])
    assert math.isclose(belt_hi[2] - belt_lo[2], F.BELT_W, abs_tol=1e-9)
    assert belt_lo[2] > -h / 2 + 0.5


def test_a_box_too_small_for_the_run_is_refused():
    with pytest.raises(ValueError):
        F.plan(0.8, 0.42, 0.97)
    with pytest.raises(ValueError):
        F.plan(4.6, 0.356, 0.3)
    F.plan(4 * 0.21 + F.MIN_BELT + 1e-6, 0.42, 0.97)
