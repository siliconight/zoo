"""Exhibit layout (pure) — organize a pile of assets into a browsable scene.

Follows the game-dev "Gym / Zoo / Museum" documentation pattern (Robin-Yann
Storm): a **zoo** lays every asset out in a neat grid ("knolling") with a
scale reference so you read size at a glance and need no names; a **museum**
puts each asset on a labelled pedestal for review. Positions are computed here
from each asset's footprint (read from its meta.json), so the Godot importer
just places things — no layout logic in the engine.

Coordinates are Godot-space: X/Z ground plane, Y up, assets rest on Y=0.
"""
from __future__ import annotations

import math

PLAYER_H = 1.8   # scale reference (a person)
PED_H = 0.4      # museum pedestal height
AISLE = 1.4      # museum walking space between rows


def _footprint(a):
    return max(a["w"], a["d"])


def _order(assets):
    # knolling: group by category, biggest first, then name — neat + scannable
    return sorted(assets, key=lambda a: (a.get("category", ""),
                                         -_footprint(a), a["name"]))


def arrange(assets, scheme="zoo", cols=None, gap=0.5, scale_ref=True):
    """Return an exhibit plan: {scheme, members, props, bounds}.

    assets: [{name, glb, w, d, h, category}]. scheme: 'zoo' | 'museum'.
    """
    if not assets:
        return {"scheme": scheme, "members": [], "props": [],
                "bounds": {"x": [0, 0], "z": [0, 0]}}
    ordered = _order(assets)
    if cols is None:
        cols = max(1, round(math.sqrt(len(ordered))))
    if scheme == "museum":
        return _museum(ordered, cols, gap, scale_ref)
    return _zoo(ordered, cols, gap, scale_ref)


def _grid_xz(i, cols, cell_w, cell_d):
    r, c = divmod(i, cols)
    x = (c - (cols - 1) / 2.0) * cell_w
    z = r * cell_d
    return round(x, 4), round(z, 4)


def _bounds(points, pad=0.5):
    xs = [p[0] for p in points] or [0.0]
    zs = [p[1] for p in points] or [0.0]
    return {"x": [round(min(xs) - pad, 3), round(max(xs) + pad, 3)],
            "z": [round(min(zs) - pad, 3), round(max(zs) + pad, 3)]}


def _zoo(ordered, cols, gap, scale_ref):
    # uniform cell = biggest footprint, so the grid stays neat (knolled)
    cell_w = max(a["w"] for a in ordered) + gap
    cell_d = max(a["d"] for a in ordered) + gap
    members, pts = [], []
    for i, a in enumerate(ordered):
        x, z = _grid_xz(i, cols, cell_w, cell_d)
        pts.append((x, z))
        members.append({"name": a["name"], "glb": a["glb"],
                        "category": a.get("category", ""),
                        "pos": [x, 0.0, z], "rot_y": 0.0})
    props = []
    if scale_ref:
        # a person-height post and a 1 m cube, just left of the grid
        x0 = -((cols - 1) / 2.0) * cell_w - cell_w
        props.append({"type": "marker", "label": "1.8 m",
                      "pos": [round(x0, 3), 0.0, 0.0],
                      "size": [0.4, PLAYER_H, 0.4]})
        props.append({"type": "marker", "label": "1 m",
                      "pos": [round(x0, 3), 0.0, round(cell_d, 3)],
                      "size": [1.0, 1.0, 1.0]})
        pts.append((x0, 0.0))
    return {"scheme": "zoo", "members": members, "props": props,
            "bounds": _bounds(pts)}


def _museum(ordered, cols, gap, scale_ref):
    cell_w = max(a["w"] for a in ordered) + gap
    row_d = max(a["d"] for a in ordered) + AISLE
    members, props, pts = [], [], []
    for i, a in enumerate(ordered):
        r, c = divmod(i, cols)
        x = round((c - (cols - 1) / 2.0) * cell_w, 4)
        z = round(r * row_d, 4)
        pts.append((x, z))
        pw = round(a["w"] * 1.3 + 0.1, 4)
        pd = round(a["d"] * 1.3 + 0.1, 4)
        props.append({"type": "pedestal", "pos": [x, 0.0, z],
                      "size": [pw, PED_H, pd]})
        members.append({"name": a["name"], "glb": a["glb"],
                        "category": a.get("category", ""),
                        "pos": [x, PED_H, z], "rot_y": 0.0})
        dims = f'{a["w"]:.2f}x{a["d"]:.2f}x{a["h"]:.2f}m'
        props.append({"type": "label",
                      "text": f'{a["name"]}  ({dims})',
                      "pos": [x, round(PED_H + a["h"] + 0.15, 3), z]})
    if scale_ref:
        x0 = -((cols - 1) / 2.0) * cell_w - cell_w
        props.append({"type": "marker", "label": "1.8 m",
                      "pos": [round(x0, 3), 0.0, 0.0],
                      "size": [0.4, PLAYER_H, 0.4]})
        pts.append((x0, 0.0))
    return {"scheme": "museum", "members": members, "props": props,
            "bounds": _bounds(pts)}
