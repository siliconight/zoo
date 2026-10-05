"""Plan facade covers from a Patina dressing manifest (pure, no bpy).

Patina v0.11 emits ``<building>.dressing.json``: a trim atlas plus per-anchor
build orders. This module turns that manifest into cover *plans* Zoo's
``dress_cover`` recipe can build — the pure half, so it is unit-testable
without Blender.

The contract (Patina ``docs/DRESSING_CONTRACT.md``):

* ``space`` — ``"spec/Blender Z-up raw coords"`` when Patina saw a DC
  slots.json (the normal case), else Patina's baked Y-up frame. Orders'
  ``pos``/``normal`` are already in that space; Zoo builds in Blender Z-up, so
  a Y-up manifest is converted here (the inverse of Patina's export).
* each order carries ``cover``, ``trim_piece``, ``uv_region``, ``pos``,
  ``normal``, ``size``, ``collision`` (always ``"none"``) and ``seed_offset``.

A plan is a small dict the recipe + orchestrator consume; the theme drives
material/color/wear via the ``dress_cover`` genome's style block, so covers
match the kit Zoo built for the same building.
"""
from __future__ import annotations

import json

DRESSING_SCHEMA = "patina-dressing/1"

# cover kind -> proud (how far it stands off the surface), cross (its height or
# width on the surface), span (nominal length along the run). Pure data so the
# recipe's geometry stays a thin wrapper and sizing is unit-testable.
# Dressing detail is capped against the surface it sits on: on a 3.7 m storey
# base_course was 1/11 and pilaster 1/15, coarse enough to read as structure
# rather than trim. Both halved. The four already finer than 1/20 -- gutter
# 1/26, curb 1/31, edge_strip 1/37, conduit 1/74 -- are left alone; the
# instinct that dressing was too chunky was right and pointed at these three.
_COVER = {
    "edge_strip":  {"proud": 0.06, "cross": 0.10, "span": 2.0},
    "base_course": {"proud": 0.04, "cross": 0.18, "span": 2.0},
    "curb":        {"proud": 0.05, "cross": 0.12, "span": 2.0},
    "conduit_run": {"proud": 0.04, "cross": 0.05, "span": 1.6},
    # One panel of a panel field (Patina v0.17 wall_panel orders): a thin
    # proud plate; the field effect comes from many orders in a grid, and
    # the gaps between plates are where the facade gets its shadow lines.
    # 0.03 -> 0.012: a panel field's proud depth IS its seam. Every cell has
    # four edge faces, and across 1032 cells those edges draw a lattice on any
    # sky-dominant ambient -- the "tiles" that kept reading as tiles after the
    # UV fix, because the seams are geometry and the UV fix was texture.
    "panel_field": {"proud": 0.012, "cross": 1.2, "span": 1.2},
    # v0.26 facade kit (Patina --frames/--gutters/--pilasters):
    "gutter_run":  {"proud": 0.10, "cross": 0.14, "span": 2.0},
    # 1.67.0 (Patina >= 0.25.0): the pipe from the gutter to the ground. A
    # 3-inch leader on straps; `span` is a placeholder -- `size` is the length.
    "downspout":   {"proud": 0.07, "cross": 0.076, "span": 2.5},
    "pilaster":    {"proud": 0.05, "cross": 0.12, "span": 4.2},
    "frame":       {"proud": 0.05, "cross": 0.12, "span": 1.0},
}

#: COVERS THAT ARE PAINTED METAL (1.67.0), whatever trim the style names: a
#: gutter and its downspout are aluminium on a 1990s rowhouse, and in the
#: concrete every other cover wears they read as one more ledge.
METAL_COVERS = ("gutter_run", "downspout", "ac_unit")
METAL_KIND = "metal_painted"
#: White aluminium. CORRECTED (1.69.0): this said "the flat colour, used only
#: with no skin library". It is also the TINT: `materials.make_material` tints
#: a tintable pack -- `metal_painted_neutral` is achromatic on purpose -- and
#: names the result for it, which is the `_dbdbd4` on every shipped gutter's
#: `M_Skin_metal_painted_delco_1997_dbdbd4`.
METAL_COLOR = (0.86, 0.86, 0.83)

