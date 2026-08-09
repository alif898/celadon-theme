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

    content = json.loads(out_file.read_text())
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

    content = json.loads((tmp_path / "dist" / output_file_name).read_text())
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
