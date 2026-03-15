# celadon-theme

![Config Version](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/alif898/celadon-theme/main/config.json&query=$.version&label=Version&color=518c83&style=flat)
[![JetBrains Plugin Downloads](https://img.shields.io/jetbrains/plugin/d/30354?style=flat&label=JetBrains%20Downloads&color=518c83)](https://plugins.jetbrains.com/plugin/30354)
[![VS Code Plugin Downloads](https://img.shields.io/visual-studio-marketplace/d/alif-naufal.celadon-theme?style=flat&label=VS%20Code%20Downloads&color=518c83)](https://marketplace.visualstudio.com/items?itemName=alif-naufal.celadon-theme)

[![codecov](https://codecov.io/gh/alif898/celadon-theme/graph/badge.svg?token=H8KVORM1T7&style=flat)](https://codecov.io/gh/alif898/celadon-theme)
[![Quality Check CI](https://github.com/alif898/celadon-theme/actions/workflows/quality-check-ci.yml/badge.svg)](https://github.com/alif898/celadon-theme/actions/workflows/quality-check-ci.yml)

---

![celadon-icon](templates/pluginIcon.svg)

**Celadon** is a dark IDE theme inspired by the muted, matte finish of classical ceramics. 
It layers cheerful, milky pastels over a deep jade base, 
providing a high-contrast yet eye-friendly environment for long-form coding.
**Celadon** is available for 
[JetBrains IDEs](https://plugins.jetbrains.com/plugin/30354)
and 
[VS Code](https://marketplace.visualstudio.com/items?itemName=alif-naufal.celadon-theme).

## Project Details

For change history, refer to [CHANGELOG.md](CHANGELOG.md).
For sample screenshots, refer to [screenshots](screenshots).

### Project Structure

This project uses a single source of truth for the color palette, defined in `palette.yml`.
The palette, along with Jinja2 templates, are used to generate the theme files for the respective target IDEs.


### Instructions

Firstly, ensure that Python `3.12` and `uv` are installed.

To install the project:
```bash
uv pip install -e .
```

To run the theme generator:
```bash
uv run celadon-theme
```

### Testing

To run unit tests:
```bash
uv run pytest tests
```

To run `mypy` static type checks:
```bash
uv run mypy src tests
```

### CI/CD

CI/CD is performed with GitHub Actions.
On top of unit tests, code coverage is also checked with `codecov` and code quality is checked with `Qodana`.

