import os
import tempfile
import zipfile

from zoo_keeper.core import genome, ingest


def _make_zip(path, names):
    with zipfile.ZipFile(path, "w") as z:
        for n in names:
            z.writestr(n, b"x")  # content irrelevant for scanning


def test_scan_archive_filters_and_sorts():
    d = tempfile.mkdtemp()
    zp = os.path.join(d, "pack.zip")
    _make_zip(zp, ["models/chair.fbx", "models/table.obj", "readme.txt",
                   "textures/wood.png", "props/lamp.glb", "sub/"])
    found = ingest.scan_archive(zp)
    paths = [e["path"] for e in found]
    assert paths == ["models/chair.fbx", "models/table.obj", "props/lamp.glb"]
    assert all(e["ext"] in ingest.SUPPORTED_EXTS for e in found)


def test_resolve_target_height_explicit_wins():
    assert ingest.resolve_target_height(1.25, "chair", genome) == 1.25


def test_resolve_target_height_from_species_genome():
    h = ingest.resolve_target_height(None, "chair", genome)
    assert h == genome.load_species("chair")["dimensions"]["height"]["default"]


def test_resolve_target_height_none_when_unknown():
    assert ingest.resolve_target_height(None, None, genome) is None


def test_ingest_meta_shape_and_provenance():
    m = ingest.ingest_meta("old_lamp", "/tmp/packs/Lamp Final.fbx", "0.10.0",
                           dimensions={"width": 0.3, "depth": 0.3,
                                       "height": 1.4}, species="lamp")
    assert m["source"] == "ingested"
    assert m["origin_file"] == "Lamp Final.fbx"      # basename only
    assert m["species_hint"] == "lamp"
    assert m["tool_version"] == "0.10.0"
    assert "user must confirm rights" in m["license"]


def test_safe_name():
    assert ingest.safe_name("/a/b/Cool Prop v2.FBX") == "cool_prop_v2"
    assert ingest.safe_name("weird!!name.obj") == "weird__name"
