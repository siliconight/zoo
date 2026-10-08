"""The responders' cruiser: a classic 1990s Crown Victoria police sedan (Zoo 1.86.0, roadmap 212).

The walker, 2026-10-08, asked what the responders drive: "I would think a
classic 1990s Crown Victoria" -- and for the department, "Delco County Police
Dept. as a start?". The comps, six photographs read for format only, are
`docs/reference/CRUISER_COMPS.md` at the factory root. No real department's
name, seal, number or plate is reproduced.

THE CAR IS `simple_car`'s, drawn as the `cruiser` row of `car_forms.FORMS` (a
Crown Victoria's proportions) and pinned by `pin_form`: four doors, the
quarter glass, black steel wheels, body-colour bumpers, a side moulding, the
blue-grey cloth of the walker's interior photo, and the same car every time
(no jitter). What this file adds is pure, and tested without Blender:

  * THE KIT (`kit`): the parts that make a sedan a police car, as boxes in
    the recipe's build frame -- a light bar across the roof (red on the
    driver's side, blue on the other, a clear centre), a push bar on the
    nose, a spotlight on the driver's A-pillar, a whip on the trunk, and
    inside, a partition behind the front seats and a radio console between
    them.
  * THE LIVERY (`LIVERIES`, `livery_art`, `livery_uv`, `finish_rgb`): one
    image on one material, the getaway van's ghost technique. The sides map
    into the image by their (y, z); the image carries the two-tone and the
    lettering, so a door's edge is as sharp as a texel. Every other face
    samples the image's white patch and takes its colour per corner -- the
    roof white or black, the hood and trunk the body's colour -- because
    those faces meet at the body's own edges, where a per-corner colour is
    sharp too.

THE SLOT. Width is the mirror heads' outer faces (a Crown Victoria's 1.986 m
body and `mirror_out` 0.105 a side), depth the push bar's front to the rear
bumper's back (the car's 5.385 m and the bar's `PUSH_PROUD`), height the
light bar's top over the 1.443 m roof. `body_dims` turns a slot into the
sedan `simple_car` builds; the kit stands on it.

Build frame, as `simple_car`'s: x across (+X the driver's side), y along
(the nose at -Y), z up from the ground.
"""
from __future__ import annotations

import hashlib

from . import car_forms

#: The slot's defaults (genome `cruiser.json`): 1.986 + 2 x 0.105 wide,
#: 5.385 + PUSH_PROUD long, 1.443 + BAR_TOP tall.
SLOT = (2.196, 5.545, 1.578)

# --- the kit ------------------------------------------------------------------

#: THE LIGHT BAR: a 1990s low bar, 48 in long, across the roof over the
#: front doors' rear edge. Its feet stand into the roof by `SINK` so no face
#: of the bar shares the roof's plane.
BAR_LEN = 1.22
BAR_DEPTH = 0.30
BAR_FOOT = 0.035          # roof to the bar's base
BAR_BASE = 0.035          # the black base's height
BAR_LENS = 0.065          # the lenses' height over the base
BAR_TOP = BAR_FOOT + BAR_BASE + BAR_LENS
#: Where along the roof, from its front edge (0) to its rear edge (1).
BAR_ALONG = 0.40
#: The clear centre ("takedown") section's half-width.
BAR_CLEAR_HALF = 0.10
#: THE PUSH BAR: a black steel frame ahead of the grille, two uprights joined
#: at the top and low down, braced back into the bumper.
PUSH_PROUD = 0.16         # the bar's front face ahead of the bumper's
PUSH_X = 0.30             # the uprights' centres, either side of the centre line
PUSH_TUBE = 0.06          # square tube
PUSH_TOP_OVER_FASCIA = 0.05
#: THE SPOTLIGHT: a lamp head on a handle through the driver's A-pillar.
SPOT_R = 0.06
SPOT_LEN = 0.14
SPOT_OVER_BELT = 0.20
#: THE WHIP: an antenna on the trunk lid behind the backlight.
WHIP_H = 0.55
WHIP_R = 0.004
#: Inside: the partition behind the front seats, and the radio console.
PARTITION_BAR = 0.025
#: The partition stands this far behind the front seat backs' rear face, and
#: its posts this far short of the door cards' (`simple_car`'s ``interior``).
#: The first cut stood it at a guessed y_fs + 0.38, through the headrests, its
#: posts 1.37 mm off their sides, and its ends 2 mm past the door cards'
#: inner face.
PARTITION_BEHIND = 0.03
#: Every kit part runs this far INTO what it stands on (no shared plane).
SINK = 0.01
#: Where one kit part meets another edge on, the smaller stands this far in
#: from the larger's faces: twice `tools/coplanar_probe.py`'s 2 mm window, so
#: no face it keeps is read as coincident. The first census found the
#: partition's posts 1-2 mm inside its rails' faces and the rails' ends flush
#: with its outer posts.
INSET = 0.004

