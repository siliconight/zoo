"""The material-options invariant, and batch 1 of the metal split.

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
BATCH1 = ("vending_machine", "simple_car", "helmet", "queue_stanchion")


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


@pytest.mark.parametrize("sp", BATCH1)
def test_batch1_species_are_on_painted_metal(sp):
    g = json.load(open(os.path.join(SPECIES_DIR, sp + ".json"),
                       encoding="utf-8"))
    opts = g["materials"]["options"]
    assert "metal_painted" in opts, "%s did not gain metal_painted" % sp
    assert "metal" not in opts, (
        "%s still offers raw `metal`; a prompt naming it would resolve the "
        "theme-owned pack and ignore the genome colour" % sp)
    for name, style in g.get("styles", {}).items():
        assert style.get("material") != "metal", \
            "%s style %r was left on raw metal" % (sp, name)


def test_batch1_is_the_only_thing_that_moved():
    """The other 49 genomes must still be on plain `metal`. When batch 2 lands
    this list changes deliberately, not by surprise."""
    moved = [g["species"] for g in _genomes()
             if "metal_painted" in g["materials"].get("options", [])]
    assert sorted(moved) == sorted(BATCH1), (
        "species on metal_painted: %s\nexpected exactly batch 1: %s"
        % (sorted(moved), sorted(BATCH1)))
