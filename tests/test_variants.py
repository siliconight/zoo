from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import dna, genome, intent, seeding, variants


def _plan(prompt, seed):
    it = intent.parse(prompt, seed=seed)
    g = genome.load_species(it.species)
    root = seeding.root_key(it.prompt_norm, it.species, seed, TOOL_VERSION)
    plan = dna.resolve_plan(it, g, seeding.RNGStreams(root), TOOL_VERSION)
    sid = f"{it.species}_{seeding.short_hash(root)}"
    return it, plan, sid


def test_variant_seed_block():
    assert variants.variant_seeds(0, 5) == [0, 1, 2, 3, 4]
    assert variants.variant_seeds(100, 3) == [100, 101, 102]


def test_count_must_be_positive():
    try:
        variants.variant_seeds(0, 0)
    except ValueError:
        return
    raise AssertionError("count 0 should raise")


def test_family_id_deterministic():
    a = variants.family_id("1990s office chair", "chair", 0, 30, TOOL_VERSION)
    b = variants.family_id("1990s office chair", "chair", 0, 30, TOOL_VERSION)
    assert a == b and a.startswith("chair_family_")
    # different count or base -> different family
    assert a != variants.family_id("1990s office chair", "chair", 0, 20,
                                   TOOL_VERSION)
    assert a != variants.family_id("1990s office chair", "chair", 1, 30,
                                   TOOL_VERSION)


def test_family_shares_look_varies_proportions():
    prompt = "1990s office chair"
    seeds = variants.variant_seeds(0, 6)
    plans = [_plan(prompt, s) for s in seeds]
    styles = {p[1]["style"] for p in plans}
    mats = {p[1]["material"] for p in plans}
    colors = {tuple(p[1]["color"]) for p in plans}
    ids = {p[2] for p in plans}
    dims = {tuple(sorted(p[1]["dimensions"].items())) for p in plans}
    # cohesive: one style, one material, one palette
    assert len(styles) == 1 and len(mats) == 1 and len(colors) == 1
    # distinct: every sibling is its own specimen with its own proportions
    assert len(ids) == 6
    assert len(dims) > 1


def test_family_manifest_shape_and_determinism():
    shared = {"style": "1990s", "material": "metal", "color": [0.5, 0.5, 0.5]}
    specimens = [{"seed": 0, "specimen_id": "chair_aaaaaa",
                  "dimensions": {"width": 0.45}, "status": "pass",
                  "files": {"glb": "chair_aaaaaa.glb"}}]
    fid = variants.family_id("1990s office chair", "chair", 0, 1, TOOL_VERSION)
    m1 = variants.build_family_manifest(TOOL_VERSION, fid, "1990s office chair",
                                        "chair", 0, 1, shared, specimens)
    m2 = variants.build_family_manifest(TOOL_VERSION, fid, "1990s office chair",
                                        "chair", 0, 1, shared, specimens)
    assert m1 == m2
    assert m1["zoo"]["family_id"] == fid
    assert m1["count"] == 1 and m1["species"] == "chair"
    assert m1["shared"]["style"] == "1990s"
