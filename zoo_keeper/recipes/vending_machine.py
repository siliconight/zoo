"""vending_machine recipe: a 1990s soda machine with a backlit brand panel.

REBUILT, 0.87.0. The walker, with a reference of a modded Deus Ex machine:
"vending machines should glow", with fake Delco brands on them. 0.86.0's
machine was a box with a tinted slab on its front, unlit, and it built 45 mm
deeper than its slot. `core/vending_forms.py` records that measurement and
decides every size, the brand and every pixel of the artwork; this file only
executes it.

Parts, in the module frame (Z up, metres, centre pivot, front toward -Y):

  * `Vending_Cabinet`, `Vending_Door`: the brand's paint (a prompt colour
    paints them instead). The door is one closed solid built from a grid of
    cells with the panel, column and flap apertures left out, so it has no
    internal faces and nothing inside it to z-fight;
  * `Vending_Panel`: the backlit artwork, `M_Vending_<art>_Face`;
  * `Vending_Buttons`: six lit selection buttons, each face one product's
    label; `Vending_DisplayLens`: the lit price. Both `M_Vending_<art>_Lens`;
  * `Vending_ColumnPlate`, `Vending_Display` (the bezel), `Vending_Slots`
    (coin slot, bill mouth, coin-return mouth), `Vending_Bin`,
    `Vending_Flap`, `Vending_Kick`: black trim;
  * `Vending_CoinMech`, `Vending_CoinReturn`, `Vending_Lock`: bare metal.

FACETED ON PURPOSE: every edge hard (`shade_by_angle(bm, 1.0)`).

Collision is the slot's box: a body walks into a machine, not between its
buttons.
"""
from __future__ import annotations

import bmesh

from ..bpylayer import geometry, materials
from ..core import vending_forms as vf


def _box(bm, b):
    x0, x1, y0, y1, z0, z1 = b
    geometry.add_box(bm, ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0),
                     (x1 - x0, y1 - y0, z1 - z0))


def _door(bm, L):
    """The door slab as one closed solid over the layout's cell grid."""
    xs, zs, filled = vf.door_cells(L)
    y0, y1 = L["door"]["y"]
    front, back = {}, {}

    def v(store, i, j, y):
        if (i, j) not in store:
            store[(i, j)] = bm.verts.new((xs[i], y, zs[j]))
        return store[(i, j)]

    ni, nj = len(filled), len(filled[0])
    for i in range(ni):
        for j in range(nj):
            if not filled[i][j]:
                continue
            # corners counter-clockwise seen from the front (x right, z up)
            corners = ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))
            bm.faces.new([v(front, a, b, y0) for a, b in corners])
            bm.faces.new([v(back, a, b, y1) for a, b in reversed(corners)])
            # walls where the neighbour is not door
            for (di, dj), (ca, cb) in (((0, -1), ((i, j), (i + 1, j))),
                                       ((1, 0), ((i + 1, j), (i + 1, j + 1))),
                                       ((0, 1), ((i + 1, j + 1), (i, j + 1))),
                                       ((-1, 0), ((i, j + 1), (i, j)))):
                a, b = i + di, j + dj
                if 0 <= a < ni and 0 <= b < nj and filled[a][b]:
                    continue
                bm.faces.new((v(front, *cb, y0), v(front, *ca, y0),
                              v(back, *ca, y1), v(back, *cb, y1)))


def _flap(bm, f):
    x0, x1 = f["x"]
    (zt, yt), (zb, yb), t = f["top"], f["bottom"], f["t"]
    p = [bm.verts.new((x, y, z)) for x in (x0, x1)
         for (z, y) in ((zb, yb), (zt, yt), (zt, yt + t), (zb, yb + t))]
    # p[0..3] at x0: bottom-front, top-front, top-back, bottom-back; p[4..7] at x1
    for q in ((0, 4, 5, 1), (3, 2, 6, 7), (1, 5, 6, 2), (0, 3, 7, 4),
              (0, 1, 2, 3), (4, 7, 6, 5)):
        bm.faces.new([p[k] for k in q])


def _map_uvs(bm, regions, dark):
    """Front faces (normal toward -Y) take the region whose x/z box holds
    their centre, mapped edge to edge; every other face samples ``dark``."""
    uv = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    du, dv = (dark[0] + dark[2]) / 2.0, (dark[1] + dark[3]) / 2.0
    for face in bm.faces:
        c = face.calc_center_median()
        hit = None
        if face.normal.y < -0.9:
            for (x0, x1, z0, z1), r in regions:
                if x0 - 1e-6 <= c.x <= x1 + 1e-6 and z0 - 1e-6 <= c.z <= z1 + 1e-6:
                    hit = ((x0, x1, z0, z1), r)
                    break
        for loop in face.loops:
            if hit is None:
                loop[uv].uv = (du, dv)
                continue
            (x0, x1, z0, z1), (u0, v0, u1, v1) = hit
            co = loop.vert.co
            loop[uv].uv = (u0 + (co.x - x0) / (x1 - x0) * (u1 - u0),
                           v0 + (co.z - z0) / (z1 - z0) * (v1 - v0))


