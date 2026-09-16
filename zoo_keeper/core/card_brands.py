"""The factory's invented trading-card games, makers and teams: ONE table.

Zoo 0.95.0, for the 1990s card shop. The walker, 2026-09-15: "a 90s Trader
Card Shop (Fake Pokemon, Fake Magic, Fake sports trading cards)", with nine
photos written up in the factory's `docs/SET_DRESSING_REFERENCES.md` under
"The walker's trading card shop references". Every brand in those photos is
a real mark and stays out of the tools; the shop sells invented Delco
parodies, the way `brands.py` (the drinks), `cigarette_brands.py` (the
packs), `liquor_brands.py` (the bottles) and `club_names.py` (the neon) do.

One table, because a booster box on a pack wall, a sealed box in a display
case and a header sign over a bay must be able to carry the same game
without a second list drifting from this one. Pure Python and no bpy;
`core/card_art.py` is the first reader.

THE RULES EVERY ROW KEEPS, and `tests/test_card_brands.py` holds the
mechanical ones:

  * INVENTED. No real card game, publisher, grader, league, team or player
    -- in a name, a slogan, a maker or a team. `DENY_WORDS` is matched as
    whole words (short marks that are also English words: SCORE, LEAF,
    CLASSIC), `DENY_PARTS` anywhere in the string. The test holds every
    PAINTED string, which is a different set from this table the moment
    somebody adds a word to the art.
  * THE ART PARODIES THE FRAME, NOT THE MARK. The reference lists the card
    styles by their FRAMES -- "a monster game's yellow border, a wizard
    game's black border and brown back, a sci-fi game's grey frame, a
    sports card's white border and team logo" -- and those are the four
    `KINDS` here. A border colour is not trade dress; a specific creature,
    a specific symbol or a specific logotype would be, and none is drawn.
  * PG-13: crass, not obscene, and nothing aimed at children even though a
    card shop's customers are.
  * LEGIBLE WHERE IT IS READ, AND NOT WHERE IT IS NOT. `short` is what a
    box front carries at `card_art.TEXEL` (160 px/m -- a 0.27 m box front
    is 43 px wide); `name` is what a bay's header sign carries, which is
    read across a room. A card FACE is never lettered: at play distance
    nobody reads one, and painting type nobody can resolve costs the same
    as painting type somebody can.

THREE SUGGESTED NAMES WERE CHANGED, kept here as the record:

  * FOLSOM FLYERS became FOLSOM FLOUNDERS. Folsom is a Delco place and the
    team is invented, but FLYERS is the Philadelphia hockey club and a
    pennant is exactly where a reader would take it as one. `DENY_WORDS`
    catches it, which is how it was caught.
  * The monster game's first slogan was "Collect 'Em All, Hon". The first
    four words of it are the national monster game's own tagline in 1997
    with a Delco word stapled on; it is now "Collect the Whole Jawn."
  * MACDADE MYSTICS became MACDADE MIDNIGHT. MYSTICS is a WNBA club --
    founded the year after this game is set, so no 1997 reader would have
    taken it that way, and every reader since would. The denylist does not
    hold it (nothing here is a WNBA reference) and it was changed anyway:
    a guard is a floor, not the decision.

Colours are sRGB hex, the space `card_art` paints in.
"""
from __future__ import annotations

#: The four card frames the reference names. A game's `kind` picks the
#: layout `card_art` draws; it is not a genre label.
KINDS = ("monster", "wizard", "scifi", "sport")

