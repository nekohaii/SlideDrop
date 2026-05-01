# Bundled LibreOffice Resources

SlideDrop can look for a bundled LibreOffice runtime before falling back to a
system installation.

Do not commit LibreOffice binaries to this repository. Place platform-specific
runtime files here only during packaging or installer creation.

Expected layout:

```text
resources/windows/libreoffice/program/soffice.exe
resources/macos/LibreOffice.app/Contents/MacOS/soffice
```

If LibreOffice is bundled in a commercial installer, include the full LibreOffice
license notices and comply with The Document Foundation's distribution terms.
