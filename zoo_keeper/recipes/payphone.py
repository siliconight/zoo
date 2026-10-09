"""payphone recipe: a 1990s coin payphone in one of three enclosures, two
atlases, two draws.

Zoo 1.88.0, roadmap 210. Planned in pure Python by `core.payphone_forms.plan`:
the booth on a post (the default), the pedestal shroud or the wall unit; the
stainless instrument with its keys, coin slot, coin-return recess, vault door,
card and cradle; the handset on its armoured cord. `recipes/_card_atlas.
build_art` builds the PAINT tiles into one object on one painted image, and
(1.89.0) the LIT tiles -- the header's face and the hood lamp's diffuser --
into one more, its backlit material named `_Face` so Lux's power cut takes
it: the ATM's two atlases (`recipes/atm.py`). See `core/payphone_forms.py`
for the reference, the forms, the company and the lamp.

1.87.0's payphone was a half-booth of boxes in three materials and three
draws: no keypad, no coin slot, no cord, nothing printed. The walker,
2026-10-09: it "doesn't have a phone or appropriate decals". 1.88.0 drew it in
one atlas; cold run 9212 found it a silhouette at midnight, and the walker,
on the lit proposal: "yes light it".

Collision is the back panel and the instrument as one column, each side
panel, and the post: a body stands in the booth's mouth, never inside its
back. `ATT_hood` stays under the roof. The hood lamp's marker,
`LuxEmit_payphone_hood`, hangs under the diffuser with its payload --
`lux_type`, and `lux_drop`, its height above the ground -- as custom
properties, which the glTF export carries as the node's extras
(`bpylayer.markers.add_marker`). Origin on the ground under the middle
(`build_module` re-centres it); the caller at -Y.
"""
from __future__ import annotations

from ..core import payphone_forms as PF

#: Painted steel and brushed stainless, outdoors: neither card nor gloss.
ROUGHNESS = 0.55


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    got = PF.plan(w, d, h, params.get("form"), plan["color"])
    from ._card_atlas import build_art
    objs = []
    for atlas_name, lit, name in (("paint", None, "Payphone"),
                                  ("glow", (PF.GLOW_EMISSION, PF.GLOW_ALBEDO), "PayphoneGlow")):
        tiles = {k: spec for k, (a, spec) in got["tiles"].items() if a == atlas_name}
        prims = [p for p in got["prims"] if p["mat"] == atlas_name]
        o, _atlas = build_art(prims, collection, dict(plan, _tiles=tiles), streams, name,
                              roughness=ROUGHNESS, lit=lit, smooth=True)
        objs += o
    f = got["facts"]
    lamp = got["lamp"]
    print(f"[payphone] {w:.2f} x {d:.2f} x {h:.2f} form={f['form']} {f['tris']} tris, "
          f"{f['materials']} materials, lamp drop {lamp['props']['lux_drop']:.3f}")
    return {"objects": objs, "collision_boxes": got["collision"],
            "attachments": {"ATT_hood": (0.0, 0.0, got["layout"]["top"] - PF.T_ROOF),
                            lamp["name"]: lamp["at"]},
            "marker_props": {lamp["name"]: dict(lamp["props"])},
            "payphone": {"form": f["form"], "company": f["company"]}}
