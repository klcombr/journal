import argparse
import getpass
import os
import sys
from pathlib import Path

from .core import (
    DEFAULT_FILE,
    _cred_path,
    append_entry,
    day_count,
    load_credentials,
    login_or_register,
    read_entries,
    save_credentials,
    sync_push,
)


def _resolve_file(value):
    if value:
        return Path(value)
    return Path(os.environ.get("JOURNAL_FILE", DEFAULT_FILE))


def _api_base(base):
    return (base or os.environ.get("JOURNAL_API") or "http://127.0.0.1:8000").rstrip("/")


def _auth(creds, base, register=False):
    if creds:
        return creds["token"]
    # Non-interactive: JOURNAL_USERNAME / JOURNAL_PASSWORD env vars.
    env_user = os.environ.get("JOURNAL_USERNAME")
    env_pass = os.environ.get("JOURNAL_PASSWORD")
    if env_user and env_pass:
        token = login_or_register(base, env_user, env_pass, register=register)
        save_credentials(base, env_user, token)
        print(f"stored credentials for {env_user} at {base}")
        return token
    if not sys.stdin.isatty():
        raise SystemExit(
            "login required: run `journal sync --login` interactively, "
            "or set JOURNAL_USERNAME and JOURNAL_PASSWORD"
        )
    username = input("username: ").strip()
    password = getpass.getpass("password: ")
    token = login_or_register(base, username, password, register=register)
    save_credentials(base, username, token)
    print(f"stored credentials for {username} at {base}")
    return token


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

    sync = sub.add_parser("sync", help="sync with the journal server")
    sync.add_argument("--base", help="API base URL")
    sync.add_argument("--login", action="store_true", help="login or register (interactive)")
    sync.add_argument("--register", action="store_true", help="register a new account on login")
    sync.add_argument("--pull", action="store_true", help="pull server entries into local file")
    sync.add_argument("--push", action="store_true", help="push local entries to server")
    sync.add_argument("--logout", action="store_true", help="remove stored credentials")
    sync.add_argument("-f", "--file", help="journal file to sync")

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

    elif args.command == "sync":
        base = _api_base(args.base)
        sync_path = Path(args.file) if args.file else _resolve_file(None)
        creds = load_credentials(base)
        if args.logout:
            p = _cred_path()
            if p.exists():
                import json
                data = json.loads(p.read_text())
                data.pop(base, None)
                p.write_text(json.dumps(data, indent=2))
                print("logged out")
            return 0
        token = _auth(creds, base, register=args.register)
        push = args.push or not (args.pull or args.push)  # default both
        pull = args.pull or not (args.pull or args.push)
        for msg in sync_push(pull, push, str(sync_path), base, token):
            print(msg)
        print(f"days logged: {day_count(sync_path)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
