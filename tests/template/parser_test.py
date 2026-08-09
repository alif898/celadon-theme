import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel
from celadon_theme.template.parser import ThemeParser


def test_theme_parser_load_palette(tmp_path: Path) -> None:
    palette_file = tmp_path / "palette.yml"
    # YAML anchors/aliases resolve natively via yaml.safe_load.
    palette_file.write_text(
        "theme:\n  base: &base_color 'FFFFFF'\n  black: *base_color\n"
    )

    palette = ThemeParser.load_palette(palette_file)
    assert isinstance(palette, PaletteModel)
    assert palette.theme["black"] == "FFFFFF"


def test_theme_parser_load_palette_rejects_jinja_literal(tmp_path: Path) -> None:
    # Jinja {{ }} placeholders in palette.yml are no longer resolved and must
    # fail validation instead of silently resolving to an empty string.
    palette_file = tmp_path / "palette.yml"
    palette_file.write_text("theme:\n  base: 'FFFFFF'\n  black: '{{ theme.base }}'\n")

    with pytest.raises(ValidationError):
        ThemeParser.load_palette(palette_file)


def test_theme_parser_load_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_content = {
        "id": "test.id",
        "name": "Test Theme",
        "version": "1.0.0",
        "short_description": "Test Short Description",
        "plugin_name": "Test Plugin",
        "author": "Test Author",
        "description": "Test Description",
    }
    config_file.write_text(json.dumps(config_content))

    config = ThemeParser.load_config(config_file)
    assert isinstance(config, ConfigModel)
    assert config.id == "test.id"
    assert config.jetbrains_description_suffix == ""


def test_theme_parser_load_config_utf8(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_content = {
        "id": "test.id",
        "name": "Test Theme",
        "version": "1.0.0",
        "short_description": "Test Short Description",
        "plugin_name": "Test Plugin",
        "author": "Test Author",
        "description": "Café: theme",
    }
    # ensure_ascii=False keeps raw UTF-8 bytes in the file.
    config_file.write_text(
        json.dumps(config_content, ensure_ascii=False), encoding="utf-8"
    )

    config = ThemeParser.load_config(config_file)
    assert config.description == "Café: theme"


def test_theme_parser_load_palette_missing_theme(tmp_path: Path) -> None:
    palette_file = tmp_path / "palette.yml"
    palette_file.write_text(yaml.dump({"meta": {"name": "celadon"}}))

    with pytest.raises(ValidationError):
        ThemeParser.load_palette(palette_file)


def test_theme_parser_load_config_with_jetbrains_description_suffix(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "config.json"
    suffix = "<p>Islands variant promo.</p>"
    config_file.write_text(
        json.dumps(
            {
                "id": "test.id",
                "name": "Test Theme",
                "version": "1.0.0",
                "short_description": "Test Short Description",
                "plugin_name": "Test Plugin",
                "author": "Test Author",
                "description": "Test Description",
                "jetbrains_description_suffix": suffix,
            }
        )
    )

    config = ThemeParser.load_config(config_file)
    assert config.jetbrains_description_suffix == suffix


def test_theme_parser_load_config_with_description_file(tmp_path: Path) -> None:
    description_dir = tmp_path / "templates"
    description_dir.mkdir()
    description_file = description_dir / "description.html"
    description_file.write_text("<p>Test Description</p>\n", encoding="utf-8")
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "id": "test.id",
                "name": "Test Theme",
                "version": "1.0.0",
                "short_description": "Test Short Description",
                "plugin_name": "Test Plugin",
                "author": "Test Author",
                "description_file": f"templates/{description_file.name}",
            }
        )
    )

    config = ThemeParser.load_config(config_file)
    assert config.description_file == f"templates/{description_file.name}"
    assert config.description == "<p>Test Description</p>"


def test_theme_parser_load_config_description_file_overrides_inline(
    tmp_path: Path,
) -> None:
    description_file = tmp_path / "description.html"
    description_file.write_text("<p>From File</p>", encoding="utf-8")
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "id": "test.id",
                "name": "Test Theme",
                "version": "1.0.0",
                "short_description": "Test Short Description",
                "plugin_name": "Test Plugin",
                "author": "Test Author",
                "description": "Inline Description",
                "description_file": description_file.name,
            }
        )
    )

    config = ThemeParser.load_config(config_file)
    assert config.description == "<p>From File</p>"


def test_theme_parser_load_config_with_missing_description_file(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "id": "test.id",
                "name": "Test Theme",
                "version": "1.0.0",
                "short_description": "Test Short Description",
                "plugin_name": "Test Plugin",
                "author": "Test Author",
                "description_file": "missing.html",
            }
        )
    )

    with pytest.raises(FileNotFoundError):
        ThemeParser.load_config(config_file)


def test_theme_parser_load_config_rejects_whitespace_only_description_file(
    tmp_path: Path,
) -> None:
    description_file = tmp_path / "description.html"
    description_file.write_text("   \n\t  \n", encoding="utf-8")
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "id": "test.id",
                "name": "Test Theme",
                "version": "1.0.0",
                "short_description": "Test Short Description",
                "plugin_name": "Test Plugin",
                "author": "Test Author",
                "description_file": description_file.name,
            }
        )
    )

    with pytest.raises(ValueError, match="contains no description content"):
        ThemeParser.load_config(config_file)
