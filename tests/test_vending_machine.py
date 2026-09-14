"""vending_machine, rebuilt in 0.87.0: a 1990s soda machine that glows.

The decisions are pure (`core/vending_forms.py`, `core/brands.py`,
`core/pixel_type.py`) and tested here without Blender. The built module --
exact fit at the genome's corners and Deli Counter's two sizes, every part,
the same GLB every build, the glow on the panel, buttons and display and in
the exported file, a brand from the table, zero coincident faces -- is the
bpy half at the bottom, skipped without Blender.

0.86.0 built 0.795 m deep for a 0.75 m slot (its coin slot stood 45 mm proud)
and failed its own `fit_depth`; `test_bpy_fits_its_slot_with_every_part`
reads that failure on 0.86.0's code.
"""
import json
import os
import random
import re
import struct
import sys
import zlib

import pytest

from zoo_keeper import SEED_EPOCH
from zoo_keeper.core import dna, genome, kit, seeding

_ZOO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RECIPE = os.path.join(_ZOO, "zoo_keeper", "recipes", "vending_machine.py")
_GENOME = os.path.join(_ZOO, "zoo_keeper", "genome", "species", "vending_machine.json")

#: Deli Counter's `vending` piece sizes (level_design._PIECES), then the
#: genome's corners.
DC_SIZES = ((0.85, 0.75, 1.83), (1.0, 0.8, 1.9))
CORNERS = DC_SIZES + ((0.7, 0.6, 1.6), (1.05, 0.9, 2.0), (0.7, 0.9, 2.0),
                      (1.05, 0.6, 1.6), (0.7, 0.75, 2.0), (1.05, 0.9, 1.6))
PROBE_TOL = 0.002
TRI_BUDGET = 600
TRIS = 464


def _vf():
    from zoo_keeper.core import vending_forms
    return vending_forms


def _brands():
    from zoo_keeper.core import brands
    return brands


def _random_dims(n, seed=87):
    rng = random.Random(seed)
    return [(round(rng.uniform(0.7, 1.05), 3), round(rng.uniform(0.6, 0.9), 3),
             round(rng.uniform(1.6, 2.0), 3)) for _ in range(n)]


def _slot(w, d, h, style=4, variant=0):
    s = {"slot_id": "vend_0", "role": "prop", "size_mod": "full", "style": style,
         "species": "vending_machine", "material": "metal_painted",
         "fit": {"dims": [w, d, h], "pivot": "center", "collision": "convex"}}
    if variant:
        s["variant"] = variant
    return s


def _kit(w, d, h, style=4, variant=0):
    return kit.plan_kit({"building_id": "t", "slots": [_slot(w, d, h, style, variant)]},
                        theme="delco_1997", style=style)


def _module_plan(dims=DC_SIZES[0], style=4, variant=0):
    mod = _kit(*dims, style=style, variant=variant)["modules"][0]
    return mod, dna.resolve_module_plan(mod, genome.load_species("vending_machine"),
                                        "delco_1997", style, "0.87.0")


def _streams(stem):
    return seeding.RNGStreams(seeding.root_key(stem, "vending_machine", 0, SEED_EPOCH))


# --- genome ---------------------------------------------------------------------------

def test_the_genome_validates_and_names_the_parts_the_recipe_builds():
    g = json.load(open(_GENOME, encoding="utf-8"))
    assert genome.validate_genome(genome.load_species("vending_machine")) == []
    assert g["version"] == 2
    src = open(_RECIPE, encoding="utf-8").read()
    assert len(g["parts"]) == 14
    for part in g["parts"]:
        assert f'"{part}"' in src, part
    assert g["budgets"]["tris_lod0"] == TRI_BUDGET
    assert g["module_variants"] == 4
    assert g["params"]["brand"] == ["auto"] + list(_brands().IDS)


def test_dc_asks_for_sizes_inside_the_genome():
    dims = genome.load_species("vending_machine")["dimensions"]
    for w, d, h in DC_SIZES:
        assert dims["width"]["min"] <= w <= dims["width"]["max"]
        assert dims["depth"]["min"] <= d <= dims["depth"]["max"]
        assert dims["height"]["min"] <= h <= dims["height"]["max"]


