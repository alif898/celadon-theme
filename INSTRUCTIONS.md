# Installation Instructions

These are the instructions for installing Celadon Theme into CLI coding agents and
terminals. The theme files can be obtained from the
[GitHub Releases](https://github.com/alif898/celadon-theme/releases) page or from the
`themes` directory of the `celadon-theme` npm package.

All paths in this document use `~` for your home directory. On Windows, `~`
is `%USERPROFILE%` (usually `C:\Users\<your username>`).

If the npm package is installed, it is also possible to run `celadon-theme` to print the exact directory that
contains the theme files.

## Table of Contents

- [Claude Code](#claude-code)
- [Pi](#pi)
- [Qwen Code](#qwen-code)
- [Kimi Code](#kimi-code)
- [Windows Terminal](#windows-terminal)
- [Troubleshooting](#troubleshooting)

## Claude Code

### Install

Place `celadon-claude-code.json` in the `~/.claude/themes` directory. This
requires Claude Code v2.1.118 or later.

### Activate

Run `/theme` and select **Celadon Theme**.

### Uninstall

Delete `~/.claude/themes/celadon-claude-code.json`.

## Pi

### Install

Place `celadon-pi.json` in the `~/.pi/agent/themes` directory.

### Activate

Run `/settings` → **Theme** and pick **Celadon Theme**.

### Uninstall

Delete `~/.pi/agent/themes/celadon-pi.json`.

## Qwen Code

### Install

Paste the contents of `celadon-qwen-code.json` into the `ui.customThemes` block
of `~/.qwen/settings.json`, for example:

```json
{ "ui": { "customThemes": { "Celadon Theme": <paste celadon-qwen-code.json contents here> } } }
```

If your `settings.json` already defines a theme via `ui.theme` (by name or by
file path), remove that setting first. Otherwise `/theme` will not allow
switching themes.

### Activate

Run `/theme` and select **Celadon Theme**. Alternatively, set
`"theme": "Celadon Theme"` inside the `ui` object to make it the default.

### Uninstall

Remove the `"Celadon Theme"` entry from the `ui.customThemes` block. If you
removed a `ui.theme` setting to install the theme, restore it.

## Kimi Code

### Install

Place `celadon-kimi-code.json` in the `~/.kimi-code/themes` directory (or
`$KIMI_CODE_HOME/themes` if the `KIMI_CODE_HOME` environment variable is set).

### Activate

Run `/theme` and select **Custom: celadon-kimi-code**. Alternatively, set
`theme = "Celadon Theme"` in `tui.toml`.

### Uninstall

Delete `~/.kimi-code/themes/celadon-kimi-code.json`. If you set the theme via
`tui.toml`, remove or reset the `theme` entry.

## Windows Terminal

### Install

Open Windows Terminal settings and click "Open JSON file". Copy the contents
of `celadon-windows-terminal.json` into the `schemes` array of `settings.json`.

The scheme is applied with a `colorScheme` setting that must match the scheme
`name` (`Celadon Theme`) inside the pasted JSON. Add
`"colorScheme": "Celadon Theme"` to `profiles.defaults` to apply it to every
profile, or to a single profile's entry in `profiles.list` to apply it there.

### Activate

No further action is needed. Windows Terminal reloads `settings.json`
automatically; open a new tab to see the scheme.

### Uninstall

Remove the `Celadon Theme` entry from the `schemes` array and delete the
`"colorScheme": "Celadon Theme"` line from the profiles that use it.

## Troubleshooting

- **The theme does not appear in `/theme`**: The file is in the wrong
  directory, or the app was started before the file was placed there. Restart
  the app and try again. For Claude Code, make sure the version is v2.1.118
  or later.
- **Settings did not change after editing `settings.json`**: The file must
  stay valid JSON. A trailing comma or a missing brace breaks parsing;
  Windows Terminal keeps its last valid settings when parsing fails. Check
  the file for errors.

If you are facing any other difficulty using the theme 
or have any feedback,
do visit this project's [GitHub](https://github.com/alif898/celadon-theme) page and raise an issue.
