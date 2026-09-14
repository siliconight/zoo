"""furnace, planned in pure Python: the basement's mechanical anchor, in two
forms -- a 1990s upflow gas furnace and a gas water heater.

A basement reads as a basement because of what stands in the corner. Both
forms stand on a concrete pad that is the slot's footprint and send a flue
pipe up to the slot's top, so Deli Counter should author the volume to the
ceiling: the flue is what says "this is connected to the house".

  * ``furnace`` -- a sheet-metal cabinet with a blower door and a louvred
    burner door, a galvanised supply plenum on top and a trunk duct leaving
    it toward the back, an inducer box with the flue rising from it at the
    front, a black-iron gas line with its drip leg and shut-off up the side,
    and, when the footprint is wide enough, a return-air drop on the other
    side.
  * ``water_heater`` -- a faceted tank on a base ring with a domed top, a
    burner access cover and the gas control valve at its foot, an
    EnergyGuide sticker, a relief valve with its discharge pipe, the copper
    cold and hot lines and the draft hood with its flue.

``auto`` takes the water heater for a squarish footprint no more than
AUTO_HEATER_MAX on its long side, the furnace otherwise.

THE RULES the interior species keep (see `core/carton_forms.py`): extents
exactly w x d x h (pad and flue define them); a part standing on another
sinks SINK into it; details stand DETAIL proud; no two faces within 2 mm of
one plane where they overlap -- the pure probe in `core/prims.py` measures
it over sizes and both forms in `tests/test_interior_species.py`.

Frame: metres, Z up, base-up, -Y the front.
"""
from __future__ import annotations

import math

from . import prims as P

SINK = 0.003
DETAIL = 0.003
PAD_H = 0.05
AUTO_HEATER_MAX = 0.8

FORMS = ("furnace", "water_heater")

#: material key -> (linear RGB, kind); "body" is the recipe's genome colour
MATERIALS = {
    "pad": ([0.30, 0.29, 0.27], "concrete"),
    "sheet": ([0.52, 0.53, 0.54], "metal_bare"),      # galvanised duct
    "iron": ([0.06, 0.06, 0.065], "metal_painted"),   # black-iron gas pipe
    "copper": ([0.50, 0.26, 0.13], "metal_bare"),
    "dark": ([0.05, 0.05, 0.05], "plastic"),          # louvres, valve body
    "red": ([0.50, 0.06, 0.05], "plastic"),           # gas valve knob
    "label": ([0.80, 0.72, 0.18], "paper"),           # EnergyGuide yellow
}


def pick_form(form, w, d):
    """The form to build: the asked one, or the dims' reading of ``auto``."""
    if form in FORMS:
        return form
    long_side, short_side = max(w, d), min(w, d)
    if long_side <= AUTO_HEATER_MAX and long_side - short_side <= 0.2:
        return "water_heater"
    return "furnace"


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def plan(w, d, h, form="auto"):
    """``{"prims", "collision", "form", "overshoot_m"}`` for a furnace slot."""
    form = pick_form(form, w, d)
    prims = [P.box("Furnace_Pad", "pad", (-w / 2, -d / 2, 0.0),
                   (w / 2, d / 2, PAD_H), bevel=True)]
    cboxes = [((-w / 2, -d / 2, 0.0), (w / 2, d / 2, PAD_H))]
    if form == "water_heater":
        _water_heater(prims, cboxes, w, d, h)
    else:
        _furnace(prims, cboxes, w, d, h)
    lo, hi = P.bounds(prims)
    overshoot = max(abs(lo[0] + w / 2), abs(hi[0] - w / 2), abs(lo[1] + d / 2),
                    abs(hi[1] - d / 2), abs(lo[2]), abs(hi[2] - h))
    prims, cboxes = P.fit_exact(prims, (-w / 2, -d / 2, 0.0), (w / 2, d / 2, h),
                                cboxes)
    return {"prims": prims, "collision": cboxes, "form": form,
            "overshoot_m": overshoot}