#: AN EMPTY'S WINDOW AIR CONDITIONER (1.69.0). The walker's window
#: photographs: "window air conditioners in nearly every photograph", a white
#: or beige box in the lower sash, standing out of the wall. A 1990s
#: 6,000 BTU unit, 52 x 36 cm, standing 30 cm out of the wall and reaching back
#: through the reveal to the pane -- `_arch` sets the pane at the wall's centre
#: plane, 13 cm behind the face of a 0.3 m wall. Lifted 2 mm off the sill so
#: its underside is never coplanar with the reveal. White painted metal: the
#: gutters' material, so on a side that has gutters it merges into their mesh
#: at no extra draw. Sized from its opening and these, not from `_COVER`.
AC_W, AC_H = 0.52, 0.36
AC_OUT, AC_BACK = 0.30, 0.13
AC_LIFT = 0.002
#: AN EMPTY'S WINDOW BARS (1.69.0), "proud of the frame on bolted straps":
#: 18 mm square uprights about 12 cm apart standing 4 cm off the wall and
#: running 5 cm past the head and the sill; two flat straps behind them,
#: reaching 7 cm past each jamb onto the brick and bolted there on standoffs.
#: Every part stands 1 mm or more off the wall face, never in it or flush.
BAR = 0.018
BAR_PITCH = 0.12
BAR_PROUD = 0.04
BAR_REACH = 0.05
STRAP_W, STRAP_T = 0.04, 0.008
STRAP_REACH = 0.07
STRAP_IN = 0.14
#: Black painted iron: the same painted metal in a second colour, so ONE more
#: surface on a side that has bars, however many windows they cover.
IRON_COVERS = ("window_bars", "security_door")
IRON_COLOR = (0.07, 0.07, 0.07)

#: AN EMPTY'S STONE LINTELS AND SILLS (1.71.0). The walker's South Philly
#: photograph: "white stone lintels and sills over and under every window".
#: A lintel stands on the opening's HEAD, 20 cm tall, bearing 10 cm into the
#: brick past each jamb and 2.8 cm proud -- behind the bars, whose uprights
#: run up past the head 3.1 cm off the wall. A sill hangs below the SILL
#: line, 7 cm deep, 6 cm proud so it reads as a ledge, 5 cm past each jamb.
#: Both stand 1 mm off the wall face.
LINTEL_H, LINTEL_PROUD, LINTEL_BEAR = 0.20, 0.028, 0.10
SILL_H, SILL_PROUD, SILL_BEAR = 0.07, 0.06, 0.05
#: In `plaster` -- Pixelcoat's `plaster_delco`, cream and matte, the nearest
#: skin to the photograph's white stone that a cover already offers. One more
#: material, so one more surface on a side that has openings. The colour is
#: the flat fallback; the pack is not tintable.
STONE_TRIM_COVERS = ("lintel", "window_sill")
STONE_TRIM_KIND = "plaster"
STONE_TRIM_COLOR = (0.80, 0.76, 0.68)

#: The gutter's sheet, drawn thicker than aluminium so it holds at street
#: distance; its front stands a little lower than its back, as a hung gutter's
#: does; and a rolled bead runs along the top of the front.
GUTTER_SHEET = 0.008
GUTTER_FRONT = 0.85
#: The downspout: a 3 x 2 inch leader held off the wall on straps, ending in a
#: cast boot at the ground, where a Philadelphia rowhouse's leader goes into
#: the sewer. A boot also means no elbow kicking out across the sidewalk:
#: non-collision geometry in walkable space is what panel fields were removed
#: for.
DOWNSPOUT_STANDOFF = 0.02
DOWNSPOUT_DEPTH = 0.05
BOOT_H, BOOT_W, BOOT_D = 0.35, 0.12, 0.10


