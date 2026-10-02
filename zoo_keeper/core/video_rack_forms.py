"""The video store's tape racks, decided in pure Python: the wall unit, the
island, every box on them and every pixel of the boxes' fronts.

Zoo 1.43.0, species `video_rack`. The walker, 2026-09-29, queued "a new
building type: a VHS movie rental store", and on 2026-10-02 named it
MACDADE MOVIES, asked for the curtained back room ("suggestive only") and
left the rest to the era: a 1997 strip-mall rental store is WALLS OF BOXES
FACED OUT under a genre board, low islands of more down the floor, and a
back room behind a curtain.

REVISED 1.44.0 FROM THE WALKER'S TEN PHOTOGRAPHS (docs/SET_DRESSING_
REFERENCES.md, "The walker's video store references"). 1.43.0 was built with
none: every box faced out, grey steel, printed boards. The photographs are a
cult store and a chain store and this is both.

FOUR FORMS, in the recipe frame (metres, Z up, floor 0, CENTRE pivot, x
along the run):

  wall     shopped from -Y, its back board at +Y against the building's
           wall. TAPES SPINE OUT, packed: each shelf a few blocks of spines,
           uneven on top, a hand's gap here and there. A section board
           across the head of each bay (ACTION, COMEDY, HORROR, DRAMA,
           SCI-FI, from a start the slot's `variant` picks), a shelf tag or
           two on every lip;
  island   the same on both faces of a spine -- full height, an aisle and
           not a counter -- with a yellow section sign on each end panel;
  adult    the wall form for the back room: its own boards, its own spines;
  display  the chain store's new-release rack: black, every box FACED OUT
           and leaning back on its foot, three or four facings a title,
           NEW RELEASES across its head.

A UNIT IS PAINTED ONE COLOUR -- purple, green, black or blue, by the slot's
variant -- frame, shelves and all; the colour is in the `Wear` vertex colour,
so it is no new material.

A BLOCK OF SPINES IS A BOX, a whole number of 25 mm tapes wide, showing its
own stretch of its section's strip of forty painted spines: a row of tapes
is a slab with an uneven top, which is what it is from an aisle. A 2.4 m
wall is 493 tapes in 1,560 triangles; faced out it was 126 boxes in 2,028.
A faced-out box is still a box: 0.105 x 0.19 x 0.03 m, twelve triangles.

A PART NAME IS ONE MATERIAL'S: the kick, the board and the lip are their own
parts because each is its own tint, and two tints under one part name build
as `Name` and `Name.001` (the first built test's failure).

TWO SUBMISSIONS WHATEVER THE LENGTH, the snack gondola's two: the steel
(colour in the `Wear` vertex colour) and the art (every box and every genre
board on ONE painted image).

EVERY TITLE IS INVENTED: Delco slang, PG-13, no real film, studio or rental
chain -- `tests/test_video_rack.py` holds them against the factory's
denylists and the chains and titles a writer would reach for. THE BACK ROOM
IS SUGGESTIVE AND NEVER EXPLICIT (docs/reference/, the lewd guide; the
walker: "suggestive only"): a plain box, a title, a pair of lips or a heart,
an 18+ badge. No figure is drawn.
"""
from __future__ import annotations

import math
import re
import zlib

from . import pixel_type as pt
from . import prims as P
from .card_art import _ellipse
from .vending_forms import Canvas

FORMS = ("wall", "island", "adult", "display")
#: Deli Counter's slots (long side first), then the genome's range.
DC_SIZES = ((2.4, 0.45, 2.0), (3.0, 0.45, 2.0), (4.0, 0.45, 2.0), (2.4, 0.9, 1.9), (2.0, 0.9, 1.4))
RANGES = {"width": (1.0, 8.0), "depth": (0.35, 1.2), "height": (1.2, 2.2)}

BURY = 0.004
KICK_H = 0.10
BOARD_T = 0.024           # the wall form's back board
SPINE_T = 0.03            # the island's
UPRIGHT_W = 0.04
TOP_T = 0.024
BAY_MAX = 1.0
SHELF_T = 0.02
SHELF_PITCH_MIN = 0.25    # a box, a lip and a hand
LIP_T = 0.012
HEAD_H = 0.16             # a genre board
BOX = (0.105, 0.19, 0.03)  # a VHS sleeve: width, height, depth
BOX_GAP = 0.012
LEAN_DEG = 12.0           # a faced-out box leans back on its foot
#: SPINE OUT (1.44.0, the walker's photographs): a tape's spine is 25 mm
#: and the sleeve runs 105 mm back into the shelf; a genre's strip of
#: painted spines is forty tapes, one metre.
SPINE_W = 0.025
SPINE_D = 0.105
STRIP_SPINES = 40
#: A shelf tag and an aisle-end sign: width, height.
TAG = (0.05, 0.024)
CAP = (0.30, 0.125)
TAGS = ("tag_yellow", "tag_orange")
TAG_RGB = ((244, 220, 60), (250, 150, 50))
#: THE UNITS ARE PAINTED (1.44.0): purple, green, black, blue -- a colour a
#: unit, by the slot's variant. The display rack is black wire and the back
#: room's is black.
UNIT_COLOURS = ((0.29, 0.16, 0.45), (0.22, 0.48, 0.17), (0.06, 0.06, 0.07), (0.10, 0.22, 0.52))
WIRE = (0.05, 0.05, 0.06)
#: A part's shade of its unit's colour.
SHADE = {"steel": 1.0, "kick": 0.55, "board": 0.8, "lip": 1.25}
STORE = "MACDADE MOVIES"
STICKER = "MM"

