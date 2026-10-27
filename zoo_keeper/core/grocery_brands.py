"""The factory's invented groceries: ONE table for a supermarket's shelves.

Zoo 1.133.0, for `snack_gondola`'s `grocery` form. The walker's grocery comps
(the factory's docs/reference/GROCERY_STORE_COMPS.md, 2026-10-26): "shiny
floor, bright lights, isles, glowing freezer section, stacked high" -- and a
supermarket whose aisles were stocked with the convenience store's chips
read as a big convenience store, not a grocer. The theme is delco_1997,
Delaware County, Pennsylvania.

A SHELF SELLS WHAT ITS SIGN SAYS. The aisle markers (`aisle_sign` form
`grocery`) print two categories a lane from `card_brands.GROCERY_AISLE_SAYS`;
`CATEGORIES` stocks every one of those names, so a gondola face told
"CANNED VEG" sells cans of vegetables under the marker that says so. A
category is a PACK -- the shape its products come in (`snack_gondola_forms.
GROCERY_PACKS`) -- and its products. Three categories are other tables'
products, so the store and the corner shop sell the same thing: CHIPS are
`snack_brands`' bags, CANDY `candy_brands`', SODA the vending machine's
drinks (`brands`) in two-litre bottles.

THE RULES, held by `tests/test_grocery_gondola.py`:

  * INVENTED. No real grocery mark and no close imitation. The cereal and
    soup makers, the canned-goods, pasta and household brands, and the
    region's supermarket chains are `DENY_WORDS` and `DENY_PARTS`. A
    product's own word is its kind (WHEAT, PEAS, BLEACH) or an invented
    name; no box borrows a real box's trade dress.
  * PG-13: crass, not obscene. Nothing aimed at kids, cereal included.
  * LEGIBLE: `short` is set in the m5x7 pixel face across a product's front
    at the art's texel density: six letters (`SHORT_MAX`).

Colours are sRGB hex, the space the art is painted in.
"""
from __future__ import annotations

#: The pasta boxes' house mark, printed over the shape on every box: the
#: same grandmother whose gravy is in the jars.
PASTA_MARK = "NONNA"


def _p(cat, short, body, second, ink, says=""):
    return {"id": (cat + "_" + short).lower().replace(" ", "_").replace("&", "and").replace("'", "")
            .replace("!", "").replace("?", ""),
            "category": cat, "short": short, "body": body, "second": second, "ink": ink, "says": says}


