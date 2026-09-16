"""What a back bar is, planned in pure Python: the wall unit behind a bar.

Zoo 0.92.0. The walker, 2026-09-15, with three photos of a lounge bar and
the bartender's side of one (docs/SET_DRESSING_REFERENCES.md, "The walker's
club bar reference"). THE CLUB'S BAR, NOT THE DIVE BAR: this is the strip
club's lit back bar, and the neighbourhood dive is a later slice with its
own look, so the shape is parameterised by FORM and the finish by style
rather than one unit standing for both.

What the photos carry, and what this builds:

  * a LOWER CABINET RUN at counter height -- a recessed plinth, doors two
    to a bay with a handle each, a worktop with the working bottles and a
    tower of glasses on it;
  * above it TIERED GLASS SHELVES crowded with bottles in rows, stemware
    on the top tier, a brass edge rail on every shelf;
  * PILASTERS dividing the run into bays, and a cornice over them;
  * in the CENTRE BAY a mirror (`straight`) or a round lit niche
    (`niche`) -- the porthole in the first photo;
  * WARM BULBS behind the shelves, one to a bay to a tier. 1997, so they
    are bulbs and not an LED strip: small spheres at the back panel under
    each shelf, emissive, and every emissive material here is named
    ``M_BackBar_*_Face`` so Lux's power cut turns them off with the room.

THE FRAME. Origin at the floor, centred on the unit's width; +Y is the
BACK (the wall, the slot's +Y face) and the unit faces -Y. Metres, Z up.
Extents are exactly w x d x h -- `prims.fit_exact` takes the last fraction
of a percent, as every slot-fit planner here does -- so a Deli Counter slot
gets the unit it asked for.

BOTTLES ARE SIZED TO THE SHELF, not pinned. The tier pitch is the shelf
zone divided by the tiers plus one (the top tier needs headroom too), and a
bottle is `pitch - BOTTLE_HEADROOM` tall, held to `BOTTLE_H`. A pinned
0.30 m bottle is right at one unit height and through the shelf above at
another; every back bar in the library is a different height.

A LABEL IS ONE QUAD, and its plane is deliberately parallel to nothing.
The bottles are hexagonal prisms drawn with `phase = pi / 6`, which puts a
VERTEX toward -Y and every facet at 30 degrees or more to the label's
plane -- a facet facing -Y would have sat 2 mm behind a label quad and
`prims.coincident_pairs` counts anything parallel within 2 mm.

NO TWO FACES SHARE A PLANE, which is the rule every species here keeps and
which this one had to be taught in four places at once (the first plan
measured 18 pairs over one size; the sweep now runs 88):

  * parts that MEET overlap by `JOIN`, never butt -- the cabinet into the
    plinth, the counter into the cabinet, a bottle's shoulder into its
    body, a stem's bowl into its foot;
  * things that STAND on a surface sink `SINK` into it, exactly as
    `_surface_stock` does;
  * parts reaching the same wall or the same end are STEPPED
    (`BACK_INSET`, `SIDE_INSET`): two parts flush to one plane are
    coplanar with each other however carefully each is joined, and
    overlapping by `JOIN` makes side faces share a plane over exactly
    that overlap;
  * and where a plane is parallel to another BY CONSTRUCTION -- a
    pilaster's face and a shelf's row of labels -- the distance between
    them is DERIVED rather than chosen (`PILASTER_CLEAR`), because a
    chosen pair of fractions has unit sizes where the two coincide and
    the sweep finds them one size at a time.
"""
from __future__ import annotations

import math

from . import back_bar_art as ART
from . import liquor_brands as LB
from . import prims as P

FORMS = ("straight", "niche")

#: How far one part reaches into the one it meets, and how far a thing
#: standing on a surface sinks into it. Both are past
#: `prims.coincident_pairs`'s 2 mm window with room to spare, and `SINK` is
#: `_surface_stock.SINK` rounded up a millimetre.
JOIN = 0.006
SINK = 0.004
#: HOW FAR EACH PART STOPS SHORT OF THE WALL, metres. Seven parts of this
#: unit reach the back and the first plan gave every one of them the same
#: plane, which is nine coincident pairs by itself -- a part flush to a
#: wall is coplanar with every other part flush to the same wall, however
#: carefully each one is joined to its neighbours. They are stepped
#: instead, by `JOIN` each, and the step is invisible: the whole back is
#: against a wall. The shelves and pilasters sit INSIDE the back panel
#: (which is `BACK_T` thick for exactly that reason), so nothing floats.
BACK_INSET = {"back": 0.000, "cabinet": 0.006, "counter": 0.012,
              "plinth": 0.018, "cornice": 0.024, "pilaster": 0.030,
              "shelf": 0.038}
