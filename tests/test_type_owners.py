"""1.49.0 -- every typeface belongs to somebody.

The walker's font catalog, 2026-10-02: "Assign a typeface to an owner." The
real look (1.46.0 to 1.48.0) set a bank's machine, a cigarette maker's ad,
the law's small print and a shop's price card in ONE face. Pixelcoat 0.55.0
vendors three more CC0 families; this holds who speaks in which, and that a
screen's letters are pixels again.
"""
from __future__ import annotations

import os

import pytest

from zoo_keeper.core import atm_forms as A
from zoo_keeper.core import cigarette_brands as CB
from zoo_keeper.core import cigarette_forms as F
from zoo_keeper.core import paint as PT
from zoo_keeper.core import pixel_type as PX
from zoo_keeper.core import smooth_type as ST
from zoo_keeper.core import video_poker_forms as V

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_every_owner_has_a_face_that_exists_and_an_unknown_owner_is_refused():
    assert set(ST.OWNERS.values()) <= set(ST.FACES)
    for owner, face in ST.OWNERS.items():
        assert ST.owned(owner) == face
        assert ST.coverage("Ag 3.50", 16, face).max() > 150, owner
    with pytest.raises(ValueError, match="no owner"):
        ST.owned("whoever")


def test_the_kinds_of_owner_do_not_share_a_family():
    """A shop's hand, a maker's legend, a notice and printed advertising are
    four families. Two weights of one family are one voice; these are not."""
    family = {"highway": "blue_highway", "aileron": "aileron", "vegur": "vegur", "oldstyle": "mfb_oldstyle",
              "minisystem": "minisystem"}

    def fam(owner):
        return family[ST.owned(owner).split("_")[0]]
    kinds = [fam("shop"), fam("maker"), fam("notice"), fam("print"), fam("display")]
    assert len(set(kinds)) == 5, kinds
    assert fam("shop") == fam("shop_small") == fam("shop_copy")
    assert fam("maker") == fam("maker_small") and fam("notice") == fam("notice_bold")
    assert fam("print") == fam("print_bold") == fam("print_italic")


def test_every_minted_face_is_one_the_mint_tool_knows_and_pixelcoat_vendors():
    import importlib.util
    spec = importlib.util.spec_from_file_location("mint", os.path.join(_ZOO, "tools", "mint_smooth_type.py"))
    mint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mint)
    assert set(mint.FACES) == set(ST.FACES)
    for name, (_rel, module) in mint.FACES.items():
        assert os.path.exists(os.path.join(_ZOO, "zoo_keeper", "core", "smooth_faces", module + ".py")), name
    fonts = os.path.join(_ZOO, "..", "pixelcoat", "assets", "fonts")
    if not os.path.isdir(fonts):
        pytest.skip("Pixelcoat is not beside this repo: the vendored files cannot be checked")
    for name, (rel, _module) in mint.FACES.items():
        path = os.path.join(fonts, rel)
        assert os.path.exists(path), (name, rel)
        folder = os.path.dirname(path)
        assert os.path.exists(os.path.join(folder, "LICENSE.txt")), rel
        assert os.path.exists(os.path.join(folder, "README.md")), rel


# --- the cigarette makers --------------------------------------------------------------


def test_every_brand_has_its_own_lettering_and_they_are_not_all_one_face():
    assert set(CB.FACE) == set(CB.IDS)
    assert set(CB.FACE.values()) <= set(ST.FACES) - {"minisystem"}
    assert len(set(CB.FACE.values())) >= 6, sorted(set(CB.FACE.values()))
    for brand in CB.IDS:
        assert F.brand_face(brand) == CB.FACE[brand]
    assert F.brand_face("no_such_brand") == F.LOGO_FACE


def test_the_ad_speaks_in_four_voices():
    """The brand's name in the brand's face, the slogan in a printed italic,
    the law in a plain notice face, the price card in the shop's."""
    assert F.COPY_FACE == ST.owned("print_italic")
    assert F.SMALL_FACE == ST.owned("notice") and F.WARN_FACE == ST.owned("notice_bold")
    assert F.PRICE_FACE == ST.owned("shop") and F.PRICE_NOTE_FACE == ST.owned("shop_small")
    assert F.LOGO_FACE == ST.owned("maker")


