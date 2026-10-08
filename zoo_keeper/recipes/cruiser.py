"""cruiser recipe: the responders' 1990s Crown Victoria police sedan (Zoo 1.86.0, roadmap 212).

The walker, 2026-10-08: "I would think a classic 1990s Crown Victoria", and
for the department "Delco County Police Dept. as a start?". The comps, read
for format only, are docs/reference/CRUISER_COMPS.md at the factory root;
every number below is `core.cruiser_forms`, which is pure and tested.

Length runs along Y, the nose at -Y, the driver's side at +X; built base-up
(z 0 .. H) and re-centred by `build.build_module`, like `simple_car`.

WHAT A CRUISER IS HERE, in the order it is built:

  * THE CAR: `simple_car`'s, as the `cruiser` row of `car_forms.FORMS` (a
    Crown Victoria's proportions), to the slot less the push bar's reach and
    the light bar's height (`cruiser_forms.body_dims`), with its form pinned
    (`cruiser_forms.pin_form`): four doors and a quarter glass, black steel
    wheels, body bumpers, the side moulding, a blue-grey cloth interior, and
    no jitter -- the same car in every level.
  * THE LIVERY: the body goes onto one material carrying one image
    (`cruiser_forms.livery_art`) under its `Wear` colour -- the getaway van's
    ghost technique (`materials.make_wear_textured_material`). Its sides map
    into the image by their (y, z) (`livery_uv`), so the doors' two-tone and
    the department's lettering are as sharp as a texel; every other face
    samples the image's white patch and wears its colour per corner
    (`finish_rgb`). The slot's `form` picks the livery: `black_white`,
    black with white doors and roof, or `white_blue`, white with a blue
    stripe -- the two the comps hold.
  * THE KIT (`cruiser_forms.kit`): a light bar across the roof, red on the
    driver's side and blue on the other; a push bar on the nose; a spotlight
    on the driver's A-pillar; a whip on the trunk; a partition behind the
    front seats and a radio console between them, both stood against the
    cabin `simple_car` returns. Boxes on the car's one painted material, each
    part's colour in `Wear`, named in the car's part family so the export
    packs them into its painted mesh: no draw call of their own. A cruiser
    exports five meshes, one a material -- the livery's body, the painted
    parts with the kit, the rubber trim, the cabin and the glass.

THE LIGHTS ARE PARTS, NOT LIGHTS. The bar's lenses are unlit, as
`simple_car`'s lamps are; `ATT_lightbar` marks the bar's centre for a game
layer that wants to light it -- responders are its to spawn.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials
from ..core import car_forms, cruiser_forms
from . import simple_car

#: The liveries, by the slot's `form` (the genome lists them; `auto` is
#: `cruiser_forms.DEFAULT_LIVERY`).
LIVERIES = tuple(cruiser_forms.LIVERIES)


def build(plan, streams, collection):
    W = plan["dimensions"]["width"]
    L = plan["dimensions"]["depth"]
    H = plan["dimensions"]["height"]
    params = plan.get("params") or {}
    asked = params.get("form") or "auto"
    livery = cruiser_forms.DEFAULT_LIVERY if asked == "auto" else asked
    if livery not in LIVERIES:
        raise ValueError(f"cruiser: no livery {asked!r}; the liveries are {', '.join(LIVERIES)}")

    # --- the car: simple_car's, to the body's own dims, its form pinned ----------
    Wb, Lb, Hb = cruiser_forms.body_dims(W, L, H)
    body_plan = dict(plan)
    body_plan["dimensions"] = {"width": Wb, "depth": Lb, "height": Hb}
    body_plan["params"] = dict(params, body_style="cruiser", doors=4)
    form = cruiser_forms.pin_form(car_forms.resolve(body_plan, streams))
    car = simple_car.build(body_plan, streams, collection, form=form)
    lay = car_forms.layout(form, Wb, Lb, Hb)

    # --- the livery on the body -----------------------------------------------------
    body = next((o for o in car["objects"] if o.name.startswith("Car_Body")), None)
    if body is None:
        raise RuntimeError("cruiser: simple_car built no Car_Body to paint")
    print("[cruiser] door seams at y %s, the door skin z %.3f .. %.3f"
          % (", ".join("%.3f" % e for e in car["door_edges"]), *car["door_skin_z"]))
    art = cruiser_forms.livery_art(lay, car["door_edges"], car["door_skin_z"], livery,
                                   moulding_z=car.get("moulding_z"))
    paint = materials.make_wear_textured_material(
        "M_Cruiser_" + livery, materials.image_from_png(art["name"], art["png"]), plan["material"])
    materials.assign([body], paint)
    if not geometry.tint_wear_by(body, lambda co, n: cruiser_forms.finish_rgb(co, n, lay, livery)):
        raise RuntimeError("cruiser: Car_Body has no Wear layer, so its livery would not land")
    if not geometry.set_uv_by(body, lambda co, n: cruiser_forms.livery_uv(co, n, art["frame"])):
        raise RuntimeError("cruiser: Car_Body has no UV layer, so its livery would not land")

    # --- black steel wheels -----------------------------------------------------------
    # simple_car paints a steel wheel grey (`car_forms.CLADDING["grey"]`, its
    # bumper grey) because black on the tyre's black read as one disc. The
    # comps' wheels are black steel; charcoal keeps them apart from the tyre.
    # The cruiser's bumpers are the body's, so the grey group holds only the
    # wheel discs; `tint_wear` multiplies, hence the ratio.
    grey = next((o for o in car["objects"] if o.name.startswith("Car_Grey_Paint")), None)
    if grey is not None:
        ratio = tuple(c / g for c, g in zip(cruiser_forms.WHEEL_RGB, car_forms.CLADDING["grey"]))
        if not geometry.tint_wear(grey, ratio):
            raise RuntimeError("cruiser: Car_Grey_Paint has no Wear layer, so its wheels would not darken")

    # --- the kit --------------------------------------------------------------------
    seat = car["attachments"]["ATT_driver_seat"]
    boxes = cruiser_forms.kit(lay, seat, car["interior"])
    painted = materials.make_material("M_Car_painted", list(car_forms.PAINTED), "metal_painted")
    rng = streams.stream("cruiser_kit")
    # in the car's own part family (`partnames.family`: "Car"), so the export
    # merges the kit into the car's painted mesh -- one draw, the same
    # material. Named `Cruiser_*` at first, they were a family of their own
    # and a sixth mesh on that one material.
    names = {"kit_black": "Car_Kit", "lens_red": "Car_Lens_Red",
             "lens_blue": "Car_Lens_Blue", "lens_clear": "Car_Lens_Clear"}
    kit_objs = []
    for key, rows in boxes.items():
        if not rows:
            continue
        bm = geometry.new_bm()
        for lo, hi in rows:
            simple_car._box(bm, lo, hi)
        obj = geometry.bm_to_object(bm, names[key], collection, bevel=0.0, texel=1.0,
                                    rng=rng, wear=0.0)
        materials.assign([obj], painted)
        if not geometry.tint_wear(obj, cruiser_forms.KIT_RGB[key]):
            raise RuntimeError(f"cruiser: {obj.name} has no Wear layer, so its colour would not land")
        kit_objs.append(obj)

    # --- what a consumer reads ------------------------------------------------------
    bar_y = lay["y_rf"] + cruiser_forms.BAR_ALONG * (lay["y_rr"] - lay["y_rf"])
    push_face = lay["yF0"] - cruiser_forms.PUSH_PROUD
    attachments = dict(car["attachments"])
    attachments["ATT_lightbar"] = (0.0, bar_y, lay["zr"] + cruiser_forms.BAR_TOP)
    collision = list(car["collision_boxes"])
    collision.append(((-cruiser_forms.PUSH_X - cruiser_forms.PUSH_TUBE / 2.0, push_face, lay["clear"] + 0.05),
                      (cruiser_forms.PUSH_X + cruiser_forms.PUSH_TUBE / 2.0, lay["yF0"],
                       lay["fascia"] + cruiser_forms.PUSH_TOP_OVER_FASCIA)))
    print(f"[cruiser] livery={livery} art={art['name']} {art['size'][0]}x{art['size'][1]} marks x{art['scale']:.2f} "
          f"kit={sum(len(r) for r in boxes.values())} box(es) body={Wb:.3f}x{Lb:.3f}x{Hb:.3f}")
    return {"objects": car["objects"] + kit_objs, "collision_boxes": collision,
            "form": car["form"], "attachments": attachments}