#: ...AND THE SAME PROBLEM ON THE SIDE FACES, which the stepped backs
#: exposed rather than caused. Overlapping one part into another by `JOIN`
#: leaves their SIDE faces sharing a plane over exactly that overlap: the
#: cabinet and its worktop are both `w` wide and both end at x = w/2, so
#: the 6 mm they interlock is 6 mm of coincident side wall. Parts that
#: overlap in Z therefore take different insets in X. Parts that share an
#: inset (counter/cornice, cabinet/back, shelf/plinth) never overlap in Z,
#: so they never meet.
SIDE_INSET = {"counter": 0.000, "cornice": 0.000, "cabinet": 0.006,
              "back": 0.006, "shelf": 0.012, "plinth": 0.012,
              "pilaster": 0.018}

# --- the carcass ------------------------------------------------------------
PLINTH_H = 0.09         # the kick under the cabinet run
PLINTH_SET = 0.04       # and how far it is recessed from the doors
TOP_T = 0.04            # the worktop's thickness
CORNICE_H = 0.07        # the moulding across the top
CORNICE_OUT = 0.02      # how far it stands proud of the pilasters
#: The back panel, thick enough to take the shelves' and the pilasters'
#: stepped embedment (`BACK_INSET`) -- a panel on battens, which is what a
#: back bar's is.
BACK_T = 0.05
FACE_SET = 0.03         # a shelf stops this far behind the unit's face
#: The working height of the lower run. A hand lower than the bar counter
#: in front of it (Deli Counter's club counters are 1.08-1.10 m) so a
#: bottle can be set down across the aisle without lifting.
COUNTER_H = 1.05
#: ...but never more than this share of a short unit's height, or the
#: shelves have nowhere to go.
COUNTER_SHARE = 0.5

#: A bay is at most this wide before another pilaster divides it. The bay
#: count is forced ODD, because the reference's mirror and porthole are in
#: the CENTRE bay and an even run has no centre bay.
BAY_W = 1.1
PILASTER_W = 0.07
#: WHERE THE ROWS STAND on a shelf, as a share of its depth: the back row
#: and, alternating with it, one a little forward.
ROW_BACK = 0.46
ROW_FRONT = 0.60
STEM_ROW = 0.45
#: A PILASTER'S DEPTH IS DERIVED FROM THE BACK ROW, not chosen. A chosen
#: 0.6 of the shelf put its front face within 1.5 mm of a label quad's
#: plane at two of the nine unit sizes measured -- the two are parallel by
#: construction, so any fixed pair of fractions has sizes where they meet.
#: The pilaster stops this far behind the back row's labels instead, which
#: is a clearance and not a coincidence.
PILASTER_CLEAR = 0.014
PILASTER_MIN_D = 0.03

# --- the shelves ------------------------------------------------------------
SHELF_T = 0.012
RAIL_H = 0.014          # the brass edge rail's height above the glass
RAIL_T = 0.010
#: Tier pitch to aim at; the tier count is the zone divided by this, less
#: one for the headroom over the top tier, held to 2..4.
TIER_PITCH = 0.34
TIERS = (2, 4)
BOTTLE_HEADROOM = 0.04
BOTTLE_H = (0.16, 0.34)
#: Bottles across a shelf, centre to centre. 0.095 m is a 0.075 m bottle
#: and a 20 mm gap: a crowded row that still reads as bottles rather than
#: as a wall.
BOTTLE_PITCH = 0.095
STEM_PITCH = 0.115
#: THE PITCH IS THE BUDGET'S, once the budget bites. A bottle is 58-78
#: triangles and a 6.0 x 3.0 m unit has 18 m of bottle shelf, which at the
#: pitch above is 171 bottles and 16,876 triangles -- nearly twice the
#: heaviest thing in the genome (the vault door, 9,000). The pitch is the
#: greater of the one above and the run divided by these caps, so a wide
#: unit thins its rows instead of blowing the budget: measured, a 6.0 m
#: unit lands at 80 bottles and about 8,100 triangles.
MAX_BOTTLES = 80
MAX_STEMS = 40

#: The bottle glass, linear RGB. The liquor table names one per brand.
GLASS = {"amber": [0.19, 0.08, 0.02], "clear": [0.72, 0.76, 0.74],
         "green": [0.04, 0.16, 0.06]}
