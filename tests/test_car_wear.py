"""simple_car 1.120.0: a parked car's history -- sun, salt, the road, a repair and its owner's stickers -- drawn per
module from its own stream, painted in the body's `Wear`, laid as thin pieces of the painted material, and stuck on
from one shared sheet (`core.car_wear`, `core.car_stickers`; the factory's roadmap 44).

The walker's look review, 2026-10-19, on the parked cars: "Looks right", and "some of the cars need some patina and
wear...rusting....ect....bumper stickers....". Pure: the recipe imports bpy and this suite runs without Blender; the
recipe's own wiring is read from its source, and what only Blender shows is in `test_car_forms.py`'s MEASURED.
"""
from __future__ import annotations

import collections
import math
import os
import re

import pytest

from zoo_keeper import SEED_EPOCH
from zoo_keeper.core import car_forms, car_stickers, car_wear, seeding

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "simple_car.py")


def _streams(stem):
    return seeding.RNGStreams(seeding.root_key(stem, "simple_car", 0, SEED_EPOCH))


def _plan(w, d, h, **params):
    return {"params": dict({"body_style": "auto", "doors": 0}, **params),
            "dimensions": {"width": w, "depth": d, "height": h},
            "color": [0.55, 0.56, 0.58], "style_block": {"color": [0.55, 0.56, 0.58]}}


# --- the history is the car's own, and moves nothing else ----------------------------------------------------------

#: Four of Lot's parked modules as Zoo 1.119.0 resolved them, BEFORE the history existed: (stem, style, paint,
#: doors, wheels, bumpers, quarter glass, rack, two-tone, belt). Literals, read off 1.119.0 -- a table computed here
#: would pass whatever the code now says.
BEFORE = (
    ("prop_simple_car_delco_1997_01_w175_d430_h145", "sedan", "silver", 4, "hubcap", "body", False, False, False,
     0.664797),
    ("prop_simple_car_delco_1997_02_w175_d480_h142", "sedan", "white", 4, "hubcap", "black", False, False, False,
     0.656589),
    ("prop_simple_car_delco_1997_01_w160_d380_h140", "hatchback", "sky_blue", 2, "hubcap", "body", True, False,
     False, 0.614847),
    ("prop_simple_car_delco_1997_02_w180_d470_h173", "suv", "tan", 4, "alloy", "grey", True, True, True, 0.623449),
)


def test_a_history_never_re_rolls_a_cars_shape_paint_or_trim():
    """The history draws from its own stream (`car_history`), so every car Zoo built before it, it builds again
    with the same style, proportions, paint and trim. FAILS if the history ever borrows another stream's draws."""
    for stem, *want in BEFORE:
        w, d, h = [int(t[1:]) / 100.0 for t in stem.split("_")[-3:]]
        f = car_forms.resolve(_plan(w, d, h), _streams(stem))
        got = [f["style"], f["paint_name"], f["doors"], f["wheel_kind"], f["bumper_kind"], f["quarter_glass"],
               f["rack"], f["two_tone"], round(f["belt"], 6)]
        assert got == want, stem
        assert f["history"] in car_wear.WEATHER


def test_the_histories_park_in_their_weights():
    """Over 3,000 stems, each history's share within three points of its weight: "some of the cars"."""
    c = collections.Counter(car_wear.resolve({}, _streams("stem_%d" % k))["history"] for k in range(3000))
    for name, weight in car_wear.HISTORIES:
        assert abs(c[name] / 3000.0 - weight) < 0.03, (name, c)
    assert sum(w for _n, w in car_wear.HISTORIES) == pytest.approx(1.0)


