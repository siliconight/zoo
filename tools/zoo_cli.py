"""Zoo headless CLI. Two modes:

Dry run (plain Python, anywhere — prints resolved Intent + BuildPlan):
    python tools/zoo_cli.py --prompt "1990s office desk with two drawers" --plan

Full build (inside Blender):
    blender --background --python tools/zoo_cli.py -- ^
        --prompt "1990s office desk with two drawers" --out exhibits

Windows PowerShell:
    & "C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" `
        --background --python tools\\zoo_cli.py -- `
        --prompt "1990s office desk with two drawers" --out exhibits
"""
from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    import bpy  # noqa: F401
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


def parse_args():
    argv = sys.argv
    if "--" in argv:  # blender ... --python this -- <our args>
        argv = argv[argv.index("--") + 1:]
    else:
        argv = argv[1:]
    ap = argparse.ArgumentParser(prog="zoo_cli")
    ap.add_argument("--prompt", help="plain-text asset prompt")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--count", type=int, default=1,
                    help="build N variant siblings (seeds base..base+N-1)")
    ap.add_argument("--habitat",
                    help="build a themed set: a named habitat "
                    "(starter/office/gear) or comma list (desk,chair). "
                    "--prompt is the shared theme, e.g. \"1990s office\".")
    ap.add_argument("--out", default="exhibits",
                    help="output directory (full build only)")
    ap.add_argument("--plan", "--dry-run", action="store_true",
                    dest="plan", help="print Intent + BuildPlan and exit "
                    "(works without Blender)")
    ap.add_argument("--no-collision", action="store_true",
                    help="force collision OFF (overrides the genome default)")
    ap.add_argument("--collision", action="store_true",
                    help="force collision ON (overrides the genome default)")
    ap.add_argument("--lods", action="store_true")
    ap.add_argument("--no-blend", action="store_true",
                    help="skip saving the .blend sidecar")
    ap.add_argument("--species-list", action="store_true")
    # --- ingest: adopt external assets (zip of itch.io assets, etc.) --------
    ap.add_argument("--ingest",
                    help="path to an external asset (.glb/.fbx/.obj/...) or a "
                         ".zip of them to condition into Zoo's standard")
    ap.add_argument("--list", action="store_true",
                    help="with --ingest <zip>: list importable files and exit")
    ap.add_argument("--pick",
                    help="with --ingest <zip>: inner file path to ingest")
    ap.add_argument("--as-name", dest="as_name",
                    help="specimen name for the ingested asset")
    ap.add_argument("--as-species", dest="as_species",
                    help="scale the asset to this species' genome size "
                         "(e.g. --as-species chair)")
    ap.add_argument("--target-height", dest="target_height", type=float,
                    help="scale the asset's overall height to this many meters")
    ap.add_argument("--license", dest="license_note",
                    help="license note recorded in the ingested meta.json")
    # --- exhibit: organize a folder of GLBs into a zoo/museum layout -------
    ap.add_argument("--exhibit",
                    help="folder of built/ingested assets to organize into an "
                         "exhibit (reads their meta.json; writes .exhibit.json)")
    ap.add_argument("--scheme", default="zoo", choices=["zoo", "museum"],
                    help="exhibit layout: zoo (knolled grid) or museum "
                         "(pedestals + labels)")
    ap.add_argument("--cols", type=int,
                    help="columns in the exhibit grid (default ~sqrt(n))")
    ap.add_argument("--exhibit-name", dest="exhibit_name",
                    help="name for the .exhibit.json (default: folder name)")
    # --- kit: plan Zoo modules to theme a Deli Counter greybox --------------
    ap.add_argument("--kit",
                    help="a Deli Counter <name>.slots.json to plan an art/zoo "
                         "module kit for (reads the swap contract; pure)")
    ap.add_argument("--theme", default="delco",
                    help="theme/kit name for module filenames (default: delco)")
    ap.add_argument("--style", type=int, default=1,
                    help="style number for module filenames (default: 1)")
    return ap.parse_args(argv)


def _collision_opt(args):
    """Tri-state: --collision -> True, --no-collision -> False, neither ->
    None (use the genome's per-species default)."""
    if args.collision:
        return True
    if args.no_collision:
        return False
    return None


def habitat_preview(args):
    from zoo_keeper import TOOL_VERSION
    from zoo_keeper.core import genome, habitat, intent, seeding

    species_list = habitat.resolve_species(args.habitat,
                                           genome.list_species())
    hid = habitat.habitat_id(args.prompt or "", species_list, args.seed,
                             TOOL_VERSION)
    members = []
    for sp in species_list:
        prompt = habitat.species_prompt(args.prompt or "", sp)
        it = intent.parse(prompt, seed=args.seed)
        root = seeding.root_key(it.prompt_norm, it.species, args.seed,
                                TOOL_VERSION)
        members.append({"species": sp, "prompt": prompt,
                        "specimen_id": "{}_{}".format(
                            it.species, seeding.short_hash(root))})
    print(json.dumps({"habitat_id": hid, "theme": args.prompt,
                      "species": species_list, "members": members},
                     indent=2, sort_keys=True))
    return 0


