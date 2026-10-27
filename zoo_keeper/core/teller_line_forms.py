"""teller_line's forms (1.137.0): what a bank's line says over its windows.

Pure -- no Blender. `recipes/teller_line.py` builds the counter, posts, header
and glass; in the ``bank`` form it asks `bank_board` for the NAMEBOARD on the
header's public face (-Y, where the trays are): the bank's name across its top
band and each window's number over its bay -- the walker's bank comps, a name
over the line and a number on every window.

THE BOARD IS A PANEL, NOT A DECAL. A quad on the header's face would share its
plane, and one hovering in front of it would float; so the header steps back
by the board's thickness and the board fills the step, its art the front and
its four edges the rim, with no back face -- `sign_box`'s face, built the same
way for the same census (1.37.0). The envelope is unchanged: the counter and
the end posts still run the full depth.

THE VARIANT IS THE DOOR SIGN'S. `storefront_names.sign_for` names a bank
``names[k % 4]`` in ``COLOURWAYS[(k // 7) % 4]``, ``k`` the crc32 of its
business; the line's sixteen variants are the four names in the four
colourways, ``variant_for(business)`` the one that sign picks, so a line
stamped with it reads the name and colours over the bank's door.
"""
from __future__ import annotations

from . import prims as P
from . import price_pylon_forms as PY
from . import storefront_names as SN

FORMS = ("auto", "bank")
#: The board's thickness, which the header steps back by.
BOARD_T = 0.02
#: How far the board stands in from the header's edges and the end posts, so
#: no face of it lies in a face of theirs.
BOARD_INSET = 0.01
#: The shortest board that sets every word with its windows numbered, metres:
#: measured off `paint` at the narrowest numbered line (two 1.0 m bays, a
#: 1.78 m board), every bank name and the digits 8 and 9 -- unset at 0.29,
#: set at 0.30. A board under it carries the name alone, which set from 0.17
#: on the narrowest line of all (1.0 m). They move when `storefront_names`'
#: density, `MIN_CAP` or `RULE` / `PAD` here do.
NUMBERED_MIN = 0.30
#: The name's share of a numbered board; the numbers have the rest.
NAME_SHARE = 0.52
#: The bank form's header, metres: its board 0.43 m, the name about 17 cm
#: tall and the numbers about 15. A design choice, not a minimum; the
#: default line's 0.20 m header sets nothing at reading size. A first board
#: of a name tile and a tile a number, each paying a sign's margins, needed
#: 0.57 m and still set the name 9 cm tall on a 6 m line.
BANK_HEADER = 0.45
#: How far a middle post reaches up into a raised header: past its underside,
#: so the two share no plane, and short of the board's lower edge, which
#: stands `BOARD_INSET` above it -- at 0.02 the post's front ran 1 cm up the
#: board's face, the one pair the bank form's first census found.
POST_INTO_HEADER = BOARD_INSET / 2.0


def bank_names():
    for kind, _match, names in SN.KINDS:
        if kind == "bank":
            return names
    raise ValueError("storefront_names has no bank kind")


