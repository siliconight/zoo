"""The bumper stickers on a parked car, and the one sheet every car's stickers are cut from (1.120.0).

The walker's look review, 2026-10-19, on the parked cars: "some of the cars need some patina and
wear...rusting....ect....bumper stickers....". What a 1997 Delco bumper said, in the walker's rule for anything a
tool letters: invented, Delco-slang, a bit crass, PG-13, and never a
real mark -- no team, no store, no beer, no station, no school. Where the factory already named a place, the sticker
uses that name rather than inventing a second: Skeevy's, the getaway van's old life (`van_forms`); FLAPPAHS, the
convenience store; The Wooder Hole, the first dive bar.

ONE SHEET, ONE MATERIAL. Every sticker any car carries is a cell of one image (`art`), so a street's stickers are one
material whatever they say -- a car with stickers is one submission more than a car without, and a merged street side
is one more, not one a sticker (CLAUDE.md's draw-call rule). A sticker is printed vinyl: the shop's own hand
(`smooth_type.OWNERS["shop"]`), two lines, a border, rounded corners, and the darkened rim of a thing that has sat on a
bumper through a few winters.

Pure: numpy through `paint.Img`, no bpy -- imported when the sheet is painted, so `car_forms`, which reads the
table to draw a car's stickers, stays free of it. ``cells`` are UV boxes in Blender's convention -- v = 1 at the
image's top row, which is where `materials.image_from_png` puts the PNG's first row.
"""
from __future__ import annotations

import hashlib

#: (first line, second line, background, ink), sRGB. Two lines a sticker, each set as large as its half fits.
STICKERS = (
    ("HONK IF YOU'RE", "FROM DELCO", (236, 233, 222), (178, 32, 36)),
    ("MY OTHER CAR", "IS A TROLLEY", (246, 206, 52), (24, 22, 20)),
    ("I BRAKE FOR", "SOFT PRETZELS", (176, 34, 38), (244, 240, 230)),
    ("WOODER ICE", "OR DIE", (34, 66, 140), (244, 240, 230)),
    ("BLUE ROUTE", "SURVIVOR", (236, 233, 222), (32, 58, 128)),
    ("DOWN THE SHORE", "OR BUST", (120, 186, 222), (18, 36, 82)),
    ("SKEEVY'S", "WOODER ICE", (236, 233, 222), (28, 104, 58)),
    ("I STOPPED AT", "FLAPPAHS", (30, 112, 64), (244, 240, 230)),
    ("MY KID BEAT UP", "YOUR HONOR STUDENT", (236, 233, 222), (24, 22, 20)),
    ("YOUSE DRIVE", "LIKE JAWNS", (230, 112, 34), (24, 22, 20)),
    ("SCRAPPLE", "POWERED", (246, 206, 52), (96, 54, 28)),
    ("THE WOODER HOLE", "LAST CALL CLUB", (24, 22, 20), (232, 176, 52)),
)
#: Words no sticker may carry: real teams, stores, brands, stations and schools of the place and the era. Whole
#: words; `test_car_wear.py` reads every string `strings()` returns against them.
DENY_WORDS = ("EAGLES", "IGGLES", "PHILLIES", "FLYERS", "SIXERS", "76ERS", "WAWA", "TASTYKAKE", "YUENGLING",
              "SEPTA", "ACME", "VILLANOVA", "PENN", "TEMPLE", "DREXEL", "WIP", "WMMR", "WYSP", "ROCKY",
              "KOHR", "PHILADELPHIA", "PHILLY", "GO BIRDS")
