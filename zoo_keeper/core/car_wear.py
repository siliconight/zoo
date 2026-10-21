"""A parked car's history: what Pennsylvania's summers and winters leave on its paint (1.120.0).

The walker's look review, 2026-10-19, on the parked cars: "Looks right", and "some of the cars need some patina and
wear...rusting....ect....bumper stickers....". The factory's roadmap 44: wear per car as seeded variation on the
shared species, never a material per colour.

WHAT A STREET OF 1997 DELCO CARS CARRIES, and where each mark comes from:

  * SUN. The paint of the era lost its clear coat to the sun on the faces that look at the sky -- the roof, the
    hood, the trunk lid -- and chalked: a dark colour toward a pale, dull version of itself, a light one hardly at all
    (`chalk`). Where the clear coat has let go altogether it lifts in ragged milky patches over the colour: a
    beater's roof (`peel_patches`).
  * SALT. Pennsylvania salts its roads, and the brine sits in the wheel arches and along the rockers and eats them
    from the inside out: rust shows first at the rear arches' lips, then the front's, then along a rocker
    (`rust_blooms`).
  * THE ROAD. A car that is driven carries the road on its lower third (`finish_rgb`'s dust).
  * A REPAIR. A dented door, filled and sanded and never painted: a patch of grey primer (`primer_patch`).
  * ITS OWNER. Bumper stickers on the rear bumper (`sticker_quads`, the sheet `car_stickers`).

A HISTORY IS DRAWN PER MODULE, from its own stream (`car_history`), so it never re-rolls a car's style, paint or
trim, and a Zoo with it builds every car's silhouette and colour exactly as one without it did. Lot parks a street
from a handful of modules (`site_parking.CARS` times its `STYLES`), so "some of the cars" is the histories' weights
over those modules. Only the street's own styles weather (`car_forms.STREET_STYLES`): the cruiser is the county's,
kept by a motor pool, and keeps its livery as it was.

THE DRAW-CALL RULE (CLAUDE.md). The sun and the dust are colour in the body's `Wear`, on the painted material it
already wears. The rust, the primer and the peeled clear coat are thin pieces of that same material, each carrying
its colour in its own `Wear` -- packed into the car's painted mesh, no submission of their own. The stickers are one
material whose one image every car's stickers sample: a car carrying any is one submission more than a car carrying
none, and a merged street side one more, not one a sticker.

NO TWO FACES SHARE A PLANE. Every piece stands proud of the face it lies on by its own distance, chosen against the
strips already on that face (`simple_car`: a seam 3 mm proud, the moulding and the cladding 6, the pinstripe 10, a
handle 12) and tools/coplanar_probe.py's 2 mm window: rust 8.5 mm, primer 11.5 mm, each at least 2.5 mm from every
strip plane it can cross, and the peel and the stickers 4 mm off faces no strip lies on. Where a piece could still
meet a strip in the same plane's window it is kept off it: rust only over the arches and along a rocker with no
cladding, the primer above the moulding line and clear of the handles.

Pure: tables, seeded choices and geometry in the recipe's build frame -- x across (0 on the centre line), y along the
car with the nose at -y, z up from the ground -- every edge the recipe knows passed in as a number or a function.
`recipes/simple_car.py` builds the pieces and nothing here imports bpy.
"""
from __future__ import annotations

import math

from . import car_stickers, van_forms

