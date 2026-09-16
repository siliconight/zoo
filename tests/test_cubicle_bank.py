"""cubicle_bank: minted 2026-09-16 by tools/new_species.py (roadmap 150) and
shaped the same day.

The walker, cold run 9060, 2.68 m from `office_stepped`'s `cubicles_w_0_col`:
"these desks are too close to each other?". All ten `cubicle*` volumes in the
library are 8.0 x 6.0 x 1.2 m and all ten routed to `desk`, whose ranges
reach 12 x 6, so they FIT and built as desk geometry at that size. These
tests are about the layout arithmetic -- bands, aisle, bays -- which is pure
and needs no Blender; the geometry itself is checked by building the kit.
"""
from zoo_keeper.core import dna, genome, kit
from zoo_keeper.core import cubicle_forms as CB

#: The slot every one of the library's ten cubicle volumes emits, after
#: `prop_species.long_axis_first` (8.0 is already the long side, so it is
#: not turned).
LIBRARY = [8.0, 6.0, 1.2]


def test_cubicle_bank_is_discovered_and_validates():
    assert "cubicle_bank" in genome.list_species()
    assert genome.validate_genome(genome.load_species("cubicle_bank")) == []


def test_it_plans_at_the_dims_every_library_cubicle_is_authored_at():
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "cubicles_w_0", "role": "prop", "size_mod": "full",
        "style": 1, "species": "cubicle_bank", "material": "drywall",
        "fit": {"dims": LIBRARY, "pivot": "center"}}]},
        theme="delco_1997", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "cubicle_bank"


def test_the_library_slot_carries_an_aisle_a_body_fits_down():
    """`aisle_min` is Deli Counter's `min_corridor_width_m`, and the whole
    point of the species is that the bank has an aisle rather than being a
    raft of desk tops."""
    g = genome.load_species("cubicle_bank")
    p = g["params"]
    rows, aisle = CB.bands(6.0, p["row_min"], p["row_max"], p["aisle_min"])
    assert len(rows) == 2, rows
    assert abs(rows[0][1] - 2.4) < 1e-9 and abs(rows[1][1] - 2.4) < 1e-9, rows
    assert abs(aisle - 1.2) < 1e-9, aisle
    assert aisle >= p["aisle_min"]


def test_the_bands_always_fill_the_slots_depth_exactly():
    """The spines stand on the bank's own outer edges, so the built bounds
    are the slot's -- `validate.fit_depth` is exact to 2 cm and a band that
    stopped short would fail it."""
    g = genome.load_species("cubicle_bank")
    p = g["params"]
    for d in (1.6, 2.0, 3.0, 4.4, 4.5, 5.0, 6.0, 8.0, 12.0):
        rows, aisle = CB.bands(d, p["row_min"], p["row_max"], p["aisle_min"])
        lo = min(y - bd / 2.0 for y, bd in rows)
        hi = max(y + bd / 2.0 for y, bd in rows)
        assert abs(lo - -d / 2.0) < 1e-9 and abs(hi - d / 2.0) < 1e-9, (d, rows)
        assert abs((hi - lo) - (sum(bd for _y, bd in rows) + aisle)) < 1e-9


def test_a_depth_that_cannot_carry_an_aisle_gets_one_band_not_a_narrow_one():
    """Two bands at `row_min` plus `aisle_min` is 4.5 m. Below that a second
    band would either be too shallow to hold a desk or leave an aisle this
    pipeline's body does not fit down, so the bank is one band."""
    g = genome.load_species("cubicle_bank")
    p = g["params"]
    assert 2 * p["row_min"] + p["aisle_min"] == 4.5
    for d in (1.6, 3.0, 4.49):
        rows, aisle = CB.bands(d, p["row_min"], p["row_max"], p["aisle_min"])
        assert len(rows) == 1 and aisle == 0.0, (d, rows)
    rows, aisle = CB.bands(4.5, p["row_min"], p["row_max"], p["aisle_min"])
    assert len(rows) == 2 and abs(aisle - p["aisle_min"]) < 1e-9, (rows, aisle)


def test_the_screens_are_cloth_whatever_the_slot_says():
    """Every one of the library's ten volumes is authored `drywall`. On an
    UPHOLSTERED species that names the FRAME; the fabric stays the genome's."""
    assert dna.UPHOLSTERED["cubicle_bank"] == "cloth"
    g = genome.load_species("cubicle_bank")
    plan = dna.resolve_module_plan(
        {"type": "prop", "species": "cubicle_bank", "dims": LIBRARY,
         "fit": "exact", "material": "drywall", "width_cm": 800,
         "depth_cm": 600, "style": 1},
        g, "delco_1997", 1, "test")
    assert plan["upholstery"]["material"] == "cloth", plan["upholstery"]
    assert plan["upholstery"]["frame"] == "drywall", plan["upholstery"]


