"""1.82.0 and 1.83.0 -- the crew's getaway van (roadmap 206).

The walker, 2026-10-07: "a Box Truck. Like a Chevrolet P30. Matte
Black....faded, with patina, like a worn in truck...that's been on many
jobs", parked at the mission's spawn. Pure half (`core/van_forms.py`): the
van fills its slot exactly, its parts stand in a step van's order at every
genome corner, the wheels sit in their arches and on the ground, the crew's
door is wider than the crew, and the finish reads black first and faded
second -- rust low on the sides, never on the roof, one primer patch on the
kerb side -- in the genome's own colour, the same van every time. The
recipe read as source: one paint material, the plan's kind and colour.

1.83.0, on the walker's first look (2026-10-08): the glass stops a header
under the roof; a chassis hangs under the body, swept for shared planes at
every centimetre of height the genome allows and clear of every tyre; and
the ghost of SKEEVY'S WOODER ICE keeps a white margin, reads the right way
round on both sides and stays off the primer patch -- every step van's
since 1.84.0 ("make the ghost the default, patchy version"). Built half
(bpy, skipped without it): PASS and an exact fit, five submissions, the
paint in the vertex, the chassis on the paint, the ghost's art under the
`Wear` colour with both exported, the same file every build.
"""
from __future__ import annotations

import ast
import itertools
import math
import os
import re
import statistics
import struct
import zlib

import pytest

from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P
from zoo_keeper.core import skins
from zoo_keeper.core import van_forms as V

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "step_van.py")
_MATERIALS = os.path.join(_ZOO, "zoo_keeper", "bpylayer", "materials.py")


def _g():
    return genome_mod.load_species("step_van")


def _corners():
    r = _g()["dimensions"]
    return [tuple(c) for c in itertools.product(
        *((r[a]["min"], r[a]["default"], r[a]["max"]) for a in ("width", "depth", "height")))]


CORNERS = _corners()

#: MEASURED in Blender 5.1.1 on the recipe as shipped: `tools/coplanar_probe.py
#: --species step_van --dims W D H` at the genome's corners and three sizes
#: between them, and `tools/coplanar_census.py --species step_van` at the
#: corners ("3 builds, 0 with coincident pairs, 0 that did not build").
#: Triangles and coincident pairs within the probe's 2 mm.
#:   1.82.0 (2026-10-07): 4,640 / 4,860 / 5,080 at the corners, 4,662 / 4,948
#:   / 5,058 between, 0 pairs. The first probe read 10-12 pairs a build; each
#:   was moved at its source (`van_forms.CAB_ROOF_INSET`, the recipe's notes).
#:   1.83.0 (2026-10-08), the chassis added: 512 triangles more at every size,
#:   0 pairs. Its first build read 1-2 pairs at the corners; the next, three
#:   more at sizes BETWEEN them -- a rail hung from the body's floor met the
#:   front axle's top within 1.8 mm near a 3.0 m slot, where no corner looks.
#:   `test_nothing_under_the_body_shares_a_plane` sweeps the heights for that.
MEASURED = {(2.4, 6.0, 2.9): (5152, 0), (2.6, 6.8, 3.05): (5372, 0),
            (2.8, 7.6, 3.3): (5592, 0), (2.5, 6.4, 3.0): (5174, 0),
            (2.7, 7.2, 3.2): (5460, 0), (2.45, 7.5, 2.95): (5570, 0)}

#: The crew's body radius, `characters.player.radius_m` in Deli Counter's
#: agent_contract.json. Pinned as a literal: Zoo does not read that contract.
CREW_RADIUS = 0.35


def _lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _side_and_roof(lay, base=V.BASE):
    """Luminance over the box's +X side (sill to roof) and its roof, on a
    5 cm grid, and the red excess (r - b) on the roof and low on the side."""
    hw, zr, zs = lay["hw"], lay["z_roof"], lay["z_sill"]
    ys = [lay["y_cab"] + 0.02 + k * 0.05 for k in range(int((lay["y_r"] - lay["y_cab"]) / 0.05))]
    zs_ = [zs + k * 0.05 for k in range(int((zr - zs) / 0.05))]
    xs = [-hw + 0.1 + k * 0.1 for k in range(int(2 * hw / 0.1) - 1)]
    side, roof, rb_roof, rb_low = [], [], [], []
    for y in ys:
        for z in zs_:
            c = V.finish_rgb((hw, y, z), (1.0, 0.0, 0.0), lay, base)
            side.append(_lum(c))
            if z < zs + 0.35:
                rb_low.append(c[0] - c[2])
        for x in xs:
            c = V.finish_rgb((x, y, zr), (0.0, 0.0, 1.0), lay, base)
            roof.append(_lum(c))
            rb_roof.append(c[0] - c[2])
    return side, roof, rb_roof, rb_low


