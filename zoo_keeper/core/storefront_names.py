"""What the lit cabinet sign over a building's door says: ONE table, here.

Zoo 1.37.0. Cold run 9120's FLAPPAHS walk found the box over the gas
station's door lit and BLANK, and it was not that store's defect: Deli
Counter derives one sign over the storefront door of every building with
windows and a door (102 across the library, about fifty kinds), and
`sign_box` paints its face only from a Pixelcoat sign pack -- no theme ships
one -- so every one of them was a plain glowing panel. The walker: "do the
blank sign over the door next".

WHO SAYS WHAT. Deli Counter stamps the sign anchor with the building's
identity (`business`: `level_design.club_building_id`, its name and the
recipe that made it). This reads the KIND from that string's words and the
NAME from the kind's list by the string's crc32 -- the same key and the same
modulus Deli Counter's `_make_volume` gives a club's `neon_sign`, so a club's
door says what its neon says. A gas station says FLAPPAHS, as its pylon and
its coffee sign do. A civic building says what it is in plain words; a
building of no kind here shows its street number, which is what a lit box
over an ordinary door is.

EVERY NAME IS INVENTED: Delco slang, PG-13, the walker's rule for every
branded surface. Place names are places. `tests/test_storefront_names.py`
holds every string against the factory's denylists and the real chains a
writer would reach for.
"""
from __future__ import annotations

import re
import zlib

from . import club_names as CN
from . import price_pylon_forms as PY

#: kind -> names. A kind's first match wins, in this order; a word is matched
#: whole against the business string's words.
KINDS = (
    ("club", ("strip",), None),                    # club_names, by the neon's rule
    # `convenience` (1.75.0): the Flappahs store, `convenience_store_a01` or a
    # generated `<level> convenience_store`, carries none of the other words.
    ("gas", ("gas", "fuel", "gs", "stop", "convenience"), (PY.STORE,)),
    ("pizza", ("pizza", "pizzeria"), ("PIE HOLE PIZZA", "TOMATO PIE TONY'S", "SAUCE BOSS PIZZA")),
    ("deli", ("deli", "hoagie"), ("JAWN'S HOAGIES", "WOODER ICE & HOAGIES", "SCRAPPLE & SONS DELI",
                                  "YO! DELI")),
    ("pawn", ("pawn",), ("HOCK IT HERE", "CASH 4 YOUR JAWN", "GOLD N STUFF PAWN")),
    ("bank", ("bank", "credit", "savings"), ("FIRST DELCO SAVINGS", "PIKE SAVINGS & LOAN",
                                             "MATTRESS MONEY TRUST", "YOUSE CREDIT CO-OP")),
    ("pharmacy", ("pharmacy", "drug"), ("PILLS N THRILLS", "DOC'S DISCOUNT DRUGS")),
    ("clinic", ("clinic", "hospital"), ("URGENT-ISH CARE", "WALK-IN CLINIC")),
    ("market", ("market", "supermarket", "grocery"), ("PIKE FOOD MARKET", "THE BIG CART",
                                                       "SCRAPPLE SUPERMARKET")),
    ("card", ("card",), ("TOPDECK TONY'S", "MINT-ISH CARDS")),
    # THE VIDEO STORE (1.43.0), named by the walker, 2026-10-02. `video`
    # alone: "rental" and "movies" are words other buildings could carry.
    ("video", ("video",), ("MACDADE MOVIES",)),
    ("brewery", ("brewery",), ("DOWN THE SHORE BREWING", "HONEST HON BREW CO")),
    ("casino", ("casino",), ("LUCKY JAWN CASINO", "THE BROKE BANK CASINO")),
    ("funeral", ("funeral",), ("STIFF & SONS FUNERAL HOME", "RESTFUL PINES FUNERAL HOME")),
    ("country", ("country",), ("PIKE HILLS COUNTRY CLUB",)),
    ("police", ("police",), ("POLICE",)),
    ("court", ("courthouse", "court"), ("COURT HOUSE",)),
    ("museum", ("museum",), ("MUSEUM",)),
    ("rail", ("rail", "train"), ("RAIL STATION",)),
    ("airport", ("airport",), ("TERMINAL A",)),
    ("arena", ("arena",), ("ARENA",)),
    ("stadium", ("stadium",), ("STADIUM",)),
)
#: The kinds that say what they are rather than who runs them: a plain field
#: and a plain face.
CIVIC = {"police", "court", "museum", "rail", "airport", "arena", "stadium"}
#: A building of no kind: its street number, in this range.
NUMBERS = (100, 2999)
CIVIC_COLOURS = ((18, 34, 70), (230, 230, 220), (250, 250, 244))
NUMBER_COLOURS = ((24, 24, 26), (200, 200, 196), (250, 244, 214))


