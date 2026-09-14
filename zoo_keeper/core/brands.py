"""The factory's invented drink brands: one table for every piece of stock.

Zoo 0.87.0, for the vending machine. The walker, with a reference of a modded
Deus Ex machine: "vending machines should glow", and "we want fake products
that are funny and a bit crass ... Delco themed". The theme is delco_1997,
Delaware County, Pennsylvania.

ONE TABLE, so a can on a shelf, a cup on a counter and the machine in the hall
can all sell the same WOODER later without a second list drifting from this
one. Pure Python and no bpy; `core/vending_forms.py` is the first reader.

THE RULES EVERY ROW KEEPS, and `tests/test_vending_machine.py` holds the
mechanical ones:

  * INVENTED. No real trademark and no close imitation of one: not a regional
    brand (Wawa, Tastykake, Yuengling, Herr's, Habbersett), not a team's mark
    or colours, not a national soda's name, script or palette. Two of the
    starting names were changed for that reason and are kept here as the
    record: BLUE ROUTE BLAST -> BLUE ROUTE BACKUP (a blue "Blast" soda is
    one word from a national lemon-lime's flavour line), and WIT WIZ ->
    WIT OR WITOUT (the "Wiz" is a processed-cheese trademark; the ordering
    phrase is not). Palettes avoid the national colas' red-and-white and
    red-white-blue, the green-and-yellow of the citrus sodas, a convenience
    chain's red and yellow, a ginger ale's green and gold, and the city
    football team's midnight green and silver.
  * PG-13: crass, not obscene.
  * LEGIBLE: the slogan is set in the factory's pixel face at the panel's
    texel density, so it has to be short enough to wrap into a few lines.
    `short` is the selection-button label and fits the button cell.

Colours are sRGB hex, the space the art is painted in.
"""
from __future__ import annotations