def test_an_asked_history_wins_and_a_drawn_one_says_so():
    f = car_wear.resolve({"history": "beater"}, _streams("x"))
    assert f["history"] == "beater" and f["history_how"] == "asked"
    lo, hi = car_wear.WEATHER["beater"]["rust"]
    assert lo <= len(f["rust"]) <= hi
    g = car_wear.resolve({}, _streams("x"))
    assert g["history_how"] == "drawn"
    # what each history may lay, and nothing a history does not lay
    for name, w in car_wear.WEATHER.items():
        for k in range(200):
            h = car_wear.resolve({"history": name}, _streams("%s_%d" % (name, k)))
            assert w["rust"][0] <= len(h["rust"]) <= w["rust"][1]
            assert w["peel"][0] <= h["peel"] <= w["peel"][1]
            assert w["stickers"][0] <= len(h["stickers"]) <= w["stickers"][1]
            assert len(set(h["stickers"])) == len(h["stickers"])
            assert len(set(h["rust"])) == len(h["rust"])
            if w["primer"] == 0.0:
                assert not h["primer"]


def test_only_the_street_weathers_and_the_cruiser_keeps_its_livery():
    """The cruiser is drawn as `simple_car`'s `cruiser` row and paints its own livery over the body; it is the
    county's, kept by a motor pool, and the recipe never lays a history on it."""
    src = open(_RECIPE, encoding="utf-8").read()
    assert "weathered = style in car_forms.STREET_STYLES" in src
    assert "cruiser" not in car_forms.STREET_STYLES
    assert re.search(r'if weathered and key == "body":', src)


# --- the paint: sun and road ----------------------------------------------------------------------------------------

def test_the_sun_never_darkens_a_paint():
    """REFUTED, kept in `car_wear`: the van's bleach is darker than a silver or a white car, and the first silver
    beater's roof went grey. Every paint the street parks chalks lighter than it was, or no darker."""
    lum = car_wear._luminance
    for name, base in car_forms.PALETTE.items():
        assert lum(car_wear.chalk(base)) >= lum(base) - 1e-9, name
    # a dark paint lifts visibly; a white one hardly moves
    assert lum(car_wear.chalk(car_forms.PALETTE["navy"])) - lum(car_forms.PALETTE["navy"]) > 0.15
    assert lum(car_wear.chalk(car_forms.PALETTE["white"])) - lum(car_forms.PALETTE["white"]) < 0.08


def test_the_finish_fades_what_faces_the_sky_and_dusts_what_is_low():
    hist = {"sun": 0.80, "dust": 0.55, "wear_seed": 12345}
    kept = {"sun": 0.10, "dust": 0.10, "wear_seed": 12345}
    navy = car_forms.PALETTE["navy"]
    up, side = (0.0, 0.0, 1.0), (1.0, 0.0, 0.0)
    roof_b = car_wear.finish_rgb((0.0, 0.5, 1.4), up, navy, hist)
    roof_k = car_wear.finish_rgb((0.0, 0.5, 1.4), up, navy, kept)
    flank = car_wear.finish_rgb((0.8, 0.5, 0.9), side, navy, hist)
    low = car_wear.finish_rgb((0.8, 0.5, 0.10), side, navy, hist)
    lum = car_wear._luminance
    assert lum(roof_b) > lum(roof_k) > lum(navy) - 1e-9          # a beater's roof chalks more than a kept car's
    assert flank == pytest.approx(navy, abs=1e-9)                 # a side above the road takes no sun and no dust
    assert lum(low) > lum(navy)                                    # the road's colour is lighter than navy
    for c in (roof_b, roof_k, flank, low):
        assert all(0.0 <= v <= 1.0 for v in c)


# --- the pieces: where each stands, and what it keeps clear of --------------------------------------------------

def _lay():
    """A 1.75 x 4.30 x 1.45 sedan's layout, from `car_forms.layout` itself."""
    f = car_forms.resolve(_plan(1.75, 4.30, 1.45, body_style="sedan"), _streams("lay"))
    return f, car_forms.layout(f, 1.75, 4.30, 1.45)


def _edge(lay):
    """A skin bottom like `simple_car`'s: the rocker line, rising over each arch."""
    def edge(y):
        z = lay["clear"] + 0.09
        for ya in (lay["ya_f"], lay["ya_r"]):
            dy = abs(y - ya)
            if dy <= lay["R"]:
                z = max(z, lay["wheel_r"] + math.sqrt(lay["R"] ** 2 - dy * dy) + 0.012)
        return z
    return edge