#: How the spirit inside reads through clear glass, by brand ground colour
#: -- not painted: the body is drawn in the glass colour and the shoulder a
#: touch darker, which is what a half-full bottle looks like from a metre.
SHOULDER_F = 0.72

#: The bulbs behind the shelves: a 1997 bar's clear pygmy lamps.
BULB_R = 0.022
BULB_OUT = 0.02         # the bulb's glass, off the back panel
BULB_COLOUR = [1.0, 0.72, 0.42]
#: 2.0 down to 1.5 (0.94.0). A pygmy lamp is allowed to be the brightest
#: thing on the shelf; it is not allowed to be WHITE, and at 2.0 the
#: brightest channel and the dimmest both landed on the dither's 239 step in
#: the walk of cold run 9060 -- a colourless dot. 1.5 keeps the tungsten in
#: it at the same station. It is a 4.4 cm sphere either way: this changes a
#: speck, and the porthole below is the change the walker asked for.
BULB_STRENGTH = 1.5
#: The niche's lit back. Warmer still and larger, so the porthole reads as
#: a light and not as a lamp. LINEAR rgb -- `back_bar_art.paint_niche`
#: encodes it for the diffuser raster.
NICHE_COLOUR = [1.0, 0.78, 0.52]
#: 1.6 down to 1.2 (0.94.0), and now the PEAK of a gradient rather than the
#: value of a flat face (see `back_bar_art.NICHE_PX` for what the flat face
#: measured). 1.2 x the preset's 0.95 exposure sits just over Heavy Rain's
#: 1.1 glow threshold, so the core alone blooms and the rest of the disc
#: does not -- a glow with an edge to it, which is what a frosted lamp is.
NICHE_STRENGTH = 1.2
#: 16 up to 32 (0.94.0). 16 put a visible facet every 22.5 degrees round a
#: 0.74 m disc read at 4 m; the diffuser's rim is black now, so this is
#: belt and braces -- and 16 more triangles against a unit that already
#: carries 8,100.
NICHE_SEGMENTS = 32
NICHE_RING = 0.035      # the surround's width round the lit disc


def _odd(n):
    return n if n % 2 else n + 1


def bays(w):
    """``(count, bay_width)``: an ODD number of bays, none wider than
    `BAY_W` once the count is odd."""
    n = _odd(max(1, int(round(w / BAY_W))))
    return n, w / n


def tiers(zone):
    """How many glass shelves a shelf zone of `zone` metres carries, and
    the pitch between them. One more gap than shelves: the top tier needs
    headroom for the stemware standing on it."""
    n = max(TIERS[0], min(TIERS[1], int(round(zone / TIER_PITCH)) - 1))
    return n, zone / (n + 1)


def _box(out, part, mat, lo, hi, bevel=False):
    out.append(P.box(part, mat, lo, hi, bevel))


def _bottle(out, brand, x, y, z0, r, hgt, form, label_h):
    """One bottle standing on a shelf, and its label quad.

    ``form``: ``tall`` (a long neck), ``squat`` (a wide shoulder and a
    short neck) or ``flask`` (no neck to speak of). The label's uvs are
    symbolic -- ``("uv", <brand id>, u, v)`` -- and `resolve_uvs` puts the
    atlas's own numbers in once the packing is known.
    """
    glass = "glass_" + brand["glass"]
    if form == "flask":
        body = hgt * 0.74
        neck_r = r * 0.52
    elif form == "squat":
        body = hgt * 0.58
        neck_r = r * 0.36
    else:
        body = hgt * 0.52
        neck_r = r * 0.30
    ph = math.pi / 6.0
    z0 -= SINK
    out.append(P.cyl("BackBar_Bottle", glass, (x, y), r, z0, z0 + body,
                     segments=6, phase=ph))
    # A NECK IS ONLY DRAWN WHERE IT READS. A `tall` bottle is a shoulder
    # and a long neck; a squat or a flask is a shoulder straight into its
    # cap, which is 20 triangles a bottle back over 80 of them.
    if form == "tall":
        shoulder = z0 + body + (hgt - body) * 0.35
        out.append(P.cyl("BackBar_Bottle", glass + "_d", (x, y), r,
                         z0 + body - JOIN, shoulder, segments=6, phase=ph,
                         r_top=neck_r))
        out.append(P.cyl("BackBar_Bottle", glass + "_d", (x, y), neck_r,
                         shoulder - JOIN, z0 + hgt - 0.008, segments=6, phase=ph))
    else:
        out.append(P.cyl("BackBar_Bottle", glass + "_d", (x, y), r,
                         z0 + body - JOIN, z0 + hgt - 0.008, segments=6,
                         phase=ph, r_top=neck_r))
    out.append(P.cyl("BackBar_Cap", "cap", (x, y), neck_r * 1.12,
                     z0 + hgt - 0.012, z0 + hgt, segments=5, phase=ph))
    # the label: one quad, its plane parallel to no facet of the prism
    lw = r * 1.35
    ly = y - r - 0.002
    lz = z0 + body * 0.42
    z1 = min(lz + label_h, z0 + body - 0.004)
    quad = {"part": "BackBar_Label", "mat": "label", "bevel": False,
            "verts": [(x - lw, ly, lz), (x + lw, ly, lz),
                      (x + lw, ly, z1), (x - lw, ly, z1)],
            "faces": [(0, 1, 2, 3)],
            "uvs": [(("uv", brand["id"], 0.0, 0.0), ("uv", brand["id"], 1.0, 0.0),
                     ("uv", brand["id"], 1.0, 1.0), ("uv", brand["id"], 0.0, 1.0))]}
    out.append(quad)


