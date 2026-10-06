"""A door box can wear its building's band (1.79.0): one name on both signs.

The walker, 2026-10-06, option A. Level Factory 0.148.0 deals each shell one
business and passes its Pixelcoat pack to the shell's fixtures build; the
door box wears it. The Blender-bound code is read as source, as
`test_car_forms` does.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "zoo_cli_door", os.path.join(HERE, "..", "tools", "zoo_cli.py"))
zoo_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(zoo_cli)


def _src(*parts):
    return open(os.path.join(HERE, "..", *parts), encoding="utf-8").read()


def test_the_cli_takes_a_sign_pack(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["zoo_cli", "--fixtures", "x.lights.json",
                                      "--out", "o", "--sign-pack", "packs/sign_jawns_hoagies"])
    args = zoo_cli.parse_args()
    assert args.sign_pack == "packs/sign_jawns_hoagies"
    assert "\"sign_pack\": (os.path.abspath(args.sign_pack)" in _src("tools", "zoo_cli.py")


def test_only_a_door_box_is_given_the_pack():
    src = _src("zoo_keeper", "bpylayer", "build.py")
    assert 'if species == "sign_box" and opts.get("sign_pack"):' in src


def test_the_door_box_wears_the_given_pack_before_it_would_pick_one():
    src = _src("zoo_keeper", "recipes", "sign_box.py")
    given = src.index('if plan.get("sign_pack"):')
    picked = src.index("skinlib.pick_pack(")
    assert given < picked
    assert "if pack is None and skins_dir:" in src
