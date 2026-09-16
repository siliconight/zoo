"""The material-kind vocabulary is one list kept in two places — check it.

`core.skins.KNOWN_KINDS` and `bpylayer.materials.ROUGHNESS` are the same
vocabulary written twice, with a "keep in sync" comment on each and, until
now, nothing enforcing it. Three kinds had already drifted out of the pair:

  * `tar`, declared by the `roof` species since it shipped, was in NEITHER
    list. `make_material` fell through to its 0.6 default roughness and
    `find_pack` could never resolve a skin pack for it, on every roof, for the
    whole life of the species. Nothing failed; it was just quietly wrong.
  * `gravel` and `vegetation` arrived with the Layer 3 dressing kit and went
    the same way.

A comment is not a test. This is the test.

WHY IT PARSES INSTEAD OF IMPORTING. `bpylayer.materials` imports `bpy` at
module scope, and this suite runs without Blender (`test_skins.py` says so in
its first line). Importing it here would make the check unrunnable in exactly
the environment that needs to run it — which is the reason the check never got
written. Reading the literal with `ast` needs no Blender and cannot execute
anything, so the test runs everywhere the suite does.
"""
from __future__ import annotations

import ast
import glob
import json
import os

from zoo_keeper.core import genome, skins

_HERE = os.path.dirname(os.path.abspath(__file__))
_ZOO = os.path.dirname(_HERE)
_MATERIALS = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "materials.py")


def _dict_literal(path, name):
    """Return the keys of a module-level dict literal, without importing."""
    tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name:
                assert isinstance(node.value, ast.Dict), \
                    f"{name} in {path} is not a dict literal"
                keys = [ast.literal_eval(k) for k in node.value.keys]
                assert len(keys) == len(set(keys)), \
                    f"{name} has duplicate keys: {keys}"
                return keys
    raise AssertionError(f"no module-level {name} found in {path}")


def test_roughness_is_a_readable_dict_literal():
    """Guard the guard: if materials.py stops exposing ROUGHNESS as a literal,
    every assertion below would silently have nothing to compare and pass."""
    keys = _dict_literal(_MATERIALS, "ROUGHNESS")
    assert len(keys) > 15, f"only {len(keys)} kinds parsed — parser broken?"


def test_known_kinds_and_roughness_agree():
    known = set(skins.KNOWN_KINDS)
    rough = set(_dict_literal(_MATERIALS, "ROUGHNESS"))
    assert known == rough, (
        "the kind vocabulary has drifted:\n"
        f"  in KNOWN_KINDS only: {sorted(known - rough)}\n"
        f"  in ROUGHNESS only:   {sorted(rough - known)}")


def test_known_kinds_has_no_duplicates():
    assert len(skins.KNOWN_KINDS) == len(set(skins.KNOWN_KINDS))


def test_metallic_kinds_are_in_the_vocabulary():
    metallic = set(_dict_literal(_MATERIALS, "METALLIC"))
    assert metallic <= set(skins.KNOWN_KINDS), \
        f"METALLIC names kinds nothing else knows: {sorted(metallic - set(skins.KNOWN_KINDS))}"


def _genome_kinds():
    """Every material kind any genome names, and who names it."""
    used = {}
    pattern = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "*.json")
    for path in sorted(glob.glob(pattern)):
        name = os.path.splitext(os.path.basename(path))[0]
        g = json.load(open(path, encoding="utf-8"))
        mats = g.get("materials", {})
        for kind in [mats.get("default")] + list(mats.get("options", [])):
            if kind:
                used.setdefault(kind, set()).add(name)
        for tag, style in (g.get("styles") or {}).items():
            if style.get("material"):
                used.setdefault(style["material"], set()).add(f"{name}:{tag}")
    return used


def test_every_genome_kind_is_in_the_vocabulary():
    """A species may not name a kind the material factory has never heard of.

    This is the assertion that would have caught `tar` on the day the roof
    species landed. It fails loudly with the species that names the orphan,
    because "some kind is missing" is not actionable and "roof names tar" is.
    """
    used = _genome_kinds()
    known = set(skins.KNOWN_KINDS)
    orphans = {k: sorted(v) for k, v in used.items() if k not in known}
    assert not orphans, (
        "genomes name material kinds that are in neither KNOWN_KINDS nor "
        f"ROUGHNESS, so they silently take default roughness and resolve no "
        f"skin pack: {orphans}")


