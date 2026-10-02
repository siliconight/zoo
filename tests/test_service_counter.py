"""1.7.0 -- the convenience store's service counter: `counter` form
``service``, the candy rack and the cigarette rack overhead.

The walker, 2026-09-27: "start with the service counter, cigarette overhead
and candy rack", from the 1990s photograph of the store's service island
(docs/SET_DRESSING_REFERENCES.md, 2026-09-15).

Pure half (`core/service_counter_forms.py`, `core/candy_brands.py`): the
fit-out stays inside the slot where it must and above it where it may, no
two of its faces share a plane, the budget, a rack that clears every
register or is not built, the art's bytes and what it says, the invented
brands and the denylist. Built half (bpy, skipped without it): PASS and
fit, the header the only thing lit, the paint painted, determinism.
"""
from __future__ import annotations

import itertools
import re

import pytest

from zoo_keeper.core import candy_brands as CANDY
from zoo_keeper.core import cigarette_brands as CB
from zoo_keeper.core import genome as genome_mod
from zoo_keeper.core import prims as P
from zoo_keeper.core import service_counter_forms as S
from zoo_keeper.recipes._bays import bays

#: Deli Counter's `register_counter` in the gas_station preset, then the
#: club's bar sizes, then the genome's corners.
DC_SIZES = ((6.0, 0.9, 1.1), (4.0, 0.8, 1.05), (2.0, 0.65, 0.95))
_G = genome_mod.load_species("counter")


def _corners():
    r = _G["dimensions"]
    return [tuple(c) for c in itertools.product(*((r[a]["min"], r[a]["max"])
                                                   for a in ("width", "depth", "height")))]


def _fit(w, d, h, variant=1):
    """The recipe's own numbers, as `recipes/counter.py` derives them."""
    lip, top_t, base_h = 0.02, 0.045, 0.07
    top_w = w + 2 * lip
    body_d = d * 0.85
    body_y = (d - body_d) / 2.0
    face_y = body_y - body_d / 2.0
    runs = bays(w, 4.0)
    att = {("ATT_register" if len(runs) == 1 else f"ATT_register_B{i + 1}"): (bx + bw * 0.15, 0.0, h)
           for i, (bx, bw) in enumerate(runs)}
    inside, on_top, facts = S.fitout(w, d, h, att, top_w, face_y, base_h, top_t, "counter_service", variant)
    return inside, on_top, facts, top_w


CASES = list(DC_SIZES) + _corners()


@pytest.mark.parametrize("dims", CASES)
def test_the_fitout_stays_inside_the_slot_where_it_must_and_shares_no_plane(dims):
    w, d, h = dims
    inside, on_top, facts, top_w = _fit(w, d, h)
    lo, hi = P.bounds(inside)
    # inside the slot: under the top, within its ends, never past its front
    assert lo[1] >= -d / 2.0 - 1e-9 and hi[1] <= d / 2.0 + 1e-9, (dims, lo, hi)
    assert lo[0] >= -top_w / 2.0 - 1e-9 and hi[0] <= top_w / 2.0 + 1e-9
    assert lo[2] > 0.0 and hi[2] <= h - 0.045
    # on top: standing on the top, within the counter's ends
    lo2, hi2 = P.bounds(on_top)
    # buried 4 mm into the top, the lottery towers 2 mm deeper each so no
    # two of them share the top's plane
    assert h - 0.012 <= lo2[2] <= h - 0.004 + 1e-9, (dims, lo2)
    assert lo2[0] >= -top_w / 2.0 - 1e-9 and hi2[0] <= top_w / 2.0 + 1e-9, (dims, lo2, hi2)
    assert P.coincident_pairs(inside + on_top, tol=0.0022) == []
    assert P.tri_count(inside + on_top) <= S.TRI_BUDGET


@pytest.mark.parametrize("dims", DC_SIZES)
def test_the_candy_rack_reaches_the_overhang_and_no_further(dims):
    """A walk-into solid stays inside its collision, and the module's
    collision is the counter's box: the lowest tier ends 4 mm short of the
    slot's front."""
    w, d, h = dims
    inside, _on, facts, _tw = _fit(w, d, h)
    tiers = [p for p in inside if p["part"] == "Counter_CandyTier"]
    assert len(tiers) == S.TIERS
    front = min(v[1] for p in tiers for v in p["verts"])
    assert front == pytest.approx(-d / 2.0 + 0.004, abs=1e-6)
    reaches = [t["reach"] for t in facts["tiers"]]
    assert reaches == sorted(reaches, reverse=False) or reaches == sorted(reaches, reverse=True)
    assert max(reaches) > min(reaches)


