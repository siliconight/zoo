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