#: The kit's colours, on `car_forms.PAINTED`: one material with the car's
#: other painted parts, and named in their part family (the recipe's
#: `names`), so the export merges the kit into their mesh and it costs no
#: draw call of its own. The lenses are unlit, like `simple_car`'s lamps: a
#: night that wants them lit gives them their own material, which is a draw.
#: The steel wheels: charcoal, between the tyre's 0.035 and simple_car's
#: grey 0.20 -- the comps' black steel, kept apart from the tyre.
WHEEL_RGB = (0.08, 0.08, 0.085)
KIT_RGB = {
    "kit_black": (0.020, 0.020, 0.022),
    "lens_red": (0.55, 0.02, 0.02),
    "lens_blue": (0.02, 0.07, 0.60),
    "lens_clear": (0.80, 0.82, 0.85),
}


def body_dims(width: float, depth: float, height: float) -> tuple:
    """The sedan `simple_car` builds for a cruiser slot: as wide, the push bar
    off its length, the light bar off its height."""
    return float(width), float(depth) - PUSH_PROUD, float(height) - BAR_TOP


def pin_form(form: dict) -> dict:
    """The drawn form with the cruiser's own choices pinned. Jitter is undone
    -- the same car in every level, as the getaway van is -- and the trim
    the comps all agree on is set rather than drawn."""
    f = dict(form)
    for key in car_forms.JITTER:
        if key in car_forms.CRUISER:
            f[key] = car_forms.CRUISER[key]
    f.update({"doors": 4, "quarter_glass": True, "rack": False, "two_tone": False,
              "wheel_kind": "steel", "bumper_kind": "body", "moulding": True,
              "blackout_b": True, "mirror_black": True, "interior": "blue_grey",
              # white: the livery paints the body, and white is the identity
              # under it (`finish_rgb`)
              "paint_name": "livery", "paint": (1.0, 1.0, 1.0)})
    return f


def _box(lo, hi):
    return (tuple(float(v) for v in lo), tuple(float(v) for v in hi))


