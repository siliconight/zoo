"""A stair hole's balustrade (1.128.0): `stoop_railing`'s level form, as long as a hole edge, posts at least every
`POST_BAY`. The walker, walking cold run 9386, of an office stair's solid wood guards: "the walling/railing doesn't
loook natural yet". FAILS ON 1.127.0, but for the stoop's, which must not move."""
from zoo_keeper.core import genome, kit
from zoo_keeper.core import stoop_railing_forms as F


def test_the_genome_fits_a_stair_holes_guard():
    """Deli Counter's office guard rail, 4.3889 x 0.1 x 1.07 m, builds as the species, not the box."""
    slot = {"slot_id": "stair_guard_rail_1", "role": "prop", "size_mod": "full", "style": 1,
            "material": "metal_painted", "species": "stoop_railing", "form": "level",
            "fit": {"dims": [4.3889, 0.1, 1.07], "pivot": "center", "collision": "none"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["modules"][0]["species"] == "stoop_railing", plan.get("species_fallbacks")
    assert not plan.get("species_fallbacks"), plan["species_fallbacks"]


def test_a_long_run_stands_a_post_every_bay_and_keeps_its_pickets_clear():
    got = F.plan(4.3889, 0.1, 1.07, "level")
    bays = got["facts"]["posts"] - 1
    assert bays == 3, got["facts"]
    def box(p):
        vs = p["verts"]
        return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]

    xs = sorted((box(p)[0][0] + box(p)[1][0]) / 2.0 for p in got["prims"]
                if abs((box(p)[1][0] - box(p)[0][0]) - F.POST) < 1e-6 and abs((box(p)[1][2] - box(p)[0][2]) - 1.07) < 1e-6)
    assert len(xs) == 4, xs
    gaps = [b - a for a, b in zip(xs, xs[1:])]
    assert max(gaps) <= F.POST_BAY + 1e-9 and max(gaps) - min(gaps) < 1e-9, gaps


def test_a_stoops_railing_is_unchanged():
    """One bay: the same parts, in the same order, as 1.127.0 drew -- 2 posts, 2 rails, the pickets."""
    got = F.plan(0.9, 0.038, 0.9144, "level")
    assert got["facts"]["posts"] == 2
    assert got["facts"]["pickets"] == len(F.pickets(-0.45 + F.POST, 0.45 - F.POST, F.members(0.038)[3]))


def test_the_genome_still_takes_a_stoop():
    d = genome.load_species("stoop_railing")["dimensions"]
    assert d["width"]["min"] <= 0.9 <= d["width"]["max"] == 8.0
    assert d["depth"]["min"] <= 0.038 and d["depth"]["max"] == 0.12
