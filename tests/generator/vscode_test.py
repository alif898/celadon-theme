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
    assert (themes_path / "celadon-theme-color-theme.json").read_text() == (
        f"THEME: {mock_config.name}"
    )


def test_vscode_generator_metadata(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Create mock README, CHANGELOG, LICENSE, and SVG in a temporary location.
    temp_root = temp_dist_path.parent
    changelog_file = temp_root / "CHANGELOG.md"
    changelog_file.write_text("Change Log Content")

    license_file = temp_root / "LICENSE.md"
    license_file.write_text("License Content")

    svg_file = temp_root / "pluginIcon.svg"
    svg_file.write_text("<svg>icon</svg>")

    monkeypatch.setattr(vscode_mod, "CHANGELOG_FILE", changelog_file)
    monkeypatch.setattr(vscode_mod, "LICENSE_FILE", license_file)
    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", svg_file)

    class FakeDrawing:
        def __init__(self) -> None:
            self.width = 10
            self.height = 10

        def scale(self, sx: float, sy: float) -> None:
            self.width *= sx
            self.height *= sy

    with (
        patch("celadon_theme.generator.vscode.svg2rlg", return_value=FakeDrawing()),
        patch("celadon_theme.generator.vscode.renderPM.drawToFile") as mock_draw,
    ):
        generator = VsCodeGenerator(
            mock_palette, mock_config, mock_env, dist_path=temp_dist_path
        )
        generator.generate_theme_metadata()

    mock_draw.assert_called_once()

    assert (temp_dist_path / "package.json").exists()
    assert (temp_dist_path / "README.md").exists()
    assert (temp_dist_path / "CHANGELOG.md").exists()
    assert (temp_dist_path / "LICENSE.md").exists()

    assert (temp_dist_path / "package.json").read_text() == (
        f"PACKAGE: {mock_config.version}"
    )
    assert (temp_dist_path / "README.md").read_text() == mock_config.description
    assert (temp_dist_path / "CHANGELOG.md").read_text() == "Change Log Content"
    assert (temp_dist_path / "LICENSE.md").read_text() == "License Content"


def test_vscode_generator_metadata_missing_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Point to non-existent files.
    temp_root = temp_dist_path.parent / "non_existent"
    temp_root.mkdir()

    monkeypatch.setattr(vscode_mod, "CHANGELOG_FILE", temp_root / "CHANGELOG.md")
    monkeypatch.setattr(vscode_mod, "LICENSE_FILE", temp_root / "LICENSE.md")
    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", temp_root / "pluginIcon.svg")

    generator = VsCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )

    # Ensure it doesn't throw and gracefully skips.
    generator.generate_theme_metadata()