MATERIALS = {
    "steel": ((0.20, 0.20, 0.22), "metal_painted"),
    "kick": ((0.08, 0.08, 0.09), "metal_painted"),
    "board": ((0.30, 0.29, 0.28), "metal_painted"),
    "lip": ((0.86, 0.84, 0.78), "metal_painted"),
}
KIND_BASE = {"metal_painted": (1.0, 1.0, 1.0)}
_VARIANT = re.compile(r"_n\d+(?=_|$)")

#: The genres, in the order a wall runs them, and each one's board: the
#: words, the board's field and its ink.
GENRES = ("new", "action", "comedy", "horror", "drama", "scifi")
#: The sections an AISLE runs; NEW RELEASES is the display rack's alone.
AISLE_GENRES = GENRES[1:]
BOARDS = {
    "new": ("NEW RELEASES", "#c8202a", "#fff4dc"),
    "action": ("ACTION", "#1a1a1e", "#f0c020"),
    "comedy": ("COMEDY", "#f0c020", "#1a1a1e"),
    "horror": ("HORROR", "#1a1a1e", "#d02828"),
    "drama": ("DRAMA", "#24406a", "#f4ead8"),
    "scifi": ("SCI-FI", "#1e7a6a", "#f4f4e0"),
    "adult": ("ADULTS ONLY 18+", "#5a1040", "#ffd0e8"),
}
#: id, genre, the title's words (one line each, six letters or fewer), the
#: box's body, second colour and ink.
TITLES = (
    ("hoagie_cop_2", "new", ("HOAGIE", "COP 2"), "#1e2a5a", "#f0c020", "#ffffff"),
    ("blue_route", "new", ("BLUE", "ROUTE"), "#1a60b0", "#e8f0f8", "#ffffff"),
    ("moon_strut", "new", ("MOON", "STRUT"), "#3a2a60", "#f0d890", "#fff4d8"),
    ("last_exit_9", "new", ("LAST", "EXIT 9"), "#2a2a2e", "#f07a10", "#fff0d0"),
    ("delco_nights", "new", ("DELCO", "NIGHTS"), "#6a1a3a", "#f0a8c8", "#ffffff"),
    ("hoagie_cop", "action", ("HOAGIE", "COP"), "#8a1a1a", "#f0c020", "#ffffff"),
    ("pike_fury", "action", ("PIKE", "FURY"), "#c83020", "#1a1a1e", "#fff0d0"),
    ("fist_of_jawn", "action", ("FIST", "OF", "JAWN"), "#1a1a1e", "#d02828", "#f0c020"),
    ("tow_zone", "action", ("TOW", "ZONE"), "#f0c020", "#1a1a1e", "#1a1a1e"),
    ("repo_kings", "action", ("REPO", "KINGS"), "#2a5c2a", "#f0e060", "#ffffff"),
    ("yo_dad", "comedy", ("YO", "DAD"), "#f8c020", "#c01a1a", "#6a0808"),
    ("prom_jawn", "comedy", ("PROM", "JAWN"), "#f0a8c8", "#8ae0e8", "#4a1440"),
    ("uncle_vinny", "comedy", ("UNCLE", "VINNY"), "#1e8a4a", "#e8f4e0", "#ffffff"),
    ("shore_boys", "comedy", ("SHORE", "BOYS"), "#2aa0b0", "#f8e8c0", "#ffffff"),
    ("two_dopes", "comedy", ("TWO", "DOPES"), "#e8f0f8", "#f07a10", "#0a2a60"),
    ("scrapple", "horror", ("SCRAP-", "PLE"), "#3a1010", "#b02020", "#f0e0d0"),
    ("it_ate_nana", "horror", ("IT ATE", "NANA"), "#101014", "#6ab04a", "#d8f0c0"),
    ("creek_thing", "horror", ("CREEK", "THING"), "#16301e", "#7a9a5a", "#e8f4e0"),
    ("the_cellar", "horror", ("THE", "CELLAR"), "#1a1a1e", "#8a8a90", "#ffffff"),
    ("night_toll", "horror", ("NIGHT", "TOLL"), "#241a3a", "#d02828", "#f4ead8"),
    ("row_home", "drama", ("ROW", "HOME"), "#7a3a18", "#f0c070", "#fff4dc"),
    ("the_el", "drama", ("THE", "EL"), "#4a4a52", "#c8c8d0", "#ffffff"),
    ("last_call", "drama", ("LAST", "CALL"), "#3a2210", "#e8a830", "#f4ead8"),
    ("third_shift", "drama", ("THIRD", "SHIFT"), "#24406a", "#9ab8f0", "#ffffff"),
    ("mill_town", "drama", ("MILL", "TOWN"), "#5a5040", "#d8c8a0", "#fff4dc"),
    ("yo_robot", "scifi", ("YO", "ROBOT"), "#1e7a6a", "#a0e8e0", "#ffffff"),
    ("moon_pike", "scifi", ("MOON", "PIKE"), "#101830", "#c8c8d0", "#ffffff"),
    ("laser_nana", "scifi", ("LASER", "NANA"), "#5a2aa0", "#f04a90", "#ffffff"),
    ("star_hoagie", "scifi", ("STAR", "HOAGIE"), "#0a1a40", "#f0e040", "#f0e040"),
    ("delco_3000", "scifi", ("DELCO", "3000"), "#2a2a2e", "#40e0d0", "#40e0d0"),
    ("hot_jawns", "adult", ("HOT", "JAWNS"), "#b01050", "#ffd0e8", "#ffffff"),
    ("shore_nights", "adult", ("SHORE", "NIGHTS"), "#40104a", "#f090c0", "#ffe0f0"),
    ("tan_lines", "adult", ("TAN", "LINES"), "#c85a20", "#ffe0b0", "#ffffff"),
    ("hot_tub_4", "adult", ("HOT", "TUB 4"), "#1a4a8a", "#f0a0c0", "#ffffff"),
    ("after_dark", "adult", ("PIKE", "AFTER", "DARK"), "#16101e", "#d02878", "#ffd0e8"),
    ("wooder_bed", "adult", ("WOODER", "BED"), "#2a6a8a", "#ffc0d8", "#ffffff"),
)
BY_GENRE = {g: tuple(t[0] for t in TITLES if t[1] == g) for g in GENRES + ("adult",)}
BY_ID = {t[0]: t for t in TITLES}


