"""counter recipe: generic service counter (deli / pharmacy / pawn front line).

Solid body, proud countertop overhanging the customer side (-Y), recessed
kick base, optional staff-side under-shelf. Origin at floor center. The
generic sibling of the bank teller_line — same posture, no security barrier.

STOCK (0.84.0). The ``stock`` param -- ``none`` by default, which builds
exactly the counter this recipe always built -- sets `_surface_stock`
clusters on each bay of the top, keeping REGISTER_CLEAR round every
``ATT_register`` so a register placed there later has room.

FORM ``bar`` (0.92.0): THE BARTENDER'S SIDE. The walker's second club
photo is a working bar -- "a brass FOOT RAIL on posts along the customer
front; along the top edge a ROW OF BEER TAP handles and two register
terminals on the service side". Those three are PARTS here and not stock,
and the difference is what each one is: stock is what is left out on a top
and is jittered off square by `_surface_stock`'s own rule, while a foot
rail is a continuous straight tube bolted to the front, a tap tower is
plumbed to the bar at a fixed pitch, and a register stands at the station
this recipe has reserved clearance round since 0.84.0. A jittered foot
rail is not a foot rail.

The rail lives INSIDE the slot, under the top's overhang, where a real one
is; the taps and the register stand ON the top and are returned as
``dressing_objects``, so the module's fit bounds stay the counter's (the
same rule that lets a monitor stand on a desk without failing fit_height).
Nothing changes for any other form: ``auto`` and ``straight`` build what
this recipe always built.

FORM ``service`` (1.7.0): THE CONVENIENCE STORE'S COUNTER, planned by
`core.service_counter_forms` from the walker's 1990s photograph of the
store's service island: checkerboard trim bands top and bottom of the
customer face, a tiered candy rack between them inside the top's overhang,
the 1997 register and up to three lottery dispensers at each station, and
the cigarette rack overhead on two chrome posts, packs faced to the
customer under a faintly lit header. The same inside/on-top rule as
``bar``: the trim and the tiers are inside the slot, everything on the top
and above it is dressing. Three parts are PAINTED rather than skinned --
the trim's checker, the candy strips, the rack's display -- each a
`Canvas` raster on a mesh with explicit UVs, the cigarette machine's
idiom, and the rack's header is the one lit surface
(``M_Counter_CigRack_<art>_Face``, so Lux's power cut takes it).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import back_bar_forms as BB
from ..core import cigarette_forms as CF
from ..core import counter_register as CREG
from ..core import register_forms as RF
from ..core import service_counter_forms as SC
from ._bays import bay_max_of, bays

#: kept clear of stock round each register station, metres
REGISTER_CLEAR = 0.22

FORMS = ("straight", "bar")

#: The two keys a register's faces carry (`counter_register.station`): its
#: painted image and its lit one. Neither is a flat material.
_REGISTER_MATS = (CREG.PAINT, CREG.VFD)


def _vfd(prims, plan, collection, streams):
    """Every register window on this counter as ONE object on ONE backlit
    image, ``M_Counter_VFD_<art>_Face`` (Lux's power cut takes it), at the
    `cash_register` species' own screen strength (1.16.0). Each face corner
    is ``(region, u, v)`` into the display image, or ``("bezel",)``."""
    if not prims:
        return [], None
    A = CREG.art(RF.pick_price(plan, streams))
    W, H = A["size"]
    mat = materials.make_backlit_material(
        f"M_Counter_VFD_{A['name']}_Face", materials.image_from_png(A["name"], A["canvas"].png()),
        RF.SCREEN_EMISSION, RF.SCREEN_ALBEDO, smooth=True)
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    for p in prims:
        vs = [bm.verts.new(v) for v in p["verts"]]
        for f, corners in zip(p["faces"], p["uvs"]):
            face = bm.faces.new([vs[i] for i in f])
            for loop, c in zip(face.loops, corners):
                x0, y0, x1, y1 = A["rects"][c[0]]
                if len(c) == 1:
                    loop[uv].uv = ((x0 + x1) / 2.0 / W, 1.0 - (y0 + y1) / 2.0 / H)
                else:
                    loop[uv].uv = ((x0 + (x1 - x0) * c[1]) / W, 1.0 - (y1 - (y1 - y0) * c[2]) / H)
    bm.normal_update()
    geometry.shade_by_angle(bm, 30.0)
    geometry.wear_colors(bm, streams.stream("counter_vfd"), 0.0)
    obj = geometry.bm_to_object(bm, "Counter_RegisterScreen", collection, finish=False)
    obj.data.materials.append(mat)
    return [obj], A


def _register_art(prims, collection, streams):
    """Every painted face of every register on this counter as ONE object on
    ONE painted image, ``M_Counter_Register_<art>_Art`` (1.46.0): the body,
    the deck, the keys, the pole. The image is the same for every counter
    (`counter_register.paint_art`), so a level's registers share one texture."""
    if not prims:
        return []
    A = CREG.paint_art()
    size = A["size"]
    mat = materials.make_painted_material(
        f"M_Counter_Register_{A['name']}_Art",
        materials.image_from_png(A["name"], A["canvas"].png()), 0.45, smooth=True)
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    for p in prims:
        u0, v0, u1, v1 = RF.uv(A["rects"][p["tile"]], size)
        vs = [bm.verts.new(v) for v in p["verts"]]
        for f, corners in zip(p["faces"], p["uvs"]):
            face = bm.faces.new([vs[i] for i in f])
            for loop, c in zip(face.loops, corners):
                loop[uv].uv = (u0 + (u1 - u0) * c[0], v0 + (v1 - v0) * c[1])
    bm.normal_update()
    geometry.shade_by_angle(bm, 30.0)
    geometry.wear_colors(bm, streams.stream("counter_register"), 0.0)
    obj = geometry.bm_to_object(bm, "Counter_RegisterArt", collection, finish=False)
    obj.data.materials.append(mat)
    return [obj]


def _darker(c, f=0.6):
    return [v * f for v in c]


def _kind_material_name(kind):
    """The service form's one material per surface kind (1.8.0). One name
    for the flat path as well as the skinned one, so a build without a skin
    library merges the same way."""
    return f"M_Counter_svc_{kind}"


def _painted_xz(p, mat, collection, streams, v_map=None):
    """A primitive painted with a raster whose UVs come from x and z:
    ``(u, v) = (x * su + ou, v_map(z * sv + ov))`` on every face (the side
    faces of a 6 mm band are slivers and take the same map). ``v_map`` puts a
    band-local v into the painted atlas's rows (1.8.0); without one v is used
    as it is. Built like the cigarette machine's display: no bevel, no wear,
    a white COLOR_0 so the import leaves the paint alone."""
    su, ou, sv, ov = p["uv_xz"]
    v_map = v_map or (lambda v: v)
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new(v) for v in p["verts"]]
    for f in p["faces"]:
        face = bm.faces.new([vs[i] for i in f])
        for loop in face.loops:
            x, _y, z = loop.vert.co
            loop[uv].uv = (x * su + ou, v_map(z * sv + ov))
    bm.normal_update()
    geometry.shade_by_angle(bm, 1.0)
    geometry.wear_colors(bm, streams.stream("service_paint"), 0.0)
    obj = geometry.bm_to_object(bm, p["part"], collection, finish=False)
    obj.data.materials.append(mat)
    return obj