def strip_size(cover: str, size_hint: float, size2=None):
    """(w, d, h) of a cover's local strip before the anchor normal orients it.

    span runs along the wall/edge (scaled by the anchor size hint); depth is how
    far it stands proud; the third axis is its height/width on the surface.
    conduit_run is the exception: a tall, slim vertical run. panel_field uses
    the order's ``size2`` = [face width, face height] exactly — panel grids
    are laid out by Patina, so cells must not be rescaled here.
    """
    c = _COVER.get(cover, _COVER["edge_strip"])
    if cover in ("panel_field", "pilaster"):
        w, h = (size2 if size2 and len(size2) == 2
                else (max(size_hint, 0.2), max(size_hint, 0.2)))
        return (max(float(w), 0.05), c["proud"], max(float(h), 0.05))
    if cover == "gutter_run":
        # spans its wall module exactly (sections join at module seams).
        return (max(size_hint, 0.2), c["proud"], c["cross"])
    if cover in ("conduit_run", "downspout"):
        # `size` IS the run length (Patina v0.19: ground plane -> fixture), so
        # it is used as the span directly. It used to be a constant 0.3 hint
        # that got scaled by span/0.6; when the field's meaning changed and
        # this did not, a 2.45 m run became a 6.53 m bar centred on the
        # fixture, spanning -0.82..5.72 -- through the ground and up past the
        # next storey.
        return (c["cross"], c["proud"], max(float(size_hint), 0.2))
    span = max(0.2, c["span"] * max(size_hint, 0.1) / 0.6)
    return (span, c["proud"], c["cross"])              # long, short


def strip_yaw(normal, tangent=None) -> float:
    """Rotation about up, in radians, that orients a cover strip.

    A strip's local shape is (span, proud, cross): LONG in +X, thin in +Y. Two
    axes have to be pinned -- which way it stands proud, and which way it runs
    -- and a normal alone pins only one.

    * Horizontal normal (wall base, conduit): yaw local +Y onto the normal.
      Local +X then lies along the wall for free. Unchanged behaviour.
    * Vertical normal (roofline, curb): the normal says nothing about yaw. This
      used to return no rotation at all, so every such strip kept world +X as
      its run direction no matter which facade it sat on -- on a wall running
      along Y, 64 capping strips became 64 sticks jutting out of the building.
      With a tangent, +X runs along the wall as intended.

    ``tangent`` is optional: absent, this reproduces the old result exactly, so
    a manifest written before Patina emitted one still builds the same way.
    """
    import math
    nx, ny, nz = (float(normal[0]), float(normal[1]), float(normal[2]))
    if abs(nz) > 0.99:
        if tangent is None:
            return 0.0
        tx, ty = float(tangent[0]), float(tangent[1])
        if (tx * tx + ty * ty) < 1e-12:      # tangent is vertical: no yaw to take
            return 0.0
        return math.atan2(ty, tx)
    return math.atan2(ny, nx) - math.pi / 2.0


def uv_offset(order) -> tuple:
    """Where this cover sits, expressed in its OWN rotated frame.

    Covers are built at the origin and moved afterwards, so
    ``geometry.cube_project_uv`` -- which reads ``loop.vert.co``, a LOCAL
    coordinate -- gave all 1374 panel covers on a building the identical UV
    rect. Every panel then sampled the identical patch of concrete, and the
    facade read as a grid of stamped tiles. The seams a player sees are not
    the 3 cm gaps; they are the texture restarting in every cell.

    Adding this offset before projecting makes the projection continuous
    across covers that share a wall: rotating it back through the cover's own
    yaw gives exactly the world position, so the projection axes stay local
    while the COORDINATE is world. Bloodborne's set-dressing writeup calls the
    underlying technique "mixing tileables with simple inserts" -- inserts only
    read as inserts when the tileable behind them is continuous.
    """
    import math
    pos = order.get("pos") or (0.0, 0.0, 0.0)
    px, py, pz = (float(pos[0]), float(pos[1]), float(pos[2]))
    yaw = strip_yaw(order.get("normal") or (0.0, 1.0, 0.0), order.get("tangent"))
    c, sn = math.cos(yaw), math.sin(yaw)
    return (px * c + py * sn, -px * sn + py * c, pz)