#: How often each history parks on a street, and what each leaves. ``sun`` and ``dust`` are the strengths
#: `finish_rgb` paints with (0..1); ``rust``, ``peel`` and ``stickers`` are (fewest, most) of each piece; ``primer``
#: is the chance of one filled dent in primer.
HISTORIES = (("kept", 0.35), ("driven", 0.45), ("beater", 0.20))
WEATHER = {
    "kept": {"sun": 0.10, "dust": 0.10, "rust": (0, 0), "primer": 0.00, "peel": (0, 0), "stickers": (0, 1)},
    "driven": {"sun": 0.35, "dust": 0.35, "rust": (0, 2), "primer": 0.15, "peel": (0, 0), "stickers": (0, 2)},
    "beater": {"sun": 0.80, "dust": 0.55, "rust": (2, 4), "primer": 0.60, "peel": (1, 3), "stickers": (1, 3)},
}
#: Where the salt starts, as (place, side, weight): the rear arches' lips first, the front's next, a rocker last.
#: A side is +1 for the driver's (+X) and -1 for the kerb's.
RUST_PLACES = (("rear_arch", 1, 3.0), ("rear_arch", -1, 3.0), ("front_arch", 1, 2.0), ("front_arch", -1, 2.0),
               ("rocker", 1, 1.5), ("rocker", -1, 1.5))

#: How far each piece stands proud of the face it lies on (see NO TWO FACES SHARE A PLANE above).
RUST_PROUD = 0.0085
PRIMER_PROUD = 0.0115
PEEL_PROUD = 0.004
STICKER_PROUD = 0.004

#: The sun: how far toward its `chalk` a face that looks straight up goes at ``sun`` 1.0.
SUN_MAX = 0.45
#: A paint's chalk: its own luminance lifted (``CHALK_LIFT`` over ``CHALK_GAIN`` times it, at most ``CHALK_MAX``)
#: as a warm grey. THE VAN'S BLEACH WAS TRIED FIRST AND IS WRONG HERE: `van_forms.SUN_BLEACH` (0.31, 0.29, 0.27) is a
#: pale grey against the van's near-black, and against a silver or a white car it is DARKER than the paint, so the
#: first silver beater's roof went grey and its peel patches read darker than the paint round them.
CHALK_GAIN, CHALK_LIFT, CHALK_MAX = 1.10, 0.18, 0.85
CHALK_WARM = (1.0, 0.97, 0.92)
#: The road: dust is full at the ground and gone at this height, and at most this strong.
DUST_TOP = 0.50
DUST_MAX = 0.50
#: Rust's two colours: the lip, eaten through to scale, and the bloom's edge, still under the paint and staining it
#: `BLOOM_EDGE` of the way to `RUST_EDGE`. The first lip was a near-black brown (0.120, 0.048, 0.022) and read as the
#: arch's own shadow on a silver car.
RUST_LIP = (0.200, 0.072, 0.030)
RUST_EDGE = (0.330, 0.140, 0.050)
BLOOM_EDGE = 0.55
#: How far past an arch's end a bloom reaches along the car: short of the cladding's stop (20 mm past the arch) and
#: the moulding's (30 mm), so a bloom never lies over either (`simple_car`'s strips; `test_car_wear` reads them).
ARCH_REACH = 0.015
#: Samples along a bloom: the lip is a polyline of this many points, each a quad to the next.
BLOOM_SAMPLES = 9
#: A bloom's depth above the lip, metres (shallowest, deepest), drawn per bloom.
BLOOM_DEPTH = (0.07, 0.15)
ROCKER_DEPTH = (0.025, 0.06)
#: The primer patch: half-sizes (along, up) in metres, how many points its ragged edge has, and its two primers --
#: red oxide on a light paint, grey on a dark one, so it reads on either (the first patch was grey on a silver car,
#: and barely showed). A paint is light above `PRIMER_LIGHT` luminance.
PRIMER_HALF = ((0.15, 0.26), (0.07, 0.11))
PRIMER_POINTS = 12
RED_OXIDE = (0.300, 0.085, 0.060)
PRIMER_LIGHT = 0.30
#: The peeled clear coat: half-sizes (across, along) and points a patch, its edge's wander, and how far toward
#: `PEEL_WHITE` it goes -- milky, the way a failed clear coat goes on any colour. The first patches were 8-point
#: rings wandering 28 % and read as stencilled discs in a row; the second, at 14 points and 45 %, still sat in a
#: column down the roof's middle, every centre drawn from smooth noise, which crowds toward 0.5 (`_u`). Each patch
#: is turned and stretched now, at 18 points wandering 55 %.
PEEL_HALF = ((0.10, 0.24), (0.12, 0.30))
PEEL_POINTS = 18
PEEL_RAG = 0.55
PEEL_WHITE = (0.70, 0.69, 0.66)
PEEL_TOWARD = 0.62
#: Stickers across a bumper: how far a centre wanders from its place, and the pitch between places -- a sticker's
#: width, its own wander and its neighbour's, and 4 cm between. THE FIRST CUT PLACED THREE at 0.45 of the band's
#: half-width: 0.293 m apart on a 1.55 m car, and the matrix found two stickers overlapping on every 1.55 m beater.
STICKER_JITTER = 0.02
STICKER_PITCH = car_stickers.SIZE[0] + 2 * STICKER_JITTER + 0.04


