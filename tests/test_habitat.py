from zoo_keeper import TOOL_VERSION
from zoo_keeper.core import genome, habitat, intent


KNOWN = genome.list_species()


def test_named_habitats_resolve():
    assert habitat.resolve_species("office", KNOWN) == ["desk", "chair"]
    assert habitat.resolve_species("gear", KNOWN) == ["helmet", "boots"]
    assert len(habitat.resolve_species("starter", KNOWN)) == 5


def test_comma_list_resolves():
    assert habitat.resolve_species("desk,chair", KNOWN) == ["desk", "chair"]


def test_unknown_species_raises():
    try:
        habitat.resolve_species("desk,gazebo", KNOWN)
    except ValueError:
        return
    raise AssertionError("unknown species should raise")


def test_species_prompt_prepends_theme():
    assert habitat.species_prompt("1990s office", "desk") == "1990s office desk"
    # underscore species becomes a natural noun
    assert habitat.species_prompt("rusty", "simple_car") == "rusty simple car"
    assert habitat.species_prompt("", "chair") == "chair"


def test_themed_prompt_parses_back_to_species_and_shared_era():
    theme = "1990s office"
    members = [(sp, intent.parse(habitat.species_prompt(theme, sp)))
               for sp in habitat.resolve_species("office", KNOWN)]
    # every member resolves to the intended species and carries the era
    assert [sp for sp, _ in members] == [it.species for _, it in members]
    assert all(it.era == "1990s" for _, it in members)


def test_habitat_id_deterministic():
    sp = habitat.resolve_species("office", KNOWN)
    a = habitat.habitat_id("1990s office", sp, 0, TOOL_VERSION)
    b = habitat.habitat_id("1990s office", sp, 0, TOOL_VERSION)
    assert a == b and a.startswith("habitat_")
    assert a != habitat.habitat_id("1990s office", sp, 1, TOOL_VERSION)
    assert a != habitat.habitat_id("1980s office", sp, 0, TOOL_VERSION)


def test_habitat_manifest_shape():
    members = [{"species": "desk", "specimen_id": "desk_aaaaaa",
                "status": "pass", "files": {"glb": "desk_aaaaaa.glb"}}]
    m = habitat.build_habitat_manifest(TOOL_VERSION, "habitat_xxxxxx",
                                       "1990s office", ["desk"], 0, members)
    assert m["zoo"]["habitat_id"] == "habitat_xxxxxx"
    assert m["theme"] == "1990s office"
    assert m["species"] == ["desk"]
    assert m["members"][0]["species"] == "desk"
