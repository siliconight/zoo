# ============================================================
#  walkabout.ps1 - DELCO fixture-pass verification harness
#  Home: zoo\tools\ (v0.30.1) - paths derived from the repo location.
#  zoo v0.29.0 / lux v0.14.0 / deli_counter v0.75.0
#
#  Runs:  env audit -> tool versions -> manifest discovery ->
#         anchor counts -> zoo plan (pure) -> zoo Blender build
#         (building) -> zoo Blender build (site streetlights) ->
#         built-index gates -> zips everything for upload.
#
#  Does NOT run: DC/Lot builds (run yours first if you want
#  fresh manifests) or Godot/Lux (Bake Lights / Bind Emissives
#  stay manual in-editor).
#
#  Run:
#  powershell -ExecutionPolicy Bypass -File C:\Projects\gabagool_studios\gabagool_factory\zoo\tools\walkabout.ps1
# ============================================================

$ErrorActionPreference = "Continue"
$ZooRepo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Factory = (Resolve-Path (Join-Path $ZooRepo "..")).Path
$Blender = "C:\blender\blender.exe"
$Tools   = @("deli_counter","lot","lux","zoo")

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Runs = Join-Path $Factory "_runs"
New-Item -ItemType Directory -Path $Runs -Force | Out-Null
$Out   = Join-Path $Runs ("walkabout_" + $Stamp)
New-Item -ItemType Directory -Path $Out -Force | Out-Null
$Log   = Join-Path $Out "walkabout.log"

function W([string]$m) { Write-Host $m; Add-Content -Path $Log -Value $m }
function Section([string]$n) { W ""; W ("=" * 62); W ("== " + $n); W ("=" * 62) }

# ------------------------------------------------------------
Section "0. ENVIRONMENT"
W ("timestamp : " + (Get-Date -Format o))
W ("factory   : " + $Factory)
W ("psversion : " + $PSVersionTable.PSVersion.ToString())
try { W ("python    : " + ((& python --version 2>&1) -join " ")) } catch { W "python    : NOT FOUND on PATH" }
if (Test-Path $Blender) {
    $bv = & $Blender --version 2>&1 | Select-Object -First 1
    W ("blender   : " + $bv)
} else {
    W ("blender   : MISSING at " + $Blender + "  (Blender stages will be skipped)")
}

# ------------------------------------------------------------
Section "1. TOOL VERSIONS (git + version markers)"
foreach ($t in $Tools) {
    $p = Join-Path $Factory $t
    if (-not (Test-Path $p)) { W ($t + " : FOLDER MISSING at " + $p); continue }
    $desc  = (& git -C $p describe --tags --always --dirty 2>&1) -join " "
    $dirty = (& git -C $p status --porcelain 2>&1 | Measure-Object).Count
    W ($t + " : git=" + $desc + "  dirty-files=" + $dirty)
    $vfiles = Get-ChildItem -Path $p -Recurse -Depth 3 -Include "VERSION","plugin.cfg" -File -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch "\\\.git\\" }
    foreach ($v in $vfiles) {
        if ($v.Name -eq "VERSION") {
            W ("    " + $v.FullName.Replace($Factory,"") + " = " + (Get-Content $v.FullName -First 1))
        } else {
            $ln = Select-String -Path $v.FullName -Pattern "version" | Select-Object -First 1
            if ($ln) { W ("    " + $v.FullName.Replace($Factory,"") + " : " + $ln.Line.Trim()) }
        }
    }
}

# ------------------------------------------------------------
Section "2. LIGHT MANIFEST DISCOVERY (*.lights.json)"
$manifests = Get-ChildItem -Path $Factory -Recurse -Filter "*.lights.json" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\\.git\\" -and $_.FullName -notmatch "walkabout_" } |
    Sort-Object LastWriteTime -Descending