def _words(business):
    return set(w for w in re.split(r"[^a-z]+", str(business or "").lower()) if w)


def key(business):
    """Deli Counter's key for a building's names (`_make_volume`)."""
    return zlib.crc32(str(business or "").encode("utf-8")) & 0xFFFFFFFF


def sign_for(business):
    """``{kind, text, colours}`` for the sign over ``business``'s door:
    colours are (field, rule, ink)."""
    words = _words(business)
    k = key(business)
    for kind, match, names in KINDS:
        if not words & set(match):
            continue
        if kind == "club":
            return {"kind": kind, "text": CN.name_for(k % len(CN.NAMES)),
                    "colours": PY.COLOURWAYS[(k // 7) % len(PY.COLOURWAYS)]}
        colours = CIVIC_COLOURS if kind in CIVIC else PY.COLOURWAYS[(k // 7) % len(PY.COLOURWAYS)]
        if kind == "gas":
            colours = PY.COLOURWAYS[0]        # the pylon's, variant 0
        return {"kind": kind, "text": names[k % len(names)], "colours": colours}
    lo, hi = NUMBERS
    return {"kind": "number", "text": str(lo + k % (hi - lo + 1)), "colours": NUMBER_COLOURS}


def all_strings():
    out = []
    for _kind, _m, names in KINDS:
        out += list(names or ())
    return out


TEXEL = 80                 # px a metre: the pylon's, read from the street


def layout(text, w, h, face):
    """``(scale, lines)``: the largest scale ``text`` sets at in ``w`` x
    ``h`` px, one line or wrapped, stacked on the face's OWN line height --
    `fit_text` stacks on the trimmed glyphs plus 1-2 px, which blurred two
    lines into one on a 0.6 m sign from the street (the first render). One
    line wins a tie."""
    from . import pixel_type as pt
    best = (0, [text])
    for s in range(6, 0, -1):
        for lines in ([text], pt.wrap(text, w, s, face) or []):
            if not lines:
                continue
            tall = pt.line(face) * s * (len(lines) - 1) + len(pt.trim(pt.render(lines[-1], s, face)))
            wide = max(pt.ink_width(ln, s, face) for ln in lines)
            if wide <= w and tall <= h and s > best[0]:
                best = (s, lines)
        if best[0]:
            return best
    return best


def paint(spec):
    """The sign's face as a Canvas: its field, a rule top and bottom, and the
    name as large as it sets, outlined in the rule. ``c.unset`` lists the
    name if it did not set."""
    from . import pixel_type as pt
    from .vending_forms import Canvas
    w = max(8, int(round(spec["w_m"] * TEXEL)))
    h = max(8, int(round(spec["h_m"] * TEXEL)))
    field, rule, ink = (tuple(x) for x in spec["colours"])
    c = Canvas(w, h, field)
    c.rect(0, 2, w, 4, rule)
    c.rect(0, h - 4, w, h - 2, rule)
    c.unset = []
    if spec.get("edge"):
        return c
    face = PY.HEAD_FACE
    s, lines = layout(spec["text"], w - 10, h - 14, face)
    if not s:
        face = "m5x7"
        s, lines = layout(spec["text"], w - 10, h - 14, face)
    if not s:
        c.unset = [spec["text"]]
        return c
    masks = [pt.trim(pt.render(ln, s, face)) for ln in lines]
    step = pt.line(face) * s
    tall = step * (len(masks) - 1) + len(masks[-1])
    y = (h - tall) // 2
    for m in masks:
        x = (w - len(m[0])) // 2
        c.mask(m, x, y, rule, grow=1)
        c.mask(m, x, y, ink)
        y += step
    return c
