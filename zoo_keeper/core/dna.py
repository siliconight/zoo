"""DNA: resolve an Intent against a Genome into a concrete BuildPlan.

Pure Python and fully deterministic — geometry recipes (bpy layer) consume
the BuildPlan and never make random decisions of their own. Every sampled
value comes from a named RNG stream.
"""
from __future__ import annotations

from . import seeding

# Boot construction constants — single source of truth. The DNA hook writes
# the resolved values into the plan; the recipe executes them verbatim so the
# built height and the plan's recorded height can never disagree.
BOOT_SHAFT_H = {"ankle": 0.14, "mid": 0.22, "tall": 0.38}
BOOT_SOLE_T = 0.025
BOOT_FOOT_H = 0.07
BOOT_GAP_FACTOR = 0.65  # each boot sits at x = ±(width * this)


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _pick_style(genome: dict, intent) -> tuple[str, dict]:
    """Choose a style block: exact era match > style tag match > default."""
    styles = genome["styles"]
    if intent.era and intent.era in styles:
        return intent.era, styles[intent.era]
    for tag in intent.style_tags:
        if tag in styles:
            return tag, styles[tag]
    if "default" in styles:
        return "default", styles["default"]
    name = sorted(styles)[0]
    return name, styles[name]


def _resolve_dimensions(genome: dict, intent, streams) -> dict:
    """default * size_hint, +/-2% deterministic jitter, clamped to range."""
    rng = streams.stream("dims")
    dims = {}
    for name in sorted(genome["dimensions"]):
        spec = genome["dimensions"][name]
        base = spec["default"] * intent.size_hint
        jitter = 1.0 + rng.uniform(-0.02, 0.02)
        dims[name] = round(_clamp(base * jitter, spec["min"], spec["max"]), 4)
    return dims


def _resolve_params(genome: dict, intent, streams) -> dict:
    params = {}
    for name in sorted(genome["params"]):
        spec = genome["params"][name]
        if isinstance(spec, dict) and "min" in spec:
            want = intent.counts.get(name, spec["default"])
            params[name] = int(_clamp(want, spec["min"], spec["max"]))
        elif isinstance(spec, list):
            params[name] = spec[0]  # first option = canonical default
        else:
            params[name] = spec
    return params


def resolve_plan(intent, genome: dict, streams: seeding.RNGStreams,
                 tool_version: str) -> dict:
    """Produce the BuildPlan the recipe layer executes verbatim."""
    style_name, style = _pick_style(genome, intent)

    material = (intent.material
                or style.get("material")
                or genome["materials"]["default"])
    if material not in genome["materials"]["options"]:
        material = genome["materials"]["default"]

    color = (list(intent.color) if intent.color
             else list(style.get("color", [0.6, 0.6, 0.6])))
    wear = intent.wear if intent.wear is not None else style.get("wear", 0.15)

    plan = {
        "species": genome["species"],
        "genome_version": genome["version"],
        "tool_version": tool_version,
        "style": style_name,
        "style_block": dict(style),
        "material": material,
        "color": [round(c, 4) for c in color],
        "wear": round(float(wear), 3),
        "dimensions": _resolve_dimensions(genome, intent, streams),
        "params": _resolve_params(genome, intent, streams),
        "parts": list(genome["parts"]),
        "budgets": dict(genome["budgets"]),
        "attachments": list(genome.get("attachments", [])),
        "bevel": style.get("bevel", 0.004),
        # per-axis multiplier applied to genome dimension ranges at validation
        # time — lets a multi-unit specimen (e.g. a boot pair) keep an honest
        # single-unit genome while still validating its true footprint.
        "dim_scale": {"width": 1.0, "depth": 1.0, "height": 1.0},
    }

    # per-species touch-ups driven by intent
    extra = _SPECIES_EXTRAS.get(genome["species"])
    if extra:
        extra(plan, intent)
    return plan


# --- per-species intent hooks ----------------------------------------------

def _desk(plan, intent):
    if "executive" in intent.style_tags:
        plan["params"]["leg_style"] = "panel"


def _chair(plan, intent):
    text = intent.prompt_norm
    if "office" in intent.style_tags or "gaming" in intent.style_tags:
        plan["params"]["has_arms"] = 1
    if "armchair" in text or "arm chair" in text or " arms" in text:
        plan["params"]["has_arms"] = 1


def _helmet(plan, intent):
    text = intent.prompt_norm
    brim_words = ("construction", "hard hat", "hardhat", "police", "bobby",
                  "peaked", "cap", "brim", "trooper", "ranger")
    if any(w in text for w in brim_words) \
            or "construction" in intent.style_tags:
        plan["params"]["brim"] = 1
    if "visor" in text or "motorcycle" in intent.style_tags:
        plan["params"]["visor"] = 1


def _boots(plan, intent):
    if "combat" in intent.style_tags or "military" in intent.style_tags:
        plan["params"]["shaft_style"] = "tall"
    elif "hiking" in intent.style_tags or "work" in intent.style_tags:
        plan["params"]["shaft_style"] = "mid"

    p = plan["params"]
    shaft_h = BOOT_SHAFT_H.get(p["shaft_style"], BOOT_SHAFT_H["ankle"])
    # publish construction values so the recipe executes the plan verbatim
    p["shaft_h"] = shaft_h
    p["sole_t"] = BOOT_SOLE_T
    p["foot_h"] = BOOT_FOOT_H
    p["gap_factor"] = BOOT_GAP_FACTOR
    # the recipe builds height from these, not from the genome dimension, so
    # write the true value back for an honest meta.json
    plan["dimensions"]["height"] = round(BOOT_SOLE_T + BOOT_FOOT_H + shaft_h, 4)
    # a mirrored pair spans (2*gap + 1) boot-widths along X
    if p.get("pair", 2) == 2:
        plan["dim_scale"]["width"] = round(2 * BOOT_GAP_FACTOR + 1, 4)


def _simple_car(plan, intent):
    text = intent.prompt_norm
    if "hatchback" in text:
        plan["params"]["body_style"] = "hatchback"
    elif "coupe" in text:
        plan["params"]["body_style"] = "coupe"


CASH_STRAP_H = 0.011  # thickness of one banded bill strap


def _cash_stack(plan, intent):
    n = int(plan["params"].get("stacks", 1))
    plan["params"]["strap_h"] = CASH_STRAP_H
    # the recipe builds height from strap count; keep meta.json honest
    plan["dimensions"]["height"] = round(n * CASH_STRAP_H, 4)


_SPECIES_EXTRAS = {
    "desk": _desk,
    "chair": _chair,
    "helmet": _helmet,
    "boots": _boots,
    "simple_car": _simple_car,
    "cash_stack": _cash_stack,
}
