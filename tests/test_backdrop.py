"""The backdrop beyond the plate's edge (Zoo 1.95.0, roadmap 228 step C): `backdrop_rowhome`
and `water_tower`, planned by `core.backdrop_forms`. No bpy here; the recipes' build is proven by
a kit build inside Blender (the factory root's `docs/findings/backdrop_kit/`)."""
import pytest

from zoo_keeper.core import backdrop_forms as BF
from zoo_keeper.core import genome, kit


@pytest.mark.parametrize("species", ["backdrop_rowhome", "water_tower"])
def test_the_species_are_discovered_and_validate(species):
    assert species in genome.list_species()
    assert genome.validate_genome(genome.load_species(species)) == []
    assert genome.load_species(species)["collision"] is False


def test_both_plan_at_their_authored_dims_as_a_kit():
    plan = kit.plan_kit({"building_id": "t", "slots": [
        {"slot_id": "backdrop_0", "role": "prop", "size_mod": "full", "style": 1,
         "species": "backdrop_rowhome", "fit": {"dims": [6.0, 12.0, 9.5], "pivot": "center"}},
        {"slot_id": "backdrop_1", "role": "prop", "size_mod": "full", "style": 1,
         "species": "water_tower", "fit": {"dims": [14.0, 14.0, 40.0], "pivot": "center"}},
    ]}, theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert sorted(m["species"] for m in plan["modules"]) == ["backdrop_rowhome", "water_tower"]


def test_a_rowhome_has_six_openings_two_a_storey_the_ground_left_one_a_door():
    bw, bd, bh, _y = BF.body_dims(6.0, 12.0, 9.5)
    ws = BF.windows(bw, bh)
    assert len(ws) == 6
    assert [k for k, *_ in ws].count("door") == 1 and ws[0][0] == "door"
    for kind, x0, z0, x1, z1 in ws:
        assert 0.0 <= x0 < x1 <= bw and 0.0 <= z0 < z1 <= bh
    # the three storeys' windows climb
    sills = [z0 for k, x0, z0, x1, z1 in ws if k == "window"]
    assert sills == sorted(sills)


def test_the_lit_pattern_is_deterministic_for_a_stem_and_differs_between_stems():
    a = BF.lit_pattern("backdrop_rowhome_delco_01_w600_d1200_h950", 5)
    assert a == BF.lit_pattern("backdrop_rowhome_delco_01_w600_d1200_h950", 5)
    assert all(s in (None, "warm", "tv") for s in a)
    # over many stems, about one window in five is lit, one in five of those a TV
    lit = tv = 0
    for i in range(400):
        p = BF.lit_pattern(f"stem_{i}", 5)
        lit += sum(1 for s in p if s)
        tv += sum(1 for s in p if s == "tv")
    assert 0.14 < lit / 2000 < 0.26
    assert 0.1 < tv / max(1, lit) < 0.3


def test_the_paint_lights_only_the_lit_windows():
    bw, bd, bh, _y = BF.body_dims(6.0, 12.0, 9.5)
    img, emi, lit = BF.paint(bw, bh, (0.4, 0.2, 0.16), "stem_7")
    assert (img.w, img.h) == (BF.IMG_W, BF.IMG_H) == (emi.w, emi.h)
    boxes = [b for b in BF.facade_boxes(bw, bh) if b[0] == "window"]
    assert len(boxes) == len(lit) == 5
    glow = emi.a.sum(axis=2)
    for (kind, x0, y0, x1, y1), state in zip(boxes, lit):
        inside = glow[y0:y1, x0:x1]
        assert (inside.max() > 0) == (state is not None)
    # nothing glows outside the windows
    mask = glow > 0
    for kind, x0, y0, x1, y1 in boxes:
        mask[y0:y1, x0:x1] = False
    assert not mask.any()
    # the strips: brick to the right of the facade, tar at the far right
    assert tuple(img.a[64, BF.FACADE_PX + 4]) != tuple(img.a[64, BF.IMG_W - 4])


def test_the_uvs_send_the_front_to_the_facade_and_the_rest_to_the_strips():
    w, d, h = 6.0, 12.0, 9.5
    bw, bd, bh, y_front = BF.body_dims(w, d, h)
    front = BF.uv_for((1.5, y_front, -h / 2 + 2.0), (0.0, -1.0, 0.0), w, d, h)
    assert 0.0 <= front[0] < BF.FACADE_PX / BF.IMG_W and abs(front[1] - 2.0 / bh) < 1e-9
    side = BF.uv_for((bw / 2, 3.0, 0.0), (1.0, 0.0, 0.0), w, d, h)
    assert BF.FACADE_PX / BF.IMG_W <= side[0] < (BF.FACADE_PX + BF.STRIP_PX) / BF.IMG_W
    roof = BF.uv_for((0.0, 0.0, -h / 2 + bh), (0.0, 0.0, 1.0), w, d, h)
    assert roof[0] >= (BF.FACADE_PX + BF.STRIP_PX) / BF.IMG_W
    # the cornice's and the stoop's fronts stand off the body's front plane: not the facade
    cornice = BF.uv_for((0.0, y_front - BF.CORNICE_OUT, -h / 2 + bh - 0.1), (0.0, -1.0, 0.0), w, d, h)
    stoop = BF.uv_for((-bw / 4, -d / 2, -h / 2 + 0.2), (0.0, -1.0, 0.0), w, d, h)
    assert cornice[0] >= (BF.FACADE_PX + BF.STRIP_PX) / BF.IMG_W
    assert stoop[0] >= (BF.FACADE_PX + BF.STRIP_PX) / BF.IMG_W


@pytest.mark.parametrize("dims", [(6.0, 12.0, 9.5), (5.5, 12.0, 8.0), (4.5, 8.0, 6.0), (8.0, 16.0, 11.0)])
def test_the_rowhome_stands_exactly_its_dims(dims):
    """Zoo's exact fit: the first build failed fit_width, fit_depth and fit_height
    because the cornice, the stoop and the chimney stood outside the slot."""
    w, d, h = dims
    parts = BF.rowhome_parts(w, d, h)
    got = BF.extents(parts)
    assert all(abs(a - b) < 1e-9 for a, b in zip(got, dims)), (got, dims)
    by = {n: (c, s) for n, c, s in parts}
    (cc, cs), (hc, hs), (sc, ss), (bc, bs) = by["cornice"], by["chimney"], by["stoop"], by["body"]
    body_front, body_top = bc[1] - bs[1] / 2, bc[2] + bs[2] / 2
    # no face of a part lies in a face of the body (the census found four such
    # pairs): the cornice's and stoop's backs and the chimney's foot stand INSET
    # inside it, the cornice's top INSET under its top
    assert abs((cc[1] + cs[1] / 2) - (body_front + BF.INSET)) < 1e-9
    assert abs((cc[2] + cs[2] / 2) - (body_top - BF.INSET)) < 1e-9
    assert abs((hc[2] - hs[2] / 2) - (body_top - BF.INSET)) < 1e-9
    assert abs((sc[1] + ss[1] / 2) - (body_front + BF.INSET)) < 1e-9
    # and its foot INSET above the body's, off the body's bottom plane
    assert abs(sc[2] - ss[2] / 2 - (-h / 2 + BF.INSET)) < 1e-9
    assert abs(sc[1] - ss[1] / 2 + d / 2) < 1e-9


def test_the_tower_stands_from_its_foot_to_its_beacon_within_its_dims():
    w, h = 14.0, 40.0
    p = BF.tower_parts(w, h)
    assert len(p["legs"]) == 4 and len(p["braces"]) == 8
    for c, s in p["legs"]:
        assert abs(c[2] - s[2] / 2 + h / 2) < 1e-9
        assert abs(c[0]) + s[0] / 2 <= w / 2 and abs(c[1]) + s[1] / 2 <= w / 2
    (tc, tr, th) = p["tank"]
    assert abs(tr - w / 2) < 1e-9 and abs(tc[2] - th / 2 - (-h / 2 + h * BF.LEG_TOP)) < 1e-9
    # the legs reach INSET into the tank, the cap's foot INSET into its top, and
    # a ring's two directions of brace stand one thickness apart in height
    tank_foot, tank_top = tc[2] - th / 2, tc[2] + th / 2
    for c, s in p["legs"]:
        assert abs((c[2] + s[2] / 2) - (tank_foot + BF.INSET)) < 1e-9
    (cc, cr, ch) = p["cap"]
    assert cr <= tr + 1e-9 and abs((cc[2] - ch / 2) - (tank_top - BF.INSET)) < 1e-9
    zs = sorted({round(c[2], 6) for c, s in p["braces"]})
    assert len(zs) == 2 * len(BF.BRACE_AT)
    (bc, br) = p["beacon"]
    assert abs(bc[2] + br - h / 2) < 1e-9
    assert abs((cc[2] + ch / 2) - (bc[2] - br)) < 1e-9
    assert BF.tower_tris_estimate() <= genome.load_species("water_tower")["budgets"]["tris_lod0"]
