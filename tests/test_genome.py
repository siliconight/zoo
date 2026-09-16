import pytest

from zoo_keeper.core import genome


PROP_SPECIES = {"desk", "chair", "helmet", "boots", "simple_car",
                "filing_cabinet", "table", "crt_tv", "atm",
                "vending_machine", "briefcase", "cash_stack",
                "soda_cup", "cheesesteak", "flat_top_grill",
                "condiment_bottle", "french_fries",
                "gold_bar", "drop_safe", "queue_stanchion",
                "security_camera",
                "hvac_unit", "water_tank", "vent_stack", "exhaust_fan",
                "skylight", "satellite_dish",
                "fluorescent_fixture", "streetlight", "sign_box", "wall_pack",
                # the below-grade bare bulb (DC >= 0.98 `pendant` anchors --
                # basements and objective rooms; roadmap 57's 90s palette)
                "pendant_fixture",
                # the club set's own hardware (0.94.0): the can a wash
                # comes out of and the par can a stage light does
                "club_fixture",
                # the interior species (0.84.0): what a generated room was
                # missing besides tables and chairs
                "carton_stack", "furnace", "dust_sheet", "pool_table",
                "booth_seat",
                # the club species (0.87.0): a 1997 Delco strip club's
                # stage, tables, tub chairs, stools and its neon
                "club_stage", "cocktail_table", "club_chair", "bar_stool",
                "neon_sign",
                # the club's games and its vice (0.91.0): the chalk-score
                # dartboard cabinet and the pull-knob cigarette machine
                "dartboard", "cigarette_machine",
                # the club's bar (0.92.0): the lit wall unit behind it
                "back_bar",
                # the card shop (0.95.0): the showcase counter, the gondola
                # bay of booster displays, the felt pennants along the wall
                # top, and the play area's table and chair
                "display_case", "pack_wall", "pennant_row",
                "folding_table", "folding_chair",
                # the flat art (0.98.0): the cheap half of "the card shop is
                # not dense enough" -- the poster on the wall above the
                # shelving, the printed banner, the painted board on a drop
                # chain, and the hand-lettered sign over an aisle. Two
                # triangles and a texture apiece; the cost is the atlas.
                "poster", "hanging_banner", "ceiling_hanger", "aisle_sign"}

# architectural modules — Deli Counter art/zoo wall-slot dressing
ARCH_SPECIES = {"wall", "wallEnd", "doorway", "window", "breach", "vault_door",
                # the broken STATE of a window slot (INTERACTIVES.md
                # state_geometry), as breach is to a breachable wall
                "window_broken",
                "teller_line", "safe_deposit_boxes", "dress_cover", "roof",
                # Phase 1 structural set (vertical-slice visual gate)
                "wallCorner", "stair_rail", "ladder", "shelving", "counter",
                # surface modules (floor/ceiling slab dressing)
                "floor", "ceiling",
                # volume module: a DC `role: "prop"` slot -- the vault, the
                # teller counter, a desk, a crate stack. It belongs HERE and
                # not in PROP_SPECIES above despite the name, and the collision
                # is worth stating: PROP_SPECIES are individually-modelled
                # objects with their own silhouettes, while this is the
                # exact-dims box Deli Counter authored, skinned by the theme.
                # The species name is forced -- `kit.slot_typename` returns the
                # slot's role verbatim, so a `prop` slot needs a `prop` species.
                "prop"}


# Layer 3 surface dressing -- collisionless micro detail scattered over an
# assembled site (docs/SURFACE_DRESSING.md). A third category on purpose:
# these are neither individually-modelled props with their own silhouettes nor
# Deli Counter slot-driven modules. Nothing places them by slot and nothing
# places them by name; they are scattered, and the scatter is the unit.
DRESSING_SPECIES = {"pebble", "rubble_frag", "weed_tuft", "litter_scrap",
                    # cosmetic glass debris (one object per shard, so the
                    # game can fling the pieces of a broken pane)
                    "glass_shard"}


def _minted():
    """Species minted by tools/new_species.py (roadmap 150) -- registered in
    genome/minted.json so a new person can add one without editing this
    file, and listed there so the hand-authored set above stays the audit
    of what somebody actually shaped."""
    import json
    import os
    p = os.path.join(os.path.dirname(genome.genome_dir()), "minted.json")
    if not os.path.exists(p):
        return set()
    with open(p, encoding="utf-8") as f:
        return set(json.load(f))


def test_all_species_load_and_validate():
    species = genome.list_species()
    assert set(species) == PROP_SPECIES | ARCH_SPECIES | DRESSING_SPECIES | _minted()
    for s in species:
        g = genome.load_species(s)
        assert genome.validate_genome(g) == []
        assert g["license"]["construction_knowledge"] == "CC0"


def test_unknown_species_helpful_error():
    with pytest.raises(FileNotFoundError) as e:
        genome.load_species("gazebo")
    assert "desk" in str(e.value)