#: id, the display name (what a header sign says), the short name (what a
#: box front says), the kind, the border, the ground behind the figure, the
#: figure's ink, an accent, and the slogan.
GAMES = (
    {"id": "jawn_beasts", "name": "JAWN BEASTS", "short": "JAWN",
     "kind": "monster", "border": "#e8c832", "ground": "#f2ead0",
     "ink": "#2a5cb8", "accent": "#c8202a",
     "slogan": "Collect the Whole Jawn."},
    {"id": "wooder_wigglers", "name": "WOODER WIGGLERS", "short": "WDR",
     "kind": "monster", "border": "#f0b428", "ground": "#dceef2",
     "ink": "#1a6a88", "accent": "#1e7a4a",
     "slogan": "They Live in the Crick."},
    {"id": "scrapple_horrors", "name": "SCRAPPLE HORRORS", "short": "SCRP",
     "kind": "monster", "border": "#d8a832", "ground": "#e8d8c0",
     "ink": "#5a2a14", "accent": "#8a1a12",
     "slogan": "Nine Parts. No Questions."},
    {"id": "hexes_and_hoagies", "name": "HEXES & HOAGIES", "short": "HEX",
     "kind": "wizard", "border": "#141416", "ground": "#4a2e18",
     "ink": "#e8c890", "accent": "#7a3a8a",
     "slogan": "Cast It, Hon."},
    {"id": "nanas_grimoire", "name": "NANA'S GRIMOIRE", "short": "NANA",
     "kind": "wizard", "border": "#1a1024", "ground": "#3a2044",
     "ink": "#e0c8f0", "accent": "#c8a032",
     "slogan": "She Wrote It All Down."},
    {"id": "blue_route_2099", "name": "BLUE ROUTE 2099", "short": "2099",
     "kind": "scifi", "border": "#6a6e74", "ground": "#101820",
     "ink": "#38d8e8", "accent": "#e8541a",
     "slogan": "The Merge Never Ends."},
    {"id": "orbit_essington", "name": "ORBIT ESSINGTON", "short": "ORBT",
     "kind": "scifi", "border": "#7a8088", "ground": "#141824",
     "ink": "#9ab4c8", "accent": "#e8c832",
     "slogan": "Cleared for the Tank Farm."},
    {"id": "delco_diamond", "name": "DELCO DIAMOND LEAGUE", "short": "DDL",
     "kind": "sport", "border": "#f2f2ec", "ground": "#2a7a3a",
     "ink": "#1a1a1a", "accent": "#c8202a",
     "slogan": "Six Innings and a Hoagie."},
    {"id": "pike_gridiron", "name": "PIKE GRIDIRON '97", "short": "PIKE",
     "kind": "sport", "border": "#f0ece0", "ground": "#2a5cb8",
     "ink": "#1a1a1a", "accent": "#d8a832",
     "slogan": "Mud Optional. Mostly."},
    {"id": "youse_vs_them", "name": "YOUSE VS. THEM", "short": "YOUS",
     "kind": "monster", "border": "#e05a1a", "ground": "#f4e8d8",
     "ink": "#3a1a4a", "accent": "#1e7a4a",
     "slogan": "Somebody's Gotta Lose."},
    {"id": "macdade_midnight", "name": "MACDADE MIDNIGHT", "short": "MDNT",
     "kind": "wizard", "border": "#101014", "ground": "#2a3a24",
     "ink": "#d8e8c0", "accent": "#b83a1a",
     "slogan": "Third Eye on the Boulevard."},
    {"id": "tinicum_troopers", "name": "TINICUM TROOPERS", "short": "TNCM",
     "kind": "scifi", "border": "#5a6068", "ground": "#1a1414",
     "ink": "#e8a038", "accent": "#38a0c8",
     "slogan": "Marshland Recon, Season Two."},
)

BY_ID = {g["id"]: g for g in GAMES}
IDS = tuple(g["id"] for g in GAMES)

#: Who printed the cards -- the name on a wax box's maker band and on the
#: header strip of a storage box. Invented, and deliberately small-press:
#: a national printer in 1997 would be a real mark.
MAKERS = (
    {"id": "pike_press", "name": "PIKE PRESS", "short": "PIKE",
     "ink": "#c8202a"},
    {"id": "wooder_works", "name": "WOODER WORKS", "short": "WDR",
     "ink": "#1a6a88"},
    {"id": "delco_deck", "name": "DELCO DECK CO.", "short": "DDC",
     "ink": "#1e5a4e"},
    {"id": "scrapple_press", "name": "SCRAPPLE PRESS", "short": "SCRP",
     "ink": "#8a4a14"},
    {"id": "nanas_attic", "name": "NANA'S ATTIC", "short": "ATTIC",
     "ink": "#6a2a5a"},
    {"id": "hoagie_mouth", "name": "HOAGIE MOUTH CARDS", "short": "HMC",
     "ink": "#3a3a3e"},
)

#: The invented local teams: what a sports card's chip and a felt pennant
#: wear. ``(name, primary sRGB hex, secondary sRGB hex)``. Places are
#: places, not businesses, and no nickname here belongs to a real club --
#: FOLSOM FLOUNDERS is the one that had to move (see the module docstring).
TEAMS = (
    ("RIDLEY RIVETERS", "#16234a", "#c8202a"),
    ("MACDADE MAULERS", "#5a1020", "#d8a832"),
    ("CHESTER PIKE PIGEONS", "#5a5e64", "#1a8aa8"),
    ("TINICUM TERNS", "#e8eaee", "#2a5cb8"),
    ("MARCUS HOOK MUDCATS", "#4a2e18", "#e0741a"),
    ("GLENOLDEN GOATS", "#1e5a2c", "#f0e4c0"),
    ("ESSINGTON EELS", "#14161a", "#8ad81a"),
    ("DARBY DRILLERS", "#e0741a", "#1a1a1e"),
    ("BOOTHWYN BRAWLERS", "#4a2070", "#f2f2ec"),
    ("CRUM CREEK CRABS", "#b82418", "#e8c890"),
    ("PROSPECT PARK PORKERS", "#e090a8", "#16234a"),
    ("FOLSOM FLOUNDERS", "#1a7a78", "#c0c4c8"),
    ("ASTON ANVILS", "#3a4048", "#c8202a"),
    ("MORTON MOLES", "#4a3218", "#e8c832"),
    ("NORWOOD NAILERS", "#16234a", "#e0741a"),
    ("SWARTHMORE SWAMPERS", "#2a5a24", "#d8a832"),
)