def _normal(verts, face):
    a, b, c = (verts[i] for i in face[:3])
    u = [b[k] - a[k] for k in range(3)]
    v = [c[k] - b[k] for k in range(3)]
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def test_rust_hugs_the_arches_and_the_rocker_and_keeps_off_the_strips():
    """A bloom stands `RUST_PROUD` off the skin, from the skin's lower edge up, wound to face out of its side, and
    reaches no further along the car than 15 mm past an arch -- the moulding stops 30 mm past it and the cladding 20,
    so a bloom never lies in a strip's plane window. A rocker's runs only between the arches."""
    f, lay = _lay()
    edge = _edge(lay)

    def skin_x(y):
        return lay["hw"]

    hist = dict(f, rust=tuple((p, s) for p, s, _w in car_wear.RUST_PLACES), wear_seed=777)
    pieces = car_wear.rust_blooms(hist, lay, edge, skin_x, lambda co, n: (0.4, 0.4, 0.4),
                                  rocker_span=(lay["ya_f"] + lay["R"] + 0.04, lay["ya_r"] - lay["R"] - 0.04))
    assert len(pieces) == 6
    for p in pieces:
        side = p["side"]
        for x, y, z in p["verts"]:
            assert x == pytest.approx(side * (lay["hw"] + car_wear.RUST_PROUD))
            assert z >= edge(y) + 0.003 - 1e-9
        for face in p["faces"]:
            assert _normal(p["verts"], face)[0] * side > 0.0
        ys = [v[1] for v in p["verts"]]
        if p["kind"].endswith("arch"):
            ya = lay["ya_f"] if "front" in p["kind"] else lay["ya_r"]
            reach = lay["R"] + car_wear.ARCH_REACH
            assert min(ys) >= ya - reach - 1e-9 and max(ys) <= ya + reach + 1e-9
        else:
            assert min(ys) >= lay["ya_f"] + lay["R"] + 0.04 - 1e-9 and max(ys) <= lay["ya_r"] - lay["R"] - 0.04 + 1e-9
    # every strip that runs between the arches (the moulding, the cladding) stops past them by its own margin,
    # read from the recipe's spans; a bloom reaches less far than the nearest
    src = open(_RECIPE, encoding="utf-8").read()
    stops = [float(m.group(1)) for m in re.finditer(
        r"\(ya_f \+ R \+ ([0-9.]+), ya_r - R - \1\)", src)]
    assert sorted(stops) == [0.02, 0.03, 0.04], stops    # the cladding's, the moulding's, the rocker rust's own
    assert car_wear.ARCH_REACH < min(stops)
    # a clad car's rocker rusts nowhere a camera sees
    clad = car_wear.rust_blooms(hist, lay, edge, skin_x, lambda co, n: (0.4, 0.4, 0.4), rocker_span=None)
    assert all(not p["kind"].endswith("rocker") for p in clad) and len(clad) == 4


def test_the_proud_distances_clear_every_strip_they_can_cross():
    """`simple_car`'s strips on the door skin: a seam 3 mm proud, the moulding and the cladding `TRIM_PROUD`, the
    pinstripe 4 mm more, a handle 12 mm. Each piece's plane stands at least 2.5 mm from every strip plane it can lie
    over -- tools/coplanar_probe.py's window is 2 mm. The primer can lie over no handle (`simple_car` keeps it 3 cm
    ahead of the front door's) and no pinstripe (it stands above the moulding's line, the pinstripe below it)."""
    src = open(_RECIPE, encoding="utf-8").read()
    trim = float(re.search(r"^TRIM_PROUD = ([0-9.]+)", src, re.M).group(1))
    seam = float(re.search(r"^SEAM_PROUD = ([0-9.]+)", src, re.M).group(1))
    for proud in (car_wear.RUST_PROUD, car_wear.PRIMER_PROUD):
        for strip in (seam, trim):
            assert abs(proud - strip) >= 0.0025 - 1e-9, (proud, strip)
    assert car_wear.PEEL_PROUD > 0.002 and car_wear.STICKER_PROUD > 0.002
    assert "door_edges[1] - 0.33" in src                 # the handle spans door_edges[1] - 0.30 .. - 0.14
    assert re.search(r"yh - 0\.08, yh \+ 0\.08", src) and "handle_ys = [e - 0.22 for e in door_edges[1:]]" in src
    assert "zm_moulding + 0.054" in src                  # the moulding is zm +/- 0.024


