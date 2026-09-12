r"""Mint a species, or list what the library is asking for (roadmap 150).

    python tools/new_species.py report [--build ../deli_counter/build] [--top 25]
    python tools/new_species.py new <species> --width W --depth D --height H
        [--like prop] [--material metal] [--keywords pump,gas_pump]
        [--genome-dir DIR --recipes-dir DIR --tests-dir DIR --minted FILE]

WHY THIS EXISTS. The deliverable is a factory somebody new points at their
game; the gap protocol (USING_THE_FACTORY.md) says that when a design asks
for a thing no tool makes, the owning tool grows the capability and nothing
is hand-authored downstream. For props the owning tool is Zoo, and until
this file "grow the capability" meant reading five recipes, a genome
schema and a test file to learn the shape. Measured 2026-09-12 over the
1,443 placements in Deli Counter's specs: 822 carry no species hint at all
-- crates and columns that are boxes by nature, and 328 that NAME a thing
(`pump` 42, `canopy_col` 42, `planter_box` 44, `supply_cart` 18, `kiosk`)
the library has no species for. `report` lists those by name so the next
species to mint is a count rather than a guess; `new` writes the genome,
a placeholder recipe, and a test, registers the species, and prints the
one line Deli Counter's keyword table needs.

WHAT `new` WRITES, and what it does not. A genome copied from `--like`
(default `prop`) with the given dims as defaults and a 0.5x..2.0x range,
the keywords, one named part; a recipe that builds a solid box of the
plan's exact dims with that part name, collision and a top attachment --
so it validates, ships, and reads as the species in every report -- with
a docstring that says it is the placeholder silhouette to be shaped; a
test that the species is discovered, validates and plans at its dims;
and a line in `genome/minted.json`, which `tests/test_genome.py` unions
into its known set. It does NOT invent the shape: a pump that is a box is
the honest state of a pump nobody has drawn, and the recipe file is where
the drawing goes.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)

from zoo_keeper.core import genome as genome_mod  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

RECIPE_TEMPLATE = '''"""{species} recipe: PLACEHOLDER SILHOUETTE, minted {date} by tools/new_species.py.

