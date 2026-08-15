<p align="center">
  <img src="templates/pluginIcon.svg" alt="celadon-icon" width="64">
</p>

<h1 align="center">celadon-theme</h1>

<p align="center">
  <img src="https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/alif898/celadon-theme/main/config.json&query=$.version&label=Version&color=518c83&style=flat" alt="Version">
</p>

<p align="center">
  <a href="https://codecov.io/gh/alif898/celadon-theme"><img src="https://codecov.io/gh/alif898/celadon-theme/graph/badge.svg?style=flat" alt="codecov"></a>
  <a href="https://github.com/alif898/celadon-theme/actions/workflows/quality-check-ci.yml"><img src="https://github.com/alif898/celadon-theme/actions/workflows/quality-check-ci.yml/badge.svg" alt="Quality Check CI"></a>
  <a href="https://socket.dev/npm/package/celadon-theme/overview"><img src="https://badge.socket.dev/npm/package/celadon-theme" alt="Socket"></a>
</p>

<h2 align="center">Download Metrics</h2>

<p align="center">
  <a href="https://plugins.jetbrains.com/plugin/30354"><img src="https://img.shields.io/jetbrains/plugin/d/30354?style=flat&label=JetBrains&color=518c83" alt="JetBrains"></a>
  <a href="https://marketplace.visualstudio.com/items?itemName=alif-naufal.celadon-theme"><img src="https://vsmarketplacebadges.dev/downloads-short/alif-naufal.celadon-theme.svg?color=518c83&subject=VS%20Code" alt="VS Code"></a>
  <a href="https://open-vsx.org/extension/alif-naufal/celadon-theme"><img src="https://img.shields.io/open-vsx/dt/alif-naufal/celadon-theme?style=flat&label=Open%20VSX&color=518c83" alt="Open VSX"></a>
  <a href="https://github.com/alif898/celadon-theme/releases"><img src="https://img.shields.io/github/downloads/alif898/celadon-theme/total?style=flat&label=GitHub%20Direct&color=518c83" alt="GitHub Direct"></a>
  <a href="https://www.npmjs.com/package/celadon-theme"><img src="https://img.shields.io/npm/dt/celadon-theme?style=flat&label=npm&color=518c83" alt="npm"></a>
</p>

<p align="center">
  <a href="https://www.jsdelivr.com/package/gh/alif898/celadon-theme"><img src="https://img.shields.io/jsdelivr/gh/hm/alif898/celadon-theme?style=flat&label=Theme%20Previews&color=518c83" alt="Theme Previews"></a>
</p>

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/alif898/celadon-theme@main/screenshots/vscode.png" alt="Screenshot">
</p>

