from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, intent, seeding


def _plan(prompt, seed=0):
    it = intent.parse(prompt, seed=seed)
    g = genome.load_species(it.species)
    root = seeding.root_key(it.prompt_norm, it.species, seed, TOOL_VERSION)
    plan = dna.resolve_plan(it, g, seeding.RNGStreams(root), TOOL_VERSION)
    return it, plan


def test_filing_cabinet_is_discovered():
    assert "filing_cabinet" in genome.list_species()


def test_parses_filing_cabinet_phrases():
    for p in ("filing cabinet", "file cabinet", "office filing cabinet",
              "grey metal cabinet", "filing"):
        it = intent.parse(p)
        assert it.species == "filing_cabinet", p


def test_default_plan_four_drawers_in_range():
    it, plan = _plan("1990s office filing cabinet")
    g = genome.load_species("filing_cabinet")
    assert plan["species"] == "filing_cabinet"
    assert plan["params"]["drawers"] == 4       # genome default
    assert plan["style"] == "1990s"
    for k, spec in g["dimensions"].items():
        assert spec["min"] <= plan["dimensions"][k] <= spec["max"]


def test_drawer_count_from_prompt():
    _, plan = _plan("filing cabinet with three drawers")
    assert plan["params"]["drawers"] == 3
    _, plan = _plan("filing cabinet with eight drawers")
    assert plan["params"]["drawers"] == 5       # clamped to genome max