def test_a_register_at_every_station_and_lottery_beside_it():
    _in, on_top, facts, _tw = _fit(6.0, 0.9, 1.1)
    assert len(facts["registers"]) == 2            # two bays of at most 4 m
    assert len(facts["lottery"]) == 2 * S.LOTTO_MAX
    # 1.46.0: a register is painted faces; one key block a station
    regs = [p for p in on_top if p["part"] == "Counter_RegisterKeys"]
    assert len(regs) == 2
    # 1.47.0: a dispenser is painted faces under one stem; its foot is the
    # part that stands at the customer edge
    feet = [p for p in on_top if p["part"] == "Counter_Lottery_Foot_front"]
    assert len(feet) == 2 * S.LOTTO_MAX
    for p in feet:
        assert min(v[1] for v in p["verts"]) == pytest.approx(-0.45 + S.LOTTO_IN, abs=1e-6)


def test_the_rack_clears_every_register_or_is_not_built():
    _in, on_top, facts, _tw = _fit(6.0, 0.9, 1.1)
    rack = facts["rack"]
    assert rack is not None and rack["w"] == S.RACK_W_MAX
    posts = [p for p in on_top if p["part"] == "Counter_CigPost"]
    assert len(posts) == 2
    for p in posts:
        px = sum(v[0] for v in p["verts"]) / len(p["verts"])
        assert all(abs(px - ax) >= S.REG_W / 2.0 + S.POST_R for ax in facts["registers"]), (px, facts["registers"])
    # the rack is over the clerk's head
    assert rack["z"][0] >= 1.9
    # a kiosk gets no rack rather than a post through its till
    _in2, on2, f2, _ = _fit(0.8, 0.5, 0.85)
    assert f2["rack"] is None
    assert not [p for p in on2 if p["part"].startswith("Counter_Cig")]


def test_the_rack_faces_the_customer_and_the_header_is_the_lit_face():
    _in, on_top, facts, _tw = _fit(6.0, 0.9, 1.1)
    # 1.16.0: the register windows carry ``uvs`` too, on their own image;
    # 1.46.0: and so does every painted face of the register
    art = next(p for p in on_top if "uvs" in p and p["mat"] not in ("vfd", "regpaint"))
    assert art["part"] == "Counter_CigRackArt"
    front = min(v[1] for v in art["verts"])
    # the art's front is on the rack's customer side (-Y), set behind its edge
    assert front < facts["rack"]["y"][0] + 0.001
    assert art["face_mats"].count("lit") == 1
    lit_face = art["faces"][art["face_mats"].index("lit")]
    assert min(art["verts"][i][2] for i in lit_face) == pytest.approx(facts["rack"]["header_z"])


def test_the_art_is_deterministic_and_says_what_it_should():
    _in, _on, facts, _tw = _fit(6.0, 0.9, 1.1, variant=2)
    a = S.rack_art(facts, "counter_service", 2)
    b = S.rack_art(facts, "counter_service", 2)
    assert a["name"] == b["name"] and bytes(a["canvas"].buf) == bytes(b["canvas"].buf)
    assert S.rack_art(facts, "counter_service", 3)["name"] != a["name"]
    assert a["header"] in CB.IDS
    assert len(a["rows"]) == S.RACK_ROWS and all(len(r) == facts["rack"]["n_packs"] for r in a["rows"])
    assert a["rows"][0][0] == a["header"]
    assert a["size"][0] == int(round(facts["rack"]["w"] * S.RACK_TEXEL)) - int(round(0.04 * S.RACK_TEXEL))
    # the header's words are the brand's, none of them a real mark
    said = " ".join(a["said"]).upper()
    for w_ in CB.DENY_WORDS:
        assert not re.search(rf"\b{re.escape(w_)}\b", said), w_
    c = S.candy_art(facts["tiers"], "counter_service", 2)
    assert sorted(c) == list(range(S.TIERS))
    for k, t in c.items():
        assert t["size"][0] == int(S.ART_REPEAT_M * S.CANDY_TEXEL)
        assert all(b in CANDY.BAR_IDS for b in t["brands"])
    # three tiers lead with three different bars
    assert len({c[k]["brands"][0] for k in c}) == S.TIERS
    assert S.candy_art(facts["tiers"], "counter_service", 2)[0]["name"] == c[0]["name"]


