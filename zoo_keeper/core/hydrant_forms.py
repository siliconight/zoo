"""The US dry-barrel fire hydrant, as decisions: layout, paint and chains.
Pure Python (no bpy), so every number the `fire_hydrant` recipe builds from is
testable without Blender.

WHAT 0.79.0 SHIPPED, measured before this file existed. Walk 9052_rain's
`cover/prop_fire_hydrant_delco_1997_01_w35_d35_h75.glb` (Zoo site kit job of
cold run 9052, slot `cover_81`): one part, `FireHydrant_Body`, 44 tris -- the
minting placeholder's 6 mm bevelled box -- plus a 12-tri collider, on one
material, `M_Skin_metal_painted_delco_1997_807d75`: the delco_1997 tintable
`metal_painted_neutral` pack times the genome's grey #807d75. Rebuilt through
`build.build_module` from this repo at 0.83.0 with that job's Pixelcoat
output, the GLB came back byte-identical, so the path measured is the path
the walk took. It is the "white box at the foot of the stop sign".

WHAT LOT ASKS FOR, kept. `site_furniture.SPECIES["fire_hydrant"]` is
(0.35, 0.35, 0.75), the genome default; the slot is centre-pivot, exact fit,
material `metal_painted`, collision "convex" (Zoo builds a box). Lot stands
one 2.5 m past each crossing's cut, on the band's outer half, at
`yaw = road.angle_deg + 0` on BOTH kerbs.

THE FRAME. Zoo's module frame: Z up, metres, centre pivot, grade at
``z = -h/2``. The PUMPER (steamer) outlet faces -Y, the species convention
for a front; the two hose outlets face +X and -X. `lot.site_furniture.
plate_facing` measured that a slot's Blender -Y points plan
``(sin yaw, -cos yaw)``; with Lot's ``yaw = road angle`` that is toward the
road on an L kerb and AWAY from it on an R kerb. `cover_81` is on road 1's R
kerb, so in walk 9052_rain the pumper faces the buildings until Lot turns an R
kerb hydrant by 180 degrees the way `_bus_stop` turns its shelter. That is
Lot's change, not this file's.

WHAT A HYDRANT IS HERE, bottom to top -- the common American dry-barrel
pattern (traffic flange, lower barrel, nozzle section, bonnet), with sizes
from the standard outlets rather than from any one maker's drawing:

  * a low ground collar and the traffic (ground-line) flange on it, six nuts
    on the flange;
  * a lower barrel with a slight taper, the one part that stretches with the
    slot's height;
  * the upper barrel flange, six nuts on it, and the nozzle section;
  * two 2 1/2 in hose outlets across X and a 4 1/2 in pumper outlet toward
    -Y, all at one height -- 0.477 m (18.8 in) to the centre at the
    nominal slot, over the usual 18 in minimum -- each a stub, a cap with a
    chain lug and a pentagonal nut; a short chain from each lug to an eye on
    the nozzle section;
  * the bonnet flange, five nuts on it, a faceted bonnet dome, a hold-down
    disc and the pentagonal operating nut (1 1/2 in point to flat).

Every round part is a 12-sided prism with a face, not a corner, toward +X,
+Y, -X and -Y, so each outlet meets a flat face and the slot's extent on an
axis is a face's apothem. Hexagon nuts are 6-sided, operating and cap nuts
5-sided.

THE SLOT IS EXACT, AND NOTHING IS SCALED PER AXIS. A barrel scaled 1.2 in X
and 0.85 in Y is an ellipse, which no hydrant is. One uniform scale ``k`` is
taken from the tightest axis, and the slack on each axis goes into the part
that can honestly be longer: the hose stubs take X, the pumper stub takes -Y
(the back is the collar), the lower barrel takes Z. At Lot's slot ``k`` is
1.0 and the stubs are 20 mm (hose) and 43 mm (pumper).

NO TWO FACES SHARE A PLANE. Each part runs `BURY` (absolute, not scaled) into
the part it stands on, so a joint is a solid passing into a solid rather
than two faces meeting in one plane; `BURY` is twice
`tools/coplanar_probe.py`'s 2 mm window.
"""
from __future__ import annotations

import math

#: The slot Lot asks for, at which every nominal size below is 1:1.
NOMINAL = (0.35, 0.35, 0.75)

