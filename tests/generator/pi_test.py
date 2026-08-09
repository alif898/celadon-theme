import json
from pathlib import Path

import pytest
from jinja2 import DictLoader, Environment, select_autoescape

from celadon_theme.generator.pi import PiGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

STUB_TEMPLATE = """\
{
  "name": {{ config.name | tojson }},
  "colors": {
    "accent": "#{{ theme.accent }}",
    "toolSuccessBg": "#{{ theme.tool_bg }}",
    "toolOutput": ""
  }
}
"""


def _build_env() -> Environment:
    """
    Build a stub-template environment for generator-level tests.
    """
    return Environment(
        loader=DictLoader({"pi-theme.json.j2": STUB_TEMPLATE}),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


@pytest.mark.parametrize("tool_bg", ["456789"])
def test_generate_theme_files_accepts_6_digit_palette_colors(
    tool_bg: str,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    palette = PaletteModel(theme={"accent": "123ABC", "tool_bg": tool_bg})
    generator = PiGenerator(
        palette, mock_config, _build_env(), dist_path=tmp_path / "dist"
    )

    generator.generate_theme_files()

    out_file = tmp_path / "dist" / "celadon-pi.json"
    assert out_file.exists()
    content = json.loads(out_file.read_text(encoding="utf-8"))
    assert content["colors"]["toolOutput"] == ""


def test_generate_theme_files_rejects_8_digit_palette_color(
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    palette = PaletteModel(theme={"accent": "123ABC", "tool_bg": "12345678"})
    generator = PiGenerator(
        palette, mock_config, _build_env(), dist_path=tmp_path / "dist"
    )

    with pytest.raises(ValueError, match="toolSuccessBg"):
        generator.generate_theme_files()


@pytest.mark.parametrize("value", ["", "#123abc", "#ABCDEF", 0, 242, 255])
def test_validate_theme_colors_accepts_supported_values(
    value: str | int,
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    generator = PiGenerator(mock_palette, mock_config, _build_env())
    theme_file = tmp_path / "theme.json"
    theme_file.write_text(json.dumps({"colors": {"accent": value}}), encoding="utf-8")

    generator.validate_theme_colors(theme_file)


@pytest.mark.parametrize(
    "value",
    ["#12345678", "#12345", "123456", "not-a-color", -1, 300, True, False],
)
def test_validate_theme_colors_rejects_unsupported_values(
    value: str | int,
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    generator = PiGenerator(mock_palette, mock_config, _build_env())
    theme_file = tmp_path / "theme.json"
    theme_file.write_text(json.dumps({"colors": {"accent": value}}), encoding="utf-8")

    with pytest.raises(ValueError, match="accent"):
        generator.validate_theme_colors(theme_file)


@pytest.mark.parametrize("value", [None, 1.5, ["#123456"], {"r": 0}])
def test_validate_theme_colors_rejects_non_string_values(
    value: object,
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    generator = PiGenerator(mock_palette, mock_config, _build_env())
    theme_file = tmp_path / "theme.json"
    theme_file.write_text(json.dumps({"colors": {"accent": value}}), encoding="utf-8")

    with pytest.raises(ValueError, match="accent"):
        generator.validate_theme_colors(theme_file)
