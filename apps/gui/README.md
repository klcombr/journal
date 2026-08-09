# journal-gui

Desktop client for journal — Python + Tkinter, no external dependencies.

## Features

- Local journal file (same markdown format as the CLI).
- Account login/register against the journal server (card layout, Enter to submit).
- One-click sync (push + pull) with status feedback.
- Auto-refresh of server entries.
- Entry list grouped by day with "today"/"yesterday" labels.
- Delete with confirmation (double-click, Delete or Enter on selection).
- Pick any journal file with the "open…" button.
- Keyboard-friendly: Enter adds an entry, Enter/Delete removes the selection.

## Run

```bash
python3 journal_gui.py
```

Env vars: `JOURNAL_FILE` (default `journal.md`), `JOURNAL_API`
(default `http://127.0.0.1:8000`).

The GUI stores its server credentials in `~/.config/journal/credentials.json`
(same file as the CLI).