# --------------------------------------------------------------------------- #
# The pure half: where the parts stand
# --------------------------------------------------------------------------- #

def test_the_genome_validates_and_names_every_part_the_recipe_builds():
    g = _g()
    assert genome_mod.validate_genome(g) == []
    assert g["license"]["construction_knowledge"] == "CC0"
    parts = set(g["parts"])
    src = open(_RECIPE, encoding="utf-8").read()
    named = set(re.findall(r'"(StepVan_[A-Za-z]+)"', src))
    named |= {n.rstrip("_") for n in re.findall(r'"(StepVan_[A-Za-z]+_)"', src)}
    assert named and named <= parts, sorted(named - parts)
    assert g.get("module_variants", 1) == 1    # one van: the ghost is its own (1.84.0)


@pytest.mark.parametrize("dims", CORNERS)
def test_the_slot_is_exact(dims):
    """Width is the mirror heads, depth the bumpers, height the clearance
    lamps: the slot the greybox site hands Laser Tag is the van."""
    W, L, H = dims
    lay = V.layout(W, L, H)
    assert abs(2.0 * (lay["hw"] + V.MIRROR_OUT) - W) < 1e-9
    assert abs((lay["yt"] - lay["y0"]) - L) < 1e-9
    assert abs((lay["z_roof"] + V.ROOF_LAMP) - H) < 1e-9


@pytest.mark.parametrize("dims", CORNERS)
def test_the_parts_stand_in_a_step_vans_order(dims):
    lay = V.layout(*dims)
    ys = [lay[k] for k in ("y0", "y_n", "y_ws", "y_wt", "y_cab", "y_r", "yt")]
    assert ys == sorted(ys) and len(set(ys)) == len(ys), ys
    zs = [lay[k] for k in ("z_sill", "z_arch", "z_nose", "z_belt", "z_head", "z_roof")]
    assert zs == sorted(zs) and len(set(zs)) == len(zs), zs
    # a longer slot is a longer box behind the same cab
    assert lay["y_cab"] - lay["y_n"] == pytest.approx(V.NOSE_LEN + V.CAB_LEN)
    assert lay["y_r"] - lay["y_cab"] > V.CAB_LEN


@pytest.mark.parametrize("dims", CORNERS)
def test_the_glass_stops_a_header_under_the_roof(dims):
    """The walker, 2026-10-08: "the windows in the front feel proportionally
    a little too tall". 1.82.0's glass ran to 0.10 m under the roof, a header
    0.07-0.08 of the glass's height; the P30 comp carries 0.25-0.30 m. Now
    0.196-0.230 of it."""
    lay = V.layout(*dims)
    assert lay["z_roof"] - lay["z_head"] == pytest.approx(V.HEADER)
    assert V.HEADER >= 0.25
    assert V.HEADER / (lay["z_head"] - lay["z_belt"]) >= 0.19


@pytest.mark.parametrize("dims", CORNERS)
def test_the_wheels_sit_in_their_arches(dims):
    lay = V.layout(*dims)
    r, A = lay["r"], lay["arch"]
    assert lay["y_n"] < lay["ya_f"] - A and lay["ya_f"] + A < lay["y_cab"]
    assert lay["y_cab"] < lay["ya_r"] - A and lay["ya_r"] + A < lay["y_r"]
    assert A - r >= 0.10 and lay["z_arch"] - 2.0 * r >= 0.05


@pytest.mark.parametrize("seg", range(10, 21))
def test_the_tread_touches_the_ground_at_any_wheel_count(seg):
    """`_lathe_x` sets a vertex every 360/seg degrees from the axle's level.
    At the default 14 an axle at r floated the built van 10.3 mm."""
    r = 0.41
    za = V.axle_height(r, seg)
    lowest = min(za + r * math.sin(2.0 * math.pi * k / seg) for k in range(seg))
    assert abs(lowest) < 1e-12, (seg, lowest)
    assert (za == pytest.approx(r)) == (seg % 4 == 0), (seg, za)


