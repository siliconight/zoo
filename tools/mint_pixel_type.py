"""Mint Zoo's pixel faces from Pixelcoat's vendored typefaces.

    python tools/mint_pixel_type.py [--face NAME | --all] [--pixelcoat DIR] [--check]

THE FACTORY'S LETTERING IS PIXEL OPERATOR, CC0, vendored by Pixelcoat at
`assets/fonts/pixel_operator/` and set by `pixelcoat/core/signage.py` for
every shop sign. Zoo lettering that is a TEXTURE (0.87.0: a vending machine's
backlit panel) is set in the same faces, so a machine's brand and the shop
sign over the door are one typeface.

WHY A TABLE AND NOT THE TTF. Zoo builds inside Blender, whose Python carries
numpy and no PIL, and a TrueType rasteriser is not something to write twice.
Pixel Operator is drawn on a 16 px grid: set at 16 px every glyph is a pure
bitmap (0 or 255, nothing between), and at 32 px it is exactly the 16 px
bitmap doubled -- both measured with PIL before this was written, on
"IGGLES TEARS", 0 of 64,000 pixels different. The face has no kerning: a
string rendered by PIL equals its glyphs composed at their advances (on
"Tastes Like the Boulevard at 2 AM.", every pixel). So the 16 px bitmaps and
advances ARE the typeface at every multiple of its grid, and a table of them
loses nothing.

MORE THAN ONE FACE (Zoo 1.10.0, docs/proposals/CC0_FONTS.md steps A and B).
`FACES` names each face the factory mints: its file, the pixel grid it is
drawn on, and the module it mints to. `bold` is the face every recipe has
used since 0.87.0 and still mints to `pixel_type_glyphs.py`, byte for byte as
before; the rest mint to `zoo_keeper/core/pixel_faces/<name>.py` and are
reached through `pixel_type`'s ``face=`` argument.

A GLYPH THE FACE DOES NOT HAVE IS REFUSED, not drawn. PIL rasterises a
character missing from a font as the font's `.notdef` box, and until 1.10.0
nothing here noticed: a face without the cent sign would have minted a box
for it and passed every other check. The mint now reads the font's own
character map (`cmap_codepoints`, the TrueType ``cmap`` table read directly,
formats 4 and 12) and exits naming every character the face lacks. A face
that is meant to lack some declares a narrower ``charset`` in `FACES`.

`--check` re-renders from the TTF and exits 1 if a table differs, which is
also what `tests/test_vending_machine.py` and `tests/test_pixel_faces.py` do
when Pixelcoat is present. Run with PYTHONDONTWRITEBYTECODE=1: this imports
Pixelcoat read-only.
"""
from __future__ import annotations

import argparse
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZOO = os.path.dirname(HERE)
CORE = os.path.join(ZOO, "zoo_keeper", "core")
OUT = os.path.join(CORE, "pixel_type_glyphs.py")
#: Printable ASCII and the cent sign a 1997 price display needs.
CHARSET = "".join(chr(c) for c in range(32, 127)) + "¢"
PX = 16

#: name -> (the file under Pixelcoat's `assets/fonts/`, family folder first;
#: the px grid it is drawn on; the module it mints to under zoo_keeper/core;
#: its label). Each family folder carries its own LICENSE.txt and README.md.
FACES = {
    "bold": ("pixel_operator/PixelOperator-Bold.ttf", 16, "pixel_type_glyphs", "Pixel Operator Bold"),
    "regular": ("pixel_operator/PixelOperator.ttf", 16, "pixel_faces/regular", "Pixel Operator"),
    "small_caps": ("pixel_operator/PixelOperatorSC.ttf", 16, "pixel_faces/small_caps",
                   "Pixel Operator SC"),
    "small_caps_bold": ("pixel_operator/PixelOperatorSC-Bold.ttf", 16, "pixel_faces/small_caps_bold",
                        "Pixel Operator SC Bold"),
    "mono": ("pixel_operator/PixelOperatorMono.ttf", 16, "pixel_faces/mono", "Pixel Operator Mono"),
    "small": ("pixel_operator/PixelOperator8.ttf", 8, "pixel_faces/small", "Pixel Operator 8"),
    # Pixelcoat 0.53.0. The pages give m5x7's size as 16 and monogram's not
    # at all; both were MEASURED on/off, whole-advance and kern-free at 16 px
    # and at no other size from 6 to 31.
    "m5x7": ("m5x7/m5x7.ttf", 16, "pixel_faces/m5x7", "m5x7"),
    "monogram": ("monogram/monogram-extended.ttf", 16, "pixel_faces/monogram", "monogram"),
    "monogram_italic": ("monogram/monogram-extended-italic.ttf", 16, "pixel_faces/monogram_italic",
                        "monogram italic"),
}
#: family folder -> (the family's name, its designer), for the minted header.
FAMILIES = {"pixel_operator": ("Pixel Operator", "Jayvee Enaguas"),
            "m5x7": ("m5x7", "Daniel Linssen"),
            "monogram": ("monogram", "datagoblin")}