def _furnace(prims, cboxes, w, d, h):
    cw = _clamp(w - 0.30, 0.40, 0.62)
    cw = min(cw, w - 0.10)
    cd = min(_clamp(d - 0.30, 0.45, 0.76), d - 0.12)
    side = (w - cw) / 2.0
    ox = -0.3 * side                       # leave the gas line room on +x
    cx0, cx1 = ox - cw / 2, ox + cw / 2
    y0 = -d / 2 + 0.06
    y1 = y0 + cd
    cab_h = _clamp(h * 0.5, 1.0, 1.25)
    cab_h = min(cab_h, max(0.8, h - 0.4))
    plen_h = _clamp(h - cab_h - 0.25, 0.18, 0.45)
    plen_h = min(plen_h, h - cab_h - 0.02)
    base = PAD_H - SINK

    prims.append(P.box("Furnace_Cabinet", "body", (cx0, y0, base),
                       (cx1, y1, cab_h), bevel=True))
    cboxes.append(((cx0, y0, PAD_H), (cx1, y1, cab_h)))

    # doors on the front, DETAIL proud; louvres DETAIL proud of the upper
    lower_top = PAD_H + (cab_h - PAD_H) * 0.45
    prims.append(P.box("Furnace_Door", "door", (cx0 + 0.03, y0 - DETAIL, PAD_H + 0.06),
                       (cx1 - 0.03, y0 + DETAIL, lower_top)))
    prims.append(P.box("Furnace_Door", "door", (cx0 + 0.03, y0 - DETAIL, lower_top + 0.02),
                       (cx1 - 0.03, y0 + DETAIL, cab_h - 0.05)))
    z = lower_top + 0.08
    n = 0
    while z + 0.015 < cab_h - 0.12 and n < 5:
        # back face 2 x DETAIL inside the cabinet: at y0 it lay on the
        # cabinet's front face (0.0 mm, back to back), at y0 + DETAIL on
        # the door's back face
        prims.append(P.box("Furnace_Louvre", "dark", (cx0 + 0.08, y0 - 2 * DETAIL, z),
                           (cx1 - 0.08, y0 + 2 * DETAIL, z + 0.015)))
        z += 0.045
        n += 1
    lab_z = PAD_H + (lower_top - PAD_H) * 0.6
    prims.append(P.box("Furnace_Label", "label", (cx0 + 0.07, y0 - 2 * DETAIL, lab_z),
                       (cx0 + 0.19, y0 + 2 * DETAIL, lab_z + 0.07)))

    # supply plenum over the rear of the cabinet top, a lip wider on the sides
    lip = 0.012
    plen_y0 = y0 + 0.14
    plen_top = cab_h + plen_h
    prims.append(P.box("Furnace_Plenum", "sheet", (cx0 - lip, plen_y0, cab_h - 0.02),
                       (cx1 + lip, y1 + lip, plen_top), bevel=True))
    cboxes.append(((cx0 - lip, plen_y0, cab_h), (cx1 + lip, y1 + lip, plen_top)))

    # the trunk leaves the plenum toward the back, 2 cm under its top
    tw = min(cw * 0.8, 0.45)
    th = min(0.22, plen_h * 0.7)
    t_top = plen_top - 0.02
    prims.append(P.box("Furnace_Trunk", "sheet", (ox - tw / 2, y1 - 0.05, t_top - th),
                       (ox + tw / 2, d / 2, t_top), bevel=True))
    # a flanged joint where it leaves
    fl = 0.006
    prims.append(P.box("Furnace_Flange", "sheet",
                       (ox - tw / 2 - fl, y1 + lip + 0.012, t_top - th - fl),
                       (ox + tw / 2 + fl, y1 + lip + 0.04, t_top + fl)))
    cboxes.append(((ox - tw / 2, y1, t_top - th), (ox + tw / 2, d / 2, t_top)))

    # inducer box on the front strip of the cabinet top, the flue from it
    ix0, ix1 = cx0 + 0.05, cx0 + 0.21
    iy0, iy1 = y0 + 0.02, y0 + 0.12
    ind_top = cab_h + 0.10
    prims.append(P.box("Furnace_Inducer", "body", (ix0, iy0, cab_h - 0.01),
                       (ix1, iy1, ind_top), bevel=True))
    fx, fy = (ix0 + ix1) / 2, (iy0 + iy1) / 2
    fr = 0.05
    prims.append(P.cyl("Furnace_Flue", "sheet", (fx, fy), fr, ind_top - 0.01, h,
                       segments=10))
    prims.append(P.cyl("Furnace_FlueCollar", "sheet", (fx, fy), fr + 0.008,
                       ind_top - 0.005, ind_top + 0.04, segments=10))
    if h - ind_top > 0.3:
        prims.append(P.cyl("Furnace_FlueCollar", "sheet", (fx, fy), fr + 0.012,
                           h - 0.10, h - 0.04, segments=10))
    cboxes.append(((fx - fr, fy - fr, ind_top), (fx + fr, fy + fr, h)))

    # black-iron gas line up the +x side: drip leg, nipple into the cabinet,
    # shut-off valve, and on up to the joists
    gx = cx1 + 0.045
    if w / 2 - gx >= 0.03:
        gy = y0 + 0.25
        gr = 0.016
        prims.append(P.cyl("Furnace_GasPipe", "iron", (gx, gy), gr, 0.30, h,
                           segments=8))
        prims.append(P.cyl("Furnace_GasPipe", "iron", (gx, gy), gr + 0.006, 0.26,
                           0.31, segments=8))
        nip = P.lay_along_x(P.cyl("Furnace_GasPipe", "iron", (0.0, gy), 0.011,
                                  cx1 - 0.01, gx + 0.005, segments=8))
        prims.append(P.translate(nip, (0.0, 0.0, 0.55)))
        prims.append(P.box("Furnace_GasValve", "red", (gx - 0.028, gy - 0.028, 0.70),
                           (gx + 0.028, gy + 0.028, 0.77)))

    # a return-air drop on the -x side when the footprint has room for one
    rw = cx0 - (-w / 2) - 0.02
    if rw >= 0.22:
        rw = min(rw, 0.36)
        rx0 = cx0 - rw
        prims.append(P.box("Furnace_Return", "sheet", (rx0, y0 + 0.10, 0.25),
                           (cx0 + 0.01, y1 - 0.06, h), bevel=True))
        # the filter slot, a dark band DETAIL proud on the drop's front
        prims.append(P.box("Furnace_Filter", "dark", (rx0 + 0.03, y0 + 0.10 - DETAIL, 0.32),
                           (cx0 - 0.03, y0 + 0.10 + DETAIL, 0.36)))
        cboxes.append(((rx0, y0 + 0.10, 0.25), (cx0, y1 - 0.06, h)))