if (-not $manifests) {
    W "NO *.lights.json found anywhere under the factory."
    W "Run your DC build (and Lot merge) first, then re-run this script."
}
foreach ($m in $manifests) {
    W ($m.LastWriteTime.ToString("yyyy-MM-dd HH:mm") + "  " + ("{0,9:n0}" -f $m.Length) + "  " + $m.FullName.Replace($Factory,""))
}

$Building = $manifests | Where-Object { $_.FullName -match "\\deli_counter\\" } | Select-Object -First 1
if (-not $Building) { $Building = $manifests | Select-Object -First 1 }
$Site = $manifests | Where-Object { $_.FullName -match "\\lot\\" } | Select-Object -First 1

$BPath = $null; $SPath = $null
if ($Building) {
    $BPath = $Building.FullName
    W ("BUILDING manifest -> " + $BPath)
    Copy-Item $BPath -Destination (Join-Path $Out ("building." + $Building.Name)) -Force
}
if ($Site) {
    $SPath = $Site.FullName
    W ("SITE manifest     -> " + $SPath)
    Copy-Item $SPath -Destination (Join-Path $Out ("site." + $Site.Name)) -Force
} else {
    W "SITE manifest     -> none found under lot\  (site streetlight stage will be skipped)"
}

# ------------------------------------------------------------
Section "3. MANIFEST ANCHOR COUNTS"
function Count-Anchors([string]$path, [string]$label) {
    try {
        $j = Get-Content $path -Raw | ConvertFrom-Json
        $arr = $null
        foreach ($k in @("anchors","lights","fixtures")) {
            if ($j.PSObject.Properties[$k]) { $arr = $j.$k; break }
        }
        if (-not $arr) {
            $keys = ($j.PSObject.Properties | ForEach-Object { $_.Name }) -join ", "
            W ($label + " : no anchors/lights array found (top-level keys: " + $keys + ")")
            return
        }
        W ($label + " : " + @($arr).Count + " anchors total")
        @($arr) | Group-Object { if ($_.PSObject.Properties["type"]) { $_.type } elseif ($_.PSObject.Properties["kind"]) { $_.kind } else { "?" } } |
            Sort-Object Count -Descending | ForEach-Object { W ("    " + $_.Name + "  x " + $_.Count) }
    } catch {
        W ($label + " : JSON parse failed - " + $_.Exception.Message)
    }
}
if ($BPath) { Count-Anchors $BPath "building" }
if ($SPath) { Count-Anchors $SPath "site" }

# ------------------------------------------------------------
$ZooDir = $ZooRepo
$ZooCli = Join-Path $ZooDir "tools\zoo_cli.py"

Section "4. ZOO PLAN (pure python, no Blender)"
if ($BPath -and (Test-Path $ZooCli)) {
    Push-Location $ZooDir
    $planOut = & python $ZooCli --fixtures $BPath 2>&1
    $planExit = $LASTEXITCODE
    Pop-Location
    $planOut | Out-File (Join-Path $Out "zoo_plan_building.log") -Encoding utf8
    $planOut | Select-Object -First 80 | ForEach-Object { W ("  " + $_) }
    W ("exit=" + $planExit + "  (full output: zoo_plan_building.log)")
} else {
    W "SKIPPED (no building manifest or zoo_cli.py not at tools\zoo_cli.py)"
}

# ------------------------------------------------------------
Section "5. ZOO FIXTURE BUILD - BUILDING (Blender bpy - THE unverified leg)"
$ArtB = Join-Path $Out "art_zoo_building"
if ($BPath -and (Test-Path $Blender) -and (Test-Path $ZooCli)) {
    Push-Location $ZooDir
    $bOut = & $Blender --background --python $ZooCli -- --fixtures $BPath --theme delco --out $ArtB 2>&1
    $bExit = $LASTEXITCODE
    Pop-Location
    $bOut | Out-File (Join-Path $Out "zoo_build_building.log") -Encoding utf8
    $bOut | Select-Object -Last 50 | ForEach-Object { W ("  " + $_) }
    W ("exit=" + $bExit + "  (full output: zoo_build_building.log)")
    if (Test-Path $ArtB) {
        Get-ChildItem $ArtB -Recurse -File | ForEach-Object { W ("  OUT " + ("{0,10:n0}" -f $_.Length) + "  " + $_.FullName.Replace($Out,"")) }
    } else {
        W "  NO OUTPUT DIRECTORY PRODUCED"
    }
} else {
    W "SKIPPED (missing manifest, blender.exe, or zoo_cli.py)"
}

