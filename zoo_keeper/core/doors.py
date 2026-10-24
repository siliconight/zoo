"""An Empty's front-door finishes (1.72.0). Pure: no Blender.

The walker's photographs (the factory root's `docs/reference/EMPTIES_COMPS.md`,
"Window comps"): the South Philly row's doors are painted house by house.
Every Empty door rendered the same brown wood: 1.61.0 built its leaf in
`wood_panel` with a navy that was only ever the flat colour, which a skinned
wood panel does not take.

A finish is a skin KIND and the colour it is tinted. The painted ones are
`metal_painted` -- Pixelcoat's `metal_painted_neutral` is achromatic and
tintable, so the tint is the paint (`materials.make_material` names the
material for it) -- and `stained` is the wood the leaf always wore.

ORDER IS THE CONTRACT. Deli Counter's `empty_panes.DOOR_FINISHES` lists the
same names in this order and its `test_front_doors.py` pins the two; the
finish rides in the module's name as `_e<finish>` (`kit.module_stem`).
"""
from __future__ import annotations

#: finish -> (skin kind, tint or None). Insertion order is the contract.
FINISHES = {
    "navy": ("metal_painted", (0.13, 0.17, 0.27)),
    "oxblood": ("metal_painted", (0.33, 0.08, 0.08)),
    "green": ("metal_painted", (0.10, 0.24, 0.15)),
    "black": ("metal_painted", (0.05, 0.05, 0.05)),
    "white": ("metal_painted", (0.86, 0.86, 0.83)),
    "stained": ("wood_panel", None),
}


def leaf_material(finish, default_color):
    """``(material name, colour, kind)`` for a facade leaf in ``finish``.

    No finish is the leaf every Empty door had: `wood_panel`, named as it was.
    A finish names its flat material for itself, not its kind -- two painted
    doors built in one process must not share the first one's colour through
    the material cache."""
    if finish not in FINISHES:
        return "M_Door_wood_panel", default_color, "wood_panel"
    kind, tint = FINISHES[finish]
    return "M_Door_%s" % finish, (tint if tint is not None else default_color), kind


#: A DOOR HAS HARDWARE (1.124.0). The walker, walking cold run 9386, at a
#: rowhome's stoop: "many of the rowhome doors dont have doorknobs?" -- the
#: leaf was one flat box in its paint. A painted panel door: two raised panels
#: on its street face, in the leaf's own material (they merge with it, no draw),
#: and a knob on an escutcheon plate at the latch edge at handle height, in one
#: shared brass (`HARDWARE`: one material for every door in a build, so the
#: Empties' per-side merge carries it as one more mesh a front at most). Each
#: piece sinks `SINK` into the leaf, so no face of it lies on the leaf's face
#: (`tests/test_coincident_faces.py`'s rule). Sizes: a residential knob about
#: 2 1/4 in across on its rose, 2 3/8 in back from the latch edge, about 38 in
#: to its centre; the plate rounded to what reads at play distance. Built by
#: `recipes/_arch.py`.
KNOB_D = 0.06
KNOB_PROUD = 0.06
KNOB_Z = 0.95
KNOB_FROM_EDGE = 0.07
PLATE = (0.065, 0.012, 0.20)
PANEL_INSET = 0.11
PANEL_PROUD = 0.012
PANEL_GAP = 0.12
SINK = 0.001
HARDWARE = ("M_Door_hardware_brass", (0.71, 0.55, 0.24), "metal_painted")
