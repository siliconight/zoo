"""What the neon over a 1997 Delaware County club says: ONE table, here.

Every name is INVENTED -- funny, a bit crass (PG-13) and local: the pikes,
the boroughs, the talk (jawn, wooder, youse, hon, down the shore). Place
names are places, not businesses. None is, or is meant to evoke, a real
club, bar or trademark; `DENYLIST` below is the guard a test holds every
name against. It is a guard and not a proof -- it lists the regional and
national club names and the local brands a writer would reach for without
thinking, and nobody has searched a business register for the rest.

`neon_sign`'s ``variant`` indexes this table exactly (the genome's
``module_variants`` is its length, and a test holds that), so Deli Counter
choosing a variant is choosing a name, and a level's two signs differ when
their variants do.

The glyph set is `neon_forms.FONT_5X7`'s: A-Z, 0-9, space and ' ! - . : / +.
A test spells every name from it.
"""
from __future__ import annotations

NAMES = (
    "THE JAWN ROOM",
    "MACDADE MAGIC",
    "LIVE GIRLS",
    "BOTTOMS UP ON BALTIMORE PIKE",
    "NANA'S NOT HERE",
    "YOUSE BEHAVE",
    "MOM THINKS I'M AT BINGO",
    "CHEEKS ON CHESTER PIKE",
    "THE WOODER HOLE",
    "SHAKE YOUR SCRAPPLE",
    "ROUTE 291 REVUE",
    "DOWN THE SHORE LOUNGE",
    "CASH ONLY CABARET",
    "NO TOUCHIN' HON",
    "THE MARCUS HOOK-UP",
    "GLENOLDEN GLOW",
    "DARBY DOLLS",
    "THE PRETZEL TWIST",
    "OPEN TIL 2 AM",
    "DOLLAR DRAFTS - LIVE DANCERS",
    "FOLSOM FOXES",
    "GO-GO ON 291",
    "TIPS APPRECIATED",
    "YO! SHOWGIRLS",
)

#: Real names this table must never contain (upper case, matched as
#: substrings of a name with its apostrophes kept). The local comparison the
#: walker gave for layout is first on the list.
DENYLIST = (
    "LOU TURK", "TURK'S", "CHRISTINE", "CHEERLEADERS", "DELILAH", "RISQUE",
    "CRAZY HORSE", "OASIS", "PENTHOUSE", "SCORES", "RICK'S", "DEJA VU",
    "HUSTLER", "SPEARMINT", "PLATINUM PLUS", "SHOW AND TELL", "DIAMOND",
    "VIVID", "GOLD CLUB", "TRIANGLE", "PARADISE", "SILVER SLIPPER",
    # local brands and teams a writer reaches for
    "WAWA", "TASTYKAKE", "EAGLES", "FLYERS", "PHILLIES", "SIXERS", "GRITTY",
    "PAT'S", "GENO'S", "YUENGLING", "RITA'S", "ACME",
)

#: (text tube, border tube) linear RGB. Neon's own colours: the neon red
#: and the pinks, argon blue, the green and the amber.
PALETTES = (
    ((1.00, 0.06, 0.32), (0.10, 0.28, 1.00)),     # hot pink on blue
    ((1.00, 0.05, 0.03), (1.00, 0.42, 0.04)),     # red on amber
    ((0.10, 0.30, 1.00), (1.00, 0.06, 0.32)),     # blue on pink
    ((0.12, 1.00, 0.26), (1.00, 0.06, 0.32)),     # green on pink
    ((1.00, 0.42, 0.04), (1.00, 0.05, 0.03)),     # amber on red
    ((0.62, 0.10, 1.00), (0.10, 0.85, 0.90)),     # violet on cyan
)
#: glTF emissive strength of the tubes. REFUTED FIRST at 4.0: in the Godot
#: walk's dark basement every channel clipped and the pink-and-blue sign read
#: as white
NEON_STRENGTH = 1.2


def name_for(variant):
    return NAMES[int(variant) % len(NAMES)]


def palette_for(variant):
    """Colours step through the palettes at a different rate from the names,
    so neighbouring variants rarely repeat both."""
    return PALETTES[(int(variant) * 5) % len(PALETTES)]
