"""safe_deposit_boxes module tests (pure -- no Blender).

A vault-room wall of deposit boxes: a solid backing + a capped bordered grid of
dividers. Tests: the backing defines the exact (w, d, h) envelope and dividers
stay inside; the grid is capped so a big wall stays low-poly; a slot's `drilled`
state defers to the intact base.
"""
from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, kit, validate


def _approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def _grid_count(usable, cell, cap):
    n = int(round(usable / cell)) if cell > 1e-6 else 1
    return max(1, min(n, int(cap)))


def _full_bbox(w, d, h, p):
    """Mirror the recipe's box extents (backing + dividers)."""
    back_d = d * 0.7
    front_d = d * 0.3
    fy = d / 2.0 - front_d / 2.0
    margin = min(p.get("margin", 0.06), min(w, h) * 0.3)
    uw = max(0.05, w - 2 * margin)
    uh = max(0.05, h - 2 * margin)
    cols = _grid_count(uw, p.get("cell", 0.22), p.get("max_cols", 16))
    rows = _grid_count(uh, p.get("cell", 0.22), p.get("max_rows", 16))
    cw, ch = uw / cols, uh / rows
    bar = p.get("bar", 0.03)
    boxes = [((0.0, -d / 2 + back_d / 2, 0.0), (w, back_d, h))]
    for i in range(cols + 1):
        boxes.append(((-uw / 2 + i * cw, fy, 0.0), (bar, front_d, uh)))
    for j in range(rows + 1):
        boxes.append(((0.0, fy, -uh / 2 + j * ch), (uw, front_d, bar)))
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for c, s in boxes:
        for i in range(3):
            lo[i] = min(lo[i], c[i] - s[i] / 2)
            hi[i] = max(hi[i], c[i] + s[i] / 2)
    return (tuple(lo), tuple(hi)), len(boxes)


def test_backing_defines_the_exact_envelope():
    for (w, d, h) in [(2.0, 0.3, 2.4), (3.6, 0.4, 3.0), (0.8, 0.2, 1.2)]:
        (lo, hi), _n = _full_bbox(w, d, h, {})
        assert _approx(hi[0] - lo[0], w)
        assert _approx(hi[1] - lo[1], d)   # backing rear + dividers front == d
        assert _approx(hi[2] - lo[2], h)
        assert _approx((lo[0] + hi[0]) / 2, 0.0)
        assert _approx((lo[2] + hi[2]) / 2, 0.0)


def test_grid_is_capped_so_a_big_wall_stays_low_poly():
    # a 5m x 3.6m wall at a tiny cell would be huge uncapped; the cap holds it.
    (_bb, n) = _full_bbox(5.0, 0.4, 3.6, {"cell": 0.05})
    # 1 backing + (cols+1) + (rows+1), cols/rows capped at 16 -> <= 1+17+17
    assert n <= 1 + 17 + 17
    tris = n * 12
    assert tris <= 1400          # within the genome budget


def test_plan_is_exact_fit_and_validates():
    g = genome.load_species("safe_deposit_boxes")
    m = {"type": "safe_deposit_boxes", "species": "safe_deposit_boxes",
         "state": None, "width_cm": 200, "fit": "exact",
         "dims": [2.0, 0.3, 2.4], "pivot": "center",
         "stem": "safe_deposit_boxes_delco_01_w200"}
    plan = dna.resolve_module_plan(m, g, "delco", 1, TOOL_VERSION)
    assert plan["pivot"] == "center" and plan["fit_exact"] is True
    (lo, hi), _n = _full_bbox(2.0, 0.3, 2.4, plan["params"])
    facts = {"dimensions": {"width": round(hi[0] - lo[0], 4),
                            "depth": round(hi[1] - lo[1], 4),
                            "height": round(hi[2] - lo[2], 4)},
             "tris": 400, "parts": list(plan["parts"]), "has_uvs": True,
             "has_wear_colors": True,
             "materials": ["M_SafeDepositBoxes_metal"], "has_collision": True,
             "unapplied_transforms": []}
    report = validate.evaluate(facts, g, plan, {"collision": True})
    assert report["status"] == "pass", validate.summarize(report)


def test_drilled_state_defers_to_intact_base():
    slot = {"role": "safe_deposit_boxes", "size_mod": "full",
            "fit": {"dims": [2.0, 0.3, 2.4], "pivot": "center"},
            "interactive": {"id": "b:if:s1", "kind": "safe_deposit_boxes",
                            "states": ["intact", "drilled"],
                            "default": "intact"}}
    plan = kit.plan_kit({"building_id": "b", "slots": [slot]})
    stems = {m["stem"] for m in plan["modules"]}
    assert "safe_deposit_boxes_delco_01_w200" in stems
    assert "safe_deposit_boxes_delco_01_w200_drilled" not in stems
    deferred = {d["stem"] for d in plan["deferred_variants"]}
    assert "safe_deposit_boxes_delco_01_w200_drilled" in deferred