@pytest.mark.parametrize("dims", CORNERS)
def test_the_crews_door_is_wider_than_the_crew(dims):
    """The kerb-side door, between the front arch and the bulkhead: where
    the crew gets in and out (`ATT_side_door`)."""
    lay = V.layout(*dims)
    assert lay["ya_f"] + lay["arch"] < lay["y_door0"] < lay["y_door1"] < lay["y_cab"]
    assert lay["y_door1"] - lay["y_door0"] >= 2.0 * CREW_RADIUS


@pytest.mark.parametrize("dims", CORNERS)
def test_the_primer_patch_is_on_the_kerb_side_of_the_box(dims):
    lay = V.layout(*dims)
    px, py, pz, prad = lay["primer"]
    assert px < 0.0
    assert lay["y_cab"] < py - prad and py + prad < lay["y_r"]
    assert lay["z_sill"] < pz - 0.7 * prad


# --------------------------------------------------------------------------- #
# The pure half: the chassis
# --------------------------------------------------------------------------- #

def _body_proxies(lay):
    """The body's planes the chassis meets, as the recipe draws them: the
    box's bottom and front cap, the cab's bottom and rear cap, the bumpers.
    Their arch cut-outs are left out, which can only add faces to collide
    with, never hide one."""
    hw, zs, ci = lay["hw"], lay["z_sill"], V.CAB_INSET
    return [P.box("proxy_box", "body", (-hw, lay["y_cab"], zs), (hw, lay["y_r"], zs + 0.5)),
            P.box("proxy_cab", "body", (-(hw - ci), lay["y_n"], zs + 0.006),
                  (hw - ci, lay["y_cab"] + 0.06, zs + 0.5)),
            P.box("proxy_bumper_front", "trim", (-(hw - 0.05), lay["y0"], 0.38),
                  (hw - 0.05, lay["y_n"] + 0.05, zs + 0.04)),
            P.box("proxy_bumper_rear", "trim", (-(hw - 0.05), lay["y_r"] - 0.05, 0.40),
                  (hw - 0.05, lay["yt"], zs + 0.04))]


SWEEP_H = [round(2.90 + 0.01 * k, 2) for k in range(41)]


@pytest.mark.parametrize("h", SWEEP_H)
def test_nothing_under_the_body_shares_a_plane(h):
    """`prims.coincident_pairs` -- the probe's own measurement -- over the
    chassis and the body's planes at every centimetre of height, three
    lengths, two widths and three wheel counts. Six probed sizes passed
    while three pairs sat between them (MEASURED's note)."""
    for w in (2.4, 2.8):
        for length in (6.0, 6.8, 7.6):
            lay = V.layout(w, length, h)
            for seg in (10, 14, 20):
                pr = V.chassis(lay, V.axle_height(lay["r"], seg)) + _body_proxies(lay)
                rows = [r for r in P.coincident_pairs(pr, tol=0.0022)
                        if not (r["a"].startswith("proxy_") and r["b"].startswith("proxy_"))]
                assert rows == [], (w, length, h, seg, rows[:3])


def _tyres(lay):
    """Each tyre as (centre x, axle y): it spans x +/- tyre_w / 2 and the
    radii 0.62 r .. r about (axle y, axle z), as the recipe lathes it."""
    hw, tw = lay["hw"], lay["tyre_w"]
    xo = hw - 0.03
    out = []
    for ya, inner in ((lay["ya_f"], False), (lay["ya_r"], True)):
        for s in (-1.0, 1.0):
            cx = s * (xo - tw / 2.0)
            out.append((cx, ya))
            if inner:
                out.append((cx - s * (tw + 0.02), ya))
    return out