#: How far a part runs into the part it stands on. Absolute metres: a
#: scaled bury would fall inside the probe's 2 mm window at k < 0.5.
BURY = 0.004

#: Round parts' sides. The brief: faceted, 10 to 12 sided barrels.
SEGMENTS = 12
NUT_SIDES = 6
PENTAGON = 5

# --- nominal sizes (metres at k = 1), bottom to top ------------------------
#: Ground collar: apothem, height. Its back face is the slot's +Y face.
COLLAR_A, COLLAR_H = 0.140, 0.025
#: Traffic flange.
FLANGE_A, FLANGE_H = 0.128, 0.030
#: Lower barrel apothem at its bottom and top: the taper.
LOWER_A = (0.090, 0.084)
#: The lower barrel's height at the nominal slot: what the slot's height
#: leaves once every other part is stacked (a test holds `layout` to it).
LOWER_H = 0.274
#: Upper barrel flange.
UPPER_FLANGE_A, UPPER_FLANGE_H = 0.114, 0.026
#: Nozzle section: apothem, height, and the outlets' centre above its base.
SECTION_A, SECTION_H, OUTLET_Z = 0.095, 0.232, 0.122
#: Bonnet flange, then the dome as (apothem, height above the flange top).
BONNET_FLANGE_A, BONNET_FLANGE_H = 0.112, 0.020
DOME = ((0.092, 0.000), (0.086, 0.035), (0.068, 0.070), (0.046, 0.095))
DOME_H = DOME[-1][1]
HOLD_DOWN_A, HOLD_DOWN_H = 0.034, 0.016
#: Operating nut: pentagon circumradius (1 1/2 in point to flat is
#: 0.0381 m = R (1 + cos 36)), height.
OP_NUT_R, OP_NUT_H = 0.021, 0.032

#: Outlets. stub_r: the nozzle; cap_r, cap_l: the cap's apothem and length;
#: nut_r, nut_l: its pentagonal nut; stub_min: the shortest stub a slot may
#: leave. A 2 1/2 in NST cap is about 3.7 in across, a 4 1/2 in about 5.7.
HOSE = {"stub_r": 0.034, "cap_r": 0.047, "cap_l": 0.038,
        "nut_r": 0.019, "nut_l": 0.022, "stub_min": 0.012}
PUMPER = {"stub_r": 0.056, "cap_r": 0.072, "cap_l": 0.048,
          "nut_r": 0.021, "nut_l": 0.024, "stub_min": 0.012}

#: Nut rings: (count, ring radius, hex circumradius, exposed height, first
#: angle in degrees, twist in degrees). Angles keep a nut out from under an
#: outlet (outlets at 0, 180 and 270 degrees). A hex nut's first corner is at
#: its ring angle plus the twist, so its faces point along (angle + twist +
#: 30 + 60 i); the twist keeps every one of them off the 12-gon's face
#: directions (multiples of 30), so no nut face is parallel to a barrel,
#: flange or dome face however close it stands (`nut_face_clearance_deg`).
FLANGE_NUTS = (6, 0.110, 0.010, 0.012, 45.0, 0.0)
UPPER_NUTS = (6, 0.1065, 0.0065, 0.010, 45.0, 0.0)
BONNET_NUTS = (5, 0.1035, 0.006, 0.009, 18.0, 3.0)

#: Chain: link length, width, wire thickness, pitch along the chain, and how
#: far below the chord's midpoint the hanging curve's control point starts
#: (the curve's own sag is half of it). `hanging_chain` lifts it until the
#: chain clears what it hangs over.
#: REFUTED, kept: 7.5 mm wide on 2.8 mm wire. A chain hanging in one
#: vertical plane gives every link a side along the same horizontal, so a
#: link's wide faces and its neighbour's wire faces are parallel and overlap
#: (W - T) / 2 apart -- 2.35 mm at k = 1, 1.99 mm at the genome's smallest
#: slot, where the probe reported four SAME pairs. 8.5 on 2.5 mm leaves
#: 2.55 mm there.
LINK_L, LINK_W, LINK_T = 0.016, 0.0085, 0.0025
LINK_PITCH = 0.0115
CHAIN_DROP = 0.09
#: Chain lug under each cap and eye on the nozzle section: size across,
#: along the outlet, and how far it hangs or stands out.
#: REFUTED, kept: a 10 mm lug and a 12 mm eye. The chain's end link runs
#: straight into both, along the outlet, so its sides stand parallel to theirs:
#: 7.5 mm link in a 10 mm lug put them 1.25 mm apart, and the probe reported
#: four SAME pairs on every build. Across, the lug and eye now clear the
#: link's width and wire by more than the probe's 2 mm at the smallest scale
#: the genome allows (`chain_side_gaps`).
LUG = (0.016, 0.012, 0.010)
EYE = (0.018, 0.012, 0.014)
#: How far below the cap's underside the eye's centre sits.
EYE_DROP = 0.022


