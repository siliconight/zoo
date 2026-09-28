"""The factory's invented candy and gum: ONE table for every wrapper.

Zoo 1.7.0, for the convenience store's service counter -- the candy rack
on its customer face and the impulse gum at the till. The walker's 1990s
photograph of the store's service island (docs/SET_DRESSING_REFERENCES.md,
"The walker's convenience store references"): "the counter front is a
candy rack -- tiered shelves of brightly wrapped bars facing the customer".
The theme is delco_1997, Delaware County, Pennsylvania.

One table beside `brands.py` (drinks) and `cigarette_brands.py` (packs), so
a bar on this rack and a bar in a vending machine's window later sell the
same SCRAPPLE BAR without a second list drifting from this one. Pure Python
and no bpy; `core/service_counter_forms.py` is the first reader.

THE RULES EVERY ROW KEEPS, and `tests/test_service_counter.py` holds the
mechanical ones:

  * INVENTED. No real confectionery mark and no close imitation -- national
    or Philadelphia's own, which is the trap here: the region has a dozen
    real candy makers and their names are exactly the words a Delco parody
    reaches for first. `DENY_WORDS` (whole words) and `DENY_PARTS` (anywhere)
    hold them. The wrapper designs are plain bands and stripes in the bar's
    own colours; none borrows a real wrapper's trade dress.
  * PG-13: crass, not obscene. Nothing aimed at kids.
  * LEGIBLE: `short` is set in the factory's pixel face on a wrapper about
    50 px wide at the rack's texel density, so it is one word of six letters
    or fewer.

Colours are sRGB hex, the space the art is painted in.
"""
from __future__ import annotations

#: The wrapper designs `service_counter_forms._bar` paints. Deliberately plain.
DESIGNS = ("band", "stripe", "split", "diag")

#: id, the wrapper's words (one line each), the slogan, the short name on
#: the wrapper, the wrapper's body, second colour and ink, and its design.
#: ``kind`` is "bar" for the rack tiers and "gum" for the impulse rack.
BRANDS = (
    {"id": "scrapple_bar", "logo": ("SCRAPPLE", "BAR"), "slogan": "Meat. Chocolate. Both.",
     "short": "SCRPL", "kind": "bar", "body": "#6a3a1a", "second": "#e8c890", "ink": "#f4ead8",
     "design": "band"},
    # JAWN CHEWS was the first name and lasted one test run: "Chews" is the
    # Philadelphia peanut bar's word and sits in DENY_WORDS below.
    {"id": "jawn_bar", "logo": ("JAWN", "BAR"), "slogan": "A Whole Jawn. In a Bar.",
     "short": "JAWN", "kind": "bar", "body": "#b83a1a", "second": "#f2e24a", "ink": "#fff8e0",
     "design": "split"},
    # DELCO CRUNCH lasted one test run too: "Crunch" is a national bar's name.
    {"id": "delco_crisp", "logo": ("DELCO", "CRISP"), "slogan": "Crispier Than the Blue Route at Five.",
     "short": "CRISP", "kind": "bar", "body": "#2a5cb8", "second": "#e6ecf8", "ink": "#ffffff",
     "design": "stripe"},
    {"id": "boardwalk_taffy", "logo": ("BOARDWALK", "TAFFY"), "slogan": "Pulls Your Fillings Out Since '52.",
     "short": "TAFFY", "kind": "bar", "body": "#f0a8c8", "second": "#8ae0e8", "ink": "#4a1440",
     "design": "diag"},
    {"id": "yo_nuts", "logo": ("YO", "NUTS"), "slogan": "Peanuts. Chocolate. Yo.",
     "short": "YO", "kind": "bar", "body": "#3a2210", "second": "#e8a830", "ink": "#e8a830",
     "design": "band"},
    {"id": "pretzel_buttz", "logo": ("PRETZEL", "BUTTZ"), "slogan": "Salted Where It Counts.",
     "short": "BUTTZ", "kind": "bar", "body": "#c8842a", "second": "#4a2a10", "ink": "#fff4dc",
     "design": "stripe"},
    {"id": "nanas_caramels", "logo": ("NANA'S", "CARAMELS"), "slogan": "Like Sunday in Her Kitchen. Sort Of.",
     "short": "NANA", "kind": "bar", "body": "#e8d8b8", "second": "#8a4a1a", "ink": "#4a2a10",
     "design": "split"},
    {"id": "mummers_mints", "logo": ("MUMMER'S", "MINTS"), "slogan": "Strut Your Breath.",
     "short": "MUMRS", "kind": "bar", "body": "#1e7a4a", "second": "#f4f0e6", "ink": "#ffffff",
     "design": "diag"},
    {"id": "macdade_mint_gum", "logo": ("MACDADE", "MINT"), "slogan": "Chew It in Traffic.",
     "short": "MACD", "kind": "gum", "body": "#2aa86a", "second": "#e6f4ea", "ink": "#0a3a20",
     "design": "band"},
    {"id": "blue_route_bubble", "logo": ("BLUE ROUTE", "BUBBLE"), "slogan": "Blows Up at the Merge.",
     "short": "BUBL", "kind": "gum", "body": "#ff5ab4", "second": "#ffffff", "ink": "#6a0048",
     "design": "stripe"},
    {"id": "pike_cinnamon", "logo": ("BALTIMORE PIKE", "CINNAMON"), "slogan": "Hot. Like Traffic on a Friday.",
     "short": "PIKE", "kind": "gum", "body": "#c8202a", "second": "#f4c040", "ink": "#fff4dc",
     "design": "split"},
)

