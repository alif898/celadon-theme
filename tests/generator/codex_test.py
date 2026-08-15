import json
import plistlib
from pathlib import Path

import pytest
from jinja2 import DictLoader, Environment, select_autoescape

from celadon_theme.generator.codex import CodexGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

# Stub token rules rendered into the VS Code theme stub. Tests derive their
# expectations from this data instead of hardcoding scopes or colors, so the
# assertions follow any change to the stub mappings.
STUB_TOKEN_RULES = [
    {
        "name": "Stub: Strings",
        "scope": ["string", "string.quoted"],
        "color": "red",
    },
    {
        "name": "Stub: Comments",
        "scope": ["comment"],
        "color": "base4",
        "font_style": "italic",
    },
]

STUB_TEMPLATE = """\
{
  "name": {{ config.name | tojson }},
  "colors": {"editor.background": "#{{ theme.base0 }}"},
  "tokenColors": __TOKEN_COLORS__
}
"""

STUB_TM_THEME_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
  <key>name</key>
  <string>{{ config.name }}</string>
  <key>settings</key>
  <array>
    <dict>
      <key>settings</key>
      <dict>
        <key>background</key>
        <string>#{{ theme.base0 }}</string>
        <key>foreground</key>
        <string>#{{ theme.base4 }}</string>
      </dict>
    </dict>
{% for rule in token_rules %}
    <dict>
      <key>name</key>
      <string>{{ rule.name }}</string>
{% if rule.scope %}      <key>scope</key>
      <string>{{ rule.scope }}</string>
{% endif %}      <key>settings</key>
      <dict>
{% if rule.font_style is not none %}        <key>fontStyle</key>
        <string>{{ rule.font_style }}</string>
{% endif %}        <key>foreground</key>
        <string>{{ rule.foreground }}</string>
      </dict>
    </dict>
{% endfor %}  </array>
</dict>
</plist>
"""


def _build_stub_template(
    palette: PaletteModel, token_rules: list[dict[str, object]] | None = None
) -> str:
    """
    Build the VS Code theme stub with the token rules spliced in as JSON.
    """
    rules = STUB_TOKEN_RULES if token_rules is None else token_rules
    token_colors = []
    for rule in rules:
        scope = rule.get("scope")
        color = rule.get("color")
        font_style = rule.get("font_style")
        assert isinstance(color, str)
        settings: dict[str, object] = {"foreground": f"#{palette.theme[color]}"}
        if font_style is not None:
            settings["fontStyle"] = font_style
        entry: dict[str, object] = {"name": rule.get("name", ""), "settings": settings}
        if scope is not None:
            entry["scope"] = scope
        token_colors.append(entry)
    return STUB_TEMPLATE.replace("__TOKEN_COLORS__", json.dumps(token_colors, indent=2))


def _build_env(
    template: str = STUB_TEMPLATE,
    tm_theme_template: str = STUB_TM_THEME_TEMPLATE,
) -> Environment:
    return Environment(
        loader=DictLoader(
            {
                "vscode-theme.json.j2": template,
                "codex.tmTheme.j2": tm_theme_template,
            }
        ),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


def _render_tm_theme(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
    token_rules: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """
    Generate the tmTheme into a temp dir and return the parsed plist.
    """
    template = _build_stub_template(mock_palette, token_rules)
    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env(template),
        dist_path=tmp_path / "dist",
    )
    generator.generate_theme_files()

    out_file = tmp_path / "dist" / "celadon.tmTheme"
    assert out_file.exists()

    data = plistlib.loads(out_file.read_bytes())
    assert isinstance(data, dict)
    return data


def _scoped_rule(data: dict[str, object], expected_scope: str) -> dict[str, object]:
    """
    Return the first theme rule matching the expected scope.
    """
    settings = data["settings"]
    assert isinstance(settings, list)
    for rule in settings:
        assert isinstance(rule, dict)
        if rule.get("scope") == expected_scope:
            return rule
    message = f"No rule found for scope {expected_scope!r}"
    raise AssertionError(message)


def test_codex_generator_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    The rendered tmTheme must be a valid plist carrying the token rules and
    the base background.
    """
    data = _render_tm_theme(mock_palette, mock_config, tmp_path)
    settings = data["settings"]
    assert isinstance(settings, list)

    assert data["name"] == mock_config.name

    base_rule = settings[0]
    assert isinstance(base_rule, dict)
    assert "scope" not in base_rule
    base_settings = base_rule["settings"]
    assert isinstance(base_settings, dict)
    assert base_settings["background"] == f"#{mock_palette.theme['base0']}"
    assert base_settings["foreground"] == f"#{mock_palette.theme['base4']}"

    for stub_rule in STUB_TOKEN_RULES:
        scopes = stub_rule["scope"]
        assert isinstance(scopes, list)
        rule = _scoped_rule(data, ", ".join(scopes))
        rule_settings = rule["settings"]
        assert isinstance(rule_settings, dict)
        color = stub_rule["color"]
        assert isinstance(color, str)
        assert rule_settings["foreground"] == f"#{mock_palette.theme[color]}"
        font_style = stub_rule.get("font_style")
        if font_style is not None:
            assert rule_settings["fontStyle"] == font_style


def test_codex_generator_metadata_is_noop(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env(),
        dist_path=tmp_path / "dist",
    )

    generator.generate_theme_metadata()

    # Metadata generation is a no-op. It must not create the dist directory.
    assert not (tmp_path / "dist").exists()


INVALID_TEMPLATE_CASES = [
    pytest.param(
        '{\n  "name": "broken",\n  "tokenColors": [\n    {\n      "scope": ["x"]',
        "not valid JSON",
        id="malformed-json",
    ),
    pytest.param(
        '{\n  "name": "no tokens"\n}',
        "missing the tokenColors array",
        id="missing-token-colors",
    ),
]