def habitat_build(args):
    from zoo_keeper.bpylayer import build

    fam = build.build_habitat(
        args.prompt or "", args.habitat, os.path.abspath(args.out),
        seed=args.seed,
        options={"collision": _collision_opt(args), "lods": args.lods,
                 "save_blend": not args.no_blend, "clear_scene": True})
    print(f"[zoo] habitat:  {fam['habitat_id']} "
          f"({len(fam['species'])} species)")
    print(f"[zoo] out:      {fam['out_dir']}")
    print(f"[zoo] manifest: {fam['manifest_file']}")
    for m in fam["members"]:
        print(f"[zoo]   {m['species']:<11} {m['specimen_id']}: "
              f"{m['status'].upper()}")
    print(f"[zoo] {len(fam['species'])} built, {fam['n_fail']} failed")
    return 0 if fam["n_fail"] == 0 else 2


def dry_run(args):
    from zoo_keeper import TOOL_VERSION
    from zoo_keeper.core import dna, genome, intent, seeding

    it = intent.parse(args.prompt, seed=args.seed)
    out = {"intent": it.to_dict()}
    if it.species:
        g = genome.load_species(it.species)
        root = seeding.root_key(it.prompt_norm, it.species, args.seed,
                                TOOL_VERSION)
        streams = seeding.RNGStreams(root)
        out["plan"] = dna.resolve_plan(it, g, streams, TOOL_VERSION)
        out["specimen_id"] = f"{it.species}_{seeding.short_hash(root)}"
        if args.count > 1:
            from zoo_keeper.core import variants
            seeds = variants.variant_seeds(args.seed, args.count)
            fid = variants.family_id(it.prompt_norm, it.species, args.seed,
                                     args.count, TOOL_VERSION)
            out["family"] = {
                "family_id": fid,
                "count": args.count,
                "shared": {"style": out["plan"]["style"],
                           "material": out["plan"]["material"],
                           "color": out["plan"]["color"]},
                "variants": [
                    {"seed": s, "specimen_id": "{}_{}".format(
                        it.species, seeding.short_hash(
                            seeding.root_key(it.prompt_norm, it.species, s,
                                             TOOL_VERSION)))}
                    for s in seeds],
            }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if it.species else 1


def full_build(args):
    from zoo_keeper.bpylayer import build
    from zoo_keeper.core import validate

    opts = {"collision": _collision_opt(args), "lods": args.lods,
            "save_blend": not args.no_blend, "clear_scene": True}

    if args.count > 1:
        fam = build.build_family(args.prompt, os.path.abspath(args.out),
                                 base_seed=args.seed, count=args.count,
                                 options=opts)
        print(f"[zoo] family:   {fam['family_id']} ({fam['count']} specimens)")
        print(f"[zoo] out:      {fam['out_dir']}")
        print(f"[zoo] shared:   style={fam['shared']['style']} "
              f"material={fam['shared']['material']}")
        print(f"[zoo] manifest: {fam['manifest_file']}")
        for r in fam["results"]:
            print(f"[zoo]   {r['specimen_id']}: "
                  f"{r['report']['status'].upper()}")
        print(f"[zoo] {fam['count']} built, {fam['n_fail']} failed")
        return 0 if fam["n_fail"] == 0 else 2

    result = build.build_specimen(
        args.prompt, os.path.abspath(args.out), seed=args.seed, options=opts)
    print(f"[zoo] specimen: {result['specimen_id']}")
    print(f"[zoo] out:      {result['out_dir']}")
    for kind, fname in result["files"].items():
        print(f"[zoo]   {kind}: {fname}")
    print("[zoo] " + validate.summarize(result["report"]).replace(
        "\n", "\n[zoo] "))
    return 0 if result["report"]["status"] != "fail" else 2


