"""The body styles of the cars parked on a 1997 Delaware County street.

The walker, 2026-09-13, after walking a generated street: "we need our cars
to upgrade quite a bit. missing a lot of detail, side windows, transparency,
etc etc". The references were a 1991 Ford Explorer, a 1990s Geo Metro
three-door and a lot of 90s sedans. What 0.78.0 built, measured before this
was written (`tools/coplanar_probe.py` and the shipped
`cover/prop_simple_car_delco_1997_01_w175_d430_h145.glb` of walk 9048):

  * 11 visual parts, 888 tris, one opaque cabin box on a slab;
  * the side panes were built INSIDE the tapered cabin solid: at pane
    height the cabin side stood outboard of the pane's outer face, so the
    only side glass a camera could see was a sliver along the top edge;
  * the glass material was `M_Skin_glass_delco_1997`, alphaMode OPAQUE --
    the delco glass pack (`glass_delco`, Pixelcoat 0.16.0) carries no
    `import_hints.transparency`, so `materials._textured` never blends it,
    and its albedo is a dark teal-grey (#2b3a3d): the "opaque green-grey
    windshield band".

A car is a lower body with wheel arches, a greenhouse of pillars, roof and
separate panes, an interior the panes show, and the parts a street reads a
car by: bumpers, grille, lamps, mirrors, handles, mouldings, a plate. What
the style decides is the SILHOUETTE -- where the windshield starts, how
far back the roof runs, whether the tail is a trunk, a hatch or a tailgate
-- and those are the numbers below.

Each row is one body style as fractions of the slot: heights of ``h``,
lengths of ``d`` measured from the FRONT bumper (the car's nose is at -Y,
the convention simple_car has always had), widths of the body's
half-width. The numbers are read off the cars the walker named, at their
published sizes:

  sedan      Chevrolet Corsica / Ford Taurus: 4.6-5.0 m long, 1.37-1.42 m
             tall, wheelbase 0.55-0.57 of length, belt 0.67 of height,
             windshield base a third of the way back, trunk a sixth.
  hatchback  Geo Metro three-door: 3.80 x 1.59 x 1.39 m, wheelbase 2.36 m
             (0.62), 145/80R12 tyres (r 0.27 m, 0.19 of height), belt 0.62,
             a big glass area and a nearly upright hatch.
  suv        Ford Explorer four-door (1991): 4.78 x 1.78 x 1.73 m,
             wheelbase 2.84 m (0.59), 235/75R15 tyres (r 0.37 m), ground
             clearance 0.21 m, belt 1.08 m (0.62), roof to the tailgate.
  coupe      the sedan with two doors and a shorter greenhouse; kept because
             the genome's prompt rules have always offered it.

The recipe builds every style to the slot's exact (w, d, h) -- a row
SHAPES and never sizes, like `tree_forms`.

Pure: tables and seeded choices; read by `recipes/simple_car.py`, testable
without Blender.
"""
from __future__ import annotations

