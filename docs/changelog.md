# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Add `journal export` to render the file as HTML.
- Optional date filtering: `journal list --since 2026-08-01`.

## [0.1.0] — 2026-08-03

### Added

- `journal add "text"` — append a timestamped entry.
- `journal list -n N` — show the most recent N entries.
- `journal count` — number of days with at least one entry.
- `journal count --days` — print the list of logged days.
- `-f/--file` flag and `JOURNAL_FILE` env override.
- Importable Python API: `append_entry`, `read_entries`, `day_count`.
- MIT license.