def _stem(out, x, y, z0, hgt):
    """A cocktail glass: a tapered foot-and-stem and a cone of a bowl."""
    r = hgt * 0.30
    z0 -= SINK
    out.append(P.cyl("BackBar_Stem", "stemware", (x, y), r * 0.62, z0,
                     z0 + hgt * 0.45, segments=5, r_top=r * 0.10))
    out.append(P.cyl("BackBar_Stem", "stemware", (x, y), r * 0.12,
                     z0 + hgt * 0.45 - JOIN, z0 + hgt, segments=6, r_top=r))


def _tumbler_tower(out, x, y, z0, n, r, t):
    """A tower of stacked rocks glasses -- ONE tapered body with a lip ring
    where each glass sits in the one below.

    DRAWN AS n NESTED CYLINDERS FIRST, and refuted by the coincidence
    probe: two glasses of the same taper, offset by a nesting step, have
    side planes 1.3 mm apart over the whole overlap. A single body cannot
    be coplanar with itself, and the rings are straight where the body is
    tapered, so no pair of planes is parallel at all."""
    step = t * 0.66
    z0 -= SINK
    top = z0 + step * (n - 1) + t
    out.append(P.cyl("BackBar_Glass", "stemware", (x, y), r, z0, top,
                     segments=6, r_top=r * 1.12))
    for k in range(1, n):
        z = z0 + k * step
        out.append(P.cyl("BackBar_Glass", "stemware", (x, y), r * 1.10, z,
                         z + 0.005, segments=6))


