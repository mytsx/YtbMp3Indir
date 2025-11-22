# Repository Guidelines

## Project Structure & Module Organization
- `mp3yap_gui.py`: PyQt5 entry point; reads `config.json`, writes `debug.log`.
- `core/`: download/conversion engine (yt-dlp + ffmpeg) and threading support.
- `services/url_analyzer.py`: URL validation/caching before enqueueing downloads.
- `ui/`: Qt widgets (`main_window.py`, `queue_widget.py`, `history_widget.py`, `converter_widget.py`, etc.).
- `utils/`: config/state helpers, translation management, update checks, YouTube utilities.
- `assets/`: icons and bundled ffmpeg binaries; `resources/` holds original images.
- `translations/`, `translation_keys_mapping.json`, `translations_for_ai.json`, `translations.db`: localization data; `data/`, `database/` store supporting artifacts.
- `scripts/`: icon processing helpers; `mp3yap.spec` and `mp3yap_portable.spec` are PyInstaller configs.

## Build, Test, and Development Commands
- `pip install -r requirements.txt` — install runtime deps (PyQt5, yt-dlp, static-ffmpeg, etc.).
- `pip install -r requirements-dev.txt` — add build-time tools (PyInstaller, Pillow).
- `python mp3yap_gui.py` — run the app locally; verifies end-to-end download/conversion.
- `pyinstaller mp3yap.spec` — build installer; `pyinstaller mp3yap_portable.spec` for portable build.
- Translation maintenance (when needed): `python generate_translations.py` or `python manage_translations.py`.

## Coding Style & Naming Conventions
- Target Python 3.11 runtime; prefer 4-space indentation and PEP 8 spacing.
- Use type hints where practical; keep UI work on the main thread and offload downloads to workers.
- Naming: `snake_case` for functions/vars, `PascalCase` for Qt widgets/classes, `UPPER_SNAKE` for constants.
- Keep translation keys aligned with `translation_keys_mapping.json`; avoid hard-coded user-facing strings.

## Testing Guidelines
- No automated test suite yet; rely on manual smoke checks.
- Validate: single and playlist downloads, cancel/resume paths, MP3 conversion of audio/video, and history updates.
- Confirm output in `music/`, localization strings after changes, and absence of regressions in `debug.log`.

## Commit & Pull Request Guidelines
- Follow conventional commit prefixes seen in history (`feat:`, `fix:`, `refactor:`, `chore:`); keep subjects imperative and concise.
- PRs should include a brief summary, reproduction/verification steps, and screenshots or clips for UI changes.
- Mention installer impact when touching `.spec` files or assets; update docs (`README.md`, `docs/TODO.md`, `docs/UI_FIXES.md`) and translation files when UI text changes.