def default_pixelcoat():
    env = os.environ.get("PIXELCOAT_DIR")
    if env:
        return env
    return os.path.join(os.path.dirname(ZOO), "pixelcoat")


def cmap_codepoints(path):
    """Every code point the TrueType/OpenType file at ``path`` maps to a
    glyph, read from its ``cmap`` table: the Unicode subtable (3,10) or
    (0,4) format 12 if present, else (3,1) or (0,3) format 4. Raises
    ValueError on a file it cannot read -- a check that cannot find the
    table has learned nothing and must say so."""
    data = open(path, "rb").read()
    num_tables = struct.unpack(">H", data[4:6])[0]
    cmap_off = None
    for i in range(num_tables):
        tag, _chk, off, _ln = struct.unpack(">4sIII", data[12 + 16 * i:28 + 16 * i])
        if tag == b"cmap":
            cmap_off = off
    if cmap_off is None:
        raise ValueError(f"{path}: no cmap table")
    n_sub = struct.unpack(">H", data[cmap_off + 2:cmap_off + 4])[0]
    subs = {}
    for i in range(n_sub):
        pid, eid, off = struct.unpack(">HHI", data[cmap_off + 4 + 8 * i:cmap_off + 12 + 8 * i])
        fmt = struct.unpack(">H", data[cmap_off + off:cmap_off + off + 2])[0]
        subs[(pid, eid, fmt)] = cmap_off + off
    for key in ((3, 10, 12), (0, 4, 12), (0, 6, 12), (3, 1, 4), (0, 3, 4), (0, 1, 4), (0, 0, 4)):
        if key in subs:
            base = subs[key]
            return _format12(data, base) if key[2] == 12 else _format4(data, base)
    raise ValueError(f"{path}: no Unicode cmap subtable of format 4 or 12 ({sorted(subs)})")


def _format4(data, base):
    seg2 = struct.unpack(">H", data[base + 6:base + 8])[0]
    n = seg2 // 2
    ends = struct.unpack(f">{n}H", data[base + 14:base + 14 + seg2])
    starts_at = base + 16 + seg2
    starts = struct.unpack(f">{n}H", data[starts_at:starts_at + seg2])
    deltas = struct.unpack(f">{n}h", data[starts_at + seg2:starts_at + 2 * seg2])
    ro_at = starts_at + 2 * seg2
    offsets = struct.unpack(f">{n}H", data[ro_at:ro_at + seg2])
    out = set()
    for i in range(n):
        for c in range(starts[i], ends[i] + 1):
            if c == 0xFFFF:
                continue
            if offsets[i] == 0:
                gid = (c + deltas[i]) & 0xFFFF
            else:
                at = ro_at + 2 * i + offsets[i] + 2 * (c - starts[i])
                gid = struct.unpack(">H", data[at:at + 2])[0]
                if gid:
                    gid = (gid + deltas[i]) & 0xFFFF
            if gid:
                out.add(c)
    return out


def _format12(data, base):
    n = struct.unpack(">I", data[base + 12:base + 16])[0]
    out = set()
    for i in range(n):
        s, e, g = struct.unpack(">III", data[base + 16 + 12 * i:base + 28 + 12 * i])
        for k, c in enumerate(range(s, e + 1)):
            if g + k:
                out.add(c)
    return out


def face_path(pixelcoat_dir, face):
    sys.dont_write_bytecode = True
    sys.path.insert(0, pixelcoat_dir)
    from pixelcoat.core import signage  # noqa: E402
    # signage.FONT_DIR is Pixel Operator's folder; its parent holds every family
    return os.path.join(os.path.dirname(signage.FONT_DIR), *FACES[face][0].split("/"))