#: Each row: id, the logo's words (one line each, top to bottom), the drink,
#: the slogan, the button label, and the panel's palette -- background top
#: and bottom, logo ink, logo outline, slogan ink, emblem colour and emblem
#: shape (see `vending_forms.EMBLEMS`), and the cabinet paint.
BRANDS = (
    {"id": "wooder", "logo": ("WOODER",), "drink": "tap water, carbonated",
     "slogan": "Delco Tap Wooder. Now With Bubbles.", "short": "WOODER",
     "bg": ("#1fb8ff", "#0a3fb0"), "ink": "#ffffff", "edge": "#062a73",
     "slogan_ink": "#e8fbff", "emblem": "#8ff0ff", "shape": "bubbles",
     "cabinet": "#123a8c"},
    {"id": "jawn_juice", "logo": ("JAWN", "JUICE"), "drink": "fruit punch",
     "slogan": "It's a Whole Jawn.", "short": "JAWN",
     "bg": ("#ff3fb4", "#ff7a00"), "ink": "#fff23a", "edge": "#6a0048",
     "slogan_ink": "#ffffff", "emblem": "#ffd000", "shape": "burst",
     "cabinet": "#8c1460"},
    {"id": "iggles_tears", "logo": ("IGGLES", "TEARS"), "drink": "salted lemon soda",
     "slogan": "Salty Since '61.", "short": "IGGLES",
     "bg": ("#6f3cff", "#23107a"), "ink": "#bfe6ff", "edge": "#10063d",
     "slogan_ink": "#ffffff", "emblem": "#7fd0ff", "shape": "drop",
     "cabinet": "#2b1670"},
    {"id": "scrapple_soda", "logo": ("SCRAPPLE", "SODA"), "drink": "breakfast soda",
     "slogan": "Everything But the Oink.", "short": "SCRAPPLE",
     "bg": ("#ff9ec4", "#b8325a"), "ink": "#5a2408", "edge": "#fff0f6",
     "slogan_ink": "#3a1204", "emblem": "#ffd9e8", "shape": "disc",
     "cabinet": "#7a2440"},
    {"id": "macdade_mud", "logo": ("MACDADE", "MUD"), "drink": "root beer",
     "slogan": "Tastes Like the Boulevard at 2 AM.", "short": "MUD",
     "bg": ("#ff8a1f", "#4a1a00"), "ink": "#fff0c8", "edge": "#2a0c00",
     "slogan_ink": "#ffe0a0", "emblem": "#ffb000", "shape": "stripes",
     "cabinet": "#4a2410"},
    {"id": "shore_thing", "logo": ("SHORE", "THING"), "drink": "lemonade",
     "slogan": "Down the Shore in a Can. Sand Included.", "short": "SHORE",
     "bg": ("#fff04a", "#29c6e0"), "ink": "#0b4f9c", "edge": "#ffffff",
     "slogan_ink": "#063a70", "emblem": "#ffffff", "shape": "wave",
     "cabinet": "#1a7fa8"},
    {"id": "hoagie_sweat", "logo": ("HOAGIE", "SWEAT"), "drink": "oil and vinegar soda",
     "slogan": "Oil & Vinegar Flavor. Don't Ask.", "short": "HOAGIE",
     "bg": ("#b8d44a", "#3f5a10"), "ink": "#fff6d8", "edge": "#2a3806",
     "slogan_ink": "#fffbe6", "emblem": "#8a3fd0", "shape": "drop",
     "cabinet": "#3f4f18"},
    {"id": "youse_grape", "logo": ("YOUSE", "GRAPE"), "drink": "grape soda",
     "slogan": "Enough for Youse and Your Cousin.", "short": "YOUSE",
     "bg": ("#c040ff", "#3a0070"), "ink": "#c8ff3a", "edge": "#1c0038",
     "slogan_ink": "#f4e0ff", "emblem": "#9aff5a", "shape": "bubbles",
     "cabinet": "#4a1070"},
    {"id": "nanas_basement", "logo": ("NANA'S", "BASEMENT"), "drink": "cream soda",
     "slogan": "Smells Like Mothballs, Tastes Like Love.", "short": "NANA'S",
     "bg": ("#ffd9b0", "#a07ac8"), "ink": "#6a2a6a", "edge": "#fff8ee",
     "slogan_ink": "#3a1440", "emblem": "#ffffff", "shape": "disc",
     "cabinet": "#6a4a80"},
    {"id": "blue_route_backup", "logo": ("BLUE", "ROUTE", "BACKUP"),
     "drink": "blue raspberry soda",
     "slogan": "Traffic in a Can.", "short": "BACKUP",
     "bg": ("#2a6aff", "#001a66"), "ink": "#ff8a00", "edge": "#ffffff",
     "slogan_ink": "#001a66", "emblem": "#ff8a00", "shape": "stripes",
     "cabinet": "#0a2a80"},
    {"id": "chester_gold", "logo": ("CHESTER", "GOLD"), "drink": "ginger ale",
     "slogan": "Filtered Twice (Once).", "short": "CHESTER",
     "bg": ("#ffc23a", "#8a1030"), "ink": "#fff8d0", "edge": "#4a0818",
     "slogan_ink": "#fff0c0", "emblem": "#ffe680", "shape": "burst",
     "cabinet": "#6a0c28"},
    {"id": "wit_or_witout", "logo": ("WIT OR", "WITOUT"), "drink": "cola",
     "slogan": "Cheesesteak Flavored. Yo.", "short": "WITOUT",
     "bg": ("#ffb000", "#e04a00"), "ink": "#1a1a1a", "edge": "#fff4c0",
     "slogan_ink": "#1a0a00", "emblem": "#ffe04a", "shape": "wave",
     "cabinet": "#262626"},
)

BY_ID = {b["id"]: b for b in BRANDS}
IDS = tuple(b["id"] for b in BRANDS)

#: Names a row may not carry, in any case, anywhere in its words. Not a
#: trademark search -- a tripwire for the obvious ones, so a later row added
#: in a hurry trips a test rather than a lawyer.
FORBIDDEN_WORDS = ("wawa", "tasty", "tastykake", "yuengling", "herr", "eagles",
                   "coke", "coca", "pepsi", "dew", "sprite", "whiz", "blast",
                   "dr pepper", "canada dry", "habbersett", "philly")


def hex_rgb(h: str) -> tuple:
    """'#rrggbb' -> (r, g, b) as 0..255 ints."""
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def srgb_to_linear(c: int) -> float:
    """One 0..255 sRGB channel as linear 0..1 (the space a Blender colour
    socket and a glTF factor take)."""
    v = c / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def words(brand: dict) -> str:
    return " ".join(list(brand["logo"]) + [brand["slogan"], brand["short"]])
