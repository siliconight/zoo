"""vault_door module tests (pure -- no Blender).

The vault door is an interactive architectural module: the species builds only
the CLOSED (locked/unlocked) armored door; its open/breached states reuse
doorway/breach geometry through the slot's interactive.state_geometry. These
tests check the closed-door plan fits the slot exactly (frame defines the outer
box; leaf + hub stay inside), and that a vault-door slot expands into the right
per-state variants.
"""
from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import arch, dna, genome, kit, validate


def _approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def _module(dims, wcm, state=None, species="vault_door", typ="vault_door"):
    m = {"type": typ, "species": species, "state": state, "width_cm": wcm,
         "fit": "exact", "dims": dims, "pivot": "center",
         "stem": kit.module_stem(typ, "delco", 1, wcm, state)}
    return m


# --- the closed-door geometry fits the slot exactly ------------------------

def test_vault_door_void_is_a_heavy_framed_portal():
    v = arch.void_for("vault_door", 1.4, 2.3, {"jamb": 0.18})
    # heavy jambs (opening well inside the width), a raised threshold lip
    assert -0.7 < v["x0"] < v["x1"] < 0.7
    assert v["z0"] > -1.15 + 1e-6     # a lip you step over (not to the floor)


def test_vault_door_frame_footprint_is_exact():
    # the frame alone must span the exact (w, d, h); the leaf + hub sit inside.
    for (w, d, h) in [(1.4, 0.5, 2.3), (2.4, 0.6, 3.0), (0.9, 0.3, 2.0)]:
        void = arch.void_for("vault_door", w, h, {"jamb": 0.18})
        frame = arch.slab_parts(w, d, h, void)
        lo, hi = arch.parts_bbox(frame)
        assert _approx(hi[0] - lo[0], w)
        assert _approx(hi[1] - lo[1], d)
        assert _approx(hi[2] - lo[2], h)


def test_vault_door_plan_is_exact_fit_and_centered():
    g = genome.load_species("vault_door")
    plan = dna.resolve_module_plan(_module([1.4, 0.5, 2.3], 140), g, "delco", 1,
                                   TOOL_VERSION)
    assert plan["species"] == "vault_door"
    assert plan["pivot"] == "center"
    assert plan["fit_exact"] is True
    assert plan["target_dims"] == {"width": 1.4, "depth": 0.5, "height": 2.3}
    assert plan["module"]["stem"] == "vault_door_delco_01_w140"
    # frame footprint validates as an exact fit (what Blender reproduces)
    lo, hi = arch.parts_bbox(
        arch.slab_parts(1.4, 0.5, 2.3,
                        arch.void_for("vault_door", 1.4, 2.3, plan["params"])))
    facts = {"dimensions": {"width": round(hi[0] - lo[0], 4),
                            "depth": round(hi[1] - lo[1], 4),
                            "height": round(hi[2] - lo[2], 4)},
             "tris": 200, "parts": list(plan["parts"]), "has_uvs": True,
             "has_wear_colors": True, "materials": ["M_VaultDoor_metal"],
             "has_collision": True, "unapplied_transforms": []}
    report = validate.evaluate(facts, g, plan, {"collision": True})
    assert report["status"] == "pass", validate.summarize(report)


# --- a vault-door slot expands into the right per-state variants ------------

VAULT = {"id": "b:if:v1", "kind": "vault_door",
         "states": ["locked", "unlocked", "open", "breached"],
         "default": "locked",
         "state_geometry": {"locked": "vault_door", "unlocked": "vault_door",
                            "open": "doorway", "breached": "breach"}}


def _slot(dims, interactive=None):
    s = {"role": "vault_door", "size_mod": "full",
         "fit": {"dims": dims, "pivot": "center"}}
    if interactive:
        s["interactive"] = interactive
    return s


def test_vault_door_slot_builds_closed_open_and_breached():
    plan = kit.plan_kit({"building_id": "b",
                         "slots": [_slot([1.4, 0.5, 2.3], VAULT)]})
    stems = {m["stem"]: m for m in plan["modules"]}
    # locked (default) -> the closed vault door, base stem
    assert stems["vault_door_delco_01_w140"]["species"] == "vault_door"
    assert stems["vault_door_delco_01_w140"]["state"] is None
    # open -> reuses doorway geometry, named as the vault door's open state
    assert stems["vault_door_delco_01_w140_open"]["species"] == "doorway"
    # breached -> reuses breach geometry
    assert stems["vault_door_delco_01_w140_breached"]["species"] == "breach"
    # unlocked is identical art to locked today -> deferred, not built
    assert "vault_door_delco_01_w140_unlocked" not in stems
    deferred = {d["stem"] for d in plan["deferred_variants"]}
    assert "vault_door_delco_01_w140_unlocked" in deferred


def test_open_variant_builds_doorway_at_the_vault_dims():
    plan = kit.plan_kit({"building_id": "b",
                         "slots": [_slot([1.4, 0.5, 2.3], VAULT)]})
    v = next(m for m in plan["modules"] if m["state"] == "open")
    g = genome.load_species(v["species"])      # doorway genome
    bp = dna.resolve_module_plan(v, g, "delco", 1, TOOL_VERSION)
    assert bp["species"] == "doorway"
    assert bp["module"]["type"] == "vault_door"   # filename stays the vault's
    assert bp["dimensions"] == {"width": 1.4, "depth": 0.5, "height": 2.3}
