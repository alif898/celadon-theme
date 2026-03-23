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

**Stack**

![Python Badge](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=flat)
![uv Badge](https://img.shields.io/badge/uv-DE5FE9?logo=uv&logoColor=fff&style=flat)
![Jinja Badge](https://img.shields.io/badge/Jinja-7E0C1B?logo=jinja&logoColor=fff&style=flat)
![Pydantic Badge](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=fff&style=flat)

**Testing**

![Pytest Badge](https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest&logoColor=fff&style=flat)
![Ty Badge](https://img.shields.io/badge/ty-30173d?style=flat)
![Ruff Badge](https://img.shields.io/badge/Ruff-D7FF64?logo=ruff&logoColor=000&style=flat)

**CI/CD**

![pre-commit Badge](https://img.shields.io/badge/pre--commit-FAB040?logo=precommit&logoColor=fff&style=flat)
![GitHub Actions Badge](https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=githubactions&logoColor=fff&style=flat)
![Codecov Badge](https://img.shields.io/badge/Codecov-F01F7A?logo=codecov&logoColor=fff&style=flat)
![Qodana Badge](https://img.shields.io/badge/Qodana-f95352?style=flat)


This project uses a single source of truth for the color palette, defined in `palette.yml`.
The Python code reads the palette and injects its values into Jinja2 templates found in `/templates` to produce the necessary theme and metadata files for each target IDE.

### Instructions

First, ensure that Python `3.12` and `uv` are installed.
`uv` is used for fast, reproducible dependency management.

To install/sync the project:
```bash
uv sync

# To also install pre-commit hooks
uv run pre-commit install
```

To run the theme generator:
```bash
uv run celadon-theme
```

### Testing

#### Code Quality
To verify the theme generator code, 
unit tests are run with `pytest`,
static type checking is performed with `ty`
and linting/formatting is done with `ruff`.
`ty` was chosen over `mypy` for its speed and for its ease of use with `uv`.

All of these steps are run within the pre-commit hook, as well as on the CI/CD pipeline.
To run the pre-commit hook manually:
```bash
uv run pre-commit run --all-files --verbose
```
It is also possible to run the individual steps separately, as shown below.

To run linter:
```bash
uv run ruff check

# To summarize results
uv run ruff check --statistics

# To apply fixes
uv run ruff check --fix   
```

To run formatter:
```bash
uv run ruff format

# To preview changes
uv run ruff format --diff
```

To run static type checks:
```bash
uv run ty check
```

To run unit tests:
```bash
uv run pytest
```

#### Plugin Verification

To verify the validity of the generated theme files for each platform,
there are different commands available for each IDE as part of their respective extension tooling/APIs:
 - JetBrains IDEs: `./gradlew verifyPlugin`
 - VS Code: `vsce ls` or `vsce package`

These commands can be run within the respective subfolder of each IDE and are also included in the CI/CD workflows.

#### Visual Inspection

To verify the aesthetics and looks of the theme,
a development version of the IDE is launched
and the theme is inspected against several sample projects covering various file types and languages.

Currently, the sample projects cover the following: 
 - `Java` + `Maven` + `Spring Boot`
 - `Python` + `FastAPI`
 - `TypeScript` + `React` + `Next.js`
 - `.sql`

These projects are not included in this repository as they are placeholder codebases that serve no purpose beyond providing syntax highlighting coverage.

For JetBrains IDEs, the various individual IDEs for each language are tested.
The configuration and mapping are found in `/jetbrains/build.gradle.kts`.

For VS Code, the various sample projects can be launched from `/vscode/.vscode/launch.json`.

### CI/CD

CI/CD is automated using GitHub Actions to ensure code quality and automated deployment to all platforms.
This is supported with a pre-commit hook, that will run linting/formatting checks, static type checks, and unit tests.

There are three levels of workflow:
 - `branch-ci` - Runs on every push to a branch, includes the same basic checks as the pre-commit hook but with additional plugin verifications for target IDEs
 - `quality-check-ci` - Runs on every pull request, includes all branch level checks, but with `codecov` coverage reporting and `Qodana` for code quality checks 
 - `release` - Runs on release, includes all quality checks and deployment to all platforms

The release workflow is triggered manually by creating a new release on GitHub, with a corresponding tag following `SemVer` conventions,
along with the release description.
Subsequently, the workflow will pick up the new version and release description, and modify `config.json` accordingly.
The workflow will then run the theme generator with this new version before publishing the new release to all platforms.
The changelog will also be updated automatically.
