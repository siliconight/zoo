"""A street tree's crown of leaf cards (1.151.0, the factory's roadmap 324).

The walker, 2026-10-30, of the vertical slice: "try the card-based trees". The grown skeleton stays; every faceted
leaf mass at a tip becomes a clump of four cut-out cards in Pixelcoat's foliage pack (>= 0.65.0, whose cutout is
leaves, not discs), each card framing one tile of it. The default crown.
"""
import json
import pathlib

import pytest

from zoo_keeper.core import genome
from zoo_keeper.core import tree_forms as T

_FACTORY = pathlib.Path(__file__).resolve().parents[2]


#: every species `street_tree.py` builds: the generic tree and the five street species Lot plants by name.
#: RETRACTED, KEPT: the first draft of this test asked `street_tree` alone, passed, and the vertical slice's
#: slice-13 build shipped plate crowns unchanged -- Lot plants `honey_locust` and its siblings, each its own
#: genome with its own `crown`.
TREES = ("street_tree", "red_maple", "pin_oak", "honey_locust", "london_plane", "callery_pear")


def test_every_tree_species_defaults_to_leaf_cards():
    """FAILS ON 1.150.0: every tree's default was the faceted volume."""
    for sp in TREES:
        assert genome.load_species(sp)["params"]["crown"] == "leafcards", sp


def test_the_list_is_every_species_the_tree_recipe_builds():
    import pathlib as _p
    rec = _p.Path(genome.__file__).resolve().parents[1] / "recipes"
    builds = {f.stem for f in rec.glob("*.py")
              if f.stem == "street_tree" or "from .street_tree import build" in f.read_text(encoding="utf-8")}
    assert builds == set(TREES), sorted(builds)


def test_a_card_frames_one_foliage_tile():
    """The card's UVs span one tile of the foliage pack, so its ellipse of leaves sits in the card's middle."""
    prof = _FACTORY / "pixelcoat" / "profiles" / "materials" / "foliage_delco.json"
    if not prof.is_file():
        pytest.skip("no Pixelcoat beside this repo to read the foliage profile from")
    d = json.loads(prof.read_text(encoding="utf-8"))
    assert d["meters_per_tile"] == T.LEAF_TILE_M
    assert d["cutout"].get("leaves"), "the foliage cutout is not leaves: a card would show discs"