def kit(lay: dict, seat: tuple, interior: dict) -> dict:
    """{group: [(lo, hi) boxes]} in the build frame, from `car_forms.layout`
    of the body, the driver's seat attachment ``seat`` = (x, y, z), and
    `simple_car`'s ``interior``: the cabin floor's top, the front seat backs'
    rear face, the rear seat's front (or None) and the door cards' inner face.
    Groups: `kit_black`, `lens_red`, `lens_blue`, `lens_clear`. Raises when
    the partition does not fit between the front and rear seats."""
    zr, hw = lay["zr"], lay["hw"]
    out = {k: [] for k in KIT_RGB}
    # the light bar
    yb = lay["y_rf"] + BAR_ALONG * (lay["y_rr"] - lay["y_rf"])
    hl, hd = BAR_LEN / 2.0, BAR_DEPTH / 2.0
    z_base0 = zr + BAR_FOOT
    z_lens0 = z_base0 + BAR_BASE
    z_top = z_lens0 + BAR_LENS
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            x, y = sx * (hl - 0.12), yb + sy * (hd - 0.06)
            out["kit_black"].append(_box((x - 0.025, y - 0.025, zr - SINK),
                                         (x + 0.025, y + 0.025, z_base0 + SINK)))
    out["kit_black"].append(_box((-hl, yb - hd, z_base0), (hl, yb + hd, z_lens0)))
    inset = 0.012
    out["lens_red"].append(_box((BAR_CLEAR_HALF, yb - hd + inset, z_lens0 - SINK),
                                (hl - inset, yb + hd - inset, z_top)))
    out["lens_blue"].append(_box((-hl + inset, yb - hd + inset, z_lens0 - SINK),
                                 (-BAR_CLEAR_HALF, yb + hd - inset, z_top)))
    out["lens_clear"].append(_box((-BAR_CLEAR_HALF + 0.004, yb - hd + inset + 0.004, z_lens0 - SINK),
                                  (BAR_CLEAR_HALF - 0.004, yb + hd - inset - 0.004, z_top - 0.006)))
    # the push bar, its front face at the slot's front
    y_face = lay["yF0"] - PUSH_PROUD
    z_lo = lay["clear"] + 0.05
    z_hi = lay["fascia"] + PUSH_TOP_OVER_FASCIA
    t = PUSH_TUBE
    for sx in (-1.0, 1.0):
        x = sx * PUSH_X
        out["kit_black"].append(_box((x - t / 2.0, y_face, z_lo), (x + t / 2.0, y_face + t, z_hi)))
        # two braces back into the bumper, which stands BUMPER_BURY proud of the
        # nose; the lower one clear under the lower bar (at z_lo + 0.08 its top
        # met the bar's underside face to face)
        for z in (z_lo + 0.04, z_hi - 0.20):
            out["kit_black"].append(_box((x - 0.02, y_face + t - SINK, z - 0.02),
                                         (x + 0.02, lay["yF0"] + 0.05, z + 0.02)))
    out["kit_black"].append(_box((-PUSH_X - t / 2.0 + SINK, y_face + 0.005, z_hi - t),
                                 (PUSH_X + t / 2.0 - SINK, y_face + t - 0.005, z_hi - 0.004)))
    out["kit_black"].append(_box((-PUSH_X - t / 2.0 + SINK, y_face + 0.005, z_lo + 0.10),
                                 (PUSH_X + t / 2.0 - SINK, y_face + t - 0.005, z_lo + 0.10 + t * 0.8)))
    # the spotlight: up the driver's (+X) A-pillar, its head outside the glass
    zs = lay["belt"] + SPOT_OVER_BELT
    k = SPOT_OVER_BELT / max(1e-6, zr - lay["belt"])
    ys = lay["y_ws"] + (lay["y_rf"] - lay["y_ws"]) * k + 0.03
    xs = hw - 0.02 + SPOT_R
    out["kit_black"].append(_box((xs - SPOT_R, ys - SPOT_LEN / 2.0, zs - SPOT_R),
                                 (xs + SPOT_R, ys + SPOT_LEN / 2.0, zs + SPOT_R)))
    out["lens_clear"].append(_box((xs - SPOT_R + 0.01, ys - SPOT_LEN / 2.0 - 0.004, zs - SPOT_R + 0.01),
                                  (xs + SPOT_R - 0.01, ys - SPOT_LEN / 2.0 + SINK, zs + SPOT_R - 0.01)))
    out["kit_black"].append(_box((hw - 0.12, ys - 0.012, zs - 0.012), (xs - SPOT_R + SINK, ys + 0.012, zs + 0.012)))
    # the whip, on the trunk lid behind the backlight
    yw = lay["y_bl"] + 0.25
    out["kit_black"].append(_box((-0.02, yw - 0.02, lay["deck"] - SINK), (0.02, yw + 0.02, lay["deck"] + 0.02)))
    out["kit_black"].append(_box((-WHIP_R, yw - WHIP_R, lay["deck"] + 0.02 - SINK),
                                 (WHIP_R, yw + WHIP_R, lay["deck"] + WHIP_H)))
    # inside: the partition, a frame behind the front seat backs from the
    # floor up, and the console on the floor between the seats
    xd, y_fs, seat_z = seat
    floor = interior["floor_top"]
    b = PARTITION_BAR
    yp = interior["back_rear"] + PARTITION_BEHIND
    rear = interior.get("rear_front")
    if rear is not None and yp + b > rear - SINK:
        raise ValueError("cruiser: the partition at y %.3f .. %.3f does not fit before the rear seat at %.3f"
                         % (yp, yp + b, rear))
    xi = interior["card_in"] - INSET
    # into the floor by INSET, not SINK: the floor is 22 mm thick and the
    # body's pan lies 12 mm under its top, so a 10 mm sink stood the rail's
    # underside 2 mm over the pan (the second census, 333 cm2 face to face)
    z0, z1 = floor - INSET, zr - 0.07
    # the rails, their ends inside the outer posts
    out["kit_black"].append(_box((-xi + INSET, yp, z0), (xi - INSET, yp + b, z0 + b)))
    out["kit_black"].append(_box((-xi + INSET, yp, z1 - b), (xi - INSET, yp + b, z1)))
    # the posts, inside the rails' faces and into the rails
    for x in (-xi, -xi / 3.0, xi / 3.0, xi - b):
        out["kit_black"].append(_box((x, yp + INSET, z0 + b - SINK), (x + b, yp + b - INSET, z1 - b + SINK)))
    # the middle bar, inside the posts' faces, its ends in the outer posts
    out["kit_black"].append(_box((-xi + SINK, yp + 2.0 * INSET, (z0 + z1) / 2.0 - b / 2.0),
                                 (xi - SINK, yp + b - 2.0 * INSET, (z0 + z1) / 2.0 + b / 2.0)))
    out["kit_black"].append(_box((-0.09, y_fs - 0.42, floor - INSET), (0.09, y_fs + 0.10, seat_z + 0.02)))
    out["kit_black"].append(_box((-0.07, y_fs - 0.38, seat_z + 0.02 - SINK), (0.07, y_fs - 0.22, seat_z + 0.10)))
    return out