#: name -> form. Heights are fractions of h, lengths of d from the front
#: bumper, `roof_w` the roof's half-width over the body's.
#:   natural     the (depth, height) window a real car of the style lives in;
#:               `auto` only picks a style whose window holds the slot
#:   wheel_r     tyre radius; clearance: rocker bottom; belt: the door top
#:   fascia      top of the vertical nose face; hood: hood top just behind it
#:   deck        trunk / tail top at the rear; tail: top of the rear face
#:   wheelbase / front_overhang   of d
#:   ws_base, roof_front, roof_rear, bl_base   the greenhouse's side profile:
#:               windshield base, roof front edge, roof rear edge, backlight
#:               (or hatch / tailgate glass) base, all of d
#:   tyre_w      tyre width, metres at a 1.75 m slot (scaled by width)
#:   mirror_out  how far a mirror head stands outboard of the body side, m
#:   pinch_front / pinch_rear   plan-view narrowing at the nose / tail,
#:               a fraction of the half-width lost at the very end
#:   trough      where the open cabin tub ends: at the backlight base (a
#:               trunk behind it) or at the tail (hatch and tailgate)
FORMS = {
    "sedan": {
        "natural": {"depth": (4.2, 5.2), "height": (1.30, 1.56)},
        "doors": ((4, 0.85), (2, 0.15)),
        "wheel_r": 0.215, "clearance": 0.13, "belt": 0.665,
        "fascia": 0.50, "hood": 0.545, "deck": 0.655, "tail": 0.60,
        "wheelbase": 0.575, "front_overhang": 0.200,
        "ws_base": 0.330, "roof_front": 0.470, "roof_rear": 0.715,
        "bl_base": 0.840, "roof_w": 0.80,
        "tyre_w": 0.195, "mirror_out": 0.075,
        "pinch_front": 0.06, "pinch_rear": 0.04, "trough": "backlight",
        "quarter_glass": 0.35, "rack": 0.0, "two_tone": 0.0,
        "wheels": (("hubcap", 0.50), ("alloy", 0.30), ("steel", 0.20)),
        "bumpers": (("body", 0.45), ("black", 0.55)),
        "moulding": 0.80,
        "palette": (("white", 18), ("silver", 12), ("dark_green", 14),
                    ("teal", 8), ("maroon", 14), ("navy", 12), ("black", 6),
                    ("tan", 10), ("red", 6)),
    },
    "coupe": {
        "natural": {"depth": (4.2, 5.0), "height": (1.30, 1.45)},
        "doors": ((2, 1.0),),
        "wheel_r": 0.215, "clearance": 0.125, "belt": 0.66,
        "fascia": 0.48, "hood": 0.535, "deck": 0.65, "tail": 0.60,
        "wheelbase": 0.570, "front_overhang": 0.205,
        "ws_base": 0.345, "roof_front": 0.495, "roof_rear": 0.700,
        "bl_base": 0.830, "roof_w": 0.78,
        "tyre_w": 0.195, "mirror_out": 0.075,
        "pinch_front": 0.06, "pinch_rear": 0.04, "trough": "backlight",
        "quarter_glass": 1.0, "rack": 0.0, "two_tone": 0.0,
        "wheels": (("alloy", 0.55), ("hubcap", 0.45)),
        "bumpers": (("body", 0.60), ("black", 0.40)),
        "moulding": 0.60,
        "palette": (("white", 14), ("silver", 10), ("teal", 12),
                    ("maroon", 12), ("navy", 10), ("black", 12), ("red", 16),
                    ("dark_green", 8)),
    },
    "hatchback": {
        "natural": {"depth": (3.6, 4.35), "height": (1.30, 1.56)},
        "doors": ((2, 0.70), (4, 0.30)),
        "wheel_r": 0.192, "clearance": 0.12, "belt": 0.625,
        "fascia": 0.435, "hood": 0.48, "deck": 0.625, "tail": 0.60,
        "wheelbase": 0.620, "front_overhang": 0.170,
        "ws_base": 0.260, "roof_front": 0.440, "roof_rear": 0.885,
        "bl_base": 0.965, "roof_w": 0.82,
        "tyre_w": 0.155, "mirror_out": 0.070,
        "pinch_front": 0.10, "pinch_rear": 0.05, "trough": "tail",
        "quarter_glass": 1.0, "rack": 0.0, "two_tone": 0.0,
        "wheels": (("hubcap", 0.60), ("steel", 0.40)),
        "bumpers": (("black", 0.80), ("body", 0.20)),
        "moulding": 0.95,
        "palette": (("sky_blue", 14), ("white", 16), ("red", 14),
                    ("silver", 10), ("teal", 12), ("navy", 8),
                    ("maroon", 8), ("black", 6)),
    },
    "suv": {
        "natural": {"depth": (4.1, 5.2), "height": (1.58, 1.76)},
        "doors": ((4, 0.80), (2, 0.20)),
        "wheel_r": 0.212, "clearance": 0.19, "belt": 0.625,
        "fascia": 0.535, "hood": 0.565, "deck": 0.625, "tail": 0.615,
        "wheelbase": 0.595, "front_overhang": 0.178,
        "ws_base": 0.290, "roof_front": 0.410, "roof_rear": 0.955,
        "bl_base": 0.978, "roof_w": 0.86,
        "tyre_w": 0.235, "mirror_out": 0.085,
        "pinch_front": 0.04, "pinch_rear": 0.02, "trough": "tail",
        "quarter_glass": 1.0, "rack": 0.80, "two_tone": 0.70,
        "wheels": (("alloy", 0.70), ("steel", 0.30)),
        "bumpers": (("grey", 0.65), ("black", 0.35)),
        "moulding": 0.0,
        "palette": (("dark_green", 22), ("maroon", 16), ("white", 14),
                    ("black", 12), ("navy", 12), ("tan", 12),
                    ("silver", 8), ("teal", 4)),
    },
}

