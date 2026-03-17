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

For sample screenshots of what the theme looks like, refer to [screenshots](screenshots).

Manual installation can be done by downloading from [GitHub Releases](https://github.com/alif898/celadon-theme/releases),
the `.zip` file is for JetBrains IDEs and the `.vsix` file is for VS Code.

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

To verify the theme generator code, 
unit tests are written with `pytest` and static type checking is performed with `mypy`.

To run unit tests:
```bash
uv run pytest tests
```

To run `mypy` static type checks:
```bash
uv run mypy src tests
```

To verify the validity of the generated theme files for each platform,
there are different commands available for each IDE as part of their respective extension tooling/APIs:
 - JetBrains IDEs: `verifyPlugin`
 - VS Code: `vsce ls` or `vsce package`

To verify the aesthetics and looks of the theme,
a development version of the IDE is launched
and the theme is inspected against a few sample projects covering various file types and languages.

Currently, the sample projects cover the following: 
 - `Java` + `Maven` + `Spring Boot`
 - `Python` + `FastAPI`
 - `TypeScript` + `React` + `Next.js`
 - `.sql`

Note that these projects are not included in the repository.

For JetBrains IDEs, the various individual IDEs for each language are tested.
The configuration and mapping are found in `\jetbrains\build.gradle.kts`.

For VS Code, the various sample projects can be launched from `\vscode\.vscode\launch.json`.

### CI/CD

CI/CD is automated using GitHub Actions to ensure code quality and automated deployment to all platforms.

There are three levels of pipelines:
 - `branch-ci` - Runs on every push to a branch, includes unit tests, static type checks, plugin verifications for target IDEs
 - `quality-check-ci` - Runs on every pull request, includes all branch level checks, but with `codecov` coverage reporting and `Qodana` for code quality checks 
 - `release` - Runs on release, includes all quality checks and deployment to all platforms

The release workflow is triggered manually by creating a new release on GitHub, with a corresponding tag following `SemVer` conventions,
along with the release description.
Subsequently, the workflow will pick up the new version and release description, and modify `config.json` accordingly.
The workflow will then run the theme generator with this new version before publishing the new release to all platforms.
The changelog will also be updated automatically.
