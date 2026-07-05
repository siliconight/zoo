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


def snap_pose(socket: dict, anchor: dict, mate: str = "coincide") -> dict:
    """Placement {pos, yaw} for a prop so its anchor mates to a socket.

    mate='coincide' (wearables/props): anchor lands exactly on the socket.
    mate='butt' (level modules): prop is flipped 180 so edges face and join.
    """
    s_pos = socket.get("pos", [0.0, 0.0, 0.0])
    a_pos = anchor.get("pos", [0.0, 0.0, 0.0])
    s_yaw = float(socket.get("yaw", 0.0))
    a_yaw = float(anchor.get("yaw", 0.0))
    flip = 180.0 if mate == "butt" else 0.0
    prop_yaw = s_yaw - a_yaw + flip
    rx, rz = _rot_y(a_pos[0], a_pos[2], prop_yaw)
    return {
        "pos": [round(s_pos[0] - rx, 5), round(s_pos[1] - a_pos[1], 5),
                round(s_pos[2] - rz, 5)],
        "yaw": round(prop_yaw % 360.0, 5),
    }


def build_connectors(genome: dict, positions: dict) -> dict:
    """Assemble a specimen's connector block from the genome's declaration and
    the recipe's attachment positions. Goes into meta.json.

    genome may declare:
      "connectors": {"anchor": {"type": "head", "pos": [..], "yaw": 0},
                     "sockets": {"ATT_surface_center": "surface"}}
    """
    decl = genome.get("connectors", {}) or {}
    a = decl.get("anchor", {}) or {}
    anchor = {
        "type": a.get("type", DEFAULT_ANCHOR_TYPE),
        "pos": [round(float(v), 5) for v in a.get("pos", [0.0, 0.0, 0.0])],
        "yaw": float(a.get("yaw", 0.0)),
    }
    sock_types = decl.get("sockets", {}) or {}
    sockets = []
    for name in sorted(positions):
        pos = positions[name]
        sockets.append({
            "name": name,
            "type": sock_types.get(name, "surface"),
            "pos": [round(float(v), 5) for v in pos],
            "yaw": 0.0,
        })
    return {"anchor": anchor, "sockets": sockets}


def find_matches(host_connectors: dict, prop_connectors: dict) -> list:
    """Sockets on a host that the prop's anchor can mate to (by type)."""
    anchor_type = prop_connectors.get("anchor", {}).get("type",
                                                        DEFAULT_ANCHOR_TYPE)
    return [s for s in host_connectors.get("sockets", [])
            if compatible(s.get("type", "surface"), anchor_type)]