def _art_face(p, art, paint, lit, collection, streams):
    """The rack's art slab: its front two quads mapped onto the raster
    (the header lit, the rows painted), every other face on the dark
    pixels -- `cigarette_machine`'s display, on a counter."""
    size = art["size"]
    art_uv = CF.uv_rect((0, 0, size[0], size[1] - 6), size)
    dark_uv = CF.uv_rect(art["dark"], size)
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new(v) for v in p["verts"]]
    for f, corners, fm in zip(p["faces"], p["uvs"], p["face_mats"]):
        face = bm.faces.new([vs[i] for i in f])
        face.material_index = 1 if fm == "lit" else 0
        for loop, c in zip(face.loops, corners):
            if c[0] == "art":
                loop[uv].uv = (art_uv[0] + (art_uv[2] - art_uv[0]) * c[1],
                               art_uv[1] + (art_uv[3] - art_uv[1]) * c[2])
            else:
                loop[uv].uv = ((dark_uv[0] + dark_uv[2]) / 2.0, (dark_uv[1] + dark_uv[3]) / 2.0)
    bm.normal_update()
    geometry.shade_by_angle(bm, 1.0)
    geometry.wear_colors(bm, streams.stream("service_paint"), 0.0)
    obj = geometry.bm_to_object(bm, p["part"], collection, finish=False)
    obj.data.materials.append(paint)
    obj.data.materials.append(lit)
    return obj


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    overhang = bool(plan["params"].get("overhang", 1))
    shelf = bool(plan["params"].get("shelf", 1))
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.4, rng=rng, wear=wear))

    base_h = 0.07
    top_t = 0.045
    lip = 0.02          # the top's overhang past the body, each end
    body_d = d * (0.85 if overhang else 1.0)
    body_y = (d - body_d) / 2 if overhang else 0.0   # body pushed to staff side
    # EXACT FIT (roadmap 44): a counter built into a Deli Counter slot must
    # be the slot's width overall -- the first hinted `counter_island` came
    # out 2.040 m against a 2.000 m slot and failed `fit_width`, because
    # the top was `w + 0.04` for a free-standing prop. Keep the lip; take it
    # out of the body instead, so the top IS the width.
    exact = bool(plan.get("fit_exact"))
    top_w = w if exact else w + 2 * lip
    body_w = w - 2 * lip if exact else w

    # recessed kick base
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, body_y, base_h / 2),
                     (body_w * 0.96, body_d * 0.92, base_h))
    part(bm, "Counter_Base")

    # body
    body_h = h - base_h - top_t
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, body_y, base_h + body_h / 2),
                     (body_w, body_d, body_h))
    part(bm, "Counter_Body")

    # countertop, proud on every side, overhanging the customer face
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, h - top_t / 2),
                     (top_w, d, top_t))
    part(bm, "Counter_Top")

    # BAYS (roadmap 44): a counter run is one continuous body and top -- a
    # 10 m bar is a 10 m bar -- so the bays only decide where the staff-side
    # shelves and the register attachment points stand: one per bay of at
    # most `bay_max` (genome params), so an 8 m teller counter has two
    # stations, not one register at 1.2 m from the end.
    runs = bays(w, bay_max_of(plan))
    attachments = {}
    for bi, (bx, bw) in enumerate(runs):
        tag = "" if len(runs) == 1 else f"_B{bi + 1}"
        if shelf:
            bm = geometry.new_bm()
            geometry.add_box(bm, (bx, body_y + body_d * 0.3, base_h + body_h * 0.5),
                             (bw * 0.9 - (2 * lip if exact else 0.0), body_d * 0.35, 0.03))
            part(bm, f"Counter_Shelf{tag}")
        attachments[f"ATT_register{tag}"] = (bx + bw * 0.15, 0.0, h)
    attachments["ATT_counter_front"] = (0.0, -d / 2, h)

    cboxes.append(((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h)))

    top = materials.make_material(
        f"M_Counter_top_{plan['material']}", _darker(plan["color"], 0.85),
        plan["material"])
    body = materials.make_material(
        f"M_Counter_{plan['material']}", plan["color"], plan["material"])
    frame = materials.make_material(
        f"M_Counter_base_{plan['material']}", _darker(plan["color"]),
        plan["material"])
    for o in objs:
        if "Top" in o.name:
            materials.assign([o], top)
        elif "Base" in o.name:
            materials.assign([o], frame)
        else:
            materials.assign([o], body)

    regions = []
    for bx, bw in runs:
        x0 = max(bx - bw / 2, -top_w / 2)
        x1 = min(bx + bw / 2, top_w / 2)
        keep = tuple((ax, ay, REGISTER_CLEAR)
                     for name, (ax, ay, _z) in attachments.items()
                     if name.startswith("ATT_register") and x0 <= ax <= x1)
        regions.append((x0, x1, -d / 2, d / 2, h, None, 0.6, keep))
    stock = prim_mesh.build_stock(plan, streams, collection, regions,
                                  _darker(plan["color"], 0.85))

    # --- FORM `bar`: the foot rail, the taps and the register -------------
    form = (plan["params"].get("form") or "auto")
    form = "straight" if form in ("auto", "", None) else str(form)
    fit_objs, top_objs = [], []
    if form == "bar":
        inside, on_top = BB.counter_fitout(w, d, h, attachments, top_w)
        mats = {
            "brass": ("M_Counter_brass", [0.58, 0.44, 0.16], "metal_bare"),
            "steel": ("M_Counter_steel", [0.60, 0.61, 0.63], "metal_bare"),
            "tap_handle": ("M_Counter_taphandle", [0.06, 0.07, 0.08], "plastic"),
        }
        fit_objs = prim_mesh.build(inside, collection, plan,
                                   streams.stream("bar_fitout"), mats, texel=1.0)
        top_objs = prim_mesh.build([p for p in on_top if p["mat"] not in _REGISTER_MATS],
                                   collection, plan, streams.stream("bar_fitout"), mats, texel=1.0)
        top_objs += _register_art([p for p in on_top if p["mat"] == CREG.PAINT], collection, streams)
        top_objs += _vfd([p for p in on_top if p["mat"] == CREG.VFD], plan, collection, streams)[0]
        print(f"[counter] form=bar rail_posts={sum(1 for p in inside) - 1} "
              f"taps={sum(1 for p in on_top if p['part'] == 'Counter_TapTower') // 2} "
              f"registers={sum(1 for p in on_top if p['part'] == 'Counter_RegisterKeys')}")
    elif form == "service":
        key, variant = SC.resolve(plan)
        inside, on_top, facts = SC.fitout(w, d, h, attachments, top_w, body_y - body_d / 2,
                                          base_h, top_t, key, variant)
        # ONE MATERIAL PER KIND (1.8.0). Each `mat` key builds with its kind's
        # one material, and its colour goes into the part's `Wear` so
        # `merge.pack_by_material` packs every part of a kind into one mesh.
        # Built key by key so every object's key is known when it is tinted.
        rng = streams.stream("service_fitout")
        fit_objs, top_objs = [], []
        for dest, pool in ((fit_objs, [p for p in inside if "paint" not in p]),
                           (top_objs, [p for p in on_top if "uvs" not in p])):
            for mk in sorted({p["mat"] for p in pool}):
                kind, factor = SC.vertex_tint(mk)
                built = prim_mesh.build([p for p in pool if p["mat"] == mk], collection, plan, rng,
                                        {mk: (_kind_material_name(kind), list(SC.KIND_BASE[kind]), kind)},
                                        texel=1.0)
                for o in built:
                    geometry.tint_wear(o, factor)
                dest.extend(built)
        # ONE PAINTED ATLAS for the trim and the three candy tiers (1.8.0;
        # 1.7.0 painted four images into four materials). REPEAT along the
        # counter, each part's v mapped into its own band.
        A = SC.paint_atlas(facts["tiers"], key, variant)
        paint_mat = materials.make_painted_material(
            f"M_Counter_Paint_{A['name']}",
            materials.image_from_png(A["name"], A["canvas"].png()), 0.4, tile=True)
        for p in (q for q in inside if "paint" in q):
            band = A["bands"]["checker" if p["paint"] == "checker" else p["paint"]]
            fit_objs.append(_painted_xz(p, paint_mat, collection, streams,
                                        v_map=lambda v, b=band: SC.atlas_v(b, A["size"], v)))
        rack = facts["rack"]
        if rack is not None:
            R = SC.rack_art(facts, key, variant)
            image = materials.image_from_png(R["name"], R["canvas"].png())
            lit = materials.make_backlit_material(f"M_Counter_CigRack_{R['name']}_Face", image,
                                                  CF.HEADER_EMISSION, CF.HEADER_ALBEDO, smooth=True)
            paint = materials.make_painted_material(f"M_Counter_CigRack_{R['name']}_Display",
                                                    image, CF.DISPLAY_ROUGHNESS, smooth=True)
            # the rack's art, not a register's face: all three carry ``uvs``
            art_p = next(q for q in on_top if "uvs" in q and q["mat"] not in _REGISTER_MATS)
            top_objs.append(_art_face(art_p, R, paint, lit, collection, streams))
        top_objs += _register_art([p for p in on_top if p["mat"] == CREG.PAINT], collection, streams)
        top_objs += _vfd([p for p in on_top if p["mat"] == CREG.VFD], plan, collection, streams)[0]
        # WHITE LAMINATE, whatever the slot said. The reference's counter is
        # white laminate under checkerboard trim, and the form is the look;
        # a Deli Counter prop arrives as `wood` by default and would build a
        # brown counter with a checker band on it. The body, top, kick and
        # the staff shelves share the candy tiers' laminate material and
        # differ by a `Wear` factor (`SC.BODY_TINT`).
        lam = materials.make_material(_kind_material_name("laminate"),
                                      list(SC.KIND_BASE["laminate"]), "laminate")
        for o in objs:
            part = next((k for k in SC.BODY_TINT if k in o.name), "Body")
            materials.assign([o], lam)
            geometry.tint_wear(o, SC.BODY_TINT[part])
        print(f"[counter] form=service registers={len(facts['registers'])} "
              f"lottery={len(facts['lottery'])} tiers={len(facts['tiers'])} "
              f"rack={'none' if rack is None else '%.2fm/%d packs' % (rack['w'], rack['n_packs'])} "
              f"candy={[A['candy'][k][0] for k in sorted(A['candy'])]} "
              f"header={'-' if rack is None else R['header']} atlas={A['size'][0]}x{A['size'][1]}")

    dressing = stock + top_objs
    return {"objects": objs + fit_objs + stock + top_objs,
            "dressing_objects": dressing,
            "collision_boxes": cboxes, "attachments": attachments}
