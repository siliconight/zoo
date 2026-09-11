"""A species the library cannot build is SAID, in one shape, on both paths.

`kit.plan_kit` has reported unknown species under `missing_modules` since
0.32.0, and `build.build_kit` has armed it with `genome.list_species()` for
just as long. The dry plan the pipeline runs as its pre-build gate
(`zoo_cli.py --kit ... --plan`) never passed the argument, so on that path an
unknown species was planned as if it would build. These pin that the plan is
armed, that the gap line carries what was asked, the nearest species that
exists and the owner, and that a clean plan prints no gap at all.
"""
import io
import json
import os
import sys
import types
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

from zoo_keeper.core import genome, kit  # noqa: E402
import zoo_cli  # noqa: E402


def _manifest(*roles):
    return {"building_id": "gap_bldg", "slots": [
        {"role": r, "fit": {"dims": [2.0, 0.3, 3.0], "pivot": "center"}}
        for r in roles]}


def test_a_missing_species_names_its_nearest_neighbour_and_owner():
    plan = kit.plan_kit(_manifest("wall", "wal"),
                        known_species={"wall", "doorway", "window"})
    missing = plan["missing_modules"]
    assert [m["species"] for m in missing] == ["wal"]
    assert missing[0]["nearest"] == ["wall"]
    assert missing[0]["owner"] == "zoo"


def test_a_genuinely_new_species_has_no_neighbour():
    plan = kit.plan_kit(_manifest("gazebo"),
                        known_species={"wall", "doorway", "window"})
    assert plan["missing_modules"][0]["nearest"] == []


def test_gap_lines_carry_the_tag_the_ask_the_nearest_and_the_owner():
    plan = kit.plan_kit(_manifest("wall", "wal", "wal"),
                        known_species={"wall", "doorway"})
    lines = kit.capability_gaps(plan)
    assert len(lines) == 1
    line = lines[0]
    assert kit.GAP_TAG in line
    assert "asked=wal" in line
    assert "x2" in line
    assert "nearest=wall" in line
    assert "owner=zoo" in line
    assert "zoo_keeper/genome/species/wal.json" in line


def test_a_clean_plan_prints_no_gap():
    plan = kit.plan_kit(_manifest("wall", "doorway"),
                        known_species={"wall", "doorway"})
    assert kit.capability_gaps(plan) == []


def test_the_dry_plan_is_armed_against_the_real_library(tmp_path):
    # The species set is the real one: `wall` is in it, `gazebo` is not.
    assert "wall" in genome.list_species()
    assert "gazebo" not in genome.list_species()
    p = tmp_path / "gap_bldg.slots.json"
    p.write_text(json.dumps(_manifest("wall", "gazebo")), encoding="utf-8")
    args = types.SimpleNamespace(kit=str(p), theme="delco", style=1,
                                 out=str(tmp_path))
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = zoo_cli.kit_run(args)
    out = buf.getvalue()
    assert rc == 0
    assert f"{kit.GAP_TAG} asked=gazebo" in out
    assert "owner=zoo" in out
    assert "1 module(s) the library cannot build" in out
    written = json.loads((tmp_path / "gap_bldg_kit.json").read_text(
        encoding="utf-8"))
    assert [m["species"] for m in written["missing_modules"]] == ["gazebo"]
    assert [m["species"] for m in written["modules"]] == ["wall"]


def test_the_dry_plan_is_quiet_when_the_library_has_everything(tmp_path):
    p = tmp_path / "ok_bldg.slots.json"
    p.write_text(json.dumps(_manifest("wall", "doorway")), encoding="utf-8")
    args = types.SimpleNamespace(kit=str(p), theme="delco", style=1,
                                 out="exhibits")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = zoo_cli.kit_run(args)
    assert rc == 0
    assert kit.GAP_TAG not in buf.getvalue()
