"""The factory's invented cigarette brands: ONE table for every pack.

Zoo 0.91.0, for the pull-knob cigarette machine. The walker, 2026-09-15:
"we need retro cigarettes' machines in the strip club. (Maybe we'll put em in
other buildings too, it was the 1990s where smoking in public was still
legal in PA)". The theme is delco_1997, Delaware County, Pennsylvania.

One table beside `brands.py` (the drinks), so a pack on a bar and the
machine by the door can sell the same DELCO REDS later without a second list
drifting from this one. Pure Python and no bpy; `core/cigarette_forms.py` is
the first reader.

THE RULES EVERY ROW KEEPS, and `tests/test_cigarette_machine.py` holds the
mechanical ones:

  * INVENTED. No real cigarette mark and no close imitation of one -- in the
    name, and in the pack. Names: none of `DENY_WORDS` (whole words) or
    `DENY_PARTS` (anywhere). Packs: every design is one of `DESIGNS`, and
    none of them is a real pack's trade dress -- no roof-shaped chevron (the
    best-selling red pack's), no spinnaker, no animal, no crest with a
    lion, no "gold pack with a thin frame". The colours are the categories'
    (red for full flavour, green for menthol, blue and silver for lights,
    gold for a 100) and nothing else of any mark.
  * ONE NAME CHANGED FOR THAT REASON, kept here as the record: CHESTER 100s,
    offered with the request, became MARCUS HOOK 100s -- Chester is a Delco
    city, but "Chester" is the first seven letters of a national brand still
    sold in 1997, and a 100 in a red-and-white pack would read as that one.
  * PG-13: crass, not obscene. Nothing aimed at kids -- no cartoon, no candy.
  * LEGIBLE: `short` is set in the factory's pixel face on a pack 55 mm wide
    at the display's texel density; `logo` and `slogan` fit the header.

Colours are sRGB hex, the space the art is painted in.
"""
from __future__ import annotations

#: The pack designs `cigarette_forms._pack` paints. Deliberately plain.
DESIGNS = ("band", "split", "stripe", "disc", "diamond", "bars")

#: id, the logo's words (one line each), the slogan, the pack's short name,
#: the pack's body, second colour and ink, its design, and the header ad's
#: two background colours.
BRANDS = (
    {"id": "delco_reds", "logo": ("DELCO", "REDS"), "slogan": "Smoke 'Em If Youse Got 'Em.",
     "short": "REDS", "pack": "#c8202a", "second": "#f4f0e6", "ink": "#1a1a1a",
     "design": "split", "bg": ("#7a0e14", "#2a0406")},
    {"id": "macdade_menthol", "logo": ("MACDADE", "MENTHOL"), "slogan": "Cool as the Boulevard at Last Call.",
     "short": "MACD", "pack": "#1e7a4a", "second": "#e6f4ea", "ink": "#ffffff",
     "design": "band", "bg": ("#0e4a2c", "#041a10")},
    {"id": "blue_route_lights", "logo": ("BLUE ROUTE", "LIGHTS"), "slogan": "For the Long Wait at the Merge.",
     "short": "LITE", "pack": "#2a5cb8", "second": "#d8e2f4", "ink": "#ffffff",
     "design": "stripe", "bg": ("#163a7a", "#060e24")},
    {"id": "marcus_hook_100s", "logo": ("MARCUS HOOK", "100s"), "slogan": "Refinery Fresh. Every Pack.",
     "short": "HOOK", "pack": "#d8a832", "second": "#3a2a10", "ink": "#2a1a06",
     "design": "bars", "bg": ("#8a6414", "#241802")},
    {"id": "nanas_slims", "logo": ("NANA'S", "SLIMS"), "slogan": "She Quit. Twice.",
     "short": "NANA", "pack": "#e8d8e8", "second": "#8a3a7a", "ink": "#4a1440",
     "design": "disc", "bg": ("#6a2a5a", "#1e0818")},
    {"id": "jawn_kings", "logo": ("JAWN", "KINGS"), "slogan": "The Whole Jawn, King Size.",
     "short": "JAWN", "pack": "#f2f2ec", "second": "#b83a1a", "ink": "#b83a1a",
     "design": "diamond", "bg": ("#8a2a10", "#200804")},
    {"id": "wooder_filters", "logo": ("WOODER", "FILTERS"), "slogan": "Filtered Through the Delaware.",
     "short": "WDR", "pack": "#9ab4c8", "second": "#1a3a5a", "ink": "#0a1a2a",
     "design": "band", "bg": ("#2a4a6a", "#0a1420")},
    {"id": "boulevard_butts", "logo": ("BOULEVARD", "BUTTS"), "slogan": "Smoke the Whole Boulevard.",
     "short": "BLVD", "pack": "#3a3a3e", "second": "#e2c24a", "ink": "#e2c24a",
     "design": "bars", "bg": ("#3a3a3e", "#0e0e10")},
    {"id": "down_the_shore_120s", "logo": ("DOWN THE", "SHORE 120s"), "slogan": "Tastes Like the Boardwalk. Sort Of.",
     "short": "120s", "pack": "#f0e4b8", "second": "#1a8aa8", "ink": "#0a4a60",
     "design": "stripe", "bg": ("#1a6a88", "#062028")},
    {"id": "havertown_haze", "logo": ("HAVERTOWN", "HAZE"), "slogan": "Low Tar. High Hopes.",
     "short": "HAZE", "pack": "#c8c8c0", "second": "#5a5a6a", "ink": "#2a2a34",
     "design": "disc", "bg": ("#4a4a58", "#121218")},
    {"id": "darby_darks", "logo": ("DARBY", "DARKS"), "slogan": "No Filter. No Problem.",
     "short": "DARK", "pack": "#5a2a14", "second": "#e8c890", "ink": "#e8c890",
     "design": "split", "bg": ("#4a200e", "#140804")},
    {"id": "pike_milds", "logo": ("BALTIMORE PIKE", "MILDS"), "slogan": "Mild. Like Traffic on a Sunday.",
     "short": "PIKE", "pack": "#e8e8e0", "second": "#2a7a6a", "ink": "#1a4a40",
     "design": "diamond", "bg": ("#1e5a4e", "#081a16")},
)