#: What a shop says that is not a brand: the hand-lettered signs the
#: reference photographs. No price is a real one and no phrase is a mark.
SHOP_SAYS = (
    "SINGLES 50 CENTS",
    "NO TRADES WITHOUT A GROWN-UP",
    "CASH ONLY HON",
    "ASK TO SEE THE CASE",
    "BOOSTERS 2 FOR 5",
    "WE BUY WHOLE COLLECTIONS",
)

#: Real marks as WHOLE WORDS (upper case), matched as tokens so a short mark
#: that is also an English word catches the mark and not a word containing
#: it. SCORE, LEAF, CLASSIC, ULTRA, PRO and UNION are card brands or clubs
#: and are also words a writer would reach for on a shop sign.
DENY_WORDS = (
    "TOPPS", "FLEER", "DONRUSS", "SCORE", "LEAF", "BOWMAN", "SKYBOX",
    "PINNACLE", "PACIFIC", "CLASSIC", "ULTRA", "PRO", "SELECT", "FINEST",
    "CHROME", "STADIUM", "COLLECTOR", "PANINI", "ACTION",
    "PSA", "BECKETT", "SGC", "BGS", "CGC",
    "NFL", "NBA", "MLB", "NHL", "NCAA", "MLS", "WNBA",
    "EAGLES", "PHILLIES", "FLYERS", "SIXERS", "76ERS", "PHANTOMS",
    "UNION", "WINGS", "QUAKERS", "STEELERS", "PIRATES", "PENGUINS",
    "YANKEES", "METS", "COWBOYS", "BRAVES", "ORIOLES", "DEVILS", "RANGERS",
    "POKEMON", "PIKACHU", "CHARIZARD", "NINTENDO", "KONAMI", "BANDAI",
    "MAGIC", "GATHERING", "WOTC", "MANA", "PLANESWALKER", "DECIPHER",
    "DIGIMON", "MARVEL", "BATMAN", "SUPERMAN",
    "WAWA", "TASTYKAKE", "YUENGLING", "ACME", "GRITTY",
)

#: Real marks ANYWHERE in a string, words run together or not.
DENY_PARTS = (
    "UPPER DECK", "UPPERDECK", "PRO SET", "PROSET", "O-PEE-CHEE", "OPEECHEE",
    "PLAYOFF", "SP AUTHENTIC", "METAL UNIVERSE", "GAME FREAK", "CREATURES INC",
    "POKE", "YU-GI-OH", "YUGIOH", "DUEL MONSTERS", "DUELMONSTERS",
    "WIZARDS OF THE COAST", "RICHARD GARFIELD", "BLACK LOTUS", "MOXEN",
    "ICE AGE", "REVISED EDITION", "UNLIMITED EDITION", "ALPHA BETA",
    "STAR WARS", "STARWARS", "STAR TREK", "STARTREK", "JEDI", "KLINGON",
    "X-MEN", "SPIDER-MAN", "SPIDERMAN", "DC COMICS",
    "ULTRA PRO", "ULTRAPRO", "DRAGON SHIELD", "DRAGONSHIELD", "CARD SAVER",
    "GRIFFEY", "MANTLE", "GRETZKY", "IVERSON", "SCHMIDT", "JETER", "BONDS",
    "BLUE DEVILS", "RED SOX", "WHITE SOX", "PHILA EAGLES",
    "PHILIP MORRIS", "RITA'S WATER ICE",
)


def hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def words(game: dict) -> str:
    """Every string a game contributes to painted art."""
    return " ".join((game["name"], game["short"], game["slogan"]))


def game_order(key: str) -> tuple:
    """The games in an order derived from ``key`` -- a module stem, so two
    bays of one pack wall and two cases in one shop carry different games
    without anybody choosing which.

    A ROTATION, not a shuffle: the table's own order is the order a shop
    stocks in (the three monster games together, then the wizards), and a
    shuffle would scatter them. `zlib.crc32` because every other art module
    here derives its picks from it.
    """
    import zlib
    n = len(GAMES)
    k = (zlib.crc32(str(key).encode("utf-8")) & 0xFFFFFFFF) % n
    return tuple(GAMES[(k + i) % n] for i in range(n))


def team_order(key: str) -> tuple:
    """`TEAMS`, rotated by ``key`` the way `game_order` rotates the games,
    so two pennant rows on two walls of one room are not the same strip."""
    import zlib
    n = len(TEAMS)
    k = (zlib.crc32(str(key).encode("utf-8")) & 0xFFFFFFFF) % n
    return tuple(TEAMS[(k + i) % n] for i in range(n))


def maker_for(key: str) -> dict:
    import zlib
    return MAKERS[(zlib.crc32(str(key).encode("utf-8")) & 0xFFFFFFFF)
                  % len(MAKERS)]
