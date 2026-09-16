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
"""
from __future__ import annotations

from ..bpylayer import geometry, materials, prim_mesh
from ..core import back_bar_forms as BB
from ._bays import bay_max_of, bays

#: kept clear of stock round each register station, metres
REGISTER_CLEAR = 0.22

FORMS = ("straight", "bar")


def _darker(c, f=0.6):
    return [v * f for v in c]


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
            "beige": ("M_Counter_register", [0.60, 0.57, 0.48], "plastic"),
            "key_dark": ("M_Counter_registerkeys", [0.16, 0.16, 0.17], "plastic"),
        }
        fit_objs = prim_mesh.build(inside, collection, plan,
                                   streams.stream("bar_fitout"), mats, texel=1.0)
        top_objs = prim_mesh.build(on_top, collection, plan,
                                   streams.stream("bar_fitout"), mats, texel=1.0)
        print(f"[counter] form=bar rail_posts={sum(1 for p in inside) - 1} "
              f"taps={sum(1 for p in on_top if p['part'] == 'Counter_TapTower') // 2} "
              f"registers={sum(1 for p in on_top if p['part'] == 'Counter_Register') // 2}")

    dressing = stock + top_objs
    return {"objects": objs + fit_objs + stock + top_objs,
            "dressing_objects": dressing,
            "collision_boxes": cboxes, "attachments": attachments}