#: What `auto` chooses between, and how often, before the slot's
#: proportions narrow it. The coupe is reachable by asking for it.
AUTO_POOL = (("sedan", 0.50), ("hatchback", 0.25), ("suv", 0.25))

#: Seeded variation WITHIN a style, as an absolute +/- on each fraction.
#: Small on purpose: two sedans on a block differ the way a Corsica differs
#: from a Taurus, not the way a sedan differs from a van.
JITTER = {"belt": 0.012, "hood": 0.015, "fascia": 0.012, "deck": 0.010,
          "ws_base": 0.012, "roof_front": 0.012, "roof_rear": 0.015,
          "bl_base": 0.008, "wheelbase": 0.010, "front_overhang": 0.008,
          "roof_w": 0.020}

#: THE 1990s PAINT PALETTE. Linear RGB, the space Blender's Base Color and
#: glTF's baseColorFactor are both in; the tintable `metal_painted` pack
#: multiplies these into an achromatic surface. 1990s colour charts ran to
#: dark green (the most popular new-car colour of 1996-97), teal, maroon,
#: navy, white and silver; the walker's Metro is the sky blue.
PALETTE = {
    "white": (0.78, 0.78, 0.74),
    "silver": (0.46, 0.48, 0.50),
    "dark_green": (0.035, 0.11, 0.065),
    "teal": (0.035, 0.24, 0.23),
    "maroon": (0.20, 0.025, 0.04),
    "navy": (0.025, 0.045, 0.14),
    "black": (0.022, 0.022, 0.024),
    "tan": (0.46, 0.36, 0.22),
    "red": (0.45, 0.03, 0.03),
    "sky_blue": (0.18, 0.46, 0.78),
}

#: Lower cladding colours for a two-tone SUV: the Explorer's tan or silver
#: band under a pinstripe.
CLADDING = {"tan": (0.42, 0.34, 0.22), "silver": (0.40, 0.42, 0.44),
            "grey": (0.20, 0.21, 0.22)}

#: Interior cloth, flat path only (the canvas pack is not tintable).
INTERIOR = {"grey": (0.24, 0.24, 0.25), "tan": (0.40, 0.33, 0.24),
            "blue_grey": (0.18, 0.21, 0.27)}

DEFAULT = "sedan"


def _weighted(rng, pairs):
    total = float(sum(w for _k, w in pairs))
    r = rng.random() * total
    acc = 0.0
    for k, w in pairs:
        acc += w
        if r < acc:
            return k
    return pairs[-1][0]


def fits(style: str, depth: float, height: float) -> bool:
    nat = FORMS[style]["natural"]
    return (nat["depth"][0] - 1e-6 <= depth <= nat["depth"][1] + 1e-6
            and nat["height"][0] - 1e-6 <= height <= nat["height"][1] + 1e-6)


def _distance(style, depth, height):
    """How far a slot is from a style's natural window, in window widths."""
    nat = FORMS[style]["natural"]
    out = 0.0
    for v, (lo, hi) in ((depth, nat["depth"]), (height, nat["height"])):
        span = max(1e-6, hi - lo)
        if v < lo:
            out += (lo - v) / span
        elif v > hi:
            out += (v - hi) / span
    return out


