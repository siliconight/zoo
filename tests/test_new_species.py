"""tools/new_species.py mints a species that validates, plans and compiles
(roadmap 150), and refuses to overwrite one that exists.
"""
from __future__ import annotations

import json
import os
import py_compile
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

import new_species  # noqa: E402
from zoo_keeper.core import genome  # noqa: E402


def _mint(tmp_path, name="pump", extra=()):
    g = tmp_path / "genomes"
    r = tmp_path / "recipes"
    t = tmp_path / "tests"
    m = tmp_path / "minted.json"
    rc = new_species.main(["new", name, "--width", "1.0", "--depth", "1.2",
                           "--height", "1.4", "--material", "metal",
                           "--keywords", "pump,gas_pump", "--date", "2026-09-12",
                           "--genome-dir", str(g), "--recipes-dir", str(r),
                           "--tests-dir", str(t), "--minted", str(m), *extra])
    return rc, g, r, t, m


def test_a_minted_species_validates_and_compiles(tmp_path):
    rc, g, r, t, m = _mint(tmp_path)
    assert rc == 0
    gd = json.load(open(g / "pump.json", encoding="utf-8"))
    assert gd["species"] == "pump" and genome.validate_genome(gd) == []
    assert gd["dimensions"]["width"] == {"min": 0.5, "max": 2.0, "default": 1.0}
    assert gd["dimensions"]["height"]["default"] == 1.4
    assert gd["keywords"] == ["pump", "gas_pump"]
    assert gd["materials"]["default"] == "metal"
    assert gd["parts"] == ["Pump_Body"]
    py_compile.compile(str(r / "pump.py"), doraise=True)
    py_compile.compile(str(t / "test_pump.py"), doraise=True)
    assert "Pump_Body" in open(r / "pump.py", encoding="utf-8").read()
    assert json.load(open(m, encoding="utf-8")) == ["pump"]


def test_minting_refuses_to_overwrite(tmp_path):
    assert _mint(tmp_path)[0] == 0
    assert _mint(tmp_path)[0] == 2


def test_the_template_must_exist(tmp_path):
    rc, *_ = _mint(tmp_path, name="planter", extra=("--like", "no_such_species"))
    assert rc == 2


def test_report_reads_a_build_dir(tmp_path, capsys):
    b = tmp_path / "build"
    b.mkdir()
    (b / "x.slots.json").write_text(json.dumps({"slots": [
        {"slot_id": "pump_0", "role": "prop", "fit": {"dims": [1.0, 1.2, 1.4]}},
        {"slot_id": "pump_1", "role": "prop", "fit": {"dims": [1.0, 1.2, 1.4]}},
        {"slot_id": "thing", "role": "prop", "species": "hoverboard",
         "fit": {"dims": [1.0, 1.0, 1.0]}},
    ]}), encoding="utf-8")
    assert new_species.main(["report", "--build", str(b)]) == 0
    out = capsys.readouterr().out
    assert "2  pump" in out and "hoverboard" in out
