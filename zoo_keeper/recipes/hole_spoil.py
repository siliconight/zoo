"""hole_spoil recipe: what came down through a hole, on the floor below it (Zoo 1.114.0; the
factory's roadmap 265).

The floor below a drop hole is where the hole's cause is written in the room under it: a crew that
broke through left the floor they cut out lying in pieces with the ceiling tiles it punched through
(`cut`); a floor that gave way left its boards, plaster and lath (`broken`). Every decision is
`core.hole_forms.spoil_plan`, which is pure and tested: which pieces, where each lies, none on
another. This file builds them.

- `panel`: a piece of the cut-out floor, the subfloor's plywood with the floor's finish on it --
  the slot's `stock` (`carpet`, `tile`; `none` is bare). Square-edged: the crew sawed it out.
- `tile`: a ceiling tile shard; `grid`: a length of the ceiling's grid tee, on its flange.
- `joist`: a joist offcut, on its wide face.
- `plank`: a floorboard, splintered at an end, with the floor's finish on it as a panel has;
  `lath`: a lath strip; `plaster`: a plaster slab.
- `chunk`: a fragment, built as `rubble_frag` builds one -- a solid sliced by planes -- one of
  them the slot's full height.

Everything lies flat on the floor, its underside at the slot's bottom, which Deli Counter stands
`SKIRT` under the visible floor -- so each piece sinks that far into it, as a resting floater does,
and none of them rests on another. NOTHING COLLIDES: it is all under the unassisted step, and the
drop lands on it. One object a colour, one material a kind.
"""
from __future__ import annotations

import math

from ..bpylayer import geometry, materials
from ..core import hole_forms as HF

#: (material kind, colour) a piece is drawn in.
LOOK = {
    "panel": ("wood", "plywood"), "joist": ("wood", "joist"), "plank": ("wood", "floorboard"),
    "lath": ("wood", "lath"), "tile": ("ceiling_tile", "tile"), "grid": ("ceiling_tile", "grid"),
    "plaster": ("plaster", "plaster"), "chunk": ("plaster", "plaster"),
    "slab": ("concrete", "concrete"), "rebar": ("metal", "rebar"),
}
#: A `cut` hole came through a drop ceiling: its fragments are the tiles' own, in their material,
#: so the spoil is three materials (wood, the finish, the tile) and not five.
CUT_CHUNK = ("ceiling_tile", "plaster")
#: The panel's finish, by the slot's stock: (kind, colour, thickness).
FINISH = {"carpet": ("carpet", (0.24, 0.26, 0.31), 0.008),
          "tile": ("tile", (0.72, 0.70, 0.64), 0.008)}


def _yawed(verts, cx, cy, yaw):
    geometry.place(verts, (cx, cy, 0.0), rot_z=yaw)


def _broken_plate(bm, rng, sx, sy, sz, cuts=2):
    """A thin plate whose outline is broken by vertical cuts, its underside at z = 0."""
    verts = geometry.add_box(bm, (0.0, 0.0, sz / 2.0), (sx, sy, sz))
    verts = geometry.fracture(bm, verts, rng, cuts=cuts, near=0.25, far=0.70, steep=1.0,
                              center=(0.0, 0.0, sz / 2.0), radius=max(sx, sy) * 0.5)
    return verts