def hex_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def all_words():
    """Every word the art sets, for the denylists."""
    out = [STORE, STICKER]
    out += [BOARDS[g][0] for g in BOARDS]
    out += [" ".join(t[2]).replace("- ", "") for t in TITLES]
    return out


def unit_colour(form, variant):
    """The colour a unit is painted: a cult store's shelving is painted one
    bold colour a unit (the walker's photographs: purple, green, black,
    blue); the display rack and the back room's are black."""
    if form in ("display", "adult"):
        return WIRE
    return UNIT_COLOURS[int(variant) % len(UNIT_COLOURS)]


def vertex_tint(mat_key, unit=None):
    """``(kind, rgb)`` for a structural part: the unit's colour, the kick a
    shade under it and the shelf's edge a shade over. No unit is the grey
    this species shipped with (1.43.0)."""
    rgb, kind = MATERIALS[mat_key]
    if unit is not None:
        k = SHADE[mat_key]
        rgb = tuple(min(1.0, c * k) for c in unit)
    return kind, tuple(c / b for c, b in zip(rgb, KIND_BASE[kind]))


def _h(*k):
    return zlib.crc32(",".join(str(v) for v in k).encode("utf-8")) & 0xFFFFFFFF


def resolve(plan_):
    """``(key, variant, form)`` from a kit plan."""
    params = plan_.get("params") or {}
    module = plan_.get("module") or {}
    variant = int(module.get("variant") or params.get("variant") or 0)
    key = _VARIANT.sub("", module.get("stem") or "") or "video_rack"
    form = str(params.get("form") or "wall")
    if form == "auto":
        form = "wall"
    return key, variant, form


