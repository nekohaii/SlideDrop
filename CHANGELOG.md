# Changelog



## Unreleased

### 2026-05-01

- Removed duplicate `config.py`; app constants and persisted settings live in `settings.py` only.
- Local HTTP API listens on `127.0.0.1` only; CLI `slidedrop api` no longer accepts `--host`.
- Optional Authenticode signing for the Windows portable EXE via `scripts/windows/sign-exe.ps1` and secrets `WINDOWS_PFX_BASE64` / `WINDOWS_PFX_PASSWORD` in the release workflow.

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

