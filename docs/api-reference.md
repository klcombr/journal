# Python API Reference

`journal` exposes a small, stable API for building your own tools on top of
your journal file.

## `journal.core.entry_line(text, when=None) -> str`

Build a single markdown entry line.

```python
from journal.core import entry_line
from datetime import datetime

entry_line("hi", datetime(2026, 8, 3, 12, 30, 15))
# '- 2026-08-03T12:30:15 hi'
```

## `journal.core.append_entry(path, text, when=None) -> str`

Append an entry to `path` (creating parent directories as needed) and return
the line that was written.

## `journal.core.read_entries(path) -> list[str]`

Return every `- ` prefixed line in the file, in order. A missing file yields
an empty list.

## `journal.core.day_count(path) -> int`

Count the number of distinct calendar days that appear in the file.

```python
from journal.core import day_count

day_count("tests/fixtures/journal-test.md")
# 6
```

## Package imports

```python
from journal import append_entry, day_count, entry_line, read_entries
```
