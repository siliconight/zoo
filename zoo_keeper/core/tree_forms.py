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
#:   cluster:      leaf cluster size as a fraction of w (a faceted blob at
#:                 every branch and twig tip)
#:   crown:        the envelope the tips are pushed toward:
#:                 "oval" (widest at mid height), "pyramid" (widest low),
#:                 "vase" (widest high), "flat" (widest high, flat top)
FORMS = {
    # Acer rubrum -- the commonest Delco street tree. One trunk, branches
    # ascending at 30-45 degrees, an oval crown of even rounded clusters.
    "red_maple": {"first_branch": 0.32, "leader": 0.72, "branches": 6,
                  "angles": (48, 40, 30), "reach": 1.0, "twigs": 2,
                  "cluster": 0.30, "crown": "oval"},
    # Quercus palustris -- a strong central leader to the top, lower limbs
    # DROOPING, middle level, upper rising: a pyramid.
    "pin_oak": {"first_branch": 0.30, "leader": 0.95, "branches": 7,
                "angles": (105, 85, 45), "reach": 1.0, "twigs": 2,
                "cluster": 0.26, "crown": "pyramid"},
    # Gleditsia triacanthos -- open and spreading, few limbs, fine twigs,
    # a thin flat-topped crown you can see the sky through.
    "honey_locust": {"first_branch": 0.36, "leader": 0.60, "branches": 5,
                     "angles": (70, 60, 50), "reach": 1.0, "twigs": 3,
                     "cluster": 0.20, "crown": "flat"},
    # Platanus x acerifolia -- massive limbs forking low, a broad crown of
    # big masses.
    "london_plane": {"first_branch": 0.30, "leader": 0.55, "branches": 5,
                     "angles": (65, 50, 40), "reach": 1.0, "twigs": 2,
                     "cluster": 0.36, "crown": "oval"},
    # Pyrus calleryana 'Bradford' -- every branch rising tight from one
    # point, a dense narrow oval; the one that splits in an ice storm.
    "callery_pear": {"first_branch": 0.28, "leader": 0.80, "branches": 8,
                     "angles": (35, 28, 20), "reach": 0.9, "twigs": 2,
                     "cluster": 0.28, "crown": "vase"},
}

DEFAULT = "red_maple"


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
