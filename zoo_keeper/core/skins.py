"""Pure skin-library resolver: map a material kind + theme to a Pixelcoat
texture pack on disk. No bpy — the bpylayer applies what this resolves.

Why kind-level, not species-level: every Zoo mesh already carries
deterministic world-meter cube-projected UVs (``geometry.cube_project_uv``,
UV = meters * texel). A *tiling* pack therefore lands on every metal part
of every species at uniform physical density with zero per-species work —
one ``metal_delco`` pack skins the vault door, the HVAC cabinet, and the
gutter runs alike. Per-part ``texel`` stays what it always was: a relative
density knob.

Library layout (``--skins`` points at the root):

    skins/
      metal_delco/        metal for the delco theme (theme dir wins)
        metal.pack.json   Pixelcoat >= 0.2 manifest (pixelcoat-pack/1)
        metal_albedo.png  + normal / roughness / emissive as listed
      concrete/           theme-less fallback for any theme
        wall_albedo.png   bare Pixelcoat 0.1 output also works (no manifest)

Resolution order for (kind, theme): ``<kind>_<theme>/`` then ``<kind>/``;
no dir or no albedo inside a bare dir -> None (flat vertex color, the
progressive-art-pass fallback). A *manifest* that names a missing albedo
is a corrupt pack and raises — quiet absence is fine, broken presence is
not.
"""

from __future__ import annotations

import glob
import json
import os

PACK_SCHEMA = "pixelcoat-pack/1"
MAP_KEYS = ("albedo", "normal", "roughness", "emissive", "height")

# Keep in sync with bpylayer.materials.ROUGHNESS (kind vocabulary).
KNOWN_KINDS = ("laminate", "wood", "metal", "plastic", "leather", "rubber",
               "canvas", "carbon", "glass", "paper", "concrete", "plaster")


def find_pack(skins_dir: str, material_kind: str,
              theme: str = "delco") -> dict | None:
    """Resolve a pack for (kind, theme). Returns a pack dict (see
    ``load_pack``) or None when nothing matches."""
    if not skins_dir:
        return None
    for name in (f"{material_kind}_{theme}", material_kind):
        d = os.path.join(skins_dir, name)
        if os.path.isdir(d):
            pack = load_pack(d)
            if pack:
                return pack
    return None


def load_pack(pack_dir: str) -> dict | None:
    """Read one pack directory.

    With a ``*.pack.json`` manifest (Pixelcoat >= 0.2): map paths resolve
    relative to the directory; maps whose files are missing are dropped,
    but a missing *albedo* raises ValueError (corrupt pack). Without a
    manifest: legacy scan for ``*_albedo.png`` (Pixelcoat 0.1 output) and
    sibling ``_normal`` / ``_roughness`` / ``_emissive`` / ``_height``
    files by stem; no albedo -> None.

    Returns ``{"id", "dir", "maps": {key: abs_path}, "meters_per_tile",
    "tileable"}``.
    """
    manifests = sorted(glob.glob(os.path.join(pack_dir, "*.pack.json")))
    if manifests:
        with open(manifests[0], encoding="utf-8") as f:
            raw = json.load(f)
        maps = {}
        for key in MAP_KEYS:
            fname = raw.get("maps", {}).get(key)
            if not fname:
                continue
            path = os.path.join(pack_dir, fname)
            if os.path.isfile(path):
                maps[key] = os.path.abspath(path)
        if "albedo" not in maps:
            raise ValueError(
                f"{manifests[0]}: pack manifest names no existing albedo")
        return {"id": raw.get("asset_id") or os.path.basename(pack_dir),
                "dir": os.path.abspath(pack_dir),
                "maps": maps,
                "meters_per_tile": float(raw.get("meters_per_tile") or 1.0),
                "tileable": raw.get("tileable")}

    albedos = sorted(glob.glob(os.path.join(pack_dir, "*_albedo.png")))
    if not albedos:
        return None
    stem = os.path.basename(albedos[0])[:-len("_albedo.png")]
    maps = {"albedo": os.path.abspath(albedos[0])}
    for key in MAP_KEYS[1:]:
        path = os.path.join(pack_dir, f"{stem}_{key}.png")
        if os.path.isfile(path):
            maps[key] = os.path.abspath(path)
    return {"id": stem, "dir": os.path.abspath(pack_dir), "maps": maps,
            "meters_per_tile": 1.0, "tileable": None}


def library_report(skins_dir: str, theme: str = "delco",
                   kinds: tuple[str, ...] = KNOWN_KINDS) -> dict:
    """Which kinds resolve to which packs — the pure dry-run view of a
    skins folder (``zoo_cli --skins DIR`` without Blender prints this)."""
    resolved = {}
    for kind in kinds:
        pack = find_pack(skins_dir, kind, theme)
        resolved[kind] = None if pack is None else {
            "pack": pack["id"], "dir": pack["dir"],
            "maps": sorted(pack["maps"]),
            "meters_per_tile": pack["meters_per_tile"]}
    return {"skins_dir": os.path.abspath(skins_dir), "theme": theme,
            "resolved": {k: v for k, v in resolved.items() if v},
            "flat_fallback": sorted(k for k, v in resolved.items() if not v)}


# ------------------------------------------------------------- sign packs
# Sign faces want VARIETY (three storefronts, three different signs), which
# kind-level resolution can't express. Convention: a ``signs_<theme>/`` (or
# theme-less ``signs/``) directory whose SUBDIRS are each one Pixelcoat pack
# (Pixelcoat's own per-asset output layout — point it straight at the build
# --output). Selection is deterministic per anchor id, so the pawn shop gets
# the same sign on every rebuild.

def find_sign_packs(skins_dir: str, theme: str = "delco") -> list[dict]:
    """All sign packs for a theme, sorted by pack id. Empty list when the
    library has none — callers fall back to the flat emissive face."""
    if not skins_dir:
        return []
    for name in (f"signs_{theme}", "signs"):
        root = os.path.join(skins_dir, name)
        if not os.path.isdir(root):
            continue
        packs = []
        for sub in sorted(os.listdir(root)):
            d = os.path.join(root, sub)
            if os.path.isdir(d):
                pack = load_pack(d)
                if pack:
                    packs.append(pack)
        if packs:
            return sorted(packs, key=lambda p: p["id"])
    return []


def pick_pack(packs: list[dict], key: str) -> dict | None:
    """Stable pick: same key (anchor id), same pack, forever."""
    if not packs:
        return None
    import zlib
    return packs[zlib.crc32(key.encode("utf-8")) % len(packs)]
