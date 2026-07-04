from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, intent, seeding


def _plan(prompt, seed=0):
    it = intent.parse(prompt, seed=seed)
    g = genome.load_species(it.species)
    root = seeding.root_key(it.prompt_norm, it.species, seed, TOOL_VERSION)
    plan = dna.resolve_plan(it, g, seeding.RNGStreams(root), TOOL_VERSION)
    return it, plan


def test_heist_species_parse():
    cases = {
        "wooden table": "table",
        "1990s crt tv": "crt_tv",
        "old television": "crt_tv",
        "bodega atm": "atm",
        "cash machine": "atm",           # 'cash machine' must beat 'cash'
        "soda machine": "vending_machine",
        "vending machine": "vending_machine",
        "leather briefcase": "briefcase",
        "stack of cash": "cash_stack",
        "money": "cash_stack",
    }
    for prompt, species in cases.items():
        assert intent.parse(prompt).species == species, prompt


def test_all_heist_species_resolve_in_range():
    for prompt in ("table", "crt tv", "atm", "vending machine", "briefcase",
                   "cash stack"):
        it, plan = _plan("1990s " + prompt)
        g = genome.load_species(it.species)
        for k, spec in g["dimensions"].items():
            v = plan["dimensions"][k]
            assert spec["min"] - 0.05 <= v <= spec["max"] + 0.05, (prompt, k, v)


def test_cash_stack_count_and_height():
    _, plan = _plan("five stacks of cash")
    assert plan["params"]["stacks"] == 5
    # height written back from strap count (honest meta)
    assert abs(plan["dimensions"]["height"] - 5 * dna.CASH_STRAP_H) < 1e-6


def test_new_habitats():
    from zoo_keeper.core import habitat
    known = genome.list_species()
    assert habitat.resolve_species("corner_store", known) == \
        ["vending_machine", "atm", "table", "crt_tv"]
    assert habitat.resolve_species("score", known) == \
        ["briefcase", "cash_stack", "atm"]


def test_collision_defaults():
    # cash is loot -> no blocking collision by default
    assert genome.load_species("cash_stack").get("collision") is False
    # solid props leave it unset -> build treats absent as True
    for s in ("atm", "vending_machine", "table", "desk"):
        assert genome.load_species(s).get("collision", True) is True
