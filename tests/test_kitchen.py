from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, intent, seeding


def _plan(prompt, seed=0):
    it = intent.parse(prompt, seed=seed)
    g = genome.load_species(it.species)
    root = seeding.root_key(it.prompt_norm, it.species, seed, TOOL_VERSION)
    return it, dna.resolve_plan(it, g, seeding.RNGStreams(root), TOOL_VERSION)


def test_kitchen_species_parse():
    cases = {
        "flat top grill": "flat_top_grill",
        "greasy griddle": "flat_top_grill",
        "ketchup": "condiment_bottle",
        "mustard squeeze bottle": "condiment_bottle",
        "french fries": "french_fries",
        "pile of fries": "french_fries",
    }
    for prompt, species in cases.items():
        assert intent.parse(prompt).species == species, prompt


def test_condiment_flavor_colors():
    _, ketchup = _plan("ketchup")
    _, mustard = _plan("mustard bottle")
    _, mayo = _plan("mayo squeeze bottle")
    assert ketchup["color"][0] > 0.6 and ketchup["color"][1] < 0.3   # red
    assert mustard["color"][0] > 0.7 and mustard["color"][2] < 0.3   # yellow
    assert min(mayo["color"]) > 0.8                                  # near-white
    # distinct flavors -> distinct colors
    assert ketchup["color"] != mustard["color"] != mayo["color"]


def test_fries_scatter_count_and_pickup():
    _, plan = _plan("french fries")
    assert 12 <= plan["params"]["fries"] <= 28
    assert genome.load_species("french_fries").get("collision") is False


def test_grill_dims_realistic():
    _, plan = _plan("flat top grill")
    dims = plan["dimensions"]
    assert 0.9 <= dims["width"] <= 1.6
    # overall height includes the splash guards; cooking surface = height-0.12
    assert 0.98 <= dims["height"] <= 1.15
    assert 0.85 <= dims["height"] - 0.12 <= 0.98   # surface at counter height