# --- the livery -------------------------------------------------------------------

#: THE TWO LIVERIES the first frames show (the comps hold both). `margin` is
#: the colour of the side outside the art's marks; `roof` the roof's.
LIVERIES = {
    "black_white": {"body": (0.012, 0.012, 0.014), "margin": (0.012, 0.012, 0.014),
                    "roof": (0.86, 0.86, 0.84), "panel": (0.86, 0.86, 0.84),
                    "ink": (0.012, 0.012, 0.014), "seal": (0.62, 0.48, 0.10)},
    "white_blue": {"body": (0.86, 0.86, 0.84), "margin": (0.86, 0.86, 0.84),
                   "roof": (0.86, 0.86, 0.84), "stripe": (0.03, 0.10, 0.42),
                   "ink": (0.86, 0.86, 0.84), "seal": (0.62, 0.48, 0.10)},
}
DEFAULT_LIVERY = "black_white"

#: The department, as the walker named it, and what the sides carry.
DEPARTMENT = ("DELCO COUNTY", "POLICE")
MOTTO = "WE'LL GET YOUSE"
UNIT = "214"
#: Cap heights on the car, metres.
CAP_DEPARTMENT = 0.07
CAP_POLICE = 0.15
CAP_MOTTO = 0.034
#: The seals' radius, and their centres' distance in from the doors' ends.
SEAL_R = 0.075
SEAL_FROM_END = 0.20
#: `simple_car`'s side moulding: its half-height (the recipe builds it
#: zm +/- 0.024), and the clear space kept between it and a mark.
MOULDING_HALF = 0.024
MARK_GAP = 0.03
#: `simple_car`'s door handles hang from this far under the door skin's top
#: (z2_at - 0.075): the marks stay under them. The first frames ran the
#: front door's handle 7 mm into DELCO COUNTY.
HANDLE_DROP = 0.075
#: Between POLICE and the department over it.
DEPARTMENT_GAP = 0.02
#: THE MARKS SCALE TO THE DOOR. Their sizes above are the default slot's; a
#: lower car has less door between the moulding and the handles, and its
#: marks (caps, gap, stripe, seals) shrink together to fit it. The genome's
#: lowest corner needs 0.92. Under this the car is one the livery was not
#: drawn for, and it is refused rather than lettered too small to read.
MARK_SCALE_MIN = 0.8
#: On the stripe, the seals stand this far in from the nose and tail faces.
STRIPE_SEAL_IN = 0.55
#: The blue stripe's half-height, and the department's cap on one line in it.
STRIPE_HALF = 0.11
CAP_STRIPE = 0.10
#: Pixels a metre, both ways, so a letter is not stretched on the car.
ART_PPM = 380
#: The art's reach above the belt and below the rocker, metres.
ART_OVER = 0.12
#: The patches every non-side face samples: white (the identity under a
#: per-corner colour) and the margin colour. Each `PATCH_PX` square, in a
#: column right of the art, far enough from it that a texel's filter never
#: mixes them.
PATCH_PX = 16
SIDE_COS = 0.9            # |normal.x| at or over this is a side face


