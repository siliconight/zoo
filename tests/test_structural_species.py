"""Phase 1 structural species (the vertical-slice visual-gate set):
stair_rail, ladder, wallCorner, shelving, counter. Pure planner tests —
geometry is proven by building the specimens (bpy)."""
from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, intent, seeding

STRUCTURAL = ("stair_rail", "ladder", "wallCorner", "shelving", "counter")


def _plan(prompt, seed=0):
    it = intent.parse(prompt, seed=seed)
    g = genome.load_species(it.species)
    root = seeding.root_key(it.prompt_norm, it.species, seed, TOOL_VERSION)
    return it, dna.resolve_plan(it, g, seeding.RNGStreams(root), TOOL_VERSION)


def test_structural_species_parse():
    cases = {
        "stair railing": "stair_rail",
        "handrail": "stair_rail",
        "guardrail": "stair_rail",
        "service ladder": "ladder",
        "roof ladder": "ladder",
        "wall corner": "wallCorner",
        "stockroom shelving": "shelving",
        "store shelf": "shelving",
        "shop counter": "counter",
        "service counter": "counter",
    }
    for prompt, species in cases.items():
        assert intent.parse(prompt).species == species, prompt


def test_structural_genomes_validate():
    for sp in STRUCTURAL:
        g = genome.load_species(sp)
        assert genome.validate_genome(g) == [], sp
        assert g.get("collision") is True, sp


def test_structural_plans_resolve_in_range():
    for sp, prompt in (("stair_rail", "stair railing"),
                       ("ladder", "service ladder"),
                       ("wallCorner", "wall corner"),
                       ("shelving", "shelving"),
                       ("counter", "shop counter")):
        it, plan = _plan(prompt)
        assert it.species == sp, (prompt, it.species)
        g = genome.load_species(sp)
        for k, spec in g["dimensions"].items():
            v = plan["dimensions"][k]
            assert spec["min"] - 0.05 <= v <= spec["max"] + 0.05, (sp, k, v)


def test_structural_plans_deterministic():
    for prompt in ("stair railing", "service ladder", "wall corner",
                   "shelving", "shop counter"):
        _, a = _plan(prompt, seed=7)
        _, b = _plan(prompt, seed=7)
        assert a == b, prompt


def test_recipes_registered():
    from zoo_keeper import recipes
    for sp in STRUCTURAL:
        assert recipes.get(sp) is not None, sp


def test_kit_categories_cover_structural():
    """The kit index taxonomy knows the new architectural types."""
    from zoo_keeper.bpylayer import build as B
    assert B._module_category("stair_rail").startswith("architecture/")
    assert B._module_category("ladder").startswith("architecture/")
    assert B._module_category("wallCorner").startswith("architecture/")