def test_the_lettering_stays_clear_of_the_warning_sticker():
    """1.49.0's bolder warning ran over a slogan's second line on the first
    cut. Measured on the art: every row of the sticker's box is sticker --
    its ground or its ink -- and never the slogan's cream."""
    facts = F.plan(0.88, 0.45, 1.5)["facts"]
    for i, brand in enumerate(CB.IDS):
        a = F.art(facts, brand, i, "k", "pull_knob", True)
        assert a["unset"] == [], (brand, a["unset"])
        x0, y0, x1, y1 = a["rects"]["header"]
        # the sticker is bottom right of the header: sample a column through
        # its left margin, which is its ground from top to bottom
        c = a["canvas"]
        col = [c.get(x1 - 8, y) for y in range(y1 - 30, y1 - 6)]
        assert all(min(p) > 200 for p in col), (brand, col[:3])


# --- a screen's letters are pixels ----------------------------------------------------


def test_pixel_text_is_the_pixel_face_at_a_whole_scale():
    im = PT.Img(200, 60, (0, 0, 0))
    box = im.pixel_text("INSERT CARD", (4, 4, 196, 56), (255, 255, 255))
    assert box is not None and im.unset == []
    w, h = box[2] - box[0], box[3] - box[1]
    k = h // len(PX.trim(PX.render("INSERT CARD", 1)))
    rows = PX.trim(PX.render("INSERT CARD", k))
    assert k >= 1 and (w, h) == (len(rows[0]), len(rows))
    # a pixel face has no grey edge: every pixel is ground or ink
    vals = set(int(v) for v in im.a[..., 0].ravel())
    assert vals == {0, 255}, sorted(vals)[:6]
    # and the next scale up would not have fitted
    assert PX.ink_width("INSERT CARD", k + 1) > 192 or len(PX.trim(PX.render("INSERT CARD", k + 1))) > 52


def test_pixel_text_that_does_not_fit_is_reported():
    im = PT.Img(20, 8, (0, 0, 0))
    assert im.pixel_text("SURCHARGE $1.50", (0, 0, 20, 8), (255, 255, 255)) is None
    assert im.unset == ["SURCHARGE $1.50"] and im.a.max() == 0.0


def test_the_tubes_are_set_in_pixels_and_the_cabinets_in_print():
    """Read off the source: the ATM's and the poker's CRT painters call
    `pixel_text`, and nothing else in either module does."""
    for mod, kind in ((A, "atm_crt"), (V, "vp_crt")):
        src = open(mod.__file__, encoding="utf-8").read()
        a = src.index(f'if kind == "{kind}":')
        b = src.index("return im.to_canvas()", a)
        assert "im.pixel_text(" in src[a:b] and "im.text(" not in src[a:b], kind
        assert "im.pixel_text(" not in src[:a] + src[b:], kind
    # every line of every tube sets, at every size the planners' tests use
    for w, d, h in ((0.5, 0.4, 1.2), (0.6, 0.55, 1.45), (0.75, 0.7, 1.65)):
        for v in range(4):
            for atlas, spec in A.plan(w, d, h, v)["tiles"].values():
                assert A.paint(spec).unset == [], (w, d, h, v, spec["kind"])
    for v in range(4):
        for atlas, spec in V.plan(0.65, 0.65, 1.75, v)["tiles"].values():
            assert V.paint(spec).unset == [], (v, spec["kind"])


def test_the_atm_s_legends_are_the_maker_s_and_its_sticker_the_shop_s():
    assert A.MAKER == ST.owned("maker") and A.MAKER_SMALL == ST.owned("maker_small")
    assert A.SHOP == ST.owned("shop")
    src = open(A.__file__, encoding="utf-8").read()
    assert '"highway' not in src, "a face named by hand: name its owner instead"