def render_table(pixelcoat_dir, weight="bold", face=None, charset=None):
    """The face's bitmaps and advances at its grid. ``weight`` is the old
    spelling (0.87.0 minted `bold` only) and is kept so a caller of that
    age gets the table it always did; ``face`` names any of `FACES`."""
    from PIL import Image, ImageDraw, ImageFont  # noqa: E402
    face = face or weight
    if face not in FACES:
        raise SystemExit(f"no face {face!r}; the factory's faces are {sorted(FACES)}")
    fname, px, _mod, label = FACES[face]
    path = face_path(pixelcoat_dir, face)
    charset = charset if charset is not None else CHARSET
    have = cmap_codepoints(path)
    missing = [ch for ch in charset if ord(ch) not in have]
    if missing:
        raise SystemExit(f"{face} ({fname}): {len(missing)} character(s) not in the font's "
                         f"character map: {''.join(missing)!r} -- PIL would draw the .notdef "
                         f"box for each and the table would carry it")
    font = ImageFont.truetype(path, px)
    top, bottom = 0, 0
    for ch in charset:
        b = font.getbbox(ch, anchor="ls")
        top, bottom = min(top, b[1]), max(bottom, b[3])
    glyphs = {}
    for ch in charset:
        adv = font.getlength(ch)
        if adv != int(adv):
            raise SystemExit(f"{face}: {ch!r}: advance {adv} is not whole pixels")
        adv = int(adv)
        w = max(adv, font.getbbox(ch, anchor="ls")[2])
        img = Image.new("L", (w, bottom - top), 0)
        ImageDraw.Draw(img).text((0, -top), ch, fill=255, font=font, anchor="ls")
        pxs = img.load()
        rows = []
        for y in range(bottom - top):
            vals = [pxs[x, y] for x in range(w)]
            if any(v not in (0, 255) for v in vals):
                raise SystemExit(f"{face}: {ch!r}: antialiased at {px} px -- not a grid face")
            rows.append("".join("#" if v else "." for v in vals))
        glyphs[ch] = (adv, tuple(rows))
    return {"ascent": -top, "descent": bottom, "px": px, "face": face, "label": label,
            "family": fname.split("/")[0], "font": os.path.basename(path), "glyphs": glyphs}


def emit(table):
    label = table.get("label", "Pixel Operator Bold")
    folder = table.get("family", "pixel_operator")
    family, designer = FAMILIES[folder]
    lines = [
        f'"""{label} at {table["px"]} px, as bitmaps. GENERATED by',
        "tools/mint_pixel_type.py from Pixelcoat's vendored TTF -- do not edit;",
        f"re-mint. {family} by {designer}, CC0 1.0 (see Pixelcoat's",
        f'assets/fonts/{folder}/README.md)."""',
        "",
        f"FONT = {table['font']!r}",
        f"PX = {table['px']}",
        "#: rows above the baseline (row ``ASCENT`` is the first below it)",
        f"ASCENT = {table['ascent']}",
        f"DESCENT = {table['descent']}",
        "#: char -> (advance px, rows top to bottom, '#' ink)",
        "GLYPHS = {",
    ]
    for ch, (adv, rows) in table["glyphs"].items():
        lines.append(f"    {ch!r}: ({adv}, (")
        for r in rows:
            lines.append(f"        {r!r},")
        lines.append("    )),")
    lines.append("}")
    return "\n".join(lines) + "\n"


def out_path(face):
    return os.path.join(CORE, *FACES[face][2].split("/")) + ".py"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixelcoat", default=default_pixelcoat())
    ap.add_argument("--face", default="bold", choices=sorted(FACES))
    ap.add_argument("--all", action="store_true", help="every face in FACES")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    faces = sorted(FACES) if a.all else [a.face]
    bad = 0
    for face in faces:
        text = emit(render_table(a.pixelcoat, face=face))
        out = out_path(face)
        if a.check:
            have = open(out, encoding="utf-8").read() if os.path.exists(out) else ""
            ok = have == text
            bad += not ok
            print(f"{face:16s} {os.path.relpath(out, ZOO)}", "matches" if ok else "DIFFERS",
                  "the TTF at", a.pixelcoat)
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("wrote", os.path.relpath(out, ZOO), len(text), "bytes")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