# ------------------------------------------------------------
Section "6. ZOO FIXTURE BUILD - SITE STREETLIGHTS (Blender bpy)"
$ArtS = Join-Path $Out "art_zoo_site"
if ($SPath -and (Test-Path $Blender) -and (Test-Path $ZooCli)) {
    Push-Location $ZooDir
    $sOut = & $Blender --background --python $ZooCli -- --fixtures $SPath --fixture-types streetlight --theme delco --out $ArtS 2>&1
    $sExit = $LASTEXITCODE
    Pop-Location
    $sOut | Out-File (Join-Path $Out "zoo_build_site.log") -Encoding utf8
    $sOut | Select-Object -Last 50 | ForEach-Object { W ("  " + $_) }
    W ("exit=" + $sExit + "  (full output: zoo_build_site.log)")
    if (Test-Path $ArtS) {
        Get-ChildItem $ArtS -Recurse -File | ForEach-Object { W ("  OUT " + ("{0,10:n0}" -f $_.Length) + "  " + $_.FullName.Replace($Out,"")) }
    }
} else {
    W "SKIPPED (no site manifest, or blender/zoo_cli missing)"
}

# ------------------------------------------------------------
Section "7. GATE - BUILT INDEXES"
$built = Get-ChildItem $Out -Recurse -Filter "*.built.json" -File -ErrorAction SilentlyContinue
if (-not $built) { W "No *.built.json produced - see build logs above." }
foreach ($bj in $built) {
    W $bj.FullName.Replace($Out,"")
    try {
        $b = Get-Content $bj.FullName -Raw | ConvertFrom-Json
        if ($b.PSObject.Properties["emitter_markers"]) { W ("  emitter_markers: " + $b.emitter_markers + "  (prefix " + $b.marker_prefix + ") - Zoo v0.30+ marker contract present") } else { W "  emitter_markers: ABSENT (pre-v0.30 build)" }
        $barr = $null
        foreach ($k in @("placements","fixtures","built","assets","items")) {
            if ($b.PSObject.Properties[$k]) { $barr = $b.$k; break }
        }
        if ($barr) {
            W ("  " + @($barr).Count + " entries")
            @($barr) | Group-Object { if ($_.PSObject.Properties["species"]) { $_.species } elseif ($_.PSObject.Properties["type"]) { $_.type } elseif ($_.PSObject.Properties["kind"]) { $_.kind } else { "?" } } |
                Sort-Object Count -Descending | ForEach-Object { W ("    " + $_.Name + "  x " + $_.Count) }
        } else {
            $keys = ($b.PSObject.Properties | ForEach-Object { $_.Name }) -join ", "
            W ("  top-level keys: " + $keys)
        }
    } catch { W ("  parse failed - " + $_.Exception.Message) }
}

# ------------------------------------------------------------
Section "8. PACKAGE RESULTS"
$Zip = Join-Path $Runs ("walkabout_" + $Stamp + ".zip")
try {
    Compress-Archive -Path (Join-Path $Out "*") -DestinationPath $Zip -Force
    W ("RESULTS ZIP -> " + $Zip)
} catch {
    W ("Compress-Archive failed - " + $_.Exception.Message)
    W ("Zip the folder manually: " + $Out)
}
W ""
W "NEXT (manual, in Godot): import shell + fixture GLBs, Lux dock ->"
W "re-run Bake Lights (streetlight recentering), then Bind Emissives,"
W "then walk under gas_station_fluorescent / gothic_street_night."
W ""
W "Upload the results zip back to Claude."
