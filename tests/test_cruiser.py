"""1.86.0 -- the responders' cruiser (roadmap 212).

The walker, 2026-10-08: "I would think a classic 1990s Crown Victoria", and
"Delco County Police Dept. as a start?". Pure half (`core/cruiser_forms.py`
and the `cruiser` row of `core/car_forms.py`): the body is a Crown
Victoria's at its published sizes, the slot holds the body and its kit
exactly, the kit stands where a police car's does and on what it stands on,
the form is pinned (the same car every time), no two of the kit's faces
share a plane at any genome corner (the census's check, without Blender),
the partition stands between the seats and inside the doors, and the livery
-- one image -- maps the sides the right way round, keeps every other face
on its white patch, sets every line in both liveries, and keeps its marks
off the moulding and under the door handles on every door the genome
allows. The recipe and `simple_car`'s hooks, read as source: the body on
one livery material, the kit on the car's one painted material,
`simple_car`'s own cars drawn as they always were, and the cabin it returns
taken from the faces it built.
"""
from __future__ import annotations

import itertools
import os
import re
import struct
import zlib

import pytest

from zoo_keeper.core import car_forms as C
from zoo_keeper.core import cruiser_forms as CF
from zoo_keeper.core import genome as genome_mod

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "cruiser.py")
_SIMPLE_CAR = os.path.join(_ZOO, "zoo_keeper", "recipes", "simple_car.py")

#: MEASURED in Blender (`tools/preview_specimen.py --species cruiser --dims
#: 2.196 5.545 1.578 --form <livery>`, 2026-10-08): `simple_car`'s door
#: seams and door skin on the default slot, and the moulding's centre line.
#: The art is tested against what the car actually cut.
DOOR_EDGES = [-0.815, 0.099, 0.858]
DOOR_SKIN = (0.249, 0.912)
MOULDING = 0.249 + 0.42 * (0.912 - 0.249)
#: The same at the genome's lowest and highest corners, MEASURED by
#: `tools/coplanar_census.py --species cruiser` (Blender 5.1.1, 2026-10-08).
#: The lowest refused its livery on that run -- its marks reached 0.794 m
#: against handles over 0.775 m -- which is why the marks scale.
DOORS_AT = {
    "min": ((2.1, 5.35, 1.5), [-0.784, 0.101, 0.835], (0.240, 0.860)),
    "default": (None, DOOR_EDGES, DOOR_SKIN),
    "max": ((2.3, 5.75, 1.66), [-0.846, 0.096, 0.882], (0.258, 0.967)),
}


def _g():
    return genome_mod.load_species("cruiser")


def _corners():
    r = _g()["dimensions"]
    return [tuple(c) for c in itertools.product(
        *((r[a]["min"], r[a]["default"], r[a]["max"]) for a in ("width", "depth", "height")))]


CORNERS = _corners()


def _lay(dims):
    Wb, Lb, Hb = CF.body_dims(*dims)
    f = dict(C.CRUISER)
    f["rack"] = False
    return C.layout(f, Wb, Lb, Hb)


def _seat(lay):
    """A driver's seat where `simple_car` puts one: a third of the way along the
    cabin, at the belt's lower half (the recipe passes the real attachment)."""
    return (0.38, lay["y_ws"] + 0.95, lay["clear"] + 0.35)


def _interior(lay):
    """`simple_car`'s ``interior`` for this layout and `_seat`, from the
    literals its source builds the faces with (pinned by
    `test_simple_car_returns_the_cabin_it_built`). The recipe passes the
    real one."""
    y_fs = _seat(lay)[1]
    return {"floor_top": lay["clear"] + 0.13 + 0.012, "back_rear": y_fs + 0.39,
            "rear_front": y_fs + 0.95 - 0.24, "card_in": lay["hw"] - 0.045 - 0.075 - 0.012}


def _kit(lay):
    return CF.kit(lay, _seat(lay), _interior(lay))


#: `tools/coplanar_probe.py`'s defaults: two faces within 2 mm of one plane
#: that overlap by 1 mm2 or more are a coincident pair.
PROBE_TOL, PROBE_MIN_AREA = 0.002, 1e-6


