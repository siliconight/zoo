"""Shutters: the parts of a lit screen that come and go (1.45.0).

The walker, 2026-10-02: the lit screens are "just fixed with nothing
dynamic/alive about them". A screen's picture is one painted image and stays
one; a SHUTTER is a black quad a hair proud of it, over one part of the
picture, that is OPEN for a stated fraction of a stated period. Closed, the
part is hidden; open, the shutter is not drawn. A dealt card, a line that
flashes, a cursor: each is a part of the picture and a shutter over it.

Pure Python. A planner calls `over` and puts the prim in its list with the
rest; `recipes/_card_atlas.build_shutters` builds every prim carrying a
``shutter`` into one object.

THE CONTRACT WITH WHOEVER DRAWS IT (Level Factory's import, 0.127.0):

  * the material's name BEGINS `MATERIAL` and it is exported fully
    transparent, so a consumer that does nothing shows the screen as painted;
    its BASE COLOUR is the colour a closed shutter is -- the screen's own
    background, so a hidden card is empty screen and not a black hole (the
    first frames: black blocks on the poker's blue tube);
  * UV  = (open_from, open_to), fractions of the period, 0 <= from < to <= 1;
  * UV2 = (period_s, phase_s);
  * the shutter is OPEN while ``fract((t + phase_s) / period_s)`` is in
    ``[open_from, open_to)``, and the closed colour otherwise.

KNOWN: the closed colour is drawn unlit, so on a machine with its power cut
a closed shutter is still its dark background colour where the dead screen
round it is the room's light on its picture. Both are dark; they are not the
same dark.
"""
from __future__ import annotations

from . import prims as P

MATERIAL = "M_Shutter_Screen"
MAT = "shutter"


def material_name(rgb):
    """The shutter material for a screen whose background is ``rgb`` (0-255):
    `MATERIAL` and the colour, so two machines built in one session do not
    share one material and one colour."""
    return "%s_%02x%02x%02x" % ((MATERIAL,) + tuple(int(c) for c in rgb))
#: Proud of the screen: past `prims.coincident_pairs`' 2 mm, so the two are
#: not one plane, and little enough to stay inside the screen's recess.
PROUD = 0.003


def over(part, screen, rect, schedule, proud=PROUD):
    """A shutter over part of a screen.

    ``screen`` is the screen quad's corners -- bottom-left, bottom-right,
    top-right, top-left as the viewer sees it. ``rect`` is ``(u0, v0, u1,
    v1)``, fractions of the screen, v UP. ``schedule`` is ``(open_from,
    open_to, period_s, phase_s)``. ``proud`` (1.46.0) is how far off that
    plane it stands: more than `PROUD` for a tube whose face bulges."""
    u0, v0, u1, v1 = rect
    a, b, period, phase = schedule
    if not (0.0 <= u0 < u1 <= 1.0 and 0.0 <= v0 < v1 <= 1.0):
        raise ValueError(f"shutter {part}: rect {rect!r} is not inside its screen")
    if not (0.0 <= a < b <= 1.0 and period > 0.0):
        raise ValueError(f"shutter {part}: schedule {schedule!r}")
    bl, br, _tr, tl = screen
    ex = [br[k] - bl[k] for k in range(3)]
    ey = [tl[k] - bl[k] for k in range(3)]
    n = (ex[1] * ey[2] - ex[2] * ey[1], ex[2] * ey[0] - ex[0] * ey[2], ex[0] * ey[1] - ex[1] * ey[0])
    size = sum(c * c for c in n) ** 0.5
    n = [c / size * float(proud) for c in n]

    def at(u, v):
        return tuple(bl[k] + ex[k] * u + ey[k] * v + n[k] for k in range(3))
    p = P.mesh(part, MAT, [at(u0, v0), at(u1, v0), at(u1, v1), at(u0, v1)], [(0, 1, 2, 3)])
    p["shutter"] = (float(a), float(b), float(period), float(phase))
    return p


def is_open(schedule, t):
    """Is a shutter with ``schedule`` open at time ``t`` seconds?"""
    a, b, period, phase = schedule
    f = ((t + phase) / period) % 1.0
    return a <= f < b