#: category (as the aisle marker prints it) -> (pack, products). The products
#: of CHIPS, CANDY and SODA are other tables' (see the module's docstring).
CATEGORIES = {
    "BREAD": ("loaf", (
        _p("BREAD", "WHITE", "#f4f0e6", "#c02a2a", "#1a3a8a", "Squishes Flat. Like Ma's."),
        _p("BREAD", "WHEAT", "#c89a5a", "#f0e0b8", "#4a2a08"),
        _p("BREAD", "RYE", "#8a6a3a", "#e8d8b0", "#fff4dc"),
        _p("BREAD", "ROLLS", "#f0e8d0", "#2a7a3a", "#1a4a1a", "Hoagie Rolls. Day Old. Still Good."))),
    "PEANUT BUTTER": ("jar", (
        _p("PEANUT BUTTER", "SMOOTH", "#c0782a", "#f4e0b0", "#ffffff"),
        _p("PEANUT BUTTER", "CHUNKY", "#8a4a1a", "#f0c070", "#fff0d0"),
        _p("PEANUT BUTTER", "GRAPE", "#6a2a8a", "#c08a40", "#ffffff", "PB&J In One Jar. You're Welcome."))),
    "CEREAL": ("cereal", (
        _p("CEREAL", "HOOPS", "#e86a1a", "#ffd860", "#ffffff", "Hangover Hoops. Fortified With Regret."),
        _p("CEREAL", "YOUZ", "#c02a6a", "#ffe0f0", "#ffffff", "Sugar Youz. For All Youz."),
        _p("CEREAL", "BRAN", "#8a5a2a", "#f0e0b0", "#fff8e8", "Boardwalk Bran. Keeps You Regular."),
        _p("CEREAL", "JAWNOS", "#2a7a5a", "#f0d890", "#ffffff", "Jawn-O's. Toasted Oat Jawns."),
        _p("CEREAL", "PUFFS", "#5a2a10", "#f0b070", "#ffe8c0", "Chester Pike Puffs. Cocoa. Allegedly."),
        _p("CEREAL", "FLAKES", "#3a5ab0", "#ffffff", "#ffffff", "Kennett Flakes. Not Mushrooms."))),
    "COFFEE & TEA": ("canister", (
        _p("COFFEE & TEA", "JOE", "#4a2a1a", "#d8a050", "#ffe8c0", "Diner Joe. Burnt On Purpose."),
        _p("COFFEE & TEA", "DECAF", "#2a5a3a", "#f0e0b0", "#ffffff", "Why Bother"),
        _p("COFFEE & TEA", "MUD", "#1a1a1a", "#c04a1a", "#f0c070", "Strong Enough to Stand a Spoon In."),
        _p("COFFEE & TEA", "TEA", "#a01a2a", "#f0d090", "#fff4dc"))),
    "CANNED VEG": ("can", (
        _p("CANNED VEG", "PEAS", "#2a6a2a", "#f8f0d0", "#ffffff", "Mom-Mom's Peas. Eat Your Peas, Hon."),
        _p("CANNED VEG", "CORN", "#e0c030", "#1a4a1a", "#1a3a0a", "Skook Creamed Corn"),
        _p("CANNED VEG", "BEANS", "#6a3a1a", "#f0c060", "#fff0d0", "Delco Baked Beans. Your Problem Now."),
        _p("CANNED VEG", "BEETS", "#7a1a3a", "#f0d0d8", "#ffffff"))),
    "SOUP": ("can", (
        _p("SOUP", "CHOWDA", "#e8e0c8", "#1a6a8a", "#0a3a50", "Shore Chowda. Chopped Like Your Shore House."),
        _p("SOUP", "PEPPOT", "#b04a1a", "#f8e8c0", "#ffffff", "Pepper Pot. Don't Ask What's In It."),
        _p("SOUP", "NOODLE", "#f0d060", "#a01a1a", "#6a0a0a"),
        _p("SOUP", "MEAT", "#d8a8a0", "#5a1a1a", "#4a0a0a", "Potted Meat Product. Meat-Adjacent."))),
    "PASTA & RICE": ("box", (
        _p("PASTA & RICE", "ZITI", "#f0e8d0", "#b02020", "#2a5a2a", "Sunday at Two. Not Two-Fifteen."),
        _p("PASTA & RICE", "PENNE", "#2a6a3a", "#f0e8d0", "#fff8e8"),
        _p("PASTA & RICE", "SHELL", "#b02020", "#f0e8d0", "#fff8e8"),
        _p("PASTA & RICE", "RICE", "#e8a020", "#ffffff", "#4a2a08"))),
    "SAUCES": ("jar", (
        _p("SAUCES", "GRAVY", "#9a1a1a", "#2a6a2a", "#fff8e0", "Nonna's Gravy. It's Gravy. Don't Start."),
        _p("SAUCES", "VODKA", "#e07050", "#f8f0e0", "#ffffff", "Vodka Sauce. Cooks Off. Mostly."),
        _p("SAUCES", "PESTO", "#2a7a2a", "#f0e8c0", "#ffffff"),
        _p("SAUCES", "SALSA", "#c03a10", "#f0d040", "#fff4d0"))),
    "BAKING": ("box", (
        _p("BAKING", "FLOUR", "#f4f0e6", "#2a4a8a", "#1a2a5a"),
        _p("BAKING", "SUGAR", "#f8f8f8", "#c02a4a", "#8a0a2a"),
        _p("BAKING", "CAKE", "#f07aa0", "#fff0f4", "#ffffff", "Cake Mix. Add Eggs. Add Guilt."),
        _p("BAKING", "FUDGE", "#4a2010", "#e8b080", "#ffe8d0"))),
    "SPICES": ("small", (
        _p("SPICES", "SALT", "#2a5ab0", "#ffffff", "#ffffff"),
        _p("SPICES", "PEPPA", "#2a2a2a", "#d8c8a0", "#ffffff", "Black Peppa"),
        _p("SPICES", "GARLC", "#f0e8d0", "#6a8a2a", "#3a4a10"),
        _p("SPICES", "CRAB", "#c03020", "#f0c040", "#fff8d0", "Crab Spice. For Fries. For Everything."))),
    "CHIPS": ("bag", ()),
    "SODA": ("bottle", ()),
    "COOKIES": ("box", (
        _p("COOKIES", "SNAPS", "#d08020", "#7a3a10", "#fff4dc", "Ginger Snaps. Older Than You."),
        _p("COOKIES", "WAFER", "#f0d8a0", "#c02a6a", "#6a0a2a"),
        _p("COOKIES", "FIGGY", "#6a3a6a", "#e8c070", "#ffffff"),
        _p("COOKIES", "CREME", "#1a1a3a", "#f8f8f8", "#ffffff", "Sandwich Cremes. Twist, Lick, Regret."))),
    "CANDY": ("candy", ()),
    "JUICE": ("bottle", (
        _p("JUICE", "OJ", "#f08a10", "#fff0a0", "#ffffff"),
        _p("JUICE", "APPLE", "#d8a020", "#c02020", "#ffffff"),
        _p("JUICE", "PRUNE", "#4a1a3a", "#d8a0c0", "#ffffff", "Prune Juice. You Know Why."),
        _p("JUICE", "PUNCH", "#d01a4a", "#ffd0e0", "#ffffff"))),
    "DRINK MIX": ("canister", (
        _p("DRINK MIX", "LEMON", "#f0e040", "#e08a10", "#4a3a08"),
        _p("DRINK MIX", "ICETEA", "#8a4a1a", "#f8e0a0", "#ffffff"),
        _p("DRINK MIX", "PUNCH", "#c01a6a", "#ffe0f0", "#ffffff", "Just Add Wooder."),
        _p("DRINK MIX", "COCOA", "#4a2a1a", "#f0e0d0", "#ffffff"))),
    "PAPER GOODS": ("pack", (
        _p("PAPER GOODS", "TOWELS", "#f8f8f8", "#2a8ac0", "#0a3a6a"),
        _p("PAPER GOODS", "TP", "#f8f4f0", "#6a3aa0", "#3a1a6a", "Two-Ply. For a Two-Ply Kind of Day."),
        _p("PAPER GOODS", "NAPKIN", "#f8f8f0", "#c03a2a", "#6a1a10"))),
    "CLEANING": ("jug", (
        _p("CLEANING", "BLEACH", "#f8f8f8", "#2a5ab0", "#0a2a6a"),
        _p("CLEANING", "SCRUB", "#2ab0a0", "#f8f8f8", "#ffffff"),
        _p("CLEANING", "PINE", "#2a6a2a", "#e8d080", "#ffffff", "Smells Like a Bus Station. In a Forest."),
        _p("CLEANING", "SUDS", "#3a8ae0", "#f0f8ff", "#ffffff"))),
    "PET FOOD": ("sack", (
        _p("PET FOOD", "KIBBLE", "#a03a1a", "#f0c060", "#ffffff"),
        _p("PET FOOD", "CHOW", "#2a5a8a", "#f0e0a0", "#ffffff", "Rowhome Chow. Your Dog Ate Worse."),
        _p("PET FOOD", "KITTY", "#6a3a8a", "#f0d0f0", "#ffffff"))),
    "CHARCOAL": ("sack", (
        _p("CHARCOAL", "COALS", "#1a1a1a", "#e05a10", "#f0c040", "Backyard Coals. The Fire Dept Knows Us."),
        _p("CHARCOAL", "LITE", "#2a2a2a", "#f0e040", "#f0e040"))),
    "HEALTH": ("small", (
        _p("HEALTH", "PILLS", "#f8f8f8", "#c02a2a", "#8a0a0a"),
        _p("HEALTH", "TUMMY", "#f07aa0", "#ffffff", "#ffffff", "For After the Pepper Pot"),
        _p("HEALTH", "COUGH", "#3a2a8a", "#f0d040", "#ffffff"),
        _p("HEALTH", "BANDS", "#e8c0a0", "#c02a2a", "#6a1a0a"))),
    "BEAUTY": ("bottle", (
        _p("BEAUTY", "SUDS", "#e080c0", "#ffffff", "#ffffff"),
        _p("BEAUTY", "HAIR", "#2aa0a0", "#f8f0e0", "#ffffff", "Wildwood Hair. Volume Like '87."),
        _p("BEAUTY", "LOTION", "#f0e8d8", "#8a6a3a", "#4a2a08"))),
    "BABY": ("pack", (
        _p("BABY", "DIAPER", "#a0d0f0", "#f8f8f8", "#1a4a8a"),
        _p("BABY", "WIPES", "#f8f8f8", "#80c080", "#2a5a2a"))),
    "CARDS": ("small", (
        _p("CARDS", "BDAY", "#f0d040", "#c02a6a", "#6a0a2a"),
        _p("CARDS", "SORRY", "#8a8aa0", "#f8f8f8", "#ffffff", "Sorry About the Dog"),
        _p("CARDS", "SICK", "#80c0a0", "#f8f8f0", "#ffffff", "Get Well. Or Don't."))),
}

