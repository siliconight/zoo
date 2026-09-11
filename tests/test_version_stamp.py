"""The stamp says which tool wrote the file; the seed does not move with it.

`TOOL_VERSION` was the literal "0.31.0" from July to 2026-09-11 while the tool
went to 0.58.0, so every index carried a stamp 27 releases stale -- and it
could not simply be corrected, because the same string is folded into every
specimen's root key and correcting it re-rolls every asset (roadmap 136). The
two meanings are split: `TOOL_VERSION` is read from `VERSION` and stamps,
`SEED_EPOCH` is frozen and seeds. These pin both halves, and pin the split
with the ids Zoo actually built on cold run 9005 the morning it was made.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import zoo_keeper  # noqa: E402
from zoo_keeper.core import habitat, intent, seeding, variants  # noqa: E402


def test_the_stamp_is_the_version_file():
    with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as fh:
        declared = fh.read().split()[-1]
    assert zoo_keeper.TOOL_VERSION == declared
    assert re.fullmatch(r"\d+\.\d+\.\d+", zoo_keeper.TOOL_VERSION)


def test_the_seed_epoch_is_frozen():
    """Changing this re-rolls every asset in every workspace. On purpose only."""
    assert zoo_keeper.SEED_EPOCH == "0.31.0"


def test_the_ids_zoo_built_on_cold_run_9005_reproduce():
    """`county_hospital_001.zoo_clutter_build`, 2026-09-11 09:0x, theme
    delco_1997, seed 9005: pebble_bb64e4.glb and habitat_a49078.habitat.json
    are on disk in cold-9005-ws. The same inputs under SEED_EPOCH give the
    same ids -- so the stamp moved and the geometry did not."""
    it = intent.parse(habitat.species_prompt("delco_1997", "pebble"), seed=9005)
    root = seeding.root_key(it.prompt_norm, it.species, 9005, zoo_keeper.SEED_EPOCH)
    assert f"{it.species}_{seeding.short_hash(root)}" == "pebble_bb64e4"
    species = ["litter_scrap", "pebble", "rubble_frag", "weed_tuft"]
    assert habitat.habitat_id("delco_1997", species, 9005,
                              zoo_keeper.SEED_EPOCH) == "habitat_a49078"


def test_no_seed_reads_the_stamp():
    """A static guard: every root_key / habitat_id / family_id call in the
    tree passes SEED_EPOCH, never TOOL_VERSION. The dynamic tests above
    would still pass while the two strings happen to be equal, which they are
    not, and will not be again."""
    offenders = []
    for base in ("zoo_keeper", "tools"):
        for dirpath, _dirs, files in os.walk(os.path.join(ROOT, base)):
            for f in files:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(dirpath, f)
                with open(p, encoding="utf-8") as fh:
                    text = fh.read()
                for m in re.finditer(r"(root_key|habitat_id|family_id)\((?:[^()]|\([^()]*\))*\)",
                                     text, re.S):
                    if "TOOL_VERSION" in m.group(0):
                        offenders.append(f"{os.path.relpath(p, ROOT)}: {m.group(0)[:60]}")
    assert offenders == [], offenders


def test_family_ids_are_seeded_by_the_epoch_too():
    a = variants.family_id("x", "pebble", 1, 3, zoo_keeper.SEED_EPOCH)
    b = variants.family_id("x", "pebble", 1, 3, zoo_keeper.TOOL_VERSION)
    assert a != b, "the two strings differ, so the choice is load-bearing"
