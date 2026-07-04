from zoo_keeper.core import intent


def test_acceptance_prompt():
    it = intent.parse("1990s office desk with two drawers")
    assert it.species == "desk"
    assert it.era == "1990s"
    assert "office" in it.style_tags
    assert it.counts.get("drawers") == 2
    assert "species" not in it.unresolved


def test_number_words_and_digits():
    assert intent.parse("desk with three drawers").counts["drawers"] == 3
    assert intent.parse("desk with 4 drawers").counts["drawers"] == 4


def test_boots_material_wear():
    it = intent.parse("worn leather combat boots")
    assert it.species == "boots"
    assert it.material == "leather"
    assert it.wear >= 0.5
    assert "combat" in it.style_tags


def test_car_color_size_era():
    it = intent.parse("small red 1970s car")
    assert it.species == "simple_car"
    assert it.color_name == "red"
    assert it.size_hint < 1.0
    assert it.era == "1970s"


def test_material_alias():
    assert intent.parse("wooden chair").material == "wood"
    assert intent.parse("steel helmet").material == "metal"


def test_unknown_species_flagged():
    it = intent.parse("a lovely gazebo")
    assert it.species is None
    assert "species" in it.unresolved


def test_hard_hat_is_helmet():
    assert intent.parse("yellow hard hat").species == "helmet"
