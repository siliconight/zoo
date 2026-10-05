"""A gutter that reads as a gutter, a downspout, painted metal (1.67.0).

The walker, 2026-10-04: "also we need rain gutters". Patina has ordered a
`gutter_run` under every roofline since its 0.18; Zoo built each as a solid
box 10 cm proud by 14 cm tall, centred ON the wall face -- half of it inside
the wall -- in the concrete every other cover wears. From the street that is a
bar, not a gutter. Patina 0.25.0 also orders the pipe that carries the water
down (`downspout`), which nothing built.

The part lists are pure, as `frame_strips` is, so the shapes are tested here
without Blender.
"""
from zoo_keeper.core import dressing as D

SPAN, PROUD, CROSS = 2.0, D._COVER["gutter_run"]["proud"], D._COVER["gutter_run"]["cross"]


def _y_range(parts):
    return (min(c[1] - s[1] / 2 for c, s in parts), max(c[1] + s[1] / 2 for c, s in parts))


def _z_range(parts):
    return (min(c[2] - s[2] / 2 for c, s in parts), max(c[2] + s[2] / 2 for c, s in parts))


def test_a_gutter_is_an_open_trough_standing_off_the_wall():
    """FAILS ON 1.66.0: no `gutter_parts`; the gutter was one solid box
    centred on the wall face."""
    parts = D.gutter_parts(SPAN, PROUD, CROSS)
    y0, y1 = _y_range(parts)
    assert abs(y0) < 1e-9 and abs(y1 - PROUD) < 1e-9          # wall face out to its lip
    z0, z1 = _z_range(parts)
    assert abs((z1 - z0) - CROSS) < 1e-9
    # open: nothing spans the trough's mouth between the back and the lip
    mouth_y = PROUD / 2.0
    top = z1 - 0.01
    assert not [p for p in parts if abs(p[0][1] - mouth_y) < PROUD / 2 - 0.02
                and p[0][2] + p[1][2] / 2 >= top and p[1][1] > PROUD / 2]
    # every part runs the full span, so sections butt at module seams
    assert all(abs(s[0] - SPAN) < 1e-9 for _c, s in parts)


def test_a_downspout_stands_off_the_wall_into_a_boot_at_the_ground():
    L = 9.075
    parts = D.downspout_parts(L, D._COVER["downspout"]["cross"])
    z0, z1 = _z_range(parts)
    assert abs(z0 + L / 2) < 1e-9 and abs(z1 - L / 2) < 1e-9   # gutter underside to ground
    y0, _y1 = _y_range(parts)
    assert y0 >= -1e-9                                          # nothing inside the wall
    boot = min(parts, key=lambda p: p[0][2])
    assert boot[1][0] > D._COVER["downspout"]["cross"]         # the boot is wider than the pipe
    assert abs((boot[0][2] - boot[1][2] / 2) + L / 2) < 1e-9   # and stands on the ground


def test_strip_size_runs_a_downspout_up_the_wall():
    w, d, h = D.strip_size("downspout", 9.075)
    assert h == 9.075 and w == D._COVER["downspout"]["cross"]


def test_gutters_and_downspouts_are_painted_metal_and_the_rest_are_not():
    genome = {"materials": {"default": "concrete", "options": ["concrete", "metal_painted"]},
              "styles": {"default": {"material": "concrete", "color": [0.5, 0.5, 0.5]}}}
    for cover in ("gutter_run", "downspout"):
        p = D.dress_plan({"cover": cover, "pos": [0, 0, 0], "normal": [0, 1, 0]},
                         genome, "default", "spec/Blender Z-up raw coords", "t")
        assert p["material"] == "metal_painted", cover
    p = D.dress_plan({"cover": "base_course", "pos": [0, 0, 0], "normal": [0, 1, 0]},
                     genome, "default", "spec/Blender Z-up raw coords", "t")
    assert p["material"] == "concrete"


def test_a_genome_without_the_metal_keeps_its_default():
    """The control: the switch asks the genome, and a genome that does not
    offer painted metal is not handed a kind it cannot build."""
    genome = {"materials": {"default": "concrete", "options": ["concrete"]},
              "styles": {"default": {"material": "concrete", "color": [0.5, 0.5, 0.5]}}}
    p = D.dress_plan({"cover": "gutter_run", "pos": [0, 0, 0], "normal": [0, 1, 0]},
                     genome, "default", "spec/Blender Z-up raw coords", "t")
    assert p["material"] == "concrete"