def shelf_levels(h, form):
    """z of each shelf's top, the kick's deck first, up to where a tape no
    longer fits under the section board (or an island's top board)."""
    top = h - (TOP_T + 0.02 if form == "island" else HEAD_H + 0.02)
    n = max(2, int((top - KICK_H) // SHELF_PITCH_MIN))
    pitch = (top - KICK_H) / n
    return [KICK_H + k * pitch for k in range(n)], pitch


def genre(form, variant, face, bi):
    """What bay ``bi`` of ``face`` rents. The back room's is its own, the
    display rack is NEW RELEASES end to end, and an aisle runs the five
    sections in order from a start the slot's variant picks."""
    if form == "adult":
        return "adult"
    if form == "display":
        return "new"
    return AISLE_GENRES[(int(variant) + bi + (2 if face == "b" else 0)) % len(AISLE_GENRES)]


def _art_box(part, lo, hi, tile, solid, win=(0.0, 1.0)):
    """A box whose -Y face (`prims.box` face 2, corners 0, 1, 5, 4: the
    tile's bottom-left, bottom-right, top-right, top-left) carries ``tile``
    -- the part of it between ``win``'s two u -- and whose other faces carry
    ``solid``'s colour block."""
    p = P.box(part, "art", lo, hi)
    u0, u1 = win
    uvs = []
    for k, f in enumerate(p["faces"]):
        if k == 2:
            uvs.append(((tile, u0, 0.0), (tile, u1, 0.0), (tile, u1, 1.0), (tile, u0, 1.0)))
        else:
            uvs.append(tuple((solid,) for _ in f))
    p["uvs"] = uvs
    p["front"] = (2,)
    return p


def _spines(sx0, sx1, y, z, bh, g, salt):
    """One shelf of tapes SPINE OUT: a few blocks of spines, each a box as
    wide as a whole number of tapes, their heights and depths a little
    uneven and a hand's gap here and there -- a row somebody has been
    pulling tapes out of. Each block shows its own stretch of the genre's
    strip of painted spines. Blocks stand 3 mm apart or more: touching, two
    blocks share a plane."""
    out, n_tapes = [], 0
    x, end, j = sx0 + 0.008, sx1 - 0.008, 0
    while end - x >= 2 * SPINE_W:
        want = 5 + _h(*salt, j, "n") % 12
        n = min(want, int((end - x) // SPINE_W))
        if n < 2:
            break
        height = bh - (0.0, 0.008, 0.016, 0.024)[_h(*salt, j, "h") % 4]
        depth = SPINE_D - (0.0, 0.01, 0.02)[_h(*salt, j, "d") % 3]
        start = _h(*salt, j, "s") % (STRIP_SPINES - n + 1)
        out.append(_art_box("VideoRack_Art", (x, y, z - BURY),
                            (x + n * SPINE_W, y + depth, z - BURY + height),
                            "spines_" + g, "solid_spines",
                            (start / float(STRIP_SPINES), (start + n) / float(STRIP_SPINES))))
        n_tapes += n
        x += n * SPINE_W + (0.04 if _h(*salt, j, "g") % 4 == 0 else 0.003)
        j += 1
    return out, n_tapes


def _faced(sx0, sx1, y, z, bh, titles, salt):
    """One shelf of boxes FACED OUT and leaning back: the display rack's."""
    out = []
    bw_, _bh, bd_ = BOX
    n = max(1, int((sx1 - sx0 - 0.02) // (bw_ + BOX_GAP)))
    span = n * bw_ + (n - 1) * BOX_GAP
    x0 = (sx0 + sx1) / 2.0 - span / 2.0 + bw_ / 2.0
    facings = 3 + _h(*salt, "f") % 2
    for i in range(n):
        t = titles[(_h(*salt[:-1]) + salt[-1] + i // facings) % len(titles)]
        x = x0 + i * (bw_ + BOX_GAP)
        p = _art_box("VideoRack_Art", (x - bw_ / 2.0, y, z - BURY),
                     (x + bw_ / 2.0, y + bd_, z - BURY + bh), "tile_" + t, "solid_" + t)
        # leaning back on its foot: the top goes toward the rack
        out.append(P.rotate_x(p, -math.radians(LEAN_DEG), about=(y, z - BURY)))
    return out, n


def _face(bays_, h, y_front, y_back, form, key, variant, face):
    """One shelved face (the -Y one): shelves, lips, tapes, tags, boards."""
    out, n_items, genres = [], 0, []
    levels, pitch = shelf_levels(h, form)
    bh = min(BOX[1], pitch - SHELF_T - 0.04)
    for bi, (bx, bw) in enumerate(bays_):
        # an island's end panels stand 3 mm in, so its shelves stop 3 mm
        # shorter: at the wall form's 4 mm they were 1 mm off the panels
        pad = 0.007 if form == "island" else 0.004
        sx0, sx1 = bx - bw / 2.0 + UPRIGHT_W / 2.0 + pad, bx + bw / 2.0 - UPRIGHT_W / 2.0 - pad
        g = genre(form, variant, face, bi)
        genres.append(g)
        for k, z in enumerate(levels):
            if k:        # the deck is the kick's top
                out.append(P.box("VideoRack_Shelf", "steel", (sx0, y_front, z - SHELF_T), (sx1, y_back, z)))
            # the lip's foot 8 mm under the shelf's: at 2 mm the two shared a plane
            out.append(P.box("VideoRack_Lip", "lip", (sx0 + 0.003, y_front - LIP_T, z - SHELF_T - 0.008),
                             (sx1 - 0.003, y_front + BURY, z + 0.006)))
            salt = (key, variant, face, bi, k)
            if form == "display":
                got, n = _faced(sx0, sx1, y_front + 0.014, z, bh, BY_GENRE[g], salt)
            else:
                got, n = _spines(sx0, sx1, y_front + 0.014, z, bh, g, salt)
                # a shelf tag or two on the lip: 3 mm proud, 5 mm into it, its
                # top and foot 4 mm or more inside the lip's own (the first
                # cut's top WAS the lip's top), and each in its own half of
                # the shelf (two drawn anywhere overlapped, face on face)
                half = (sx1 - sx0) / 2.0
                for j in range(1 + _h(*salt, "tags") % 2):
                    tx = sx0 + j * half + 0.04 + (_h(*salt, "tag", j) % 1000) / 1000.0 * (half - 0.08 - TAG[0])
                    tile = TAGS[_h(*salt, "tagc", j) % len(TAGS)]
                    out.append(_art_box("VideoRack_Art",
                                        (tx, y_front - LIP_T - 0.003, z - TAG[1]),
                                        (tx + TAG[0], y_front - LIP_T + 0.005, z),
                                        tile, "solid_" + tile))
            out += got
            n_items += n
        if form != "island":
            # the section board, proud of the shelves' lips and 4 mm inside
            # the slot's front
            out.append(_art_box("VideoRack_Art", (sx0, y_front - 0.026, h - HEAD_H),
                                (sx1, y_front - 0.004, h - TOP_T - 0.006),
                                "head_" + g, "solid_head_" + g))
    return out, n_items, genres


def _end_sign(w, h, g, side):
    """An island's aisle-end sign: a yellow board on its end panel at the
    eye, the section's word. Built facing -Y at the origin and turned to
    face along the aisle; its face IS the slot's end."""
    z1 = min(h - 0.15, 1.62)
    z0 = z1 - CAP[1]
    p = _art_box("VideoRack_Art", (-CAP[0] / 2.0, -0.006, z0), (CAP[0] / 2.0, 0.0, z1),
                 "cap_" + g, "solid_cap")
    p = P.rotate_z(p, side * math.pi / 2.0, about=(0.0, 0.0))
    return P.translate(p, (side * (w / 2.0 - 0.006), 0.0, 0.0))


def layout(w, d, h, form="wall", variant=0, key="video_rack"):
    """Every part at slot (w, d, h): ``(prims, facts)``."""
    if form not in FORMS:
        raise ValueError(f"video_rack: no form {form!r}; the forms are {', '.join(FORMS)}")
    out = []
    xa, xb = -w / 2.0, w / 2.0
    n_bays = int(math.ceil(w / BAY_MAX - 1e-9))
    bays_ = [(xa + (w / n_bays) * (i + 0.5), w / n_bays) for i in range(n_bays)]
    island = form == "island"
    # an island's end panels stand 3 mm inside the slot's ends: its aisle-end
    # signs are what reach them
    inset = 0.003 if island else 0.0
    # --- the frame. Each part buries into its neighbours at its own depth,
    # 4 mm or more from every parallel face (the snack gondola's rule).
    # the wall form's kick ends 8 mm INSIDE the back board (whose front face
    # is at d/2 - 0.030: ending there, the two shared it)
    out.append(P.box("VideoRack_Kick", "kick", (xa + 0.010, -d / 2.0 + 0.03, 0.004),
                     (xb - 0.010, d / 2.0 - (0.03 if island else 0.022), KICK_H)))
    for s in (-1, 1):
        ex0, ex1 = sorted((s * (w / 2.0 - inset), s * (w / 2.0 - 0.020 - inset)))
        out.append(P.box("VideoRack_Frame", "steel", (ex0, -d / 2.0, 0.0), (ex1, d / 2.0, h)))
    out.append(P.box("VideoRack_Frame", "steel", (xa + 0.008, -d / 2.0 + 0.036, h - TOP_T - 0.006),
                     (xb - 0.008, d / 2.0 - 0.036, h - 0.006)))
    if island:
        out.append(P.box("VideoRack_Board", "board", (xa + 0.014, -SPINE_T / 2.0, KICK_H - BURY),
                         (xb - 0.014, SPINE_T / 2.0, h - TOP_T - 0.006 + BURY)))
        y_back = -SPINE_T / 2.0 + BURY
        up_y = (-SPINE_T / 2.0 - 0.012, SPINE_T / 2.0 + 0.012)
    else:
        out.append(P.box("VideoRack_Board", "board", (xa + 0.014, d / 2.0 - 0.006 - BOARD_T, KICK_H - BURY),
                         (xb - 0.014, d / 2.0 - 0.006, h - 0.012)))
        y_back = d / 2.0 - 0.006 - BOARD_T + 0.008
        up_y = (-d / 2.0 + 0.05, d / 2.0 - 0.006 - BOARD_T + 0.012)
    for j in range(1, n_bays):
        ux = xa + j * bays_[0][1]
        out.append(P.box("VideoRack_Frame", "steel", (ux - UPRIGHT_W / 2.0, up_y[0], KICK_H - 0.012),
                         (ux + UPRIGHT_W / 2.0, up_y[1], h - TOP_T - 0.006 + 0.012)))
    y_front = -d / 2.0 + 0.03
    side, n_items, genres = _face(bays_, h, y_front, y_back, form, key, variant, "a")
    out += side
    if island:
        other, n_b, g_b = _face(bays_, h, y_front, y_back, form, key, variant, "b")
        out += [P.rotate_z(p, math.pi, about=(0.0, 0.0)) for p in other]
        n_items += n_b
        out.append(_end_sign(w, h, genres[-1], 1))
        out.append(_end_sign(w, h, genres[0], -1))
        genres += g_b
    facts = {"form": form, "bays": n_bays, "bay_width": bays_[0][1],
             "tapes": n_items, "boxes": n_items if form == "display" else 0,
             "shelves": len(shelf_levels(h, form)[0]), "genres": genres,
             "unit": unit_colour(form, variant),
             "collision": ((-w / 2.0, -d / 2.0, 0.0), (w / 2.0, d / 2.0, h))}
    return out, facts


def plan(w, d, h, form="wall", variant=0, key="video_rack"):
    prims, facts = layout(w, d, h, form, variant, key)
    return {"prims": prims, "facts": facts}


def signed_volume(p):
    vs = p["verts"]
    tot = 0.0
    for f in p["faces"]:
        a = vs[f[0]]
        for k in range(1, len(f) - 1):
            b, c = vs[f[k]], vs[f[k + 1]]
            tot += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return tot / 6.0


# --- the art ------------------------------------------------------------------------------

TILE = (40, 70)           # a box's front: 0.105 x 0.19 m
COLS = 6
STRIP = (240, 46)         # forty spines: 1.0 x 0.19 m
HEAD_TILE = (168, 24)     # a section board, 7 : 1 as the board is
CAP_TILE = (48, 20)       # an aisle-end sign
TAG_TILE = (12, 8)        # a shelf tag
SIGN_YELLOW = (244, 208, 40)


def _set(c, text, x0, y, tw, ink, plate=None, face="m5x7", scale=1):
    """``text`` centred on a tile ``tw`` wide whose left edge is ``x0``, its
    top at ``y``. A word wider than the tile raises: a defect, not a crop."""
    m = pt.trim(pt.render(text, scale, face))
    assert len(m[0]) <= tw - 2, (text, len(m[0]), tw)
    mx = x0 + (tw - len(m[0])) // 2
    if plate is not None:
        c.rect(mx - 2, y - 1, mx + len(m[0]) + 2, y + len(m) + 1, plate)
    c.mask(m, mx, y, ink)
    return len(m)


def _dark(rgb, by=60):
    return tuple(max(0, v - by) for v in rgb)


def _picture(c, g, cx, cy, s, second, ink, body):
    """The box's one picture, by its genre. Nothing here is a figure."""
    if g in ("new", "action"):                    # a burst
        for k in range(-s, s + 1):
            c.rect(cx - (s - abs(k)), cy + k, cx + (s - abs(k)) + 1, cy + k + 1, second)
        c.rect(cx - s, cy - 1, cx + s + 1, cy + 2, second)
        c.rect(cx - 1, cy - s, cx + 2, cy + s + 1, second)
    elif g == "comedy":                           # a grin
        _ellipse(c, cx, cy, s, s, second)
        c.rect(cx - s // 2, cy - s // 3, cx - s // 2 + 2, cy - s // 3 + 2, body)
        c.rect(cx + s // 2 - 2, cy - s // 3, cx + s // 2, cy - s // 3 + 2, body)
        c.rect(cx - s // 2, cy + s // 3, cx + s // 2 + 1, cy + s // 3 + 2, body)
    elif g == "horror":                           # two eyes in the dark
        _ellipse(c, cx - s // 2, cy, s // 3 + 1, s // 4 + 1, second)
        _ellipse(c, cx + s // 2, cy, s // 3 + 1, s // 4 + 1, second)
        c.rect(cx - s // 2, cy - 1, cx - s // 2 + 1, cy + 2, body)
        c.rect(cx + s // 2, cy - 1, cx + s // 2 + 1, cy + 2, body)
    elif g == "drama":                            # a lit window in a wall
        c.rect(cx - s, cy - s, cx + s + 1, cy + s + 1, _dark(body, 30))
        c.rect(cx - s // 2, cy - s // 2, cx + s // 2 + 1, cy + s // 2 + 1, second)
        c.rect(cx, cy - s // 2, cx + 1, cy + s // 2 + 1, _dark(body, 30))
    elif g == "scifi":                            # a ringed planet
        _ellipse(c, cx, cy, s * 2 // 3, s * 2 // 3, second)
        c.rect(cx - s, cy, cx + s + 1, cy + 2, ink)
    else:                                         # the back room: a pair of lips
        _ellipse(c, cx - s // 3, cy - 1, s // 2, s // 3, second)
        _ellipse(c, cx + s // 3, cy - 1, s // 2, s // 3, second)
        _ellipse(c, cx, cy + s // 4, s * 2 // 3, s // 3, second)
        c.rect(cx - s * 2 // 3, cy, cx + s * 2 // 3 + 1, cy + 1, _dark(second, 90))


def _paint_box(c, x0, y0, t):
    tid, g, words, body, second, ink = t
    tw, th = TILE
    body, second, ink = hex_rgb(body), hex_rgb(second), hex_rgb(ink)
    c.rect(x0, y0, x0 + tw, y0 + th, body)
    c.rect(x0, y0, x0 + tw, y0 + 2, tuple(min(255, v + 36) for v in body))
    y = y0 + 5
    for word in words:
        y += _set(c, word, x0, y, tw, ink, None) + 2
    _picture(c, g, x0 + tw // 2, y0 + 44, 8, second, ink, body)
    # the store's rental sticker, bottom left; the back room's boxes carry
    # the 18+ badge beside it
    c.rect(x0 + 2, y0 + th - 12, x0 + 16, y0 + th - 2, (244, 220, 60))
    m = pt.trim(pt.render(STICKER, 1, "m5x7"))
    c.mask(m, x0 + 3, y0 + th - 10, (30, 26, 20))
    if g == "adult":
        m = pt.trim(pt.render("18+", 1, "m5x7"))
        bx = x0 + tw - 3 - len(m[0])            # the badge ends 2 px inside the tile
        c.rect(bx - 1, y0 + th - 12, x0 + tw - 2, y0 + th - 2, (20, 16, 20))
        c.mask(m, bx, y0 + th - 10, (255, 208, 232))
    c.rect(x0, y0 + th - 1, x0 + tw, y0 + th, _dark(body, 40))


def _paint_strip(c, x0, y0, g):
    """Forty tape spines, side by side: each its own colour off the
    genre's boxes or a plain black, white or red sleeve; a paler label
    panel with a column of ticks where a title runs up it -- too small to
    read, as a spine is from an aisle -- and on some a rental sticker at
    the foot. One pixel of shadow between tapes."""
    sw, sh = STRIP[0] // STRIP_SPINES, STRIP[1]
    pal = [hex_rgb(BY_ID[t][3]) for t in BY_GENRE[g]] + [(22, 22, 26), (232, 228, 214), (190, 30, 40)]
    for i in range(STRIP_SPINES):
        x = x0 + i * sw
        body = pal[_h("spine", g, i) % len(pal)]
        c.rect(x, y0, x + sw, y0 + sh, body)
        light = sum(body) > 380
        panel = _dark(body, 46) if light else tuple(min(255, v + 70) for v in body)
        if _h("spine", g, i, "p") % 4:
            c.rect(x + 1, y0 + 5, x + sw - 1, y0 + 30, panel)
        tick = (24, 22, 26) if sum(panel) > 300 else (236, 232, 220)
        for y in range(y0 + 8, y0 + 28, 3):
            if _h("spine", g, i, y - y0) % 3:
                c.rect(x + 2, y, x + sw - 2, y + 1, tick)
        if _h("spine", g, i, "s") % 3 == 0:
            c.rect(x + 1, y0 + sh - 9, x + sw - 1, y0 + sh - 4, (244, 220, 60))
        c.rect(x + sw - 1, y0, x + sw, y0 + sh, _dark(body, 70))


def _paint_head(c, x0, y0, g):
    """A section board: the word lettered as large as it sets."""
    text, field, ink = BOARDS[g]
    tw, th = HEAD_TILE
    field, ink = hex_rgb(field), hex_rgb(ink)
    c.rect(x0, y0, x0 + tw, y0 + th, field)
    scale = 2 if len(pt.trim(pt.render(text, 2, "m5x7"))[0]) <= tw - 6 else 1
    m = pt.trim(pt.render(text, scale, "m5x7"))
    _set(c, text, x0, y0 + (th - len(m)) // 2, tw, ink, scale=scale)


def _paint_cap(c, x0, y0, g):
    tw, th = CAP_TILE
    c.rect(x0, y0, x0 + tw, y0 + th, SIGN_YELLOW)
    c.rect(x0, y0, x0 + tw, y0 + 1, (30, 26, 20))
    c.rect(x0, y0 + th - 1, x0 + tw, y0 + th, (30, 26, 20))
    _set(c, BOARDS[g][0], x0, y0 + 6, tw, (30, 26, 20))


def _paint_tag(c, x0, y0, rgb):
    tw, th = TAG_TILE
    c.rect(x0, y0, x0 + tw, y0 + th, rgb)
    c.rect(x0 + 2, y0 + 2, x0 + tw - 2, y0 + 3, (40, 36, 30))
    c.rect(x0 + 2, y0 + 5, x0 + tw - 4, y0 + 6, (40, 36, 30))


def rack_art():
    """ONE image for everything on a rack that is not its frame: a tile a
    title (``tile_<id>``, ``solid_<id>``), a strip of spines a genre
    (``spines_<genre>``; their tops and ends are ``solid_spines``), a
    section board a genre (``head_<genre>``, ``solid_head_<genre>``), an
    aisle-end sign an aisle genre (``cap_<genre>``, ``solid_cap``) and the
    shelf tags. ``{canvas, size, rects, said, name}``; rects are pixel
    boxes, row 0 at the top."""
    tw, th = TILE
    rows = int(math.ceil(len(TITLES) / float(COLS)))
    strips = list(BOARDS)                         # every genre, the back room's too
    heads = list(BOARDS)
    y_strip = rows * th
    y_head = y_strip + len(strips) * STRIP[1]
    y_cap = y_head + len(heads) * HEAD_TILE[1]
    y_tag = y_cap + CAP_TILE[1]
    y_solid = y_tag + TAG_TILE[1]
    W, H = COLS * tw, y_solid + 8
    assert STRIP[0] <= W and HEAD_TILE[0] <= W and len(AISLE_GENRES) * CAP_TILE[0] <= W
    c = Canvas(W, H, (20, 20, 20))
    rects, said, solids = {}, [], []

    def put(name, rect):
        assert name not in rects, name
        rects[name] = rect

    for i, t in enumerate(TITLES):
        x0, y0 = (i % COLS) * tw, (i // COLS) * th
        _paint_box(c, x0, y0, t)
        put("tile_" + t[0], (x0, y0, x0 + tw, y0 + th))
        said += list(t[2]) + [STICKER]
        solids.append(("solid_" + t[0], hex_rgb(t[3])))
    for j, g in enumerate(strips):
        y0 = y_strip + j * STRIP[1]
        _paint_strip(c, 0, y0, g)
        put("spines_" + g, (0, y0, STRIP[0], y0 + STRIP[1]))
    solids.append(("solid_spines", (26, 26, 30)))
    for j, g in enumerate(heads):
        y0 = y_head + j * HEAD_TILE[1]
        _paint_head(c, 0, y0, g)
        put("head_" + g, (0, y0, HEAD_TILE[0], y0 + HEAD_TILE[1]))
        said.append(BOARDS[g][0])
        solids.append(("solid_head_" + g, hex_rgb(BOARDS[g][1])))
    for j, g in enumerate(AISLE_GENRES):
        x0 = j * CAP_TILE[0]
        _paint_cap(c, x0, y_cap, g)
        put("cap_" + g, (x0, y_cap, x0 + CAP_TILE[0], y_cap + CAP_TILE[1]))
    solids.append(("solid_cap", SIGN_YELLOW))
    for j, (name, rgb) in enumerate(zip(TAGS, TAG_RGB)):
        x0 = j * TAG_TILE[0]
        _paint_tag(c, x0, y_tag, rgb)
        put(name, (x0, y_tag, x0 + TAG_TILE[0], y_tag + TAG_TILE[1]))
        solids.append(("solid_" + name, rgb))
    assert len(solids) * 4 <= W, len(solids)
    for i, (name, rgb) in enumerate(solids):
        sx = i * 4
        c.rect(sx, y_solid + 2, sx + 3, y_solid + 6, rgb)
        put(name, (sx, y_solid + 2, sx + 3, y_solid + 6))
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "rects": rects, "said": said,
            "name": f"videorack_{W}x{H}_{digest:08x}"}
