"""What the wall posters say -- every word invented, reviewed, and fixed here.

Zoo 1.30.0. The walker, 2026-09-29, choosing where posters go: strip club
interiors, bar interiors, exterior alley walls and poles, store windows and
walls -- with three guides now in the root repo, `docs/reference/`:
`Making_Strong_2D_Poster_Art_With_Procedural_Tools.md` (the art),
`Procedural_Poster_Art_Guide_Blender_Godot_4_7.md` (the system) and
`Lewd_Poster_Art_Direction_Guide.md` (the copy and the tone by location).

THE COPY IS A TABLE, NEVER GENERATED. The system guide: "Use explicit
generated copy rather than letting the system invent text at render time;
this keeps spelling, humor, and world lore reviewable." A seed picks a row;
it never writes one.

THE JOKE HAS A SHAPE (the lewd guide): a ridiculous promise, a double
meaning, and a deflating turn -- one gag a poster, the headline carrying it
at a glance and the small line rewarding a closer look. The limits are the
guide's and the walker's standing ones together: suggestive, never
explicit; adults only, and never in a youth-coded place (the card shop keeps
its collector promos); no real protected group as the punchline; every name
an invented Delco one, PG-13 crass, and no real business, band or brand --
held against `DENYLIST` below and the factory's other denylists by
`test_poster_wall.py`.

Family keys are the locations the walker named: `club`, `bar`, `alley`,
`store`. Each row is ``(headline, small_line)``; a bar row's headline is a
band. Every character must be in the pixel face the painter sets it in.
"""
from __future__ import annotations

FAMILIES = ("club", "bar", "alley", "store")

#: The strip club's own posters: brash faux glamour with a wink. The
#: headline is the promise; the small line lets the air out of it. Every
#: headline word sets at scale 2 across a marquee (102 px): CHAMPAGNE and
#: SHOWGIRLS were 110 and shrank to scale 1, so they became BUBBLY and SHOW
#: GIRLS (the typography guide's first fix is the words, not the size).
CLUB = (
    ("VIP ROOM", "VERY IMPORTANT PARKING LOT"),
    ("AMATEUR NIGHT", "EVERY NIGHT, APPARENTLY"),
    ("LIVE ON STAGE", "MOSTLY LIVE"),
    ("BUBBLY ROOM", "ASK ABOUT OUR BEER"),
    ("WORLD FAMOUS", "IN UPPER DARBY"),
    ("NO COVER TIL 9", "AFTER 9 WE COVER NOTHING"),
    ("BIRTHDAY BASH", "BRING YOUR OWN CAKE. AND ID."),
    ("DOLLAR DANCES", "SHAME NOT INCLUDED"),
    ("SHOW GIRLS", "SHOWING UP IS HALF OF IT"),
    ("GRAND OPENING", "AGAIN. SINCE 1991."),
    ("CLASSY LADIES", "CLASSY IS A STRONG WORD"),
    ("HAPPY HOUR", "HAPPINESS NOT GUARANTEED"),
)

#: The bar's photocopied gig bills: a band nobody has heard of, a promise the
#: venue cannot keep. Headline = the band.
BAR = (
    ("THE JAWNS", "COLD BEER. ONE WORKING MIC."),
    ("SCRAPPLE TRAP", "$2 DRAFTS TIL THE BAND GETS GOOD"),
    ("MACDADE MAYHEM", "NO COVER. NO REFUNDS. NO NOTES."),
    ("THE PIKE RATS", "ALL AGES* *21 AND OVER"),
    ("DIRTY WOODER", "FRI NITE. LOUD. SORRY IN ADVANCE."),
    ("YO YO DELCO", "FEATURING THE GUY WHO OWES YOU $20"),
    ("THE SHOOBIES", "DOWN THE SHORE SOUND. UP THE PIKE."),
    ("RIDLEY RUCKUS", "HEADLINING THE BACK ROOM"),
    ("ESSINGTON EMERGENCY", "TONIGHT ONLY. THANK GOD."),
    ("THE HOAGIE ROLLS", "ROCK N ROLL WITH EVERYTHING"),
    ("CHESTER PIKE CHOIR", "NOT A CHOIR. BARELY A BAND."),
    ("KARAOKE HELL", "EVERY TUES. YOU WERE WARNED."),
)