def test_one_atlas_holds_the_candy_and_the_checker_and_repeats_cleanly():
    """1.8.0: the trim and the three tiers paint one image. It is one metre
    of art wide, a whole and even number of checker squares, so both the
    candy and the checker meet themselves at the repeat."""
    inside, _on, facts, _tw = _fit(6.0, 0.9, 1.1)
    A = S.paint_atlas(facts["tiers"], "counter_service", 1)
    W, H = A["size"]
    assert W == int(round(S.ART_REPEAT_M * S.CANDY_TEXEL))
    n = S.CHECKER_PX
    assert n == pytest.approx(S.CHECK * S.CANDY_TEXEL) and W % (2 * n) == 0
    assert sorted(A["bands"]) == ["candy_0", "candy_1", "candy_2", "checker"]
    # the bands tile the image top to bottom with no gap and no overlap
    spans = sorted(A["bands"].values())
    assert spans[0][0] == 0 and spans[-1][1] == H
    assert all(a[1] == b[0] for a, b in zip(spans, spans[1:]))
    # the checker band: two rows, alternating, and the first and last
    # squares of a row differ so the wrap continues the pattern
    c = A["canvas"]
    y0, y1 = A["bands"]["checker"]
    assert y1 - y0 == 2 * n
    assert c.get(0, y0) != c.get(n, y0) and c.get(0, y0) == c.get(n, y0 + n)
    assert c.get(0, y0) != c.get(W - 1, y0)
    # the candy bands are the tiers' own art, pasted
    tiles = S.candy_art(facts["tiers"], "counter_service", 1)
    for k in range(S.TIERS):
        ty0, _ty1 = A["bands"]["candy_%d" % k]
        src = tiles[k]["canvas"]
        assert all(c.get(x, ty0 + y) == src.get(x, y) for x in (0, 57, 399) for y in (0, 10, src.h - 1))
    assert S.paint_atlas(facts["tiers"], "counter_service", 1)["name"] == A["name"]
    # every painted part's u repeats once a metre; v is 0..1 of its band
    for p in (q for q in inside if "paint" in q):
        su, ou, sv, ov = p["uv_xz"]
        assert su == pytest.approx(1.0 / S.ART_REPEAT_M)
        zs = [v[2] for v in p["verts"]]
        vs = [z * sv + ov for z in zs]
        assert min(vs) == pytest.approx(0.0, abs=1e-9) and max(vs) == pytest.approx(1.0, abs=1e-9), p["part"]


def test_atlas_v_stays_half_a_pixel_inside_its_band():
    size = (400, 300)
    band = (40, 80)
    lo, hi = S.atlas_v(band, size, 0.0), S.atlas_v(band, size, 1.0)
    # in pixel rows, 0 at the top: the band's bottom row centre and top row centre
    assert (1.0 - lo) * size[1] == pytest.approx(79.5)
    assert (1.0 - hi) * size[1] == pytest.approx(40.5)


def test_one_material_per_kind_and_the_colours_survive_the_move():
    """1.8.0: every `mat` key maps to one material per KIND, and the colour
    the part used to carry in its material is exactly base x factor."""
    kinds = {}
    for mk, (rgb, kind) in S.MATERIALS.items():
        k2, factor = S.vertex_tint(mk)
        assert k2 == kind
        got = tuple(b * f for b, f in zip(S.KIND_BASE[kind], factor))
        assert got == pytest.approx(tuple(rgb)), mk
        assert all(0.0 <= f <= 1.0 for f in factor), (mk, factor)   # COLOR_0 cannot exceed 1
        kinds.setdefault(kind, []).append(mk)
    # 1.47.0: no `plastic`. Its only users were the tills' bodies and the
    # lottery dispensers, and both are painted into the till's image now
    assert sorted(kinds) == ["laminate", "metal_painted"]
    assert sorted(S.KIND_BASE) == ["laminate", "metal_painted"]
    assert all(0.0 < f <= 1.0 for t in S.BODY_TINT.values() for f in t)