def test_a_variant_is_honoured_and_one_past_the_range_is_dropped():
    assert _kit(*DC_SIZES[0], variant=3)["modules"][0]["stem"].endswith("_h183_n3")
    plan = _kit(*DC_SIZES[0], variant=4)
    assert not plan["modules"][0]["stem"].endswith("_n4")
    assert plan["dressing_fallbacks"], "a variant past module_variants must be said"


# --- layout ----------------------------------------------------------------------------

@pytest.mark.parametrize("dims", CORNERS + tuple(_random_dims(30)))
def test_the_layout_claims_exactly_the_slot(dims):
    vf = _vf()
    w, d, h = dims
    got = vf.extents(vf.layout(w, d, h))
    for g, want in zip(got, (-w / 2, w / 2, -d / 2, d / 2, -h / 2, h / 2)):
        assert abs(g - want) <= 1e-9, (dims, got)


@pytest.mark.parametrize("dims", CORNERS)
def test_nothing_stands_proud_of_the_door_and_the_column_parts_sit_in_the_column(dims):
    vf = _vf()
    L = vf.layout(*dims)
    yf = L["yf"]
    cx0, cx1, cz0, cz1 = L["apertures"]["column"]
    column = ("display_bezel", "display_lens", "coin_mech", "coin_slot", "bill_mouth",
              "reject", "coin_return", "return_mouth", "lock", "lock_handle")
    for name in column:
        b = L[name]
        assert b[2] >= yf + 0.004 - 1e-9, name
        assert cx0 < b[0] and b[1] < cx1 and cz0 < b[4] and b[5] < cz1, (name, dims)
    for b in L["buttons"]:
        assert b[2] >= yf + 0.004 - 1e-9
        assert cx0 < b[0] and b[1] < cx1 and cz0 < b[4] and b[5] < cz1
    # the column's stack does not overlap itself
    zs = sorted([(L[n][4], L[n][5], n) for n in ("display_bezel", "coin_mech", "coin_return", "lock")]
                + [(b[4], b[5], "button") for b in L["buttons"]])
    for (a0, a1, na), (b0, b1, nb) in zip(zs, zs[1:]):
        assert a1 < b0, (na, nb, dims)


def test_every_burial_clears_the_probe_window():
    vf = _vf()
    assert vf.BURY >= 3 * PROBE_TOL


@pytest.mark.parametrize("dims", CORNERS)
def test_the_door_leaves_three_apertures_and_the_triangle_count_is_fixed(dims):
    vf = _vf()
    L = vf.layout(*dims)
    _xs, _zs, filled = vf.door_cells(L)
    assert sum(1 for col in filled for f in col if not f) == 5   # panel 3, column 1, flap 1
    assert vf.triangles(L) == TRIS <= TRI_BUDGET


def test_a_slot_too_small_for_a_machine_says_so():
    vf = _vf()
    with pytest.raises(ValueError):
        vf.layout(0.5, 0.6, 1.6)


# --- brands ----------------------------------------------------------------------------

def test_the_brand_table_is_complete_and_invented():
    br = _brands()
    vf = _vf()
    assert len(br.BRANDS) == 12
    assert len(set(br.IDS)) == len(br.IDS)
    keys = {"id", "logo", "drink", "slogan", "short", "bg", "ink", "edge",
            "slogan_ink", "emblem", "shape", "cabinet"}
    hexcol = re.compile(r"^#[0-9a-f]{6}$")
    for b in br.BRANDS:
        assert set(b) == keys, b["id"]
        for k in ("ink", "edge", "slogan_ink", "emblem", "cabinet"):
            assert hexcol.match(b[k]), (b["id"], k)
        assert all(hexcol.match(c) for c in b["bg"])
        assert b["shape"] in vf.EMBLEMS
        text = br.words(b).lower()
        for bad in br.FORBIDDEN_WORDS:
            assert bad not in text, (b["id"], bad)


@pytest.mark.parametrize("width", (0.7, 0.85, 1.05))
def test_every_brand_lays_out_on_the_narrowest_panel(width):
    """Logo lines, drink and slogan wrap into the panel with no word broken,
    at the genome's narrowest machine too."""
    vf, br = _vf(), _brands()
    L = vf.layout(width, 0.75, 1.6)
    for bid in br.IDS:
        a = vf.art(L, bid, "k")
        f = a["facts"]
        pw = a["rects"]["panel"][2]
        for line, s, x, _y, w, _h in f["logo"]:
            assert x >= 0 and x + w <= pw, (bid, line)
        assert f["slogan_lines"] and f["drink_lines"], bid
        assert f["slogan_band"][0] > f["logo_bottom"], bid


