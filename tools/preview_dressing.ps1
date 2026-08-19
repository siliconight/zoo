# Preview the four Layer 3 surface-dressing species headlessly.
#
# For each species: build + render a scale-true specimen shot, build + render a
# PATCH shot (many instances at standing eye height, which is the unit a
# scatter species is actually judged in), then MEASURE the built GLB with
# tools/shape_metrics.py.
#
# WHY MEASURE AND NOT JUST LOOK. The first pass of this kit was reviewed from
# renders alone, and renders alone could not show that a rubble fragment needed
# only 7 distinct facing directions to cover 80% of its surface (it was still a
# box), that nothing in the kit touched the ground (base_contact_ratio 0.001),
# or that the pebble was 334 triangles against a 260 budget. Every one of those
# is one number. Send back the PNGs AND the table.
#
# Usage:  pwsh -ExecutionPolicy Bypass -File preview_dressing.ps1

$Blender = "C:\blender\blender.exe"
$Zoo     = "C:\Projects\gabagool_studios\gabagool_factory\zoo"
$Factory = "C:\Projects\gabagool_studios\gabagool_factory"

if (-not (Test-Path $Blender)) {
  $found = Get-ChildItem -Path "C:\blender" -Filter "blender.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { $Blender = $found.FullName }
  else { Write-Error "blender.exe not found under C:\blender - set `$Blender at the top."; exit 1 }
}

$Out  = Join-Path $Zoo "_preview_dressing"
$Tool = Join-Path $Zoo "tools\preview_specimen.py"
New-Item -ItemType Directory -Force -Path $Out | Out-Null
Write-Host "Blender: $Blender"
Write-Host "Out:     $Out"

$jobs = @(
  @{ prompt = "pebble";          name = "pebble" },
  @{ prompt = "rubble fragment"; name = "rubble_frag" },
  @{ prompt = "weed tuft";       name = "weed_tuft" },
  @{ prompt = "litter scrap";    name = "litter_scrap" }
)

foreach ($j in $jobs) {
  Write-Host "`n=== Building: $($j.prompt) ==="
  & $Blender --background --python $Tool -- `
      --prompt $j.prompt --seed 1999 --out $Out `
      --render (Join-Path $Out ($j.name + "_specimen.png"))
  Write-Host "--- patch view: $($j.prompt) ---"
  & $Blender --background --python $Tool -- `
      --prompt $j.prompt --seed 1999 --out $Out --view patch --patch 45 `
      --render (Join-Path $Out ($j.name + "_patch.png"))
}

Write-Host "`n=== SHAPE METRICS FROM THE BUILT GLBs ==="
Write-Host "(glTF space is Y-UP; shape_metrics defaults to up=1 for that reason)"
$env:PYTHONIOENCODING = "utf-8"
python (Join-Path $Factory "tools\shape_metrics.py") --dir $Out

Write-Host "`nPNGs:"
Get-ChildItem $Out -Filter *.png -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "  $($_.FullName)" }