def test_every_candy_brand_is_invented_and_legible():
    seen = set()
    for b in CANDY.BRANDS:
        assert b["id"] not in seen
        seen.add(b["id"])
        assert b["design"] in CANDY.DESIGNS and b["kind"] in ("bar", "gum")
        up = CANDY.words(b).upper()
        toks = set(re.findall(r"[A-Z0-9&']+", up))
        for w_ in CANDY.DENY_WORDS:
            assert w_ not in toks, (b["id"], w_)
        for part in CANDY.DENY_PARTS:
            assert part not in up, (b["id"], part)
        assert len(b["short"]) <= 6
    assert len(CANDY.BAR_IDS) >= 6 and len(CANDY.GUM_IDS) >= 2


def test_the_genome_offers_the_form_and_names_the_parts():
    g = genome_mod.load_species("counter")
    assert "service" in g["params"]["form"]
    # 1.47.0: the lottery dispensers are in `Counter_RegisterArt`, the one
    # painted object on a counter's top
    for part in ("Counter_Trim", "Counter_CandyTier", "Counter_CandyArt", "Counter_RegisterArt",
                 "Counter_CigPost", "Counter_CigRack", "Counter_CigRackArt"):
        assert part in g["parts"], part
    assert "Counter_Lottery" not in g["parts"]
    assert genome_mod.validate_genome(g) == []


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _build(tmp_path, dims, **fields):
    """The cigarette machine's idiom: a Deli Counter slot through
    `kit.plan_kit` and `build.build_module`, so the form arrives the way a
    package's does."""
    import bpy
    from zoo_keeper.bpylayer import build
    from zoo_keeper.bpylayer.export import _COL_SUFFIXES
    from zoo_keeper.core import kit
    slot = {"slot_id": "register_counter", "role": "prop", "size_mod": "full", "style": 1,
            "species": "counter", "material": "laminate", "form": "service",
            "fit": {"dims": list(dims), "pivot": "center"}}
    slot.update(fields)
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["dressing_fallbacks"] == [], plan["dressing_fallbacks"]
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997",
                             style=1, options={"save_blend": False})
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES)), key=lambda o: o.name)
    return res, objs


def _glb_json(path):
    import json
    import struct
    raw = open(path, "rb").read()
    n = struct.unpack("<I", raw[12:16])[0]
    return json.loads(raw[20:20 + n])


@pytest.mark.parametrize("dims", DC_SIZES)
def test_bpy_the_service_counter_passes_and_fits(tmp_path, dims):
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, dims)
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    got = res["facts"]["dimensions"]
    for k, want in zip(("width", "depth", "height"), dims):
        assert abs(got[k] - want) <= 0.001, got
    names = {o.name for o in objs}
    parts = set(genome_mod.load_species("counter")["parts"])
    for o in objs:
        assert any(o.name == p or o.name.startswith(p + "_") for p in parts), o.name
    # every part of the fit-out is there, by its genome name or a suffix of
    # it: the painted parts are built one object each and named apart
    # (Counter_Trim_top, Counter_CandyArt_T1 ...), never Blender's `.001`
    for want in ("Counter_Trim", "Counter_CandyTier", "Counter_CandyArt", "Counter_RegisterArt",
                 "Counter_RegisterScreen", "Counter_CigPost", "Counter_CigRack", "Counter_CigRackArt"):
        assert any(n == want or n.startswith(want + "_") for n in names), (want, names)
    assert not any("." in n for n in names), names