def load_manifest(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    schema = data.get("schema", "")
    if not schema.startswith("patina-dressing/"):
        raise ValueError(
            f"{path}: not a Patina dressing manifest (schema={schema!r})")
    return data


def _patina_yup_to_blender(pos):
    """Patina baked Y-up (x, y, z) -> Blender Z-up (x, -z, y).

    Inverse of Patina's ``blender_to_patina`` (which is the glTF axis
    convention). Only used when a manifest is in Patina space; a DC-aligned
    manifest is already Blender Z-up and passes through untouched.
    """
    x, y, z = pos
    return [float(x), float(-z), float(y)]


def _needs_conversion(space: str) -> bool:
    # Blender-Z-up manifests (the DC-aligned default) pass through; only a
    # Patina baked-frame manifest is rotated into Blender.
    return "Blender" not in (space or "")


def order_position(order: dict, space: str):
    pos = order.get("pos", [0.0, 0.0, 0.0])
    return _patina_yup_to_blender(pos) if _needs_conversion(space) else list(pos)


def order_normal(order: dict, space: str):
    n = order.get("normal", [0.0, 0.0, 1.0])
    return _patina_yup_to_blender(n) if _needs_conversion(space) else list(n)


def _style_block(genome: dict, theme: str):
    styles = genome.get("styles", {})
    return styles.get(theme) or styles.get("default") or {}


def dress_plan(order: dict, genome: dict, theme: str, space: str,
               tool_version: str) -> dict:
    """A build plan for one cover order (consumed by recipes/dress_cover.build).

    ``ambient`` is carried like ``wear`` and ``bevel``. It was authored in the
    style blocks (``rockay`` 0.05, ``industrial_flats`` 0.1) and copied here by
    nothing, so every cover took ``bm_to_object``'s default of 0.0 and no cover
    ever got the cool-up / warm-fill-down form tint the styles asked for. That
    tint is the one variation lever that costs no extra elements: it changes
    how a surface reads by face orientation rather than by adding geometry.
    """
    style = _style_block(genome, theme)
    material = style.get("material") or genome["materials"]["default"]
    if material not in genome["materials"]["options"]:
        material = genome["materials"]["default"]
    color = [round(float(c), 4) for c in style.get("color", [0.6, 0.6, 0.6])]
    # a gutter and its downspout are painted metal (1.67.0) -- when the
    # genome offers it, so a genome that does not is never handed a kind it
    # cannot build
    if order.get("cover") in METAL_COVERS and METAL_KIND in genome["materials"]["options"]:
        material, color = METAL_KIND, [round(float(c), 4) for c in METAL_COLOR]
    # and an Empty's window bars are black painted iron (1.69.0)
    elif order.get("cover") in IRON_COVERS and METAL_KIND in genome["materials"]["options"]:
        material, color = METAL_KIND, [round(float(c), 4) for c in IRON_COLOR]
    # and its lintels and sills are stone-coloured plaster (1.71.0)
    elif order.get("cover") in STONE_TRIM_COVERS and STONE_TRIM_KIND in genome["materials"]["options"]:
        material, color = STONE_TRIM_KIND, [round(float(c), 4) for c in STONE_TRIM_COLOR]
    return {
        "species": "dress_cover",
        "tool_version": tool_version,
        "theme": theme,
        "style": theme if theme in genome.get("styles", {}) else "default",
        "material": material,
        "color": color,
        "wear": round(float(style.get("wear", 0.15)), 3),
        "ambient": round(float(style.get("ambient", 0.0)), 3),
        "bevel": style.get("bevel", 0.002),
        "order": {
            "cover": order.get("cover", "edge_strip"),
            "trim_piece": order.get("trim_piece"),
            "uv_region": order.get("uv_region"),
            "tangent": order.get("tangent"),
            "size": float(order.get("size", 0.6)),
            "pos": order_position(order, space),
            "normal": order_normal(order, space),
            "collision": order.get("collision", "none"),
            "seed_offset": int(order.get("seed_offset", 0)),
            "size2": ([float(v) for v in order["size2"]]
                      if isinstance(order.get("size2"), (list, tuple))
                      else None),
            "frame_width": float(order.get("frame_width", 0.12)),
        },
    }


#: THE SIDES A BUILDING'S COVERS MERGE BY (1.68.0), in Deli Counter's facings
#: -- N = +y, E = +x, S = -y, W = -x, the letters its `ext_<storey>_<facing>_*`
#: slot ids carry, read against their own orders' normals on cold run 9154.
#: A side is the unit that enters and leaves view together, which is what a
#: merged mesh has to be: the export culls by occlusion, and one mesh holding
#: a building's front and back covers keeps the back drawn whenever the front
#: is seen.
SIDES = ("N", "E", "S", "W")


def footprint(points):
    """``(cx, cy, hx, hy)``: the box the covers stand in, seen from above --
    its centre and half-sizes in x and y. The building as its covers see it."""
    xs = [float(p[0]) for p in points]
    ys = [float(p[1]) for p in points]
    if not xs:
        return (0.0, 0.0, 0.0, 0.0)
    return ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0,
            (max(xs) - min(xs)) / 2.0, (max(ys) - min(ys)) / 2.0)