def _clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def _lerp3(a, b, t):
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(3))


def _weighted(rng, pairs):
    total = float(sum(w for _k, w in pairs))
    r = rng.random() * total
    acc = 0.0
    for k, w in pairs:
        acc += w
        if r < acc:
            return k
    return pairs[-1][0]


def _count(rng, lo_hi):
    lo, hi = lo_hi
    return lo + int(rng.random() * (hi - lo + 1))


def _sample(rng, items, weights, n):
    """``n`` of ``items`` without replacement, each draw weighted by what is left."""
    pool = list(zip(items, weights))
    out = []
    for _ in range(min(n, len(pool))):
        total = sum(w for _i, w in pool)
        r = rng.random() * total
        acc = 0.0
        for k, (item, w) in enumerate(pool):
            acc += w
            if r < acc or k == len(pool) - 1:
                out.append(item)
                pool.pop(k)
                break
    return out


def resolve(params, streams) -> dict:
    """A car's history, from its own stream (`car_history`): the history's name, the strengths `finish_rgb` paints
    with, where its rust is, whether it carries a primer patch, how many patches of clear coat it has lost, which
    stickers it carries (indices into `car_stickers.STICKERS`), and a seed every piece's shape is drawn from.

    ``params["history"]`` names one ("kept", "driven", "beater") and wins; the draw is taken either way, so asking for
    a history never moves what a drawn one would have been."""
    rng = streams.stream("car_history")
    drawn = _weighted(rng, HISTORIES)
    asked = (params or {}).get("history", "auto")
    name = asked if asked in WEATHER else drawn
    w = WEATHER[name]
    places = _sample(rng, [(p, s) for p, s, _w in RUST_PLACES], [wt for _p, _s, wt in RUST_PLACES],
                     _count(rng, w["rust"]))
    primer = rng.random() < w["primer"]
    peel = _count(rng, w["peel"])
    n_st = len(car_stickers.STICKERS)
    stickers = _sample(rng, list(range(n_st)), [1.0] * n_st, _count(rng, w["stickers"]))
    seed = int(rng.random() * 1000003)
    return {"history": name, "history_how": "asked" if asked in WEATHER else "drawn",
            "sun": w["sun"], "dust": w["dust"], "rust": tuple(places), "primer": primer, "peel": peel,
            "stickers": tuple(stickers), "wear_seed": seed}


def _noise(a, b, seed, k):
    return van_forms.vnoise(a, b, (seed + 7919 * k) % 1000003)


def _u(seed, a, b=0):
    """A uniform number in [0, 1) from integers: where a piece stands, how big it is, which one. `van_forms.vnoise`
    is for shapes -- it is smooth, and a smooth noise's values crowd toward the middle, so every position drawn from
    it lands near the middle of its range."""
    h = (int(a) * 374761393 + int(b) * 668265263 + int(seed) * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFF) / float(0x1000000)