def art_frame(lay: dict) -> dict:
    """Where the art lies on the side: its (y, z) span in metres and its size
    in pixels. The art runs the body's whole side, nose face to tail face,
    and from the ground's clearance to `ART_OVER` above the belt."""
    y0, y1 = lay["y0"], lay["yt"]
    z0, z1 = lay["clear"] - 0.02, lay["belt"] + ART_OVER
    w = int(round((y1 - y0) * ART_PPM))
    h = int(round((z1 - z0) * ART_PPM))
    return {"y0": y0, "y1": y1, "z0": z0, "z1": z1, "w": w, "h": h,
            "W": w + 3 * PATCH_PX, "H": max(h, 2 * PATCH_PX + 8)}


def patch_uv(frame: dict, which: str) -> tuple:
    """The UV at the centre of the white or the margin patch."""
    x = frame["w"] + 2 * PATCH_PX
    y = PATCH_PX / 2.0 + (0 if which == "white" else PATCH_PX + 4)
    return ((x + 0.5) / frame["W"], 1.0 - (y + 0.5) / frame["H"])


def livery_uv(co, normal, frame: dict) -> tuple:
    """Where a body corner samples the art. A face looking along X maps by its
    (y, z), read the right way round from outside on either side, clamped to
    the art so a face that runs past its edge reads the margin; any other face
    samples the white patch and keeps its per-corner colour."""
    nx = normal[0]
    if abs(nx) < SIDE_COS:
        return patch_uv(frame, "white")
    x, y, z = co
    u = (y - frame["y0"]) / (frame["y1"] - frame["y0"])
    if nx < 0.0:
        u = 1.0 - u
    v = (z - frame["z0"]) / (frame["z1"] - frame["z0"])
    u = min(1.0, max(0.0, u)) * frame["w"] / frame["W"]
    v = min(1.0, max(0.0, v))
    # v in the art's own pixels: its rows are the top `h` of the image
    v = 1.0 - (1.0 - v) * frame["h"] / frame["H"]
    return (u, v)


def finish_rgb(co, normal, lay: dict, livery: str) -> tuple:
    """A body corner's colour under the art. A side face is white -- the art
    paints it. The roof's top takes the livery's roof; everything else, the
    livery's body colour."""
    lv = LIVERIES[livery]
    if abs(normal[0]) >= SIDE_COS:
        return (1.0, 1.0, 1.0)
    if normal[2] > 0.85 and co[2] > lay["belt"] + 0.15:
        return lv["roof"]
    return lv["body"]