def ingest_run(args):
    import tempfile
    import zipfile
    from zoo_keeper.core import ingest as ing

    src = args.ingest
    is_zip = src.lower().endswith(".zip")

    # inventory mode (pure — works without Blender)
    if is_zip and (args.list or not args.pick):
        entries = ing.scan_archive(src)
        if not entries:
            print("[zoo] no importable meshes found in", src)
            return 1
        print(f"[zoo] {len(entries)} importable file(s) in {src}:")
        for e in entries:
            print(f"  {e['path']}  ({e['ext']}, {e['size']} bytes)")
        if not args.pick:
            print("[zoo] re-run with --pick <path> --out <dir> "
                  "[--as-species X | --target-height M] to ingest one.")
        return 0

    if not HAS_BPY:
        print("[zoo] ingest import/normalize needs Blender. Run inside "
              "Blender (blender --background --python tools/zoo_cli.py -- ...).")
        return 1

    from zoo_keeper import TOOL_VERSION
    from zoo_keeper.bpylayer import ingest as bing
    from zoo_keeper.core import genome

    tmp = None
    if is_zip:
        if not args.pick:
            print("[zoo] --pick <inner path> is required to ingest from a zip.")
            return 1
        tmp = tempfile.mkdtemp(prefix="zoo_ingest_")
        with zipfile.ZipFile(src) as z:
            src_file = z.extract(args.pick, tmp)
    else:
        src_file = src

    target_h = ing.resolve_target_height(
        args.target_height, args.as_species, genome)
    name = args.as_name or ing.safe_name(src_file)
    collision = not args.no_collision

    report = bing.ingest(src_file, args.out, name=name, target_height=target_h,
                         species=args.as_species, collision=collision,
                         license_note=args.license_note,
                         tool_version=TOOL_VERSION)
    print(f"[zoo] ingested: {report['name']}")
    print(f"[zoo]   glb:  {report['glb']}")
    print(f"[zoo]   meta: {report['meta']}")
    print(f"[zoo]   dims (m): {report['dimensions']}")
    if target_h:
        print(f"[zoo]   scaled to height {target_h}m"
              + (f" (from '{args.as_species}' genome)" if args.as_species
                 and not args.target_height else ""))
    else:
        print("[zoo]   no target size given -> assumed already in meters")
    return 0


def exhibit_run(args):
    import os
    from zoo_keeper import TOOL_VERSION
    from zoo_keeper.core import exhibit

    directory = args.exhibit
    if not os.path.isdir(directory):
        print("[zoo] not a folder:", directory)
        return 1
    assets = exhibit.scan_collection(directory)
    if not assets:
        print("[zoo] no assets with meta.json found in", directory)
        return 1
    name = args.exhibit_name or (os.path.basename(os.path.normpath(directory))
                                 + "_" + args.scheme)
    manifest = exhibit.build_exhibit(
        assets, scheme=args.scheme, name=name, tool_version=TOOL_VERSION,
        cols=args.cols, gap=(0.5 if args.no_collision else 0.5))
    out_dir = args.out if args.out != "exhibits" else directory
    path = exhibit.write_exhibit(manifest, out_dir, name=name)
    b = manifest["bounds"]
    print(f"[zoo] exhibit '{name}' ({args.scheme}): "
          f"{manifest['asset_count']} assets")
    print(f"[zoo]   manifest: {path}")
    print(f"[zoo]   footprint: x{b['x']} z{b['z']} (meters)")
    print("[zoo]   import it with the Zoo Importer dock in Godot.")
    return 0


def kit_run(args):
    import json
    import os
    from zoo_keeper.core import kit

    if not os.path.isfile(args.kit):
        print("[zoo] not a file:", args.kit)
        return 1
    manifest = json.load(open(args.kit, encoding="utf-8"))
    plan = kit.plan_kit(manifest, theme=args.theme, style=args.style)
    print(f"[zoo] kit for '{plan['building_id']}' "
          f"(theme={plan['theme']}, style={plan['style']:02d}):")
    print(f"[zoo]   {plan['module_count']} distinct modules dress "
          f"{plan['slot_count']} slots")
    for m in plan["modules"]:
        w, d, h = m["dims"]
        note = ("unit box, scaled per-slot" if m["fit"] == "unit"
                else f"{w}x{d}x{h}m exact")
        print(f"[zoo]   {m['stem']+'.glb':32} x{m['count']:<4} {note}")
    print(f"[zoo] build these into art/zoo/, then Deli Counter's resolver "
          f"swaps them in (theme={args.theme}).")
    if args.out and args.out != "exhibits":
        os.makedirs(args.out, exist_ok=True)
        p = os.path.join(args.out, f"{plan['building_id']}_kit.json")
        json.dump(plan, open(p, "w", encoding="utf-8"), indent=2)
        print("[zoo]   plan written:", p)
    return 0


def main():
    args = parse_args()
    if args.species_list:
        from zoo_keeper.core import genome
        print("\n".join(genome.list_species()))
        return 0
    if args.ingest:
        return ingest_run(args)
    if args.exhibit:
        return exhibit_run(args)
    if args.kit:
        return kit_run(args)
    if not args.prompt:
        print("error: --prompt is required (or use --species-list)")
        return 1
    if args.habitat:
        if args.plan or not HAS_BPY:
            if not args.plan and not HAS_BPY:
                print("[zoo] bpy not available -> habitat preview only.")
            return habitat_preview(args)
        return habitat_build(args)
    if args.plan or not HAS_BPY:
        if not args.plan and not HAS_BPY:
            print("[zoo] bpy not available -> dry run (plan only). "
                  "Run inside Blender for a full build.")
        return dry_run(args)
    return full_build(args)


if __name__ == "__main__":
    sys.exit(main())
