"""What a club's light hardware is, planned in pure Python.

Zoo 0.94.0. The walker, 2026-09-16, with a frame of the strip club's main
floor showing a warm pool on the floor and a matching wash on the ceiling
above it, both circled: "awesome lighting in the strip club, but it doesn't
look like that light is coming out of any viewable light fixtures... curious
if we can get the same look in but actually using lights?"

He is right about the cause. Lux 0.37.0 wrote the club set -- `club_wash`,
`stage_light`, `neon`, `room_ambient`, and 0.39.0's `back_bar` -- with "no
hardware and no marker today" in its own docstring, while every older anchor
type (`fluorescent`, `streetlight`, `sign`, `wall_pack`, `pendant`) has had
a Zoo fixture at it since v0.28. Two of the five are a LAMP and can have
one; the other three already do or cannot:

  * `neon` IS its sign, and Zoo builds that (`sign_box`);
  * `back_bar` is the bar's own bulbs and porthole, which Zoo builds;
  * `room_ambient` is a probe, not a light, and has nothing to hang.

So this plans the two that were missing:

  * FORM ``can`` -- a small surface-mounted downlight can for a `club_wash`.
    A ring trim, a short cylindrical body, a lit lens across the bottom, and
    a cast baffle inside the mouth so it reads as a can and not a disc.
  * FORM ``par`` -- a PAR can for a `stage_light`: a wider barrel, a yoke of
    two arms and a clamp, a lit lens, and four barn doors round the mouth.

THE FRAME. Origin at the fixture's CENTRE, metres, Z up; the lens faces -Z
and the mount faces +Z, so `bpylayer.build.build_fixtures`' ``above`` mount
(bottom at the emitter point) puts the LIT FACE exactly on the anchor Lux
puts its lamp at. A `par` is additionally TILTED about its lens by the
placement's `tilt_deg`, which `core.fixtures` derives from the anchor's own
`target` -- so the barrel swings up and back from a lens that does not move.

THE GEL. A club light's colour belongs to the light, not to the metal, but a
white-hot lens under a magenta pool is exactly the disagreement the walker
photographed. `GEL` is therefore a SECOND COPY of Lux's `CLUB_PALETTE`, and
being a second copy it is a contract: the names are Lux's, an unknown name
falls back to the warm lens rather than guessing, and the values are the
palette's own sRGB multipliers. If Lux adds a colour and this does not, a
club still builds -- one can's lens is warm where it should have been
chartreuse, and no build fails over it.
"""
from __future__ import annotations

import math

#: Lux's CLUB_PALETTE by name (see the module docstring on why it is copied).
#: sRGB, each with its largest channel at 1.0, as the light colours are.
GEL = {
    "magenta": (1.0, 0.0, 0.8),
    "hot_pink": (1.0, 0.12, 0.5),
    "red": (1.0, 0.04, 0.06),
    "violet": (0.55, 0.1, 1.0),
    "blue": (0.1, 0.2, 1.0),
    "cyan": (0.0, 0.8, 1.0),
    "amber": (1.0, 0.55, 0.08),
    "tungsten": (1.0, 0.72, 0.42),
}
#: A lens with no colour named, and the fallback for a name this table does
#: not carry: a 1997 tungsten lamp behind clear glass.
GEL_DEFAULT = (1.0, 0.86, 0.66)
#: How hard the lens reads. Well under the 1.6 that made the back bar's
#: porthole a sun at 4 m (`back_bar_art.NICHE_PX`), because a ceiling can is
#: seen from three metres BELOW it, straight into the lens, which is the
#: worst angle there is -- and because the pool it is the source of is the
#: thing the eye is meant to follow.
LENS_STRENGTH = 0.9

FORMS = ("can", "par")

#: The can's proportions, as fractions of its own height unless stated.
#: A 0.25 m body at 0.16 m across is a 1997 surface-mount downlight, and
#: 0.25 is not a free number: it is the drop Lux hangs a ceiling lamp at
#: (`LuxLightLoader.FLUORESCENT_MOUNT`, which the club wash inherits), so a
#: can whose lens is on the anchor has its lamp at its own mouth.
CAN = {"trim_over": 1.30, "trim_h": 0.035, "baffle_h": 0.30, "lip": 0.86}
#: How far up the can's throat its lit disc sits, as a fraction of the
#: baffle. See `plan`'s `can` branch for the frame that set it.
LENS_SEAT = 0.42
#: The PAR's: a stubbier, wider barrel on a yoke, with barn doors.
PAR = {"barrel": 0.74, "yoke_w": 1.24, "yoke_t": 0.055, "clamp_h": 0.16,
       "door_out": 0.46, "door_t": 0.012}
#: Sides round a barrel. 20 is round at a metre and cheap at three.
SEGMENTS = 20


def tilt_for(pos, target) -> tuple:
    """``(bearing_deg, tilt_deg)`` that points a lens-down fixture at
    `target` from `pos`, both in the manifest's own frame (Z up).

    `bearing` is measured from +X toward +Y, the same convention the
    manifest's `rot_y` uses; `tilt` is the angle from straight DOWN, so 0 is
    a fixture hanging plumb and 90 is one shining along the ceiling. A
    target at or above the fixture returns a 90-degree tilt rather than
    swinging the barrel over the top: a stage light that has to aim UP is a
    manifest error, and clamping says so without refusing the build.
    """
    ax = float(target[0]) - float(pos[0])
    ay = float(target[1]) - float(pos[1])
    az = float(target[2]) - float(pos[2])
    flat = math.hypot(ax, ay)
    if flat < 1e-9 and az >= 0.0:
        return 0.0, 0.0
    bearing = math.degrees(math.atan2(ay, ax)) % 360.0
    tilt = math.degrees(math.atan2(flat, -az)) if az < 0.0 else 90.0
    return round(bearing, 4), round(min(tilt, 90.0), 4)


