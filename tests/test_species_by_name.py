"""A species can be asked for by name, not only guessed at from a prompt.

WHY THIS EXISTS. Until now `intent.parse` had exactly one way in: keyword
matching against a plain-text prompt. That is the right interface for a person
and the wrong one for a program, and it had already failed twice without
anyone noticing:

  * `wallCorner` and `wallEnd` return species None for their own names. Two
    species have been in the library, tested by `test_genome`, and completely
    unrequestable for their whole lives. `test_every_species_is_addressable`
    below is the assertion that would have caught it.
  * Layer 3 surface dressing needs a placement layer to ask for `pebble` a few
    thousand times per site. `parse("pebble")` works today because no other
    keyword currently beats it -- a coincidence, not a contract. A new species
    with an overlapping keyword would silently redress the level.

Pure tests: no bpy, no Blender. `build_specimen` takes the same `species=`
argument and is exercised by the preview harness, not here.
"""
from __future__ import annotations

import pytest

from zoo_keeper.core import genome, intent


def test_every_species_is_addressable_by_name():
    """The whole library, one round trip each. This is the regression guard:
    a species that exists must be buildable."""
    for sp in genome.list_species():
        assert intent.parse("", species=sp).species == sp


def test_two_species_are_unreachable_by_prompt():
    """The measurement that motivated the argument, kept as a test so the
    claim in the docstrings stays true or fails loudly.

    If this ever fails because the set SHRANK, someone fixed a keyword set and
    should shrink it here too. If it fails because the set GREW, a new species
    just landed that nothing can ask for."""
    unreachable = {sp for sp in genome.list_species()
                   if intent.parse(sp.replace("_", " ")).species != sp}
    assert unreachable == {"wallCorner", "wallEnd"}, (
        "the set of prompt-unreachable species changed: " + repr(unreachable))


def test_named_species_beats_a_conflicting_prompt():
    """The guarantee a placement layer is buying. The prompt says desk as
    loudly as it can; the argument still wins."""
    it = intent.parse("1990s office desk with two drawers", species="pebble")
    assert it.species == "pebble"
    assert it.species_source == "explicit"


def test_prompt_still_supplies_styling_when_species_is_named():
    """Naming the species must not switch the rest of the parser off, or a
    caller would have to choose between the species it needs and the look it
    wants."""
    it = intent.parse("small red worn", species="rubble_frag")
    assert it.species == "rubble_frag"
    assert it.color_name == "red"
    assert it.wear >= 0.5
    assert it.size_hint < 1.0


def test_keyword_path_is_unchanged_and_labelled():
    it = intent.parse("1990s office desk with two drawers")
    assert it.species == "desk"
    assert it.species_source == "keyword"
    assert "species" not in it.unresolved


def test_unresolved_species_has_no_source():
    it = intent.parse("something nobody models")
    assert it.species is None
    assert it.species_source is None
    assert "species" in it.unresolved


def test_unknown_species_raises_and_names_the_alternatives():
    """A program asking for a species that does not exist has a bug. It
    surfaces here, not as a quietly different asset three stages later."""
    with pytest.raises(ValueError) as e:
        intent.parse("", species="gazebo")
    assert "gazebo" in str(e.value)
    assert "pebble" in str(e.value)


def test_empty_prompt_canonicalises_to_the_species_name():
    """Repeated requests for one species must hash to one root key, or every
    caller's choice of empty string becomes part of the asset's identity."""
    a = intent.parse("", species="pebble")
    b = intent.parse("   ", species="pebble")
    c = intent.parse(None, species="pebble")
    assert a.prompt_norm == b.prompt_norm == c.prompt_norm == "pebble"


def test_a_supplied_prompt_is_kept_in_the_root_key_input():
    """...but a caller that DOES pass a prompt keeps it, so two differently
    styled pebbles remain two different specimens rather than colliding."""
    plain = intent.parse("", species="pebble")
    mossy = intent.parse("wet mossy", species="pebble")
    assert plain.prompt_norm != mossy.prompt_norm


def test_dressing_species_are_all_addressable():
    """Named individually so a regression says which layer broke."""
    for sp in ("pebble", "rubble_frag", "weed_tuft", "litter_scrap"):
        it = intent.parse("", species=sp)
        assert it.species == sp
        assert it.species_source == "explicit"
