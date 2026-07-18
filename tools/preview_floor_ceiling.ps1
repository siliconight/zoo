# Preview the new Zoo floor/ceiling species headlessly (flat colour, no skins).
# Builds three specimens and renders a PNG for each. Send the PNGs (or the
# console output) back to verify the species build correctly.
#
# Usage (from anywhere):  powershell -ExecutionPolicy Bypass -File preview_floor_ceiling.ps1

# --- edit these two paths if needed ---
$Blender = "C:\blender\blender.exe"
$Zoo     = "C:\Projects\gabagool_studios\gabagool_factory\zoo"
# --------------------------------------

if (-not (Test-Path $Blender)) {
  $found = Get-ChildItem -Path "C:\blender" -Filter "blender.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { $Blender = $found.FullName }
  else { Write-Error "blender.exe not found under C:\blender - set `$Blender manually at the top of this script."; exit 1 }
}

$Out = Join-Path $Zoo "_preview"
$Skins = Join-Path $Zoo "_skins"          # Pixelcoat texture packs (<kind>_delco\)
$Tool = Join-Path $Zoo "tools\preview_specimen.py"
Write-Host "Blender: $Blender"
Write-Host "Zoo:     $Zoo"
New-Item -ItemType Directory -Force -Path $Out | Out-Null

$jobs = @(
  @{ prompt = "carpet floor";          png = "floor_carpet.png" },
  @{ prompt = "tiled floor";           png = "floor_tile.png" },
  @{ prompt = "acoustic ceiling tile"; png = "ceiling_acoustic.png" }
)

$SkinArgs = @()
if (Test-Path $Skins) { $SkinArgs = @("--skins", $Skins, "--theme", "delco"); Write-Host "Skins:   $Skins" }
else { Write-Host "Skins:   (none found at $Skins - rendering flat colour)" }

foreach ($j in $jobs) {
  Write-Host "`n=== Building: $($j.prompt) ==="
  & $Blender --background --python $Tool -- `
      --prompt $j.prompt --seed 1999 --out $Out --render (Join-Path $Out $j.png) `
      @SkinArgs
}

Write-Host "`nDone. PNGs in $Out :"
Get-ChildItem $Out -Filter *.png -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $($_.FullName)" }
