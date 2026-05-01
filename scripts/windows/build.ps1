param(
    [ValidateSet("Portable", "OneFolder", "Both")]
    [string]$Mode = "Portable"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
Set-Location $ProjectRoot

Write-Host "Installing runtime and packaging dependencies..."
python -m pip install -r requirements.txt -r requirements-dev.txt

Write-Host "Syncing Windows VERSIONINFO..."
python "$ProjectRoot\scripts\windows\sync-version-info.py"

Remove-Item -Recurse -Force dist\windows, release\windows -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path release\windows | Out-Null

if ($Mode -eq "OneFolder" -or $Mode -eq "Both") {
    Write-Host "Building optional Windows one-folder package..."
    python -m PyInstaller `
        --clean `
        --noconfirm `
        --distpath dist\windows `
        --workpath build\windows\onefolder `
        packaging\windows\SlideDrop.spec

    New-Item -ItemType Directory -Force -Path release\windows\SlideDrop-one-folder | Out-Null
    Copy-Item -Recurse -Force dist\windows\SlideDrop release\windows\SlideDrop-one-folder\SlideDrop
}

if ($Mode -eq "Portable" -or $Mode -eq "Both") {
    Write-Host "Building recommended Windows portable single-EXE package..."
    python -m PyInstaller `
        --clean `
        --noconfirm `
        --windowed `
        --onefile `
        --name SlideDrop `
        --icon "$ProjectRoot\assets\slidedrop.ico" `
        --version-file "$ProjectRoot\packaging\windows\version_info.txt" `
        --paths "$ProjectRoot\src" `
        --collect-data customtkinter `
        --collect-data tkinterdnd2 `
        --collect-binaries tkinterdnd2 `
        --distpath dist\windows `
        --workpath build\windows\onefile `
        --specpath build\windows\generated `
        "$ProjectRoot\run.py"

    New-Item -ItemType Directory -Force -Path release\windows\SlideDrop-portable | Out-Null
    Copy-Item -Force dist\windows\SlideDrop.exe release\windows\SlideDrop-portable\SlideDrop.exe

    if ($env:WINDOWS_PFX_BASE64 -and $env:WINDOWS_PFX_PASSWORD) {
        Write-Host "Signing portable EXE (Authenticode)..."
        & (Join-Path $ScriptDir "sign-exe.ps1") -ExePath "release\windows\SlideDrop-portable\SlideDrop.exe"
    }
    else {
        Write-Host "Skipping Authenticode: set WINDOWS_PFX_BASE64 and WINDOWS_PFX_PASSWORD to sign before zipping."
    }

    Copy-Item -Force README.md release\windows\SlideDrop-portable\README.txt
    Copy-Item -Force LICENSE release\windows\SlideDrop-portable\LICENSE.txt
    Copy-Item -Force NOTICE.txt release\windows\SlideDrop-portable\NOTICE.txt
    Compress-Archive -Path release\windows\SlideDrop-portable\* -DestinationPath release\windows\SlideDrop-windows-portable.zip -Force
}

Write-Host "Build complete."
Write-Host "Recommended Windows release: release\windows\SlideDrop-windows-portable.zip"
Write-Host "Portable EXE: release\windows\SlideDrop-portable\SlideDrop.exe"
