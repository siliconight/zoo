"""The forms of the street trees a Delaware County street actually plants.

Roadmap 153, the tree. The walker, 2026-09-13: "trees usually have
multiple branches that stem from the trunk and those branches have twigs
and depending on what species of tree determines how that looks." A tree
is a trunk, primary branches leaving it at an angle the species sets,
twigs off those, and leaf mass at the tips -- and the SILHOUETTE is the
species: a pin oak's lower limbs droop and its upper ones rise, a callery
pear's all rise tight, a honey locust's spread open and thin.

Each row is one species as a street tree of about 6 m (a young planting
in a kerb grate), with the branch angles in degrees FROM VERTICAL (0 = up,
90 = level, more than 90 = drooping), the crown envelope as fractions of
the slot, and the leaf clusters' size. Numbers are what a photograph of
the species shows, not what a lane needs; the recipe scales the built
tree to the slot's exact (w, d, h), so a row shapes and never sizes.

Pure: a dict, read by `recipes/street_tree.py`; testable without Blender.
"""
from __future__ import annotations

import math

#: THE LEAF PALETTE, and why it is indexed rather than random. A row of
#: street trees in October is not one colour: the walker's frames show
#: green, gold and orange within a few metres of each other. A recipe that
#: picked a colour from its wear stream would give every INSTANCE of one
#: module the same leaf anyway -- Deli Counter builds a module once per
#: stem and Lot instances it -- so the colour rides the module's STYLE
#: index, which is already part of the stem. Lot plants style 1, 2 or 3
#: and gets three trees.
LEAF_PALETTE = (
    (0.26, 0.42, 0.18),        # 1: high summer
    (0.55, 0.46, 0.13),        # 2: turning, gold
    (0.58, 0.29, 0.11),        # 3: turned, orange-red
    (0.34, 0.44, 0.16),        # 4: a late green
)


def leaf_color(style: int) -> list:
    """The leaf colour for a module built at ``style`` (1-based)."""
    i = (int(style) - 1) % len(LEAF_PALETTE)
    return list(LEAF_PALETTE[i])


#: name -> form. Fields:
#:   first_branch: height of the lowest primary branch, as a fraction of h
#:   leader:       how far up the trunk continues as a central leader, of h
#:                 (a pin oak keeps one to the top; a plane tree forks)
#:   branches:     how many primary branches
#:   angles:       (low, mid, high) branch angle from vertical, degrees, for
#:                 the lowest, the middle and the highest branch; between
#:                 them the angle is interpolated
#:   reach:        how far the outermost tip reaches, as a fraction of w/2
#:   twigs:        twigs per branch (each forks off the branch's outer half)
#:   twiglets:     how many finer shoots each twig carries; the third order
#:                 is what makes a crown read as tracery rather than blobs
#:   cluster:      leaf cluster size as a fraction of w (a faceted blob at
#:                 every branch and twig tip)
#:   crown:        the envelope the tips are pushed toward:
#:                 "oval" (widest at mid height), "pyramid" (widest low),
#:                 "vase" (widest high), "flat" (widest high, flat top)
FORMS = {
    # Acer rubrum -- the commonest Delco street tree. One trunk, branches
    # ascending at 30-45 degrees, an oval crown of even rounded clusters.
    "red_maple": {"first_branch": 0.34, "leader": 0.74, "branches": 8,
                  "angles": (48, 40, 30), "reach": 1.0, "twigs": 3,
                  "twiglets": 2, "cluster": 0.20, "crown": "oval"},
    # Quercus palustris -- a strong central leader to the top, lower limbs
    # DROOPING, middle level, upper rising: a pyramid.
    "pin_oak": {"first_branch": 0.30, "leader": 0.95, "branches": 9,
                "angles": (105, 85, 45), "reach": 1.0, "twigs": 3,
                "twiglets": 2, "cluster": 0.18, "crown": "pyramid"},
    # Gleditsia triacanthos -- open and spreading, few limbs, fine twigs,
    # a thin flat-topped crown you can see the sky through.
    "honey_locust": {"first_branch": 0.38, "leader": 0.62, "branches": 6,
                     "angles": (70, 60, 50), "reach": 1.0, "twigs": 4,
                     "twiglets": 2, "cluster": 0.15, "crown": "flat"},
    # Platanus x acerifolia -- massive limbs forking low, a broad crown of
    # big masses.
    "london_plane": {"first_branch": 0.30, "leader": 0.58, "branches": 6,
                     "angles": (65, 50, 40), "reach": 1.0, "twigs": 3,
                     "twiglets": 2, "cluster": 0.24, "crown": "oval"},
    # Pyrus calleryana 'Bradford' -- every branch rising tight from one
    # point, a dense narrow oval; the one that splits in an ice storm.
    "callery_pear": {"first_branch": 0.28, "leader": 0.82, "branches": 10,
                     "angles": (35, 28, 20), "reach": 0.9, "twigs": 3,
                     "twiglets": 2, "cluster": 0.17, "crown": "vase"},
}

