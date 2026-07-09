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

Non-collision by construction: :func:`build` returns an empty
``collision_boxes`` list, so ``build.build_dressing`` never emits a
``-colonly`` proxy. The DC greybox collision stays authoritative; covers are
visual only. UVs are assigned to the order's ``uv_region`` on Patina's trim
atlas so the strip reads as the right trim piece.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core.dressing import strip_size


def build(plan, streams, collection):
    """Build one cover strip. ``plan`` is a dressing plan (see core.dressing).

    The dressing path always supplies ``plan['order']``; if this recipe is ever
    reached via the prompt/DNA path (no order), it falls back to a default
    edge-strip so it never crashes.
    """
    order = plan.get("order") or {"cover": "edge_strip", "size": 0.6}
    cover = order.get("cover", "edge_strip")
    rng = streams.stream("wear")
    w, d, h = strip_size(cover, order.get("size", 0.6))

    bm = geometry.new_bm()
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
