"""Where the streetlight's lamp point is, and who else depends on it.

Lot 0.79.0 stopped deriving street lighting from the path graph and started
deriving it from the POLES `site_furniture` stands, so every exterior light
sits on the lamp it appears to come from. That made one number cross the
repo boundary: how far below the top of an exact-fit streetlight module the
emissive lens sits. Lot carries it as `STREETLIGHT_LENS_DROP = 0.175` and
places its light there; a light at the module's top would be inside the
shoebox head, and a shadow-casting head would occlude its own spot.

The arithmetic, from `recipes/streetlight.py`, in the module's local frame
for the SLOT placement (`fit_exact`, which is how the site kit stands
these):

    top  = h / 2 - 0.18          the pole's top
    head = box at top + 0.10, 0.16 thick  -> head top = top + 0.18 = h / 2
    lens = box at top + 0.015, 0.02 thick -> lens underside = top + 0.005

    module top - lens underside = h/2 - (h/2 - 0.18 + 0.005) = 0.175

WHAT THIS TEST IS. A SOURCE check, not a measurement -- it asserts the
literals are still what the arithmetic above was read off, so a change to
the head or the lens fails here rather than silently burying a site's
street lighting inside 48 shoeboxes. The measurement belongs in a Blender
run; this is the cheap detector that runs everywhere, which is the same
distinction the triangle budgets in the genomes make.
"""
import os

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "streetlight.py")

#: What Lot places its light at, below the module's top. Stated here as a
#: literal on purpose: if the recipe moves and this file is edited to match
#: without Lot being edited too, the cross-repo test below still fails.
LENS_DROP = 0.175


def _src():
    with open(_RECIPE, encoding="utf-8") as fh:
        return fh.read()


def test_the_lamp_point_is_where_lot_puts_its_light():
    src = _src()
    # the pole top in an exact fit
    assert "top = h / 2.0 - (0.18 if exact else 0.0)" in src, (
        "the pole top moved; Lot's STREETLIGHT_LENS_DROP is derived from it")
    # the head, filling the last 0.18 up to the module's top
    assert "geometry.add_box(bm, (0.0, 0.0, top + 0.02 + 0.08), (w, d, 0.16))" in src, (
        "the shoebox head moved; a light at the module top would be inside it")
    # the lens, protruding below the head
    assert "geometry.add_box(bm, (0.0, 0.0, top + 0.015)," in src, (
        "the lens moved; Lot places its light under the lens")
    # and the number those three make
    assert abs((0.18 - 0.005) - LENS_DROP) < 1e-9


def test_lot_agrees_with_this_number():
    """The other half of the coupling, checked where both repos are present.

    Zoo alone cannot prove Lot is right, and a standalone Zoo checkout has
    no sibling to read -- so this reads `../lot/lot.py` when the factory
    workspace is around it and says nothing when it is not. It is a check
    that CAN fail in the place the mismatch would actually happen, which is
    this workspace.
    """
    lot_py = os.path.join(os.path.dirname(_ZOO), "lot", "lot.py")
    if not os.path.exists(lot_py):
        return
    with open(lot_py, encoding="utf-8") as fh:
        lot_src = fh.read()
    assert "STREETLIGHT_LENS_DROP = %s" % LENS_DROP in lot_src, (
        "lot.py's STREETLIGHT_LENS_DROP no longer matches this recipe's lens")
