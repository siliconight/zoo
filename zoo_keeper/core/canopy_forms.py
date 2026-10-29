"""The filling station canopy's shapes, pure (the factory's roadmap 324): the deck (`recipes/fuel_canopy`) and its
columns (`recipes/canopy_column`). The recipes build these boxes; the tests read them without Blender. Each recipe's
docstring says why its parts are where they are.
"""
from __future__ import annotations

from . import price_pylon_forms as PF

FASCIA_T = 0.10          # the fascia ring's thickness, inward from its face
STRIPE_PROUD = 0.004     # the stripe stands this far proud of the fascia; the module's sides are its outer faces
STRIPE_H = 0.08          # the stripe's height; it sits STRIPE_AT of the fascia's height up from its foot
STRIPE_AT = 0.62
SOFFIT_T = 0.04
CAP_T = 0.03
BURY = 0.004
SHY = 0.003

SOFFIT_RGB = (0.86, 0.86, 0.83)
CAP_RGB = (0.42, 0.43, 0.45)


def colours(variant):
    """(fascia, stripe) for the store's colourway ``variant``, 0..1."""
    field, rule, _ink = PF.COLOURWAYS[int(variant) % len(PF.COLOURWAYS)]
    return tuple(c / 255.0 for c in field), tuple(c / 255.0 for c in rule)


def boxes(w, d, h):
    """The deck's parts as (name, lo, hi) boxes, centre pivot -- pure, for the tests."""
    sp, ft = STRIPE_PROUD, FASCIA_T
    x1, y1, z0, z1 = w / 2.0, d / 2.0, -h / 2.0, h / 2.0
    fx, fy = x1 - sp, y1 - sp                      # the fascia's outer faces
    zs0 = z0 + h * STRIPE_AT - STRIPE_H / 2.0
    zs1 = zs0 + STRIPE_H
    out = [
        # the fascia ring: N and S the whole width, E and W between their backs
        ("Fascia", (-fx, fy - ft, z0), (fx, fy, z1)),
        ("Fascia", (-fx, -fy, z0), (fx, -fy + ft, z1)),
        ("FasciaEnds", (fx - ft, -fy + ft, z0), (fx, fy - ft, z1)),
        ("FasciaEnds", (-fx, -fy + ft, z0), (-fx + ft, fy - ft, z1)),
        # the stripe on its face, the module's side its outer face; N and S the whole width, E and W to their backs
        ("Stripe", (-x1, fy - BURY, zs0), (x1, y1, zs1)),
        ("Stripe", (-x1, -y1, zs0), (x1, -fy + BURY, zs1)),
        ("StripeEnds", (fx - BURY, -fy + BURY, zs0), (x1, fy - BURY, zs1)),
        ("StripeEnds", (-x1, -fy + BURY, zs0), (-fx + BURY, fy - BURY, zs1)),
        # the soffit, its underside the module's bottom, its edges ON the ring's inner faces: abutting, never
        # overlapping -- buried, its underside and the ring's would be one plane facing one way, a z-fight seen from
        # the forecourt
        ("Soffit", (-fx + ft, -fy + ft, z0), (fx - ft, fy - ft, z0 + SOFFIT_T)),
        # the roof cap, SHY under the ring's top, its edges on the ring's inner faces
        ("Cap", (-fx + ft, -fy + ft, z1 - SHY - CAP_T), (fx - ft, fy - ft, z1 - SHY)),
    ]
    return out


#: THE FACES NOBODY SEES, dropped by part (the house pattern, `geometry.drop_faces`): the E and W runs' ends stand
#: against the N and S runs' backs, and the soffit's and the cap's sides against the ring's inner faces. Kept, each
#: was a coincident pair in `tools/coplanar_census.py` (12 at the genome's smallest corner).
HIDDEN = {"FasciaEnds": "ends", "StripeEnds": "ends", "Soffit": "sides", "Cap": "sides"}


def hidden(part, normal) -> bool:
    """Whether a face of ``part`` with outward ``normal`` stands against another part."""
    nx, ny, nz = normal
    rule = HIDDEN.get(part)
    if rule == "ends":
        return abs(ny) > 0.9
    if rule == "sides":
        return abs(nz) < 0.1
    return False



GUARD_H = 0.9            # a forecourt column's concrete guard: about a bumper's height and a half
SHAFT = 0.6              # the shaft's side, as a share of the slot's narrower side

GUARD_RGB = (0.88, 0.72, 0.16)
SHAFT_RGB = (0.86, 0.86, 0.83)


def column_boxes(w, d, h):
    """The column's parts as (name, lo, hi), centre pivot -- pure, for the tests."""
    z0, z1 = -h / 2.0, h / 2.0
    gh = min(GUARD_H, h / 5.0)
    s = min(w, d) * SHAFT / 2.0
    return [("Guard", (-w / 2.0, -d / 2.0, z0), (w / 2.0, d / 2.0, z0 + gh)),
            ("Shaft", (-s, -s, z0 + gh - BURY), (s, s, z1))]


