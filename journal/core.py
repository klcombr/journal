from datetime import datetime
from pathlib import Path

DEFAULT_FILE = "journal.md"


def entry_line(text: str, when: datetime | None = None) -> str:
    when = when or datetime.now().astimezone()
    stamp = when.isoformat(timespec="seconds")
    return f"- {stamp} {text}"


def append_entry(path, text: str, when: datetime | None = None) -> str:
    line = entry_line(text, when)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return line


def read_entries(path):
    p = Path(path)
    if not p.exists():
        return []
    return [l for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]


def day_count(path) -> int:
    days = set()
    for line in read_entries(path):
        parts = line.split()
        if len(parts) >= 2:
            days.add(parts[1][:10])
    return len(days)