#: The alley's layered handbills: the neighbourhood talking to itself. Most
#: are not a gag about sex at all -- the guide: "mix adult humor with local
#: band bills, fake civic notices, odd jobs, lost-pet flyers".
ALLEY = (
    ("LOST CAT", "ANSWERS TO NOTHING"),
    ("ROOM 4 RENT", "NO WEIRDOS. OK SOME WEIRDOS."),
    ("GUITAR LESSONS", "CALL VINNY. HIS MOM ANSWERS."),
    ("WE BUY GOLD", "AND SCRAP. AND WHATEVER."),
    ("SEEN MY BIKE?", "I KNOW YOU DID"),
    ("BLOCK PARTY SAT", "BRING A CHAIR. BRING TWO."),
    ("PAINTER NEEDED", "MUST OWN LADDER. AND PANTS."),
    ("BASEMENT DOJO", "KARATE. BRING SNACKS."),
    ("YARD SALE", "THE COUCH MUST GO."),
    ("CAR WASH SAT", "WE WASH. WE DO NOT DRY."),
    ("GARAGE BAND", "NEEDS DRUMMER. ANY DRUMMER."),
    ("FOUND: KEYS", "NOT YOURS. PROBABLY."),
)

#: The store's day-glo sale posters, in the window and on the walls. The
#: headline is the deal; the small line is the fine print.
STORE = (
    ("2 FOR $3", "ANY 20 OZ. LIMIT: NONE. GOOD LUCK."),
    ("ICE COLD", "COLDER THAN THE CLERK"),
    ("LOTTO HERE", "WINNERS SOLD HERE. ONCE."),
    ("SCRATCH & WIN", "OR SCRATCH & WAIT"),
    ("HOAGIES", "MADE FRESH. FRESHISH."),
    ("COFFEE 69C", "HOT. BROWN. LEGAL."),
    ("OPEN 24 HRS", "THE CLERK IS NOT"),
    ("PHONE CARDS", "CALL HOME. THEY MISS YOU."),
    ("ATM INSIDE", "FEES ALSO INSIDE"),
    ("WE CARD", "EVEN YOU, GRANDPA"),
    ("HOT DOGS 2/$1", "ASK NO QUESTIONS"),
    ("PRETZELS", "SOFT. SALTY. LIKE US."),
)

COPY = {"club": CLUB, "bar": BAR, "alley": ALLEY, "store": STORE}

#: Real businesses, bands, brands and chains a writer reaches for around
#: Delaware County in the 1990s, held against every line above.
DENYLIST = (
    "WAWA", "SHEETZ", "TASTYKAKE", "HERR", "YUENGLING", "ROLLING ROCK",
    "PABST", "COORS", "BUDWEISER", "MILLER", "GATORADE", "POWERADE", "PEPSI",
    "COKE", "COCA", "SPRITE", "DR PEPPER", "7UP", "SNAPPLE", "LOTTERY",
    "POWERBALL", "MEGA MILLIONS", "CHICKIE", "PAT'S", "GENO", "DELILAH",
    "CHEERLEADERS", "PENTHOUSE", "PLAYBOY", "HOOTERS", "BON JOVI",
    "SPRINGSTEEN", "HALL & OATES", "PHISH", "PEARL JAM", "NIRVANA",
)

#: Fictional phone numbers only: the 555-01xx block is reserved for fiction.
PHONES = ("610-555-0142", "610-555-0177", "484-555-0119", "610-555-0103",
          "484-555-0186", "610-555-0158")

#: Fictional dates, all in the autumn of 1997.
DATES = ("FRI 10/17", "SAT 10/18", "FRI 10/24", "SAT 10/25", "FRI 10/31",
         "SAT 11/1")


def rows(family):
    """The family's ``(headline, small_line)`` rows."""
    if family not in COPY:
        raise ValueError(f"no poster family {family!r}; the families are {', '.join(FAMILIES)}")
    return COPY[family]


def all_strings():
    """Every string a poster can paint, for the denylist and font tests."""
    out = []
    for fam in FAMILIES:
        for head, small in COPY[fam]:
            out += [head, small]
    return out + list(PHONES) + list(DATES)
