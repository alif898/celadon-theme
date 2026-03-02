# celadon-theme

[![JetBrains Plugin Downloads](https://img.shields.io/jetbrains/plugin/d/30354?style=flat&logo=jetbrains&label=Downloads&color=518c83)](https://plugins.jetbrains.com/plugin/30354)

[![codecov](https://codecov.io/gh/alif898/celadon-theme/graph/badge.svg?token=H8KVORM1T7)](https://codecov.io/gh/alif898/celadon-theme)
[![Quality Check CI](https://github.com/alif898/celadon-theme/actions/workflows/quality-check-ci.yml/badge.svg?branch=main)](https://github.com/alif898/celadon-theme/actions/workflows/quality-check-ci.yml)

**Celadon** is a dark IDE theme inspired by the muted, matte finish of classical ceramics. 
It layers cheerful, milky pastels over a deep jade base, 
providing a high-contrast yet eye-friendly environment for long-form coding.

## Project Details

This project uses a single source of truth for the color palette, defined in `palette.yml`.
The palette, along with Jinja2 templates, are used to generate the theme files.

The project uses Python `3.12` and is managed using `uv`

## Instructions

To install the project:
```bash
uv pip install -e .
```

To run the theme generator:
```bash
uv run celadon-theme
```

To run unit tests:
```bash
uv run pytest tests
```

To run `mypy` static type checks:
```bash
uv run mypy src tests
```

## CI/CD

CI/CD is performed with GitHub Actions.
On top of unit tests, code coverage is also checked with `codecov` and code quality is checked with `Qodana`.

