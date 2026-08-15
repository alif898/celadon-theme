import json
from pathlib import Path

import pytest
from jinja2 import DictLoader, Environment, select_autoescape

from celadon_theme.generator.claude_code import ClaudeCodeGenerator
from celadon_theme.generator.kimi_code import KimiCodeGenerator
from celadon_theme.generator.pi import PiGenerator
from celadon_theme.generator.qwen_code import QwenCodeGenerator
from celadon_theme.generator.single_file import SingleFileThemeGenerator
from celadon_theme.generator.windows_terminal import WindowsTerminalGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

STUB_TEMPLATE = """\
{
  "name": {{ config.name | tojson }},
  "Background": "#{{ theme.base }}",
  "Foreground": "#{{ theme.text }}"
}
"""

SINGLE_FILE_CASES = [
    pytest.param(
        (ClaudeCodeGenerator, "claude-code-theme.json.j2", "celadon-claude-code.json"),
        id="claude-code",
    ),
    pytest.param(
        (QwenCodeGenerator, "qwen-code-theme.json.j2", "celadon-qwen-code.json"),
        id="qwen-code",
    ),
    pytest.param(
        (KimiCodeGenerator, "kimi-code-theme.json.j2", "celadon-kimi-code.json"),
        id="kimi-code",
    ),
    pytest.param(
        (PiGenerator, "pi-theme.json.j2", "celadon-pi.json"),
        id="pi",
    ),
    pytest.param(
        (
            WindowsTerminalGenerator,
            "windows-terminal-theme.json.j2",
            "celadon-windows-terminal.json",
        ),
        id="windows-terminal",
    ),
]


CASE_TYPE = tuple[type[SingleFileThemeGenerator], str, str]


def _build_env(template_name: str) -> Environment:
    return Environment(
        loader=DictLoader({template_name: STUB_TEMPLATE}),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


@pytest.mark.parametrize("case", SINGLE_FILE_CASES)
def test_single_file_generator_files(
    case: CASE_TYPE,
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    generator_cls, template_name, output_file_name = case
    generator = generator_cls(
        mock_palette,
        mock_config,
        _build_env(template_name),
        dist_path=tmp_path / "dist",
    )

    generator.generate_theme_files()

    out_file = tmp_path / "dist" / output_file_name
    assert out_file.exists()

    content = json.loads(out_file.read_text(encoding="utf-8"))
    assert content["name"] == mock_config.name
    assert content["Background"] == f"#{mock_palette.theme['base']}"
    assert content["Foreground"] == f"#{mock_palette.theme['text']}"


@pytest.mark.parametrize("case", SINGLE_FILE_CASES)
def test_single_file_generator_escapes_config_name(
    case: CASE_TYPE,
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A name with JSON-special characters must be escaped, not injected raw.
    """
    generator_cls, template_name, output_file_name = case
    mock_config.name = 'A "quoted" name with \\ backslash\nand a newline'

    generator = generator_cls(
        mock_palette,
        mock_config,
        _build_env(template_name),
        dist_path=tmp_path / "dist",
    )
    generator.generate_theme_files()

    content = json.loads(
        (tmp_path / "dist" / output_file_name).read_text(encoding="utf-8")
    )
    assert content["name"] == mock_config.name


@pytest.mark.parametrize("case", SINGLE_FILE_CASES)
def test_single_file_generator_metadata_is_noop(
    case: CASE_TYPE,
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    generator_cls, template_name, output_file_name = case
    generator = generator_cls(
        mock_palette,
        mock_config,
        _build_env(template_name),
        dist_path=tmp_path / "dist",
    )

    assert generator.template_name == template_name
    assert generator.output_file_name == output_file_name

    generator.generate_theme_metadata()

    # Metadata generation is a no-op. It must not create the dist directory.
    assert not (tmp_path / "dist").exists()


def test_single_file_generator_skips_name_check_when_disabled(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A generator with validate_name=False must accept a theme without a
    name key. Targets such as OpenCode derive the theme name from the
    file name, and their schema forbids extra top-level properties.
    """
    template = '{\n  "Background": "#{{ theme.base }}"\n}'
    env = Environment(
        loader=DictLoader({"opencode-theme.json.j2": template}),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )

    class NoNameThemeGenerator(SingleFileThemeGenerator):
        template_name = "opencode-theme.json.j2"
        output_file_name = "no-name.json"
        dist_dir = tmp_path
        label = "No Name"
        validate_name = False

    generator = NoNameThemeGenerator(
        mock_palette, mock_config, env, dist_path=tmp_path / "dist"
    )
    generator.generate_theme_files()

    content = json.loads(
        (tmp_path / "dist" / "no-name.json").read_text(encoding="utf-8")
    )
    assert content["Background"] == f"#{mock_palette.theme['base']}"


INVALID_TEMPLATE_CASES = [
    pytest.param(
        (
            '{\n  "name": "Wrong Name",\n  "Background": "#{{ theme.base }}"\n}',
            ValueError,
            "expected",
        ),
        id="wrong-name",
    ),
    pytest.param(
        (
            '{\n  "name": {{ config.name | tojson }},\n  "Bad": "#ZZZZZZ"\n}',
            ValueError,
            "#ZZZZZZ",
        ),
        id="invalid-hex",
    ),
    pytest.param(
        ('{\n  "name": {{ config.name | tojson }},', ValueError, "not valid JSON"),
        id="malformed-json",
    ),
    pytest.param(
        ('[\n  "not",\n  "a",\n  "theme"\n]', TypeError, "must be a JSON object"),
        id="non-object-array",
    ),
    pytest.param(
        ('"just a string"', TypeError, "must be a JSON object"),
        id="non-object-string",
    ),
    pytest.param(
        (
            (
                '{\n  "name": {{ config.name | tojson }},\n'
                '  "GradientColors": ["#123456", "#ZZZZZZ"]\n}'
            ),
            ValueError,
            "#ZZZZZZ",
        ),
        id="invalid-hex-in-list",
    ),
]


@pytest.mark.parametrize("case", INVALID_TEMPLATE_CASES)
def test_single_file_generator_rejects_invalid_theme(
    case: tuple[str, type[Exception], str],
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A rendered theme with the wrong name, a non-hex color, malformed
    JSON, or a non-object JSON value must abort generation instead of
    shipping a broken theme.
    """
    template, exc_type, match = case
    env = Environment(
        loader=DictLoader({"claude-code-theme.json.j2": template}),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )
    generator = ClaudeCodeGenerator(
        mock_palette, mock_config, env, dist_path=tmp_path / "dist"
    )

    with pytest.raises(exc_type, match=match):
        generator.generate_theme_files()

    # The rendered file is left on disk for inspection; generation aborts after it.
    assert (tmp_path / "dist" / "celadon-claude-code.json").exists()


def test_single_file_generator_accepts_color_lists(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A theme with an array of hex colors (such as Qwen's GradientColors)
    must validate successfully.
    """
    template = (
        '{\n  "name": {{ config.name | tojson }},\n'
        '  "GradientColors": ["#123456", "#ABCDEF"]\n}'
    )
    env = Environment(
        loader=DictLoader({"claude-code-theme.json.j2": template}),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )
    generator = ClaudeCodeGenerator(
        mock_palette, mock_config, env, dist_path=tmp_path / "dist"
    )

    generator.generate_theme_files()

    out_file = tmp_path / "dist" / "celadon-claude-code.json"
    content = json.loads(out_file.read_text(encoding="utf-8"))
    assert content["GradientColors"] == ["#123456", "#ABCDEF"]
