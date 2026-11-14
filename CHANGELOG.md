# Changelog

## 1.3.0
### Added
- Pure Bengali (বাংলা) language switcher: Full UI translation across all menus, units, dialogs, and tray icon
- Interactive hover tooltips on Upload, Download, RAM, and CPU with smart taskbar placement and top-level Z-index
- 2-Row Stacked speed layout option (Upload on top or Download on top) for an ultra-compact taskbar footprint
- Classic Windows Setup installer wizard (`BanglaNetSpeed-Setup.exe`) with Desktop/Start menu shortcuts and uninstaller
- Rebranded to Bangla Net Speed Meter (বাংলা নেট স্পিড মিটার)

## 1.2.1
- Updates `setuptools` to 84.1.0 in the build lock to clear GHSA-xmj3-9gf7-h52w, which failed the dependency audit

## 1.2.0
### Added
- Right-click "CPU / RAM usage": CPU + RAM (stacked), RAM only, CPU only (single row) or Hidden
- Right-click "Widget size" and a bottom-right grip to resize by dragging; Ctrl+wheel still works
### Changed
- Upload/download speeds are always centred, with new arrow icons matching the CPU/RAM icons
- Default width is now 310; `show_stats` setting replaced by `stats_mode`

## 1.1.2
- Regenerates `requirements-build.txt` on Windows so it includes `pefile` and `pywin32-ctypes`, which PyInstaller needs; the build failed without them

## 1.1.1
- Fixes the unit tests for the new `show_stats` setting (v1.1.0 never built)

## 1.1.0
### Added
- CPU and RAM usage (%) column: RAM icon on top, CPU icon below. Toggle it from the right-click menu ("Show CPU / RAM usage")

## Unreleased
### Security
- Validates every value in `settings.json` (types, finite numbers, ranges, `#RRGGBB` colors, 64 KB size limit) so a corrupted or tampered file falls back to defaults instead of crashing
- Writes settings atomically to prevent corruption
- Uses explicit `ctypes` prototypes and `use_last_error` for Win32 calls
- Pins all dependencies to exact versions with SHA-256 hashes and installs them into isolated virtual environments
- Hardens GitHub Actions: SHA-pinned actions, least-privilege permissions, no persisted credentials, dependency audit and tests before every build, build provenance attestations
- Adds CI (tests + `pip-audit`), CodeQL scanning and Dependabot
- Signing script no longer exposes the PFX password on the command line, and the workflow now actually signs when signing secrets are configured
- Builds without UPX to reduce antivirus false positives
- `uninstall.bat` no longer risks deleting the wrong folder when `%APPDATA%` is unset

## 1.0.0
- Automatically enables current-user startup on first successful launch
- Adds a checked Start with Windows menu item
- Refreshes startup path after the app is moved and launched again
- Removes only the legacy startup value from earlier project builds
- Fixes duplicate topmost guard timers from the tray Bring to front action
- Adds startup failure handling instead of crashing
- Adds privacy, permissions, security and distribution documentation