def test_the_primer_patch_stays_on_the_door_and_reads_on_any_paint():
    f, lay = _lay()
    door = (-0.60, 0.20, 0.62, 0.86)
    hist = dict(f, primer=True, wear_seed=4242)
    for base, want in ((car_forms.PALETTE["silver"], car_wear.RED_OXIDE),
                       (car_forms.PALETTE["navy"], car_wear.van_forms.PRIMER)):
        p = car_wear.primer_patch(hist, door, lambda y: lay["hw"], base)
        assert p is not None and p["side"] == -1
        for x, y, z in p["verts"]:
            assert x == pytest.approx(-(lay["hw"] + car_wear.PRIMER_PROUD))
            assert door[0] - 1e-9 <= y <= door[1] + 1e-9 and door[2] - 1e-9 <= z <= door[3] + 1e-9
        for face in p["faces"]:
            assert _normal(p["verts"], face)[0] < 0.0
        # red oxide is red; the grey primer is grey
        r, g, b = p["rgb"][0]
        assert (r / g > 2.0) == (want is car_wear.RED_OXIDE), (r, g, b)
    assert car_wear.primer_patch(dict(hist, primer=False), door, lambda y: lay["hw"], (0.5, 0.5, 0.5)) is None
    # a door too small for the smallest patch gets none
    assert car_wear.primer_patch(hist, (0.0, 0.10, 0.6, 0.65), lambda y: lay["hw"], (0.5, 0.5, 0.5)) is None


def test_the_peeled_clear_coat_lies_on_the_roof_inside_its_edges():
    roof = {"z": 1.45, "x_half": 0.40, "y0": -0.30, "y1": 0.95}
    for seed in range(60):
        hist = {"peel": 3, "wear_seed": seed * 7919}
        pieces = car_wear.peel_patches(hist, roof, lambda co, n: (0.2, 0.05, 0.05))
        boxes = []
        for p in pieces:
            xs, ys = [v[0] for v in p["verts"]], [v[1] for v in p["verts"]]
            assert all(v[2] == pytest.approx(roof["z"] + car_wear.PEEL_PROUD) for v in p["verts"])
            assert min(xs) >= -roof["x_half"] + 0.03 - 1e-9 and max(xs) <= roof["x_half"] - 0.03 + 1e-9
            assert min(ys) >= roof["y0"] + 0.03 - 1e-9 and max(ys) <= roof["y1"] - 0.03 + 1e-9
            for face in p["faces"]:
                assert _normal(p["verts"], face)[2] > 0.0
            boxes.append((min(ys), max(ys)))
        boxes.sort()
        for (a0, a1), (b0, b1) in zip(boxes, boxes[1:]):
            assert a1 <= b0 + 1e-9                          # each its own stretch of the roof: none overlap
    assert car_wear.peel_patches({"peel": 0, "wear_seed": 1}, roof, lambda co, n: (0, 0, 0)) == []


