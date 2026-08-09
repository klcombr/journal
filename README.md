# journal

A tiny personal journal CLI. Write short entries to a markdown file and keep
track of how many days you have logged.

> **Website:** <https://klcombr.github.io/journal/>

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

## Example

```bash
$ journal add "shipped the URL shortener"
✔ added — 2026-08-08T09:27:47+00:00

$ journal count
6
```

## Development

```bash
pip install -e . pytest
pytest
```

## Documentation

- [Guide](docs/guide.md)
- [API reference](docs/api-reference.md)
- [Architecture](docs/architecture.md)
- [Examples](examples/workflow.md)
- [Changelog](docs/changelog.md)

## License

[MIT](LICENSE)