def plan(w, d, h, form="auto", variant=0, key=""):
    """The whole unit. Returns ``{prims, collision, attachments, form,
    brands, facts}``; ``prims`` carry symbolic label uvs (see `_bottle`).

    ``form`` ``auto`` reads the centre bay from the unit: a bay wide enough
    to hold a porthole of at least `NICHE_MIN_D` takes one, else a mirror.
    """
    w, d, h = float(w), float(d), float(h)
    v = int(variant)
    n_bays, bay_w = bays(w)
    counter = min(COUNTER_H, h * COUNTER_SHARE)
    zone_lo = counter + TOP_T
    zone_hi = h - CORNICE_H
    zone = max(0.2, zone_hi - zone_lo)
    n_tiers, pitch = tiers(zone)
    shelf_d = max(0.12, d - BACK_T - FACE_SET)
    y_back = d / 2.0
    y_face = d / 2.0 - BACK_T - shelf_d
    bottle_h = max(BOTTLE_H[0], min(BOTTLE_H[1], pitch - BOTTLE_HEADROOM))
    bottle_r = min(0.040, bottle_h * 0.13)
    b_pitch = max(BOTTLE_PITCH, w * max(1, n_tiers - 1) / MAX_BOTTLES)
    pilaster_d = max(PILASTER_MIN_D,
                     shelf_d * ROW_BACK - bottle_r - PILASTER_CLEAR)
    s_pitch = max(STEM_PITCH, w / MAX_STEMS)
    niche_d = min(bay_w - 2 * PILASTER_W, zone) * 0.86
    if form in (None, "", "auto"):
        form = "niche" if niche_d >= 0.34 else "straight"
    form = form if form in FORMS else "straight"

    out = []
    # --- the carcass --------------------------------------------------
    def _x(part):
        return w / 2.0 - SIDE_INSET[part]
    _box(out, "BackBar_Plinth", "case_dark",
         (-_x("plinth"), y_face + PLINTH_SET, 0.0),
         (_x("plinth"), y_back - BACK_INSET["plinth"], PLINTH_H))
    _box(out, "BackBar_Cabinet", "case",
         (-_x("cabinet"), y_face, PLINTH_H - JOIN),
         (_x("cabinet"), y_back - BACK_INSET["cabinet"], counter), bevel=True)
    _box(out, "BackBar_Counter", "top",
         (-_x("counter"), y_face - 0.012, counter - JOIN),
         (_x("counter"), y_back - BACK_INSET["counter"], counter + TOP_T),
         bevel=True)
    _box(out, "BackBar_Back", "back",
         (-_x("back"), y_back - BACK_T, zone_lo - JOIN),
         (_x("back"), y_back - BACK_INSET["back"], zone_hi + JOIN))
    _box(out, "BackBar_Cornice", "case_dark",
         (-_x("cornice"), y_face - CORNICE_OUT, zone_hi),
         (_x("cornice"), y_back - BACK_INSET["cornice"], h), bevel=True)

    centre = n_bays // 2
    order = LB.order(f"{key}:{v}")
    facts = {"bottles": 0, "stems": 0, "bulbs": 0, "brands": []}
    for b in range(n_bays):
        bx = -w / 2.0 + bay_w * (b + 0.5)
        inner = bay_w - PILASTER_W - 0.03

        def _across(pitch, radius, cx=bx):
            """``(count, first x)`` for a row across this bay at ``pitch``,
            the outermost item's own radius kept `JOIN` clear of the
            pilaster faces. Counting the row from the bay's INNER width
            alone put a bottle 1.6 mm from a pilaster on the 3.0 m unit."""
            room = bay_w - PILASTER_W - 2.0 * (radius + JOIN)
            n = max(1, int(room / pitch) + 1) if room > 0 else 1
            while n > 1 and (n - 1) * pitch > room:
                n -= 1
            return n, cx - (n - 1) * pitch / 2.0
        # --- the cabinet doors, two to a bay, with a handle each
        for s in (-1, 1):
            dx = bx + s * bay_w * 0.24
            dw = bay_w * 0.21
            _box(out, "BackBar_Door", "case",
                 (dx - dw, y_face - 0.006, PLINTH_H + 0.02),
                 (dx + dw, y_face + 0.006, counter - 0.02), bevel=True)
            out.append(P.cyl("BackBar_Handle", "brass",
                             (dx - s * dw * 0.62, y_face - 0.022), 0.008,
                             counter - 0.14, counter - 0.06, segments=6))
        # --- the mirror or the porthole, in the CENTRE bay only
        if b == centre:
            cz = zone_lo + zone / 2.0
            if form == "niche":
                # the porthole: a surround standing proud of the back
                # panel, and the lit disc a few millimetres behind it, so
                # the two planes are never within the coincident tolerance
                nr = niche_d / 2.0
                _ring(out, bx, y_back - BACK_T - 0.012, cz, nr, nr + NICHE_RING)
                _disc(out, "BackBar_NicheLamp", "niche_lit", bx,
                      y_back - BACK_T - 0.004, cz, nr)
            else:
                mw = min(inner, zone * 0.8) / 2.0
                mh = min(zone * 0.42, mw * 1.3)
                _box(out, "BackBar_Mirror", "mirror",
                     (bx - mw, y_back - BACK_T - 0.008, cz - mh),
                     (bx + mw, y_back - BACK_T + JOIN, cz + mh))
        # --- the working top: a tower of glasses or a pair of bottles
        if (b + v) % 2 == 0:
            _tumbler_tower(out, bx, (y_face + y_back) / 2.0,
                           counter + TOP_T, 4, 0.038, 0.085)
        else:
            for k in (-1, 1):
                brand = LB.BY_ID[order[(b * 3 + (k > 0)) % len(order)]]
                _bottle(out, brand, bx + k * 0.10, (y_face + y_back) / 2.0,
                        counter + TOP_T, bottle_r, bottle_h * 1.05,
                        "tall", bottle_h * 0.30)
                facts["bottles"] += 1
                facts["brands"].append(brand["id"])
        # --- the tiers
        for t in range(n_tiers):
            sz = zone_lo + pitch * (t + 1)
            if b == 0:          # one shelf plate spans the whole run
                _box(out, "BackBar_Shelf", "shelf",
                     (-_x("shelf"), y_face, sz),
                     (_x("shelf"), y_back - BACK_INSET["shelf"], sz + SHELF_T))
                # the rail stops short of the glass at each end: flush, its
                # own side faces lay in the shelf's
                _box(out, "BackBar_ShelfRail", "brass",
                     (-_x("shelf") + JOIN, y_face + 0.004, sz + SHELF_T - 0.005),
                     (_x("shelf") - JOIN, y_face + 0.004 + RAIL_T,
                      sz + SHELF_T + RAIL_H))
            # the bulb behind this tier, at the back panel
            # BULB_OUT, not a few millimetres: a 6 x 3 sphere has facets at
            # every angle, and one of them ran parallel to the mirror's
            # face 1.5 mm away when the bulb sat against the panel
            out.append(P.sphere("BackBar_Bulb", "bulb",
                                (bx, y_back - BACK_T - BULB_R - BULB_OUT,
                                 sz - BULB_R - 0.02), (BULB_R, BULB_R, BULB_R),
                                u=6, v=3))
            facts["bulbs"] += 1
            top_tier = t == n_tiers - 1
            if top_tier:
                stem_h = min(0.19, pitch - 0.06)
                n, x0 = _across(s_pitch, stem_h * 0.30)
                for i in range(n):
                    sx = x0 + i * s_pitch
                    _stem(out, sx, y_back - BACK_T - shelf_d * STEM_ROW,
                          sz + SHELF_T, stem_h)
                    facts["stems"] += 1
            else:
                n, x0 = _across(b_pitch, bottle_r)
                for i in range(n):
                    sx = x0 + i * b_pitch
                    brand = LB.BY_ID[order[(b * 7 + t * 3 + i) % len(order)]]
                    shape = ("tall", "squat", "tall", "flask")[(i + t) % 4]
                    # the row breathes: every other bottle stands a
                    # centimetre further FORWARD (-Y is the front), which
                    # is what a bar's row looks like and what keeps two
                    # labels from lining up
                    yb = y_back - BACK_T - shelf_d * (ROW_FRONT if i % 2
                                                      else ROW_BACK)
                    _bottle(out, brand, sx, yb, sz + SHELF_T, bottle_r,
                            bottle_h * (0.86 if shape == "squat" else 1.0),
                            shape, bottle_h * 0.34)
                    facts["bottles"] += 1
                    facts["brands"].append(brand["id"])
    # --- the pilasters, over everything, at every bay boundary
    for i in range(n_bays + 1):
        px = -w / 2.0 + bay_w * i
        if i == 0:
            px = -(w / 2.0 - SIDE_INSET["pilaster"])
        elif i == n_bays:
            px = w / 2.0 - SIDE_INSET["pilaster"] - PILASTER_W
        else:
            px -= PILASTER_W / 2.0
        _box(out, "BackBar_Pilaster", "case_dark",
             (px, y_back - BACK_T - pilaster_d, zone_lo - 2 * JOIN),
             (px + PILASTER_W, y_back - BACK_INSET["pilaster"], zone_hi + 2 * JOIN),
             bevel=True)

    cboxes = [((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h))]
    fitted, boxes = P.fit_exact(out, (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h),
                                cboxes)
    used = []
    for bid in facts["brands"]:
        if bid not in used:
            used.append(bid)
    facts["brands"] = used
    facts["bays"] = n_bays
    facts["tiers"] = n_tiers
    facts["tier_pitch"] = round(pitch, 4)
    facts["counter_h"] = round(counter, 4)
    facts["tris"] = P.tri_count(fitted)
    return {"prims": fitted, "collision": boxes, "form": form,
            "brands": tuple(used), "facts": facts,
            "attachments": {"ATT_niche": (0.0, y_back - BACK_T - 0.02,
                                          zone_lo + zone / 2.0),
                            "ATT_shelf": (0.0, (y_face + y_back) / 2.0,
                                          zone_lo + pitch)}}


