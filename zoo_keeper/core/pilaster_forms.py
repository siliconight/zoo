"""wall_pilaster's shape, pure: the boxes `recipes/wall_pilaster.py` builds and the faces it drops (1.150.0).

A flat stone pier standing a hand proud of a civic wall, ground to cornice -- Deli Counter (>= 0.294.0) chooses where,
from the wall's openings, and gives it a collider, so it is solid where a body walks. A plinth block at its foot, a
shaft set back from it, a cap block under the cornice; one material, the building's stone trim
(`dressing.STONE_TRIM_KIND`, `STONE_TRIM_COLOR`), so it reads as one stone with the string courses and the quoins.

THE ENVELOPE IS THE SLOT'S, EXACTLY: plinth and cap span the slot's full width and depth; the shaft is `SHAFT_INSET`
narrower each side and stands `SHAFT_BACK` behind their front, its back on the slot's back face (the wall). It ABUTS
the plinth's top and the cap's bottom, so its own top and bottom faces are hidden and dropped: no two faces coincide.
Frame: x across the pier, z up, centre pivot; the FRONT is local -Y, as every Zoo prop's is (Deli Counter turns a
slot's +Y onto its bearing), so the wall is the +Y face.
"""
from __future__ import annotations

PLINTH_H = 0.45
PLINTH_MAX = 0.12          # of the height, for a short pier
CAP_H = 0.25
CAP_MAX = 0.06
SHAFT_INSET = 0.03
SHAFT_BACK = 0.02


def boxes(w: float, d: float, h: float):
    """``[(name, lo, hi)]`` in the centre-pivot frame."""
    hw, hd, hh = w / 2.0, d / 2.0, h / 2.0
    ph = min(PLINTH_H, h * PLINTH_MAX)
    ch = min(CAP_H, h * CAP_MAX)
    back = min(SHAFT_BACK, d * 0.4)
    inset = min(SHAFT_INSET, w * 0.2)
    return [
        ("Plinth", (-hw, -hd, -hh), (hw, hd, -hh + ph)),
        ("Shaft", (-hw + inset, -hd + back, -hh + ph), (hw - inset, hd, hh - ch)),
        ("Cap", (-hw, -hd, hh - ch), (hw, hd, hh)),
    ]


def hidden(part: str, normal) -> bool:
    """The shaft's top and bottom: the cap's underside and the plinth's top cover them."""
    return part == "Shaft" and abs(normal[2]) > 0.9
