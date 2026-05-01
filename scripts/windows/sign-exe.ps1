param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath
)

$ErrorActionPreference = "Stop"

if (-not $env:WINDOWS_PFX_BASE64) {
    throw "WINDOWS_PFX_BASE64 is not set."
}
if (-not $env:WINDOWS_PFX_PASSWORD) {
    throw "WINDOWS_PFX_PASSWORD is not set."
}

$exeResolved = Resolve-Path $ExePath
if (-not (Test-Path $exeResolved)) {
    throw "Executable not found: $ExePath"
}

$signtoolCandidates = @()
if ($env:WindowsSdkDir) {
    $signtoolCandidates += Get-ChildItem -Path (Join-Path $env:WindowsSdkDir "bin") -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue
}
$signtoolCandidates += Get-ChildItem -Path "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue

$signtool = $signtoolCandidates |
    Where-Object { $_.FullName -match '\\x64\\signtool\.exe$' } |
    Sort-Object FullName -Descending |
    Select-Object -First 1

if (-not $signtool) {
    throw "signtool.exe not found. Install the Windows SDK on this runner or set WindowsSdkDir."
}

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("slidedrop-sign-" + [Guid]::NewGuid().ToString("n"))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
$pfxPath = Join-Path $tempDir "sign.pfx"

try {
    $pfxBytes = [Convert]::FromBase64String($env:WINDOWS_PFX_BASE64)
    [System.IO.File]::WriteAllBytes($pfxPath, $pfxBytes)

    $secureArgs = @(
        "sign",
        "/f", $pfxPath,
        "/p", $env:WINDOWS_PFX_PASSWORD,
        "/tr", "http://timestamp.digicert.com",
        "/td", "sha256",
        "/fd", "sha256",
        $exeResolved.Path
    )

    $proc = Start-Process -FilePath $signtool.FullName -ArgumentList $secureArgs -Wait -PassThru -NoNewWindow
    if ($proc.ExitCode -ne 0) {
        throw "signtool exited with code $($proc.ExitCode)."
    }
    Write-Host "Signed: $exeResolved"
}
finally {
    Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
