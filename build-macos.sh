#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "macOS builds must be created on macOS."
  echo "Use build.ps1 on Windows and build-macos.sh on macOS."
  exit 1
fi

echo "Installing runtime and packaging dependencies..."
python3 -m pip install -r requirements.txt -r requirements-dev.txt

rm -rf "dist-macos" "build/macos" "release/macos"
mkdir -p "release/macos"

echo "Building SlideDrop.app..."
python3 -m PyInstaller \
  --clean \
  --noconfirm \
  --distpath "dist-macos" \
  --workpath "build/macos" \
  "packaging/SlideDrop.macos.spec"

echo "Creating macOS zip..."
ditto -c -k --sequesterRsrc --keepParent \
  "dist-macos/SlideDrop.app" \
  "release/macos/SlideDrop-macOS.zip"

echo "Build complete."
echo "macOS app: dist-macos/SlideDrop.app"
echo "macOS release: release/macos/SlideDrop-macOS.zip"
echo "Note: users need LibreOffice installed in /Applications."