DEFAULT = "red_maple"

#: WHAT A TREE COSTS, DERIVED RATHER THAN PINNED. `street_tree` builds one
#: grate box, one limb per trunk/leader/branch/twig and one leaf cluster per
#: tip; a box triangulates to 12, a cluster is three boxes (36), and a
#: 6-segment capped cylinder is 12 side + 8 cap = 20 before the bevel, 72
#: after it. Measured across the five species built 2026-09-13 -- 1,812 /
#: 2,136 / 2,352 / 2,460 / 2,784 tris for 16 / 19 / 21 / 22 / 25 tips --
#: `84 + 108 * tips` reproduces every one of them exactly, so the budget a
#: genome carries is this formula and not a number somebody chose. A build
#: that warns against it has changed its piece count or its bevel, which is
#: worth knowing.
TRIS_GRATE = 12
TRIS_LIMB = 72             # trunk, leader, primary branch: a cylinder
TRIS_TWIG = 12             # a twig or a twiglet: a thin box (`_stick`)
TRIS_CLUSTER = 36          # a branch-tip mass: three boxes
TRIS_SMALL_CLUSTER = 12    # a twig's mass: one tapered box
#: Headroom on the derived count: one cluster and one limb, so a recipe that
#: grows a single extra fork reports rather than warns.
TRIS_HEADROOM = TRIS_LIMB + TRIS_CLUSTER


def twiglets(f: dict) -> int:
    return int(f.get("twiglets", 0))


def big_tips(f: dict) -> int:
    """Leaf masses built as three boxes: one per branch tip, one on the
    leader. These are the masses that carry the crown's silhouette."""
    return 1 + int(f["branches"])


def small_tips(f: dict) -> int:
    """Leaf masses built as ONE tapered box: where each branch's twigs fork,
    at every twig tip and at every twiglet tip. Many and cheap, which is
    what a crown of tracery costs."""
    b, t = int(f["branches"]), int(f["twigs"])
    return b * (1 + t + t * twiglets(f))


def tips(f: dict) -> int:
    """Every leaf mass on a tree of form ``f``."""
    return big_tips(f) + small_tips(f)


def limbs(f: dict) -> int:
    """CYLINDERS: the trunk, the leader and one per primary branch."""
    return 2 + int(f["branches"])


def sticks(f: dict) -> int:
    """THIN BOXES: one per twig and one per twiglet. A twig at two
    centimetres does not need a cylinder, and a crown carrying eighty of
    them cannot afford one."""
    b, t = int(f["branches"]), int(f["twigs"])
    return b * t * (1 + twiglets(f))


def tri_count(f: dict) -> int:
    """Triangles `street_tree` builds for form ``f`` -- the derivation above."""
    return (TRIS_GRATE + TRIS_LIMB * limbs(f) + TRIS_TWIG * sticks(f)
            + TRIS_CLUSTER * big_tips(f) + TRIS_SMALL_CLUSTER * small_tips(f))


def tri_budget(f: dict) -> int:
    """The genome's `tris_lod0` for form ``f``: the derived count plus one
    fork's headroom, rounded up to a round fifty."""
    return int(math.ceil((tri_count(f) + TRIS_HEADROOM) / 50.0) * 50)


def form(name: str | None) -> dict:
    """The form for ``name``, or the default's when the name is unknown --
    a tree the genome could not name is still a tree, and the default is
    the commonest one on the street."""
    return dict(FORMS.get(str(name or DEFAULT), FORMS[DEFAULT]))


def branch_angle(f: dict, k: int, n: int) -> float:
    """Degrees from vertical for branch ``k`` of ``n`` (0 lowest): the
    form's (low, mid, high) interpolated along the trunk."""
    lo, mid, hi = f["angles"]
    if n <= 1:
        return float(mid)
    t = k / (n - 1)
    if t < 0.5:
        return lo + (mid - lo) * (t / 0.5)
    return mid + (hi - mid) * ((t - 0.5) / 0.5)


def envelope(f: dict, z01: float) -> float:
    """How far (0..1 of the half width) the crown reaches at height ``z01``
    (0 at the first branch, 1 at the top), by the form's crown shape."""
    shape = f.get("crown", "oval")
    if shape == "pyramid":
        return 1.0 - 0.75 * z01
    if shape == "vase":
        return 0.45 + 0.55 * z01
    if shape == "flat":
        return 0.6 + 0.4 * min(1.0, z01 * 1.5)
    # oval: widest at mid height
    return 0.55 + 0.45 * (1.0 - abs(2.0 * z01 - 1.0))