def _bar(bm, pts, s):
    """A bar `s` square in section lying on z = 0 along the plan polyline `pts`: a ring of four
    vertices a point, mitred at a joint so the section keeps its width, capped at both ends -- one
    closed mesh, nothing inside it. Returns its vertices."""
    rings = []
    for i, (x, y) in enumerate(pts):
        dirs = []
        if i > 0:
            dirs.append((x - pts[i - 1][0], y - pts[i - 1][1]))
        if i < len(pts) - 1:
            dirs.append((pts[i + 1][0] - x, pts[i + 1][1] - y))
        units = [(dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)) for dx, dy in dirs]
        ux, uy = sum(u[0] for u in units), sum(u[1] for u in units)
        ln = math.hypot(ux, uy)
        ux, uy = ux / ln, uy / ln
        # at a joint the ring lies across the two segments' mean, 1/cos(half the bend) wider
        scale = 1.0 / max(units[0][0] * ux + units[0][1] * uy, 0.5)
        nx, ny = -uy * s / 2.0 * scale, ux * s / 2.0 * scale
        rings.append([bm.verts.new((x + nx, y + ny, 0.0)), bm.verts.new((x - nx, y - ny, 0.0)),
                      bm.verts.new((x - nx, y - ny, s)), bm.verts.new((x + nx, y + ny, s))])
    for a, b in zip(rings, rings[1:]):
        for k in range(4):
            bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
    bm.faces.new(tuple(reversed(rings[0])))
    bm.faces.new(tuple(rings[-1]))
    return [v for r in rings for v in r]


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    form = params.get("form", "auto")
    stock = params.get("stock", "none") or "none"
    variant = int(params.get("variant", 0) or 0)
    rng = streams.stream("wear")
    wear, ambient = plan["wear"], plan.get("ambient", 0.0)
    pieces = HF.spoil_plan(w, d, h, form, variant)
    groups = {}

    def bm_for(key):
        if key not in groups:
            groups[key] = geometry.new_bm()
        return groups[key]

    for kind, cx, cy, sx, sy, sz, yaw in pieces:
        if kind == "panel":
            bm = bm_for("panel")
            _yawed(geometry.add_box(bm, (0.0, 0.0, sz / 2.0), (sx, sy, sz)), cx, cy, yaw)
            if stock in FINISH:
                # the finish on the panel, inset a centimetre and sunk a floater's skirt into it
                _fk, _rgb, ft = FINISH[stock]
                fv = geometry.add_box(bm_for("finish"), (0.0, 0.0, sz - HF.SKIRT + ft / 2.0),
                                      (sx - 0.02, sy - 0.02, ft))
                _yawed(fv, cx, cy, yaw)
        elif kind in ("tile", "plaster"):
            verts = _broken_plate(bm_for(kind), rng, sx, sy, sz, cuts=3 if kind == "tile" else 2)
            _yawed(verts, cx, cy, yaw)
        elif kind == "rebar":
            # a length of bar `sz` square in section, straight for two thirds of its length and
            # bent at the third: the plan's width less the bar's is the bend's throw, reserved by
            # `spoil_plan` so the bend lands on no other piece. The first build sheared an
            # eight-vertex box instead -- no vertex stood at the third, so the bar was not bent but
            # set askew, past its plan's width, and the census read a fragment lying on it.
            y0 = -sy / 2.0 + sz / 2.0
            verts = _bar(bm_for("rebar"),
                         [(-sx / 2.0, y0), (sx / 6.0, y0), (sx / 2.0, y0 + max(0.0, sy - sz))], sz)
            _yawed(verts, cx, cy, yaw)
        elif kind == "grid":
            bm = bm_for("grid")
            # a 6 mm flange, the web stopping 2.5 mm short of its ends and standing in its middle,
            # 3 mm from either face: no face of one within the census's 2 mm of the other
            flange = geometry.add_box(bm, (0.0, 0.0, 0.003), (sx, sy, 0.006))
            web = geometry.add_box(bm, (0.0, 0.0, 0.003 + (sz - 0.003) / 2.0),
                                   (sx - 0.005, 0.004, sz - 0.003))
            _yawed(list(flange) + list(web), cx, cy, yaw)
        elif kind in ("joist", "plank", "lath"):
            verts = geometry.add_box(bm_for(kind), (0.0, 0.0, sz / 2.0), (sx, sy, sz))
            if kind == "plank":
                # a splintered end: the far end narrowed to a point off its centre line
                tip = 0.35 + 0.4 * rng.random()
                for v in verts:
                    if v.co.x > 0.0:
                        v.co.y *= tip
                        v.co.x += (rng.random() - 0.5) * 0.06
                if stock in FINISH:
                    # the floor's finish came down on its boards: inset a centimetre a side, tapered
                    # as the board is, and stopping 4 cm short of each end, past the splinter's 3 cm
                    # of play; sunk a floater's skirt into the board's top as a panel's is
                    _fk, _rgb, ft = FINISH[stock]
                    fv = geometry.add_box(bm_for("finish"), (0.0, 0.0, sz - HF.SKIRT + ft / 2.0),
                                          (sx - 0.08, sy - 0.02, ft))
                    for v in fv:
                        if v.co.x > 0.0:
                            v.co.y *= tip
                    _yawed(list(fv), cx, cy, yaw)
            _yawed(verts, cx, cy, yaw)
        else:                                           # chunk or slab: rubble_frag's construction
            bm = bm_for(kind)
            verts = geometry.add_box(bm, (0.0, 0.0, 0.0), (sx, sy, sz))
            verts = geometry.fracture(bm, verts, rng, cuts=4, near=0.10, far=0.50, steep=0.85,
                                      radius=max(sx, sy, sz) / 2.0)
            base_z = geometry.flatten_base(verts, tol_frac=0.12)
            geometry.place(verts, (cx, cy, -base_z), rot_z=yaw)
            # the cuts took the top down: stretch it back to the planned height, base kept at 0
            top = max(v.co.z for v in verts)
            if top > 1e-6:
                for v in verts:
                    v.co.z *= sz / top

    # THE SLOT IS EXACT in plan: a stray that could not be laid on a face leaves the spoil a few
    # centimetres short of it, and one affine map in X and Y closes that before anything is
    # finished; Z is already exact (the keystone chunk is the slot's height, every base is at 0).
    allv = [v for bm in groups.values() for v in bm.verts]
    x0, x1 = min(v.co.x for v in allv), max(v.co.x for v in allv)
    y0, y1 = min(v.co.y for v in allv), max(v.co.y for v in allv)
    for v in allv:
        v.co.x = (v.co.x - x0) / (x1 - x0) * w - w / 2.0
        v.co.y = (v.co.y - y0) / (y1 - y0) * d - d / 2.0

    # ONE MATERIAL A KIND, its base the kind's own colour; a group of another colour carries the
    # difference in `Wear` (`geometry.tint_wear`), so the woods are one submission
    # THE BODY is the genome's material: the floor's pieces (panels, planks, joists, lath) are of
    # it; the ceiling's tile and plaster, and a slab's concrete and bar, are what they are
    body = plan["material"]
    cause, slab, plaster = HF.parse_form(form)
    base = {"wood": HF.COLOURS["plywood"], "plaster": HF.COLOURS["plaster"],
            "ceiling_tile": HF.COLOURS["tile"], "concrete": HF.COLOURS["concrete"],
            "metal": HF.COLOURS["rebar"]}
    objs = []
    for key in sorted(groups):
        if key == "finish":
            kind, rgb, _t = FINISH[stock]
            tint = (1.0, 1.0, 1.0)
        else:
            if key == "chunk":
                # fragments are the floor's where it was a slab, else the ceiling's they came through
                kind, colour = (("concrete", "concrete") if slab else
                                ("plaster", "plaster") if plaster else CUT_CHUNK)
            else:
                kind, colour = LOOK[key]
            rgb = base[kind]
            tint = tuple(a / b for a, b in zip(HF.COLOURS[colour], rgb))
        if kind == "wood":
            kind = body
        obj = geometry.bm_to_object(groups[key], f"HoleSpoil_{key}", collection, bevel=0.0,
                                    texel=1.2, rng=rng, wear=wear, ambient=ambient)
        if any(abs(c - 1.0) > 1e-6 for c in tint):
            geometry.tint_wear(obj, tint)
        materials.assign([obj], materials.make_material(f"M_HoleSpoil_{kind}", rgb, kind))
        objs.append(obj)
    print(f"[hole_spoil] {w:.2f} x {d:.2f} x {h:.3f} form={HF._form(form)} stock={stock} "
          f"variant={variant} pieces={len(pieces)} groups={sorted(groups)} "
          f"plan span before the fit {x1 - x0:.3f} x {y1 - y0:.3f}")
    return {"objects": objs, "collision_boxes": [], "attachments": {}}
