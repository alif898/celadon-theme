from pathlib import Path

import pytest
from jinja2 import DictLoader, Environment, select_autoescape

import celadon_theme.generator.jetbrains as jetbrains_mod
from celadon_theme.generator.jetbrains import JetBrainsGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel


@pytest.fixture
def mock_env() -> Environment:
    return Environment(
        loader=DictLoader(
            {
                "celadon.icls.j2": "ICLS: #{{ theme.black }}",
                "celadon.theme.json.j2": "JSON: {{ config.name }}",
                "gradle.properties.j2": "GRADLE: {{ config.version }}",
                "plugin.xml.j2": (
                    "PLUGIN: {{ config.author }}, CHANGES: {{ config.change_notes }}"
                ),
                "pluginIcon.svg": "<svg>Icon</svg>",
            }
        ),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


@pytest.fixture
def temp_dist_path(tmp_path: Path) -> Path:
    return tmp_path / "jetbrains"


def test_jetbrains_generator_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
) -> None:
    generator = JetBrainsGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )

    generator.generate_theme_files()

    themes_path = temp_dist_path / "src/main/resources/themes"
    assert (themes_path / "Celadon.xml").exists()
    assert (themes_path / "celadon.theme.json").exists()
    assert (temp_dist_path / "gradle.properties").exists()

    assert (themes_path / "Celadon.xml").read_text() == "ICLS: #000000"
    assert (themes_path / "celadon.theme.json").read_text() == "JSON: Test Theme"
    assert (temp_dist_path / "gradle.properties").read_text() == "GRADLE: 1.0.0"


def test_jetbrains_generator_metadata(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    temp_templates_dir = temp_dist_path.parent / "templates"
    temp_templates_dir.mkdir()
    (temp_templates_dir / "pluginIcon.svg").write_text("<svg>Icon</svg>")

    monkeypatch.setattr(jetbrains_mod, "TEMPLATES_DIR", temp_templates_dir)

    generator = JetBrainsGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    meta_inf_path = temp_dist_path / "src/main/resources/META-INF"
    assert (meta_inf_path / "plugin.xml").exists()
    assert (meta_inf_path / "pluginIcon.svg").exists()

    assert (
        meta_inf_path / "plugin.xml"
    ).read_text() == "PLUGIN: Test Author, CHANGES: Fixes bug"
    assert (meta_inf_path / "pluginIcon.svg").read_text() == "<svg>Icon</svg>"


def test_jetbrains_generator_metadata_no_icon(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Set an empty templates dir so pluginIcon.svg is not found
    temp_templates_dir = temp_dist_path.parent / "empty_templates"
    temp_templates_dir.mkdir()

    monkeypatch.setattr(jetbrains_mod, "TEMPLATES_DIR", temp_templates_dir)

    generator = JetBrainsGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    # Ensure it doesn't throw and gracefully skips
    generator.generate_theme_metadata()

    meta_inf_path = temp_dist_path / "src/main/resources/META-INF"
    assert not (meta_inf_path / "pluginIcon.svg").exists()
