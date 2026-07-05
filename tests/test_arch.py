"""Architectural module tests (pure — no Blender).

Covers the fit-to-exact-dims + center-pivot guarantees that make Zoo a valid
Deli Counter art/zoo library: a module's outer footprint must equal the slot's
authored size exactly (DC never scales it), and validation must catch it if not.
"""
from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import arch, dna, genome, kit, validate

ARCH_SPECIES = ["wall", "wallEnd", "doorway", "window", "breach"]


def _approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


# --- core.arch: void + slab decomposition ----------------------------------

def test_solid_species_have_no_void():
    assert arch.void_for("wall", 2.0, 3.6) is None
    assert arch.void_for("wallEnd", 1.0, 1.0) is None


def test_opening_species_have_a_void_inside_the_footprint():
    for sp in ("doorway", "window", "breach"):
        v = arch.void_for(sp, 1.3, 2.2, {})
        assert v is not None
        # jambs always survive: the opening never reaches the width edges
        assert -0.65 < v["x0"] < v["x1"] < 0.65
        # and never below the floor or above the ceiling
        assert -1.1 - 1e-9 <= v["z0"] < v["z1"] <= 1.1 + 1e-9


def test_doorway_and_breach_openings_reach_the_floor():
    for sp in ("doorway", "breach"):
        v = arch.void_for(sp, 1.1, 2.2, {})
        assert _approx(v["z0"], -1.1)  # floor = -h/2


def test_window_opening_is_off_the_floor():
    v = arch.void_for("window", 1.3, 1.5, {})
    assert v["z0"] > -0.75 + 1e-6  # a sill remains below the glass


def test_solid_slab_is_one_exact_box():
    parts = arch.slab_parts(2.0, 0.3, 3.6, None)
    assert len(parts) == 1
    (lo, hi) = arch.parts_bbox(parts)
    assert _approx(hi[0] - lo[0], 2.0)
    assert _approx(hi[1] - lo[1], 0.3)
    assert _approx(hi[2] - lo[2], 3.6)


def test_every_module_footprint_is_exact():
    # this is the whole point: the union bbox must equal (w, d, h) so DC can
    # instance the module at the slot without scaling.
    for sp in ARCH_SPECIES:
        for (w, d, h) in [(2.0, 0.3, 3.6), (0.3, 0.3, 3.6), (1.1, 0.3, 2.2),
                          (1.3, 0.3, 1.5), (4.0, 0.4, 3.0)]:
            void = arch.void_for(sp, w, h, {})
            parts = arch.slab_parts(w, d, h, void)
            lo, hi = arch.parts_bbox(parts)
            assert _approx(hi[0] - lo[0], w), (sp, "width", w)
            assert _approx(hi[1] - lo[1], d), (sp, "depth", d)
            assert _approx(hi[2] - lo[2], h), (sp, "height", h)
            # centered on origin
            assert _approx((lo[0] + hi[0]) / 2, 0.0)
            assert _approx((lo[2] + hi[2]) / 2, 0.0)


def test_doorway_has_jambs_and_header_no_sill():
    parts = arch.slab_parts(1.1, 0.3, 2.1, arch.void_for("doorway", 1.1, 2.1))
    names = {n for n, _c, _s in parts}
    assert "Jamb_L" in names and "Jamb_R" in names and "Header" in names
    assert "Sill" not in names  # opening reaches the floor


def test_window_has_all_four_frame_boxes():
    parts = arch.slab_parts(1.3, 0.3, 1.5, arch.void_for("window", 1.3, 1.5))
    names = {n for n, _c, _s in parts}
    assert names == {"Jamb_L", "Jamb_R", "Sill", "Header"}


def test_collision_boxes_track_solid_parts_only():
    parts = arch.slab_parts(1.3, 0.3, 1.5, arch.void_for("window", 1.3, 1.5))
    boxes = arch.collision_boxes(parts)
    assert len(boxes) == len(parts)  # one per solid box; void gets none


def test_root_name_keeps_camelcase_wallend():
    assert arch.root_name("wallEnd") == "WallEnd"
    assert arch.root_name("wall") == "Wall"
    assert arch.root_name("doorway") == "Doorway"


# --- dna.resolve_module_plan ------------------------------------------------

def _module(typ, dims, width_cm, fit="exact"):
    return {"type": typ, "width_cm": width_cm, "fit": fit, "dims": dims,
            "pivot": "center",
            "stem": kit.module_stem(typ, "delco", 1, width_cm)}