@pytest.mark.parametrize("dims", CORNERS)
def test_nothing_under_the_body_cuts_a_tyre(dims):
    """A part beside a tyre misses its band in x; one through it stays inside
    the hollow (the axles) or outside the tread, judged on its bounding
    rectangle in YZ, which can only overstate it."""
    lay = V.layout(*dims)
    r, tw = lay["r"], lay["tyre_w"]
    za = V.axle_height(r, 14)
    for p in V.chassis(lay, za):
        xs = [v[0] for v in p["verts"]]
        ys = [v[1] for v in p["verts"]]
        zs = [v[2] for v in p["verts"]]
        for cx, ya in _tyres(lay):
            if max(xs) <= cx - tw / 2.0 or min(xs) >= cx + tw / 2.0:
                continue
            near = math.hypot(max(min(ys) - ya, 0.0, ya - max(ys)), max(min(zs) - za, 0.0, za - max(zs)))
            far = max(math.hypot(y - ya, z - za) for y in (min(ys), max(ys)) for z in (min(zs), max(zs)))
            assert far < 0.62 * r or near > r, (p["part"], cx, ya, near, far)


def _part(prims, name):
    got = [p for p in prims if p["part"] == name]
    assert len(got) == 1, (name, len(got))
    return got[0]


def _bounds(p):
    return ([min(v[k] for v in p["verts"]) for k in range(3)],
            [max(v[k] for v in p["verts"]) for k in range(3)])


@pytest.mark.parametrize("dims", CORNERS)
def test_the_chassis_is_where_a_step_vans_is(dims):
    """Inside the slot and off the ground; the driveshaft from inside the
    transmission to inside the pinion's nose; the differential between the
    inner tyres; the tailpipe out under the road side; the tank on the kerb
    side; the rails into both bumpers."""
    W, L, H = dims
    lay = V.layout(W, L, H)
    za = V.axle_height(lay["r"], 14)
    pr = V.chassis(lay, za)
    for p in pr:
        lo, hi = _bounds(p)
        assert -W / 2.0 <= lo[0] and hi[0] <= W / 2.0, p["part"]
        assert lay["y0"] <= lo[1] and hi[1] <= lay["yt"], p["part"]
        assert lo[2] >= 0.15 and hi[2] <= lay["z_sill"] + 0.03, p["part"]
    shaft = _part(pr, "driveshaft")["verts"]
    n = len(shaft) // 2
    ends = [tuple(sum(v[k] for v in ring) / n for k in range(3)) for ring in (shaft[:n], shaft[n:])]
    for end, holder in zip(ends, ("transmission", "pinion")):
        lo, hi = _bounds(_part(pr, holder))
        assert all(lo[k] < end[k] < hi[k] for k in range(3)), (holder, end, lo, hi)
    xo, tw = lay["hw"] - 0.03, lay["tyre_w"]
    inner_face = xo - 2.0 * tw - 0.02
    lo, hi = _bounds(_part(pr, "differential"))
    assert max(abs(lo[0]), abs(hi[0])) < inner_face
    lo, hi = _bounds(_part(pr, "tail_out"))
    assert hi[0] >= lay["hw"] - 0.06 and hi[2] < lay["z_sill"]
    assert _bounds(_part(pr, "fuel_tank"))[1][0] < 0.0
    for side in ("kerb", "road"):
        lo, hi = _bounds(_part(pr, "rail_" + side))
        assert lay["y0"] < lo[1] < lay["y_n"] + 0.05 and lay["y_r"] - 0.05 < hi[1] < lay["yt"]


def test_the_chassis_is_painted_as_grime_and_the_exhaust_as_rust():
    lay = V.layout(2.6, 6.8, 3.05)
    pr = V.chassis(lay, V.axle_height(lay["r"], 14))
    assert {p["mat"] for p in pr} == {"frame", "exhaust"}
    assert {p["part"] for p in pr if p["mat"] == "exhaust"} == {
        "downpipe", "pipe", "muffler", "tailpipe", "tail_out"}
    pts = [(x * 0.1, y * 0.37, z * 0.05) for x in range(-5, 6) for y in range(-9, 10) for z in range(4, 12)]
    frame = [V.chassis_rgb(p, (0.0, 0.0, -1.0), "frame") for p in pts]
    rust = [V.chassis_rgb(p, (0.0, 0.0, -1.0), "exhaust") for p in pts]
    assert max(_lum(c) for c in frame) < 0.10
    assert min(c[0] - c[2] for c in rust) > 0.04 > max(c[0] - c[2] for c in frame)


