"""Mint Zoo's SMOOTH faces: anti-aliased glyph tables from CC0 outline fonts.

    python tools/mint_smooth_type.py --fonts <dir> [--face NAME | --all] [--check]

WHY. The walker, 2026-10-02: "this looks like it is made with a 90s GPU ...
replace the retro look". Every letter Zoo painted was a pixel face -- 0 or 255,
on a 5 to 16 px grid, drawn with nearest sampling -- which is the right face
for a CRT and the wrong one for a printed marquee. A printed letter has an
outline, and an outline at texture resolution is grey at its edge.

WHY A TABLE AND NOT THE FONT FILE, as `mint_pixel_type.py` says of the pixel
faces: Zoo builds inside Blender, whose Python has numpy and no PIL. So the
outline is rasterised HERE, once, large -- `EM` px to the em, 8-bit coverage
-- and `core/smooth_type.py` composes those masters and area-resamples them
down to whatever size a tile sets its type at. Downsampling coverage by area
is exact anti-aliasing; a master four times the largest size used loses
nothing a tile can show.

NO KERNING: glyphs are composed at their advances. Measured on the strings a
machine carries it is not what reads as wrong; if it ever is, a pair table is
the fix, not the font file.

THE FACES are CC0, vendored by Pixelcoat with their licence notes
(`assets/fonts/blue_highway/`, `assets/fonts/minisystem/`): Ray Larabie's
Blue Highway (1998), a highway-sign sans, and Minisystem (2004), a dot
display face. Both from typodermicfonts.com/public-domain/, "released under
CC0 1.0 Universal".
"""
from __future__ import annotations

import argparse
import os
import sys

EM = 64
CHARS = "".join(chr(c) for c in range(32, 127))
#: name -> (file under the fonts dir, module it mints to)
FACES = {
    "highway": ("blue_highway/Blue Highway Rg.otf", "highway"),
    "highway_bold": ("blue_highway/Blue Highway Bd.otf", "highway_bold"),
    "highway_cond": ("blue_highway/Blue Highway Cd.otf", "highway_cond"),
    "minisystem": ("minisystem/Minisystem.otf", "minisystem"),
    # 1.49.0, the owner pass: a face for each kind of owner (Pixelcoat 0.55.0)
    "aileron": ("aileron/Aileron-SemiBold.otf", "aileron"),
    "aileron_bold": ("aileron/Aileron-Bold.otf", "aileron_bold"),
    "vegur": ("vegur/Vegur-Regular.otf", "vegur"),
    "vegur_bold": ("vegur/Vegur-Bold.otf", "vegur_bold"),
    "oldstyle": ("mfb_oldstyle/MFBOldstyle-Regular.otf", "oldstyle"),
    "oldstyle_bold": ("mfb_oldstyle/MFBOldstyle-Bold.otf", "oldstyle_bold"),
    "oldstyle_italic": ("mfb_oldstyle/MFBOldstyle-Italic.otf", "oldstyle_italic"),
}

HEADER = '''"""{name}: a smooth face, minted by tools/mint_smooth_type.py. DO NOT EDIT.

{file}, CC0. EM = {em} px; coverage 0-255, one hex byte a pixel, row-major.
GLYPHS: char -> (advance, x_offset, y_offset, width, height, hex). The offsets
are from the pen and from the top of the line box (ASCENT above the baseline).
"""
EM = {em}
ASCENT = {ascent}
DESCENT = {descent}
CAP = {cap}
GLYPHS = {{
'''


def mint(path, name):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(path, EM)
    ascent, descent = font.getmetrics()
    cap = font.getbbox("H")
    cap_h = cap[3] - cap[1]
    rows = []
    for ch in CHARS:
        adv = font.getlength(ch)
        box = font.getbbox(ch)                       # relative to the pen, top of line = 0
        w, h = max(0, box[2] - box[0]), max(0, box[3] - box[1])
        if w == 0 or h == 0:
            rows.append((ch, round(adv, 3), 0, 0, 0, 0, ""))
            continue
        im = Image.new("L", (w + 4, h + 4), 0)
        ImageDraw.Draw(im).text((2 - box[0], 2 - box[1]), ch, font=font, fill=255)
        ink = im.getbbox()
        if ink is None:
            rows.append((ch, round(adv, 3), 0, 0, 0, 0, ""))
            continue
        crop = im.crop(ink)
        x_off = box[0] + ink[0] - 2
        y_off = box[1] + ink[1] - 2
        rows.append((ch, round(adv, 3), x_off, y_off, crop.width, crop.height, crop.tobytes().hex()))
    out = HEADER.format(name=name, file=os.path.basename(path), em=EM, ascent=ascent, descent=descent, cap=cap_h)
    for ch, adv, xo, yo, w, h, hx in rows:
        out += f"    {ch!r}: ({adv}, {xo}, {yo}, {w}, {h}, {hx!r}),\n"
    return out + "}\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", required=True, help="the directory holding blue_highway/ and minisystem/")
    ap.add_argument("--face")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                                  "zoo_keeper", "core", "smooth_faces"))
    ap.add_argument("--check", action="store_true", help="exit 1 if a minted module differs from the font")
    a = ap.parse_args(argv)
    names = list(FACES) if a.all or not a.face else [a.face]
    os.makedirs(a.out, exist_ok=True)
    init = os.path.join(a.out, "__init__.py")
    if not os.path.exists(init) and not a.check:
        open(init, "w", encoding="utf-8", newline="\n").write('"""Smooth faces, minted. See tools/mint_smooth_type.py."""\n')
    bad = 0
    for name in names:
        rel, module = FACES[name]
        text = mint(os.path.join(a.fonts, rel), name)
        path = os.path.join(a.out, module + ".py")
        if a.check:
            same = os.path.exists(path) and open(path, encoding="utf-8").read() == text
            print(("ok   " if same else "STALE"), module)
            bad += 0 if same else 1
        else:
            open(path, "w", encoding="utf-8", newline="\n").write(text)
            print("minted", module, len(text) // 1024, "KiB")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