def build(plan, streams, collection):
    L = vf.resolve(plan, streams)
    w, d, h = L["w"], L["d"], L["h"]
    wear, ambient = plan["wear"], plan.get("ambient", 0.0)
    rng = streams.stream("vending_wear")
    A = L["art"]
    size = A["size"]

    B = {k: geometry.new_bm() for k in (
        "cabinet", "door", "panel", "column_plate", "display", "display_lens",
        "coin_mech", "slots", "buttons", "coin_return", "lock", "bin", "flap", "kick")}
    _box(B["cabinet"], L["cabinet"])
    _door(B["door"], L)
    _box(B["panel"], L["panel"])
    _box(B["column_plate"], L["column_plate"])
    _box(B["display"], L["display_bezel"])
    _box(B["display_lens"], L["display_lens"])
    _box(B["coin_mech"], L["coin_mech"])
    _box(B["coin_mech"], L["reject"])
    for k in ("coin_slot", "bill_mouth", "return_mouth"):
        _box(B["slots"], L[k])
    for b in L["buttons"]:
        _box(B["buttons"], b)
    _box(B["coin_return"], L["coin_return"])
    _box(B["lock"], L["lock"])
    _box(B["lock"], L["lock_handle"])
    _box(B["bin"], L["bin"])
    _flap(B["flap"], L["flap"])
    _box(B["kick"], L["kick"])

    # --- materials ---------------------------------------------------------------
    kind = plan["material"]
    paint = list(L["paint"])
    hexof = materials._tint_key
    body = materials.make_material(f"M_Vending_body_{hexof(paint)}", paint, kind)
    black = materials.make_material(f"M_Vending_trim_{hexof(vf.BLACK)}",
                                    list(vf.BLACK), "metal_painted")
    chrome = materials.make_material(f"M_Vending_chrome_{hexof(vf.CHROME)}",
                                     list(vf.CHROME), "metal_bare")
    image = materials.image_from_png("vending_" + A["name"], A["canvas"].png())
    # `lit` 0 is a machine with its plug pulled: the same artwork, no glow.
    # It was declared in the genome since the species shipped and read by
    # nothing until 0.87.0.
    lit_on = float((plan.get("params") or {}).get("lit", 1)) > 0.0
    tag = A["name"] if lit_on else A["name"] + "_unlit"
    face = materials.make_backlit_material(f"M_Vending_{tag}_Face", image,
                                           vf.PANEL_EMISSION if lit_on else 0.0,
                                           vf.PANEL_ALBEDO)
    lens = materials.make_backlit_material(f"M_Vending_{tag}_Lens", image,
                                           vf.LENS_EMISSION if lit_on else 0.0,
                                           vf.LENS_ALBEDO)
    rects = A["rects"]
    dark = vf.uv_rect(rects["dark"], size)
    ax = L["apertures"]["panel"]
    lit = {
        "panel": ([((ax[0], ax[1], ax[2], ax[3]), vf.uv_rect(rects["panel"], size))], face),
        "buttons": ([((b[0], b[1], b[4], b[5]), vf.uv_rect(rects[f"button_{i}"], size))
                     for i, b in enumerate(L["buttons"])], lens),
        "display_lens": ([((L["display_lens"][0], L["display_lens"][1],
                            L["display_lens"][4], L["display_lens"][5]),
                           vf.uv_rect(rects["display"], size))], lens),
    }
    names = {"cabinet": ("Vending_Cabinet", body), "door": ("Vending_Door", body),
             "panel": ("Vending_Panel", face), "column_plate": ("Vending_ColumnPlate", black),
             "display": ("Vending_Display", black),
             "display_lens": ("Vending_DisplayLens", lens),
             "coin_mech": ("Vending_CoinMech", chrome), "slots": ("Vending_Slots", black),
             "buttons": ("Vending_Buttons", lens),
             "coin_return": ("Vending_CoinReturn", chrome), "lock": ("Vending_Lock", chrome),
             "bin": ("Vending_Bin", black), "flap": ("Vending_Flap", black),
             "kick": ("Vending_Kick", black)}
    objs = []
    for key, bm in B.items():
        name, mat = names[key]
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        geometry.shade_by_angle(bm, 1.0)
        if key in lit:
            _map_uvs(bm, lit[key][0], dark)
            # a lit face does not grime; a white COLOR_0 keeps it neutral
            geometry.wear_colors(bm, rng, 0.0)
        else:
            geometry.cube_project_uv(bm, 1.0)
            geometry.wear_colors(bm, rng, wear * (0.5 if mat is chrome else 1.0),
                                 ambient=ambient)
        obj = geometry.bm_to_object(bm, name, collection, finish=False)
        materials.assign([obj], mat)
        objs.append(obj)

    f = L["apertures"]["flap"]
    print(f"[vending] brand={L['brand']} art={A['name']} products={','.join(A['products'])} "
          f"panel={L['panel_m'][0]:.3f}x{L['panel_m'][1]:.3f} m")
    return {"objects": objs,
            "collision_boxes": [((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0))],
            "attachments": {"ATT_tray": ((f[0] + f[1]) / 2.0, -d / 2.0, (f[2] + f[3]) / 2.0)},
            "vending": {"brand": L["brand"], "products": A["products"], "art": A["name"]}}
