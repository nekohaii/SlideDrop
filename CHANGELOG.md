# Changelog

## Unreleased

- Added headless `slidedrop convert` CLI and loopback-only `slidedrop api` HTTP JSON automation surface.
- Added `.pptx` font preflight heuristics and optional hash-based skip-if-unchanged PDF workflow with sidecar metadata.
- Added GitHub Actions workflows for macOS builds and GitHub Pages deployment; enabled Dependabot for pip and Actions.
- Raised CI coverage gate to 65% on automation-tested modules (GUI/API entrypoints omitted from denominator).
- Sync Windows `version_info.txt` from `slidedrop.version`, added Inno Setup template and Linux headless notes.
- Moved mock conversion engine out of the shipped package into `tests/support`.
- Added optional Sentry initialization via `SLIDEDROP_SENTRY_DSN`.

## 0.1.0

- Added the first Windows portable SlideDrop release.
- Added local LibreOffice conversion with queue management and background processing.
- Added proprietary licensing, release packaging, GitHub Pages, and CI/release automation scaffolding.