def cover_side(normal, pos, box):
    """Which of `SIDES` a cover belongs to.

    A WALL-FACING cover is on the side its normal leaves. An UP-FACING one --
    a curb at the wall's foot, an edge strip on the roof, 60 of a rowhome's
    103 covers -- has no side of its own and takes the one it stands nearest,
    measured in units of the footprint's half-size so a long building's end
    curbs go to its end and not its flank. Grouped by normal alone, every curb
    and roof edge of a building would be one mesh the size of the building.
    Ties go to x, then to the negative side: deterministic, not meaningful.
    """
    nx, ny, nz = (float(v) for v in normal)
    side = max(abs(nx), abs(ny))
    if side > 1e-6 and side >= abs(nz):
        if abs(nx) >= abs(ny):
            return "E" if nx > 0 else "W"
        return "N" if ny > 0 else "S"
    cx, cy, hx, hy = box
    dx = (float(pos[0]) - cx) / max(hx, 1e-6)
    dy = (float(pos[1]) - cy) / max(hy, 1e-6)
    if abs(dx) >= abs(dy):
        return "E" if dx > 0 else "W"
    return "N" if dy > 0 else "S"


def plan_dressing(manifest: dict, genome: dict, theme: str,
                  tool_version: str) -> dict:
    """All cover plans for a dressing manifest, plus a summary.

    Orders with ``collision`` other than ``"none"`` are dropped defensively —
    the contract is non-collision only; Zoo never builds a colliding cover from
    a dressing order.
    """
    space = manifest.get("space", "")
    orders = [o for o in manifest.get("orders", [])
              if o.get("collision", "none") == "none"]
    plans = [dress_plan(o, genome, theme, space, tool_version) for o in orders]
    # every cover's side (1.68.0), against the footprint of ALL of them, in
    # the Blender frame `dress_plan` has already put them in
    box = footprint([p["order"]["pos"] for p in plans])
    counts: dict[str, int] = {}
    sides: dict[str, int] = {}
    for p in plans:
        k = p["order"]["cover"]
        counts[k] = counts.get(k, 0) + 1
        p["side"] = cover_side(p["order"]["normal"], p["order"]["pos"], box)
        sides[p["side"]] = sides.get(p["side"], 0) + 1
    return {
        "building_id": manifest.get("building_id"),
        "trim_sheet": manifest.get("trim_sheet"),
        "space": space,
        "theme": theme,
        "plans": plans,
        "counts": dict(sorted(counts.items())),
        "sides": dict(sorted(sides.items())),
        "cover_count": len(plans),
    }


def gutter_parts(span: float, proud: float, cross: float):
    """A hung gutter's parts, as (center, size) boxes in cover-local space:
    x along the wall, y out from the wall FACE (y = 0 is the face, which is
    where Patina's ``pos`` sits), z up about the gutter's centre line.

    AN OPEN TROUGH, NOT A BAR (1.67.0). The box this replaces was centred on
    the face, so half of it stood inside the wall, and it had no mouth. Here:
    a back on the wall, a floor, a front a little lower than the back, and a
    rolled bead along the front's top -- with nothing across the mouth, so a
    street-level eye sees a lip and a shadow. Every part runs the full span,
    so sections butt at module seams as real gutter sections join.
    """
    t = GUTTER_SHEET
    front = cross * GUTTER_FRONT
    zb = -cross / 2.0
    return [
        ((0.0, t / 2.0, 0.0), (span, t, cross)),                          # back
        ((0.0, proud / 2.0, zb + t / 2.0), (span, proud, t)),             # floor
        ((0.0, proud - t / 2.0, zb + front / 2.0), (span, t, front)),     # front
        ((0.0, proud - 0.007, zb + front - 0.006), (span, 0.014, 0.012)),  # bead
    ]