def test_slogans_and_labels_read_against_what_they_sit_on():
    vf, br = _vf(), _brands()
    for b in br.BRANDS:
        slogan = vf.contrast(br.hex_rgb(b["slogan_ink"]), br.hex_rgb(b["edge"]))
        assert slogan >= 4.5, (b["id"], round(slogan, 2))
        bg, fg = vf.label_colours(b)
        assert vf.contrast(bg, fg) >= 3.0, b["id"]


def test_every_button_label_fits_its_button():
    vf, br = _vf(), _brands()
    from zoo_keeper.core import pixel_type as pt
    lw = int(round(vf.BUTTON[0] * vf.LABEL_TEXEL))
    lh = int(round(vf.BUTTON[1] * vf.LABEL_TEXEL))
    for b in br.BRANDS:
        m = pt.trim(pt.render(b["short"], 1))
        assert len(m[0]) <= lw - 4 and len(m) <= lh - 4, b["short"]


def test_variants_of_one_slot_are_different_brands_and_stems_spread_over_the_table():
    vf, br = _vf(), _brands()
    got = []
    for variant in range(4):
        _mod, plan = _module_plan(variant=variant)
        got.append(vf.pick_brand(plan))
    assert len(set(got)) == 4, got
    spread = set()
    for style in range(1, 41):
        _mod, plan = _module_plan(style=style)
        spread.add(vf.pick_brand(plan))
    assert len(spread) >= 8, spread
    assert spread <= set(br.IDS)


def test_the_brand_is_the_same_every_build_and_an_asked_brand_wins():
    vf = _vf()
    mod, plan = _module_plan(variant=2)
    assert vf.pick_brand(plan) == vf.pick_brand(json.loads(json.dumps(plan)))
    plan["params"]["brand"] = "hoagie_sweat"
    assert vf.pick_brand(plan) == "hoagie_sweat"
    plan["params"]["brand"] = "auto"
    assert vf.pick_brand(plan) != "auto"


def test_a_lineup_is_the_brand_then_five_others():
    vf, br = _vf(), _brands()
    for bid in br.IDS:
        line = vf.lineup(bid, "stem")
        assert line[0] == bid and len(set(line)) == vf.N_BUTTONS == len(line)


def test_the_cabinet_wears_the_brand_unless_a_colour_was_asked():
    vf, br = _vf(), _brands()
    _mod, plan = _module_plan()
    b = br.BY_ID["wooder"]
    assert vf.paint_for(plan, b) == tuple(br.srgb_to_linear(c) for c in br.hex_rgb(b["cabinet"]))
    asked = dict(plan, color=[0.1, 0.2, 0.3])
    assert vf.paint_for(asked, b) == (0.1, 0.2, 0.3)


# --- artwork -----------------------------------------------------------------------------

def test_the_artwork_is_the_same_bytes_every_time_and_a_real_png():
    vf = _vf()
    _mod, plan = _module_plan()
    a = vf.resolve(plan)["art"]["canvas"].png()
    b = vf.resolve(json.loads(json.dumps(plan)))["art"]["canvas"].png()
    assert a == b
    assert a[:8] == b"\x89PNG\r\n\x1a\n"
    w, h = struct.unpack(">II", a[16:24])
    L = vf.resolve(plan)
    assert (w, h) == L["art"]["size"]
    raw = zlib.decompress(a[a.index(b"IDAT") + 4:-16])
    assert len(raw) == h * (1 + 3 * w)


def test_every_region_lies_in_the_texture_and_the_name_carries_the_pixels():
    vf = _vf()
    _mod, plan = _module_plan()
    A = vf.resolve(plan)["art"]
    W, H = A["size"]
    for name, (x0, y0, x1, y1) in A["rects"].items():
        assert 0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H, name
    assert A["name"].endswith("%08x" % (zlib.crc32(bytes(A["canvas"].buf)) & 0xFFFFFFFF))