def _water_heater(prims_out, cboxes_out, w, d, h):
    """Built about the tank's axis at the origin, then moved to where the
    controls on its front and the relief valve on its side fit the pad.

    REFUTED FIRST: the tank centred on the pad at r = min(w, d)/2 - 0.05.
    The gas valve knob stands f + 0.09 in front of the axis, so on a
    0.6 x 0.6 slot it reached 3 cm past the pad and `fit_exact` squeezed
    the whole heater 10 % to take it back (the planner's own overshoot_m,
    0.0315)."""
    prims, cboxes = [], []
    r_fit = min((d - 0.11) / (1.0 + math.cos(math.pi / 12)),
                (w / 2 - 0.06) / math.cos(math.pi / 12), w / 2 - 0.01)
    r = _clamp(r_fit, 0.16, 0.28)
    seg = 12
    phase = math.pi / seg            # a facet faces -Y, +X and -X
    f = r * math.cos(math.pi / seg)  # distance to a facet
    base = PAD_H - SINK
    tank_top = PAD_H + min(1.45, h - 0.45)
    ring_top = PAD_H + 0.07
    prims.append(P.cyl("Heater_Base", "dark", (0.0, 0.0), r * 0.92, base, ring_top,
                       segments=seg, phase=phase))
    prims.append(P.cyl("Heater_Tank", "body", (0.0, 0.0), r, ring_top - SINK, tank_top,
                       segments=seg, phase=phase, bevel=True))
    dome_top = tank_top + 0.07
    prims.append(P.cyl("Heater_Dome", "body", (0.0, 0.0), r, tank_top - SINK,
                       dome_top, segments=seg, r_top=r * 0.35, phase=phase))
    cboxes.append(((-r, -r, PAD_H), (r, r, dome_top)))

    # burner access cover and gas control valve on the front facet
    cwid = min(0.12, 0.45 * r)
    prims.append(P.box("Heater_Cover", "dark", (-cwid / 2, -f - DETAIL, PAD_H + 0.12),
                       (cwid / 2, -f + DETAIL, PAD_H + 0.26)))
    vz0, vz1 = PAD_H + 0.34, PAD_H + 0.46
    prims.append(P.box("Heater_Valve", "dark", (-0.05, -f - 0.07, vz0),
                       (0.05, -f + 0.01, vz1)))
    knob = P.lay_along_y(P.cyl("Heater_Knob", "red", (0.0, 0.0), 0.022,
                               f + 0.065, f + 0.09, segments=8))
    # lay_along_y maps z -> y and x stays; the cylinder ran z in [f+.065, f+.09]
    # so it now runs y in that range: mirror it to the front
    knob = P.mesh("Heater_Knob", "red",
                  [(v[0], -v[1], v[2] + (vz0 + vz1) / 2) for v in knob["verts"]],
                  knob["faces"])
    prims.append(knob)
    # EnergyGuide sticker
    swid = min(0.10, 0.42 * r)
    sz = PAD_H + (tank_top - PAD_H) * 0.55
    prims.append(P.box("Heater_Label", "label", (-swid / 2, -f - DETAIL, sz),
                       (swid / 2, -f + DETAIL, sz + 0.14)))

    # gas line from the valve's side, up to the slot's top
    gx, gy = 0.11, -f - 0.035
    nip = P.lay_along_x(P.cyl("Heater_GasPipe", "iron", (0.0, gy), 0.011,
                              0.045, gx + 0.005, segments=8))
    prims.append(P.translate(nip, (0.0, 0.0, (vz0 + vz1) / 2)))
    prims.append(P.cyl("Heater_GasPipe", "iron", (gx, gy), 0.014, vz0 - 0.08, h,
                       segments=8))
    prims.append(P.cyl("Heater_GasPipe", "iron", (gx, gy), 0.019, vz0 - 0.12,
                       vz0 - 0.075, segments=8))

    # relief valve on the +X facet and its discharge pipe down the side
    tz = tank_top - 0.20
    prims.append(P.box("Heater_Relief", "sheet", (f - 0.01, -0.025, tz),
                       (f + 0.05, 0.025, tz + 0.06)))
    prims.append(P.cyl("Heater_Discharge", "copper", (f + 0.035, 0.0), 0.011,
                       PAD_H + 0.15, tz + 0.01, segments=8))

    # cold and hot lines, each with a union, and the draft hood and flue
    for sx in (-1, 1):
        px, py = sx * 0.6 * r, 0.1 * r
        prims.append(P.cyl("Heater_Line", "copper", (px, py), 0.012,
                           tank_top + 0.01, h, segments=8))
        prims.append(P.cyl("Heater_Union", "sheet", (px, py), 0.018,
                           tank_top + 0.10, tank_top + 0.14, segments=8))
    hood_top = dome_top + 0.09
    prims.append(P.cyl("Heater_Hood", "sheet", (0.0, 0.0), 0.05, dome_top - SINK,
                       hood_top, segments=10, r_top=0.085))
    prims.append(P.cyl("Heater_Flue", "sheet", (0.0, 0.0), 0.055, hood_top - SINK,
                       h, segments=10))
    cboxes.append(((-0.085, -0.085, dome_top), (0.085, 0.085, h)))
    cy = _clamp(0.0, -d / 2 + 0.01 + f + 0.09, d / 2 - 0.01 - r)
    cx = _clamp(0.0, -w / 2 + 0.01 + r, w / 2 - 0.01 - f - 0.05)
    for p in prims:
        prims_out.append(P.translate(p, (cx, cy, 0.0)))
    for a, b in cboxes:
        cboxes_out.append(((a[0] + cx, a[1] + cy, a[2]), (b[0] + cx, b[1] + cy, b[2])))
