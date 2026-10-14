"""A door box under its building's band says the trade (1.112.0); from 1.79.0 to 1.111.0 it wore the band.

The walker, 2026-10-06, option A: one name on both signs. Level Factory 0.148.0 deals each shell one business and
passes its Pixelcoat pack to the shell's fixtures build, and 1.79.0 dressed the door box in it. The walker, walking
cold run 9305's pharmacy, 2026-10-14: "double sign here looks...redundant", and chose the trade for the door. The
pack still arrives -- it is how the door knows a band names the shop -- and the door paints its trade. The
Blender-bound code is read as source, as `test_car_forms` does.
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


def test_a_door_box_given_the_band_s_pack_paints_its_trade():
    """FAILS ON 1.111.0: the door wore the pack, so it said the band's name again."""
    src = _src("zoo_keeper", "recipes", "sign_box.py")
    assert 'banded = bool(plan.get("sign_pack"))' in src
    assert "if not banded and skins_dir:" in src
    assert "(SN.trade_for if banded else SN.sign_for)(" in src
    assert "skinlib.load_pack(" not in src