def _coincident(boxes):
    """Every pair of axis-aligned boxes with a face of each within
    `PROBE_TOL` of one plane, overlapping by `PROBE_MIN_AREA` or more: what
    the probe reads off the built mesh, for boxes, in either facing."""
    found = []
    for i, (alo, ahi) in enumerate(boxes):
        for blo, bhi in boxes[i + 1:]:
            for ax in range(3):
                u, v = [k for k in range(3) if k != ax]
                du = min(ahi[u], bhi[u]) - max(alo[u], blo[u])
                dv = min(ahi[v], bhi[v]) - max(alo[v], blo[v])
                if du <= 0.0 or dv <= 0.0 or du * dv < PROBE_MIN_AREA:
                    continue
                for fa in (alo[ax], ahi[ax]):
                    for fb in (blo[ax], bhi[ax]):
                        if abs(fa - fb) <= PROBE_TOL + 1e-9:
                            found.append(((alo, ahi), (blo, bhi), ax, round(abs(fa - fb) * 1000.0, 2)))
    return found


def _png_rgb(png, x, y):
    """One pixel of an 8-bit RGB PNG with filter 0 rows (the Canvas's own)."""
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, w = 8, b"", None
    while pos < len(png):
        n = struct.unpack(">I", png[pos:pos + 4])[0]
        kind, body = png[pos + 4:pos + 8], png[pos + 8:pos + 8 + n]
        if kind == b"IHDR":
            w = struct.unpack(">I", body[:4])[0]
        elif kind == b"IDAT":
            idat += body
        pos += 12 + n
    raw = zlib.decompress(idat)
    stride = 1 + 3 * w
    row = raw[y * stride:(y + 1) * stride]
    assert row[0] == 0, "a filtered row: this reader takes filter 0 only"
    return tuple(row[1 + 3 * x:4 + 3 * x])


# --------------------------------------------------------------------------- #
# The car
# --------------------------------------------------------------------------- #

def test_the_genome_validates_and_names_every_part_the_recipe_builds():
    g = _g()
    assert genome_mod.validate_genome(g) == []
    assert g["license"]["construction_knowledge"] == "CC0"
    assert g["params"]["form"] == ["auto"] + list(CF.LIVERIES)
    src = open(_RECIPE, encoding="utf-8").read()
    named = set(re.findall(r'"(Car_(?:Kit|Lens_[A-Za-z]+))"', src))
    assert named and named <= set(g["parts"]), sorted(named - set(g["parts"]))


def test_the_body_is_a_crown_victorias():
    """1998-2002: 5.385 m long, 1.443 m tall, a 2.913 m wheelbase, about
    0.99 m of front overhang, P225/60R16 (r 0.338 m), 1.986 m at the body."""
    W, L, H = CF.SLOT
    Wb, Lb, Hb = CF.body_dims(W, L, H)
    lay = _lay(CF.SLOT)
    assert Lb == pytest.approx(5.385, abs=1e-3) and Hb == pytest.approx(1.443, abs=1e-3)
    assert lay["ya_r"] - lay["ya_f"] == pytest.approx(2.913, abs=0.01)
    assert lay["ya_f"] - lay["yF0"] == pytest.approx(0.99, abs=0.02)
    assert lay["wheel_r"] == pytest.approx(0.338, abs=0.005)
    assert 2.0 * lay["hw"] == pytest.approx(1.986, abs=0.01)


def test_auto_never_parks_a_police_car():
    assert "cruiser" not in dict(C.AUTO_POOL)


def test_the_form_is_pinned_and_the_same_every_time():
    jittered = dict(C.CRUISER)
    for k in C.JITTER:
        if k in jittered:
            jittered[k] = jittered[k] + 0.01
    f = CF.pin_form(jittered)
    for k in C.JITTER:
        if k in C.CRUISER:
            assert f[k] == C.CRUISER[k], k
    assert (f["doors"], f["quarter_glass"], f["wheel_kind"], f["bumper_kind"], f["interior"]) == \
        (4, True, "steel", "body", "blue_grey")
    assert f["paint"] == (1.0, 1.0, 1.0)      # the identity under the livery


