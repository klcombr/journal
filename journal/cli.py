import argparse
import os
from pathlib import Path

from .core import DEFAULT_FILE, append_entry, day_count, read_entries


def _resolve_file(value):
    if value:
        return Path(value)
    return Path(os.environ.get("JOURNAL_FILE", DEFAULT_FILE))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="journal", description="Personal journal CLI")
    parser.add_argument("-f", "--file", help="journal file (default: journal.md or $JOURNAL_FILE)")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="append an entry")
    add.add_argument("text", nargs="+", help="entry text")

    ls = sub.add_parser("list", help="list entries")
    ls.add_argument("-n", type=int, default=10, help="number of recent entries")

    cnt = sub.add_parser("count", help="number of days with entries")
    cnt.add_argument("--days", action="store_true", help="show the list of days")

    args = parser.parse_args(argv)
    path = _resolve_file(args.file)

    if args.command == "add":
        print(append_entry(path, " ".join(args.text)))

    elif args.command == "list":
        entries = read_entries(path)
        for line in entries[-args.n:]:
            print(line)

    elif args.command == "count":
        if args.days:
            days = sorted({l.split()[1][:10] for l in read_entries(path) if len(l.split()) >= 2})
            print("\n".join(days))
        else:
            print(day_count(path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
