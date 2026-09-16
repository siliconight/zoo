"""The factory's invented LIQUOR brands: one table for every bottle on a bar.

Zoo 0.92.0, for the back bar. The walker, 2026-09-15, with a photo of a
lounge bar: "in the strip club there should be a bar with lots of bottles
like this". The photo's labels are real marks and stay out of the repo and
out of the art; these are the ones the pipeline paints instead.

The sibling of `brands.py` (drinks, for the vending machine) and
`cigarette_brands.py`, and it keeps the same rules for the same reason: a
bottle on a back bar shelf, a bottle in a speed rail and a bottle on a
counter top must be able to carry the same LABEL later, so there is one
table and not three. Pure Python, no bpy; `core/back_bar_art.py` is the
first reader.

THE RULES EVERY ROW KEEPS, and `tests/test_back_bar.py` holds the
mechanical ones:

  * INVENTED. No real trademark and no close imitation of one. Not a
    national spirit's name, script or palette; not a Pennsylvania distiller
    or brewer (`DENYLIST` carries the ones a Delco bar would actually
    stock, which is exactly why they are the easy mistake); not a real
    bar's name. Place names are not marks and the neighbouring tables
    already use them -- MacDade, Chester, Baltimore Pike -- so a row may be
    named for a road or a creek but never for a company on one. Two
    candidates were cut while writing this and are kept as the record:
    RITTENHOUSE RYE -> CHESTER CREEK RYE (Rittenhouse is a shipping rye,
    not just a square), and BLUECOAT -> YOUSE FIRST (Bluecoat is a
    Philadelphia gin). Palettes avoid the black-and-white Tennessee label,
    the red wax, the green-and-gold Irish cream and the amber-on-cream of
    the bourbons.
  * PG-13: crass, not obscene. A bar in 1997 Delaware County, not a
    bachelor party.
  * LEGIBLE AT THE SHELF. `logo` is set in the factory's pixel face across
    a label 64 px wide (about 1 mm a pixel at bottle scale), so each line
    is short; `line` is the small type under it and `proof` the number in
    the corner. `back_bar_art.LABEL_PX` is where those numbers live.

Colours are sRGB 0..255 triples, the space the art is painted in.
"""
from __future__ import annotations

#: Each row: id, the label's words (one line each, top to bottom), what is
#: in the bottle, the small line under the logo, the proof in the corner,
#: the label's ground and ink, the foil band's colour, and the GLASS the
#: bottle is blown in (`back_bar_forms.GLASS`).
BRANDS = (
    {"id": "macdade_gold", "logo": ("MACDADE", "GOLD"),
     "spirit": "blended whiskey", "line": "AGED SINCE LAST TUESDAY",
     "proof": "80", "ground": (28, 22, 18), "ink": (236, 198, 96),
     "foil": (196, 150, 40), "glass": "amber"},
    {"id": "wooder_shine", "logo": ("WOODER", "SHINE"),
     "spirit": "corn whiskey", "line": "CUT WITH WOODER. ALLEGEDLY.",
     "proof": "101", "ground": (238, 234, 220), "ink": (26, 58, 96),
     "foil": (150, 170, 190), "glass": "clear"},
    {"id": "jawn_royale", "logo": ("JAWN", "ROYALE"),
     "spirit": "vodka", "line": "TRIPLE FILTERED THRU A JAWN",
     "proof": "80", "ground": (18, 26, 52), "ink": (222, 228, 240),
     "foil": (170, 180, 200), "glass": "clear"},
    {"id": "youse_first", "logo": ("YOUSE", "FIRST"),
     "spirit": "gin", "line": "YOUSE FIRST. NO, YOUSE.",
     "proof": "94", "ground": (20, 60, 44), "ink": (226, 236, 222),
     "foil": (180, 196, 150), "glass": "green"},
    {"id": "chester_creek", "logo": ("CHESTER", "CREEK", "RYE"),
     "spirit": "rye whiskey", "line": "STRAIGHT. MOSTLY.",
     "proof": "90", "ground": (120, 34, 26), "ink": (242, 224, 190),
     "foil": (208, 168, 80), "glass": "amber"},
    {"id": "hoagie_mouth", "logo": ("HOAGIE", "MOUTH"),
     "spirit": "anisette", "line": "CURES WHAT THE HOAGIE STARTED",
     "proof": "70", "ground": (226, 214, 120), "ink": (44, 38, 12),
     "foil": (160, 140, 50), "glass": "clear"},
    {"id": "nanas_cordial", "logo": ("NANA'S", "CORDIAL"),
     "spirit": "blackberry brandy", "line": "TWO FINGERS AND A NAP",
     "proof": "60", "ground": (78, 26, 72), "ink": (238, 214, 236),
     "foil": (198, 170, 196), "glass": "amber"},
    {"id": "pike_silver", "logo": ("PIKE", "SILVER"),
     "spirit": "tequila", "line": "WORM SOLD SEPARATELY",
     "proof": "80", "ground": (232, 232, 226), "ink": (60, 60, 64),
     "foil": (190, 190, 186), "glass": "clear"},
    {"id": "ridley_dark", "logo": ("RIDLEY", "DARK"),
     "spirit": "dark rum", "line": "DARK AS THE CREEK IN JULY",
     "proof": "86", "ground": (34, 20, 12), "ink": (216, 160, 78),
     "foil": (150, 96, 34), "glass": "amber"},
    {"id": "tinicum_triple", "logo": ("TINICUM", "TRIPLE SEC"),
     "spirit": "orange cordial", "line": "ORANGE-ISH",
     "proof": "48", "ground": (226, 122, 26), "ink": (36, 20, 6),
     "foil": (240, 190, 90), "glass": "clear"},
    {"id": "boothwyn_barrel", "logo": ("BOOTHWYN", "BARREL"),
     "spirit": "bourbon", "line": "BARREL AGED IN A BASEMENT",
     "proof": "100", "ground": (96, 52, 20), "ink": (240, 222, 178),
     "foil": (214, 176, 90), "glass": "amber"},
    {"id": "crum_creek_cream", "logo": ("CRUM CREEK", "CREAM"),
     "spirit": "cream liqueur", "line": "CURDLES WITH ATTITUDE",
     "proof": "34", "ground": (214, 198, 168), "ink": (72, 40, 24),
     "foil": (170, 140, 96), "glass": "clear"},
    {"id": "delco_devil", "logo": ("DELCO", "DEVIL"),
     "spirit": "cinnamon whiskey", "line": "BURNS TWICE. SORRY.",
     "proof": "66", "ground": (150, 18, 22), "ink": (250, 226, 150),
     "foil": (230, 170, 60), "glass": "amber"},
    {"id": "essington_eel", "logo": ("ESSINGTON", "EEL"),
     "spirit": "aquavit", "line": "TASTES LIKE THE AIRPORT SMELLS",
     "proof": "84", "ground": (24, 66, 78), "ink": (206, 232, 236),
     "foil": (140, 178, 188), "glass": "green"},
)