def pick_style(requested, dims: dict, rng) -> tuple[str, str]:
    """(style, how) for a plan's ``body_style`` param and the slot's dims.

    A named style is built as asked, at whatever size the slot is -- an SUV
    in a 1.45 m slot is a squat SUV, and that is the caller's call. `auto`
    (or anything the table does not hold) picks from `AUTO_POOL` among the
    styles whose natural window holds the slot's depth and height, weighted;
    when none does, the nearest window wins outright. The draw is taken from
    ``rng`` either way, so asking for a style never shifts what an `auto`
    build of the same seed would otherwise draw next.
    """
    r = rng.random()
    if requested in FORMS:
        return requested, "asked"
    d, h = float(dims["depth"]), float(dims["height"])
    pool = [(s, w) for s, w in AUTO_POOL if fits(s, d, h)]
    if not pool:
        best = min((s for s, _w in AUTO_POOL), key=lambda s: _distance(s, d, h))
        return best, "nearest"
    total = sum(w for _s, w in pool)
    acc = 0.0
    for s, w in pool:
        acc += w / total
        if r < acc:
            return s, "auto"
    return pool[-1][0], "auto"


def pick_paint(plan: dict, style: str, rng) -> tuple[str, tuple]:
    """(name, linear rgb). The prompt's colour, or a style block that says
    ``"paint": "fixed"`` (police black, racing red, the era styles), wins;
    otherwise the style's 1990s palette, weighted, from ``rng``."""
    r_draw = rng.random()
    block = plan.get("style_block") or {}
    colour = [round(float(c), 4) for c in plan.get("color", [])]
    styled = [round(float(c), 4) for c in block.get("color", colour)]
    if colour and (colour != styled or block.get("paint") == "fixed"):
        return "asked", tuple(colour)
    pairs = FORMS[style]["palette"]
    total = float(sum(w for _k, w in pairs))
    acc = 0.0
    for name, w in pairs:
        acc += w / total
        if r_draw < acc:
            return name, PALETTE[name]
    name = pairs[-1][0]
    return name, PALETTE[name]


def resolve(plan: dict, streams) -> dict:
    """Every decision the recipe executes, from named streams: the style
    (`car_style`), its proportions (`car_form`), paint (`car_paint`) and
    trim (`car_trim`). Separate streams so adding a trim decision later
    never re-rolls a car's paint or silhouette."""
    params = plan.get("params") or {}
    dims = plan["dimensions"]
    style, how = pick_style(params.get("body_style", "auto"), dims,
                            streams.stream("car_style"))
    base = FORMS[style]
    rng = streams.stream("car_form")
    f = {"style": style, "style_how": how}
    for key, val in base.items():
        if isinstance(val, float) and key in JITTER:
            f[key] = val + (rng.random() * 2.0 - 1.0) * JITTER[key]
        else:
            f[key] = val
    trim = streams.stream("car_trim")
    asked_doors = int(params.get("doors", 0) or 0)
    doors_drawn = _weighted(trim, base["doors"])
    f["doors"] = 2 if 0 < asked_doors <= 3 else (4 if asked_doors >= 4 else doors_drawn)
    f["quarter_glass"] = trim.random() < base["quarter_glass"]
    f["rack"] = trim.random() < base["rack"]
    f["two_tone"] = trim.random() < base["two_tone"]
    f["wheel_kind"] = _weighted(trim, base["wheels"])
    f["bumper_kind"] = _weighted(trim, base["bumpers"])
    f["moulding"] = trim.random() < base["moulding"]
    f["blackout_b"] = trim.random() < 0.85
    f["mirror_black"] = trim.random() < 0.75
    f["cladding"] = _weighted(trim, (("tan", 0.5), ("silver", 0.3), ("grey", 0.2)))
    f["interior"] = _weighted(trim, (("grey", 0.5), ("tan", 0.3), ("blue_grey", 0.2)))
    f["paint_name"], f["paint"] = pick_paint(plan, style, streams.stream("car_paint"))
    return f


#: The nose and tail faces stand this far inside the bumpers' outer faces.
BUMPER_BURY = 0.07
#: Radial gap between a tyre and its arch.
ARCH_GAP = 0.035
#: Roof rack height: the rails' tops are the slot's height.
RACK_H = 0.065
#: The side glass starts this far behind the windshield base at the belt.
A_SIDE_BELT = 0.10
#: How far a tyre's outer face sits inside the door skin's plane (0.78.0's
#: WHEEL_TUCK: the tyre-in-the-body-plane z-fight is what it fixed).
WHEEL_TUCK = 0.02


