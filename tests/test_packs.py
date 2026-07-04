"""Knowledge Pack mechanism: species are self-describing (keywords +
prompt_rules in the genome) and recipes auto-discover by filename."""
import os

import pytest

from zoo_keeper import TOOL_VERSION
from zoo_keeper import recipes
from zoo_keeper.core import dna, genome, intent, seeding

RECIPE_DIR = os.path.join(os.path.dirname(recipes.__file__))


def _plan(prompt):
    it = intent.parse(prompt, seed=0)
    g = genome.load_species(it.species)
    root = seeding.root_key(it.prompt_norm, it.species, 0, TOOL_VERSION)
    return dna.resolve_plan(it, g, seeding.RNGStreams(root), TOOL_VERSION)


def test_every_species_declares_keywords():
    for sp in genome.list_species():
        kws = genome.load_species(sp).get("keywords")
        assert kws, f"{sp} genome has no keywords"


def test_every_species_has_a_recipe_module():
    for sp in genome.list_species():
        assert os.path.exists(os.path.join(RECIPE_DIR, f"{sp}.py")), \
            f"no recipe module for {sp}"


def test_keyword_collisions_resolve():
    # position-then-length tie-break keeps the specific term winning
    cases = {"soda machine": "vending_machine", "cash machine": "atm",
             "writing table": "desk", "cash": "cash_stack",
             "fountain drink": "soda_cup"}
    for prompt, species in cases.items():
        assert intent.parse(prompt).species == species, prompt


def test_prompt_rules_apply_from_genome():
    assert _plan("mustard bottle")["color"][1] > 0.6      # yellow
    assert _plan("police helmet")["params"].get("brim") == 1
    assert _plan("office chair")["params"].get("has_arms") == 1
    assert _plan("red hatchback car")["params"].get("body_style") == "hatchback"
    assert _plan("executive desk")["params"].get("leg_style") == "panel"


def test_recipe_registry_unknown_species_raises():
    with pytest.raises(KeyError):
        recipes.get("no_such_species_xyz")
