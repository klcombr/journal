# Contributing

Thanks for taking the time to contribute. `journal` is a tiny project on
purpose — the bar for new features is high.

## Setup

```bash
pip install -e . pytest
pytest
```

## Checklist before opening a PR

- [ ] Add or update tests under `tests/`.
- [ ] Run the full suite: `pytest`.
- [ ] Update `docs/changelog.md` under *Unreleased*.
- [ ] Keep the diff small and focused.

## Conventions

- Follow the existing style: short functions, no dependencies beyond the
  stdlib, docstrings where behaviour isn't obvious.
- `core.py` must stay pure — no printing, no `sys` access.
- Prefer the fixture `tests/fixtures/journal-test.md` for sample data over
  hand-writing temp files when the test isn't about file I/O.

## Issues

- Bug? Include the command you ran and the output.
- Idea? Open a discussion before writing code — most ideas don't survive
  contact with the *tiny* philosophy.
