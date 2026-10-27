"""night_drop recipe: a bank's night depository -- a stainless plate in the facade, a hood with a pull-down chute door
and its handle, a keyed lock, NIGHT DEPOSITORY lettered over it.

Zoo 1.138.0, from the walker's bank list, outside (the factory's docs/reference/BANK_INTERIOR_COMPS.md, researched): "a
night depository is a slot in the wall for after-hours deposits: envelopes for people, locking zip bags for businesses,
collected the next morning." Minted by `tools/new_species.py`; shaped here.

TWO SUBMISSIONS: the steel, its colours in the `Wear` vertex colour (`geometry.tint_wear`) on one material; and the
lettering, one painted atlas (`card_art` kind `teller_board`, the teller line's nameboard painter with no numbers, in
the bank's sign voice). The lettering is a PANEL, not a decal: an art front and four edges and no back face, standing
proud of the plate, the teller board's and `sign_box`'s construction.

Recipe frame: centre pivot, the wall at +Y and the plate facing the street at -Y (`wall_clock`'s convention). The
module is exactly (w, d, h): the plate is the width and the height at the back, the hood's door handle the front.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import prims as P
from ..core.night_drop_forms import (BURY, DOOR_IN, DOOR_MARGIN, DOOR_RGB, DOOR_T, HANDLE, HANDLE_RGB, HOOD_H,
                                     HOOD_RGB, HOOD_W_F, HOOD_Z_F, LABEL_COLOURS, LABEL_TEXT, LOCK_PROUD, LOCK_R,
                                     LOCK_RGB, PLATE_RGB, PLATE_T, label_box)


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    wear = plan["wear"]
    rng = streams.stream("wear")
    objs = []

    def box(name, lo, hi, rgb):
        bm = geometry.new_bm()
        c = tuple((lo[i] + hi[i]) / 2.0 for i in range(3))
        s = tuple(hi[i] - lo[i] for i in range(3))
        geometry.add_box(bm, c, s)
        o = geometry.bm_to_object(bm, name, collection, bevel=0.0, texel=1.2, rng=rng, wear=wear)
        geometry.tint_wear(o, rgb)
        objs.append(o)

    y_front, y_back = -d / 2.0, d / 2.0
    plate_front = y_back - PLATE_T
    # the plate at the wall, the module's whole width and height
    box("NightDrop_Plate", (-w / 2.0, plate_front, -h / 2.0), (w / 2.0, y_back, h / 2.0), PLATE_RGB)
    # the hood: out from the plate (its back buried in it) to the door's plane
    hw = w * HOOD_W_F
    hz = h * HOOD_Z_F
    door_front = y_front + DOOR_IN
    hood_front = door_front + DOOR_T
    box("NightDrop_Hood", (-hw / 2.0, hood_front, hz - HOOD_H / 2.0), (hw / 2.0, plate_front + BURY, hz + HOOD_H / 2.0),
        HOOD_RGB)
    # the chute door on the hood's face, its back buried in the hood
    dw, dh = hw - 2.0 * DOOR_MARGIN, HOOD_H - 2.0 * DOOR_MARGIN
    box("NightDrop_Door", (-dw / 2.0, door_front, hz - dh / 2.0), (dw / 2.0, hood_front + BURY, hz + dh / 2.0),
        DOOR_RGB)
    # the pull: a bar across the door's top on two stand-offs, its front the module's front
    hl, hs = HANDLE
    top = hz + dh / 2.0 - DOOR_MARGIN
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, y_front + hs / 2.0, top), (hl, hs, hs))
    # the stand-offs from inside the door to the bar's middle: ended 1 mm into the bar, the census read their ends
    # a millimetre off the bar's back face
    for sx in (-1.0, 1.0):
        geometry.add_box(bm, (sx * (hl / 2.0 - hs / 2.0), (y_front + hs / 2.0 + door_front + BURY) / 2.0, top),
                         (hs * 0.7, door_front + BURY - y_front - hs / 2.0, hs * 0.7))
    o = geometry.bm_to_object(bm, "NightDrop_Handle", collection, bevel=0.0, texel=1.2, rng=rng, wear=wear)
    geometry.tint_wear(o, HANDLE_RGB)
    objs.append(o)
    # the lock: a keyed cylinder in the plate under the hood
    bm = geometry.new_bm()
    lz = hz - HOOD_H / 2.0 - 0.06
    geometry.add_cylinder(bm, (0.0, plate_front - LOCK_PROUD / 2.0 + BURY / 2.0, lz), LOCK_R, LOCK_PROUD + BURY,
                          segments=12, axis="Y")
    o = geometry.bm_to_object(bm, "NightDrop_Lock", collection, bevel=0.0, texel=1.2, rng=rng, wear=wear)
    geometry.tint_wear(o, LOCK_RGB)
    objs.append(o)
    steel = materials.make_material(f"M_NightDrop_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, steel)
    # the lettering
    from ._card_atlas import build_art
    lx0, lx1, lz0, lz1, ly = label_box(w, d, h)
    quad_uv = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))]
    art = P.mesh("NightDrop_LabelFace", "art", [(lx0, ly, lz0), (lx1, ly, lz0), (lx1, ly, lz1), (lx0, ly, lz1)],
                 [(0, 1, 2, 3)])
    art["tile"] = "label"
    art["uvs"] = list(quad_uv)
    rim = P.box("NightDrop_LabelRim", "art", (lx0, ly, lz0), (lx1, plate_front, lz1))
    rim["faces"] = [f for k, f in enumerate(rim["faces"]) if k in (0, 1, 3, 5)]
    rim["tile"] = "edge"
    rim["uvs"] = list(quad_uv) * len(rim["faces"])
    tiles = {"label": {"kind": "teller_board", "w_m": lx1 - lx0, "h_m": lz1 - lz0, "text": LABEL_TEXT,
                       "colours": LABEL_COLOURS, "voice": "shop", "numbers": []},
             "edge": {"kind": "storefront_sign", "w_m": 0.1, "h_m": 0.1, "edge": True, "text": "",
                      "colours": LABEL_COLOURS}}
    got, _atlas = build_art([art, rim], collection, dict(plan, _tiles=tiles), streams, "NightDrop_Label", smooth=True)
    objs += got
    return {"objects": objs, "collision_boxes": [((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0))],
            "attachments": {"ATT_back": (0.0, d / 2.0, 0.0)}}
