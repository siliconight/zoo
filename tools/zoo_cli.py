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
    ap.add_argument("--out", default="exhibits",
                    help="output directory (full build only)")
    ap.add_argument("--plan", "--dry-run", action="store_true",
                    dest="plan", help="print Intent + BuildPlan and exit "
                    "(works without Blender)")
    ap.add_argument("--no-collision", action="store_true")
    ap.add_argument("--lods", action="store_true")
    ap.add_argument("--no-blend", action="store_true",
                    help="skip saving the .blend sidecar")
    ap.add_argument("--species-list", action="store_true")
    return ap.parse_args(argv)


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

    opts = {"collision": not args.no_collision, "lods": args.lods,
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


def main():
    args = parse_args()
    if args.species_list:
        from zoo_keeper.core import genome
        print("\n".join(genome.list_species()))
        return 0
    if not args.prompt:
        print("error: --prompt is required (or use --species-list)")
        return 1
    if args.plan or not HAS_BPY:
        if not args.plan and not HAS_BPY:
            print("[zoo] bpy not available -> dry run (plan only). "
                  "Run inside Blender for a full build.")
        return dry_run(args)
    return full_build(args)


if __name__ == "__main__":
    sys.exit(main())