@pytest.mark.parametrize("dims", CORNERS)
def test_the_kit_fills_the_slot_and_no_more(dims):
    """Width is the mirror heads, depth the push bar's front to the rear
    bumper, height the light bar's top: every kit box inside, and the push
    bar and the light bar ON the slot's front and top."""
    W, L, H = dims
    lay = _lay(dims)
    boxes = [b for rows in _kit(lay).values() for b in rows]
    eps = 1e-6
    for lo, hi in boxes:
        assert -W / 2.0 - eps <= lo[0] and hi[0] <= W / 2.0 + eps, (lo, hi)
        assert lay["yF0"] - CF.PUSH_PROUD - eps <= lo[1] and hi[1] <= lay["yR0"] + eps, (lo, hi)
        assert -eps <= lo[2] and hi[2] <= H + eps, (lo, hi)
    assert min(lo[1] for lo, hi in boxes) == pytest.approx(lay["yF0"] - CF.PUSH_PROUD)
    assert max(hi[2] for lo, hi in boxes) == pytest.approx(H)


@pytest.mark.parametrize("dims", CORNERS)
def test_the_bar_is_red_on_the_drivers_side_and_stands_on_the_roof(dims):
    lay = _lay(dims)
    k = _kit(lay)
    (red_lo, red_hi), = k["lens_red"]
    (blue_lo, blue_hi), = k["lens_blue"]
    assert red_lo[0] > 0.0 and blue_hi[0] < 0.0      # +X is the driver's side
    # over the roof only: the trunk's whip crosses the roof's height too
    feet = [b for b in k["kit_black"]
            if b[0][2] < lay["zr"] < b[1][2] and lay["y_rf"] < b[0][1] < lay["y_rr"]]
    assert len(feet) == 4                             # four feet run into the roof


def test_the_spotlight_is_on_the_drivers_a_pillar():
    lay = _lay(CF.SLOT)
    lens = [b for b in _kit(lay)["lens_clear"] if b[0][2] < lay["zr"]]
    assert len(lens) == 1
    (lo, hi), = lens
    assert lo[0] > lay["hw"] - 0.05                   # outboard, driver's side
    assert lay["y_ws"] < lo[1] < lay["y_rf"]          # up the A-pillar
    assert lay["belt"] < lo[2] < lay["zr"]


@pytest.mark.parametrize("dims", CORNERS)
def test_no_two_kit_faces_share_a_plane(dims):
    """The first census found 6-7 such pairs a build in the kit alone: the
    partition's posts 1-2 mm inside its rails' faces, the middle bar 1 mm
    inside the posts', the rails' ends flush with the outer posts, and the
    push bar's lower brace touching its lower bar."""
    lay = _lay(dims)
    boxes = [b for rows in _kit(lay).values() for b in rows]
    assert _coincident(boxes) == []


def test_the_check_sees_a_coincident_pair():
    """A checker that cannot fail is indistinguishable from one that passed:
    the first cut's outer partition post found where the census found it --
    flush with its rail's end, and 2 mm inside both the rail's faces -- and
    the same corner as the kit builds it now found clean."""
    rail = ((-0.5, 0.0, 0.0), (0.5, 0.025, 0.025))
    post = ((-0.5, 0.002, 0.015), (-0.475, 0.023, 0.5))
    assert sorted((c[2], c[3]) for c in _coincident([rail, post])) == [(0, 0.0), (1, 2.0), (1, 2.0)]
    rail_now = ((-0.5 + CF.INSET, 0.0, 0.0), (0.5 - CF.INSET, 0.025, 0.025))
    post_now = ((-0.5, CF.INSET, 0.015), (-0.475, 0.025 - CF.INSET, 0.5))
    assert _coincident([rail_now, post_now]) == []


@pytest.mark.parametrize("dims", CORNERS)
def test_the_partition_stands_between_the_seats_and_inside_the_doors(dims):
    lay = _lay(dims)
    cab = _interior(lay)
    yp = cab["back_rear"] + CF.PARTITION_BEHIND
    part = [b for b in _kit(lay)["kit_black"]
            if b[0][1] >= yp - 1e-9 and b[1][1] <= yp + CF.PARTITION_BAR + 1e-9 and b[1][2] <= lay["zr"]]
    assert len(part) == 7                              # two rails, four posts, a bar
    for lo, hi in part:
        assert lo[1] > cab["back_rear"] and hi[1] < cab["rear_front"]
        assert -cab["card_in"] < lo[0] and hi[0] < cab["card_in"]
        assert lo[2] >= cab["floor_top"] - CF.INSET - 1e-9
    # the rail's underside is in the floor, clear of its top and of the
    # body's pan under it (simple_car: floor_top = floor_z + 0.012), each by
    # more than the probe's window -- the second census found it 2 mm over
    # the pan at a 10 mm sink
    bottom = min(lo[2] for lo, hi in part)
    pan = cab["floor_top"] - 0.012
    assert cab["floor_top"] - bottom > PROBE_TOL and bottom - pan > PROBE_TOL