**Celadon** is a dark IDE/terminal theme inspired by the muted, matte finish of classical ceramics. 
It layers cheerful, milky pastels over a deep jade base, 
providing a high-contrast yet eye-friendly environment for long-form coding.
**Celadon** is available for 
[JetBrains IDEs](https://plugins.jetbrains.com/plugin/30354),
[VS Code](https://marketplace.visualstudio.com/items?itemName=alif-naufal.celadon-theme),
VS Code-based editors (VSCodium, AI-native IDEs: Cursor, Devin, Antigravity)
via the [Open VSX Registry](https://open-vsx.org/extension/alif-naufal/celadon-theme),
CLI coding agents (Claude Code, Pi, Qwen Code, Kimi Code, OpenCode, Codex CLI)
and Windows Terminal, via [npm](https://www.npmjs.com/package/celadon-theme).

## Project Details

For change history, refer to [CHANGELOG.md](CHANGELOG.md).

For sample screenshots of what the theme looks like, refer to [screenshots](screenshots).

### Installation

#### Marketplace

Marketplace installation is available for the following platforms:
 - [JetBrains](https://plugins.jetbrains.com/plugin/30354)
 - [VS Code](https://marketplace.visualstudio.com/items?itemName=alif-naufal.celadon-theme)
 - [Open VSX Registry](https://open-vsx.org/extension/alif-naufal/celadon-theme)
 - [npm](https://www.npmjs.com/package/celadon-theme)

The files needed for the CLI coding agents and Windows Terminal are distributed via npm
and can be installed via various package managers:

| Package manager | Install globally | Install in a project | Run without installing | Where the files land (global install) |
| --- | --- | --- | --- | --- |
| npm | `npm install -g celadon-theme` | `npm install celadon-theme` | `npx -y celadon-theme` | `$(npm root -g)/celadon-theme/themes` |
| yarn 1.x | `yarn global add celadon-theme` | `yarn add celadon-theme` | — | `$(yarn global dir)/node_modules/celadon-theme/themes` |
| yarn 2+ | — | `yarn add celadon-theme` | `yarn dlx celadon-theme` | `node_modules/celadon-theme/themes` (project) |
| pnpm | `pnpm add -g celadon-theme` | `pnpm add celadon-theme` | `pnpm dlx celadon-theme` | `$(pnpm root -g)/celadon-theme/themes` |
| bun | `bun add -g celadon-theme` | `bun add celadon-theme` | `bunx celadon-theme` | `$(bun pm root -g)/celadon-theme/themes` |

The `$(...)` commands print the exact directory on your machine. The paths
above are for global installs while project installs place the files under
`node_modules/celadon-theme/themes`. The "Run without installing" commands
download the package into a cache and will print the theme file locations. In all
cases, run `celadon-theme` to print the exact themes directory, then copy the
files from it to each target as described in
[INSTRUCTIONS.md](INSTRUCTIONS.md).

#### Manual Installation

Manual installation can be done by downloading from [GitHub Releases](https://github.com/alif898/celadon-theme/releases),
the `.zip` file is for JetBrains IDEs,
the `.vsix` file is for VS Code/VS Code-based editors,
the `.tgz` file is the npm package, installable with `npm install -g ./celadon-theme-<version>.tgz`,
the `.json` files are for Claude Code, Pi, Qwen Code, Kimi Code, OpenCode and Windows Terminal,
and the `celadon.tmTheme` file is for the Codex CLI.

For installation instructions for Claude Code, Pi, Qwen Code, Kimi Code, OpenCode, and Windows Terminal,
refer to [INSTRUCTIONS.md](INSTRUCTIONS.md).

### Project Structure

**Core Technologies**

![Python Badge](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=flat)
![uv Badge](https://img.shields.io/badge/uv-DE5FE9?logo=uv&logoColor=fff&style=flat)
![Jinja Badge](https://img.shields.io/badge/Jinja-7E0C1B?logo=jinja&logoColor=fff&style=flat)
![Pydantic Badge](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=fff&style=flat)

**CDN**

![jsDelivr Badge](https://img.shields.io/badge/jsDelivr-E84D3D?logo=jsdelivr&logoColor=fff&style=flat)

**Testing**

![Pytest Badge](https://img.shields.io/badge/Pytest-0A9EDC?logo=pytest&logoColor=fff&style=flat)
![ty Badge](https://img.shields.io/badge/ty-46EBE1?logo=ty&logoColor=000&style=flat)
![Ruff Badge](https://img.shields.io/badge/Ruff-D7FF64?logo=ruff&logoColor=000&style=flat)

**CI/CD**

![pre-commit Badge](https://img.shields.io/badge/pre--commit-FAB040?logo=precommit&logoColor=fff&style=flat)
![GitHub Actions Badge](https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=githubactions&logoColor=fff&style=flat)
![Codecov Badge](https://img.shields.io/badge/Codecov-F01F7A?logo=codecov&logoColor=fff&style=flat)
![CodeRabbit Badge](https://img.shields.io/badge/CodeRabbit-FF570A?logo=coderabbit&logoColor=fff&style=flat)


This project uses a single source of truth for the color palette, defined in `palette.yml`.
The Python code reads the palette and injects its values into Jinja2 templates found in `/templates` to produce the necessary theme and metadata files for each target IDE.

### Running Locally

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

It is also possible to build the final extension files locally for manual installation into the respective IDEs.

For JetBrains:
```bash
cd jetbrains
./gradlew buildPlugin

# Alternatively with below environment variables
# CERTIFICATE_CHAIN, PRIVATE_KEY, PRIVATE_KEY_PASSWORD, PUBLISH_TOKEN
./gradlew signPlugin
```
Output `.zip` file will be located in `jetbrains/build/distributions/celadon-theme-*.zip`.

For VS Code:
```bash
cd vscode
vsce package --no-git-tag-version
```
Output `.vsix` file will be located in `vscode/celadon-theme-*.vsix`.

For Claude Code, Qwen Code, Kimi Code, Windows Terminal, Pi, and OpenCode,
their respective `.json` files will be generated automatically when running the generator 
and can be found in the respective `claude-code`, `qwen-code`, `kimi-code`, `windows-terminal`, `pi`, and `opencode` folders.

The Codex CLI theme is generated as `codex/celadon.tmTheme`.

For the npm package, running the generator also produces the package contents
under `npm/`. To validate and try the package locally:

```bash
cd npm
npm pack --dry-run                     # preview the tarball contents
npm pack                               # build celadon-theme-<version>.tgz
npm install -g ./celadon-theme-<version>.tgz
celadon-theme                          # prints the exact themes directory
```

The same package can be validated with `yarn pack --dry-run`,
`pnpm pack --dry-run`, or `bun pm pack --dry-run`.

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
 - npm: `npm pack --dry-run` (with `yarn pack --dry-run`, `pnpm pack --dry-run`, and `bun pm pack --dry-run` to cover the other package managers)

These commands can be run within the respective subfolder of each target and are also included in the CI/CD workflows.
The `.vsix` file built for VS Code can directly be used for Open VSX Registry too.

#### Visual Inspection

To verify the aesthetics and looks of the theme,
a development/sandbox version of the IDE is launched with the theme loaded
and the theme is inspected against several sample projects covering various file types and languages.

The programming languages and frameworks covered by the sample projects can be seen in [STATS.md](STATS.md).
These projects are not included in this repository as they are placeholder codebases that serve no purpose beyond providing syntax highlighting coverage.
As such, `STATS.md` can only be generated locally, which is done via the generator script itself.

For JetBrains IDEs, the various individual IDEs for each language are tested.
For example, the `Java` project will be tested against IntelliJ, 
while the `Rust` project will be tested against RustRover.
The configuration and mapping are found in `/jetbrains/build.gradle.kts`.

Analogously, the relevant language extensions need to be installed for VS Code.
The various sample projects can be launched from `/vscode/.vscode/launch.json`.
However, depending on the specific language extension, the way it interacts with the theme keys may be inconsistent.

For the JetBrains plugin, it includes variants for both the classic JetBrains layout and the new Islands UI.

For the CLI coding agents, each tool exposes a different set of customizable elements,
therefore the visual feel is not fully consistent from tool to tool.
It is recommended that the Windows Terminal theme be used concurrently,
as they were designed and tested together.

### CI/CD

CI/CD is automated using GitHub Actions to ensure code quality and automated deployment to all platforms.
This is supported with a pre-commit hook that will run linting/formatting checks, static type checks, and unit tests.

There are three levels of workflow:
 - `branch-ci` - Runs on every push to a branch, includes the same basic checks as the pre-commit hook but with additional plugin verifications for target IDEs
 - `quality-check-ci` - Runs on every pull request, includes all branch level checks, but with `uv audit` to scan dependency vulnerabilities, `codecov` for unit test coverage reporting and `CodeRabbit` for AI-generated summary and review 
 - `release` - Runs on release, includes all quality checks and deployment to all platforms

The release workflow is triggered manually by creating a new release on GitHub, with a corresponding tag following `SemVer` conventions,
along with the release description.
Subsequently, the workflow will pick up the new version and release description and modify `config.json` accordingly.
The workflow will then run the theme generator with this new version before publishing the new release to all platforms.
The changelog will also be updated automatically.
