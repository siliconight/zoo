"""Which way a machine's faces point, read off the names `machine_parts` gives
them (1.46.0). The ATM, the video-poker cabinet and both registers are built
from the same parts, so the three suites ask this one question one way.

A face wound backwards renders as nothing and nothing else says why, which is
why each suite has always carried this check; a part this file does not
recognise FAILS rather than passing unexamined.
"""
from __future__ import annotations

_S = 0.5 ** 0.5

#: A suffix a part's name ends with -> the exact direction its first face
#: points. Frame: metres, Z up, the player at -Y.
EXACT = (
    ("_ChamferFR", (_S, -_S, 0.0)), ("_ChamferBR", (_S, _S, 0.0)),
    ("_ChamferBL", (-_S, _S, 0.0)), ("_ChamferFL", (-_S, -_S, 0.0)),
    ("_front", (0.0, -1.0, 0.0)), ("_back", (0.0, 1.0, 0.0)),
    ("_left", (-1.0, 0.0, 0.0)), ("_right", (1.0, 0.0, 0.0)),
    ("_top", (0.0, 0.0, 1.0)), ("_under", (0.0, 0.0, -1.0)), ("Under", (0.0, 0.0, -1.0)),
    ("_bottom", (0.0, 0.0, -1.0)),
    ("_Bezel_B", (0.0, -1.0, 0.0)), ("_Bezel_T", (0.0, -1.0, 0.0)),
    ("_Bezel_L", (0.0, -1.0, 0.0)), ("_Bezel_R", (0.0, -1.0, 0.0)),
    ("SideL", (-1.0, 0.0, 0.0)), ("SideR", (1.0, 0.0, 0.0)),
    ("_Fascia", (0.0, -1.0, 0.0)), ("_Belly", (0.0, -1.0, 0.0)), ("_Sign", (0.0, -1.0, 0.0)),
    ("Shutter", (0.0, -1.0, 0.0)),
)
#: A surround's four faces slope: each looks at the player AND across the
#: opening. (suffix, axis, sign) on top of "toward -Y".
WELLS = (("_Well_B", 2, 1.0), ("_Well_T", 2, -1.0), ("_Well_L", 0, 1.0), ("_Well_R", 0, -1.0))


def normal(p, k=0):
    a, b, c = (p["verts"][i] for i in p["faces"][k][:3])
    u = [b[i] - a[i] for i in range(3)]
    w = [c[i] - a[i] for i in range(3)]
    n = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
    size = sum(x * x for x in n) ** 0.5
    return tuple(x / size for x in n)


def check(prims, sloped=(), screens=()):
    """Assert every prim's first face points where its name says. ``sloped``
    names the parts on a deck that looks up and at the player (the deck and
    whatever stands on it, whose first face is its top -- a numbered run of
    parts by its stem); ``screens`` the
    tubes, which bulge and so only lean toward -Y. Returns the set of kinds
    seen, for a caller to hold what it expects to have checked."""
    seen = set()
    for p in prims:
        part, n = p["part"], normal(p)
        if part in sloped or part.rstrip("0123456789") in sloped:
            assert n[1] < -0.3 and n[2] > 0.3, (part, n)
            seen.add("sloped")
            continue
        if part in screens:
            assert n[1] < -0.9, (part, n)
            seen.add("Screen")
            continue
        well = next((w for w in WELLS if part.endswith(w[0])), None)
        if well is not None:
            assert n[1] < -0.1 and n[well[1]] * well[2] > 0.1, (part, n)
            seen.add(well[0][1:])
            continue
        hit = next((e for e in EXACT if part.endswith(e[0])), None)
        assert hit is not None, f"no rule says which way {part} faces"
        assert all(abs(n[i] - hit[1][i]) < 1e-6 for i in range(3)), (part, n, hit[1])
        seen.add("Chamfer" if "Chamfer" in hit[0] else hit[0].strip("_"))
    return seen