#: A sticker's printed size, metres (11 x 3 inches, the common bumper sticker), and its cell on the sheet: 256 px
#: across 0.28 m is 914 px a metre, which a sticker read from the kerb a car's length away does not out-resolve, and
#: the sheet stays small enough that a module carrying it costs little. NO GRAIN: noise does not compress, and it is
#: most of a PNG's size -- measured on this sheet, 294 KB with `Img.grain` at 2.0, 247 KB at 1.0, 75 KB without (the
#: first cut's 320 x 86 cells at 5.0 made 543 KB) -- for a texture no camera on the kerb resolves.
SIZE = (0.28, 0.075)
CELL = (256, 69)
PAD = 4
COLS = 2
RADIUS = 6
BORDER = 3
#: Between a sticker's two lines: the first cut set each line to fill its half and the lines touched.
LINE_GAP = 4
#: Whose hand sets the lines (`smooth_type.OWNERS`: "a sticker somebody stuck on"), and the smallest capital a line
#: may shrink to before the sheet refuses it.
OWNER = "shop"
MIN_CAP = 9


def strings():
    """Every line the sheet sets, for the denylist test."""
    return [line for a, b, _bg, _ink in STICKERS for line in (a, b)]


def layout():
    """``(W, H, boxes)``: the sheet's size in pixels and each sticker's pixel box ``(x0, y0, x1, y1)``, row 0 at the
    top, in `STICKERS`' order."""
    rows = (len(STICKERS) + COLS - 1) // COLS
    W = COLS * CELL[0] + (COLS + 1) * PAD
    H = rows * CELL[1] + (rows + 1) * PAD
    boxes = []
    for k in range(len(STICKERS)):
        c, r = k % COLS, k // COLS
        x0 = PAD + c * (CELL[0] + PAD)
        y0 = PAD + r * (CELL[1] + PAD)
        boxes.append((x0, y0, x0 + CELL[0], y0 + CELL[1]))
    return W, H, boxes


def cells():
    """Each sticker's UV box ``(u0, v0, u1, v1)``, v = 1 at the sheet's top row, inset half a pixel so a clamped,
    linearly filtered sample never reads the gutter."""
    W, H, boxes = layout()
    out = []
    for x0, y0, x1, y1 in boxes:
        out.append(((x0 + 0.5) / W, 1.0 - (y1 - 0.5) / H, (x1 - 0.5) / W, 1.0 - (y0 + 0.5) / H))
    return out


def art():
    """The sheet: ``{"png", "name", "size", "cells", "unset"}``. Every sticker is a rounded card in its background
    with a border in its ink, its two lines set in the shop's face as large as each half of the card fits, a gap
    between them, and the darkened rim of a few winters. ``unset`` lists any line that did not fit at `MIN_CAP`
    (a test holds it empty). Deterministic: the name carries the pixels' identity."""
    from . import paint as PT
    from . import smooth_type as ST
    face = ST.owned(OWNER)
    W, H, boxes = layout()
    img = PT.Img(W, H, (128, 128, 128))
    for (top, bottom, bg, ink), (x0, y0, x1, y1) in zip(STICKERS, boxes):
        img.rrect((x0, y0, x1, y1), RADIUS, ink)
        img.rrect((x0 + BORDER, y0 + BORDER, x1 - BORDER, y1 - BORDER), max(1, RADIUS - BORDER), bg)
        ix0, iy0, ix1, iy1 = x0 + 3 * BORDER, y0 + 2 * BORDER, x1 - 3 * BORDER, y1 - 2 * BORDER
        mid = (iy0 + iy1) / 2.0
        img.text(top, (ix0, iy0, ix1, mid - LINE_GAP / 2.0), ink, face=face, min_cap=MIN_CAP)
        img.text(bottom, (ix0, mid + LINE_GAP / 2.0, ix1, iy1), ink, face=face, min_cap=MIN_CAP)
        img.edge_dark((x0, y0, x1, y1), depth=8, strength=0.22, radius=RADIUS)
    canvas = img.to_canvas()
    png = canvas.png()
    return {"png": png, "name": "Car_stickers_" + hashlib.sha1(png).hexdigest()[:8], "size": (W, H),
            "cells": cells(), "unset": list(img.unset)}
