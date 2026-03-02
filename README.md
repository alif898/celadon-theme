# celadon-theme

[![JetBrains Plugin Downloads](https://img.shields.io/jetbrains/plugin/d/30354?style=flat&logo=jetbrains&label=Downloads&color=518c83)](https://plugins.jetbrains.com/plugin/30354)

[![codecov](https://codecov.io/gh/alif898/celadon-theme/graph/badge.svg?token=H8KVORM1T7)](https://codecov.io/gh/alif898/celadon-theme)


**Celadon** is a dark IDE theme inspired by the muted, matte finish of classical ceramics. 
It layers cheerful, milky pastels over a deep jade base, 
providing a high-contrast yet eye-friendly environment for long-form coding.

## Project Details

This project uses a single source of truth for the HEX palette. 
Theme files are generated automatically via Python and Jinja2 templates.

The project is managed using `uv`.

## Development

### Prerequisites
- Python 3.12+
- `uv`

### Setup
```bash
uv pip install -e .
```

### Run Generator
```bash
uv run celadon-theme
```

### Run Tests
```bash
uv run pytest tests
```

### Run Type Checks
```bash
uv run mypy src tests
```