def scale(w: float, d: float, h: float) -> float:
    """The one uniform scale: the tightest axis against the nominal slot."""
    return min(w / NOMINAL[0], d / NOMINAL[1], h / NOMINAL[2])


def layout(w: float, d: float, h: float) -> dict:
    """Every position and size the recipe builds, in the module frame.

    NO SLOT IS REFUSED, AND THAT IS ARITHMETIC. Because ``k`` is the
    tightest axis's ratio, each axis's slack is at least what the nominal
    slot has at that scale: a hose stub is at least ``w/2 - k (0.155)`` with
    ``k <= w/0.35``, so at least 0.057 w, where its minimum is at most
    0.034 w; the pumper stub and the lower barrel (at least 0.365 h against
    0.107 h) are bounded the same way. A first draft raised ValueError for
    both and no slot could reach it -- `test_a_far_undersized_slot_still_fits`
    holds the bound instead. The asserts below are the invariant, not a
    check anyone should expect to fire."""
    k = scale(w, d, h)
    s = lambda v: v * k  # noqa: E731
    z0 = -h / 2.0
    L = {"k": k, "w": w, "d": d, "h": h, "z0": z0, "bury": BURY,
         "segments": SEGMENTS}
    # Z: fixed parts scale, the lower barrel takes the rest
    fixed = (COLLAR_H + FLANGE_H + UPPER_FLANGE_H + SECTION_H + BONNET_FLANGE_H
             + DOME_H + HOLD_DOWN_H + OP_NUT_H)
    lower = h - s(fixed)
    assert lower >= s(0.08), (w, d, h, lower)
    z = z0
    L["collar"] = (z, z + s(COLLAR_H)); z += s(COLLAR_H)
    L["flange"] = (z, z + s(FLANGE_H)); z += s(FLANGE_H)
    L["lower"] = (z, z + lower); z += lower
    L["upper_flange"] = (z, z + s(UPPER_FLANGE_H)); z += s(UPPER_FLANGE_H)
    L["section"] = (z, z + s(SECTION_H))
    L["outlet_z"] = z + s(OUTLET_Z)
    z += s(SECTION_H)
    L["bonnet_flange"] = (z, z + s(BONNET_FLANGE_H)); z += s(BONNET_FLANGE_H)
    L["dome"] = [(s(a), z + s(dz)) for a, dz in DOME]; z += s(DOME_H)
    L["hold_down"] = (z, z + s(HOLD_DOWN_H)); z += s(HOLD_DOWN_H)
    L["op_nut"] = (z, z + s(OP_NUT_H)); z += s(OP_NUT_H)
    assert abs(z - h / 2.0) < 1e-9, (z, h)

    L["collar_a"] = s(COLLAR_A)
    L["flange_a"] = s(FLANGE_A)
    L["lower_a"] = (s(LOWER_A[0]), s(LOWER_A[1]))
    L["upper_flange_a"] = s(UPPER_FLANGE_A)
    L["section_a"] = s(SECTION_A)
    L["bonnet_flange_a"] = s(BONNET_FLANGE_A)
    L["hold_down_a"] = s(HOLD_DOWN_A)
    L["op_nut_r"] = s(OP_NUT_R)

    # Y: the collar's back face is the slot's +Y face; the pumper's nut tip
    # is its -Y face. X: the hose nut tips are the slot's X faces.
    L["y_axis"] = d / 2.0 - s(COLLAR_A)
    R = s(SECTION_A)
    outlets = {}
    for name, spec, reach in (("hose", HOSE, w / 2.0),
                              ("pumper", PUMPER, d - s(COLLAR_A))):
        stub = reach - R - s(spec["cap_l"]) - s(spec["nut_l"])
        assert stub >= s(spec["stub_min"]), (name, w, d, h, stub)
        o = {"stub": stub, "stub_r": s(spec["stub_r"]), "cap_r": s(spec["cap_r"]),
             "cap_l": s(spec["cap_l"]), "nut_r": s(spec["nut_r"]),
             "nut_l": s(spec["nut_l"])}
        o["cap0"] = R + stub                    # from the barrel axis
        o["cap1"] = o["cap0"] + o["cap_l"]
        o["tip"] = o["cap1"] + o["nut_l"]
        outlets[name] = o
    L["outlets"] = outlets
    L["outlet_dirs"] = {"hose_pos": (1.0, 0.0), "hose_neg": (-1.0, 0.0),
                        "pumper": (0.0, -1.0)}

    for key, ring in (("flange_nuts", FLANGE_NUTS), ("upper_nuts", UPPER_NUTS),
                      ("bonnet_nuts", BONNET_NUTS)):
        n, rr, nr, nh, a0, tw = ring
        L[key] = {"count": n, "ring": s(rr), "r": s(nr), "h": s(nh),
                  "angles": [math.radians(a0 + i * 360.0 / n) for i in range(n)],
                  "twist": math.radians(tw)}
    L["chain"] = {"link": (s(LINK_L), s(LINK_W), s(LINK_T)), "pitch": s(LINK_PITCH),
                  "drop": s(CHAIN_DROP), "lug": tuple(s(v) for v in LUG),
                  "eye": tuple(s(v) for v in EYE), "eye_drop": s(EYE_DROP)}
    return L


