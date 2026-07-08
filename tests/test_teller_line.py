"""teller_line module tests (pure -- no Blender).

The teller line is an interactive architectural module: a solid counter + a
framed bulletproof-glass barrier with a transaction slot, built intact. These
tests check the frame + counter tile the exact (w, d, h) envelope (the glass
sits inside), the plan is center-pivot exact-fit, and a teller slot expands so
`shattered` defers to the intact base until a shattered-glass art pass.
"""
from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, kit, validate


def _approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


# Replicate the recipe's structural boxes (counter + posts + header) to prove
# their union is exactly (w, d, h). (Pure — mirrors teller_line.build.)
def _structure_bbox(w, d, h, p):
    counter_h = min(p.get("counter_h", 1.1), h * 0.6)
    post = min(p.get("post", 0.10), w * 0.3)
    header = min(p.get("header", 0.20), (h - counter_h) * 0.5)
    hw, hh = w / 2.0, h / 2.0
    counter_top = -hh + counter_h
    open_w = w - 2.0 * post
    boxes = [((0.0, 0.0, -hh + counter_h / 2.0), (w, d, counter_h))]
    boxes.append(((-hw + post / 2.0, 0.0, (counter_top + hh) / 2.0),
                  (post, d, hh - counter_top)))
    boxes.append(((hw - post / 2.0, 0.0, (counter_top + hh) / 2.0),
                  (post, d, hh - counter_top)))
    boxes.append(((0.0, 0.0, (hh - header + hh) / 2.0), (open_w, d, header)))
    lo = [1e9, 1e9, 1e9]
    hi = [-1e9, -1e9, -1e9]
    for c, s in boxes:
        for i in range(3):
            lo[i] = min(lo[i], c[i] - s[i] / 2.0)
            hi[i] = max(hi[i], c[i] + s[i] / 2.0)
    return tuple(lo), tuple(hi)


def test_counter_and_frame_tile_the_exact_envelope():
    for (w, d, h) in [(2.0, 0.5, 3.0), (3.5, 0.6, 3.2), (1.2, 0.4, 2.6)]:
        lo, hi = _structure_bbox(w, d, h, {"counter_h": 1.1, "post": 0.1,
                                           "header": 0.2})
        assert _approx(hi[0] - lo[0], w)
        assert _approx(hi[1] - lo[1], d)
        assert _approx(hi[2] - lo[2], h)
        assert _approx((lo[0] + hi[0]) / 2, 0.0)   # centered on x
        assert _approx((lo[2] + hi[2]) / 2, 0.0)   # centered on z


def test_teller_line_plan_is_exact_fit_and_centered():
    g = genome.load_species("teller_line")
    m = {"type": "teller_line", "species": "teller_line", "state": None,
         "width_cm": 200, "fit": "exact", "dims": [2.0, 0.5, 3.0],
         "pivot": "center", "stem": "teller_line_delco_01_w200"}
    plan = dna.resolve_module_plan(m, g, "delco", 1, TOOL_VERSION)
    assert plan["pivot"] == "center" and plan["fit_exact"] is True
    assert plan["target_dims"] == {"width": 2.0, "depth": 0.5, "height": 3.0}
    assert plan["module"]["stem"] == "teller_line_delco_01_w200"
    lo, hi = _structure_bbox(2.0, 0.5, 3.0, plan["params"])
    facts = {"dimensions": {"width": round(hi[0] - lo[0], 4),
                            "depth": round(hi[1] - lo[1], 4),
                            "height": round(hi[2] - lo[2], 4)},
             "tris": 150, "parts": list(plan["parts"]), "has_uvs": True,
             "has_wear_colors": True, "materials": ["M_TellerLine_metal"],
             "has_collision": True, "unapplied_transforms": []}
    report = validate.evaluate(facts, g, plan, {"collision": True})
    assert report["status"] == "pass", validate.summarize(report)


TELLER = {"id": "b:if:t1", "kind": "teller_window",
          "states": ["intact", "shattered"], "default": "intact",
          "collision_per_state": {"intact": True, "shattered": False}}


def test_teller_slot_builds_intact_and_defers_shattered():
    plan = kit.plan_kit({"building_id": "b", "slots": [
        {"role": "teller_line", "size_mod": "full",
         "fit": {"dims": [2.0, 0.5, 3.0], "pivot": "center"},
         "interactive": TELLER}]})
    stems = {m["stem"]: m for m in plan["modules"]}
    assert stems["teller_line_delco_01_w200"]["species"] == "teller_line"
    assert "teller_line_delco_01_w200_shattered" not in stems  # deferred
    deferred = {d["stem"] for d in plan["deferred_variants"]}
    assert "teller_line_delco_01_w200_shattered" in deferred
