"""Facade relief: articulation carved INTO the wall, not pasted onto it.

The rule this exists to satisfy is "no dressing in walkable space". It used to
be enforced by aiming proud covers; it could not be. A module's collider is
built from the same slab as its visual, so its collision volume ends exactly at
its face, and a cover standing 5 cm proud is by construction geometry outside
the collider that a body walks through. Inward put 546 panel fields in rooms.
Outward put the same 546 in the gaps between buildings, which are routes.

Carving inward has no direction to get wrong.
"""

from zoo_keeper.core import arch

W, D, H = 4.0, 0.35, 3.7


def _by_name(parts):
    return {n: (c, s) for n, c, s in parts}


def _volume_outside(parts, w, d, h):
    """Any part poking outside the authored (w, d, h) box, by how much."""
    lo, hi = arch.parts_bbox(parts)
    return max([-(lo[0] + w / 2.0), -(lo[1] + d / 2.0), -(lo[2] + h / 2.0),
                hi[0] - w / 2.0, hi[1] - d / 2.0, hi[2] - h / 2.0])


_DELCO = {'pier': 0.02, 'reveal': 0.015, 'base': 0.45, 'cap': 0.12, 'bay': 1.0}

def test_nothing_stands_proud_of_the_authored_depth():
    """THE WHOLE POINT. A cover was 1.2 cm to 10 cm outside this box; every
    part of a relief wall is inside it or exactly on it."""
    assert round(_volume_outside(arch.relief_parts(W, D, H), W, D, H), 9) <= 0


def test_the_outer_bbox_is_still_exactly_the_authored_dims():
    """Fit-to-exact-dims: Deli Counter never scales a module, so the union has
    to be the slot's box. The plinth alone guarantees it."""
    lo, hi = arch.parts_bbox(arch.relief_parts(W, D, H))
    assert [round(v, 6) for v in lo] == [-2.0, -0.175, -1.85]
    assert [round(v, 6) for v in hi] == [2.0, 0.175, 1.85]


def test_the_fields_are_recessed_on_both_faces():
    """Symmetric on purpose: a one-sided carve would need the module to know
    which face is the street, and it is instanced at slots of every
    orientation. That is the outward-direction bug baked into the mesh, where
    no per-slot transform can flip it."""
    parts = _by_name(arch.relief_parts(W, D, H))
    _c, s = parts["Field_0"]
    assert round(s[1], 6) == round(D - 2 * arch.RELIEF["reveal"], 6)
    assert parts["Field_0"][0][1] == 0.0          # still centred in depth
    assert parts["Pier_0"][1][1] == D             # piers span the full depth


def test_a_plinth_and_a_cap_break_the_wall_horizontally():
    parts = _by_name(arch.relief_parts(W, D, H))
    base_c, base_s = parts["Base"]
    assert base_s == (4.0, 0.35, 0.45)
    assert round(base_c[2] + base_s[2] / 2.0, 6) == round(-H / 2.0 + 0.45, 6)
    assert parts["Cap"][1][2] == 0.12


def test_the_end_piers_are_flush_not_centred_on_the_seam():
    """A pier centred on x = -w/2 hangs half its width into the neighbouring
    module and doubles at every seam -- the 6 cm overhang the old pilaster had
    at all 225 slots."""
    parts = _by_name(arch.relief_parts(W, D, H))
    c, s = parts["Pier_0"]
    assert round(c[0] - s[0] / 2.0, 6) == -2.0
    c, s = parts["Pier_2"]
    assert round(c[0] + s[0] / 2.0, 6) == 2.0


def test_bay_count_follows_the_width():
    def bays(w):
        return sum(1 for n, _c, _s in arch.relief_parts(w, D, H)
                   if n.startswith("Field"))
    assert bays(2.0) == 1
    assert bays(4.0) == 2
    assert bays(12.0) == 5


def test_a_wall_too_narrow_to_articulate_stays_one_panel():
    """Better a plain box than a rhythm made of slivers. A 0.5 m remainder is
    a piece of wall, not a colonnade."""
    p = arch.relief_parts(0.5, D, H)
    assert p == [("Panel", (0.0, 0.0, 0.0), (0.5, 0.35, 3.7))]


def test_zero_reveal_is_the_old_flat_wall_exactly():
    """The escape hatch has to be byte-identical, not merely similar --
    it is what a style turns relief off with."""
    p = arch.relief_parts(W, D, H, {"reveal": 0.0})
    assert p == arch.slab_parts(W, D, H, None)


def test_the_style_moves_the_rhythm():
    """One rhythm on every wall of every building is the failure mode this
    replaces. The numbers are per-style, not constants."""
    wide = arch.relief_parts(12.0, D, H, {"bay": 6.0})
    tight = arch.relief_parts(12.0, D, H, {"bay": 1.5})
    assert (sum(1 for n, _c, _s in wide if n.startswith("Field"))
            < sum(1 for n, _c, _s in tight if n.startswith("Field")))
    deep = _by_name(arch.relief_parts(W, D, H, {"reveal": 0.1}))
    assert round(deep["Field_0"][1][1], 6) == round(D - 0.2, 6)


def test_the_reveal_can_never_cut_through_the_wall():
    p = _by_name(arch.relief_parts(W, D, H, {"reveal": 9.0}))
    assert p["Field_0"][1][1] > 0.0


def test_collision_is_unchanged_because_it_comes_from_the_solid_slab():
    """The recipe collides from `slab_parts`, never from the relief. A notch
    in the collider is somewhere a player can stand inside a wall, and every
    build before this one has to keep the collision it had."""
    solid = arch.slab_parts(W, D, H, None)
    assert arch.collision_boxes(solid) == [((-2.0, -0.175, -1.85),
                                            (2.0, 0.175, 1.85))]


def test_deterministic():
    assert arch.relief_parts(W, D, H) == arch.relief_parts(W, D, H)


def test_a_seam_reads_exactly_like_a_bay_line():
    """Two abutting modules must not draw a wider pier than the wall's own
    bay lines. Flush end piers at FULL width made every module seam a
    double-width strip that appeared nowhere else on the facade -- so the
    relief added to disguise the module grid was drawing it, at exactly the
    module pitch. Half-width ends sum to one interior pier across a seam."""
    parts = _by_name(arch.relief_parts(W, D, H))
    interior = parts["Pier_1"][1][0]
    seam = parts["Pier_0"][1][0] + parts["Pier_2"][1][0]
    assert round(seam, 6) == round(interior, 6)


def test_every_field_on_a_run_is_the_same_width():
    """The eye compares field widths, not pier widths. With half-width ends
    the first and last field of a module match its interior fields, so a
    tiled run has ONE field width all the way along."""
    widths = {round(s[0], 6) for n, _c, s in arch.relief_parts(12.0, D, H)
              if n.startswith("Field")}
    assert len(widths) == 1


def test_a_delco_wall_module_actually_gets_a_bay():
    """delco shipped `bay: 2.4` against a 2.00 m module, so round(2.0/2.4)
    is 1: every wall in every build had two end piers and no bay, and the
    parameter was inert from the day it landed."""
    parts = arch.relief_parts(2.0, 0.30, 3.6, _DELCO)
    assert sum(1 for n, _c, _s in parts if n.startswith("Field")) >= 2