@pytest.mark.parametrize(("template", "match"), INVALID_TEMPLATE_CASES)
def test_codex_generator_rejects_invalid_vscode_theme(
    template: str,
    match: str,
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A malformed or token-less VS Code theme must abort generation instead of
    shipping a broken tmTheme.
    """
    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env(template),
        dist_path=tmp_path / "dist",
    )

    with pytest.raises(ValueError, match=match):
        generator.generate_theme_files()


def test_codex_generator_rejects_non_object_theme(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A rendered VS Code theme that is not a JSON object must abort generation.
    """
    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env("[]"),
        dist_path=tmp_path / "dist",
    )

    with pytest.raises(TypeError, match="must be a JSON object"):
        generator.generate_theme_files()


def test_codex_generator_rejects_non_list_token_colors(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A tokenColors value that is not a list must abort generation.
    """
    template = '{\n  "name": "broken",\n  "tokenColors": {}\n}'
    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env(template),
        dist_path=tmp_path / "dist",
    )

    with pytest.raises(TypeError, match="tokenColors must be a list"):
        generator.generate_theme_files()


def test_codex_generator_rejects_non_dict_rule(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A token rule that is not a dictionary must abort generation.
    """
    template = '{\n  "name": "broken",\n  "tokenColors": ["not-a-dict"]\n}'
    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env(template),
        dist_path=tmp_path / "dist",
    )

    with pytest.raises(TypeError, match="token rule must be a dictionary"):
        generator.generate_theme_files()


def test_codex_generator_rejects_non_dict_settings(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A token rule whose settings are not a dictionary must abort generation.
    """
    template = (
        '{\n  "name": "broken",\n  "tokenColors": [\n'
        '    {"name": "bad", "settings": "nope"}\n  ]\n}'
    )
    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env(template),
        dist_path=tmp_path / "dist",
    )

    with pytest.raises(TypeError, match="token settings must be a dictionary"):
        generator.generate_theme_files()


def test_codex_generator_accepts_string_scope(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A token rule whose scope is a single string must render as-is.
    """
    token_rules: list[dict[str, object]] = [
        {"name": "Stub: Plain Scope", "scope": "plain.scope", "color": "red"}
    ]
    data = _render_tm_theme(mock_palette, mock_config, tmp_path, token_rules)

    scope = token_rules[0]["scope"]
    assert isinstance(scope, str)
    rule = _scoped_rule(data, scope)
    rule_settings = rule["settings"]
    assert isinstance(rule_settings, dict)
    color = token_rules[0]["color"]
    assert isinstance(color, str)
    assert rule_settings["foreground"] == f"#{mock_palette.theme[color]}"


def test_codex_generator_preserves_empty_font_style(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A token rule with an explicit empty fontStyle must be carried over as-is.
    """
    token_rules: list[dict[str, object]] = [
        {
            "name": "Stub: No Style",
            "scope": ["plain.scope"],
            "color": "red",
            "font_style": "",
        }
    ]
    data = _render_tm_theme(mock_palette, mock_config, tmp_path, token_rules)

    scopes = token_rules[0]["scope"]
    assert isinstance(scopes, list)
    rule = _scoped_rule(data, ", ".join(scopes))
    rule_settings = rule["settings"]
    assert isinstance(rule_settings, dict)
    assert rule_settings["fontStyle"] == token_rules[0]["font_style"]


def test_codex_generator_omits_scope_for_empty_scope(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A token rule without a scope must not render a match-all scope key.
    """
    token_rules: list[dict[str, object]] = [{"name": "Stub: Unscoped", "color": "red"}]
    data = _render_tm_theme(mock_palette, mock_config, tmp_path, token_rules)

    settings = data["settings"]
    assert isinstance(settings, list)
    unscoped_rules = [rule for rule in settings if "scope" not in rule]
    name = token_rules[0]["name"]
    assert isinstance(name, str)
    assert any(rule.get("name") == name for rule in unscoped_rules)


def test_codex_generator_rejects_invalid_plist(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    An unparseable rendered plist must abort generation with a clear error.
    """

    def broken_loads(_data: bytes) -> object:
        message = "boom"
        raise plistlib.InvalidFileException(message)

    monkeypatch.setattr(plistlib, "loads", broken_loads)

    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env(_build_stub_template(mock_palette)),
        dist_path=tmp_path / "dist",
    )

    with pytest.raises(ValueError, match="not a valid plist"):
        generator.generate_theme_files()


def test_codex_generator_rejects_missing_settings(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A rendered plist without a settings array must abort generation.
    """
    monkeypatch.setattr(plistlib, "loads", lambda _data: {"foo": "bar"})

    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env(_build_stub_template(mock_palette)),
        dist_path=tmp_path / "dist",
    )

    with pytest.raises(ValueError, match="missing the settings array"):
        generator.generate_theme_files()


def test_codex_generator_rejects_non_dict_plist(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A rendered plist that is not a dictionary must abort generation.
    """
    monkeypatch.setattr(plistlib, "loads", lambda _data: [1, 2, 3])

    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env(_build_stub_template(mock_palette)),
        dist_path=tmp_path / "dist",
    )

    with pytest.raises(TypeError, match="must be a plist dictionary"):
        generator.generate_theme_files()


def test_codex_generator_rejects_non_list_settings(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A rendered plist whose settings are not a list must abort generation.
    """
    monkeypatch.setattr(plistlib, "loads", lambda _data: {"settings": "nope"})

    generator = CodexGenerator(
        mock_palette,
        mock_config,
        _build_env(_build_stub_template(mock_palette)),
        dist_path=tmp_path / "dist",
    )

    with pytest.raises(TypeError, match="settings must be a list"):
        generator.generate_theme_files()
