from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, intent, seeding


def _plan(prompt, seed=0):
    it = intent.parse(prompt, seed=seed)
    g = genome.load_species(it.species)
    root = seeding.root_key(it.prompt_norm, it.species, seed, TOOL_VERSION)
    return dna.resolve_plan(it, g, seeding.RNGStreams(root), TOOL_VERSION), g


def test_acceptance_plan():
    plan, g = _plan("1990s office desk with two drawers")
    assert plan["species"] == "desk"
    assert plan["style"] == "1990s"
    assert plan["material"] == "laminate"
    assert plan["params"]["drawers"] == 2
    assert plan["wear"] == 0.30
    for name, spec in g["dimensions"].items():
        assert spec["min"] <= plan["dimensions"][name] <= spec["max"]


def test_deterministic():
    a, _ = _plan("worn leather combat boots", seed=7)
    b, _ = _plan("worn leather combat boots", seed=7)
    assert a == b
    c, _ = _plan("worn leather combat boots", seed=8)
    assert a != c


def test_counts_clamped():
    plan, _ = _plan("desk with twelve drawers")
    assert plan["params"]["drawers"] == 4  # genome max


def test_intent_overrides_style_material():
    plan, _ = _plan("metal 1990s desk")
    assert plan["material"] == "metal"


def test_species_hooks():
    plan, _ = _plan("motorcycle helmet with visor")
    assert plan["params"]["visor"] == 1
    plan, _ = _plan("combat boots")
    assert plan["params"]["shaft_style"] == "tall"
    plan, _ = _plan("office chair")
    assert plan["params"]["has_arms"] == 1
    plan, _ = _plan("red hatchback car")
    assert plan["params"]["body_style"] == "hatchback"


def test_boots_pair_footprint_and_height():
    # A mirrored pair validates against the whole footprint, not one boot,
    # and the plan records the real shaft-derived height (regression: the
    # first Blender run FAILed width 0.249 vs single-boot [0.09,0.13] and
    # height 0.475 vs [0.12,0.45]).
    from zoo_keeper.core import validate
    plan, g = _plan("worn leather combat boots")
    assert plan["params"]["shaft_style"] == "tall"
    assert plan["dimensions"]["height"] == 0.475      # sole+foot+tall shaft
    assert plan["dim_scale"]["width"] == 2.3          # pair spans 2*0.65+1

    facts = {"dimensions": {"width": 0.249, "depth": 0.28, "height": 0.475},
             "tris": 900, "parts": ["Boot_L_Sole", "Boot_R_Sole"],
             "has_uvs": True, "has_wear_colors": True,
             "materials": ["M_Boots_leather"], "has_collision": True,
             "unapplied_transforms": []}
    rep = validate.evaluate(facts, g, plan, {"collision": True, "lods": False})
    assert rep["status"] == "pass"


def test_single_boot_still_single_scale():
    plan, _ = _plan("one leather boot")
    if plan["params"].get("pair", 2) == 1:
        assert plan["dim_scale"]["width"] == 1.0