def _disc(out, part, mat, cx, y, cz, r, segments=NICHE_SEGMENTS):
    """A flat disc in the XZ plane facing -Y: the niche's lit back.

    Carries its own UVs (0.94.0), mapping the disc's BOUNDING SQUARE onto
    the diffuser raster so the inscribed circle is exactly the disc and the
    raster's corners fall off the mesh. v is flipped because a Canvas keeps
    row 0 at the top and +z is up.
    """
    verts, faces, uvs = [], [], []
    for k in range(segments):
        a = 2.0 * math.pi * k / segments
        verts.append((cx + r * math.cos(a), y, cz + r * math.sin(a)))
    faces.append(tuple(range(segments)))
    uvs.append(tuple((0.5 + (v[0] - cx) / (2.0 * r),
                      0.5 - (v[2] - cz) / (2.0 * r)) for v in verts))
    out.append({"part": part, "mat": mat, "bevel": False, "verts": verts,
                "faces": faces, "uvs": uvs})


def _ring(out, cx, y, cz, r0, r1, segments=NICHE_SEGMENTS):
    """A flat annulus in the XZ plane facing -Y: the porthole's surround."""
    verts, faces = [], []
    for k in range(segments):
        a = 2.0 * math.pi * k / segments
        verts.append((cx + r0 * math.cos(a), y, cz + r0 * math.sin(a)))
    for k in range(segments):
        a = 2.0 * math.pi * k / segments
        verts.append((cx + r1 * math.cos(a), y, cz + r1 * math.sin(a)))
    for k in range(segments):
        k1 = (k + 1) % segments
        faces.append((k, segments + k, segments + k1, k1))
    out.append({"part": "BackBar_Niche", "mat": "case_dark", "bevel": False,
                "verts": verts, "faces": faces})


