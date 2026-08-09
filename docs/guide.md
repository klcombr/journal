# journal — Guide

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

## Everyday workflow

1. Open a terminal.
2. `journal add "what I did / learned"`.
3. At the end of the week run `journal count --days` to see your consistency.

## Where the entries live

| Flag / var         | What it does                            |
| ------------------ | --------------------------------------- |
| `-f FILE`          | Use `FILE` for this invocation          |
| `JOURNAL_FILE`     | Set the default file for every call     |

## Nice shell aliases

```bash
alias j="journal add"
alias jc="journal count --days"
alias jl="journal list -n 10"
```
