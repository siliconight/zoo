"""Connectors (pure) — the "Lego" anchoring system.

Every asset already exports named ATT_* markers. This turns them into typed
connectors so props snap onto players and levels the way a Lego stud only fits
an anti-stud:

- a SOCKET is a point on a host (a character's head, a table's surface, a
  wall's edge) with a position, a facing (yaw), and a TYPE.
- an ANCHOR is the point on a prop that mates into a socket, with its own type
  (a helmet anchors by its "head" type, a briefcase by "grip").
- they connect only when their types are COMPATIBLE, and snapping aligns the
  prop's anchor onto the socket's transform.

Positions/yaw are Godot-space (X/Z ground plane, Y up, yaw about Y in degrees).
The Godot side does the same alignment with Transform3D; this module is the
testable reference + the data model baked into meta.json.
"""
from __future__ import annotations

import math

# canonical socket/anchor types
CHARACTER_TYPES = {"head", "hand_l", "hand_r", "back", "hip", "feet", "chest"}
WORLD_TYPES = {"surface", "floor", "wall", "ceiling"}
PROP_TYPES = {"lid", "cap", "cup"}

DEFAULT_ANCHOR_TYPE = "surface"

# an anchor type may mate with more than its exact socket type
_ALIASES = {
    "grip": {"hand_l", "hand_r"},
    "hand_l": {"grip"},
    "hand_r": {"grip"},
    "cup": {"surface"},        # a cup sits in a holder OR on any surface
    "surface": {"floor"},      # something "surface"-anchored also rests on floor
}


def compatible(socket_type: str, anchor_type: str) -> bool:
    """Does an anchor of anchor_type fit a socket of socket_type?"""
    if socket_type == anchor_type:
        return True
    if anchor_type in _ALIASES.get(socket_type, set()):
        return True
    if socket_type in _ALIASES.get(anchor_type, set()):
        return True
    return False


def _rot_y(x: float, z: float, deg: float):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (c * x + s * z, -s * x + c * z)


def _clamp_area(x: float, z: float, size) -> tuple:
    hw, hd = size[0] / 2.0, size[1] / 2.0
    return (max(-hw, min(hw, x)), max(-hd, min(hd, z)))


def _nearest_grid(x: float, z: float, size, cell) -> tuple:
    cx = cell[0] if cell[0] else 1e9
    cz = cell[1] if cell[1] else 1e9
    gx = round(x / cx) * cx
    gz = round(z / cz) * cz
    return _clamp_area(gx, gz, size)


def resolve_socket_offset(socket: dict, hit_local=(0.0, 0.0)) -> tuple:
    """Where on the socket plane the prop lands, as an (x, z) offset in the
    socket's local frame, given where the user pointed (hit_local).

    point: always the socket origin.  area: clamp the hit to the region.
    grid: snap the hit to the nearest cell (Lego studs), clamped to the region.
    """
    shape = socket.get("shape", "point")
    if shape == "point":
        return (0.0, 0.0)
    size = socket.get("size", [0.0, 0.0])
    hx, hz = hit_local
    if shape == "grid":
        return _nearest_grid(hx, hz, size, socket.get("cell", [0.1, 0.1]))
    return _clamp_area(hx, hz, size)


def snap_pose(socket: dict, anchor: dict, mate: str = "coincide",
              hit_local=(0.0, 0.0)) -> dict:
    """Placement {pos, yaw} for a prop so its anchor mates to a socket.

    mate='coincide' (wearables/props): anchor lands on the socket.
    mate='butt' (level modules): prop flipped 180 so edges face and join.
    hit_local lets area/grid sockets place the prop where the user pointed
    (in the socket's local XZ); ignored for point sockets.
    """
    ox, oz = resolve_socket_offset(socket, hit_local)
    s_pos = socket.get("pos", [0.0, 0.0, 0.0])
    a_pos = anchor.get("pos", [0.0, 0.0, 0.0])
    s_yaw = float(socket.get("yaw", 0.0))
    a_yaw = float(anchor.get("yaw", 0.0))
    flip = 180.0 if mate == "butt" else 0.0
    prop_yaw = s_yaw - a_yaw + flip
    # the local offset rotates into the host frame by the socket's yaw
    orx, orz = _rot_y(ox, oz, s_yaw)
    sx, sy, sz = s_pos[0] + orx, s_pos[1], s_pos[2] + orz
    arx, arz = _rot_y(a_pos[0], a_pos[2], prop_yaw)
    return {
        "pos": [round(sx - arx, 5), round(sy - a_pos[1], 5),
                round(sz - arz, 5)],
        "yaw": round(prop_yaw % 360.0, 5),
    }


def build_connectors(genome: dict, positions: dict, dims: dict = None) -> dict:
    """Assemble a specimen's connector block from the genome's declaration and
    the recipe's attachment positions. Goes into meta.json.

    A socket declaration may be a plain type string, or an object:
      {"type": "surface", "shape": "area", "size_rel": [0.85, 0.85]}
      {"type": "wall", "shape": "grid", "size": [2, 2], "cell": [0.5, 0.5]}
    size_rel scales the specimen's width/depth into an absolute size.
    """
    decl = genome.get("connectors", {}) or {}
    a = decl.get("anchor", {}) or {}
    anchor = {
        "type": a.get("type", DEFAULT_ANCHOR_TYPE),
        "pos": [round(float(v), 5) for v in a.get("pos", [0.0, 0.0, 0.0])],
        "yaw": float(a.get("yaw", 0.0)),
    }
    sock_decls = decl.get("sockets", {}) or {}
    dims = dims or {}
    sockets = []
    for name in sorted(positions):
        d = sock_decls.get(name, "surface")
        if isinstance(d, str):
            d = {"type": d}
        sock = {
            "name": name,
            "type": d.get("type", "surface"),
            "pos": [round(float(v), 5) for v in positions[name]],
            "yaw": float(d.get("yaw", 0.0)),
            "shape": d.get("shape", "point"),
        }
        size = d.get("size")
        if size is None and "size_rel" in d:
            rel = d["size_rel"]
            size = [round(float(dims.get("width", 0.0)) * rel[0], 4),
                    round(float(dims.get("depth", 0.0)) * rel[1], 4)]
        if size is not None:
            sock["size"] = size
        if sock["shape"] == "grid" and "cell" in d:
            sock["cell"] = d["cell"]
        sockets.append(sock)
    return {"anchor": anchor, "sockets": sockets}


def find_matches(host_connectors: dict, prop_connectors: dict) -> list:
    """Sockets on a host that the prop's anchor can mate to (by type)."""
    anchor_type = prop_connectors.get("anchor", {}).get("type",
                                                        DEFAULT_ANCHOR_TYPE)
    return [s for s in host_connectors.get("sockets", [])
            if compatible(s.get("type", "surface"), anchor_type)]
