"""dress_cover recipe: a thin, non-collision facade cover from a Patina order.

This is the Zoo half of the Patina v0.11 dressing contract
(``docs/DRESSING_CONTRACT.md`` in Patina). Patina emits a trim atlas plus a
``<building>.dressing.json`` of per-anchor build orders; Zoo builds the cover
geometry. A cover is deliberately trivial geometry — a thin proud strip laid
over the greybox at an anchor — because the whole point of the contract is that
Patina places and skins while Zoo only supplies the mesh.

Cover kinds (from the order's ``cover`` field), each a thin box oriented by the
anchor normal:

* ``edge_strip``  — a capping strip along a roofline edge (normal up).
* ``base_course`` — a foundation band at a wall foot (normal outward).
* ``curb``        — a low ground-meet strip (normal up).
* ``conduit_run`` — a slim vertical conduit up a wall to a light (normal out).
* ``panel_field``  — one thin plate of a wall panel grid (normal outward;
  Patina v0.17 emits one order per grid cell, sized by ``size2``).
* ``gutter_run``   — a horizontal eave run spanning its wall module exactly.
* ``pilaster``     — a vertical proud strip at a module seam; reads as a
  column at sixth-gen fidelity (``size2`` = [width, wall height]).
* ``frame``        — four thin strips around a doorway/window opening
  (``size2`` = the exact opening rect from DC's ``fit.openings``;
  ``frame_width`` from the order).

Non-collision by construction: :func:`build` returns an empty
``collision_boxes`` list, so ``build.build_dressing`` never emits a
``-colonly`` proxy. The DC greybox collision stays authoritative; covers are
visual only.

CORRECTED CLAIM. This docstring used to say "UVs are assigned to the order's
``uv_region`` on Patina's trim atlas so the strip reads as the right trim
piece." They are not, and never were. UVs come from
``geometry.bm_to_object(..., texel=1.2)`` -> ``cube_project_uv``, the same
world-metres box projection every other Zoo mesh gets. ``uv_region`` is read
from the order and returned in this function's result dict, where nothing
reads it -- ``build.build_dressing`` uses ``result["objects"]`` only. The
atlas PNG is likewise recorded into ``<stem>_dressing.built.json`` and never
opened. Measured on a shipped level: 2255 cover primitives, all carrying
TEXCOORD_0 from the cube projection, one material, zero images.

That is not a gap to fill here. Pixelcoat "owns the themed skin library that
Zoo kits resolve against" (its README), and trim sheets are on its own feature
list -- so a cover gets its surface the same way a wall does, by resolving a
pack for its material kind through :func:`materials.make_material`. Patina
places; Pixelcoat skins. The ``uv_region`` field stays in the contract because
Patina still emits it and a future atlas-based path may want it; it is
carried, not used.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core.dressing import frame_strips, strip_size


def build(plan, streams, collection):
    """Build one cover strip. ``plan`` is a dressing plan (see core.dressing).

    The dressing path always supplies ``plan['order']``; if this recipe is ever
    reached via the prompt/DNA path (no order), it falls back to a default
    edge-strip so it never crashes.
    """
    order = plan.get("order") or {"cover": "edge_strip", "size": 0.6}
    cover = order.get("cover", "edge_strip")
    rng = streams.stream("wear")

    bm = geometry.new_bm()
    if cover == "frame":
        size2 = order.get("size2") or [1.0, 2.1]
        proud = 0.05
        for center, size in frame_strips(float(size2[0]), float(size2[1]),
                                         float(order.get("frame_width",
                                                         0.12)), proud):
            geometry.add_box(bm, center, size)
    else:
        w, d, h = strip_size(cover, order.get("size", 0.6),
                             order.get("size2"))
        geometry.add_box(bm, (0.0, 0.0, 0.0), (w, d, h))
    obj = geometry.bm_to_object(
        bm, f"Cover_{cover}", collection,
        bevel=plan.get("bevel", 0.002), texel=1.2, rng=rng,
        wear=plan.get("wear", 0.15))

    mat = materials.make_material(
        f"M_Cover_{plan['material']}", plan["color"], plan["material"])
    materials.assign([obj], mat)

    # No collision boxes -> build.build_dressing emits no -colonly proxy.
    return {"objects": [obj], "collision_boxes": [], "attachments": {},
            "uv_region": order.get("uv_region")}
