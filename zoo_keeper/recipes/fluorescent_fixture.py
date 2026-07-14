"""fluorescent_fixture recipe: a ceiling troffer — sheet-metal housing over an
emissive prismatic diffuser. Built centered; the light-anchor pipeline lifts
it so the diffuser face (bottom, at -h/2) sits exactly at the DC anchor point
and the body fills the gap up to the ceiling. The diffuser is a self-lit
glTF-emissive face (no wear paint — a lit lens doesn't grime), so it glows
under any Lux preset and feeds LightmapGI on the pc2000 path."""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]      # length along the lamp row
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    style = plan.get("style_block", {})
    rng = streams.stream("wear")
    z0 = -h / 2.0
    objs = []

    # Diffuser: the lit face, slightly inset, occupying the bottom third.
    td = h * 0.35
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + td / 2.0), (w * 0.94, d * 0.8, td))
    diffuser = geometry.bm_to_object(
        bm, "FluorescentFixture_Diffuser", collection,
        bevel=0.0, texel=1.0, rng=rng, wear=0.0)
    objs.append(diffuser)

    # Housing: the metal body above it, flush to the ceiling once mounted.
    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, z0 + td + (h - td) / 2.0), (w, d, h - td))
    housing = geometry.bm_to_object(
        bm, "FluorescentFixture_Housing", collection,
        bevel=bevel, texel=1.5, rng=rng, wear=wear)
    objs.append(housing)

    mat = materials.make_material(
        f"M_FluorescentFixture_{plan['material']}", plan["color"],
        plan["material"])
    materials.assign([housing], mat)
    lens = materials.make_emissive_material(
        "M_FluorescentFixture_Lens",
        style.get("emissive_color", [0.82, 0.93, 0.87]),
        style.get("emissive_strength", 2.0))
    materials.assign([diffuser], lens)

    # No collision: ceiling hardware, nothing traverses it.
    return {"objects": objs, "collision_boxes": [], "attachments": {}}
