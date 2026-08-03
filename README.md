# journal

A tiny personal journal CLI. Write short entries to a markdown file and keep
track of how many days you have logged.

## Install

```bash
pip install -e .
```

## Usage

```bash
journal add "learned how Actions cron works"
journal list -n 5
journal count
journal count --days
```

By default entries go to `journal.md` in the current directory. Override with
`-f FILE` or the `JOURNAL_FILE` environment variable.

## Development

```bash
pip install -e . pytest
pytest
```
