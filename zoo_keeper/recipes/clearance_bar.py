"""clearance_bar recipe: a drive-through lane's clearance bar -- the "headache bar" -- two safety-yellow posts, a beam
across the lane, a bar hung on two chains at the posted clearance, and CLEARANCE lettered on a plate on the bar.

Zoo 1.139.0, from the walker's "do some more research, make it look better" of the bank's drive-up: a bank drive-up
plan details one at the lane's entry (a 2022 Albuquerque plan: 'PROPOSED NEW CLEARANCE "HEADACHE BAR"'). The bar
hangs at `CLEAR`, 9 ft: lower than the canopy's 3.8 m on purpose, the posted figure a truck's driver reads before the
roof does. Minted by `tools/new_species.py`; shaped here.

TWO SUBMISSIONS: the steel, its colours in the `Wear` vertex colour on one material; the plate, one atlas (`card_art`
kind `teller_board`, the nameboard painter, black on safety yellow).

Recipe frame: centre pivot, the lane along Y, the plate facing -Y (the lane's entry). The module is exactly (w, d, h):
the posts are the width and the height, their section the depth.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import prims as P

POST = 0.20              # a post's width across the lane; its depth is the slot's, so the module is its slot
CLEAR = 2.74             # the bar's underside over the ground: 9 ft
BAR = 0.12               # the bar's section
BEAM = 0.18              # the beam's depth under the posts' tops
CHAIN = 0.03
BAR_END = 0.15           # the bar's ends inside the posts' inner faces
CHAIN_IN = 0.30          # a chain in from the bar's end
PLATE = (1.6, 0.22)      # the plate's width and height: the words set at 0.17 m and up
PLATE_T = 0.06
PLATE_TEXT = "CLEARANCE 9 FT"
BURY = 0.004
SHY = 0.003

YELLOW = (0.95, 0.74, 0.08)
CHAIN_RGB = (0.14, 0.14, 0.15)
PLATE_COLOURS = ((242, 190, 20), (20, 20, 20), (16, 16, 16))


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    wear = plan["wear"]
    rng = streams.stream("wear")
    objs = []
    floor, top = -h / 2.0, h / 2.0

    def finish(bm, name, rgb):
        o = geometry.bm_to_object(bm, name, collection, bevel=0.0, texel=1.2, rng=rng, wear=wear)
        geometry.tint_wear(o, rgb)
        objs.append(o)

    def box(bm, lo, hi):
        geometry.add_box(bm, tuple((lo[i] + hi[i]) / 2.0 for i in range(3)), tuple(hi[i] - lo[i] for i in range(3)))

    # the posts: the module's width, depth and height (posts a section short of the depth measured the module 0.225
    # deep in a 0.25 slot, and validation failed it)
    bm = geometry.new_bm()
    for sx in (-1.0, 1.0):
        x0, x1 = sorted((sx * w / 2.0, sx * (w / 2.0 - POST)))
        box(bm, (x0, -d / 2.0, floor), (x1, d / 2.0, top))
    # the beam between them, its ends in the posts, its top and sides SHY of the posts' planes
    ix = w / 2.0 - POST
    box(bm, (-ix - BURY, -d / 2.0 + SHY, top - BEAM), (ix + BURY, d / 2.0 - SHY, top - SHY))
    # the bar, hung at the clearance
    bx = ix - BAR_END
    bz0 = floor + CLEAR
    box(bm, (-bx, -BAR / 2.0, bz0), (bx, BAR / 2.0, bz0 + BAR))
    finish(bm, "ClearanceBar_Steel", YELLOW)
    # two chains from the bar's top into the beam's underside
    bm = geometry.new_bm()
    for sx in (-1.0, 1.0):
        cx = sx * (bx - CHAIN_IN)
        box(bm, (cx - CHAIN / 2.0, -CHAIN / 2.0, bz0 + BAR - BURY), (cx + CHAIN / 2.0, CHAIN / 2.0, top - BEAM + BURY))
    finish(bm, "ClearanceBar_Chain", CHAIN_RGB)
    steel = materials.make_material(f"M_ClearanceBar_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, steel)
    # the plate on the bar's entry face: its front the module's -Y, its back SHY off the bar's face, centred on the bar
    from ._card_atlas import build_art
    pw, ph = PLATE
    zc = bz0 + BAR / 2.0
    y0, y1 = -d / 2.0, -BAR / 2.0 - SHY
    quad_uv = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))]
    art = P.mesh("ClearanceBar_PlateFace", "art", [(-pw / 2.0, y0, zc - ph / 2.0), (pw / 2.0, y0, zc - ph / 2.0),
                                                   (pw / 2.0, y0, zc + ph / 2.0), (-pw / 2.0, y0, zc + ph / 2.0)],
                 [(0, 1, 2, 3)])
    art["tile"] = "plate"
    art["uvs"] = list(quad_uv)
    rim = P.box("ClearanceBar_PlateRim", "art", (-pw / 2.0, y0, zc - ph / 2.0), (pw / 2.0, y1, zc + ph / 2.0))
    # every face but the front, which is the art: its back faces the bar, SHY off it
    rim["faces"] = [f for k, f in enumerate(rim["faces"]) if k != 2]
    rim["tile"] = "edge"
    rim["uvs"] = list(quad_uv) * len(rim["faces"])
    tiles = {"plate": {"kind": "teller_board", "w_m": pw, "h_m": ph, "text": PLATE_TEXT, "colours": PLATE_COLOURS,
                       "voice": "shop", "numbers": []},
             "edge": {"kind": "storefront_sign", "w_m": 0.1, "h_m": 0.1, "edge": True, "text": "",
                      "colours": PLATE_COLOURS}}
    got, _atlas = build_art([art, rim], collection, dict(plan, _tiles=tiles), streams, "ClearanceBar_Plate",
                            smooth=True)
    objs += got
    # a body walks under the bar; the posts stop it
    posts = [((-w / 2.0, -d / 2.0, floor), (-ix, d / 2.0, top)), ((ix, -d / 2.0, floor), (w / 2.0, d / 2.0, top))]
    return {"objects": objs, "collision_boxes": posts, "attachments": {}}
