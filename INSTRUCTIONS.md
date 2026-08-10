# Celadon Theme Installation Instructions

Instructions for installing Celadon Theme into CLI coding agents and
terminals. The theme files can be obtained from the
[GitHub Releases](https://github.com/alif898/celadon-theme/releases) page or from the
`themes` directory of the `celadon-theme` npm package.

## Claude Code

Place `celadon-claude-code.json` in the `~/.claude/themes` directory
(requires Claude Code v2.1.118 or later), then activate it in Claude Code
with `/theme` and select **Celadon Theme**.

## Pi

Place `celadon-pi.json` in the `~/.pi/agent/themes` directory, then select it
via `/settings` → **Theme** and pick **Celadon Theme**.

## Qwen Code

Paste the contents of `celadon-qwen-code.json` into the `ui.customThemes`
block of `~/.qwen/settings.json`, for example:

```json
{ "ui": { "customThemes": { "Celadon Theme": <paste celadon-qwen-code.json contents here> } } }
```

Then activate it with `/theme` and select **Celadon Theme**. If your
`settings.json` already defines a theme via `ui.theme` (by name or by file
path), remove that setting first. Otherwise `/theme` will not allow switching
themes. Alternatively, set `"theme": "Celadon Theme"` inside the `ui`
object to make it the default.

## Kimi Code

Place `celadon-kimi-code.json` in the `~/.kimi-code/themes` directory (or
`$KIMI_CODE_HOME/themes` if the `KIMI_CODE_HOME` environment variable is
set), then activate it in Kimi Code with `/theme` and select
**Custom: celadon-kimi-code**. Alternatively, set
`theme = "Celadon Theme"` in `tui.toml`.

## Windows Terminal

Copy the contents of `celadon-windows-terminal.json` into the `schemes` array
of `settings.json`, by opening Windows Terminal settings and clicking "Open
JSON file". Then set the scheme in your profile with
`"colorScheme": "Celadon Theme"`.