def test_stickers_stand_on_the_rear_band_apart_and_read_from_behind():
    """On the band, `STICKER_PROUD` out along its normal, above the rub strip and under the band's top, inside its
    width, no two overlapping however they wander, each a cell of the sheet with its first letter at the car's +x
    end -- the viewer's left behind it. FAILS ON THE FIRST CUT at the narrowest car: three stickers 0.293 m apart."""
    sw, sh = car_stickers.SIZE
    for x_half in (0.652, 0.75, 0.86, 0.36, 0.20):
        band = {"x_half": x_half, "y_lo": 2.138, "z_lo": 0.313, "y_hi": 2.103, "z_hi": 0.49, "z_seen": 0.333}
        dy, dz = band["y_hi"] - band["y_lo"], band["z_hi"] - band["z_lo"]
        run = math.hypot(dy, dz)
        n = (0.0, dz / run, -dy / run)
        for seed in range(40):
            hist = {"stickers": (0, 5, 11), "wear_seed": seed * 104729}
            quads = car_wear.sticker_quads(hist, band)
            spans = []
            for q in quads:
                vs = q["verts"]
                for x, y, z in vs:
                    assert abs(x) <= x_half - 0.02 + 1e-9
                    assert band["z_seen"] < z < band["z_hi"]
                    # its plane: STICKER_PROUD off the band's
                    off = (y - band["y_lo"]) * n[1] + (z - band["z_lo"]) * n[2]
                    assert off == pytest.approx(car_wear.STICKER_PROUD, abs=1e-9)
                nrm = _normal(vs, q["faces"][0])
                assert nrm[1] > 0.0 and nrm[2] > 0.0
                assert q["uv"][1][0] < q["uv"][0][0]           # the +x end samples the cell's left
                u0, v0, u1, v1 = car_stickers.cells()[q["index"]]
                assert set(q["uv"]) == {(u0, v0), (u1, v0), (u1, v1), (u0, v1)}
                spans.append((min(v[0] for v in vs), max(v[0] for v in vs)))
            spans.sort()
            for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
                assert a1 < b0, (x_half, seed, spans)
            assert len(quads) <= {0.652: 3, 0.75: 3, 0.86: 3, 0.36: 2, 0.20: 1}[x_half]
    # a band too short shows none
    tight = {"x_half": 0.7, "y_lo": 2.1, "z_lo": 0.30, "y_hi": 2.09, "z_hi": 0.38, "z_seen": 0.33}
    assert car_wear.sticker_quads({"stickers": (1,), "wear_seed": 5}, tight) == []


# --- the sheet ------------------------------------------------------------------------------------------------------

def test_the_sticker_sheet_sets_every_line_and_carries_no_real_mark():
    art = car_stickers.art()
    assert art["unset"] == [], art["unset"]
    words = set()
    for line in car_stickers.strings():
        words.update(re.findall(r"[A-Z0-9']+", line.upper()))
        for phrase in car_stickers.DENY_WORDS:
            if " " in phrase:
                assert phrase not in line.upper(), line
    for word in car_stickers.DENY_WORDS:
        assert word not in words, word
    # one sheet, every cell inside it, no two sharing a pixel
    W, H, boxes = car_stickers.layout()
    assert art["size"] == (W, H) and len(boxes) == len(car_stickers.STICKERS)
    for a, b in zip(boxes, boxes[1:]):
        assert a != b
    for u0, v0, u1, v1 in car_stickers.cells():
        assert 0.0 < u0 < u1 < 1.0 and 0.0 < v0 < v1 < 1.0
    # small, because noise does not compress: measured 74,835 bytes at 1.120.0
    assert len(art["png"]) < 150_000


def test_the_sheet_is_one_material_and_the_pieces_ride_the_painted_one():
    """The draw-call rule (CLAUDE.md): the pieces are the painted material's, the stickers one named material, the
    same name in every car, so a merged street side packs every car's stickers into one mesh."""
    src = open(_RECIPE, encoding="utf-8").read()
    assert src.count('"M_Car_stickers"') == 1
    assert re.search(r"for obj in weather_objs \+ \(\[peel_obj\] if peel_obj is not None else \[\]\):\n"
                     r"\s+materials\.assign\(\[obj\], painted\)", src)
    assert '"dressing_objects": [peel_obj] if peel_obj is not None else []' in src
    assert 'streams.stream("car_weather")' in src