BY_ID = {b["id"]: b for b in BRANDS}
IDS = tuple(b["id"] for b in BRANDS)
BAR_IDS = tuple(b["id"] for b in BRANDS if b["kind"] == "bar")
GUM_IDS = tuple(b["id"] for b in BRANDS if b["kind"] == "gum")

#: Real marks as WHOLE WORDS (upper case). The Philadelphia makers are the
#: ones a Delco parody would reach for, so they lead.
DENY_WORDS = ("GOLDENBERG", "GOLDENBERGS", "CHEWS", "MALLO", "CLARK", "ZAGNUT", "PEEPS",
              "TASTYKAKE", "KRIMPET", "JUNIOR", "ASHER", "ASHERS", "WILBUR",
              "SNICKERS", "TWIX", "SKITTLES", "STARBURST", "HERSHEY", "HERSHEYS", "REESE",
              "REESES", "KITKAT", "ROLO", "MOUNDS", "YORK", "TWIZZLERS", "CRUNCH",
              "BUTTERFINGER", "PAYDAY", "MUSKETEERS", "MILKY", "DOTS", "JUJYFRUITS",
              "TRIDENT", "DENTYNE", "BUBBLICIOUS", "BAZOOKA", "CHICLETS", "WRIGLEY",
              "WRIGLEYS", "ORBIT", "EXTRA", "ECLIPSE", "WAWA", "EAGLES", "FLYERS", "PHILLIES",
              "SIXERS")
#: Real marks ANYWHERE in a name, words run together or not.
DENY_PARTS = ("PEANUT CHEW", "PEANUTCHEW", "MALLO CUP", "MALLOCUP", "KIT KAT", "KITKAT",
              "MILKY WAY", "MILKYWAY", "M&M", "BABY RUTH", "BABYRUTH", "ALMOND JOY", "ALMONDJOY",
              "SWEDISH FISH", "SWEDISHFISH", "MIKE AND IKE", "MIKE & IKE", "HOT TAMALE",
              "GOOD & PLENTY", "GOOD AND PLENTY", "JUICY FRUIT", "JUICYFRUIT", "BIG RED",
              "BIGRED", "HUBBA BUBBA", "HUBBABUBBA", "WHATCHAMACALLIT", "THREE MUSKETEER",
              "3 MUSKETEER", "JUST BORN", "JUSTBORN", "TOOTSIE", "NESTLE", "CADBURY", "MARS",
              "WONKA", "HARIBO")

#: What the rack says that is not a brand.
SHELF_TALKER = "2 FOR $1"


def hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def words(brand: dict) -> str:
    return " ".join(list(brand["logo"]) + [brand["slogan"], brand["short"]])