def test_a_rod_at_phase_zero_is_the_rod_it_always_was():
    """`prims.rod` gained `phase` (1.83.0); every caller before it passes none."""
    a = P.rod("x", "m", (0.0, 0.0, 0.0), (0.0, 1.0, 0.1), 0.05, segments=8)
    b = P.rod("x", "m", (0.0, 0.0, 0.0), (0.0, 1.0, 0.1), 0.05, segments=8, phase=0.0)
    assert a == b
    assert a["verts"][0] == pytest.approx((0.05, 0.0, 0.0))


@pytest.mark.parametrize("n", (6, 8, 10, 12))
def test_a_turned_rod_has_no_facet_square_to_an_axis(n):
    for p1 in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)):
        pr = P.rod("x", "m", (0.0, 0.0, 0.0), p1, 0.05, segments=n, phase=math.pi / (2 * n))
        for f in pr["faces"][2:]:                     # [0] and [1] are the caps
            a, b, c = (pr["verts"][i] for i in f[:3])
            u = [b[k] - a[k] for k in range(3)]
            w = [c[k] - a[k] for k in range(3)]
            nrm = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
            ln = math.sqrt(sum(x * x for x in nrm))
            assert all(abs(abs(x / ln) - 1.0) > 1e-6 for x in nrm), (n, p1, nrm)


# --------------------------------------------------------------------------- #
# The pure half: the finish
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("dims", CORNERS)
def test_the_van_reads_black_first_and_faded_second(dims):
    """Half the side darker than 0.06 linear (measured 0.051-0.053), the
    roof's sun-chalk at least 1.3 times that (measured 0.078-0.080). The
    first draft chalked the sides linearly and read as a mid-grey van."""
    side, roof, _rb_roof, _rb_low = _side_and_roof(V.layout(*dims))
    med = statistics.median(side)
    assert med < 0.06, med
    assert statistics.mean(roof) > 1.3 * med, (statistics.mean(roof), med)


@pytest.mark.parametrize("dims", CORNERS)
def test_rust_blooms_low_on_the_sides_and_never_on_the_roof(dims):
    _side, _roof, rb_roof, rb_low = _side_and_roof(V.layout(*dims))
    assert max(rb_roof) <= 0.01, max(rb_roof)
    assert max(rb_low) >= 0.10, max(rb_low)


@pytest.mark.parametrize("dims", CORNERS)
def test_the_primer_shows_on_the_kerb_side_only(dims):
    lay = V.layout(*dims)
    hw = lay["hw"]
    _px, py, pz, _pr = lay["primer"]
    kerb = _lum(V.finish_rgb((-hw, py, pz), (-1.0, 0.0, 0.0), lay))
    road = _lum(V.finish_rgb((hw, py, pz), (1.0, 0.0, 0.0), lay))
    assert kerb > 0.15 and road < 0.06, (kerb, road)


def test_the_finish_is_the_same_van_every_time():
    lay = V.layout(2.6, 6.8, 3.05)
    pts = [((x, y, z), n) for x in (-1.15, 1.15) for y in (-3.0, -1.0, 0.5, 2.5)
           for z in (0.3, 0.7, 1.2, 2.4, 2.99)
           for n in ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0))]
    a = [V.finish_rgb(p, n, lay) for p, n in pts]
    b = [V.finish_rgb(p, n, lay) for p, n in pts]
    assert a == b
    assert all(0.0 <= V.vnoise(x * 0.37, x * 0.91, s) <= 1.0 for x in range(-40, 40) for s in range(5))


def test_the_genome_colour_is_the_paint():
    """BASE is the genome's style colour and the recipe passes the plan's in,
    so editing the genome repaints the van; the chalk derives from it."""
    styles = _g()["styles"]
    style = styles["default"]
    assert tuple(style["color"]) == pytest.approx(V.BASE, abs=1e-9)
    assert style["material"] == _g()["materials"]["default"] == "paint_matte"
    # the crew's van is the same van in every theme: `delco` is there so
    # `delco_1997` resolves (test_theme_style_resolution.py), not to differ
    assert all(s == style for s in styles.values()), sorted(styles)
    assert V.chalk(V.BASE) == pytest.approx((0.100, 0.096, 0.092), abs=1e-9)
    lay = V.layout(2.6, 6.8, 3.05)
    red = V.finish_rgb((lay["hw"], 1.0, 1.6), (1.0, 0.0, 0.0), lay, (0.5, 0.05, 0.05))
    assert red[0] > 2.0 * red[1] and red[0] > 2.0 * red[2], red


