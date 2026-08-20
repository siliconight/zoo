# Build, render and MEASURE the species that could stand in for a gameplay
# solid outdoors -- a car, a dumpster-sized box, a vending machine, an HVAC
# unit, a water tank, a sign box, a streetlight.
#
# The sibling of preview_dressing.ps1, and it asks one extra question that one
# does not need to. Surface dressing is collisionless by definition. These are
# the opposite: they exist BECAUSE of the volume they occupy, so the script
# reads the collision back out of every built GLB and prints it beside the
# shape metrics. A stand-in whose collider does not match its art is the whole
# defect this family of work is about.
#
# SPECIES ARE NAMED OUTRIGHT, not prompted. `core.intent.parse` says why: a
# prompt that resolves today does so because no better keyword match exists
# yet, which is a coincidence and not a contract, and two species in the
# library could never be reached by prompt at all. The prompt still rides along
# for material, colour and wear.
#
# Usage:  pwsh -ExecutionPolicy Bypass -File preview_street_solids.ps1

$Blender = "C:\blender\blender.exe"
$Zoo     = "C:\Projects\gabagool_studios\gabagool_factory\zoo"
$Factory = "C:\Projects\gabagool_studios\gabagool_factory"

if (-not (Test-Path $Blender)) {
  $found = Get-ChildItem -Path "C:\blender" -Filter "blender.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { $Blender = $found.FullName }
  else { Write-Error "blender.exe not found under C:\blender - set `$Blender at the top."; exit 1 }
}

# Pixelcoat texture packs, if a pack has been generated. Same convention as
# preview_floor_ceiling.ps1: use them when present, say so when not, and
# render flat colour rather than failing. Without a pack you are judging
# silhouette and shading only, which is worth knowing before you judge.
$Skins = Join-Path $Zoo "_skins"
$SkinArgs = @()
if (Test-Path $Skins) {
  $SkinArgs = @("--skins", $Skins, "--theme", "delco")
  Write-Host "Skins:   $Skins"
} else {
  Write-Host "Skins:   none at $Skins -- flat style colour + baked vertex wear"
}

$Out  = Join-Path $Zoo "_preview_street"
$Tool = Join-Path $Zoo "tools\preview_specimen.py"
New-Item -ItemType Directory -Force -Path $Out | Out-Null
Write-Host "Blender: $Blender"
Write-Host "Out:     $Out"

# species is the contract; prompt only styles it.
$jobs = @(
  @{ species = "simple_car";      prompt = "weathered sedan";              name = "car" },
  @{ species = "prop";            prompt = "rusted steel container";       name = "solid" },
  @{ species = "hvac_unit";       prompt = "rooftop hvac unit";            name = "hvac" },
  @{ species = "water_tank";      prompt = "galvanised water tank";        name = "tank" },
  @{ species = "vending_machine"; prompt = "street vending machine";       name = "vending" },
  @{ species = "sign_box";        prompt = "shopfront sign box";           name = "sign" },
  @{ species = "streetlight";     prompt = "concrete streetlight";         name = "streetlight" }
)

foreach ($j in $jobs) {
  Write-Host "`n=== Building: $($j.species) ==="
  & $Blender --background --python $Tool -- `
      --species $j.species --prompt $j.prompt --seed 1999 --out $Out `
      --render (Join-Path $Out ($j.name + "_specimen.png")) `
      @SkinArgs
  if ($LASTEXITCODE -ne 0) { Write-Host "  (build reported exit $LASTEXITCODE)" }
}

Write-Host "`n=== SHAPE METRICS FROM THE BUILT GLBs ==="
Write-Host "(glTF space is Y-UP; shape_metrics defaults to up=1 for that reason)"
$env:PYTHONIOENCODING = "utf-8"
python (Join-Path $Factory "tools\shape_metrics.py") --dir $Out

# --- what collision does each one actually bring? --------------------------
# Read with level_factory's glb_collision, which walks the container and the
# node tree and needs neither Blender nor Godot. A `-colonly` sibling mesh is
# how Zoo ships collision (bpylayer/collision.py), so this is reading Zoo's own
# output through an independent implementation rather than trusting the build.
$Probe = Join-Path $Out "_collision_probe.py"
@'
import glob, os, sys
sys.path.insert(0, sys.argv[1])
from packages.validation.glb_collision import collision_solids

print(f"{'file':<34} {'read':>5} {'solids':>7}   collider extents (m)")
print("-" * 92)
for p in sorted(glob.glob(os.path.join(sys.argv[2], "**", "*.glb"), recursive=True)):
    r = collision_solids(p)
    name = os.path.basename(p)
    if not r.read:
        print(f"{name:<34} {'NO':>5} {'-':>7}   {r.detail}")
        continue
    if not r.solids:
        print(f"{name:<34} {'yes':>5} {0:>7}   none -- this asset brings no collision")
        continue
    parts = "  ".join(f"{s.size[0]:.2f}x{s.size[1]:.2f}x{s.size[2]:.2f}"
                      for s in r.solids)
    print(f"{name:<34} {'yes':>5} {len(r.solids):>7}   {parts}")
'@ | Set-Content -Encoding utf8 $Probe

Write-Host "`n=== COLLISION EACH GLB BRINGS (read back, not assumed) ==="
python $Probe (Join-Path $Factory "level_factory") $Out

Write-Host "`nPNGs:"
Get-ChildItem $Out -Filter *.png -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $($_.FullName)" }
