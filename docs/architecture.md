# Architecture

## Overview

```
journal.md ──► journal.core ──► journal.cli ──► your terminal
   (data)         (logic)         (interface)     (usage)
```

The project is intentionally small: one data file, one logic module, one thin
CLI wrapper.

## Modules

### `journal.core`

Pure functions, no I/O beyond the file path passed in. Easy to test and easy
to reuse:

- `entry_line` — format a line.
- `append_entry` — write a line.
- `read_entries` — read lines back.
- `day_count` — distinct days.

### `journal.cli`

`argparse`-based entrypoint. Resolves the target file via `-f` or
`JOURNAL_FILE`, then delegates to `core`. Keep logic here minimal.

## Data format

Plain markdown list, one entry per line:

```markdown
- 2026-08-03T18:00:00+00:00 created this project
- 2026-08-04T09:54:31Z entry
```

Human-readable in any editor; machine-parseable because timestamps are
always the second token.

## Design rules

1. Entries are append-only.
2. Never store anything but the file path in `core`.
3. The CLI never formats timestamps itself.
4. The fixture `tests/fixtures/journal-test.md` is the canonical sample of
   the on-disk format.
