import json

from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, intent, meta, seeding, validate


def _setup():
    it = intent.parse("1990s office desk with two drawers")
    g = genome.load_species("desk")
    root = seeding.root_key(it.prompt_norm, "desk", 0, TOOL_VERSION)
    plan = dna.resolve_plan(it, g, seeding.RNGStreams(root), TOOL_VERSION)
    return it, g, plan


def _good_facts(plan):
    return {"dimensions": dict(plan["dimensions"]), "tris": 500,
            "parts": ["Desk_Top", "Desk_Leg_L"], "has_uvs": True,
            "has_wear_colors": True, "materials": ["M_Desk_laminate"],
            "has_collision": True, "unapplied_transforms": []}


def test_validate_pass_and_fail():
    it, g, plan = _setup()
    report = validate.evaluate(_good_facts(plan), g, plan,
                               {"collision": True})
    assert report["status"] == "pass"

    bad = _good_facts(plan)
    bad["has_uvs"] = False
    bad["dimensions"]["height"] = 2.5
    report = validate.evaluate(bad, g, plan, {"collision": True})
    assert report["status"] == "fail"
    ids = {c["id"] for c in report["checks"] if c["level"] == "fail"}
    assert {"uvs", "dim_height"} <= ids


def test_tri_budget_warns_not_fails():
    it, g, plan = _setup()
    facts = _good_facts(plan)
    facts["tris"] = 999999
    report = validate.evaluate(facts, g, plan, {"collision": True})
    assert report["status"] == "warn"


def test_meta_deterministic_and_timestamp_free(tmp_path):
    it, g, plan = _setup()
    report = validate.evaluate(_good_facts(plan), g, plan,
                               {"collision": True})
    m1 = meta.build_meta(TOOL_VERSION, it, plan, g, report,
                         {"glb": "x.glb"}, "desk_abc123")
    m2 = meta.build_meta(TOOL_VERSION, it, plan, g, report,
                         {"glb": "x.glb"}, "desk_abc123")
    assert json.dumps(m1, sort_keys=True) == json.dumps(m2, sort_keys=True)
    assert "time" not in json.dumps(m1).lower()
    p = tmp_path / "m.json"
    meta.write_meta(str(p), m1)
    assert json.loads(p.read_text())["license"][
        "construction_knowledge"] == "CC0"
