import uuid

from journal.core import _parse_line, entry_line


def test_parse_line_builds_stable_id():
    line = entry_line("hi", __import__("datetime").datetime(2026, 8, 3, 12, 30, 15))
    e = _parse_line(line)
    assert e["body"] == "hi"
    assert e["created_at"] == "2026-08-03T12:30:15"
    # deterministic: same input -> same id
    e2 = _parse_line(line)
    assert e2["id"] == e["id"]
    assert uuid.UUID(e["id"]).version == 5


def test_parse_line_ignores_non_entries():
    assert _parse_line("# not an entry") is None
    assert _parse_line("") is None