def test_every_bay_is_a_workstation_and_none_is_a_sliver():
    """`_bays` divides equally, so 8.0 m at `bay_max` 2.0 is four 2.0 m
    workstations and never three plus a stub."""
    from zoo_keeper.recipes._bays import bays
    g = genome.load_species("cubicle_bank")
    runs = bays(8.0, g["params"]["bay_max"])
    assert len(runs) == 4, runs
    assert all(abs(bw - 2.0) < 1e-9 for _bx, bw in runs), runs
    assert abs(min(bx - bw / 2 for bx, bw in runs) - -4.0) < 1e-9
    assert abs(max(bx + bw / 2 for bx, bw in runs) - 4.0) < 1e-9


def test_a_1p2m_bank_carries_no_overhead_bin_and_a_1p7m_one_does():
    """The reference's own rule: a binder bin needs a panel that reaches over
    it. It is not a toggle -- the height decides."""
    assert CB.BIN_Z + CB.BIN_H > 1.2 - CB.CAP_T
    assert CB.BIN_Z + CB.BIN_H <= 1.7 - CB.CAP_T


def _library_plan(variant=0):
    g = genome.load_species("cubicle_bank")
    return CB.plan(LIBRARY[0], LIBRARY[1], LIBRARY[2], g["params"], variant)


def test_the_built_plan_fills_the_slot_box_exactly():
    """`validate` gates a slot-fit module on its built bounds equalling the
    slot's dims to 2 cm, and `core.pivot` re-centres from those bounds -- so
    a plan short on any axis ships a bank floating off its slot."""
    lo, hi = CB.bounds(_library_plan()["boxes"])
    for i, want in enumerate(LIBRARY):
        assert abs((hi[i] - lo[i]) - want) < 1e-9, (i, lo, hi)
    assert abs(lo[0] - -4.0) < 1e-9 and abs(hi[0] - 4.0) < 1e-9
    assert abs(lo[1] - -3.0) < 1e-9 and abs(hi[1] - 3.0) < 1e-9
    assert abs(lo[2] - 0.0) < 1e-9 and abs(hi[2] - 1.2) < 1e-9


def test_nothing_the_species_builds_stands_in_the_aisle():
    """The measured complaint was a raft with no aisle. The aisle is the
    middle 1.2 m of the depth and it must be EMPTY -- not of low geometry,
    of any."""
    got = _library_plan()
    a0, a1 = -0.6, 0.6                       # 1.2 m aisle, centred
    for name, _key, c, s, _solid in got["boxes"]:
        assert c[1] - s[1] / 2.0 >= a1 - 1e-9 or c[1] + s[1] / 2.0 <= a0 + 1e-9, \
            (name, c, s)


def test_the_collision_it_declares_is_per_part_and_leaves_the_aisle_open():
    """The species' own collision, which is what `bpylayer.build` bakes into
    the module's `-colonly` mesh: screens, work surfaces, pedestals. Not one
    8 x 6 box, and nothing at all in the aisle."""
    got = _library_plan()
    solids = [b for b in got["boxes"] if b[4]]
    # 2 bands x (1 spine + 5 cross screens over 4 bays + 4 surfaces + 4
    # pedestals) = 28
    assert len(solids) == got["facts"]["solids"] == 28, len(solids)
    kinds = sorted({n.split("_")[1].rstrip("0123456789") for n, *_ in solids})
    assert kinds == ["Cross", "Pedestal", "Spine", "Surface"], kinds
    for name, _key, c, s, _k in solids:
        assert c[1] - s[1] / 2.0 >= 0.6 - 1e-9 or c[1] + s[1] / 2.0 <= -0.6 + 1e-9, name


def test_the_four_variants_are_four_different_banks():
    """`module_variants` is 4, and a variant that changed nothing but wear
    noise is one `kit.honour_dressing` refuses to carry."""
    assert genome.load_species("cubicle_bank")["module_variants"] == 4
    shapes = {v: tuple(sorted((n, c, s) for n, _k, c, s, _o
                              in _library_plan(v)["boxes"]))
              for v in range(4)}
    assert len(set(shapes.values())) == 4, sorted(shapes)


ALL = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

if __name__ == "__main__":
    for fn in ALL:
        fn()
        print(f"[ok] {fn.__name__}")
    print(f"\n{len(ALL)} cubicle_bank tests passed.")