BY_ID = {b["id"]: b for b in BRANDS}
IDS = tuple(b["id"] for b in BRANDS)

#: Names a row may not carry, in any case, anywhere in its words. NOT a
#: trademark search -- a tripwire for the ones a person writing a Delco bar
#: would reach for first, so a later row added in a hurry trips a test
#: rather than a lawyer. The Pennsylvania entries are here because they are
#: the likeliest, not the least.
DENYLIST = (
    "JAMESON", "JACK DANIEL", "JIM BEAM", "BEAM", "SMIRNOFF", "ABSOLUT",
    "TITO", "BACARDI", "CAPTAIN MORGAN", "CUERVO", "PATRON", "GREY GOOSE",
    "KETEL", "TANQUERAY", "BOMBAY", "BEEFEATER", "HENDRICK", "JOHNNIE WALKER",
    "CHIVAS", "DEWAR", "GLENLIVET", "MACALLAN", "MAKER'S MARK", "WILD TURKEY",
    "BULLEIT", "CROWN ROYAL", "SEAGRAM", "JAGERMEISTER", "FIREBALL",
    "SOUTHERN COMFORT", "KAHLUA", "BAILEYS", "MALIBU", "HENNESSY", "REMY",
    "COURVOISIER", "SKYY", "SVEDKA", "POPOV", "FOUR ROSES", "OLD FORESTER",
    "KNOB CREEK", "WOODFORD", "EVAN WILLIAMS", "EARLY TIMES", "RITTENHOUSE",
    "DAD'S HAT", "BLUECOAT", "KINSEY", "PUBLICKER", "SIX GUN",
    "YUENGLING", "ROLLING ROCK", "IRON CITY", "SCHMIDT", "ORTLIEB", "SCHLITZ",
    "PABST", "COORS", "BUDWEISER", "MICHELOB", "MILLER", "CORONA", "HEINEKEN",
    "WAWA", "TASTYKAKE", "HERR", "HABBERSETT", "EAGLES", "PHILLIES", "FLYERS",
    "SIXERS", "LOU TURK",
)


def words(brand: dict) -> str:
    """Every word a row carries, for the denylist."""
    return " ".join(list(brand["logo"]) + [brand["line"], brand["spirit"]])


def painted_strings(brand_id: str) -> list:
    """Every string a LABEL of this brand paints. The art paints nothing a
    row does not carry plus the proof mark, so this is the whole set and
    the denylist test is over the whole set."""
    b = BY_ID[brand_id]
    return list(b["logo"]) + [b["line"], b["proof"] + " PROOF"]


def order(key: str) -> tuple:
    """The brand ids in a deterministic order for ``key`` -- a back bar's
    shelves draw from the front of this, so two bars in one building stock
    different bottles. A rotation, not a shuffle: every row is used before
    any row is used twice."""
    import zlib
    n = len(IDS)
    start = (zlib.crc32(str(key).encode("utf-8")) & 0xFFFFFFFF) % n
    return tuple(IDS[(start + i) % n] for i in range(n))
