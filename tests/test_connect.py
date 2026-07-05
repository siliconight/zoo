import math

from zoo_keeper.core import connect


def test_compatibility_exact_and_aliases():
    assert connect.compatible("head", "head")
    assert connect.compatible("hand_r", "grip")      # grip fits either hand
    assert connect.compatible("surface", "cup")      # cup rests on a surface
    assert connect.compatible("floor", "surface")
    assert not connect.compatible("head", "feet")
    assert not connect.compatible("wall", "grip")


def test_snap_coincide_at_origin():
    socket = {"pos": [2.0, 1.0, 3.0], "yaw": 90.0}
    anchor = {"pos": [0.0, 0.0, 0.0], "yaw": 0.0}
    pose = connect.snap_pose(socket, anchor)
    assert pose["pos"] == [2.0, 1.0, 3.0]
    assert pose["yaw"] == 90.0


def test_snap_offsets_the_anchor():
    # anchor sits 0.5 in front of the prop origin; snapping to origin socket
    # must pull the prop back 0.5 so the anchor lands on the socket
    socket = {"pos": [0.0, 0.0, 0.0], "yaw": 0.0}
    anchor = {"pos": [0.0, 0.0, 0.5], "yaw": 0.0}
    pose = connect.snap_pose(socket, anchor)
    assert pose["pos"][2] == -0.5


def test_snap_butt_flips_for_modules():
    socket = {"pos": [0.0, 0.0, 0.0], "yaw": 0.0}
    anchor = {"pos": [0.0, 0.0, 0.0], "yaw": 0.0}
    pose = connect.snap_pose(socket, anchor, mate="butt")
    assert pose["yaw"] == 180.0


def test_build_connectors_from_genome_and_positions():
    genome = {"connectors": {"anchor": {"type": "head"},
                             "sockets": {"ATT_top": "surface"}}}
    conn = connect.build_connectors(
        genome, {"ATT_top": (0.0, 0.0, 0.9), "ATT_side": (0.2, 0.0, 0.0)})
    assert conn["anchor"]["type"] == "head"
    types = {s["name"]: s["type"] for s in conn["sockets"]}
    assert types["ATT_top"] == "surface"
    assert types["ATT_side"] == "surface"          # undeclared -> default
    assert conn["sockets"][0]["name"] == "ATT_side"  # sorted


def test_build_connectors_defaults_when_undeclared():
    conn = connect.build_connectors({}, {})
    assert conn["anchor"]["type"] == connect.DEFAULT_ANCHOR_TYPE
    assert conn["sockets"] == []


def test_find_matches():
    host = {"sockets": [{"name": "ATT_head", "type": "head"},
                        {"name": "ATT_hand_r", "type": "hand_r"}]}
    helmet = {"anchor": {"type": "head"}}
    briefcase = {"anchor": {"type": "grip"}}
    assert [s["name"] for s in connect.find_matches(host, helmet)] == ["ATT_head"]
    assert [s["name"] for s in connect.find_matches(host, briefcase)] == \
        ["ATT_hand_r"]


def test_genomes_declare_valid_connector_types():
    from zoo_keeper.core import genome
    valid = (connect.CHARACTER_TYPES | connect.WORLD_TYPES
             | connect.PROP_TYPES | {"grip"})
    for sp in genome.list_species():
        conn = genome.load_species(sp).get("connectors")
        if not conn:
            continue
        atype = conn.get("anchor", {}).get("type")
        if atype:
            assert atype in valid, f"{sp} anchor type {atype}"
        for stype in (conn.get("sockets", {}) or {}).values():
            assert stype in valid, f"{sp} socket type {stype}"