def test_a_partition_that_does_not_fit_is_refused():
    lay = _lay(CF.SLOT)
    cab = dict(_interior(lay))
    cab["rear_front"] = cab["back_rear"] + CF.PARTITION_BEHIND + 0.01
    with pytest.raises(ValueError):
        CF.kit(lay, _seat(lay), cab)


# --------------------------------------------------------------------------- #
# The livery
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("livery", list(CF.LIVERIES))
def test_every_line_sets_and_the_patches_are_white_and_margin(livery):
    lay = _lay(CF.SLOT)
    art = CF.livery_art(lay, DOOR_EDGES, DOOR_SKIN, livery, moulding_z=MOULDING)
    assert len(art["lines"]) == (3 if livery == "black_white" else 2)
    fr = art["frame"]
    for which, want in (("white", (255, 255, 255)),
                        ("margin", tuple(CF._srgb8(c) for c in CF.LIVERIES[livery]["margin"]))):
        u, v = CF.patch_uv(fr, which)
        px = _png_rgb(art["png"], int(u * fr["W"]), int((1.0 - v) * fr["H"]))
        assert px == want, (which, px)


@pytest.mark.parametrize("livery", list(CF.LIVERIES))
def test_the_marks_stand_between_the_moulding_and_the_handles(livery):
    """The first frames ran the black rub strip through POLICE, and the front
    door's handle 7 mm into DELCO COUNTY."""
    lay = _lay(CF.SLOT)
    art = CF.livery_art(lay, DOOR_EDGES, DOOR_SKIN, livery, moulding_z=MOULDING)
    fr = art["frame"]

    def z_of(py):
        return fr["z1"] - py / CF.ART_PPM

    lines = art["lines"][:-1]                         # all but the motto
    motto = art["lines"][-1]
    for x0, y0, x1, y1 in lines:
        assert z_of(y1) > MOULDING + CF.MOULDING_HALF
        assert z_of(y0) < DOOR_SKIN[1] - CF.HANDLE_DROP
    assert z_of(motto[1]) < MOULDING - CF.MOULDING_HALF


@pytest.mark.parametrize("livery", list(CF.LIVERIES))
@pytest.mark.parametrize("corner", list(DOORS_AT))
def test_the_marks_fit_every_door_the_genome_allows(livery, corner):
    """On a lower car the marks shrink together to the door between the
    moulding and the handles; the genome's lowest corner needs 0.92 of the
    black-and-white's size, and the stripe fits as drawn."""
    dims, edges, skin = DOORS_AT[corner]
    lay = _lay(dims or CF.SLOT)
    moulding = skin[0] + 0.42 * (skin[1] - skin[0])
    art = CF.livery_art(lay, edges, skin, livery, moulding_z=moulding)
    fr = art["frame"]
    for x0, y0, x1, y1 in art["lines"][:-1]:
        assert fr["z1"] - y1 / CF.ART_PPM > moulding + CF.MOULDING_HALF
        assert fr["z1"] - y0 / CF.ART_PPM < skin[1] - CF.HANDLE_DROP
    want = 0.92 if (corner, livery) == ("min", "black_white") else 1.0
    assert art["scale"] == pytest.approx(want, abs=0.005)
    assert art["scale"] >= CF.MARK_SCALE_MIN


def test_marks_too_small_to_read_are_refused():
    lay = _lay(CF.SLOT)
    low = (DOOR_SKIN[0], DOOR_SKIN[0] + 0.45)          # a door skin 0.45 m tall
    with pytest.raises(ValueError, match="of their size"):
        CF.livery_art(lay, DOOR_EDGES, low, "black_white",
                      moulding_z=low[0] + 0.42 * (low[1] - low[0]))


def test_a_line_that_cannot_set_is_refused_not_dropped():
    lay = _lay(CF.SLOT)
    with pytest.raises(ValueError):
        CF.livery_art(lay, [-0.3, 0.0, 0.3], DOOR_SKIN, "black_white", moulding_z=MOULDING)