def layout(form: dict, width: float, depth: float, height: float) -> dict:
    """The car's governing numbers in metres, in the recipe's build frame:
    x across (0 on the centre line), y along (nose at -depth/2), z up from
    the ground (the recipe builds base-up; `build_module` re-centres).

    Pure so the dims contract can be tested without Blender: the slot's
    width is the mirror heads' outer faces (`hw + mirror_out`), its depth
    the bumpers' outer faces, its height the roof or the rack's rails.
    Clamps keep the greenhouse clear of the arches and the tail at any size
    the genome allows."""
    W, L, H = float(width), float(depth), float(height)
    f = form
    rack_h = RACK_H if f.get("rack") else 0.0
    out = {"width": W, "depth": L, "height": H, "rack_h": rack_h,
           "zr": H - rack_h,
           "wheel_r": f["wheel_r"] * H, "clear": f["clearance"] * H,
           "belt": f["belt"] * H, "fascia": f["fascia"] * H,
           "hood": f["hood"] * H, "deck": f["deck"] * H,
           "tail": f["tail"] * H,
           "hw": W / 2.0 - f["mirror_out"],
           "tyre_w": f["tyre_w"] * W / 1.75,
           "yF0": -L / 2.0, "yR0": L / 2.0}
    out["y0"] = out["yF0"] + BUMPER_BURY
    out["yt"] = out["yR0"] - BUMPER_BURY

    def Y(frac):
        return out["yF0"] + frac * L

    out["ya_f"] = Y(f["front_overhang"])
    out["ya_r"] = Y(f["front_overhang"] + f["wheelbase"])
    out["R"] = out["wheel_r"] + ARCH_GAP
    out["y_bl"] = min(Y(f["bl_base"]), out["yt"] - 0.03)
    out["y_rr"] = min(Y(f["roof_rear"]), out["y_bl"] - 0.02)
    out["y_ws"] = max(Y(f["ws_base"]), out["ya_f"] + out["R"] + 0.10)
    out["y_rf"] = max(Y(f["roof_front"]), out["y_ws"] + 0.25)
    out["roll"] = 0.025 * L
    trunk = f["trough"] == "backlight"
    out["trunk"] = trunk
    # where the open tub ends: at the backlight over a trunk, near the tail
    # under a hatch or tailgate (clear of the rear glass's buried edge)
    out["y_te"] = (out["y_bl"] if trunk
                   else min(out["yt"] - 0.10, out["y_bl"] - 0.05))
    out["tail_roll"] = (out["yt"] - out["roll"] if trunk
                        else max(out["y_bl"] + 0.01, out["yt"] - out["roll"]))
    out["tyre_outer_x"] = out["hw"] - WHEEL_TUCK
    out["mirror_outer_x"] = out["hw"] + f["mirror_out"]
    return out


def door_split(form: dict) -> list:
    """Side openings between pillars, front to rear, as (kind, weight):
    the weights share the side glass length between the openings. A
    two-door has one long door glass; a four-door two; a quarter glass
    follows where the style has one."""
    out = [("door_f", 1.0)] if form["doors"] >= 4 else [("door_f", 1.45)]
    if form["doors"] >= 4:
        out.append(("door_r", 0.92))
    if form["quarter_glass"]:
        out.append(("quarter", 0.42 if form["style"] in ("sedan", "coupe")
                    else 0.80))
    return out


def pane_names(form: dict) -> list:
    """Every pane the recipe builds, one object each: windshield, one per
    side opening per side (L is +X, the driver's side of a car whose nose is
    at -Y), backlight. The recipe names its panes from this list."""
    names = ["Car_Glass_Windshield"]
    for side in ("L", "R"):
        for kind, _w in door_split(form):
            names.append({"door_f": f"Car_Glass_Door_F{side}",
                          "door_r": f"Car_Glass_Door_R{side}",
                          "quarter": f"Car_Glass_Quarter_{side}"}[kind])
    names.append("Car_Glass_Backlight")
    return names
