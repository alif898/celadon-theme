from pathlib import Path
from unittest.mock import patch

import pytest
from jinja2 import DictLoader, Environment, select_autoescape

import celadon_theme.generator.vscode as vscode_mod
from celadon_theme.generator.vscode import VsCodeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel


@pytest.fixture
def mock_env() -> Environment:
    return Environment(
        loader=DictLoader(
            {
                "vscode-theme.json.j2": "THEME: {{ config.name }}",
                "vscode-package.json.j2": "PACKAGE: {{ config.version }}",
            }
        ),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


@pytest.fixture
def temp_dist_path(tmp_path: Path) -> Path:
    return tmp_path / "vscode"


def test_vscode_generator_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    generator = VsCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )

    generator.generate_theme_files()

    themes_path = temp_dist_path / "themes"
    assert (themes_path / "celadon-theme-color-theme.json").exists()
    assert (
        themes_path / "celadon-theme-color-theme.json"
    ).read_text() == "THEME: Test Theme"


def test_vscode_generator_metadata(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Create mock README, CHANGELOG, LICENSE, and SVG in a temporary location
    temp_root = temp_dist_path.parent
    changelog_file = temp_root / "CHANGELOG.md"
    changelog_file.write_text("Change Log Content")

    license_file = temp_root / "LICENSE.md"
    license_file.write_text("License Content")

    svg_file = temp_root / "pluginIcon.svg"
    svg_file.write_text(
        '<svg width="10" height="10"><rect width="10" height="10" fill="red"/></svg>'
    )

    monkeypatch.setattr(vscode_mod, "CHANGELOG_FILE", changelog_file)
    monkeypatch.setattr(vscode_mod, "LICENSE_FILE", license_file)
    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", svg_file)

    generator = VsCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    assert (temp_dist_path / "package.json").exists()
    assert (temp_dist_path / "README.md").exists()
    assert (temp_dist_path / "CHANGELOG.md").exists()
    assert (temp_dist_path / "LICENSE.md").exists()
    assert (temp_dist_path / "icon.png").exists()

    assert (temp_dist_path / "package.json").read_text() == "PACKAGE: 1.0.0"
    assert (temp_dist_path / "README.md").read_text() == "Test Description"
    assert (temp_dist_path / "CHANGELOG.md").read_text() == "Change Log Content"
    assert (temp_dist_path / "LICENSE.md").read_text() == "License Content"


def test_vscode_generator_metadata_missing_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Point to non-existent files
    temp_root = temp_dist_path.parent / "non_existent"
    temp_root.mkdir()

    monkeypatch.setattr(vscode_mod, "CHANGELOG_FILE", temp_root / "CHANGELOG.md")
    monkeypatch.setattr(vscode_mod, "LICENSE_FILE", temp_root / "LICENSE.md")
    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", temp_root / "pluginIcon.svg")

    generator = VsCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )

    # Ensure it doesn't throw and gracefully skips
    generator.generate_theme_metadata()


def test_vscode_generator_metadata_no_svg(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Test when svg2rlg returns None
    svg_file = temp_dist_path.parent / "non_existent.svg"
    # We want it to exist but fail to load
    svg_file.write_text("<invalid>svg</invalid>")

    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", svg_file)

    with patch("celadon_theme.generator.vscode.svg2rlg", return_value=None):
        generator = VsCodeGenerator(
            mock_palette, mock_config, mock_env, dist_path=temp_dist_path
        )
        generator.generate_theme_metadata()

    assert not (temp_dist_path / "icon.png").exists()


def test_vscode_generator_readme_prefix(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    mock_config.vscode_description_prefix = "PREFIX"
    generator = VsCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    assert (temp_dist_path / "README.md").read_text() == "PREFIX\nTest Description"