def test_vscode_generator_metadata_no_svg(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Test when svg2rlg returns None.
    svg_file = temp_dist_path.parent / "non_existent.svg"
    # We want it to exist but fail to load.
    svg_file.write_text("<invalid>svg</invalid>")

    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", svg_file)

    with patch("celadon_theme.generator.vscode.svg2rlg", return_value=None):
        generator = VsCodeGenerator(
            mock_palette, mock_config, mock_env, dist_path=temp_dist_path
        )
        generator.generate_theme_metadata()

    assert not (temp_dist_path / "icon.png").exists()


def test_vscode_generator_metadata_zero_size_svg(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # An SVG with zero width/height must be skipped, not hit a ZeroDivisionError.
    temp_root = temp_dist_path.parent / "non_existent"
    temp_root.mkdir()
    monkeypatch.setattr(vscode_mod, "CHANGELOG_FILE", temp_root / "CHANGELOG.md")
    monkeypatch.setattr(vscode_mod, "LICENSE_FILE", temp_root / "LICENSE.md")
    svg_file = temp_root / "zero.svg"
    svg_file.write_text('<svg width="0" height="10"/>', encoding="utf-8")
    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", svg_file)

    class ZeroDrawing:
        width = 0
        height = 10

        def scale(self, sx: float, sy: float) -> None:
            pass

    with patch("celadon_theme.generator.vscode.svg2rlg", return_value=ZeroDrawing()):
        generator = VsCodeGenerator(
            mock_palette, mock_config, mock_env, dist_path=temp_dist_path
        )
        generator.generate_theme_metadata()

    assert not (temp_dist_path / "icon.png").exists()


def test_vscode_generator_metadata_svg_load_raises(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A raise from svg2rlg must degrade to a skipped icon, not abort metadata.
    temp_root = temp_dist_path.parent / "non_existent"
    temp_root.mkdir()
    monkeypatch.setattr(vscode_mod, "CHANGELOG_FILE", temp_root / "CHANGELOG.md")
    monkeypatch.setattr(vscode_mod, "LICENSE_FILE", temp_root / "LICENSE.md")
    svg_file = temp_root / "broken.svg"
    svg_file.write_text("<svg>broken</svg>", encoding="utf-8")
    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", svg_file)

    with patch(
        "celadon_theme.generator.vscode.svg2rlg",
        side_effect=ValueError("malformed"),
    ):
        generator = VsCodeGenerator(
            mock_palette, mock_config, mock_env, dist_path=temp_dist_path
        )
        generator.generate_theme_metadata()

    assert not (temp_dist_path / "icon.png").exists()


def test_vscode_generator_metadata_png_render_raises(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A raise from renderPM.drawToFile must degrade to a skipped icon,
    # not abort the metadata generation.
    temp_root = temp_dist_path.parent / "non_existent"
    temp_root.mkdir()
    monkeypatch.setattr(vscode_mod, "CHANGELOG_FILE", temp_root / "CHANGELOG.md")
    monkeypatch.setattr(vscode_mod, "LICENSE_FILE", temp_root / "LICENSE.md")
    svg_file = temp_root / "icon.svg"
    svg_file.write_text("<svg>icon</svg>", encoding="utf-8")
    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", svg_file)

    class FakeDrawing:
        def __init__(self) -> None:
            self.width = 10
            self.height = 10

        def scale(self, sx: float, sy: float) -> None:
            self.width *= sx
            self.height *= sy

    with (
        patch("celadon_theme.generator.vscode.svg2rlg", return_value=FakeDrawing()),
        patch(
            "celadon_theme.generator.vscode.renderPM.drawToFile",
            side_effect=OSError("disk full"),
        ),
    ):
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
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Point file constants at non-existent paths so no real repo files are used.
    temp_root = temp_dist_path.parent / "non_existent"
    temp_root.mkdir()
    monkeypatch.setattr(vscode_mod, "CHANGELOG_FILE", temp_root / "CHANGELOG.md")
    monkeypatch.setattr(vscode_mod, "LICENSE_FILE", temp_root / "LICENSE.md")
    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", temp_root / "pluginIcon.svg")

    generator = VsCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    assert (temp_dist_path / "README.md").read_text() == mock_config.description


def test_vscode_generator_readme_screenshot_path(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    # When a screenshot path is provided, the generator should compose
    # a jsDelivr URL pinned to the tag v{version} and prepend it.
    mock_config.vscode_screenshot_path = "screenshots/vscode.png"
    mock_config.version = "1.2.3"
    mock_config.github_url = "https://github.com/alif898/celadon-theme"

    generator = VsCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    readme = (temp_dist_path / "README.md").read_text()
    assert (
        "https://cdn.jsdelivr.net/gh/alif898/celadon-theme@v1.2.3/screenshots/vscode.png"
        in readme
    )
    assert readme.endswith(mock_config.description)


def test_vscode_generator_readme_screenshot_path_version_with_v_prefix(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A version that already starts with "v" must not produce a "vv" tag.
    temp_root = temp_dist_path.parent / "non_existent"
    temp_root.mkdir()
    monkeypatch.setattr(vscode_mod, "CHANGELOG_FILE", temp_root / "CHANGELOG.md")
    monkeypatch.setattr(vscode_mod, "LICENSE_FILE", temp_root / "LICENSE.md")
    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", temp_root / "pluginIcon.svg")

    mock_config.vscode_screenshot_path = "screenshots/vscode.png"
    mock_config.version = "v1.2.3"
    mock_config.github_url = "https://github.com/alif898/celadon-theme"

    generator = VsCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    readme = (temp_dist_path / "README.md").read_text()
    assert "@v1.2.3/screenshots/vscode.png" in readme
    assert "@vv1.2.3" not in readme


def test_vscode_generator_readme_screenshot_path_missing_github_url(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    # With a screenshot path but missing/invalid github_url, the generator
    # should skip adding the prefix and keep README as description only.
    mock_config.vscode_screenshot_path = "screenshots/vscode.png"
    mock_config.version = "9.9.9"
    # Explicitly unset to trigger the skip path.
    mock_config.github_url = ""

    generator = VsCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    readme = (temp_dist_path / "README.md").read_text()
    assert readme == mock_config.description


def test_vscode_generator_readme_screenshot_path_short_github_url(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A github_url with only one path segment cannot be split into owner/repo,
    # so the screenshot prefix must be skipped without crashing.
    temp_root = temp_dist_path.parent / "non_existent"
    temp_root.mkdir()
    monkeypatch.setattr(vscode_mod, "CHANGELOG_FILE", temp_root / "CHANGELOG.md")
    monkeypatch.setattr(vscode_mod, "LICENSE_FILE", temp_root / "LICENSE.md")
    monkeypatch.setattr(vscode_mod, "PLUGIN_ICON_SVG", temp_root / "pluginIcon.svg")

    mock_config.vscode_screenshot_path = "screenshots/vscode.png"
    mock_config.github_url = "https://github.com/alif898"

    generator = VsCodeGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    readme = (temp_dist_path / "README.md").read_text()
    assert readme == mock_config.description
    assert "jsdelivr" not in readme