BY_ID = {b["id"]: b for b in BRANDS}
IDS = tuple(b["id"] for b in BRANDS)

#: Real marks as WHOLE WORDS (upper case): short ones that are also English
#: words, matched as tokens so "MORE" catches a pack called MORE and not
#: "MOREOVER".
DENY_WORDS = ("KOOL", "SALEM", "CAMEL", "MERIT", "MORE", "EVE", "TRUE", "KENT", "BASIC",
              "DORAL", "MISTY", "CAPRI", "NOW", "VANTAGE", "RALEIGH", "BELAIR", "MONARCH",
              "GPC", "PYRAMID", "SENECA", "MAVERICK", "CAMBRIDGE", "WINSTON", "NEWPORT",
              "LUCKY", "STRIKE", "VICEROY", "CARLTON", "PARLIAMENT", "MARLBORO", "CHESTER",
              "WAWA", "EAGLES", "FLYERS", "PHILLIES", "SIXERS")
#: Real marks ANYWHERE in a name, words run together or not.
DENY_PARTS = ("MARLB", "WINST", "NEWPO", "PARLIAM", "VIRGINIA", "BENSON", "HEDGES",
              "PALLMALL", "PALL MALL", "LUCKYSTR", "CHESTERF", "OLDGOLD", "OLD GOLD",
              "AMERICANSPIRIT", "AMERICAN SPIRIT", "DUNHILL", "ROTHMAN", "DJARUM", "SWISHER",
              "BLACK & MILD", "PHILIP MORRIS", "REYNOLDS", "LORILLARD", "LIGGETT",
              "WILLIAMSON", "JOE CAMEL", "FLAVOR COUNTRY", "L&M", "TASTYKAKE", "YUENGLING")
#: The designs no pack may use: the trade dress of real packs.
DENY_DESIGNS = ("chevron", "roof", "spinnaker", "camel", "crest", "lion", "eagle", "frame_gold")

#: What the machine says that is not a brand: the law on the strips, the
#: price card, the warning sticker and the split form's panel. The warning
#: is the Surgeon General's own 1985 text (public law, not a mark).
MINORS = "SALES OF CIGARETTES TO MINORS ARE FORBIDDEN BY LAW"
MINORS_SHORT = "SALES TO MINORS FORBIDDEN BY LAW"
PRICE = ("$3.50", "QUARTERS ONLY")
WARNING = ("SURGEON GENERAL'S WARNING:", "SMOKING CAUSES LUNG CANCER,", "HEART DISEASE, EMPHYSEMA.")
PANEL_WORD = "CIGARETTES"


def hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def words(brand: dict) -> str:
    return " ".join(list(brand["logo"]) + [brand["slogan"], brand["short"]])
