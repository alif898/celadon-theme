import json
from pathlib import Path

import pytest
from jinja2 import DictLoader, Environment, select_autoescape

from celadon_theme.generator.windows_terminal import WindowsTerminalGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel


@pytest.fixture
def mock_env() -> Environment:
    return Environment(
        loader=DictLoader(
            {
                "windows-terminal-theme.json.j2": """\
{
  "name": {{ config.name | tojson }},
  "background": "#{{ theme.base }}",
  "foreground": "#{{ theme.text }}"
}
""",
            },
        ),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


@pytest.fixture
def temp_dist_path(tmp_path: Path) -> Path:
    return tmp_path / "windows-terminal"


def test_windows_terminal_generator_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    generator = WindowsTerminalGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )

    generator.generate_theme_files()

    out_file = temp_dist_path / "celadon-windows-terminal.json"
    assert out_file.exists()

    content = json.loads(out_file.read_text())
    assert content["name"] == mock_config.name
    assert content["background"] == f"#{mock_palette.theme['base']}"
    assert content["foreground"] == f"#{mock_palette.theme['text']}"


def test_windows_terminal_generator_escapes_config_name(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    """
    A name with JSON-special characters must be escaped, not injected raw.
    """
    mock_config.name = 'A "quoted" name with \\ backslash\nand a newline'

    generator = WindowsTerminalGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_files()

    content = json.loads((temp_dist_path / "celadon-windows-terminal.json").read_text())
    assert content["name"] == mock_config.name


def test_windows_terminal_generator_metadata_is_noop(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    generator = WindowsTerminalGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )

    generator.generate_theme_metadata()

    # Metadata generation is a no-op: it must not create the dist directory
    assert not temp_dist_path.exists()
