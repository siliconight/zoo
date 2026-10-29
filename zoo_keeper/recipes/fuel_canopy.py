"""fuel_canopy recipe: a filling station's canopy deck -- a fascia band in the store's colour all round, a stripe in
its rule colour along the fascia, a light soffit under it and a roof cap over it.

Minted by `tools/new_species.py`; shaped here (the factory's roadmap 324). The walker, 2026-10-29, of the game's
vertical slice: "Things still look simple, and computer made". Deli Counter's specs author the canopy as a volume,
`canopy_roof`, and until this species nothing built it: the forecourt's landmark shipped as its greybox box, a grey
slab with the canopy's lights under it (the factory's docs/findings/slice_look/, slice 6).

THE COLOURS ARE THE STORE'S. A 1990s canopy's fascia is the brand's: the price pylon at the same frontage paints
FLAPPAHS in `price_pylon_forms.COLOURWAYS` by its variant, and the deck takes the same variant's field for the fascia
and its rule for the stripe, so the canopy and the sign out front are one brand.

ONE MATERIAL: fascia, stripe, soffit and cap are colour only, in the `Wear` vertex colour (`geometry.tint_wear`), as
`drive_up_canopy` does: one submission for the whole deck.

THE ENVELOPE IS THE SLOT'S, EXACTLY: the stripe's outer faces are the module's sides; the fascia stands
`STRIPE_PROUD` inside them; the soffit's underside is the module's bottom face -- the plane Deli Counter's canopy
lights hang from (`lights._CANOPY_DROP`), so Lux's lamps stay where they were. The corners close as the coping's do:
the N and S fascia and stripes run the whole width, the E and W stop at their backs. Nothing is coplanar with
anything it overlaps: the soffit and the cap ABUT the fascia ring's inner faces, the cap `SHY` under its top, and the
stripes are buried `BURY` into the fascia they stand on.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core.canopy_forms import CAP_RGB, SOFFIT_RGB, boxes, colours, hidden


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    wear = plan["wear"]
    variant = int((plan.get("module") or {}).get("variant") or (plan.get("params") or {}).get("variant") or 0)
    rng = streams.stream("wear")
    fascia_rgb, stripe_rgb = colours(variant)
    rgb = {"Fascia": fascia_rgb, "FasciaEnds": fascia_rgb, "Stripe": stripe_rgb, "StripeEnds": stripe_rgb,
           "Soffit": SOFFIT_RGB, "Cap": CAP_RGB}
    objs = []
    by = {}
    for name, lo, hi in boxes(w, d, h):
        by.setdefault(name, []).append((lo, hi))
    for name, parts in by.items():
        bm = geometry.new_bm()
        for lo, hi in parts:
            geometry.add_box(bm, tuple((lo[i] + hi[i]) / 2.0 for i in range(3)),
                             tuple(hi[i] - lo[i] for i in range(3)))
        geometry.drop_faces(bm, lambda nrm, part=name: hidden(part, nrm))
        o = geometry.bm_to_object(bm, f"FuelCanopy_{name}", collection, bevel=0.0, texel=1.2, rng=rng, wear=wear)
        geometry.tint_wear(o, rgb[name])
        objs.append(o)
    surface = materials.make_material(f"M_FuelCanopy_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, surface)
    return {"objects": objs, "collision_boxes": [((-w / 2, -d / 2, -h / 2), (w / 2, d / 2, h / 2))],
            "attachments": {"ATT_top": (0.0, 0.0, h / 2)}}
