# journal-gui

Desktop client for journal — Python + Tkinter, no external dependencies.

## Features

- Local journal file (same markdown format as the CLI).
- Account login/register against the journal server.
- One-click sync (push + pull).
- Auto-refresh of server entries.

## Run

```bash
python3 journal_gui.py
```

Env vars: `JOURNAL_FILE` (default `journal.md`), `JOURNAL_API`
(default `http://127.0.0.1:8000`).

The GUI stores its server credentials in `~/.config/journal/credentials.json`
(same file as the CLI).