def extents(L: dict) -> tuple:
    """(xmin, xmax, ymin, ymax, zmin, zmax) the layout claims, analytically:
    the hose nut tips, the pumper nut tip and the collar's back, grade and
    the operating nut's top."""
    ya = L["y_axis"]
    return (-L["outlets"]["hose"]["tip"], L["outlets"]["hose"]["tip"],
            ya - L["outlets"]["pumper"]["tip"], ya + L["collar_a"],
            L["collar"][0], L["op_nut"][1])


def prism_ring(n: int, apothem: float, rot: float | None = None) -> list:
    """``n`` corners of a regular polygon whose FACES centre at angle 0, 90,
    180 and 270 degrees (for ``n`` divisible by 4) -- corners at
    ``pi / n + 2 pi i / n`` -- unless ``rot`` names the first corner."""
    r = apothem / math.cos(math.pi / n)
    a0 = math.pi / n if rot is None else rot
    return [(r * math.cos(a0 + 2.0 * math.pi * i / n),
             r * math.sin(a0 + 2.0 * math.pi * i / n)) for i in range(n)]


def pentagon(circumradius: float, point_at: float = math.pi / 2.0) -> list:
    """A pentagon with a corner at angle ``point_at`` (default: pointing up
    the local +y axis, so a flat face is down)."""
    return [(circumradius * math.cos(point_at + 2.0 * math.pi * i / 5),
             circumradius * math.sin(point_at + 2.0 * math.pi * i / 5))
            for i in range(5)]


def nut_face_clearance_deg(ring) -> float:
    """The smallest angle between any face of a ``ring``'s hex nuts and any
    face direction of a `SEGMENTS`-gon (multiples of 360 / SEGMENTS)."""
    n, _rr, _nr, _nh, a0, tw = ring
    step = 360.0 / SEGMENTS
    worst = step
    for i in range(n):
        for j in range(NUT_SIDES):
            phi = (a0 + i * 360.0 / n + tw + 180.0 / NUT_SIDES + j * 360.0 / NUT_SIDES) % step
            worst = min(worst, phi, step - phi)
    return worst


def chain_side_gaps(k: float) -> list:
    """Half-width differences (metres) at scale ``k`` between the chain
    link's two widths and the lug's and eye's widths across -- the plane
    gaps between an end link's sides and the part it runs into -- and between
    a link's width and its neighbour's wire."""
    return [abs(k * (part / 2.0 - link / 2.0))
            for part in (LUG[0], EYE[0], LINK_W) for link in (LINK_W, LINK_T)
            if part != link]