def test_module_plan_uses_exact_dims_and_center_pivot():
    g = genome.load_species("wall")
    m = _module("wall", [2.0, 0.3, 3.6], 200)
    plan = dna.resolve_module_plan(m, g, "delco", 1, TOOL_VERSION)
    assert plan["dimensions"] == {"width": 2.0, "depth": 0.3, "height": 3.6}
    assert plan["pivot"] == "center"
    assert plan["fit_exact"] is True
    assert plan["target_dims"] == plan["dimensions"]
    assert plan["module"]["stem"] == "wall_delco_01_w200"
    # no size_hint / jitter — dims are verbatim (unlike resolve_plan)
    assert plan["dim_scale"] == {"width": 1.0, "depth": 1.0, "height": 1.0}


def test_module_plan_picks_theme_style_block_when_present():
    g = genome.load_species("wall")
    m = _module("wall", [2.0, 0.3, 3.6], 200)
    plan = dna.resolve_module_plan(m, g, "delco", 1, TOOL_VERSION)
    assert plan["style"] == "delco"  # genome has a 'delco' style block


def test_wallend_plan_is_unit_box():
    g = genome.load_species("wallEnd")
    m = {"type": "wallEnd", "width_cm": None, "fit": "unit",
         "dims": [1.0, 1.0, 1.0], "pivot": "center",
         "stem": "wallEnd_delco_01"}
    plan = dna.resolve_module_plan(m, g, "delco", 1, TOOL_VERSION)
    assert plan["dimensions"] == {"width": 1.0, "depth": 1.0, "height": 1.0}
    assert plan["fit_exact"] is False
    assert plan["module"]["stem"] == "wallEnd_delco_01"


def test_window_plan_carries_glass_color():
    g = genome.load_species("window")
    m = _module("window", [1.3, 0.3, 1.5], 130)
    plan = dna.resolve_module_plan(m, g, "delco", 1, TOOL_VERSION)
    assert "glass_color" in plan and len(plan["glass_color"]) == 3


# --- exact-fit validation (simulating the facts Blender would gather) -------

def _facts_for(plan, dims_override=None):
    dims = dims_override or dict(plan["dimensions"])
    return {"dimensions": dims, "tris": 120,
            "parts": list(plan["parts"]), "has_uvs": True,
            "has_wear_colors": True,
            "materials": ["M_Doorway_concrete"], "has_collision": True,
            "unapplied_transforms": []}


def test_exact_fit_passes_when_built_to_target():
    g = genome.load_species("doorway")
    m = _module("doorway", [1.1, 0.3, 2.2], 110)
    plan = dna.resolve_module_plan(m, g, "delco", 1, TOOL_VERSION)
    report = validate.evaluate(_facts_for(plan), g, plan, {"collision": True})
    assert report["status"] == "pass"
    ids = {c["id"] for c in report["checks"]}
    assert {"fit_width", "fit_depth", "fit_height"} <= ids


def test_exact_fit_fails_when_size_drifts():
    g = genome.load_species("doorway")
    m = _module("doorway", [1.1, 0.3, 2.2], 110)
    plan = dna.resolve_module_plan(m, g, "delco", 1, TOOL_VERSION)
    bad = _facts_for(plan, {"width": 1.25, "depth": 0.3, "height": 2.2})
    report = validate.evaluate(bad, g, plan, {"collision": True})
    assert report["status"] == "fail"
    fails = {c["id"] for c in report["checks"] if c["level"] == "fail"}
    assert "fit_width" in fails


def test_full_footprint_from_slab_validates_exact():
    # end-to-end (pure): plan a real slot, decompose it, and prove the measured
    # footprint validates as an exact fit — what Blender will reproduce.
    for typ, dims, wcm in [("wall", [2.0, 0.3, 3.6], 200),
                           ("doorway", [1.1, 0.3, 2.1], 110),
                           ("window", [1.3, 0.3, 1.5], 130),
                           ("breach", [1.2, 0.3, 2.4], 120)]:
        g = genome.load_species(typ)
        plan = dna.resolve_module_plan(_module(typ, dims, wcm), g, "delco", 1,
                                       TOOL_VERSION)
        parts = arch.slab_parts(dims[0], dims[1], dims[2],
                                arch.void_for(typ, dims[0], dims[2],
                                              plan["params"]))
        lo, hi = arch.parts_bbox(parts)
        measured = {"width": round(hi[0] - lo[0], 4),
                    "depth": round(hi[1] - lo[1], 4),
                    "height": round(hi[2] - lo[2], 4)}
        report = validate.evaluate(_facts_for(plan, measured), g, plan,
                                   {"collision": True})
        assert report["status"] == "pass", (typ, validate.summarize(report))


# --- integration with the existing species set -----------------------------

def test_arch_species_registered_without_breaking_prop_parsing():
    from zoo_keeper.core import intent
    species = set(genome.list_species())
    assert set(ARCH_SPECIES) <= species
    # the new keywords must not hijack a normal prop prompt
    assert intent.parse("1990s office desk with two drawers").species == "desk"
    assert intent.parse("a wall").species == "wall"
    assert intent.parse("wall end filler").species == "wallEnd"
