param(
    [string]$AppName = "FocusFlow"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

python -m pip install -r requirements.txt

$distPath = Join-Path $root "dist"
$buildPath = Join-Path $root "build"
$specPath = Join-Path $root "$AppName.spec"

if (Test-Path $distPath) { Remove-Item -Path $distPath -Recurse -Force }
if (Test-Path $buildPath) { Remove-Item -Path $buildPath -Recurse -Force }
if (Test-Path $specPath) { Remove-Item -Path $specPath -Force }

pyinstaller --noconfirm --windowed --name $AppName --paths src src/focusflow/__main__.py

Write-Host "Build complete. Executable is available under dist/$AppName/"