def _dict_value(path, name, key):
    tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
            raise AssertionError("%s has no %r" % (name, key))
    raise AssertionError("no module-level %s in %s" % (name, path))


def test_paint_matte_is_a_known_matte_dielectric():
    """Read off materials.py with `ast`: it imports bpy at module scope."""
    assert "paint_matte" in skins.KNOWN_KINDS
    assert _dict_value(_MATERIALS, "ROUGHNESS", "paint_matte") >= 0.8
    assert _dict_value(_MATERIALS, "METALLIC", "paint_matte") == 0.0


def test_the_recipe_paints_one_material_in_the_plans_kind_and_colour():
    """The draw-call rule: the van's colour varies per corner in `Wear`,
    never as a material per colour, and the genome's kind and colour are
    what the body is drawn in (a recipe that hard-codes them makes the
    genome inert). The paint carries the ghost's one image under the same
    kind; it adds no material."""
    src = open(_RECIPE, encoding="utf-8").read()
    assert 'plan["material"]' in src and 'plan["color"]' in src
    assert "geometry.tint_wear_by(" in src and "van_forms.finish_rgb(" in src
    made = re.findall(r'make_material\(\s*(f?)"([^"]+)"', src)
    assert sorted(n for _f, n in made) == ["M_Van_interior", "M_Van_painted",
                                          "M_Van_rubber"], made
    assert not any(f for f, _n in made), "a material name built from a value"
    assert re.search(r'make_see_through_material\(\s*"M_Van_glass"', src)
    assert re.search(r'make_wear_textured_material\(\s*"M_Van_paint"', src)
    assert "van_forms.chassis(" in src and "van_forms.ghost_uv(" in src


def test_the_measured_builds_are_clean_and_inside_the_budget():
    budget = _g()["budgets"]["tris_lod0"]
    r = _g()["dimensions"]
    for (w, d, h), (tris, pairs) in MEASURED.items():
        assert r["width"]["min"] <= w <= r["width"]["max"]
        assert r["depth"]["min"] <= d <= r["depth"]["max"]
        assert r["height"]["min"] <= h <= r["height"]["max"]
        assert pairs == 0 and tris <= budget, ((w, d, h), tris, pairs)


# --------------------------------------------------------------------------- #
# The pure half: the ghost
# --------------------------------------------------------------------------- #

_ART = {}


def _art():
    if not _ART:
        _ART.update(V.ghost_art())
    return _ART


def _png_rows(png):
    """Canvas.png's own layout read back: one IDAT, filter 0 on every row."""
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    i, idat, w, h = 8, b"", 0, 0
    while i < len(png):
        n = struct.unpack(">I", png[i:i + 4])[0]
        tag, data = png[i + 4:i + 8], png[i + 8:i + 8 + n]
        if tag == b"IHDR":
            w, h = struct.unpack(">II", data[:8])
        elif tag == b"IDAT":
            idat += data
        i += 12 + n
    raw = zlib.decompress(idat)
    stride = 3 * w + 1
    assert all(raw[r * stride] == 0 for r in range(h))
    return w, h, [raw[r * stride + 1:(r + 1) * stride] for r in range(h)]


def test_the_ghost_sets_every_line_and_keeps_a_white_margin():
    """A face sent past the art's corner reads the clamped edge, so every
    edge pixel must be white or the whole van would darken; the letters
    never go darker than `GHOST_INK` (the patching only lightens them)."""
    art = _art()
    w, h, rows = _png_rows(art["png"])
    assert (w, h) == V.GHOST_PX == art["size"]
    assert len(art["lines"]) == len(V.GHOST_LINES)
    edge = rows[0] + rows[-1] + bytes(b for r in rows for b in (r[0:3] + r[-3:]))
    assert set(edge) == {255}
    darkest = min(min(r) for r in rows)
    assert V._srgb8(V.GHOST_INK) - 1 <= darkest < 230, darkest
    assert art["name"] == V.ghost_art()["name"]