def downspout_parts(length: float, cross: float):
    """A downspout's parts, in the same cover-local space (y out from the wall
    face, z about the run's middle): the leader on its standoff, a cast boot
    at the ground, two straps. Bottom at ``-length / 2`` -- the ground -- and
    top at ``+length / 2``, the gutter's underside (Patina 0.25.0 measures
    the run between the two).
    """
    L = float(length)
    zb = -L / 2.0
    y0 = DOWNSPOUT_STANDOFF
    pipe_z0 = zb + BOOT_H - 0.02                      # the leader enters the boot
    pipe = ((0.0, y0 + DOWNSPOUT_DEPTH / 2.0, (pipe_z0 + L / 2.0) / 2.0),
            (cross, DOWNSPOUT_DEPTH, L / 2.0 - pipe_z0))
    boot = ((0.0, BOOT_D / 2.0, zb + BOOT_H / 2.0), (BOOT_W, BOOT_D, BOOT_H))
    strap_d = y0 + DOWNSPOUT_DEPTH + 0.004
    straps = [((0.0, strap_d / 2.0, zb + L * f), (cross + 0.012, strap_d, 0.025))
              for f in (1.0 / 3.0, 2.0 / 3.0)]
    return [pipe, boot] + straps


def ac_parts(opening_w: float):
    """A window air conditioner's parts (1.69.0), as (center, size) boxes in
    cover-local space: x along the wall, y out from the wall FACE, z up from
    the SILL, where Patina orders the unit.

    The cabinet, from the pane (``-AC_BACK``) to ``AC_OUT`` out of the wall;
    five fins across its back -- the side the street sees, the condenser
    grille; louvres down each flank, outside the wall; the accordion panels
    that close the sash out to the jambs, at the window plane, each with three
    pleats; and two L brackets under the overhang, their legs flat on the wall
    below the sill. Touching parts overlap by a millimetre rather than sharing
    a face. A narrow opening takes a narrower unit, 20 cm short of it.
    """
    ow = float(opening_w)
    w = min(AC_W, max(0.30, ow - 0.20))
    h = AC_H
    y0, y1 = -AC_BACK, AC_OUT
    z0 = AC_LIFT
    parts = [((0.0, (y0 + y1) / 2.0, z0 + h / 2.0), (w, y1 - y0, h))]       # cabinet
    for k in range(5):                                                     # grille fins
        parts.append(((0.0, y1 + 0.004, z0 + h * (0.2 + 0.15 * k)), (w - 0.08, 0.01, 0.02)))
    for sx in (-1.0, 1.0):                                                 # flank louvres
        for k in range(3):
            parts.append(((sx * (w / 2.0 + 0.003), y1 * 0.55, z0 + h * (0.3 + 0.2 * k)),
                          (0.008, y1 * 0.6, 0.025)))
    side = ow / 2.0 - w / 2.0 - 0.01
    if side > 0.02:                                                        # accordion panels
        for sx in (-1.0, 1.0):
            cx = sx * (w / 2.0 + side / 2.0)
            parts.append(((cx, y0 + 0.01, z0 + h / 2.0), (side, 0.012, h * 0.95)))
            for j in (-1, 0, 1):
                parts.append(((cx + j * side / 4.0, y0 + 0.021, z0 + h / 2.0),
                              (0.008, 0.012, h * 0.95)))
    arm = y1 - 0.04                                                        # brackets
    for sx in (-1.0, 1.0):
        x = sx * (w / 2.0 - 0.06)
        parts.append(((x, 0.001 + arm / 2.0, -0.013), (0.025, arm, 0.024)))
        parts.append(((x, 0.013, -0.15), (0.025, 0.024, 0.28)))
    return parts


def bar_parts(opening_w: float, opening_h: float):
    """A barred window's parts (1.69.0), in the same cover-local space with z
    about the opening's centre, where Patina orders them: square uprights
    across the opening running past its head and sill, two flat straps behind
    them reaching past the jambs onto the brick, and a bolted standoff at each
    strap end. Everything stands at least 1 mm off the wall face."""
    ow, oh = float(opening_w), float(opening_h)
    n = max(2, int(round(ow / BAR_PITCH)) - 1)
    pitch = ow / (n + 1)
    parts = [((-ow / 2.0 + j * pitch, BAR_PROUD, 0.0), (BAR, BAR, oh + 2 * BAR_REACH))
             for j in range(1, n + 1)]
    back = BAR_PROUD - BAR / 2.0                    # the uprights' back face
    for z in (-oh / 2.0 + STRAP_IN, oh / 2.0 - STRAP_IN):
        parts.append(((0.0, back - STRAP_T / 2.0 + 0.001, z),
                      (ow + 2 * STRAP_REACH, STRAP_T, STRAP_W)))
        for sx in (-1.0, 1.0):
            parts.append(((sx * (ow / 2.0 + STRAP_REACH - 0.02), 0.001 + (back - 0.001) / 2.0, z),
                          (0.03, back - 0.001, 0.03)))
    return parts


