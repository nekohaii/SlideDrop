macOS icon asset

PyInstaller uses `assets/slidedrop.ico` on Windows. For a polished `.app` bundle,
generate `assets/slidedrop.icns` from the same master artwork and reference it from
`packaging/macos/SlideDrop.macos.spec` using PyInstaller's `icon=` parameter.

Apple guidelines recommend including multiple icon sizes inside the `.icns` container.