def test_the_ghost_maps_the_sides_and_nothing_else():
    lay = V.layout(2.6, 6.8, 3.05)
    hw = lay["hw"]
    yc, zc = V.ghost_centre(lay)
    assert V.ghost_uv((hw, yc, zc), (1.0, 0.0, 0.0), lay) == pytest.approx((0.5, 0.5))
    assert V.ghost_uv((-hw, yc, zc), (-1.0, 0.0, 0.0), lay) == pytest.approx((0.5, 0.5))
    for nrm in ((0.0, 0.0, 1.0), (0.0, -1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, -1.0)):
        assert V.ghost_uv((0.0, yc, zc), nrm, lay) == V.GHOST_OUTSIDE
    # read from outside, the art's left is the front on the road side (+X)
    # and the rear on the kerb side (-X): neither side is a mirror image
    road = [V.ghost_uv((hw, y, zc), (1.0, 0.0, 0.0), lay)[0] for y in (yc - 1.0, yc + 1.0)]
    kerb = [V.ghost_uv((-hw, y, zc), (-1.0, 0.0, 0.0), lay)[0] for y in (yc - 1.0, yc + 1.0)]
    assert road[0] < road[1] and kerb[0] > kerb[1]


@pytest.mark.parametrize("dims", CORNERS)
def test_the_ghost_stays_on_the_box_and_off_the_primer(dims):
    """Every line's ink inside the box's flat side -- behind the bulkhead,
    ahead of the rear doors, under the roof's round -- and, on the kerb side,
    clear of the primer at its widest (`finish_rgb`'s edge noise can push
    it out to sqrt(1.225) of its radii)."""
    lay = V.layout(*dims)
    art = _art()
    W, H = art["size"]
    sy, sz = V.GHOST_SPAN
    yc, zc = V.ghost_centre(lay)
    _px, py, pz, prad = lay["primer"]
    k = math.sqrt(1.225)
    for x0, y0, x1, y1 in art["lines"]:
        z_top, z_bot = zc + (0.5 - y0 / H) * sz, zc + (0.5 - y1 / H) * sz
        u0, u1 = x0 / W - 0.5, x1 / W - 0.5
        for (ya, yb), kerb in (((yc + u0 * sy, yc + u1 * sy), False), ((yc - u1 * sy, yc - u0 * sy), True)):
            assert lay["y_cab"] + 0.05 < ya < yb < lay["y_r"] - 0.05, (dims, ya, yb)
            assert lay["z_sill"] + 0.3 < z_bot < z_top < lay["z_roof"] - V.ROOF_ROUND, (dims, z_bot, z_top)
            if kerb:
                clear = (yb < py - prad * k or ya > py + prad * k
                         or z_bot > pz + 0.7 * prad * k or z_top < pz - 0.7 * prad * k)
                assert clear, (dims, (ya, yb, z_bot, z_top), (py, pz, prad))


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, dims):
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "getaway_van", "role": "prop", "size_mod": "full", "style": 1,
            "species": "step_van", "fit": {"dims": list(dims), "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == [], plan["dressing_fallbacks"]
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES)), key=lambda o: o.name)
    return res, objs


def _glb(path):
    """``(json, bin)`` of a GLB."""
    import json
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    doc = json.loads(raw[20:20 + n])
    b = 20 + n
    bn = struct.unpack("<I", raw[b:b + 4])[0]
    return doc, raw[b + 8:b + 8 + bn]


def _accessor(doc, binc, i):
    a = doc["accessors"][i]
    bv = doc["bufferViews"][a["bufferView"]]
    fmt, size = {5126: ("f", 4), 5123: ("H", 2), 5121: ("B", 1)}[a["componentType"]]
    nc = {"VEC2": 2, "VEC3": 3, "VEC4": 4, "SCALAR": 1}[a["type"]]
    stride = bv.get("byteStride") or size * nc
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    rows = []
    for k in range(a["count"]):
        vals = struct.unpack("<" + fmt * nc, binc[base + k * stride:base + k * stride + size * nc])
        if a.get("normalized"):
            vals = tuple(v / (65535.0 if fmt == "H" else 255.0) for v in vals)
        rows.append(vals)
    return rows


