"""night_drop's measures (1.138.0): the plate, the hood, the door and the lettering, and where the lettering
stands. Pure -- no Blender -- so the tests can set the lettering at every size the genome allows;
`recipes/night_drop.py` builds from these.
"""
from __future__ import annotations

PLATE_T = 0.02           # the plate's thickness, at the wall
MARGIN = 0.03            # the label and the hood this far in from the plate's edges
#: the label's height: NIGHT DEPOSITORY sets on two lines at 0.18 m and a 0.52 m width in the shop voice (`paint`'s
#: 5 cm least cap), and not at 0.16; 0.20 is that and a margin
LABEL_H = 0.20
LABEL_T = 0.006          # the label panel's stand off the plate
HOOD_W_F = 0.72          # the hood's width, a fraction of the plate's
HOOD_H = 0.30
HOOD_Z_F = -0.08         # the hood's centre, a fraction of the height, below the middle
DOOR_IN = 0.03           # the chute door's front this far behind the module's front: the handle stands in front of it
DOOR_T = 0.008
DOOR_MARGIN = 0.035      # the door inside the hood's face
HANDLE = (0.26, 0.022)   # the pull's length and its bar's section
BURY = 0.004
LOCK_R = 0.018
LOCK_PROUD = 0.012

PLATE_RGB = (0.62, 0.63, 0.64)
HOOD_RGB = (0.52, 0.53, 0.55)
DOOR_RGB = (0.30, 0.31, 0.33)
HANDLE_RGB = (0.78, 0.78, 0.76)
LOCK_RGB = (0.70, 0.55, 0.25)
#: the lettering: a brushed plate with black letters outlined in the rule
LABEL_COLOURS = ((168, 170, 172), (92, 94, 98), (18, 18, 20))
LABEL_TEXT = "NIGHT DEPOSITORY"


def label_box(w, d, h):
    """``(x0, x1, z0, z1, y_front)`` of the lettering's panel."""
    x0, x1 = -w / 2.0 + MARGIN, w / 2.0 - MARGIN
    z1 = h / 2.0 - MARGIN
    plate_front = d / 2.0 - PLATE_T
    return x0, x1, z1 - LABEL_H, z1, plate_front - LABEL_T