def _srgb8(lin):
    c = 12.92 * lin if lin <= 0.0031308 else 1.055 * lin ** (1.0 / 2.4) - 0.055
    return int(round(255.0 * max(0.0, min(1.0, c))))


def _rgb8(rgb):
    return tuple(_srgb8(c) for c in rgb)


def livery_art(lay: dict, door_edges: list, door_skin_z: tuple, livery: str = DEFAULT_LIVERY,
               moulding_z: float | None = None) -> dict:
    """The livery's image: the side's two-tone and its marks, then the white
    and margin patches. Returns ``{"png", "name", "size", "frame", "lines"}``;
    ``lines`` holds each set line's ink box, ``scale`` the marks' size against
    the default slot's. Raises when a line does not set -- a door that
    silently lost its department would look like a choice -- and when the
    marks over the moulding would have to shrink under `MARK_SCALE_MIN` to
    stay under the door handles.

    THE MARKS STAND ABOVE THE MOULDING, the motto below it (the first frames
    ran the black rub strip through POLICE). ``moulding_z`` is the strip's
    centre line as `simple_car` built it, or None for a car without one."""
    from . import paint as PT
    from . import smooth_type as ST
    lv = LIVERIES[livery]
    fr = art_frame(lay)
    img = PT.Img(fr["W"], fr["H"], _rgb8(lv["margin"]))

    def px_y(y):                     # metres along -> pixels from the art's left
        return (y - fr["y0"]) * ART_PPM

    def px_z(z):                     # metres up -> pixels from the image's top
        return (fr["z1"] - z) * ART_PPM

    face = ST.owned("maker")         # an institution's lettering
    lines = []
    ink = _rgb8(lv["ink"])
    if moulding_z is not None:
        z_lo = moulding_z + MOULDING_HALF + MARK_GAP
        z_motto = moulding_z - MOULDING_HALF - MARK_GAP - CAP_MOTTO / 2.0
    else:
        z_lo = door_skin_z[0] + 0.30
        z_motto = z_lo - MARK_GAP - CAP_MOTTO / 2.0
    ceiling = door_skin_z[1] - HANDLE_DROP - 0.01
    need = (CAP_POLICE + DEPARTMENT_GAP + CAP_DEPARTMENT if livery == "black_white"
            else 2.0 * STRIPE_HALF)
    s = min(1.0, (ceiling - z_lo) / need)
    if s < MARK_SCALE_MIN:
        raise ValueError("the cruiser's marks need %.3f m over the moulding and have %.3f m under the door "
                         "handles: %.2f of their size, under %.2f" % (need, ceiling - z_lo, s, MARK_SCALE_MIN))
    cap_police, cap_department, gap = CAP_POLICE * s, CAP_DEPARTMENT * s, DEPARTMENT_GAP * s
    stripe_half, cap_stripe, seal_r = STRIPE_HALF * s, CAP_STRIPE * s, SEAL_R * s
    if livery == "black_white":
        z_mid = z_lo + cap_police / 2.0
    else:
        z_mid = z_lo + stripe_half
    ya, yb = px_y(door_edges[0]), px_y(door_edges[-1])
    if livery == "black_white":
        # the white doors, nose seam to tail seam, rocker to the shoulder;
        # on them the department over POLICE, the motto under, centred across
        # both doors so they read the same from either side
        img.rect((ya, px_z(door_skin_z[1]), yb, px_z(door_skin_z[0])), _rgb8(lv["panel"]))
        rows = ((DEPARTMENT[0], cap_department, z_mid + cap_police / 2.0 + gap + cap_department / 2.0, ink),
                (DEPARTMENT[1], cap_police, z_mid, ink),
                (MOTTO, CAP_MOTTO, z_motto, ink))
        seal_fill = ink
    else:
        # one broad stripe, fender to quarter, through the door handles'
        # height; the department in it on one line, in the body's white, and
        # the motto in the stripe's blue under it -- white on white is no line
        half = stripe_half
        img.rect((px_y(lay["y0"] + 0.30), px_z(z_mid + half), px_y(lay["yt"] - 0.30), px_z(z_mid - half)),
                 _rgb8(lv["stripe"]))
        rows = (("%s %s" % DEPARTMENT, cap_stripe, z_mid, ink),
                (MOTTO, CAP_MOTTO, z_motto, _rgb8(lv["stripe"])))
        seal_fill = _rgb8(lv["stripe"])
    # the black-and-white's marks keep clear of its seals at the doors' ends;
    # the stripe's name runs the doors' width and its seals stand out on the
    # stripe's ends, over the fender and the quarter
    if livery == "black_white":
        inset = SEAL_FROM_END + seal_r + 0.025
        span = (ya + inset * ART_PPM, yb - inset * ART_PPM)
    else:
        # the stripe's name rides the stripe between its seals: on one line
        # it is longer than a Crown Victoria's two doors (1.45 m on the
        # default slot), and the stripe is centred on the car as the doors are
        span = (px_y(lay["y0"] + STRIPE_SEAL_IN + seal_r + 0.05), px_y(lay["yt"] - STRIPE_SEAL_IN - seal_r - 0.05))
    for text, cap, zc, rgb in rows:
        cap_px = cap * ART_PPM
        box = (span[0], px_z(zc) - cap_px * 0.75, span[1], px_z(zc) + cap_px * 0.75)
        got = img.text(text, box, rgb, face=face, cap=cap_px, min_cap=int(cap_px) - 2)
        if got is None:
            raise ValueError("the cruiser's line %r does not set at %.3f m" % (text, cap))
        lines.append(got)
    # a seal at each end of the marks, gold, with the unit inside
    r = seal_r * ART_PPM
    seal_x = ((ya + SEAL_FROM_END * ART_PPM, yb - SEAL_FROM_END * ART_PPM) if livery == "black_white"
              else (px_y(lay["y0"] + STRIPE_SEAL_IN), px_y(lay["yt"] - STRIPE_SEAL_IN)))
    for xc in seal_x:
        img.disc(xc, px_z(z_mid), r, _rgb8(lv["seal"]))
        img.disc(xc, px_z(z_mid), r * 0.78, seal_fill)
        got = img.text(UNIT, (xc - r * 0.7, px_z(z_mid) - r * 0.4, xc + r * 0.7, px_z(z_mid) + r * 0.4),
                       _rgb8(lv["seal"]), face=face, cap=r * 0.55, min_cap=int(r * 0.55) - 2)
        if got is None:
            raise ValueError("the cruiser's unit number does not set in its seal")
    # the patches, right of the art
    x0 = fr["w"] + int(1.5 * PATCH_PX)
    img.rect((x0, 0, x0 + PATCH_PX * 1.5, PATCH_PX + 2), (255, 255, 255))
    img.rect((x0, PATCH_PX + 2, x0 + PATCH_PX * 1.5, 2 * PATCH_PX + 8), _rgb8(lv["margin"]))
    canvas = img.to_canvas()
    ident = repr((livery, round(fr["y0"], 4), round(fr["y1"], 4), round(fr["z0"], 4), round(fr["z1"], 4),
                  [round(e, 4) for e in door_edges], [round(z, 4) for z in door_skin_z],
                  None if moulding_z is None else round(moulding_z, 4),
                  DEPARTMENT, MOTTO, UNIT, ART_PPM, face)).encode("utf-8")
    return {"png": canvas.png(), "name": "Cruiser_livery_" + hashlib.sha1(ident).hexdigest()[:8],
            "size": (fr["W"], fr["H"]), "frame": fr, "lines": lines, "scale": s}
