"""Interactive-slot expansion tests (pure).

An interactive slot (door, breachable wall) is a replicable state machine; the
kit planner must build the art for each state that DIFFERS, name it with the
`_<state>` suffix Deli Counter's resolver expects, and defer states whose art
is identical today (resolver falls back to the base). Zoo builds art only — no
network concepts leak into the plan. See INTERACTIVES.md.
"""
from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, kit


def _wall(dims, interactive=None):
    slot = {"role": "wall", "size_mod": "full",
            "fit": {"dims": dims, "pivot": "center"}}
    if interactive:
        slot["interactive"] = interactive
    return slot


def _door(dims, interactive=None):
    slot = {"role": "doorway", "size_mod": "full",
            "fit": {"dims": dims, "pivot": "center"}}
    if interactive:
        slot["interactive"] = interactive
    return slot


# --- plain slots are completely unchanged ----------------------------------

def test_non_interactive_slot_yields_single_base_variant():
    variants = list(kit.slot_variants(_wall([2.0, 0.3, 3.6]), "wall"))
    assert variants == [("wall", None, None, False)]


def test_plain_kit_modules_carry_species_and_null_state():
    plan = kit.plan_kit({"building_id": "b", "slots": [_wall([2.0, 0.3, 3.6])]})
    m = plan["modules"][0]
    assert m["type"] == "wall" and m["species"] == "wall"
    assert m["state"] is None
    assert m["stem"] == "wall_delco_01_w200"
    assert plan["deferred_variants"] == []


# --- breachable wall: breached is a STATE of the wall, built with breach ----

BREACH_WALL = {"id": "b:if:1", "kind": "breach_wall",
               "states": ["intact", "breached"], "default": "intact",
               "state_geometry": {"intact": "wall", "breached": "breach"}}


def test_breachable_wall_expands_to_intact_base_plus_breached_variant():
    plan = kit.plan_kit({"building_id": "b",
                         "slots": [_wall([2.0, 0.3, 3.6], BREACH_WALL)]})
    stems = {m["stem"]: m for m in plan["modules"]}
    # intact = base stem, built with wall geometry
    assert stems["wall_delco_01_w200"]["species"] == "wall"
    assert stems["wall_delco_01_w200"]["state"] is None
    # breached = suffixed stem, built with BREACH geometry, at the wall's dims
    v = stems["wall_delco_01_w200_breached"]
    assert v["species"] == "breach"
    assert v["state"] == "breached"
    assert v["type"] == "wall"                 # filename stays the wall's
    assert v["dims"] == [2.0, 0.3, 3.6]         # inherits the wall's size
    assert plan["module_count"] == 2


def test_breached_variant_builds_breach_plan_at_wall_dims():
    plan = kit.plan_kit({"building_id": "b",
                         "slots": [_wall([2.0, 0.3, 3.6], BREACH_WALL)]})
    v = next(m for m in plan["modules"] if m["state"] == "breached")
    g = genome.load_species(v["species"])          # breach genome
    bp = dna.resolve_module_plan(v, g, "delco", 1, TOOL_VERSION)
    assert bp["species"] == "breach"               # breach recipe runs
    assert bp["module"]["type"] == "wall"          # DC contract = wall slot
    assert bp["module"]["state"] == "breached"
    assert bp["module"]["stem"] == "wall_delco_01_w200_breached"
    assert bp["dimensions"] == {"width": 2.0, "depth": 0.3, "height": 3.6}


def test_breachable_walls_collapse_across_slots():
    plan = kit.plan_kit({"building_id": "b", "slots": [
        _wall([2.0, 0.3, 3.6], BREACH_WALL),
        _wall([2.0, 0.3, 3.6], BREACH_WALL),
        _wall([2.0, 0.3, 3.6]),  # a plain (non-breachable) 2m wall
    ]})
    stems = {m["stem"]: m for m in plan["modules"]}
    # all three intact walls share the base module
    assert stems["wall_delco_01_w200"]["count"] == 3
    # both breachable ones share the breached variant
    assert stems["wall_delco_01_w200_breached"]["count"] == 2


# --- same-species states are deferred (progressive art pass) ---------------

DOOR_PLAIN = {"id": "b:if:2", "kind": "door",
              "states": ["closed", "open"], "default": "closed"}


def test_same_species_state_is_deferred_not_built():
    # no state_geometry -> both states resolve to 'doorway' -> identical art
    # today -> the 'open' state is deferred (resolver falls back to base).
    plan = kit.plan_kit({"building_id": "b",
                         "slots": [_door([1.1, 0.3, 2.1], DOOR_PLAIN)]})
    stems = {m["stem"] for m in plan["modules"]}
    assert "doorway_delco_01_w110" in stems
    assert "doorway_delco_01_w110_open" not in stems     # not built
    deferred = {d["stem"] for d in plan["deferred_variants"]}
    assert "doorway_delco_01_w110_open" in deferred


def test_door_with_distinct_open_geometry_is_built():
    # once the art pass gives 'open' its own geometry (here modeled by mapping
    # open -> a different species), it IS built as a variant.
    door = {"id": "b:if:3", "kind": "door", "states": ["closed", "open"],
            "default": "closed",
            "state_geometry": {"closed": "doorway", "open": "wall"}}
    plan = kit.plan_kit({"building_id": "b",
                         "slots": [_door([1.1, 0.3, 2.1], door)]})
    stems = {m["stem"]: m for m in plan["modules"]}
    assert stems["doorway_delco_01_w110_open"]["species"] == "wall"
    assert plan["deferred_variants"] == []


def test_default_defaults_to_first_state_when_unset():
    door = {"id": "b:if:4", "kind": "door", "states": ["shut", "ajar"],
            "state_geometry": {"shut": "doorway", "ajar": "wall"}}
    variants = list(kit.slot_variants(_door([1.0, 0.3, 2.0], door), "doorway"))
    # first state 'shut' is the base (state None); 'ajar' is the variant
    assert (build_sp for build_sp, st, _ss, _d in variants)
    base = [v for v in variants if v[1] is None]
    assert base and base[0][0] == "doorway"