def resolve_uvs(prims, rects, size):
    """Replace a label's symbolic uvs (``("uv", brand id, u, v)``) with the
    atlas's own, once `back_bar_art.label_atlas` has packed it."""
    from .dartboard_art import uv_of
    out = []
    for p in prims:
        if p.get("uvs") and isinstance(p["uvs"][0][0], tuple) \
                and len(p["uvs"][0][0]) == 4:
            q = dict(p)
            q["uvs"] = [tuple(uv_of(rects[c[1]], size, c[2], c[3]) for c in face)
                        for face in p["uvs"]]
            out.append(q)
        else:
            out.append(p)
    return out


def materials(colour, kind, bulb=None):
    """``key -> (linear rgb, material kind)`` for every non-lit material key
    the plan uses. The lit ones are the recipe's, because they carry an
    emission strength as well."""
    def f(c, k):
        return [max(0.0, min(1.0, v * k)) for v in c]

    out = {
        "case": (list(colour), kind),
        "case_dark": (f(colour, 0.6), kind),
        "top": (f(colour, 0.42), kind),
        "back": (f(colour, 0.34), kind),
        "shelf": ([0.62, 0.70, 0.68], "glass"),
        "stemware": ([0.70, 0.76, 0.74], "glass"),
        "brass": ([0.58, 0.44, 0.16], "metal_bare"),
        "mirror": ([0.60, 0.62, 0.64], "metal_bare"),
        "cap": ([0.42, 0.34, 0.14], "metal_painted"),
    }
    for name, rgb in GLASS.items():
        out["glass_" + name] = (list(rgb), "plastic")
        out["glass_" + name + "_d"] = (f(rgb, SHOULDER_F), "plastic")
    del bulb
    return out


# --- the bartender's side of the counter in front of it -----------------------
#
# THE COUNTER'S OWN FIT-OUT LIVES HERE, in the planner, and not in
# `recipes/counter.py` where it was first written: the recipe imports
# `bpy` at module scope, so a test of it cannot run in the suite that
# runs without Blender -- which is the suite that measures whether a
# foot rail is inside its slot.
#
# COUNTER_FORMS, not FORMS: moved here verbatim, the counter's own tuple
# rebound this module's `FORMS` to ("straight", "bar") and `plan` then
# refused every `niche` it was asked for and built a mirror. Caught by the
# centre-bay test in the same run, which is the only reason it is a
# footnote and not a frame.
COUNTER_FORMS = ("straight", "bar")
#: THE FOOT RAIL, from the reference and from a bar's own dimensions: a
#: 38 mm brass tube at ankle-to-shin height on posts about a metre apart,
#: standing off the counter's front by a boot's width.
RAIL_R = 0.019
RAIL_Z = 0.22
RAIL_POST_PITCH = 1.1
RAIL_POST_R = 0.014
#: The tap towers: a column a metre or so apart along the SERVICE edge,
#: each with two or three handles on it.
TAP_PITCH = 1.0
TAP_H = 0.30
TAP_R = 0.032
TAP_HANDLE_H = 0.11
#: The register: a beige box with a raised keyboard deck and a display on a
#: stalk, 1997 and not a touch terminal. It stands at an ``ATT_register``
#: station, inside `REGISTER_CLEAR`.
REG_W = 0.30
REG_D = 0.34
REG_H = 0.12
REG_SCREEN_H = 0.13