def test_bpy_only_the_rack_header_and_the_registers_glow_and_the_paint_is_paint(tmp_path):
    """1.16.0: the registers' green displays are the second lit surface
    (`counter_register`); before it the rack's header was the only one."""
    import os
    pytest.importorskip("bpy")
    res, objs = _build(tmp_path, DC_SIZES[0])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    lit = sorted(m["name"] for m in doc["materials"] if (m.get("emissiveFactor") and any(m["emissiveFactor"]))
                 or "emissiveTexture" in m)
    assert len(lit) == 2 and all(n.endswith("_Face") for n in lit), lit
    assert lit[0].startswith("M_Counter_CigRack_") and lit[1].startswith("M_Counter_VFD_"), lit
    painted = [m["name"] for m in doc["materials"]
               if "baseColorTexture" in m.get("pbrMetallicRoughness", {})]
    assert len([n for n in painted if n.startswith("M_Counter_Paint_")]) == 1
    assert any(n.startswith("M_Counter_CigRack_") and n.endswith("_Display") for n in painted)
    # the trim and the candy strips tile, the rack's display clamps. glTF's
    # default wrap IS repeat (10497), so the exporter writes no sampler or no
    # wrapS for a tiling texture and 33071 (CLAMP_TO_EDGE) for a clamped one.
    def wrap_of(mat_name):
        m = next(m for m in doc["materials"] if m["name"] == mat_name)
        ti = m["pbrMetallicRoughness"]["baseColorTexture"]["index"]
        si = doc["textures"][ti].get("sampler")
        if si is None:
            return 10497
        return doc["samplers"][si].get("wrapS", 10497)
    assert wrap_of(next(n for n in painted if n.startswith("M_Counter_Paint_"))) == 10497
    assert wrap_of(next(n for n in painted if n.endswith("_Display"))) == 33071


def test_bpy_seven_materials_seven_submissions_and_no_colour_only_twins(tmp_path):
    """1.8.0, the point of the release: 1.7.0 shipped this counter as 15
    meshes over 14 materials. Now one material per surface kind, one
    painted atlas, the rack's display and its lit header -- and no two
    skinned materials that differ in nothing but the tint in their name.
    1.16.0: seven. The registers' green displays are one more backlit image,
    ``M_Counter_VFD_<art>_Face``, whatever the register count.

    1.46.0: eight. The registers' bodies rode in the counter's shared plastic
    as flat-coloured boxes; painted (`counter_register.paint_art`) they are
    one more image, ``M_Counter_Register_<art>_Art``.

    1.47.0: SEVEN AGAIN. The lottery dispensers were the last thing in that
    shared plastic; painted into the till's image they ride in its draw, and
    ``M_Counter_svc_plastic`` has nothing left to draw. So the painted till
    and the painted dispensers together cost the counter no draw over
    1.45.0's flat boxes."""
    import os
    import re as _re
    pytest.importorskip("bpy")
    res, _objs = _build(tmp_path, DC_SIZES[0])
    doc = _glb_json(os.path.join(str(tmp_path), res["files"]["glb"]))
    names = [m["name"] for m in doc["materials"]]
    assert len(names) == 7, names
    assert "M_Counter_svc_plastic" not in names, names
    assert sum(1 for n in names if n.startswith("M_Counter_VFD_") and n.endswith("_Face")) == 1, names
    assert sum(1 for n in names if n.startswith("M_Counter_Register_") and n.endswith("_Art")) == 1, names
    # visual submissions only: a collision proxy (`-colonly` and kin) becomes
    # a collider on import and is never drawn
    from zoo_keeper.core import partnames
    visual = [m for m in doc["meshes"] if not m["name"].endswith(tuple(partnames.COL_SUFFIXES))]
    prims = sum(len(m["primitives"]) for m in visual)
    assert prims == 7, (prims, [m["name"] for m in visual])
    assert len(visual) < len(doc["meshes"]), "the collision proxy should still be exported"
    kinds = [(_re.match(r"M_Skin_([a-z_]+?)_delco_1997", n) or [None, n])[1] for n in names
             if n.startswith("M_Skin_")]
    assert len(kinds) == len(set(kinds)), names
    # the colour rode into COLOR_0: the merged plastic is not all one value
    for mesh in visual:
        for prim in mesh["primitives"]:
            mat = names[prim["material"]]
            if "plastic" in mat:
                assert "COLOR_0" in prim["attributes"], mat


def test_bpy_the_same_file_every_build(tmp_path):
    import os
    pytest.importorskip("bpy")
    files = []
    for k in range(2):
        out = tmp_path / ("a%d" % k)
        res, _o = _build(out, DC_SIZES[0], variant=2)
        files.append(open(os.path.join(str(out), res["files"]["glb"]), "rb").read())
    assert files[0] == files[1]
