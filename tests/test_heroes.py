import math

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, intent, scatter, seeding


class _RNG:
    """Tiny deterministic RNG stand-in for scatter tests."""
    def __init__(self, seed=1):
        self.s = seed

    def random(self):
        # LCG — deterministic, enough for placement tests
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s / 0x7FFFFFFF


def test_scatter_count_and_bounds():
    ts = scatter.scatter_transforms(20, _RNG(3), area=(0.1, 0.4))
    assert len(ts) == 20
    for t in ts:
        x, y, z = t["pos"]
        assert abs(x) <= 0.1 + 1e-6 and abs(y) <= 0.4 + 1e-6
        assert 0.85 <= t["scale"] <= 1.15 + 1e-6
        assert -math.pi - 1e-6 <= t["rot_z"] <= math.pi + 1e-6


def test_scatter_deterministic():
    a = scatter.scatter_transforms(15, _RNG(7), area=(0.2, 0.2))
    b = scatter.scatter_transforms(15, _RNG(7), area=(0.2, 0.2))
    assert a == b


def test_scatter_builds_height():
    ts = scatter.scatter_transforms(10, _RNG(2), area=(0.1, 0.1),
                                    base_z=0.0, layer_rise=0.01)
    assert ts[-1]["pos"][2] > ts[0]["pos"][2]  # a heap, not a flat sheet


def _plan(prompt, seed=0):
    it = intent.parse(prompt, seed=seed)
    g = genome.load_species(it.species)
    root = seeding.root_key(it.prompt_norm, it.species, seed, TOOL_VERSION)
    return it, dna.resolve_plan(it, g, seeding.RNGStreams(root), TOOL_VERSION)


def test_hero_species_parse():
    assert intent.parse("philly cheesesteak").species == "cheesesteak"
    assert intent.parse("cheese steak hoagie").species == "cheesesteak"
    assert intent.parse("fountain soda cup").species == "soda_cup"


def test_hero_plans_resolve():
    _, plan = _plan("1990s cheesesteak")
    assert plan["species"] == "cheesesteak"
    assert 6 <= plan["params"]["meat_chunks"] <= 18
    _, plan = _plan("diner soda cup")
    assert plan["species"] == "soda_cup"


def test_food_is_pickup_no_collision():
    for s in ("cheesesteak", "soda_cup"):
        assert genome.load_species(s).get("collision") is False