@pytest.mark.parametrize("dims", [CORNERS[0], (2.6, 6.8, 3.05), CORNERS[-1]])
def test_bpy_the_van_passes_and_fills_its_slot(tmp_path, dims):
    """Fit to the millimetre: before `axle_height` the default build stood
    3.040 m in its 3.05 m slot and this failed."""
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    parts = set(_g()["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name


def test_bpy_five_submissions_and_one_paint(tmp_path):
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, (2.6, 6.8, 3.05))
    doc, _b = _glb(os.path.join(str(tmp_path), res["files"]["glb"]))
    mats = {m["name"]: m for m in doc["materials"]}
    assert sorted(mats) == ["M_Van_glass", "M_Van_interior", "M_Van_paint",
                            "M_Van_painted", "M_Van_rubber"], sorted(mats)
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 5, [m["name"] for m in visual]
    assert mats["M_Van_glass"].get("alphaMode") == "BLEND"
    pbr = mats["M_Van_paint"]["pbrMetallicRoughness"]
    assert pbr["roughnessFactor"] == pytest.approx(0.86) and pbr.get("metallicFactor", 1.0) == 0
    assert "baseColorTexture" in pbr      # the ghost's art, every build (1.84.0)


def test_bpy_the_chassis_is_built_on_the_paint(tmp_path):
    """Every face `van_forms.chassis` plans arrives, on the body's material."""
    pytest.importorskip("bpy")
    dims = (2.6, 6.8, 3.05)
    _res, objs = _build(tmp_path, dims)
    lay = V.layout(*dims)
    pr = V.chassis(lay, V.axle_height(lay["r"], int(_g()["params"]["wheel_segments"]["default"])))
    for name, mat in (("StepVan_Chassis", "frame"), ("StepVan_Exhaust", "exhaust")):
        got = [o for o in objs if o.name == name]
        assert len(got) == 1, [o.name for o in objs]
        assert [m.name for m in got[0].data.materials] == ["M_Van_paint"]
        assert len(got[0].data.polygons) == sum(len(p["faces"]) for p in pr if p["mat"] == mat)


def test_bpy_the_ghost_ships_its_art_under_the_paint(tmp_path):
    """Every build (1.84.0): five submissions, the paint one image richer; the
    image AND the paint's per-corner colour both reach the GLB (a material
    that reads no vertex colour ships COLOR_0 white), and the box's sides
    sample the art while every other face samples its margin."""
    pytest.importorskip("bpy")
    from zoo_keeper.core import partnames
    res, _objs = _build(tmp_path, (2.6, 6.8, 3.05))
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    doc, binc = _glb(os.path.join(str(tmp_path), res["files"]["glb"]))
    mats = {m["name"]: m for m in doc["materials"]}
    assert sorted(mats) == ["M_Van_glass", "M_Van_interior", "M_Van_paint",
                            "M_Van_painted", "M_Van_rubber"], sorted(mats)
    assert "baseColorTexture" in mats["M_Van_paint"]["pbrMetallicRoughness"]
    assert [im["name"] for im in doc["images"]] == [V.ghost_art()["name"]]
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    assert sum(len(m["primitives"]) for m in visual) == 5
    names = [m["name"] for m in doc["materials"]]
    prim = [p for m in visual for p in m["primitives"] if names[p["material"]] == "M_Van_paint"]
    assert len(prim) == 1
    cols = _accessor(doc, binc, prim[0]["attributes"]["COLOR_0"])
    assert max(c[0] for c in cols) < 0.5, "COLOR_0 went out white"
    uvs = _accessor(doc, binc, prim[0]["attributes"]["TEXCOORD_0"])
    inside = sum(1 for u, v in uvs if 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0)
    assert 0 < inside < len(uvs)


def test_bpy_the_same_file_every_build(tmp_path):
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, (2.6, 6.8, 3.05))
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]


def test_bpy_the_paint_is_in_the_vertex(tmp_path):
    """The roof's corners chalked lighter than the side's, as built."""
    pytest.importorskip("bpy")
    _res, objs = _build(tmp_path, (2.6, 6.8, 3.05))
    body = [o for o in objs if o.name == "StepVan_Body"]
    assert len(body) == 1, [o.name for o in objs]
    mesh = body[0].data
    wear = mesh.color_attributes["Wear"].data
    up, side = [], []
    for poly in mesh.polygons:
        lums = [_lum(wear[li].color) for li in poly.loop_indices]
        if poly.normal[2] > 0.9:
            up.extend(lums)
        elif abs(poly.normal[0]) > 0.9:
            side.extend(lums)
    assert up and side
    assert statistics.mean(up) > statistics.median(side), (statistics.mean(up), statistics.median(side))
