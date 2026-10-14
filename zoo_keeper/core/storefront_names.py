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

import numpy as np

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
            # A strip club by Deli Counter's own rule (`level_design.
            # _strip_club_building`: "strip_club" in the id), not the word
            # `strip` alone. Until 1.76.0 `strip_retail_a01`, a retail strip,
            # said THE WOODER HOLE over its door.
            if "strip_club" not in str(business or "").lower():
                continue
            return {"kind": kind, "text": CN.name_for(k % len(CN.NAMES)),
                    "colours": PY.COLOURWAYS[(k // 7) % len(PY.COLOURWAYS)]}
        colours = CIVIC_COLOURS if kind in CIVIC else PY.COLOURWAYS[(k // 7) % len(PY.COLOURWAYS)]
        if kind == "gas":
            colours = PY.COLOURWAYS[0]        # the pylon's, variant 0
        return {"kind": kind, "text": names[k % len(names)], "colours": colours}
    lo, hi = NUMBERS
    return {"kind": "number", "text": str(lo + k % (hi - lo + 1)), "colours": NUMBER_COLOURS}


#: WHAT A DOOR SAYS UNDER ITS BAND (1.112.0). Where Level Factory hangs a street band naming the shop, the door box
#: said the same name again -- 1.79.0's one name on both signs, the walker's option A of 2026-10-06 -- and on a
#: one-storey front the two stack. The walker, at cold run 9305's pharmacy: "double sign here looks...redundant",
#: and chose the trade for the door. A civic building's words are its trade already; a kind with no word here, and a
#: building of no kind, says OPEN.
TRADE = {"club": "OPEN", "gas": "OPEN 24 HOURS", "pizza": "PIZZA", "deli": "DELI", "pawn": "PAWN", "bank": "BANK",
         "pharmacy": "PHARMACY", "clinic": "CLINIC", "market": "GROCERY", "card": "CARDS", "video": "VIDEO",
         "brewery": "BREWERY", "casino": "CASINO", "funeral": "FUNERAL HOME", "country": "CLUBHOUSE"}


def trade_for(business):
    """``{kind, text, colours}`` for the sign over a door whose building's band names it (1.112.0): the trade, in
    the colours `sign_for` gives the name."""
    said = sign_for(business)
    if said["kind"] in CIVIC:
        return said
    return {"kind": said["kind"], "text": TRADE.get(said["kind"], "OPEN"), "colours": said["colours"]}


def all_strings():
    out = []
    for _kind, _m, names in KINDS:
        out += list(names or ())
    return out + sorted(set(TRADE.values()) | {"OPEN"})


TEXEL = 80                 # px a metre: the pylon's, read from the street
#: THE SIGN IS PAINTED SMOOTH (1.90.0), at this many times `TEXEL`. The walker,
#: 2026-10-09, walking club_block_014: "need better looking fonts on these
#: signs", then "use Blue Highway for the shop signs". Until 1.89.0 the name
#: was `pixel_type`'s Pixel Operator at a whole scale, 80 px a metre, sampled
#: Closest: a CRT's letter on a lit acrylic panel. The realism trial paints a
#: machine's art at three times its texel and samples it filtered (1.46.0),
#: and so does this: a 3.2 x 0.6 m face is 768 x 144 px.
DENSITY = 3
#: WHOSE HAND A SIGN IS IN: a voice's owner in `smooth_type.OWNERS`, the
#: walker's font catalog ("Assign a typeface to an owner"). A shop's sign is
#: the shop's own hand, Blue Highway, in its condensed weight: a sign is a
#: strip, and the narrow face sets a long name biggest (the mock-up of
#: 2026-10-09, sent to the walker with that recommendation; `"shop"` is the
#: bold and `"shop_copy"` the regular, one word away). A civic building's
#: fascia is the institution's, Aileron Bold.
VOICES = {"shop": "shop_small", "civic": "maker"}
#: Two lines' baselines apart, in caps: room for a cap and a third of one.
LINE_STEP = 1.32
#: The least cap height a name is set at, in painted px: 5 cm on the sign.
MIN_CAP = 12
#: The outline in the rule's colour, in painted px: the pixel sign's one-texel
#: `grow`, at this density.
OUTLINE = DENSITY


def voice_for(kind):
    """The voice the sign over a ``kind`` building's door speaks in: a civic
    building's is the institution's, every other the shop's own."""
    return "civic" if kind in CIVIC else "shop"


def _splits(text):
    """The name on one line, and on two at the word break nearest even."""
    words = str(text).split()
    out = [[str(text)]]
    if len(words) > 1:
        i = min(range(1, len(words)),
                key=lambda k: abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
        out.append([" ".join(words[:i]), " ".join(words[i:])])
    return out


def _block(lines, cap, face):
    """``lines`` set at ``cap`` in ``face``, each centred on the widest, their
    baselines `LINE_STEP` caps apart: uint8 coverage trimmed to the ink.
    Untrimmed, every line of one face at one cap is one line box tall, so a
    line's offset is its baseline's."""
    from . import smooth_type as ST
    covs = [ST.coverage(ln, cap, face, trim=False) for ln in lines]
    step = int(round(cap * LINE_STEP))
    wide = max(c.shape[1] for c in covs)
    tall = max(i * step + c.shape[0] for i, c in enumerate(covs))
    out = np.zeros((tall, wide), dtype=np.uint8)
    for i, c in enumerate(covs):
        x = (wide - c.shape[1]) // 2
        view = out[i * step:i * step + c.shape[0], x:x + c.shape[1]]
        np.maximum(view, c, out=view)
    ys = np.where(out.max(axis=1) > 0)[0]
    xs = np.where(out.max(axis=0) > 0)[0]
    if not len(ys):
        return np.zeros((1, 1), dtype=np.uint8)
    return out[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]


def layout(text, w, h, voice="shop", min_cap=MIN_CAP):
    """``(face, cap, lines)``: ``text`` in ``voice``'s face at the largest cap
    height that sets inside ``w`` x ``h`` px, on one line or two; one line
    wins a tie. The cap is 0 when not even ``min_cap`` sets: a name that does
    not fit is reported, never cropped. An unknown voice is refused by name."""
    from . import smooth_type as ST
    if voice not in VOICES:
        raise ValueError(f"no sign voice {voice!r}; the voices are {', '.join(sorted(VOICES))}")
    face = ST.owned(VOICES[voice])
    best = (0, [str(text)])
    for lines in _splits(text):
        most = int(h // (1.0 + LINE_STEP * (len(lines) - 1)))
        if most <= best[0]:
            continue                # two lines cannot beat what one has set
        caps = [ST.fit_cap(ln, w, most, face, min_cap) for ln in lines]
        if None in caps or min(caps) <= best[0]:
            continue
        cap = min(caps)
        # `fit_cap` asks the width alone; the composed block, descenders and
        # all, must sit in the box: scale to it, then step past the rounding
        while cap >= min_cap:
            b = _block(lines, cap, face)
            if b.shape[0] <= h and b.shape[1] <= w:
                break
            cap = min(cap - 1, int(cap * min(h / b.shape[0], w / b.shape[1])))
        if cap >= min_cap and cap > best[0]:
            best = (cap, lines)
    return face, best[0], best[1]


def _grow(cov, r):
    """``cov`` dilated by a disc of ``r`` px, padded by ``r`` on every side."""
    h, w = cov.shape
    out = np.zeros((h + 2 * r, w + 2 * r), dtype=np.uint8)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                view = out[r + dy:r + dy + h, r + dx:r + dx + w]
                np.maximum(view, cov, out=view)
    return out


def paint(spec):
    """The sign's face as a Canvas: its field, a rule top and bottom, and the
    name as large as it sets, smooth, outlined in the rule. ``spec["voice"]``
    is `voice_for`'s, the shop's when absent. ``c.unset`` lists the name if
    it did not set."""
    from . import paint as PT
    tx = TEXEL * DENSITY
    w = max(8, int(round(spec["w_m"] * tx)))
    h = max(8, int(round(spec["h_m"] * tx)))
    field, rule, ink = (tuple(x) for x in spec["colours"])
    img = PT.Img(w, h, field)
    img.rect((0, 2 * DENSITY, w, 4 * DENSITY), rule)
    img.rect((0, h - 4 * DENSITY, w, h - 2 * DENSITY), rule)
    if spec.get("edge"):
        return img.to_canvas()
    # the outline is inside the box, as the mock-up's stroke was
    face, cap, lines = layout(spec["text"], w - 10 * DENSITY - 2 * OUTLINE,
                              h - 14 * DENSITY - 2 * OUTLINE, spec.get("voice", "shop"))
    if not cap:
        img.unset.append(spec["text"])
        return img.to_canvas()
    cov = _block(lines, cap, face)
    x = (w - cov.shape[1]) // 2
    y = (h - cov.shape[0]) // 2
    img.mask(_grow(cov, OUTLINE), x - OUTLINE, y - OUTLINE, rule)
    img.mask(cov, x, y, ink)
    return img.to_canvas()