A solid center-pivot box built to the plan's exact dims, one named part,
collision and a top attachment -- so the species validates, ships and is
counted as itself in every kit report. It is NOT yet a {species}: this file
is where the drawing goes. Shape it the way `desk.py` or `counter.py` shape
theirs -- boxes from `geometry.add_box` per part, `part(bm, name)` to turn
each into an object, a collision box per solid, and keep the overall
extents equal to (w, d, h): Deli Counter places this module on a slot of
exactly that size and `validate` fails a module that is not.
"""
from __future__ import annotations

from ..bpylayer import geometry, materials


def build(plan, streams, collection):
    w = plan["dimensions"]["width"]
    d = plan["dimensions"]["depth"]
    h = plan["dimensions"]["height"]
    bevel, wear = plan["bevel"], plan["wear"]
    rng = streams.stream("wear")
    objs, cboxes = [], []

    def part(bm, name):
        objs.append(geometry.bm_to_object(
            bm, name, collection, bevel=bevel, texel=1.2, rng=rng, wear=wear))

    bm = geometry.new_bm()
    geometry.add_box(bm, (0.0, 0.0, h / 2), (w, d, h))
    part(bm, "{root}_Body")
    cboxes.append(((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h)))

    surface = materials.make_material(
        f"M_{root}_{{plan['material']}}", plan["color"], plan["material"])
    materials.assign(objs, surface)
    return {{"objects": objs, "collision_boxes": cboxes,
            "attachments": {{"ATT_top": (0.0, 0.0, h)}}}}
'''

TEST_TEMPLATE = '''"""{species}: minted {date} by tools/new_species.py (roadmap 150)."""
from zoo_keeper.core import genome, kit


def test_{species}_is_discovered_and_validates():
    assert "{species}" in genome.list_species()
    assert genome.validate_genome(genome.load_species("{species}")) == []


def test_{species}_plans_at_its_authored_dims():
    plan = kit.plan_kit({{"building_id": "t", "slots": [{{
        "slot_id": "{species}_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "{species}",
        "fit": {{"dims": [{w}, {d}, {h}], "pivot": "center"}}}}]}},
        theme="delco", style=1)
    assert plan["species_fallbacks"] == []
    assert plan["modules"][0]["species"] == "{species}"
'''


def root_name(species: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in species.split("_"))


def cmd_report(args) -> int:
    build = os.path.abspath(args.build)
    manifests = sorted(glob.glob(os.path.join(build, "*.slots.json")))
    if not manifests:
        print(f"no *.slots.json under {build}", file=sys.stderr)
        return 2
    unhinted = collections.Counter()
    fallbacks = collections.Counter()
    no_genome = collections.Counter()
    hinted = 0
    for p in manifests:
        with open(p, encoding="utf-8") as f:
            m = json.load(f)
        props = [s for s in m.get("slots", []) if s.get("role") == "prop"
                 and (s.get("fit") or {}).get("dims")]
        for s in props:
            if not s.get("species"):
                unhinted[re.sub(r"_\d+$", "", str(s.get("slot_id", "")))] += 1
        hinted += sum(1 for s in props if s.get("species"))
        plan = kit.plan_kit({"building_id": "r", "slots": props},
                            theme="delco", style=1)
        for fb in plan.get("species_fallbacks", []):
            if str(fb.get("reason", "")).startswith("no genome"):
                no_genome[fb["hint"]] += 1
            else:
                fallbacks[fb["hint"]] += 1
    print(f"{len(manifests)} manifests; {hinted} hinted prop slots")
    if no_genome:
        print("HINTED TO A SPECIES THAT DOES NOT EXIST (mint these first):")
        for k, n in no_genome.most_common():
            print(f"  {n:4d}  {k}")
    print(f"NO SPECIES HINT ({sum(unhinted.values())} slots) -- the names, most "
          f"common first; a keyword in deli_counter/prop_species.py routes one, "
          f"`new` mints one:")
    for k, n in unhinted.most_common(args.top):
        print(f"  {n:4d}  {k}")
    if fallbacks:
        print("HINTED, SPECIES EXISTS, DID NOT FIT (a range or a bay, not a mint):")
        for k, n in fallbacks.most_common():
            print(f"  {n:4d}  {k}")
    return 0


def cmd_new(args) -> int:
    sp = args.species.strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", sp):
        print(f"species name must be snake_case: {sp!r}", file=sys.stderr)
        return 2
    genome_dir = os.path.abspath(args.genome_dir)
    recipes_dir = os.path.abspath(args.recipes_dir)
    tests_dir = os.path.abspath(args.tests_dir)
    minted = os.path.abspath(args.minted)
    gpath = os.path.join(genome_dir, f"{sp}.json")
    rpath = os.path.join(recipes_dir, f"{sp}.py")
    tpath = os.path.join(tests_dir, f"test_{sp}.py")
    for p in (gpath, rpath, tpath):
        if os.path.exists(p):
            print(f"refusing: {p} exists", file=sys.stderr)
            return 2
    try:
        like = genome_mod.load_species(args.like)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    w, d, h = float(args.width), float(args.depth), float(args.height)
    if min(w, d, h) <= 0.0:
        print("dims must be positive", file=sys.stderr)
        return 2
    root = root_name(sp)
    keywords = [k.strip() for k in (args.keywords or sp).split(",") if k.strip()]
    g = json.loads(json.dumps(like))
    g["species"] = sp
    g["version"] = 1
    g["license"] = {"construction_knowledge": "CC0",
                    "notes": (f"Minted {args.date} by tools/new_species.py from "
                              f"'{args.like}': a placeholder box at the authored "
                              f"dims until the recipe is shaped.")}
    g["dimensions"] = {k: {"min": round(v * args.min_scale, 3),
                           "max": round(v * args.max_scale, 3),
                           "default": round(v, 3)}
                       for k, v in (("width", w), ("depth", d), ("height", h))}
    g["parts"] = [f"{root}_Body"]
    g["params"] = {}
    g["attachments"] = []
    g["keywords"] = keywords
    g["match_priority"] = 0
    if args.material:
        opts = list(g.get("materials", {}).get("options", []))
        if args.material not in opts:
            opts.append(args.material)
        g["materials"] = {"default": args.material, "options": opts}
        for st in g.get("styles", {}).values():
            st["material"] = args.material
    problems = genome_mod.validate_genome(g)
    if problems:
        print("genome would not validate: " + "; ".join(problems), file=sys.stderr)
        return 2
    os.makedirs(genome_dir, exist_ok=True)
    os.makedirs(recipes_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)
    with open(gpath, "w", encoding="utf-8") as f:
        json.dump(g, f, indent=2)
        f.write("\n")
    with open(rpath, "w", encoding="utf-8") as f:
        f.write(RECIPE_TEMPLATE.format(species=sp, root=root, date=args.date))
    with open(tpath, "w", encoding="utf-8") as f:
        f.write(TEST_TEMPLATE.format(species=sp, date=args.date, w=w, d=d, h=h))
    reg = []
    if os.path.exists(minted):
        with open(minted, encoding="utf-8") as f:
            reg = json.load(f)
    if sp not in reg:
        reg.append(sp)
    with open(minted, "w", encoding="utf-8") as f:
        json.dump(sorted(reg), f, indent=2)
        f.write("\n")
    print(f"minted '{sp}' ({w} x {d} x {h}, range {args.min_scale}x..{args.max_scale}x):")
    print(f"  genome  {gpath}")
    print(f"  recipe  {rpath}   <- the placeholder box; shape it here")
    print(f"  test    {tpath}")
    print(f"  registry {minted}")
    print("route Deli Counter's placements to it -- add to "
          "deli_counter/prop_species.py PROP_SPECIES, before any broader keyword:")
    print(f"    (({', '.join(repr(k) for k in keywords)},), \"{sp}\"),")
    _say_texture(g["materials"]["default"], args.theme)
    return 0


def _say_texture(kind: str, theme: str | None) -> None:
    """A species wears a KIND; a theme with no profile for it renders flat.
    Say which, and the pixelcoat command that mints one (roadmap 150, the
    texture half). Reads the sibling repo when it is there; silent if not."""
    themes = os.path.join(os.path.dirname(REPO), "pixelcoat", "profiles", "themes")
    if not theme or not os.path.isdir(themes):
        return
    tpath = os.path.join(themes, f"{theme}.json")
    if not os.path.isfile(tpath):
        print(f"texture: no theme '{theme}' in pixelcoat/profiles/themes; nothing checked")
        return
    with open(tpath, encoding="utf-8") as f:
        mats = json.load(f).get("materials", {})
    if kind in mats:
        print(f"texture: theme {theme} dresses '{kind}' with '{mats[kind]}'")
        return
    print(f"texture: theme {theme} has NO profile for '{kind}' -- the species renders "
          f"flat there. Mint one:")
    print(f"    python ../pixelcoat/tools/new_material.py new {kind}_{theme} --kind {kind} "
          f"--like <template profile> --colors '#..,#..,#..' --theme {theme}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report", help="what the library asks for and has no species for")
    r.add_argument("--build", default=os.path.join(REPO, "..", "deli_counter", "build"))
    r.add_argument("--top", type=int, default=25)
    r.set_defaults(func=cmd_report)
    n = sub.add_parser("new", help="mint a species as a placeholder box")
    n.add_argument("species")
    n.add_argument("--like", default="prop", help="template genome (default prop)")
    n.add_argument("--width", type=float, required=True)
    n.add_argument("--depth", type=float, required=True)
    n.add_argument("--height", type=float, required=True)
    n.add_argument("--min-scale", type=float, default=0.5)
    n.add_argument("--max-scale", type=float, default=2.0)
    n.add_argument("--material", default=None)
    n.add_argument("--keywords", default=None, help="comma-separated placement-name keywords")
    n.add_argument("--theme", default="delco_1997",
                   help="theme whose Pixelcoat profile for the material is checked")
    n.add_argument("--date", default=__import__("datetime").date.today().isoformat())
    n.add_argument("--genome-dir", default=os.path.join(REPO, "zoo_keeper", "genome", "species"))
    n.add_argument("--recipes-dir", default=os.path.join(REPO, "zoo_keeper", "recipes"))
    n.add_argument("--tests-dir", default=os.path.join(REPO, "tests"))
    n.add_argument("--minted", default=os.path.join(REPO, "zoo_keeper", "genome", "minted.json"))
    n.set_defaults(func=cmd_new)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
