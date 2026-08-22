"""Glass debris + broken-window state art -- the breakable-glass chain.

Zoo's leg of the replicated-destructible pattern: the game owns the state
machine (an id and an intact/broken flag; see INTERACTIVES.md), and these
two species own what a break LOOKS like. `glass_shard` is the cosmetic
debris -- one object per shard, so the game can fling each piece.
`window_broken` is the `_broken` state variant of a window slot, expanded
by the same kit machinery that gives a breachable wall its breached state.
"""
from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, intent, kit, seeding


def _plan(prompt, species=None, seed=0):
    it = intent.parse(prompt, seed=seed, species=species)
    g = genome.load_species(it.species)
    root = seeding.root_key(it.prompt_norm, it.species, seed, TOOL_VERSION)
    return it, g, dna.resolve_plan(it, g, seeding.RNGStreams(root),
                                   TOOL_VERSION)


# --- prompt door -------------------------------------------------------------

def test_glass_prompts_resolve():
    assert intent.parse("broken glass").species == "glass_shard"
    assert intent.parse("glass shards").species == "glass_shard"
    assert intent.parse("shattered glass on the floor").species == \
        "glass_shard"
    assert intent.parse("broken window").species == "window_broken"
    assert intent.parse("shattered window").species == "window_broken"


def test_intact_window_prompts_are_untouched():
    # "broken window" matches at position 0 and wins; a plain "window"
    # must keep resolving to the intact module. (A prompt naming several
    # species -- "a wall with a window" -- resolves by earliest match, as
    # it always has; that is the parser's law, not this species'.)
    assert intent.parse("window").species == "window"
    assert intent.parse("office window").species == "window"


# --- glass_shard: cosmetic debris -------------------------------------------

def test_glass_shard_plan_resolves_glass():
    _it, g, plan = _plan("", species="glass_shard")
    assert plan["material"] == "glass"
    assert plan["params"]["shards"] == 9
    for k, spec in g["dimensions"].items():
        assert spec["min"] - 0.05 <= plan["dimensions"][k] <= \
            spec["max"] + 0.05, k


def test_glass_shard_is_cosmetic():
    """Shards must never block a route or a beam -- same law as the other
    dressing debris."""
    assert genome.load_species("glass_shard").get("collision") is False


def test_shards_share_the_pane_kind_and_tint():
    """One Pixelcoat pack skins both the window pane and the shards, so
    debris matches the pane it fell out of. The genome tints agree too, so
    the flat fallback matches as well."""
    shard = genome.load_species("glass_shard")
    window = genome.load_species("window")
    assert shard["materials"]["default"] == "glass"
    assert shard["styles"]["default"]["color"] == window["glass_color"]


# --- window_broken: the _broken state of a window slot ----------------------

WINDOW_INT = {"id": "b:if:9", "kind": "window",
              "states": ["intact", "broken"], "default": "intact",
              "state_geometry": {"intact": "window",
                                 "broken": "window_broken"}}


def _window_slot(dims, interactive=None):
    slot = {"role": "window", "size_mod": "full",
            "fit": {"dims": dims, "pivot": "center"}}
    if interactive:
        slot["interactive"] = interactive
    return slot


def test_breakable_window_expands_like_a_breachable_wall():
    plan = kit.plan_kit(
        {"building_id": "b",
         "slots": [_window_slot([1.1, 0.3, 2.1], WINDOW_INT)]},
        known_species=genome.list_species())
    stems = {m["stem"]: m for m in plan["modules"]}
    assert stems["window_delco_01_w110"]["species"] == "window"
    v = stems["window_delco_01_w110_broken"]
    assert v["species"] == "window_broken"
    assert v["state"] == "broken"
    assert v["type"] == "window"                # filename stays the window's
    assert v["dims"] == [1.1, 0.3, 2.1]         # inherits the slot's size
    assert plan["deferred_variants"] == []
    assert plan.get("missing_modules", []) == []


def test_broken_variant_builds_window_broken_plan_at_slot_dims():
    plan = kit.plan_kit(
        {"building_id": "b",
         "slots": [_window_slot([1.1, 0.3, 2.1], WINDOW_INT)]})
    v = next(m for m in plan["modules"] if m["state"] == "broken")
    g = genome.load_species(v["species"])
    bp = dna.resolve_module_plan(v, g, "delco", 1, TOOL_VERSION)
    assert bp["species"] == "window_broken"
    assert bp["module"]["type"] == "window"
    assert bp["module"]["state"] == "broken"
    assert bp["module"]["stem"] == "window_delco_01_w110_broken"
    assert bp["dimensions"] == {"width": 1.1, "depth": 0.3, "height": 2.1}
    assert bp["glass_color"] == [0.55, 0.66, 0.72]


def test_plain_window_slot_is_completely_unchanged():
    plan = kit.plan_kit({"building_id": "b",
                         "slots": [_window_slot([1.1, 0.3, 2.1])]})
    stems = [m["stem"] for m in plan["modules"]]
    assert stems == ["window_delco_01_w110"]
    assert plan["deferred_variants"] == []
