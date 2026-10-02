"""The parts a floor-standing machine is made of: the shape of a made thing.

Zoo 1.46.0. The walker, 2026-10-02: "this looks like it is made with a 90s
GPU ... replace the retro look". Half of that look was the shape: an ATM and a
video-poker cabinet were stacks of sharp boxes with a flat rectangle for a
tube. A made cabinet has its corners broken, stands on a kick set in from its
faces, carries its sign proud of its head, and its tube bulges behind a
surround that slopes in to it.

Every function here returns art prims in the planners' frame (metres, Z up,
the player at -Y): a prim names its ``mat`` (an atlas) and its ``tile``, and
carries ``uvs`` a face. Triangles are not the frame budget (CLAUDE.md: draw
calls are); a chamfered cabinet is still one mesh on one material.

Pure Python: no bpy.
"""
from __future__ import annotations

from . import prims as P


def quad(part, mat, tile, verts, uv=(0.0, 1.0, 0.0, 1.0)):
    """One textured quad: corners bottom-left, bottom-right, top-right,
    top-left as the viewer sees it; ``uv`` the part of its tile it shows."""
    p = P.mesh(part, mat, verts, [(0, 1, 2, 3)])
    u0, u1, v0, v1 = uv
    p["tile"] = tile
    p["uvs"] = [((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
    return p


def poly(part, mat, tile, verts):
    """One flat polygon, its tile laid over its own x-y bounds."""
    xs, ys = [v[0] for v in verts], [v[1] for v in verts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    p = P.mesh(part, mat, verts, [tuple(range(len(verts)))])
    p["tile"] = tile
    p["uvs"] = [tuple(((v[0] - x0) / (x1 - x0), (v[1] - y0) / (y1 - y0)) for v in verts)]
    return p


def wedge(part, mat, tile, x, ya, yb, z0, z1, left):
    """The triangle closing one end of a sloped deck, facing out."""
    tri = [(x, ya, z0), (x, yb, z0), (x, yb, z1)]
    if left:
        tri = [tri[1], tri[0], tri[2]]
    t = P.mesh(part, mat, tri, [(0, 1, 2)])
    t["tile"] = tile
    t["uvs"] = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0))]
    return t


def cbody(part, x0, x1, ya, yb, z0, z1, c, skip=(), side="side", edge="edge", top="top", mat="paint"):
    """A box with CHAMFERED vertical corners, ``ya`` toward the player: four
    faces, four chamfers and a top, each its own quad so each takes its own
    light. A chamfer wears the ``edge`` tile, a shade lighter than the
    panels: the worn, light-catching corner of a painted cabinet.

    ``skip`` names what another part covers: "front", "back", "left",
    "right", "top". Parts are ``<part>_front`` ... and ``<part>_ChamferFR``,
    ``BR``, ``BL``, ``FL``."""
    loop = [("front", (x0 + c, ya), (x1 - c, ya)), ("ChamferFR", (x1 - c, ya), (x1, ya + c)),
            ("right", (x1, ya + c), (x1, yb - c)), ("ChamferBR", (x1, yb - c), (x1 - c, yb)),
            ("back", (x1 - c, yb), (x0 + c, yb)), ("ChamferBL", (x0 + c, yb), (x0, yb - c)),
            ("left", (x0, yb - c), (x0, ya + c)), ("ChamferFL", (x0, ya + c), (x0 + c, ya))]
    out = []
    for name, a, b in loop:
        if name in skip:
            continue
        tile = edge if name.startswith("Chamfer") else side
        out.append(quad(f"{part}_{name}", mat, tile,
                        [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]))
    if "top" not in skip:
        out.append(poly(f"{part}_top", mat, top, [(a[0], a[1], z1) for _n, a, _b in loop]))
    return out


def kick(prefix, x0, x1, y0, y1, zp, inset, tile="kick", mat="paint"):
    """The toe kick: a plinth set in ``inset`` = (sides, front) from the
    cabinet's faces, and the cabinet's underside where it overhangs it."""
    kx, ky = inset
    out = []
    for name, verts in (
            ("front", [(x0 + kx, y0 + ky, 0.0), (x1 - kx, y0 + ky, 0.0), (x1 - kx, y0 + ky, zp), (x0 + kx, y0 + ky, zp)]),
            ("right", [(x1 - kx, y0 + ky, 0.0), (x1 - kx, y1, 0.0), (x1 - kx, y1, zp), (x1 - kx, y0 + ky, zp)]),
            ("back", [(x1 - kx, y1, 0.0), (x0 + kx, y1, 0.0), (x0 + kx, y1, zp), (x1 - kx, y1, zp)]),
            ("left", [(x0 + kx, y1, 0.0), (x0 + kx, y0 + ky, 0.0), (x0 + kx, y0 + ky, zp), (x0 + kx, y1, zp)])):
        out.append(quad(f"{prefix}_Plinth_{name}", mat, tile, verts))
    out.append(quad(f"{prefix}_CabinetUnder", mat, tile,
                    [(x0, y1, zp), (x1, y1, zp), (x1, y0, zp), (x0, y0, zp)]))
    return out


def bezel(prefix, hx0, hx1, z_lo, z_hi, hole, yh, tile="bezel", mat="paint"):
    """The head's front round the tube's opening ``hole`` = (x0, x1, z0, z1):
    four strips, ``<prefix>_Bezel_B`` / ``T`` / ``L`` / ``R``."""
    bx0, bx1, bz0, bz1 = hole
    return [
        quad(f"{prefix}_Bezel_B", mat, tile, [(hx0, yh, z_lo), (hx1, yh, z_lo), (hx1, yh, bz0), (hx0, yh, bz0)]),
        quad(f"{prefix}_Bezel_T", mat, tile, [(hx0, yh, bz1), (hx1, yh, bz1), (hx1, yh, z_hi), (hx0, yh, z_hi)]),
        quad(f"{prefix}_Bezel_L", mat, tile, [(hx0, yh, bz0), (bx0, yh, bz0), (bx0, yh, bz1), (hx0, yh, bz1)]),
        quad(f"{prefix}_Bezel_R", mat, tile, [(bx1, yh, bz0), (hx1, yh, bz0), (hx1, yh, bz1), (bx1, yh, bz1)]),
    ]


def wells(prefix, hole, screen, yh, yi, tile="well", mat="paint"):
    """THE SURROUND SLOPES IN to the tube: from the opening ``hole`` at the
    head's face ``yh`` to the tube's edge ``screen`` at ``yi``. Each face
    lists its OUTER edge first, so the ``well`` tile's gradient runs light at
    the bezel to dark at the glass on all four."""
    bx0, bx1, bz0, bz1 = hole
    sx0, sx1, sz0, sz1 = screen
    return [
        quad(f"{prefix}_Well_B", mat, tile, [(bx0, yh, bz0), (bx1, yh, bz0), (sx1, yi, sz0), (sx0, yi, sz0)]),
        quad(f"{prefix}_Well_T", mat, tile, [(bx1, yh, bz1), (bx0, yh, bz1), (sx0, yi, sz1), (sx1, yi, sz1)]),
        quad(f"{prefix}_Well_L", mat, tile, [(bx0, yh, bz1), (bx0, yh, bz0), (sx0, yi, sz0), (sx0, yi, sz1)]),
        quad(f"{prefix}_Well_R", mat, tile, [(bx1, yh, bz0), (bx1, yh, bz1), (sx1, yi, sz1), (sx1, yi, sz0)]),
    ]


def curved_screen(part, screen, yi, bulge, grid=(6, 4), tile="screen", mat="glow"):
    """The tube's face: a grid over ``screen`` = (x0, x1, z0, z1) at ``yi``,
    bulging toward the player by ``bulge`` at its middle and not at all at
    its edge. The whole tile maps across it."""
    sx0, sx1, sz0, sz1 = screen
    nx, nz = grid
    verts, faces, uvs = [], [], []
    for j in range(nz + 1):
        for i in range(nx + 1):
            u, v = i / float(nx), j / float(nz)
            b = bulge * (1.0 - (2.0 * u - 1.0) ** 2) * (1.0 - (2.0 * v - 1.0) ** 2)
            verts.append((sx0 + (sx1 - sx0) * u, yi - b, sz0 + (sz1 - sz0) * v))
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
            uvs.append(((i / float(nx), j / float(nz)), ((i + 1) / float(nx), j / float(nz)),
                        ((i + 1) / float(nx), (j + 1) / float(nz)), (i / float(nx), (j + 1) / float(nz))))
    p = P.mesh(part, mat, verts, faces)
    p["tile"] = tile
    p["uvs"] = uvs
    return p


def cap(part, tile, cx, t, deck, size, mat="glow", rim=0.12):
    """A block standing off a sloped deck -- a button, a key pad: its top the
    whole ``tile``, its four sides the tile's lowest ``rim``. ``deck`` is
    ``(y_a, z_a, y_b, z_b)``, the deck's near and far edges; ``t`` is how far
    up the slope the block's middle is; ``size`` is (across, along the slope,
    standing off). Its foot is 2 mm into the deck, so the two share no plane."""
    ya, za, yb, zb = deck
    run = ((yb - ya) ** 2 + (zb - za) ** 2) ** 0.5
    sy, sz = (yb - ya) / run, (zb - za) / run           # up the slope
    ny, nz = -sz, sy                                    # off the deck
    bw, bl, bh = size
    my, mz = ya + (yb - ya) * t, za + (zb - za) * t
    base = [(cx + sx * bw / 2.0, my + sl * bl / 2.0 * sy, mz + sl * bl / 2.0 * sz)
            for sx, sl in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    foot = [(x, y - ny * 0.002, z - nz * 0.002) for x, y, z in base]
    head = [(x, y + ny * bh, z + nz * bh) for x, y, z in base]
    p = P.mesh(part, mat, foot + head,
               [(4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    p["tile"] = tile
    full = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    edge = ((0.0, 0.0), (1.0, 0.0), (1.0, rim), (0.0, rim))
    p["uvs"] = [full, edge, edge, edge, edge]
    return p
