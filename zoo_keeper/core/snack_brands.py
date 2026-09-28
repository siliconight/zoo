"""The factory's invented salty snacks: ONE table for every chip bag.

Zoo 1.13.0, for the convenience store's snack gondolas. The walker's store
references (docs/SET_DRESSING_REFERENCES.md, 2026-09-15): "gondola shelving,
four or five shelves of chip bags faced out, end caps stacked with more
chips". The theme is delco_1997, Delaware County, Pennsylvania.

Beside `brands.py` (drinks), `candy_brands.py` and `cigarette_brands.py`, so
a bag on a gondola and a bag on a counter later sell the same DELCO DUST.
Pure Python, no bpy; `core/snack_gondola_forms.py` is the first reader.

THE RULES, held by `tests/test_snack_gondola.py`:

  * INVENTED. No real snack mark and no close imitation -- and this region
    is the potato-chip capital of the country, so the trap is local: the
    Pennsylvania and Philadelphia makers lead `DENY_WORDS`, and the nationals
    follow. No bag borrows a real bag's trade dress; the designs are plain
    bands, windows and stripes in the bag's own colours.
  * PG-13: crass, not obscene. Nothing aimed at kids.
  * LEGIBLE: `short` is set in the m5x7 pixel face across a bag's front at
    the art's texel density, so it is six letters or fewer.

Colours are sRGB hex, the space the art is painted in.
"""
from __future__ import annotations

DESIGNS = ("band", "window", "stripe", "split")

BRANDS = (
    {"id": "scrapple_crisps", "logo": ("SCRAPPLE", "CRISPS"), "flavour": "Pan-Fried Mystery",
     "short": "SCRPL", "body": "#7a3a18", "second": "#f0c070", "ink": "#fff4dc", "design": "window"},
    {"id": "delco_dust", "logo": ("DELCO", "DUST"), "flavour": "Cheese Curls. Gets Everywhere.",
     "short": "DUST", "body": "#f07a10", "second": "#fff0a0", "ink": "#3a1a00", "design": "band"},
    {"id": "jawn_chips", "logo": ("JAWN", "CHIPS"), "flavour": "Sour Cream & Onion",
     "short": "JAWN", "body": "#1e8a4a", "second": "#e8f4e0", "ink": "#ffffff", "design": "split"},
    {"id": "blue_route_bbq", "logo": ("BLUE ROUTE", "BBQ"), "flavour": "Smoked in Traffic",
     "short": "BBQ", "body": "#8a1a1a", "second": "#f0a040", "ink": "#fff0d0", "design": "stripe"},
    {"id": "macdade_munchers", "logo": ("MACDADE", "MUNCHERS"), "flavour": "Pretzel Nuggets",
     "short": "MUNCH", "body": "#3a2a60", "second": "#e8c050", "ink": "#ffffff", "design": "band"},
    {"id": "boardwalk_sticks", "logo": ("BOARDWALK", "STICKS"), "flavour": "Shoestring Potato",
     "short": "STIX", "body": "#1a70a8", "second": "#f8e070", "ink": "#ffffff", "design": "window"},
    {"id": "nanas_rinds", "logo": ("NANA'S", "PORK RINDS"), "flavour": "Don't Tell Your Doctor",
     "short": "RINDS", "body": "#d8c8a0", "second": "#8a3a1a", "ink": "#4a1a08", "design": "split"},
    {"id": "wooder_chips", "logo": ("WOODER", "CHIPS"), "flavour": "Salt & Vinegar",
     "short": "WOODER", "body": "#e8f0f8", "second": "#1a60b0", "ink": "#0a2a60", "design": "stripe"},
    {"id": "shore_salties", "logo": ("SHORE", "SALTIES"), "flavour": "Sea Salt, Allegedly",
     "short": "SALTY", "body": "#f8e8c0", "second": "#2aa0b0", "ink": "#0a4a58", "design": "band"},
    {"id": "yo_cheez", "logo": ("YO", "CHEEZ"), "flavour": "Puffs. Yo.",
     "short": "YO!", "body": "#f8c020", "second": "#c01a1a", "ink": "#6a0808", "design": "window"},
    {"id": "hoagie_crisps", "logo": ("HOAGIE", "CRISPS"), "flavour": "Italian With Everything",
     "short": "HOAGIE", "body": "#c83020", "second": "#f0e8c8", "ink": "#ffffff", "design": "stripe"},
    {"id": "pike_twists", "logo": ("PIKE", "TWISTS"), "flavour": "Hard Pretzel. Harder Road.",
     "short": "TWIST", "body": "#6a4a20", "second": "#f0d890", "ink": "#fff4d8", "design": "split"},
)

BY_ID = {b["id"]: b for b in BRANDS}
IDS = tuple(b["id"] for b in BRANDS)

#: Real marks as WHOLE WORDS. Pennsylvania's own chip and pretzel makers
#: first -- a Delco parody reaches for them before anything national.
DENY_WORDS = ("HERR", "HERRS", "HERR'S", "UTZ", "WISE", "SNYDER", "SNYDERS", "HANOVER", "MARTIN",
              "MARTINS", "MIDDLESWARTH", "GIBBLE", "GIBBLES", "BACHMAN", "TASTYKAKE", "UNIQUE",
              "STURGIS", "LAYS", "LAY'S", "DORITOS", "CHEETOS", "FRITOS", "RUFFLES", "PRINGLES",
              "TOSTITOS", "FUNYUNS", "SUNCHIPS", "SMARTFOOD", "GOLDFISH", "COMBOS", "BUGLES",
              "KETTLE", "ZAPPS", "TGI", "WAWA", "EAGLES", "FLYERS", "PHILLIES", "SIXERS")
#: Real marks ANYWHERE, words run together or not.
DENY_PARTS = ("SUN CHIPS", "OLD DUTCH", "CAPE COD", "CHEEZ-IT", "CHEEZIT", "CHEEZ IT", "DORITO",
              "CHEETO", "FRITO", "FRITO-LAY", "PEPSICO", "HOSTESS", "LANCE", "NABISCO", "KELLOGG",
              "UTZ ", "HERR'")


def hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def words(brand: dict) -> str:
    return " ".join(list(brand["logo"]) + [brand["flavour"], brand["short"]])