def test_the_vocabulary_check_can_actually_fail():
    """Falsification. If the genome sweep found nothing to look at, the test
    above passes vacuously — assert it is really reading the genomes, and that
    an invented kind would be caught."""
    used = _genome_kinds()
    assert len(used) >= 15, f"only {len(used)} kinds seen across genomes"
    assert "concrete" in used, "the sweep is not reading genome materials"
    probe = dict(used)
    probe["unobtainium"] = ["fake_species"]
    orphans = [k for k in probe if k not in set(skins.KNOWN_KINDS)]
    assert orphans == ["unobtainium"], \
        "an invented kind was not flagged — the orphan check is dead"


def test_dressing_kinds_are_present():
    """The Layer 3 kit's two kinds specifically, named so a regression says
    which layer broke rather than just 'the vocabulary'."""
    for kind in ("gravel", "vegetation"):
        assert kind in skins.KNOWN_KINDS, f"{kind} missing from KNOWN_KINDS"
        assert kind in _dict_literal(_MATERIALS, "ROUGHNESS"), \
            f"{kind} missing from ROUGHNESS"


def test_the_card_shop_kinds_are_present():
    """Pixelcoat 0.44.0's `wood_panel_delco` and `slatwall_retail`, named so
    a regression says which library broke rather than just "the vocabulary".
    `carpet_tournament` came with them and needs NO kind: a pack directory is
    `<kind>_<theme>`, so it is `carpet` under a `tournament` theme.

    THIS FAILS ON 0.94.0, where neither kind exists and a card shop asking
    for one built the genome default in silence."""
    for kind in ("wood_panel", "slatwall"):
        assert kind in skins.KNOWN_KINDS, f"{kind} missing from KNOWN_KINDS"
        assert kind in _dict_literal(_MATERIALS, "ROUGHNESS"),             f"{kind} missing from ROUGHNESS"
    assert "carpet" in skins.KNOWN_KINDS


def test_an_unknown_slot_material_is_reported_and_not_dropped_in_silence():
    """The defect this release closes, and the reason it is a REPORT rather
    than a refusal: older manifests carry kinds this vocabulary never had,
    and failing a building that is otherwise fine would be worse than
    building the genome default. What was wrong was the silence --
    `carpet_club` shipped in Pixelcoat 0.42.0 and built as concrete for a
    release because nothing said so.

    FAILS ON 0.94.0: `plan_kit` has no `unknown_materials` key at all, so
    this cannot even read the answer."""
    from zoo_keeper.core import kit
    plan = kit.plan_kit({"building_id": "t", "slots": [
        {"slot_id": "w0", "role": "wall", "size_mod": "full", "style": 1,
         "material": "unobtainium",
         "fit": {"dims": [2.0, 0.2, 3.0], "pivot": "center"}},
        {"slot_id": "w1", "role": "wall", "size_mod": "full", "style": 1,
         "material": "wood_panel",
         "fit": {"dims": [2.0, 0.2, 3.0], "pivot": "center"}}]},
        theme="delco_1997", style=1)
    said = plan["unknown_materials"]
    assert [u["material"] for u in said] == ["unobtainium"], said
    assert said[0]["slot_id"] == "w0"
    # and the known one reaches a module NAME, which is the end-to-end claim
    stems = [m["stem"] for m in plan["modules"]]
    assert any(s.endswith("_mwood_panel") for s in stems), stems
    assert not any("unobtainium" in s for s in stems), stems


def test_species_count_matches_the_genome_folder():
    """`genome.list_species` and the folder must agree — a stray or missing
    file is how a species goes untested without anything going red."""
    pattern = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "*.json")
    on_disk = {os.path.splitext(os.path.basename(p))[0]
               for p in glob.glob(pattern)}
    assert set(genome.list_species()) == on_disk
