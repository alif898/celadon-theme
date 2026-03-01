import json
import yaml
from pathlib import Path
from celadon_theme.template.parser import ThemeParser
from celadon_theme.models.palette import PaletteModel
from celadon_theme.models.config import ConfigModel

def test_theme_parser_load_palette(tmp_path: Path) -> None:
    palette_file = tmp_path / "palette.yml"
    palette_content = {
        "theme": {
            "colors": {"base": "#FFFFFF"},
            "ansi": {"black": "{{ theme.colors.base }}"}
        }
    }
    palette_file.write_text(yaml.dump(palette_content))
    
    palette = ThemeParser.load_palette(palette_file)
    assert isinstance(palette, PaletteModel)
    assert palette.theme["ansi"]["black"] == "#FFFFFF"

def test_theme_parser_load_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_content = {
        "id": "test.id",
        "name": "Test Theme",
        "version": "1.0.0",
        "plugin_name": "Test Plugin",
        "author": "Test Author",
        "description": "Test Description"
    }
    config_file.write_text(json.dumps(config_content))
    
    config = ThemeParser.load_config(config_file)
    assert isinstance(config, ConfigModel)
    assert config.id == "test.id"
