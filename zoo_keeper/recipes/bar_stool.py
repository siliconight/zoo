"""bar_stool recipe: a padded round seat on a chrome column with a footring
and a domed base.

Planned in pure Python by `core.club_forms.plan_stool`, built by
`bpylayer.prim_mesh`. The column, footring and base take the genome's colour
and kind (bright bare metal) -- or a slot's material, which on an
upholstered species names the FRAME (`dna.UPHOLSTERED`); the seat is
`club_forms.SEATS[variant]`, red or black vinyl (`plastic`) or velvet, on
kinds whose delco packs tint (Pixelcoat 0.43.0); the pan under it is black
paint.
"""
from __future__ import annotations

from ..bpylayer import prim_mesh
from ..core import club_forms as CF


def _hex(c):
    return "".join("%02x" % max(0, min(255, int(round(v * 255)))) for v in c[:3])


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    variant = int((plan.get("params") or {}).get("variant", 0) or 0)
    got = CF.plan_stool(w, d, h, streams.stream("form"), variant=variant)
    kind = plan["material"]
    seat, seat_kind = got["seat_rgb"], got["seat_kind"]
    mats = {key: (f"M_BarStool_{key}_{k}", list(c), k)
            for key, (c, k) in CF.STOOL_MATERIALS.items()}
    mats["column"] = (f"M_BarStool_column_{kind}", list(plan["color"]), kind)
    mats["seat"] = (f"M_BarStool_seat_{seat_kind}_{_hex(seat)}", list(seat), seat_kind)
    objs = prim_mesh.build(got["prims"], collection, plan, streams.stream("wear"),
                           mats, texel=1.0)
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_seat": (0.0, 0.0, h)}}
