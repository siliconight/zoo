"""pew recipe: a church pew -- two solid ends, a seat, a high back and a book rack.

The factory's roadmap 308: a chapel, a funeral home's viewing room, a
courtroom's public benches and an assembly room were furnished as a
cafeteria, because Deli Counter had no seat for a row that faces one front
and Zoo's `bench` is a street bench with no back. REFERENCE: an American
oak pew, the common pattern of church-furniture catalogues -- two end
panels the pew's full height and depth, a seat 0.45 m up and about 0.46 m
deep meeting a back behind it, a rack on the back's rear for the hymnals of
the row behind and, where the slot is deep enough, a kneeler for that row at
the floor. Every part is the same stained wood, one material, so a room of
pews is one mesh a row to the merge.

THE SEAT IS A PEW'S DEPTH WHATEVER THE SLOT'S. A slot deeper than a seat,
back and rack -- the 0.9 m `pew_row` boxes Deli Counter's funeral home
authored -- keeps the seat at `SEAT_D` and puts the rest behind the rack as
the kneeler, rather than stretching the seat until nobody's knees reach its
edge; a first draft ran the seat to a back pushed against the slot's rear.

Recipe frame: centre pivot, the FRONT (where a person sits facing) at -y,
the back at +y, as `chair.py`'s. The two ends are the pew's whole extent
in every axis, so the module is exactly (w, d, h) whatever the parts
inside them do. Collision is the pew as one block: a body walks the aisle,
never through a row.

NO TWO FACES SHARE A PLANE (`tests/test_coincident_faces.py`): every part
runs `BURY` into whatever it meets -- the seat, back, rail and rack into
both ends, the back into the seat and the rail, the shelf into the back and
the lip -- and stops `FACE_GAP` short of the ends' outer faces, so a face
that meets another is inside it rather than on it. Parts that pass into one
another also end at different depths in the ends -- the back and the rack's
lip half as deep as the seat, rail and shelf -- or their end faces would
share a plane inside the end panel (the census's first reading: four pairs a
corner, Pew_Back with Pew_Seat and with Pew_Rack, all at x = +-span / 2).
"""
from __future__ import annotations

from ..bpylayer import geometry, materials

END_T = 0.05          # an end panel's thickness along the pew
SEAT_Z = 0.45         # the seat's top above the floor
SEAT_T = 0.04
BACK_T = 0.03
TOP_RAIL = (0.05, 0.05)   # the back's cap, deep x tall
RACK_D = 0.09         # the book rack, out from the back's rear face
RACK_Z = 0.62         # the rack shelf's top above the floor
RACK_T = 0.02
RACK_LIP = 0.07       # the rack's lip, tall
SEAT_D = 0.46         # front edge to the back's front face
KNEEL = (0.18, 0.10, 0.10)   # the kneeler: deep, thick, its top's height above its underside's
KNEEL_MIN = 0.25     # the depth left behind the rack that takes one
BURY = 0.01
FACE_GAP = 0.005


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []
    z0, y0, y1 = -h / 2.0, -d / 2.0, d / 2.0

    def part(name, boxes):
        bm = geometry.new_bm()
        for centre, size in boxes:
            geometry.add_box(bm, centre, size)
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.2, rng=rng, wear=wear))

    # the two ends: the whole height and depth
    for tag, sx in (("L", -1), ("R", 1)):
        part(f"Pew_End_{tag}", [((sx * (w / 2.0 - END_T / 2.0), 0.0, 0.0), (END_T, d, h))])
    span = w - 2.0 * END_T + 2.0 * BURY          # between the ends, into both
    half = span - BURY                            # the back's and the lip's
    # the back stands a seat's depth behind the front, or as far back as
    # leaves the rack room; the rack hangs on the back
    back_y = min(y1 - FACE_GAP - RACK_D - BACK_T / 2.0, y0 + FACE_GAP + SEAT_D + BACK_T / 2.0)
    seat_z = z0 + min(SEAT_Z, h * 0.6)
    seat_front = y0 + FACE_GAP
    seat_back = back_y          # the seat runs into the back: no gap a hand falls through
    part("Pew_Seat", [((0.0, (seat_front + seat_back) / 2.0, seat_z - SEAT_T / 2.0),
                       (span, seat_back - seat_front, SEAT_T))])
    rail_top = h / 2.0 - FACE_GAP
    rail_lo = rail_top - TOP_RAIL[1]
    back_lo = seat_z - SEAT_T / 2.0                      # into the seat
    back_hi = rail_lo + BURY                              # into the rail
    part("Pew_Back", [((0.0, back_y, (back_lo + back_hi) / 2.0), (half, BACK_T, back_hi - back_lo))])
    part("Pew_TopRail", [((0.0, back_y, (rail_lo + rail_top) / 2.0), (span, TOP_RAIL[0], TOP_RAIL[1]))])
    # the book rack for the row behind: a shelf from inside the back to inside
    # the lip, and the lip hanging below the shelf
    rack_top = min(z0 + RACK_Z, rail_lo - RACK_LIP)
    lip_y = back_y + BACK_T / 2.0 + RACK_D - RACK_T / 2.0
    shelf_y0, shelf_y1 = back_y, lip_y
    part("Pew_Rack", [
        ((0.0, (shelf_y0 + shelf_y1) / 2.0, rack_top - RACK_T / 2.0), (span, shelf_y1 - shelf_y0, RACK_T)),
        ((0.0, lip_y, rack_top - 2.0 * RACK_T + RACK_LIP / 2.0), (half, RACK_T, RACK_LIP)),
    ])
    # the kneeler for the row behind, at the slot's rear, raised off the floor
    if y1 - FACE_GAP - (lip_y + RACK_T / 2.0) >= KNEEL_MIN:
        kd, kt, kz = KNEEL
        part("Pew_Kneeler", [((0.0, y1 - FACE_GAP - kd / 2.0, z0 + kz + kt / 2.0), (span, kd, kt))])

    cboxes.append(((-w / 2.0, -d / 2.0, -h / 2.0), (w / 2.0, d / 2.0, h / 2.0)))
    wood = materials.make_material(
        f"M_Pew_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, wood)
    return {"objects": objs, "collision_boxes": cboxes,
            "attachments": {"ATT_seat_center": (0.0, (seat_front + seat_back) / 2.0, seat_z)}}
