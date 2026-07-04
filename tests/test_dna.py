from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, intent, seeding


def _plan(prompt, seed=0):
    it = intent.parse(prompt, seed=seed)
    g = genome.load_species(it.species)
    root = seeding.root_key(it.prompt_norm, it.species, seed, TOOL_VERSION)
    return dna.resolve_plan(it, g, seeding.RNGStreams(root), TOOL_VERSION), g


def test_acceptance_plan():
    plan, g = _plan("1990s office desk with two drawers")
    assert plan["species"] == "desk"
    assert plan["style"] == "1990s"
    assert plan["material"] == "laminate"
    assert plan["params"]["drawers"] == 2
    assert plan["wear"] == 0.30
    for name, spec in g["dimensions"].items():
        assert spec["min"] <= plan["dimensions"][name] <= spec["max"]


def test_deterministic():
    a, _ = _plan("worn leather combat boots", seed=7)
    b, _ = _plan("worn leather combat boots", seed=7)
    assert a == b
    c, _ = _plan("worn leather combat boots", seed=8)
    assert a != c


def test_counts_clamped():
    plan, _ = _plan("desk with twelve drawers")
    assert plan["params"]["drawers"] == 4  # genome max


def test_intent_overrides_style_material():
    plan, _ = _plan("metal 1990s desk")
    assert plan["material"] == "metal"


def test_species_hooks():
    plan, _ = _plan("motorcycle helmet with visor")
    assert plan["params"]["visor"] == 1
    plan, _ = _plan("combat boots")
    assert plan["params"]["shaft_style"] == "tall"
    plan, _ = _plan("office chair")
    assert plan["params"]["has_arms"] == 1
    plan, _ = _plan("red hatchback car")
    assert plan["params"]["body_style"] == "hatchback"