def _pixelcoat_dir():
    for cand in (os.environ.get("PIXELCOAT_DIR"), os.path.join(os.path.dirname(_ZOO), "pixelcoat")):
        if cand and os.path.isdir(os.path.join(cand, "pixelcoat", "core")):
            return cand
    return None


def test_the_glyph_table_is_pixelcoats_typeface():
    """The table against the TTF Pixelcoat vendors, and Zoo's layout against
    Pixelcoat's own rasteriser. Skipped where Pixelcoat is not beside Zoo."""
    pc = _pixelcoat_dir()
    if pc is None:
        pytest.skip("Pixelcoat not found (set PIXELCOAT_DIR)")
    # PIL.Image, not PIL: inside Blender the host's pure-Python PIL package
    # imports and its C extension (built for another Python) does not
    pytest.importorskip("PIL.Image")
    sys.dont_write_bytecode = True
    import importlib.util
    spec = importlib.util.spec_from_file_location("mint", os.path.join(_ZOO, "tools", "mint_pixel_type.py"))
    mint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mint)
    have = open(os.path.join(_ZOO, "zoo_keeper", "core", "pixel_type_glyphs.py"), encoding="utf-8").read()
    assert mint.emit(mint.render_table(pc)) == have
    from pixelcoat.core import signage
    from zoo_keeper.core import pixel_type as pt
    for text, scale in (("WOODER", 2), ("IGGLES TEARS", 1), ("NANA'S BASEMENT", 3), ("75¢", 1)):
        ours = [list(r) for r in pt.trim(pt.render(text, scale))]
        theirs = signage._render_ttf(text, signage._face("bold", 16 * scale))
        assert ours == [[int(v) for v in row] for row in theirs.tolist()], text


# --- bpy: the built module --------------------------------------------------------------

def _build(tmp_path, dims, style=4, variant=0, params=None):
    from zoo_keeper.bpylayer import build as B
    mod = _kit(*dims, style=style, variant=variant)["modules"][0]
    if params:
        real = B.dna.resolve_module_plan

        def patched(*a, **k):
            p = real(*a, **k)
            p["params"].update(params)
            return p
        B.dna.resolve_module_plan = patched
        try:
            return B.build_module(mod, str(tmp_path), theme="delco_1997", style=style,
                                  options={"save_blend": False})
        finally:
            B.dna.resolve_module_plan = real
    return B.build_module(mod, str(tmp_path), theme="delco_1997", style=style,
                          options={"save_blend": False})


