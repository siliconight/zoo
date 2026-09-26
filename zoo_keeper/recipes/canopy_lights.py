"""canopy_lights recipe: the recessed downlight grid in a fuel canopy's soffit.

WHY THIS EXISTS. Measured on cold run 9080's package, 2026-09-26: the forecourt
canopy is 22 x 13 m on six columns with three pump islands under it, and of the
20 Lux fixture holders within 45 m every one sits on the SHOP between world
x 58.7 and 81.3 -- the canopy spans 81 to 103. Nothing was over it, because Zoo
had `pendant_fixture`, `fluorescent_fixture`, `club_fixture` and `sign_box` and
no species that goes on a canopy soffit. Lux lit what it was given.

In every reference the walker supplied the canopy IS the light source for the
whole forecourt: a grid of flush units in the soffit, and the tarmac lit by
them rather than by street lighting.

ONE PROP FOR THE WHOLE GRID, AND THAT IS THE POINT. The obvious build is a
fixture species placed once per anchor, which costs two draw calls per unit --
a lens and a housing -- so a twelve-unit canopy would submit 24. This recipe
takes the canopy's FOOTPRINT and lays the whole grid inside one pair of
meshes, so the same twelve units cost 2. That is the repo's own rule ("merge a
module's parts by material ... a prop is that unit: every part of one pack wall
enters view together") applied to a thing whose parts are always seen together:
a canopy soffit is looked at as one surface or not at all.

AND THE LIGHT IS NOT HERE. `max_lights_per_object` is 8 on GL Compatibility,
and a literal 12-20 fixture grid would put every one of them on the forecourt
ground mesh -- the surface that fills the frame when a player stands under it.
So these lenses are EMISSIVE GEOMETRY, costing no light at all, and the real
illumination comes from a handful of wash anchors Deli Counter emits
separately. The walker's call, 2026-09-26, with the three options and their
costs put in front of them: "build the canopy with emissive soffit and a few
lights".

PITCH IS DERIVED, NOT CHOSEN. A unit every `_TARGET_PITCH_M` of span, at least
two per axis, so a small canopy does not get one lonely light and a large one
does not get a pair swimming in the dark. The number a bound would have to come
from is the span, and the span is what this reads.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

#: Metres of soffit per downlight, per axis. From the walker's daylight
#: reference: a 22 x 13 m canopy carrying roughly a 6 x 4 grid of flush units.
_TARGET_PITCH_M = 3.5
#: Never fewer than this per axis -- a single row down the middle of a
#: forecourt reads as a corridor, not a canopy.
_MIN_PER_AXIS = 2
#: The unit itself. A 1990s canopy downlight is a shallow square pan, wide
#: relative to its depth, sitting flush in the deck.
_UNIT_M = 0.60
#: How much of the unit's face is lit lens; the rest is the trim the housing
#: shows around it.
_LENS_FRAC = 0.82
#: The lit face stands this far below the soffit plane, so the lens is not
#: coplanar with the deck it sits in. Coplanar faces flicker, and this
#: package already carries a PRESENTATION_ZFIGHT finding for exactly that.
_PROUD_M = 0.02


def _grid(span: float, pitch: float, minimum: int) -> list[float]:
    """Centres along one axis, inset half a pitch from each edge."""
    n = max(minimum, int(round(span / pitch)))
    step = span / float(n)
    return [-span / 2.0 + step * (i + 0.5) for i in range(n)]


def build(plan, streams, collection):
    # The dimensions ARE the canopy's footprint: this species is placed once
    # for the whole deck, not once per lamp.
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    style = plan.get("style_block", {})
    rng = streams.stream("wear")

    unit = min(_UNIT_M, w * 0.5, d * 0.5)
    lens_side = unit * _LENS_FRAC
    housing_h = max(h, 0.08)
    # Built centred on the deck; the anchor pipeline lifts the prop so the lit
    # face sits at the soffit. z0 is the bottom of the lit face.
    z0 = -housing_h / 2.0

    xs = _grid(w, _TARGET_PITCH_M, _MIN_PER_AXIS)
    ys = _grid(d, _TARGET_PITCH_M, _MIN_PER_AXIS)

    # ONE bmesh for every lens and ONE for every housing. Two draw calls for
    # the whole grid instead of two per unit.
    lens_bm = geometry.new_bm()
    house_bm = geometry.new_bm()
    lens_t = housing_h * 0.30
    for x in xs:
        for y in ys:
            geometry.add_box(
                lens_bm, (x, y, z0 + lens_t / 2.0 - _PROUD_M),
                (lens_side, lens_side, lens_t))
            geometry.add_box(
                house_bm, (x, y, z0 + lens_t + (housing_h - lens_t) / 2.0),
                (unit, unit, housing_h - lens_t))

    lenses = geometry.bm_to_object(
        lens_bm, "CanopyLights_Lens", collection,
        bevel=0.0, texel=1.0, rng=rng, wear=0.0)
    housings = geometry.bm_to_object(
        house_bm, "CanopyLights_Housing", collection,
        bevel=bevel, texel=1.5, rng=rng, wear=wear)

    mat = materials.make_material(
        f"M_CanopyLights_{plan['material']}", plan["color"], plan["material"])
    materials.assign([housings], mat)
    # Cool and slightly green: a 1990s canopy runs metal halide or fluorescent,
    # and every night reference the walker supplied reads green-cyan rather
    # than warm. A warm canopy would date it wrong as surely as a digital
    # pump display would.
    lens = materials.make_emissive_material(
        "M_CanopyLights_Lens",
        style.get("emissive_color", [0.80, 0.95, 0.88]),
        style.get("emissive_strength", 3.0))
    materials.assign([lenses], lens)

    # No collision: it is in the deck, and nothing traverses a soffit.
    return {"objects": [lenses, housings], "collision_boxes": [],
            "attachments": {}, "lamp_count": len(xs) * len(ys)}