def bank_said(variant):
    """``{text, colours}``: the variant's bank name, ``variant % 4``, in its
    colourway, ``variant // 4``."""
    names = bank_names()
    v = int(variant or 0)
    return {"text": names[v % len(names)], "colours": PY.COLOURWAYS[(v // len(names)) % len(PY.COLOURWAYS)]}


def variant_for(business):
    """The variant whose name and colours are the ones `storefront_names.
    sign_for` puts over ``business``'s door: what Deli Counter stamps on a
    bank's teller slot."""
    k = SN.key(business)
    return k % len(bank_names()) + len(bank_names()) * ((k // 7) % len(PY.COLOURWAYS))


#: The line's variants: every name in every colourway.
VARIANTS = 4 * len(PY.COLOURWAYS)


def header_of(header, h, counter_h):
    """The bank form's header height: `BANK_HEADER`, never less than the
    genome's, never more than half the space above the counter."""
    return min(max(float(header), BANK_HEADER), (h - counter_h) * 0.5)


def bank_board(w, d, h, post, header, runs, variant):
    """``(prims, tiles)`` for the nameboard: one art quad (``tile`` set) and a
    rim, in the recipe's frame (centre pivot, public face at -Y); ``runs``
    are `_bays.bays`' ``(x_centre, width)``. One bay carries the name alone;
    more carry the name over a number a bay -- when the board is tall enough
    for both bands, and the name alone on a line too short for them."""
    hw, hh = w / 2.0, h / 2.0
    x0, x1 = -hw + post + BOARD_INSET, hw - post - BOARD_INSET
    z0, z1 = hh - header + BOARD_INSET, hh - BOARD_INSET
    y0, y1 = -d / 2.0, -d / 2.0 + BOARD_T
    said = bank_said(variant)
    numbered = len(runs) >= 2 and z1 - z0 >= NUMBERED_MIN
    numbers = []
    if numbered:
        numbers = [((min(x1, max(x0, bx)) - x0) / (x1 - x0), str(i + 1)) for i, (bx, _bw) in enumerate(runs)]
    quad_uv = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))]
    art = P.mesh("TellerLine_BoardFace", "art", [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
                 [(0, 1, 2, 3)])
    art["tile"] = "board"
    art["uvs"] = list(quad_uv)
    rim = P.box("TellerLine_BoardRim", "art", (x0, y0, z0), (x1, y1, z1))
    # the box's bottom, top and two ends; its front is the art, and it has
    # no back -- that would lie in the header's stepped face
    rim["faces"] = [f for k, f in enumerate(rim["faces"]) if k in (0, 1, 3, 5)]
    rim["tile"] = "edge"
    rim["uvs"] = list(quad_uv) * len(rim["faces"])
    tiles = {"board": {"kind": "teller_board", "w_m": x1 - x0, "h_m": z1 - z0, "text": said["text"],
                       "colours": said["colours"], "voice": SN.voice_for("bank"), "numbers": numbers,
                       "bay_m": min(bw for _bx, bw in runs)},
             "edge": {"kind": "storefront_sign", "w_m": 0.1, "h_m": 0.1, "edge": True,
                      "text": "", "colours": said["colours"]}}
    return [art, rim], tiles


#: The board's one rule top and bottom, and the rule between its bands, in
#: painted px; the pad every word keeps from a rule or an edge.
RULE = 2
PAD = 1


def paint(spec):
    """The board as a Canvas (`card_art`'s ``teller_board`` kind): the field,
    a rule top and bottom, the name as large as it sets across the top band,
    and under a rule each window's number centred on its bay. One tile and
    one set of rules, where a name tile and a tile a number paid a sign's
    margins each and set the name 9 cm tall on a 6 m line. ``c.unset`` lists
    every word that did not set."""
    from . import paint as PT
    D, O = SN.DENSITY, SN.OUTLINE
    tx = SN.TEXEL * D
    w = max(8, int(round(spec["w_m"] * tx)))
    h = max(8, int(round(spec["h_m"] * tx)))
    field, rule, ink = (tuple(x) for x in spec["colours"])
    img = PT.Img(w, h, field)
    r, pad = RULE * D, PAD * D
    img.rect((0, 0, w, r), rule)
    img.rect((0, h - r, w, h), rule)
    numbers = spec.get("numbers") or []
    split = h - r
    if numbers:
        split = int(round(h * NAME_SHARE))
        img.rect((0, split - r // 2, w, split - r // 2 + r), rule)

    def word(text, cx, top, bottom, box_w):
        face, cap, lines = SN.layout(text, box_w - 2 * pad - 2 * O, bottom - top - 2 * pad - 2 * O,
                                     spec.get("voice", "shop"))
        if not cap:
            img.unset.append(text)
            return
        cov = SN._block(lines, cap, face)
        x = int(round(cx - cov.shape[1] / 2.0))
        y = top + (bottom - top - cov.shape[0]) // 2
        img.mask(SN._grow(cov, O), x - O, y - O, rule)
        img.mask(cov, x, y, ink)

    word(spec["text"], w / 2.0, r, split - r // 2, w)
    bay = int(round(spec.get("bay_m", spec["w_m"]) * tx))
    for frac, text in numbers:
        word(text, frac * w, split - r // 2 + r, h - r, min(bay, w))
    return img.to_canvas()
