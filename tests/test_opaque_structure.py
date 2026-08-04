"""A structural slab is never see-through. The pane still is.

Measured on the shipped build, `wall_rockay_02_w200.glb` carried one material:

    M_Skin_glass_rockay   BLEND  alpha 0.50  doubleSided  used by 5 node(s)
        Wall_Base   Wall_Cap   Wall_Pier_0   Wall_Field_0

The entire carved wall, built out of window glass. Deli Counter had authored
those slots as a glass curtain-wall material zone, `glass` is a legal kind, and
Zoo agreed.

Not a look bug: the collider is built from the same slab and stays solid, so
the wall stops a body and not an eye. On a game whose tactical layer IS
sightlines, that is a wall you scout enemies through -- and `sightlines.py` is
analysing a building nobody renders.
"""

from zoo_keeper.core import dna, skins


def test_the_opaque_counterpart_is_a_real_kind():
    """`glass_facade` ships no Pixelcoat transparency hint, which is what makes
    it opaque. If it ever stopped being a known kind this map would silently
    hand `dna` a material nothing can resolve."""
    for kind in dna.OPAQUE_FOR.values():
        assert kind in skins.KNOWN_KINDS


def test_glass_is_the_only_see_through_kind_today():
    """A second translucent kind must join OPAQUE_FOR rather than reopen the
    hole. This fails loudly when one is added, which is the point."""
    assert set(dna.OPAQUE_FOR) == {"glass"}


def test_every_structural_kind_maps_to_itself():
    """The substitution must touch nothing else. Concrete stays concrete."""
    for kind in skins.KNOWN_KINDS:
        if kind == "glass":
            continue
        assert dna.OPAQUE_FOR.get(kind, kind) == kind


def test_a_glass_wall_slot_becomes_facade_glass():
    assert dna.OPAQUE_FOR.get("glass") == "glass_facade"


def test_the_pane_kind_is_separate_from_the_slab_kind():
    """The window's own glazing rides `plan['glazing_kind']`, not
    `plan['material']`, so making the FRAME opaque leaves the GLASS alone."""
    assert "glazing_kind" not in dna.OPAQUE_FOR