def gel(colour) -> tuple:
    """The lens colour for an anchor's `color` name. An unknown name (or
    none) is the warm lamp -- never a guess, and never a failure."""
    if not colour:
        return GEL_DEFAULT
    return GEL.get(str(colour), GEL_DEFAULT)


def plan(form: str, w: float, d: float, h: float) -> dict:
    """``{parts, lens, facts}``: every piece as a primitive description the
    recipe turns into a mesh, plus which of them is the lit face.

    ``parts`` entries are ``{kind, name, ...}`` with `kind` one of
    ``cyl`` (center, radius, depth, radius_top), ``box`` (center, size) --
    the two `bpylayer.geometry` builds -- and every coordinate is in this
    module's own frame: centre at the origin, lens at ``-h / 2``.
    """
    form = form if form in FORMS else "can"
    w, d, h = float(w), float(d), float(h)
    r = min(w, d) / 2.0
    z0 = -h / 2.0
    parts, facts = [], {"form": form}
    if form == "can":
        trim_h = CAN["trim_h"] * h / 0.25
        parts.append({"kind": "cyl", "name": "ClubFixture_Trim", "part": "body",
                      "center": (0.0, 0.0, h / 2.0 - trim_h / 2.0),
                      "radius": r * CAN["trim_over"], "depth": trim_h})
        parts.append({"kind": "cyl", "name": "ClubFixture_Body", "part": "body",
                      "center": (0.0, 0.0, z0 + (h - trim_h) / 2.0),
                      "radius": r, "depth": h - trim_h})
        # the baffle: a dark cone inside the mouth. Without it the can is a
        # bright disc on a dark ceiling from every angle, which is the thing
        # being fixed, not a fixture.
        bh = CAN["baffle_h"] * h
        parts.append({"kind": "cyl", "name": "ClubFixture_Baffle", "part": "dark",
                      "center": (0.0, 0.0, z0 + bh / 2.0), "radius": r * 0.995,
                      "radius_top": r * CAN["lip"], "depth": bh})
        # THE LENS SITS IN THE THROAT, NOT AT THE TOP OF IT. At the baffle's
        # full height (the first build) the lit disc was 7.4 cm up a 16 cm
        # mouth and invisible from anywhere but straight below: shot looking
        # up at `main_floor_wash_5` from 3 m and the can read as a black
        # cylinder over a magenta pool. `LENS_SEAT` puts it under half the
        # baffle, so the disc is in view from about 60 degrees off the axis
        # and the baffle still shades it from across the room.
        lens_z = z0 + bh * LENS_SEAT
        lens_r = r * (CAN["lip"] + (1.0 - CAN["lip"]) * (1.0 - LENS_SEAT)) * 0.96
        facts["throat"] = round(bh, 4)
    else:
        barrel_h = PAR["barrel"] * h
        yoke_h = h - barrel_h
        parts.append({"kind": "cyl", "name": "ClubFixture_Body", "part": "body",
                      "center": (0.0, 0.0, z0 + barrel_h / 2.0),
                      "radius": r, "depth": barrel_h})
        parts.append({"kind": "cyl", "name": "ClubFixture_Body", "part": "body",
                      "center": (0.0, 0.0, z0 + barrel_h - 0.012),
                      "radius": r * 1.06, "depth": 0.024})
        # the yoke: two arms down the barrel's sides and a clamp above
        arm_h = barrel_h * PAR["yoke_w"]
        for s in (-1.0, 1.0):
            parts.append({"kind": "box", "name": "ClubFixture_Yoke",
                          "part": "dark",
                          "center": (s * (r + PAR["yoke_t"]), 0.0,
                                     z0 + barrel_h - arm_h / 2.0),
                          "size": (PAR["yoke_t"] * 2.0, PAR["yoke_t"] * 3.0,
                                   arm_h)})
        parts.append({"kind": "box", "name": "ClubFixture_Yoke", "part": "dark",
                      "center": (0.0, 0.0, z0 + barrel_h + yoke_h * 0.22),
                      "size": (2.0 * (r + 2.0 * PAR["yoke_t"]),
                               PAR["yoke_t"] * 3.0, yoke_h * 0.44)})
        parts.append({"kind": "cyl", "name": "ClubFixture_Clamp", "part": "dark",
                      "center": (0.0, 0.0, h / 2.0 - PAR["clamp_h"] * h / 2.0),
                      "radius": r * 0.28, "depth": PAR["clamp_h"] * h})
        # barn doors: four flaps standing off the mouth, splayed outward
        door = PAR["door_out"] * r * 2.0
        for i in range(4):
            a = math.pi / 2.0 * i
            parts.append({"kind": "box", "name": "ClubFixture_Door",
                          "part": "dark", "rot_z": math.degrees(a),
                          "center": (math.cos(a) * r * 1.02,
                                     math.sin(a) * r * 1.02, z0 + door / 2.0),
                          "size": (PAR["door_t"], r * 1.9, door)})
        lens_r = r * 0.94
        lens_z = z0 + 0.010
        facts["throat"] = 0.0
    parts.append({"kind": "cyl", "name": "ClubFixture_Lens", "part": "lens",
                  "center": (0.0, 0.0, lens_z + 0.006), "radius": lens_r,
                  "depth": 0.012})
    facts["parts"] = len(parts)
    facts["lens_r"] = round(lens_r, 4)
    # the lens's own face, in this frame: what a co-location check measures
    facts["lens_z"] = round(lens_z, 4)
    return {"parts": parts, "facts": facts}
