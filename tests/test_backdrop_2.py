"""The backdrop's tree and warehouse (Zoo 1.96.0, roadmap 228): the parkland, roadside and yards
recipes' species, planned by `core.backdrop_forms`. No bpy here; the build is proven by a kit
build inside Blender (the factory root's `docs/findings/backdrop_kit/`)."""
import pytest

from zoo_keeper.core import backdrop_forms as BF
from zoo_keeper.core import genome, kit


@pytest.mark.parametrize("species", ["backdrop_tree", "backdrop_warehouse"])
def test_the_species_are_discovered_and_validate(species):
    assert species in genome.list_species()
    assert genome.validate_genome(genome.load_species(species)) == []
    assert genome.load_species(species)["collision"] is False


def test_both_plan_at_their_authored_dims_as_a_kit():
    plan = kit.plan_kit({"building_id": "t", "slots": [
        {"slot_id": "b0", "role": "prop", "size_mod": "full", "style": 1,
         "species": "backdrop_tree", "fit": {"dims": [7.0, 7.0, 10.0], "pivot": "center"}},
        {"slot_id": "b1", "role": "prop", "size_mod": "full", "style": 1,
         "species": "backdrop_warehouse", "fit": {"dims": [30.0, 16.0, 8.0], "pivot": "center"}},
    ]}, theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert sorted(m["species"] for m in plan["modules"]) == ["backdrop_tree", "backdrop_warehouse"]


@pytest.mark.parametrize("w, h", [(7.0, 10.0), (3.0, 5.0), (12.0, 16.0)])
def test_the_tree_stands_exactly_its_dims(w, h):
    p = BF.tree_parts(w, h)
    (tc, ts), (cc, radii) = p["trunk"], p["crown"]
    assert abs(tc[2] - ts[2] / 2 + h / 2) < 1e-9                      # the trunk's foot
    assert abs(cc[2] + radii[2] - h / 2) < 1e-9                       # the crown's top
    assert abs(radii[0] - w / 2) < 1e-9 and abs(radii[1] - w / 2) < 1e-9
    assert ts[0] == BF.TREE_TRUNK and tc[2] + ts[2] / 2 <= cc[2] + 1e-9   # the trunk ends in the crown
    assert BF.tree_tris_estimate() <= genome.load_species("backdrop_tree")["budgets"]["tris_lod0"]


def test_the_crowns_facets_put_a_vertex_on_both_axes():
    assert BF.TREE_U_SEG % 4 == 0


@pytest.mark.parametrize("dims", [(30.0, 16.0, 8.0), (16.0, 10.0, 5.0), (48.0, 24.0, 12.0)])
def test_the_warehouse_stands_exactly_its_dims_with_its_monitors_inset(dims):
    w, d, h = dims
    parts = BF.warehouse_parts(w, d, h)
    assert all(abs(a - b) < 1e-9 for a, b in zip(BF.extents(parts), dims))
    body = next(p for p in parts if p[0] == "body")
    body_top = body[1][2] + body[2][2] / 2
    monitors = [p for p in parts if p[0].startswith("monitor")]
    assert len(monitors) == BF.MONITORS
    for _n, c, s in monitors:
        assert abs((c[2] - s[2] / 2) - (body_top - BF.INSET)) < 1e-9
        assert abs((c[2] + s[2] / 2) - h / 2) < 1e-9
        assert abs(c[0]) + s[0] / 2 <= w / 2 + 1e-9 and s[1] < d


def test_the_warehouse_paint_lights_only_the_lit_high_windows():
    bw, bh = 30.0, 8.0 - BF.MONITOR_H
    img, emi, lit = BF.paint_warehouse(bw, bh, BF.WH_SIDING, "stem_3")
    openings = BF.warehouse_openings(bw, bh)
    assert openings[0][0] == "door" and sum(1 for o in openings if o[0] == "window") == len(lit) >= 4
    glow = emi.a.sum(axis=2)
    assert (glow > 0).any() == any(lit)
    # over many stems, about one window in three is lit
    n = lit_n = 0
    for i in range(300):
        p = BF.warehouse_lit(f"s{i}", 6)
        n += 6
        lit_n += sum(1 for s in p if s)
    assert 0.25 < lit_n / n < 0.42


def test_the_warehouse_uvs_send_the_front_to_the_facade_and_the_roof_to_the_tar():
    w, d, h = 30.0, 16.0, 8.0
    front = BF.warehouse_uv_for((3.0, -d / 2, -h / 2 + 2.0), (0.0, -1.0, 0.0), w, d, h)
    assert 0.0 <= front[0] < BF.FACADE_PX / BF.IMG_W
    roof = BF.warehouse_uv_for((0.0, 0.0, -h / 2 + h - BF.MONITOR_H), (0.0, 0.0, 1.0), w, d, h)
    assert roof[0] >= (BF.FACADE_PX + BF.STRIP_PX) / BF.IMG_W
    monitor_front = BF.warehouse_uv_for((0.0, -d * 0.3, h / 2 - 0.5), (0.0, -1.0, 0.0), w, d, h)
    assert monitor_front[0] >= (BF.FACADE_PX + BF.STRIP_PX) / BF.IMG_W
    side = BF.warehouse_uv_for((w / 2, 2.0, 0.0), (1.0, 0.0, 0.0), w, d, h)
    assert BF.FACADE_PX / BF.IMG_W <= side[0] < (BF.FACADE_PX + BF.STRIP_PX) / BF.IMG_W
