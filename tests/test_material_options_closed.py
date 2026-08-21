"""The material-options invariant, and the metal split by batch.

`dna.resolve_plan` and `dna.resolve_module_plan` both do this, silently:

    if material not in genome["materials"]["options"]:
        material = genome["materials"]["default"]

A style block naming a kind that is missing from `options` is DISCARDED, and
the species quietly renders in its default material. Nothing logs. The render
looks plausible. That is the trap the metal split walks into once per species,
and it is why these tests sweep every genome rather than only the ones a given
batch touched.
"""

import glob
import json
import os

import pytest

from zoo_keeper.core import skins

SPECIES_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "zoo_keeper", "genome", "species")

# Batch 1 (0.44.0) and batch 2 (0.45.0). Split painted/bare because METALLIC
# is a per-kind lookup: paint is a dielectric, bare metal a conductor.
PAINTED = ("vending_machine", "simple_car", "helmet", "queue_stanchion",
           "chair", "filing_cabinet", "atm")
BARE = ("gold_bar", "flat_top_grill", "water_tank", "shelving", "vault_door")
MOVED = PAINTED + BARE


def _genomes():
    out = []
    for p in sorted(glob.glob(os.path.join(SPECIES_DIR, "*.json"))):
        out.append(json.load(open(p, encoding="utf-8")))
    return out


def test_the_sweep_is_actually_reading_genomes():
    """Guard the guard: every assertion below is a loop, and a loop over an
    empty directory passes vacuously."""
    g = _genomes()
    assert len(g) >= 50, "only %d genomes found" % len(g)
    assert any(x["species"] == "vending_machine" for x in g)


@pytest.mark.parametrize("g", _genomes(), ids=lambda g: g["species"])
def test_every_style_material_is_in_options(g):
    opts = set(g["materials"].get("options", []))
    for name, style in g.get("styles", {}).items():
        if not isinstance(style, dict) or "material" not in style:
            continue
        assert style["material"] in opts, (
            "%s style %r names %r, which is not in materials.options %s. "
            "resolve_plan will discard it and silently use %r."
            % (g["species"], name, style["material"], sorted(opts),
               g["materials"].get("default")))


@pytest.mark.parametrize("g", _genomes(), ids=lambda g: g["species"])
def test_default_material_is_in_options(g):
    opts = set(g["materials"].get("options", []))
    assert g["materials"]["default"] in opts, (
        "%s default %r is not in its own options -- the fallback target is "
        "itself unreachable" % (g["species"], g["materials"]["default"]))


@pytest.mark.parametrize("g", _genomes(), ids=lambda g: g["species"])
def test_every_named_kind_is_in_the_vocabulary(g):
    """A kind nothing knows takes the 0.6 default roughness and resolves no
    pack. This is the check that would have caught `tar` on day one."""
    named = set(g["materials"].get("options", []))
    named.add(g["materials"]["default"])
    for style in g.get("styles", {}).values():
        if isinstance(style, dict) and "material" in style:
            named.add(style["material"])
    unknown = named - set(skins.KNOWN_KINDS)
    assert not unknown, "%s names unknown kinds: %s" % (g["species"],
                                                        sorted(unknown))


@pytest.mark.parametrize("sp", MOVED)
def test_moved_species_no_longer_offer_raw_metal(sp):
    g = json.load(open(os.path.join(SPECIES_DIR, sp + ".json"),
                       encoding="utf-8"))
    opts = g["materials"]["options"]
    assert "metal" not in opts, (
        "%s still offers raw `metal`; a prompt naming it would resolve the "
        "theme-owned pack and ignore the genome colour" % sp)
    for name, style in g.get("styles", {}).items():
        assert style.get("material") != "metal", \
            "%s style %r was left on raw metal" % (sp, name)


@pytest.mark.parametrize("sp", PAINTED)
def test_painted_species_are_on_metal_painted(sp):
    g = json.load(open(os.path.join(SPECIES_DIR, sp + ".json"),
                       encoding="utf-8"))
    assert "metal_painted" in g["materials"]["options"], sp


@pytest.mark.parametrize("sp", BARE)
def test_bare_species_are_on_metal_bare(sp):
    g = json.load(open(os.path.join(SPECIES_DIR, sp + ".json"),
                       encoding="utf-8"))
    assert "metal_bare" in g["materials"]["options"], sp


def test_nothing_else_moved():
    """The remaining 41 genomes stay on plain `metal`. When batch 3 lands this
    list changes deliberately, not by surprise."""
    moved = [g["species"] for g in _genomes()
             if {"metal_painted", "metal_bare"} & set(
                 g["materials"].get("options", []))]
    assert sorted(moved) == sorted(MOVED), (
        "on a split kind: %s\nexpected: %s" % (sorted(moved), sorted(MOVED)))


def test_no_species_is_both_painted_and_bare():
    """One object, one metal. A species offering both would let a prompt pick
    the conductor value for a painted surface."""
    for g in _genomes():
        opts = set(g["materials"].get("options", []))
        assert not ({"metal_painted", "metal_bare"} <= opts), \
            "%s offers BOTH metal_painted and metal_bare" % g["species"]


RECIPE_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "zoo_keeper", "recipes")


@pytest.mark.parametrize("sp", ("flat_top_grill", "vault_door"))
def test_recipes_no_longer_hardcode_the_kind(sp):
    """THE DEFECT THAT MADE A GENOME EDIT INERT. flat_top_grill passed the
    literal "metal" to all three of its make_material calls, so editing its
    genome changed nothing at all -- silently. vault_door hard-coded only its
    hub, which would have split one door across two kinds."""
    src = open(os.path.join(RECIPE_DIR, sp + ".py"), encoding="utf-8").read()
    assert '"metal")' not in src, (
        "%s.py still passes the literal \"metal\" to make_material; its "
        "genome would be ignored" % sp)
