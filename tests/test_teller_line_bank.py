"""teller_line's bank form (1.137.0): the nameboard (pure -- no Blender).

The board names the bank over the line and numbers each window; these hold
that every word on it sets at the size it is painted (through `card_art`'s
own dispatch), that it stays inside the module's envelope on the header's
public face, and that its threshold is the one `teller_line_forms` measured.
"""
import pytest

from zoo_keeper.core import card_art as CA
from zoo_keeper.core import genome
from zoo_keeper.core import kit
from zoo_keeper.core import storefront_names as SN
from zoo_keeper.core import teller_line_forms as TF
from zoo_keeper.recipes._bays import bays

#: the genome's corners and lines between: one bay, two, four, six; and the
#: three the library's banks build (Deli Counter 0.282.0's slots)
LINES = [(1.0, 0.3, 2.0), (2.0, 0.5, 3.0), (2.01, 0.5, 2.0), (7.5, 0.6, 3.2), (12.0, 1.2, 4.0),
         (12.0, 0.8, 2.4), (10.0, 0.9, 2.4), (8.0, 0.8, 2.4)]


def _board(w, d, h, variant=0):
    g = genome.load_species("teller_line")
    p = {k: (v["default"] if isinstance(v, dict) else v) for k, v in g["params"].items()}
    counter_h = min(p["counter_h"], h * 0.6)
    post = min(p["post"], w * 0.3)
    header = TF.header_of(min(p["header"], (h - counter_h) * 0.5), h, counter_h)
    runs = bays(w, p["bay_max"])
    return TF.bank_board(w, d, h, post, header, runs, variant), runs, post, header


def _numbered(h_m, said):
    return {"kind": "teller_board", "w_m": 1.78, "h_m": h_m, "text": said["text"], "colours": said["colours"],
            "voice": "shop", "numbers": [(0.25, "8"), (0.75, "9")], "bay_m": 0.89}


def test_the_genome_offers_the_bank_form_and_a_name_a_variant():
    g = genome.load_species("teller_line")
    assert g["params"]["form"] == list(TF.FORMS)
    assert g["module_variants"] == TF.VARIANTS == 16
    got, why = kit.honour_dressing({"form": "bank", "variant": 15}, "teller_line")
    assert got == {"form": "bank", "stock": None, "variant": 15} and not why


def test_a_bank_line_reads_its_door_sign():
    """`variant_for` is the variant whose name and colours `sign_for` puts
    over the door -- for every bank in the library and a run of made-up ones."""
    names = ["bank_branch_a0%d" % i for i in range(1, 8)] + ["lf_bank_block_001_%d bank" % s for s in range(40)]
    seen = set()
    for business in names:
        sign = SN.sign_for(business)
        assert sign["kind"] == "bank", business
        v = TF.variant_for(business)
        assert 0 <= v < TF.VARIANTS
        said = TF.bank_said(v)
        assert said["text"] == sign["text"] and tuple(said["colours"]) == tuple(sign["colours"]), business
        seen.add(v)
    assert len(seen) > 8, seen


@pytest.mark.parametrize("w,d,h", LINES)
@pytest.mark.parametrize("variant", range(16))
def test_every_word_on_the_board_sets(w, d, h, variant):
    (_prims, tiles), runs, _post, _header = _board(w, d, h, variant)
    board = tiles["board"]
    assert board["text"] == TF.bank_names()[variant % 4]
    assert [n for _f, n in board["numbers"]] == ([] if len(runs) < 2 else [str(i + 1) for i in range(len(runs))])
    c = CA.paint(board)
    assert not c.unset, (w, h, variant, c.unset)


@pytest.mark.parametrize("w,d,h", LINES)
def test_the_board_is_inside_the_envelope_on_the_public_face(w, d, h):
    (prims, tiles), runs, post, header = _board(w, d, h)
    art, rim = prims
    for q in prims:
        for x, y, z in q["verts"]:
            assert -w / 2 + post < x < w / 2 - post, (q["part"], x)
            assert -d / 2 - 1e-9 <= y <= -d / 2 + TF.BOARD_T + 1e-9, (q["part"], y)
            assert h / 2 - header < z < h / 2, (q["part"], z)
    # the art faces the trays, on the front plane, and is the rim's front
    assert all(abs(y + d / 2) < 1e-9 for _x, y, _z in art["verts"])
    assert {(x, z) for x, _y, z in art["verts"]} == {(x, z) for x, y, z in rim["verts"] if abs(y + d / 2) < 1e-9}
    # no back face: the rim keeps its bottom, top and ends
    assert len(rim["faces"]) == 4
    # each number sits over its own bay
    x0 = -w / 2 + post + TF.BOARD_INSET
    for (frac, _n), (bx, _bw) in zip(tiles["board"]["numbers"], runs):
        assert abs(x0 + frac * tiles["board"]["w_m"] - bx) < 1e-9


def test_a_board_too_short_for_both_bands_carries_the_name_alone():
    # unreachable inside the genome's ranges, which never leave a board under
    # NUMBERED_MIN; held here so the fallback is not a branch nobody runs
    runs = bays(4.0, 2.0)
    _prims, tiles = TF.bank_board(4.0, 0.5, 3.0, 0.1, TF.NUMBERED_MIN, runs, 0)
    assert tiles["board"]["numbers"] == []
    assert not CA.paint(tiles["board"]).unset
    _prims, tiles = TF.bank_board(4.0, 0.5, 3.0, 0.1, TF.NUMBERED_MIN + 2 * TF.BOARD_INSET, runs, 0)
    assert len(tiles["board"]["numbers"]) == 2


@pytest.mark.parametrize("variant", range(4))
def test_the_measured_threshold_is_the_one_paint_keeps(variant):
    """`NUMBERED_MIN` is where the narrowest numbered board first sets every
    word; a centimetre under it, one does not."""
    said = TF.bank_said(variant)
    assert not CA.paint(_numbered(TF.NUMBERED_MIN, said)).unset
    assert CA.paint(_numbered(TF.NUMBERED_MIN - 0.01, said)).unset


def test_the_bank_header_is_raised_but_never_past_half_the_opening():
    assert TF.header_of(0.2, 3.0, 1.1) == TF.BANK_HEADER
    assert TF.header_of(0.2, 2.0, 1.2) == pytest.approx(0.4)
    assert TF.header_of(0.5, 3.0, 1.1) == 0.5


def test_a_middle_post_stops_inside_the_header_and_under_the_board():
    """At 0.02 a middle post's front ran 1 cm up the board's face, the one
    coincident pair the bank form's first census found."""
    assert 0.0 < TF.POST_INTO_HEADER < TF.BOARD_INSET

