# Contributing

## Setup

```bash
git clone https://github.com/TadMSTR/nextcloud-mcp.git
cd nextcloud-mcp
pip install -e ".[dev]"
```

## Testing

```bash
pytest tests/ -v
```

## Linting

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Adding a tool

1. Add the backend function to `occ.py`, `ocs.py`, or `webdav.py`.
2. Add the `@mcp.tool()` decorator in `server.py`.
3. Add a unit test in `tests/`.

## Pull Requests

- Feature branches: `feature/<slug>`
- Bug fixes: `fix/<slug>`
- Tests required for all new tools.
- Run `ruff check` and `pytest` before opening a PR.
