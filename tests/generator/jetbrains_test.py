import json
from pathlib import Path

import pytest
from jinja2 import DictLoader, Environment, FileSystemLoader, select_autoescape

import celadon_theme.generator.jetbrains as jetbrains_mod
from celadon_theme.config.paths import PALETTE_FILE, TEMPLATES_DIR
from celadon_theme.generator.jetbrains import JetBrainsGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel
from celadon_theme.template.parser import ThemeParser


@pytest.fixture
def mock_env() -> Environment:
    return Environment(
        loader=DictLoader(
            {
                "jetbrains.icls.j2": "ICLS: #{{ theme.black }}",
                "jetbrains-theme.json.j2": (
                    "{% if is_islands %}"
                    "ISLANDS: {{ config.name }} (Islands)"
                    "{% else %}"
                    "JSON: {{ config.name }}"
                    "{% endif %}"
                ),
                "jetbrains-gradle.properties.j2": "GRADLE: {{ config.version }}",
                "jetbrains-plugin.xml.j2": (
                    "PLUGIN: {{ config.author }}, CHANGES: {{ change_notes_html }}, "
                    "PROVIDERS: {{ config.id }}|{{ config.id }}.islands"
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
    assert (themes_path / "celadon-islands.theme.json").exists()
    assert (temp_dist_path / "gradle.properties").exists()

    assert (themes_path / "Celadon.xml").read_text() == "ICLS: #000000"
    assert (themes_path / "celadon.theme.json").read_text() == "JSON: Test Theme"
    assert (
        themes_path / "celadon-islands.theme.json"
    ).read_text() == "ISLANDS: Test Theme (Islands)"
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
    # Fallback to config.change_notes by pointing CHANGELOG_FILE to non-existent path
    monkeypatch.setattr(
        jetbrains_mod, "CHANGELOG_FILE", temp_dist_path.parent / "NO_CHANGELOG.md"
    )

    generator = JetBrainsGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    meta_inf_path = temp_dist_path / "src/main/resources/META-INF"
    assert (meta_inf_path / "plugin.xml").exists()
    assert (meta_inf_path / "pluginIcon.svg").exists()

    assert (meta_inf_path / "plugin.xml").read_text() == (
        "PLUGIN: Test Author, CHANGES: Fixes bug, PROVIDERS: test.id|test.id.islands"
    )
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


def test_jetbrains_generator_metadata_uses_changelog_html(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Create a temporary CHANGELOG with Markdown content
    temp_root = temp_dist_path.parent
    changelog_file = temp_root / "CHANGELOG.md"
    changelog_file.write_text(
        "# Changelog\n\n## 1.2.3 - 2026-01-01\n- Added feature X\n- Fixed bug Y\n"
    )

    # Point the generator CHANGELOG_FILE to this temp file
    monkeypatch.setattr(jetbrains_mod, "CHANGELOG_FILE", changelog_file)

    generator = JetBrainsGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    meta_inf_path = temp_dist_path / "src/main/resources/META-INF"
    content = (meta_inf_path / "plugin.xml").read_text()

    # Expect HTML headings/list rendered by markdown-it-py
    assert "<h2>1.2.3 - 2026-01-01</h2>" in content
    assert "<ul>" in content
    assert "<li>Added feature X</li>" in content


def test_jetbrains_generator_metadata_changelog_conversion_failure_falls_back(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    If Markdown-to-HTML conversion fails with a specific exception, the
    generator should not crash and must fall back to config.change_notes.
    """

    # Prepare a temporary CHANGELOG file (it will be read before failing)
    temp_root = temp_dist_path.parent
    changelog_file = temp_root / "CHANGELOG.md"
    changelog_file.write_text("# Changelog\n\nSome content\n")

    # Point the generator's CHANGELOG_FILE to this temp file
    monkeypatch.setattr(jetbrains_mod, "CHANGELOG_FILE", changelog_file)

    # Stub MarkdownIt so that render() raises a ValueError (covered in except)
    class DummyMarkdown:
        def __init__(self, *_: object, **__: object) -> None:  # pragma: no cover
            pass

        def render(self, *_: object, **__: object) -> str:  # always fail
            msg = "conversion failed"
            raise ValueError(msg)

    monkeypatch.setattr(jetbrains_mod, "MarkdownIt", DummyMarkdown)

    generator = JetBrainsGenerator(
        mock_palette, mock_config, mock_env, dist_path=temp_dist_path
    )

    # Should not raise; should fall back to config.change_notes
    generator.generate_theme_metadata()

    meta_inf_path = temp_dist_path / "src/main/resources/META-INF"
    content = (meta_inf_path / "plugin.xml").read_text()
    assert (
        "PLUGIN: Test Author, CHANGES: Fixes bug, PROVIDERS: test.id|test.id.islands"
    ) in content


@pytest.fixture
def production_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


@pytest.fixture
def production_palette() -> PaletteModel:
    return ThemeParser.load_palette(PALETTE_FILE)


def test_jetbrains_islands_theme_json(
    mock_config: ConfigModel,
    production_env: Environment,
    production_palette: PaletteModel,
    temp_dist_path: Path,
) -> None:
    generator = JetBrainsGenerator(
        production_palette, mock_config, production_env, dist_path=temp_dist_path
    )
    generator.generate_theme_files()

    islands_path = (
        temp_dist_path / "src/main/resources/themes/celadon-islands.theme.json"
    )
    classic_path = temp_dist_path / "src/main/resources/themes/celadon.theme.json"
    assert islands_path.exists()

    islands_theme = json.loads(islands_path.read_text(encoding="utf-8"))
    classic_theme = json.loads(classic_path.read_text(encoding="utf-8"))

    assert islands_theme["name"] == "Test Theme (Islands)"
    assert islands_theme["parentTheme"] == "Islands Dark"
    assert islands_theme["editorScheme"] == "/themes/Celadon.xml"
    assert islands_theme["ui"]["Islands"] == 1
    assert islands_theme["ui"]["Island.borderColor"] == "base2"
    assert islands_theme["ui"]["MainWindow.background"] == "base2"
    assert islands_theme["ui"]["EditorTabs.underTabsBorderColor"] == "base2"
    assert islands_theme["ui"]["EditorTabs.borderColor"] == "base0"
    assert islands_theme["ui"]["StatusBar.borderColor"].endswith("00")
    assert islands_theme["ui"]["StatusBar.borderColor"].startswith("#")

    assert "parentTheme" not in classic_theme
    assert "Island.borderColor" not in classic_theme["ui"]
    assert "Islands" not in classic_theme["ui"]


def test_jetbrains_plugin_xml_registers_both_themes(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    production_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    temp_templates_dir = temp_dist_path.parent / "templates"
    temp_templates_dir.mkdir()
    (temp_templates_dir / "pluginIcon.svg").write_text("<svg>Icon</svg>")

    monkeypatch.setattr(jetbrains_mod, "TEMPLATES_DIR", temp_templates_dir)
    monkeypatch.setattr(
        jetbrains_mod, "CHANGELOG_FILE", temp_dist_path.parent / "NO_CHANGELOG.md"
    )

    generator = JetBrainsGenerator(
        mock_palette, mock_config, production_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    plugin_xml = (temp_dist_path / "src/main/resources/META-INF/plugin.xml").read_text(
        encoding="utf-8"
    )
    assert 'since-build="253"' in plugin_xml
    assert 'path="/themes/celadon.theme.json"' in plugin_xml
    assert 'path="/themes/celadon-islands.theme.json"' in plugin_xml
    assert 'id="test.id"' in plugin_xml
    assert 'id="test.id.islands"' in plugin_xml


def test_jetbrains_plugin_description_includes_suffix(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    production_env: Environment,
    temp_dist_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    temp_templates_dir = temp_dist_path.parent / "templates"
    temp_templates_dir.mkdir()
    (temp_templates_dir / "pluginIcon.svg").write_text("<svg>Icon</svg>")

    monkeypatch.setattr(jetbrains_mod, "TEMPLATES_DIR", temp_templates_dir)
    monkeypatch.setattr(
        jetbrains_mod, "CHANGELOG_FILE", temp_dist_path.parent / "NO_CHANGELOG.md"
    )

    generator = JetBrainsGenerator(
        mock_palette, mock_config, production_env, dist_path=temp_dist_path
    )
    generator.generate_theme_metadata()

    plugin_xml = (temp_dist_path / "src/main/resources/META-INF/plugin.xml").read_text(
        encoding="utf-8"
    )
    assert "Test Description" in plugin_xml
    assert "Test Theme (Islands)" in plugin_xml
    assert plugin_xml.index("Test Description") < plugin_xml.index(
        "Test Theme (Islands)"
    )
