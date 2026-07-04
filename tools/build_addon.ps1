<#
    build_addon.ps1 — package zoo_keeper/ as an installable Blender add-on zip.

    The add-on SOURCE lives in the repo (zoo_keeper/). This script produces a
    redistributable zip with zoo_keeper/ at the top level, which is what
    Blender's "Install from Disk" expects. It is a build artifact — attach it
    to a GitHub Release; do not commit it.

    Usage (from anywhere):
        .\tools\build_addon.ps1
        .\tools\build_addon.ps1 -OutDir C:\somewhere

    Output: dist\zoo_keeper_blender_addon_v<VERSION>.zip
#>
param(
    [string]$OutDir = "dist"
)

$ErrorActionPreference = "Stop"

# repo root = parent of this script's folder
$repo = Split-Path -Parent $PSScriptRoot
$pkg  = Join-Path $repo "zoo_keeper"
if (-not (Test-Path $pkg)) {
    throw "zoo_keeper/ not found next to the repo root ($repo)."
}

# version string from the VERSION file, e.g. "Zoo 0.4.0" -> "0.4.0"
$verLine = (Get-Content (Join-Path $repo "VERSION") -First 1).Trim()
$version = ($verLine -replace '^\D*', '')

if (-not [System.IO.Path]::IsPathRooted($OutDir)) {
    $OutDir = Join-Path $repo $OutDir
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$zip = Join-Path $OutDir "zoo_keeper_blender_addon_v$version.zip"
if (Test-Path $zip) { Remove-Item $zip }

# stage a clean copy (no __pycache__ / .pyc) so the zip is reproducible
$stage = Join-Path $env:TEMP ("zoo_addon_" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $stage | Out-Null
try {
    Copy-Item $pkg -Destination $stage -Recurse
    Get-ChildItem $stage -Recurse -Include "__pycache__" -Directory |
        Remove-Item -Recurse -Force
    Get-ChildItem $stage -Recurse -Include "*.pyc" -File | Remove-Item -Force
    Compress-Archive -Path (Join-Path $stage "zoo_keeper") -DestinationPath $zip
    Write-Host "Built $zip"
}
finally {
    Remove-Item $stage -Recurse -Force
}
