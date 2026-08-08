import json
from pathlib import Path

import pytest
from jinja2 import DictLoader, Environment, select_autoescape

from celadon_theme.generator.claude_code import ClaudeCodeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel


@pytest.fixture
def mock_env() -> Environment:
    return Environment(
        loader=DictLoader(
            {
                "claude-code-theme.json.j2": """\
{
  "name": {{ config.name | tojson }},
  "base": "dark",
  "overrides": {
    "claude": "#{{ theme.base }}",
    "text": "#{{ theme.text }}"
  }
}
""",
            },
        ),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


@pytest.fixture
def temp_dist_path(tmp_path: Path) -> Path:
    return tmp_path / "claude-code"


def test_claude_code_generator_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    generator = ClaudeCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )

    generator.generate_theme_files()

    out_file = temp_dist_path / "celadon-claude-code.json"
    assert out_file.exists()

    content = json.loads(out_file.read_text())
    assert content["name"] == mock_config.name
    assert content["base"] == "dark"
    assert content["overrides"]["claude"] == f"#{mock_palette.theme['base']}"
    assert content["overrides"]["text"] == f"#{mock_palette.theme['text']}"


def test_claude_code_generator_escapes_config_name(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    """
    A name with JSON-special characters must be escaped, not injected raw.
    """
    mock_config.name = 'A "quoted" name with \\ backslash\nand a newline'

    generator = ClaudeCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_files()

    content = json.loads((temp_dist_path / "celadon-claude-code.json").read_text())
    assert content["name"] == mock_config.name


def test_claude_code_generator_metadata_is_noop(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    generator = ClaudeCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )

    generator.generate_theme_metadata()

    # Metadata generation is a no-op: it must not create the dist directory
    assert not temp_dist_path.exists()