def chain_links(p0, p1, pitch: float, drop: float, link_l: float) -> list:
    """Links hanging from ``p0`` to ``p1`` (3D points): a quadratic Bezier
    whose control point sits ``drop`` metres below the chord's midpoint,
    sampled by arc length. Returns [(centre, unit tangent)], at least three
    links, the first and last a half link in from the ends."""
    mid = [(a + b) / 2.0 for a, b in zip(p0, p1)]
    ctrl = (mid[0], mid[1], mid[2] - drop)

    def at(t):
        u = 1.0 - t
        return tuple(u * u * p0[i] + 2 * u * t * ctrl[i] + t * t * p1[i] for i in range(3))

    samples = [at(i / 200.0) for i in range(201)]
    acc = [0.0]
    for a, b in zip(samples, samples[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    total = acc[-1]
    usable = max(0.0, total - link_l)
    n = max(3, int(round(usable / pitch)) + 1)
    out = []
    for i in range(n):
        target = link_l / 2.0 + usable * i / (n - 1)
        j = next((q for q in range(1, len(acc)) if acc[q] >= target), len(acc) - 1)
        a, b = samples[j - 1], samples[j]
        seg = acc[j] - acc[j - 1]
        f = 0.0 if seg <= 0 else (target - acc[j - 1]) / seg
        c = tuple(a[q] + (b[q] - a[q]) * f for q in range(3))
        tv = tuple(b[q] - a[q] for q in range(3))
        ln = math.sqrt(sum(v * v for v in tv)) or 1.0
        out.append((c, tuple(v / ln for v in tv)))
    return out


def hanging_chain(p0, p1, pitch: float, link_l: float, floor_z: float,
                  drop: float) -> list:
    """`chain_links` at the deepest drop, from ``drop`` down in 15% steps,
    whose lowest link end stays above ``floor_z`` -- a pumper chain must not
    hang through the upper flange's nuts. A chain that cannot clear even
    straight is returned straight."""
    while drop > 1e-4:
        links = chain_links(p0, p1, pitch, drop, link_l)
        if min(c[2] - abs(t[2]) * link_l / 2.0 for c, t in links) >= floor_z:
            return links
        drop *= 0.85
    return chain_links(p0, p1, pitch, 0.0, link_l)



#: Triangles in everything but the chains, and in one chain link: the module's
#: count is ``FIXED_TRIS + LINK_TRIS * links``. Counted off the built module at
#: Lot's slot (1,416 with 17 links) and held equal by a bpy test.
FIXED_TRIS = 1212
LINK_TRIS = 12


def outlet_hardware(L: dict, key: str) -> dict:
    """The lug under an outlet's cap, the eye on the nozzle section below it,
    and the chain between them, for outlet ``key`` of `layout`'s
    ``outlet_dirs``. Boxes are (centre, (half along the outlet, half across,
    half up)); links are `hanging_chain`'s. The chain may not hang lower than
    the upper flange's nuts plus a link's width."""
    o = L["outlets"]["pumper" if key == "pumper" else "hose"]
    dx, dy = L["outlet_dirs"][key]
    ch, R, ya, zo, bury = L["chain"], L["section_a"], L["y_axis"], L["outlet_z"], L["bury"]

    def along(dist, z):
        return (dx * dist, ya + dy * dist, z)

    mid = (o["cap0"] + o["cap1"]) / 2.0
    lug_w, lug_l, lug_h = ch["lug"]
    lug_top = zo - o["cap_r"] + bury
    lug_bot = zo - o["cap_r"] - lug_h
    eye_w, eye_h, eye_out = ch["eye"]
    z_eye = zo - o["cap_r"] - ch["eye_drop"]
    floor = L["upper_flange"][1] + L["upper_nuts"]["h"] + ch["link"][1]
    p0 = along(mid, lug_bot + 0.002)
    p1 = along(R + eye_out - 0.003, z_eye - eye_h / 2.0 + 0.002)
    return {
        "lug": (along(mid, (lug_top + lug_bot) / 2.0),
                (lug_l / 2.0, lug_w / 2.0, (lug_top - lug_bot) / 2.0)),
        "eye": (along(R + (eye_out - bury) / 2.0, z_eye),
                ((eye_out + bury) / 2.0, eye_w / 2.0, eye_h / 2.0)),
        "floor": floor,
        "links": hanging_chain(p0, p1, ch["pitch"], ch["link"][0], floor, ch["drop"]),
    }


def triangles(L: dict) -> int:
    """The built module's triangle count, from the layout alone."""
    return FIXED_TRIS + LINK_TRIS * sum(len(outlet_hardware(L, k)["links"])
                                        for k in L["outlet_dirs"])

# --- paint -----------------------------------------------------------------

#: Linear RGB, as the tintable `metal_painted` pack multiplies them.
CHROME_YELLOW = (0.78, 0.50, 0.015)
HYDRANT_RED = (0.40, 0.030, 0.020)
#: REFUTED, kept: (0.46, 0.47, 0.47) rendered as white paint on the pack's
#: near-white grain, not as aluminium.
ALUMINIUM = (0.34, 0.35, 0.35)
WHITE = (0.70, 0.70, 0.66)
BLACK = (0.035, 0.035, 0.035)
#: NFPA 291's bonnet-and-cap colours by rated flow: AA (1500 gpm and over)
#: light blue, A (1000-1499) green, B (500-999) orange, C (under 500) red.
FLOW = {"AA": ((0.12, 0.33, 0.62), 0.22), "A": ((0.030, 0.22, 0.060), 0.38),
        "B": ((0.80, 0.20, 0.015), 0.28), "C": ((0.42, 0.030, 0.020), 0.12)}
#: Schemes: (body, top, weight). ``top`` is the bonnet, caps and nuts; the
#: string "flow" means colour-coded by `FLOW`. CHOSEN, not surveyed: the
#: period's common municipal patterns -- NFPA's chrome yellow with coded
#: tops, red with white or silver tops, aluminium bodies -- and no claim
#: about which Delaware County authority painted which. Nothing here was
#: checked against a 1997 photograph.
SCHEMES = {
    "yellow_coded": (CHROME_YELLOW, "flow", 0.34),
    "yellow_white": (CHROME_YELLOW, WHITE, 0.12),
    "red_white": (HYDRANT_RED, WHITE, 0.18),
    "red_silver": (HYDRANT_RED, ALUMINIUM, 0.08),
    "silver_coded": (ALUMINIUM, "flow", 0.12),
    "silver_red": (ALUMINIUM, HYDRANT_RED, 0.08),
    "red_black": (HYDRANT_RED, BLACK, 0.08),
}
#: The collar and flange are the body's paint gone dark with grime.
BASE_SHADE = 0.45
#: Galvanised chain.
CHAIN_STEEL = (0.30, 0.29, 0.27)


def _weighted(rng, pairs):
    total = float(sum(w for _k, w in pairs))
    r = rng.random() * total
    acc = 0.0
    for k, w in pairs:
        acc += w
        if r < acc:
            return k
    return pairs[-1][0]


def pick_scheme(plan: dict, rng) -> dict:
    """{name, body, top, flow, base}. Both draws are always taken, so asking
    for a colour never shifts a later one. A prompt colour (a plan colour
    that differs from its style block's) paints the body and keeps the
    drawn top."""
    name = _weighted(rng, [(k, v[2]) for k, v in SCHEMES.items()])
    flow = _weighted(rng, [(k, v[1]) for k, v in FLOW.items()])
    body, top, _w = SCHEMES[name]
    flow_used = None
    if top == "flow":
        top, flow_used = FLOW[flow][0], flow
    block = plan.get("style_block") or {}
    colour = [round(float(c), 4) for c in plan.get("color", [])]
    styled = [round(float(c), 4) for c in block.get("color", colour)]
    if colour and (colour != styled or block.get("paint") == "fixed"):
        name, body = "asked", tuple(colour)
    return {"name": name, "body": tuple(body), "top": tuple(top), "flow": flow_used,
            "base": tuple(c * BASE_SHADE for c in body), "chain": CHAIN_STEEL}


def resolve(plan: dict, streams) -> dict:
    dims = plan["dimensions"]
    f = layout(float(dims["width"]), float(dims["depth"]), float(dims["height"]))
    f["paint"] = pick_scheme(plan, streams.stream("hydrant_paint"))
    return f