def lintel_parts(opening_w: float):
    """A stone lintel (1.71.0): one block standing on the opening's head --
    z from 0 up, where Patina orders it -- bearing past both jambs, 1 mm off
    the wall face."""
    w = float(opening_w) + 2.0 * LINTEL_BEAR
    return [((0.0, 0.001 + LINTEL_PROUD / 2.0, LINTEL_H / 2.0), (w, LINTEL_PROUD, LINTEL_H))]


def sill_parts(opening_w: float):
    """A stone sill (1.71.0): one block hung below the sill line -- z from 0
    down, where Patina orders it -- projecting as a ledge, 1 mm off the wall
    face."""
    w = float(opening_w) + 2.0 * SILL_BEAR
    return [((0.0, 0.001 + SILL_PROUD / 2.0, -SILL_H / 2.0), (w, SILL_PROUD, SILL_H))]


#: AN EMPTY'S IRON SECURITY DOOR (1.72.0). The walker's South Philly
#: photograph: "a black iron security door with a grille". Hung in the
#: doorway's reveal: from 6 cm to 2 cm behind the wall face, so 2 cm in front
#: of the leaf `_arch` sets back 8 cm. Two stiles and three rails -- top,
#: bottom and the lock rail at handle height -- with uprights between, and a
#: lock box on the lock rail. In the bars' black iron, so on a side with bars
#: it merges into their mesh.
SEC_Y0, SEC_Y1 = -0.06, -0.02
SEC_STILE = SEC_RAIL = 0.05
SEC_BAR = 0.016
SEC_PITCH = 0.11
SEC_LOCK_Z = 1.0


def security_door_parts(opening_w: float, opening_h: float):
    """An iron security door's parts (1.72.0), as (center, size) boxes in
    cover-local space with z about the opening's centre, where Patina orders
    it: 5 mm clear of the jambs and head, the threshold at the bottom."""
    ow, oh = float(opening_w), float(opening_h)
    w, h = ow - 0.01, oh - 0.01
    y, d = (SEC_Y0 + SEC_Y1) / 2.0, SEC_Y1 - SEC_Y0
    zb = -h / 2.0
    parts = [((sx * (w / 2.0 - SEC_STILE / 2.0), y, 0.0), (SEC_STILE, d, h))
             for sx in (-1.0, 1.0)]
    inner = w - 2.0 * SEC_STILE
    for z in (zb + SEC_RAIL / 2.0, zb + h - SEC_RAIL / 2.0, zb + SEC_LOCK_Z):
        parts.append(((0.0, y, z), (inner + 0.002, d, SEC_RAIL)))
    n = max(2, int(round(inner / SEC_PITCH)) - 1)
    pitch = inner / (n + 1)
    for j in range(1, n + 1):
        parts.append(((-inner / 2.0 + j * pitch, y, 0.0), (SEC_BAR, SEC_BAR, h - 2.0 * SEC_RAIL + 0.002)))
    parts.append(((inner / 2.0 - 0.05, SEC_Y1 + 0.0115, zb + SEC_LOCK_Z + 0.07), (0.07, 0.024, 0.14)))
    return parts


def frame_strips(w: float, h: float, frame_w: float, proud: float):
    """The four strips of an opening frame, as (center, size) box specs in
    cover-local space (x along the wall, y proud, z up; opening centered on
    the origin). Pure so the geometry contract is testable without Blender:
    top and bottom strips overhang the jambs (butt joints at the corners),
    the jambs run the opening height exactly.
    """
    f, p = float(frame_w), float(proud)
    return [
        ((0.0, 0.0, h / 2 + f / 2), (w + 2 * f, p, f)),      # head
        ((0.0, 0.0, -h / 2 - f / 2), (w + 2 * f, p, f)),     # sill
        ((-w / 2 - f / 2, 0.0, 0.0), (f, p, h)),             # left jamb
        ((w / 2 + f / 2, 0.0, 0.0), (f, p, h)),              # right jamb
    ]