def _luminance(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def chalk(base):
    """What ``base`` paint goes to in full sun: its own luminance lifted, as a warm grey -- a navy toward a dull
    grey-blue, a red toward a faded pink, a white hardly at all."""
    level = min(CHALK_MAX, max(0.0, _luminance(base)) * CHALK_GAIN + CHALK_LIFT)
    return tuple(level * w for w in CHALK_WARM)


def finish_rgb(co, normal, base, hist) -> tuple:
    """A body corner's paint: ``base``, the car's colour, chalked (`chalk`) on the faces that look at the sky and
    dusted toward the road's colour low down, by the history's strengths, mottled so no two cars fade
    alike. Deterministic from the corner, its face and the history."""
    x, y, z = co
    seed = hist["wear_seed"]
    up = _clamp((normal[2] - 0.30) / 0.60)
    mott = 0.70 + 0.60 * _noise(y * 1.3, x * 1.7 + 3.0, seed, 1)
    c = _lerp3(base, chalk(base), _clamp(SUN_MAX * hist["sun"] * up * mott))
    low = _clamp((DUST_TOP - z) / DUST_TOP)
    grit = 0.55 + 0.45 * _noise(y * 2.1, z * 3.3 + 5.0, seed, 2)
    return _lerp3(c, van_forms.DUST, _clamp(DUST_MAX * hist["dust"] * low * grit))


def _strip(ys, z_lo, z_hi, side, skin_x, proud, rgb_lo, rgb_hi):
    """A band of quads on a door skin: for each y in ``ys`` a point at ``z_lo(y)`` and one at ``z_hi(y)``, both at
    ``side * (skin_x(y) + proud)``. ``rgb_lo`` / ``rgb_hi`` colour the two rows (functions of the point)."""
    verts, rgb, faces = [], [], []
    for y in ys:
        x = side * (skin_x(y) + proud)
        lo, hi = (x, y, z_lo(y)), (x, y, z_hi(y))
        verts += [lo, hi]
        rgb += [rgb_lo(lo), rgb_hi(hi)]
    for k in range(len(ys) - 1):
        a, b, c, d = 2 * k, 2 * k + 2, 2 * k + 3, 2 * k + 1
        faces.append((a, b, c, d) if side > 0 else (a, d, c, b))
    return {"verts": verts, "faces": faces, "rgb": rgb}


def rust_blooms(hist, lay, edge, skin_x, paint, rocker_span=None):
    """The history's rust, as pieces ``{"kind", "side", "verts", "faces", "rgb"}`` on the door skins, `RUST_PROUD`
    off them.

    An arch's bloom hugs the skin's lower edge over the arch -- ``edge(y)``, the height the recipe's sections give the
    skin's bottom at y, which over an arch IS the arch -- from just past one end of the arch to just past the other
    (`lay`'s ``ya_f`` / ``ya_r`` and ``R``, `ARCH_REACH` beyond, never so far that it meets the moulding or the
    cladding, which stop 30 and 20 mm beyond), its top edge ragged, deepest over the wheel. A rocker's runs along the
    skin's lower edge on a seeded stretch of ``rocker_span`` (between the arches; None when the car's lower body is
    clad, and then a rocker rusts nowhere a camera sees). ``paint(co, normal)`` is the body's finish where a piece
    lies: a bloom's lip is `RUST_LIP`, its edge `BLOOM_EDGE` of the way from that paint to `RUST_EDGE`."""
    out = []
    seed = hist["wear_seed"]
    for k, (place, side) in enumerate(hist["rust"]):
        rng_a = _u(seed, 10, k)
        if place in ("front_arch", "rear_arch"):
            ya = lay["ya_f"] if place == "front_arch" else lay["ya_r"]
            reach = lay["R"] + ARCH_REACH
            ys = [ya - reach + 2.0 * reach * i / (BLOOM_SAMPLES - 1) for i in range(BLOOM_SAMPLES)]
            depth = BLOOM_DEPTH[0] + (BLOOM_DEPTH[1] - BLOOM_DEPTH[0]) * rng_a

            def top(y, ya=ya, reach=reach, depth=depth, k=k):
                hump = 0.35 + 0.65 * math.sin(math.pi * _clamp((y - (ya - reach)) / (2.0 * reach)))
                rag = 0.55 + 0.45 * _noise(y * 9.0, 1.3 + k, seed, 11)
                return edge(y) + depth * hump * rag
        else:
            if rocker_span is None:
                continue
            y0, y1 = rocker_span
            if y1 - y0 < 0.30:
                continue
            length = (0.35 + 0.45 * rng_a) * (y1 - y0)
            start = y0 + (y1 - y0 - length) * _u(seed, 12, k)
            ys = [start + length * i / (BLOOM_SAMPLES - 1) for i in range(BLOOM_SAMPLES)]
            depth = ROCKER_DEPTH[0] + (ROCKER_DEPTH[1] - ROCKER_DEPTH[0]) * rng_a

            def top(y, depth=depth, k=k):
                return edge(y) + depth * (0.50 + 0.50 * _noise(y * 7.0, 4.1 + k, seed, 13))
        nrm = (float(side), 0.0, 0.0)
        piece = _strip(ys, lambda y: edge(y) + 0.003, top, side, skin_x, RUST_PROUD,
                       lambda p: RUST_LIP,
                       lambda p: _lerp3(paint((p[0], p[1], p[2]), nrm), RUST_EDGE, BLOOM_EDGE))
        piece.update(kind="rust_" + place, side=side)
        out.append(piece)
    return out


def _blob(cx, cy, ha, hb, points, seed, k, rag=0.28):
    """A ragged closed outline round (cx, cy), half-sizes ha x hb, as (a, b) points: an ellipse whose radius wanders
    by ``rag`` of itself, at two frequencies, so the edge reads as sanded or lifted by hand, not cut by a stencil
    (the van's first primer patch, a smooth ellipse, "read as a pasted grey rectangle"). Every radius stays inside
    the ellipse, so the outline never leaves the box the caller cleared for it."""
    out = []
    for i in range(points):
        t = 2.0 * math.pi * i / points
        n = (0.65 * _noise(math.cos(t) * 1.7 + k, math.sin(t) * 1.7, seed, 20 + k)
             + 0.35 * _noise(math.cos(t) * 4.3 + k, math.sin(t) * 4.3, seed, 60 + k))
        r = (1.0 - rag) + rag * n
        out.append((cx + ha * r * math.cos(t), cy + hb * r * math.sin(t)))
    return out


def _fan(centre, ring):
    """A centre point and a closed ring of points as triangles: verts [centre] + ring."""
    n = len(ring)
    return [centre] + ring, [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]


def primer_patch(hist, door, skin_x, base, side=-1):
    """The history's filled dent, or None: a ragged patch of primer on the front door, `PRIMER_PROUD` off its skin,
    on the kerb side by default (the side a car is parked against and a door is opened into) -- red oxide on a
    light ``base`` paint, grey (`van_forms.PRIMER`) on a dark one.

    ``door`` is the front door's clear panel as the recipe measures it: ``(y0, y1, z0, z1)``, already clear of its
    seams, the handle at its rear and the moulding below. The patch sits in its front part, and a door too small for
    the smallest patch gets none."""
    if not hist["primer"]:
        return None
    y0, y1, z0, z1 = door
    seed = hist["wear_seed"]
    ha = PRIMER_HALF[0][0] + (PRIMER_HALF[0][1] - PRIMER_HALF[0][0]) * _u(seed, 30)
    hb = PRIMER_HALF[1][0] + (PRIMER_HALF[1][1] - PRIMER_HALF[1][0]) * _u(seed, 31)
    ha, hb = min(ha, (y1 - y0) / 2.0), min(hb, (z1 - z0) / 2.0)
    if ha < PRIMER_HALF[0][0] * 0.8 or hb < PRIMER_HALF[1][0] * 0.8:
        return None
    cy = y0 + ha + (y1 - y0 - 2.0 * ha) * 0.35 * _u(seed, 32)
    cz = z0 + hb + (z1 - z0 - 2.0 * hb) * _u(seed, 33)
    ring = [(side * (skin_x(y) + PRIMER_PROUD), y, z)
            for y, z in _blob(cy, cz, ha, hb, PRIMER_POINTS, seed, 1, 0.32)]
    centre = (side * (skin_x(cy) + PRIMER_PROUD), cy, cz)
    verts, faces = _fan(centre, ring)
    if side < 0:
        faces = [(a, c, b) for a, b, c in faces]
    primer = RED_OXIDE if _luminance(base) > PRIMER_LIGHT else van_forms.PRIMER
    rgb = [_lerp3(primer, tuple(0.88 * c for c in primer), _noise(v[1] * 6.0, v[2] * 6.0, seed, 34)) for v in verts]
    return {"kind": "primer", "side": side, "verts": verts, "faces": faces, "rgb": rgb}


def peel_patches(hist, roof, paint):
    """The history's lost clear coat: up to ``hist["peel"]`` ragged patches on the roof's flat top, `PEEL_PROUD`
    above it, each `PEEL_TOWARD` of the way from the paint there to `PEEL_WHITE` -- milky and dull.

    ``roof`` is the flat top as the recipe builds it: ``{"z", "x_half", "y0", "y1"}`` (the greenhouse's top, between
    its front and rear edges). Each patch has its own stretch of the roof's length, anywhere across it and anywhere
    along its stretch, so no two overlap, and stands 3 cm inside every edge."""
    n = hist["peel"]
    if n <= 0:
        return []
    seed = hist["wear_seed"]
    out = []
    span = (roof["y1"] - roof["y0"]) / n
    for k in range(n):
        ha = PEEL_HALF[0][0] + (PEEL_HALF[0][1] - PEEL_HALF[0][0]) * _u(seed, 40, k)
        hb = PEEL_HALF[1][0] + (PEEL_HALF[1][1] - PEEL_HALF[1][0]) * _u(seed, 41, k)
        turn = math.pi * _u(seed, 44, k)
        c, s = abs(math.cos(turn)), abs(math.sin(turn))
        # the turned outline's reach along x and y: every radius is inside its ellipse, and the ellipse inside
        # this box, so clearing the box clears the patch
        ex, ey = ha * c + hb * s, ha * s + hb * c
        k_fit = min(1.0, (roof["x_half"] - 0.03) / ex, (span / 2.0 - 0.03) / ey)
        ha, hb, ex, ey = ha * k_fit, hb * k_fit, ex * k_fit, ey * k_fit
        if min(ha, hb) < 0.04:
            continue
        lo, hi = -roof["x_half"] + 0.03 + ex, roof["x_half"] - 0.03 - ex
        cx = lo + (hi - lo) * _u(seed, 42, k)
        y_lo, y_hi = roof["y0"] + span * k + 0.03 + ey, roof["y0"] + span * (k + 1) - 0.03 - ey
        cy = y_lo + (y_hi - y_lo) * _u(seed, 43, k)
        z = roof["z"] + PEEL_PROUD
        ring = []
        for a, b in _blob(0.0, 0.0, ha, hb, PEEL_POINTS, seed, 5 + k, PEEL_RAG):
            ring.append((cx + a * math.cos(turn) - b * math.sin(turn),
                         cy + a * math.sin(turn) + b * math.cos(turn), z))
        verts, faces = _fan((cx, cy, z), ring)
        up = (0.0, 0.0, 1.0)
        rgb = [_lerp3(paint((v[0], v[1], roof["z"]), up), PEEL_WHITE, PEEL_TOWARD) for v in verts]
        out.append({"kind": "peel", "side": 0, "verts": verts, "faces": faces, "rgb": rgb})
    return out


def sticker_quads(hist, band):
    """The history's stickers on the rear bumper's upper band, ``{"index", "verts", "faces", "uv"}`` each, a quad
    `STICKER_PROUD` off the band, `car_stickers.SIZE`, tilted a degree or two as a hand puts one on.

    ``band`` is the band's rear face as the recipe builds it: ``{"x_half", "y_lo", "z_lo", "y_hi", "z_hi",
    "z_seen"}`` -- the face runs from (y_lo, z_lo) up and in to (y_hi, z_hi), its outward normal toward +y and up,
    and only above ``z_seen`` (the rub strip's top) does a camera see it. A band too short for a sticker carries
    none. As many as the band's width holds, up to three, `STICKER_PITCH` apart, so no two touch however each
    wanders."""
    ids = hist["stickers"]
    if not ids:
        return []
    sw, sh = car_stickers.SIZE
    dy, dz = band["y_hi"] - band["y_lo"], band["z_hi"] - band["z_lo"]
    run = math.hypot(dy, dz)
    vy, vz = dy / run, dz / run                       # up the band
    ny, nz = vz, -vy                                  # its outward normal: +y and up for a rear band
    if ny < 0.0:
        ny, nz = -ny, -nz
    z_lo, z_hi = band["z_seen"] + sh / 2.0 + 0.012, band["z_hi"] - sh / 2.0 - 0.012
    if z_hi < z_lo:
        return []
    cells = car_stickers.cells()
    seed = hist["wear_seed"]
    # the band narrows by 2 cm to its top; a sticker turned 2.5 degrees reaches 2 mm further
    reach = band["x_half"] - 0.02 - sw / 2.0 - STICKER_JITTER - 0.005
    if reach < 0.0:
        return []
    slots = ((-STICKER_PITCH, 0.0, STICKER_PITCH) if reach >= STICKER_PITCH
             else (-STICKER_PITCH / 2.0, STICKER_PITCH / 2.0) if reach >= STICKER_PITCH / 2.0 else (0.0,))
    order = sorted(range(len(slots)), key=lambda s: _u(seed, 50, s))
    out = []
    for k, idx in enumerate(ids[:len(slots)]):
        xc = slots[order[k]] + STICKER_JITTER * (2.0 * _u(seed, 51, k) - 1.0)
        zc = z_lo + (z_hi - z_lo) * _u(seed, 52, k)
        t = (zc - band["z_lo"]) / dz
        yc = band["y_lo"] + dy * t
        yc, zc = yc + ny * STICKER_PROUD, zc + nz * STICKER_PROUD
        tilt = math.radians(2.5 * (2.0 * _u(seed, 53, k) - 1.0))
        ux, uy, uz = math.cos(tilt), -math.sin(tilt) * vy, -math.sin(tilt) * vz
        wx, wy, wz = math.sin(tilt), math.cos(tilt) * vy, math.cos(tilt) * vz
        verts = []
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            verts.append((xc + a * ux * sw / 2.0 + b * wx * sh / 2.0,
                          yc + a * uy * sw / 2.0 + b * wy * sh / 2.0,
                          zc + a * uz * sw / 2.0 + b * wz * sh / 2.0))
        u0, v0, u1, v1 = cells[idx]
        # seen from behind the car (looking along -y), +x is the viewer's LEFT: the sticker reads left to right
        # from x high to x low
        uv = [(u1, v0), (u0, v0), (u0, v1), (u1, v1)]
        # wound so the face looks out of the bumper: x then up the band is (0, -vz, vy), into
        # the car; up the band then x is its negative
        out.append({"index": idx, "verts": verts, "faces": [(0, 3, 2, 1)], "uv": uv})
    return out
