from datetime import datetime

import pytest

from journal.core import append_entry, day_count, entry_line, read_entries


def test_entry_line_format():
    when = datetime(2026, 8, 3, 12, 30, 15)
    assert entry_line("hi", when) == "- 2026-08-03T12:30:15 hi"


def test_append_and_read_roundtrip(tmp_path):
    f = tmp_path / "j.md"
    append_entry(f, "first")
    append_entry(f, "second")
    lines = read_entries(f)
    assert len(lines) == 2
    assert lines[0].endswith("first")
    assert lines[1].endswith("second")


def test_read_missing_file_returns_empty(tmp_path):
    assert read_entries(tmp_path / "nope.md") == []


def test_day_count_dedupes(tmp_path):
    f = tmp_path / "j.md"
    f.write_text(
        "- 2026-08-03T10:00:00 a\n"
        "- 2026-08-03T11:00:00 b\n"
        "- 2026-08-04T09:00:00 c\n"
    )
    assert day_count(f) == 2