def counter_fitout(w, d, h, attachments, top_w):
    """``(inside, on_top)``: the foot rail (inside the slot) and the tap
    towers and register (on the top), as primitive lists.

    Frame: the recipe's own -- -Y the customer side, +Y the service side.
    The rail hangs under the top's overhang on the customer front; the taps
    run along the service edge; a register stands at each station.
    """
    inside, on_top = [], []
    body_d = d * 0.85
    body_y = (d - body_d) / 2.0
    face = body_y - body_d / 2.0          # the body's customer face
    # the rail stands off the body's face, still inside the top's edge
    rail_y = max(-d / 2.0 + RAIL_R + 0.004, face - 0.055)
    x0, x1 = -top_w / 2.0 + 0.05, top_w / 2.0 - 0.05
    # `lay_along_x` maps z -> x, so the tube is drawn from x0 to x1 along Z
    # and then laid down; drawn from -x1 to -x0 it lands on the wrong half
    inside.append(P.translate(
        P.lay_along_x(P.cyl("Counter_FootRail", "brass", (0.0, 0.0), RAIL_R,
                            x0, x1, segments=8)),
        (0.0, rail_y, RAIL_Z)))
    n_posts = max(2, int(round((x1 - x0) / RAIL_POST_PITCH)) + 1)
    for i in range(n_posts):
        px = x0 + (x1 - x0) * i / (n_posts - 1)
        inside.append(P.cyl("Counter_FootRail", "brass", (px, rail_y),
                            RAIL_POST_R, 0.0, RAIL_Z + RAIL_R - 0.006,
                            segments=6))
    # THE REGISTERS FIRST, because a tap tower does not stand on the till.
    # Measured the other way round: at 4.0 x 0.8 the third tap landed
    # inside the register's footprint and the two shared their base plane.
    regs = []
    ry = d / 2.0 - REG_D / 2.0 - 0.06
    for name, (ax, _ay, _az) in sorted(attachments.items()):
        if not name.startswith("ATT_register"):
            continue
        regs.append(ax)
        on_top.append(P.box("Counter_Register", "beige",
                            (ax - REG_W / 2.0, ry - REG_D / 2.0, h - 0.004),
                            (ax + REG_W / 2.0, ry + REG_D / 2.0, h + REG_H)))
        on_top.append(P.box("Counter_Register", "beige",
                            (ax - REG_W / 2.0 + 0.03, ry + REG_D / 2.0 - 0.09,
                             h + REG_H - 0.004),
                            (ax + REG_W / 2.0 - 0.03, ry + REG_D / 2.0 - 0.02,
                             h + REG_H + REG_SCREEN_H)))
        on_top.append(P.box("Counter_RegisterKeys", "key_dark",
                            (ax - REG_W / 2.0 + 0.035, ry - REG_D / 2.0 + 0.03,
                             h + REG_H - 0.006),
                            (ax + REG_W / 2.0 - 0.035, ry + REG_D / 2.0 - 0.13,
                             h + REG_H + 0.004)))
    # the taps, along the service edge, wherever no register stands
    tap_y = d / 2.0 - 0.10
    n_taps = max(1, int(round((x1 - x0) / TAP_PITCH)))
    for i in range(n_taps):
        tx = x0 + (x1 - x0) * (i + 0.5) / n_taps
        if any(abs(tx - ax) < REG_W / 2.0 + TAP_R * 1.5 + 0.03 for ax in regs):
            continue
        on_top.append(P.cyl("Counter_TapTower", "steel", (tx, tap_y), TAP_R * 1.5,
                            h - 0.004, h + 0.022, segments=8))
        on_top.append(P.cyl("Counter_TapTower", "steel", (tx, tap_y), TAP_R,
                            h + 0.016, h + TAP_H, segments=8))
        for k in (-1, 1):
            hy = tap_y - TAP_R - 0.012
            on_top.append(P.cyl("Counter_TapSpout", "steel",
                                (tx + k * 0.035, hy), 0.008,
                                h + TAP_H - 0.10, h + TAP_H - 0.02, segments=5))
            on_top.append(P.box("Counter_TapHandle", "tap_handle",
                                (tx + k * 0.035 - 0.013, hy - 0.013,
                                 h + TAP_H - 0.024),
                                (tx + k * 0.035 + 0.013, hy + 0.013,
                                 h + TAP_H - 0.024 + TAP_HANDLE_H)))
    return inside, on_top
