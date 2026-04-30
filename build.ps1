param(
    [ValidateSet("Portable", "OneFolder", "Both")]
    [string]$Mode = "Portable"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "Installing runtime and packaging dependencies..."
python -m pip install -r requirements.txt -r requirements-dev.txt

Remove-Item -Recurse -Force dist, release -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path release | Out-Null

if ($Mode -eq "OneFolder" -or $Mode -eq "Both") {
    Write-Host "Building optional one-folder package..."
    python -m PyInstaller --clean --noconfirm packaging\SlideDrop.spec
    New-Item -ItemType Directory -Force -Path release\SlideDrop-one-folder | Out-Null
    Copy-Item -Recurse -Force dist\SlideDrop release\SlideDrop-one-folder\SlideDrop
}

if ($Mode -eq "Portable" -or $Mode -eq "Both") {
    Write-Host "Building recommended portable single-EXE package..."
    python -m PyInstaller `
        --clean `
        --noconfirm `
        --windowed `
        --onefile `
        --name SlideDrop `
        --icon "$ProjectRoot\assets\slidedrop.ico" `
        --version-file "$ProjectRoot\packaging\version_info.txt" `
        --paths "$ProjectRoot\src" `
        --collect-data customtkinter `
        --collect-data tkinterdnd2 `
        --collect-binaries tkinterdnd2 `
        --workpath build\onefile `
        --specpath build\generated `
        "$ProjectRoot\run.py"

    New-Item -ItemType Directory -Force -Path release\SlideDrop-portable | Out-Null
    Copy-Item -Force dist\SlideDrop.exe release\SlideDrop-portable\SlideDrop.exe
    Copy-Item -Force README.md release\SlideDrop-portable\README.txt
    Compress-Archive -Path release\SlideDrop-portable\* -DestinationPath release\SlideDrop-portable.zip -Force
}

Write-Host "Build complete."
Write-Host "Recommended portable release: release\SlideDrop-portable.zip"
Write-Host "Portable EXE: release\SlideDrop-portable\SlideDrop.exe"
