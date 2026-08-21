"""A recipe that builds materials must read its genome's material.

THE DEFECT THIS CATCHES: flat_top_grill passed the literal "metal" to every
make_material call it made. Its genome had a material field. Editing that field
changed nothing -- silently. Nothing failed, nothing warned, and the genome was
decorative for as long as nobody looked.

The rule is deliberately module-level rather than call-level. A call-level rule
("plan[\'material\'] must appear in the arguments") reports flat_top_grill as
broken even after it was fixed, because the fix assigns kind = plan["material"]
and passes kind. Indirection through a local is normal and correct.

Sub-part literals are NOT a defect: a bottle cap is plastic, a boot sole is
rubber, the paper boat under the fries is paper. Those parts do not vary with
the body material and hardcoding them is right. This test says nothing about
them; it only requires that the module consult its genome at least once.
"""
import ast
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
RECIPES = os.path.join(os.path.dirname(HERE), "zoo_keeper", "recipes")

# A recipe may appear here only with a reason. The test below ALSO fails if an
# exempt recipe starts reading its genome, so a stale exemption cannot survive.
EXEMPT = {
    "cheesesteak": (
        "composite food prop: bun, crust, meat, cheese and seeds each carry "
        "their own material and there is no single body surface for the genome "
        "to control. Its genome offers exactly one option (paper), so nothing "
        "is rendered wrong today. If a second option is ever added, remove this "
        "exemption and give the wrapper plan['material']."
    ),
}


def _modules():
    out = []
    for fn in sorted(os.listdir(RECIPES)):
        if fn.endswith(".py") and not fn.startswith("_"):
            out.append((fn[:-3], os.path.join(RECIPES, fn)))
    return out


def _analyse(path):
    with open(path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    calls = 0
    reads = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if (getattr(fn, "id", None) or getattr(fn, "attr", None)) == "make_material":
                calls += 1
            if (getattr(fn, "attr", None) == "get" and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == "material"):
                reads += 1
        if (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
                and node.slice.value == "material"):
            reads += 1
    return calls, reads


MODULES = _modules()


def test_the_sweep_is_actually_reading_recipes():
    assert len(MODULES) >= 40, "only %d recipe modules found" % len(MODULES)
    assert sum(_analyse(p)[0] for _, p in MODULES) >= 40, "no make_material calls seen"


@pytest.mark.parametrize("name,path", MODULES, ids=[m[0] for m in MODULES])
def test_recipe_that_builds_materials_reads_its_genome(name, path):
    calls, reads = _analyse(path)
    if calls == 0:
        pytest.skip("builds no materials")
    if name in EXEMPT:
        assert reads == 0, (
            "%s is listed as EXEMPT but now reads its genome %d time(s). "
            "Remove it from EXEMPT -- a stale exemption hides the next "
            "regression." % (name, reads)
        )
        return
    assert reads > 0, (
        "%s calls make_material %d time(s) but never reads a \'material\' key, "
        "so its genome cannot affect it. Either pass plan['material'] to the "
        "body material, or add it to EXEMPT with a reason." % (name, calls)
    )


def test_every_exemption_names_a_real_recipe():
    names = {n for n, _ in MODULES}
    unknown = sorted(set(EXEMPT) - names)
    assert not unknown, "EXEMPT names no such recipe: %s" % ", ".join(unknown)
    for name, reason in EXEMPT.items():
        assert len(reason) > 40, "%s exemption needs a real reason" % name