#: The longest `short` a front tile can set: every grocery tile is 40 pixels
#: across (`snack_gondola_forms.GROCERY_TILES`), six letters of m5x7.
SHORT_MAX = 6

PRODUCTS = tuple(p for _pack, items in CATEGORIES.values() for p in items)
BY_ID = {p["id"]: p for p in PRODUCTS}

#: Real marks a row may not carry, as whole words (upper case): the cereal,
#: soup, canned-goods, pasta and household makers, then the region's
#: supermarket chains.
DENY_WORDS = ("KELLOGG", "KELLOGGS", "KELLOGG'S", "POST", "CHEERIOS", "WHEATIES", "KIX", "TRIX",
              "CHEX", "FROOT", "CAP'N", "CAMPBELL", "CAMPBELLS", "CAMPBELL'S", "PROGRESSO",
              "GOYA", "HEINZ", "HUNT'S", "HUNTS", "LIBBY'S", "SPAM", "HORMEL", "BARILLA",
              "RONZONI", "MUELLER'S", "MUELLERS", "PRINCE", "CONTADINA", "PRAGO", "RAGU", "JIF",
              "SKIPPY", "FOLGERS", "MAXWELL", "LIPTON", "TETLEY", "OREO", "OREOS", "NABISCO",
              "TROPICANA", "MOTT'S", "MOTTS", "KOOL-AID", "TANG", "BOUNTY", "CHARMIN", "SCOTT",
              "CLOROX", "PINE-SOL", "LYSOL", "AJAX", "PURINA", "ALPO", "MEOW", "KINGSFORD",
              "TYLENOL", "BAYER", "PEPTO", "BAND-AID", "PAMPERS", "HUGGIES", "HALLMARK",
              "PRELL", "SUAVE", "JERGENS", "MCCORMICK", "MORTON", "DOMINO", "PILLSBURY",
              "DUNCAN", "BETTY", "STROEHMANN", "AMOROSO", "AMOROSO'S", "ACME", "PATHMARK",
              "GENUARDI'S", "GENUARDIS", "SHOPRITE", "CLEMENS", "WEIS", "GIANT")
#: Real product names and marks of more than one word, as substrings.
DENY_PARTS = ("GENERAL MILLS", "FROSTED FLAKES", "CORN FLAKES", "RAISIN BRAN", "LUCKY CHARMS",
              "RICE KRISPIES", "SPECIAL K", "CRUNCH BERRIES", "DEL MONTE", "GREEN GIANT",
              "CHEF BOYARDEE", "DINTY MOORE", "SAN GIORGIO", "DE CECCO", "SHOP RITE",
              "SUPER FRESH", "BUSH'S", "B&M", "OLD BAY", "CRYSTAL LIGHT", "COUNTRY TIME",
              "MR. CLEAN", "MR CLEAN", "SWISS MISS", "NEW ENGLAND", "CAMPBELL'S")


def hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def words(p: dict) -> str:
    return " ".join((p["category"], p["short"], p["says"]))