def _glb_json(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    return json.loads(b[20:20 + n])


@pytest.mark.parametrize("dims", CORNERS)
def test_bpy_fits_its_slot_with_every_part(tmp_path, dims):
    bpy = pytest.importorskip("bpy")
    res = _build(tmp_path, dims)
    checks = {c["id"]: c for c in res["report"]["checks"]}
    for cid in ("fit_width", "fit_depth", "fit_height", "fit_pivot", "collision",
                "wear_colors", "uvs", "parts_named", "materials", "transforms", "tri_budget"):
        assert checks[cid]["level"] == "pass", (dims, checks[cid])
    assert res["report"]["status"] == "pass"
    f = res["facts"]
    for axis, v in zip(("width", "depth", "height"), dims):
        assert abs(f["dimensions"][axis] - v) <= 0.001, (dims, axis, f["dimensions"])
    assert max(abs(c) for c in f["center"]) <= 0.001
    g = json.load(open(_GENOME, encoding="utf-8"))
    assert sorted(f["parts"]) == sorted(g["parts"])
    assert f["tris"] == TRIS
    col = [o for o in bpy.context.scene.objects if o.name.endswith("-colonly")]
    assert len(col) == 1


def _emission(mat):
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    sock = bsdf.inputs["Emission Color"]
    img = sock.links[0].from_node.image if sock.is_linked else None
    return bsdf.inputs["Emission Strength"].default_value, img


def test_bpy_the_panel_buttons_and_display_glow_and_the_file_says_so(tmp_path):
    bpy = pytest.importorskip("bpy")
    vf, br = _vf(), _brands()
    res = _build(tmp_path, DC_SIZES[0])
    objs = {o.name: o for o in bpy.context.scene.objects}
    want = {"Vending_Panel": ("_Face", vf.PANEL_EMISSION),
            "Vending_Buttons": ("_Lens", vf.LENS_EMISSION),
            "Vending_DisplayLens": ("_Lens", vf.LENS_EMISSION)}
    lit_names = set()
    for part, (suffix, strength) in want.items():
        mat = objs[part].data.materials[0]
        assert mat.name.startswith("M_") and mat.name.endswith(suffix), mat.name
        s, img = _emission(mat)
        assert s == pytest.approx(strength) and s > 0
        assert img is not None and img.packed_file is not None
        lit_names.add(mat.name)
    for name, o in objs.items():
        if o.type == "MESH" and name not in want and not name.endswith("-colonly"):
            s, _img = _emission(o.data.materials[0])
            assert s == 0.0 or o.data.materials[0].name not in lit_names, name
    # the brand is from the table and names the lit materials
    brand = next(b for b in br.IDS if f"M_Vending_{b}_" in objs["Vending_Panel"].data.materials[0].name)
    assert brand == vf.pick_brand(_module_plan()[1])
    # and the GLB carries it: emissive texture, strength, dimmed base colour
    g = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    mats = {m["name"]: m for m in g["materials"]}
    for name in lit_names:
        m = mats[name]
        assert m["emissiveFactor"] == [1, 1, 1]
        assert "emissiveTexture" in m
        # the exporter writes the extension only above 1.0
        strength = (m.get("extensions", {}).get("KHR_materials_emissive_strength", {})
                    .get("emissiveStrength", 1.0))
        assert strength == pytest.approx(vf.PANEL_EMISSION if name.endswith("_Face") else vf.LENS_EMISSION)
        assert m["pbrMetallicRoughness"]["baseColorFactor"][0] == pytest.approx(vf.PANEL_ALBEDO, abs=1e-6)
    assert any(i["name"].startswith(f"vending_{brand}_") for i in g["images"])


def test_bpy_lit_zero_is_a_machine_with_its_plug_pulled(tmp_path):
    """Dark IN THE FILE. Strength 0 with the texture still linked exports an
    emissiveTexture with no emissiveFactor, which Godot 4.7 imports as
    emission on at energy 1.0 -- so the file is what is checked."""
    bpy = pytest.importorskip("bpy")
    res = _build(tmp_path, DC_SIZES[0], params={"lit": 0})
    objs = {o.name: o for o in bpy.context.scene.objects}
    names = set()
    for part in ("Vending_Panel", "Vending_Buttons", "Vending_DisplayLens"):
        mat = objs[part].data.materials[0]
        s, img = _emission(mat)
        assert s == 0.0 and img is None, part
        names.add(mat.name)
    g = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    for m in g["materials"]:
        if m["name"] in names:
            assert "emissiveTexture" not in m and not any(m.get("emissiveFactor", [0])), m
            assert "baseColorTexture" in m["pbrMetallicRoughness"], m["name"]


def test_bpy_the_same_file_every_build_and_four_variants_four_brands(tmp_path):
    pytest.importorskip("bpy")
    digests, images = [], set()
    for k in range(2):
        out = tmp_path / f"a{k}"
        res = _build(out, DC_SIZES[0])
        digests.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert digests[0] == digests[1]
    for variant in range(4):
        out = tmp_path / f"v{variant}"
        res = _build(out, DC_SIZES[0], variant=variant)
        g = _glb_json(os.path.join(str(out), res["files"]["glb"]))
        images |= {i["name"] for i in g["images"] if i["name"].startswith("vending_")}
    assert len(images) == 4, images


def _probe():
    import runpy
    saved = sys.argv
    sys.argv = ["coplanar_probe.py", "--"]
    try:
        return runpy.run_path(os.path.join(_ZOO, "tools", "coplanar_probe.py"))
    finally:
        sys.argv = saved


@pytest.mark.parametrize("dims", CORNERS[:6])
def test_bpy_no_two_faces_share_a_plane(tmp_path, dims):
    bpy = pytest.importorskip("bpy")
    import mathutils
    probe = _probe()
    _build(tmp_path, dims)
    objs = probe["_visual_meshes"](bpy, bpy.context.scene)
    rows, ntri = probe["probe"](bpy, mathutils, objs, PROBE_TOL, 1e-6, 1e-3)
    assert ntri == TRIS
    assert rows == [], (dims, rows[:4])
