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
                    "PLUGIN: {{ config.author }}, CHANGES: {{ change_notes_html }}"
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
    assert "PLUGIN: Test Author, CHANGES: Fixes bug" in content