def test_the_sides_read_the_right_way_round_and_nothing_else_maps():
    lay = _lay(CF.SLOT)
    fr = CF.art_frame(lay)
    y = 0.4
    u_l, v_l = CF.livery_uv((lay["hw"], y, 0.6), (1.0, 0.0, 0.0), fr)
    u_r, v_r = CF.livery_uv((-lay["hw"], y, 0.6), (-1.0, 0.0, 0.0), fr)
    art_w = fr["w"] / fr["W"]
    assert u_l + u_r == pytest.approx(art_w)          # mirrored across the art
    assert v_l == pytest.approx(v_r)
    for n in ((0.0, 0.0, 1.0), (0.0, -1.0, 0.0), (0.7, 0.0, 0.7)):
        assert CF.livery_uv((0.0, 0.0, 1.0), n, fr) == CF.patch_uv(fr, "white")
    u, v = CF.livery_uv((lay["hw"], lay["yt"] + 1.0, 0.6), (1.0, 0.0, 0.0), fr)
    assert u == pytest.approx(art_w)                  # clamped to the art, not the patches


def test_the_finish_is_white_on_the_sides_and_the_livery_elsewhere():
    lay = _lay(CF.SLOT)
    for lv, spec in CF.LIVERIES.items():
        assert CF.finish_rgb((lay["hw"], 0.0, 0.6), (1.0, 0.0, 0.0), lay, lv) == (1.0, 1.0, 1.0)
        assert CF.finish_rgb((0.0, 0.0, lay["zr"]), (0.0, 0.0, 1.0), lay, lv) == spec["roof"]
        assert CF.finish_rgb((0.0, -2.0, lay["hood"]), (0.0, 0.0, 1.0), lay, lv) == spec["body"]


# --------------------------------------------------------------------------- #
# The recipe and simple_car's hook, read as source
# --------------------------------------------------------------------------- #

def test_the_recipe_paints_one_livery_material_and_the_kit_on_the_cars_painted():
    src = open(_RECIPE, encoding="utf-8").read()
    assert src.count("make_wear_textured_material(") == 1
    assert 'make_material("M_Car_painted"' in src
    assert "set_uv_by(body" in src and "tint_wear_by(body" in src


def test_the_kit_merges_into_the_cars_painted_mesh():
    """The export packs parts by (family, material); a kit part outside the
    car's family is a mesh -- a draw -- of its own on the same material. The
    first build named them `Cruiser_*` and exported six meshes where five do."""
    from zoo_keeper.core import partnames
    src = open(_RECIPE, encoding="utf-8").read()
    named = set(re.findall(r'"(Car_(?:Kit|Lens_[A-Za-z]+))"', src))
    assert len(named) == 4
    assert {partnames.family(n) for n in named} == {partnames.family("Car_Body")}
    assert all(partnames.is_mergeable(n) for n in named)


def test_simple_car_returns_the_cabin_it_built():
    """The partition and console stand against `simple_car`'s cabin: the
    values it returns are the ones its faces were built from, and `_interior`
    above reads the same literals."""
    src = open(_SIMPLE_CAR, encoding="utf-8").read()
    for line in ("floor_z = clear + 0.13",
                 "floor_top = floor_z + 0.012",
                 "(xtub - 0.01, y_te - 0.05, floor_top))",
                 "back_rear = y_fs + 0.39",
                 "(xc + 0.13, back_rear, back_top + 0.15))",
                 "rear_front = y_rs - 0.24 if y_rs - 0.24 > y_fs + 0.40 else None",
                 "card_in = xi - 0.012",
                 "x0, x1 = sign * card_in, sign * (xi + 0.006)",
                 "SHOULDER_IN = 0.045",
                 "DOOR_T = 0.075",
                 '"interior": {"floor_top": floor_top, "back_rear": back_rear,'):
        assert line in src, line
    rec = open(_RECIPE, encoding="utf-8").read()
    assert 'cruiser_forms.kit(lay, seat, car["interior"])' in rec


def test_simple_car_draws_its_own_cars_as_it_always_did():
    """The hook is a default: without ``form`` the car is resolved here, from
    the same streams in the same order."""
    src = open(_SIMPLE_CAR, encoding="utf-8").read()
    assert "def build(plan, streams, collection, form=None):" in src
    assert "f = form if form is not None else car_forms.resolve(plan, streams)" in src
