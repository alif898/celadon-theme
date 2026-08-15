import json
from pathlib import Path

import pytest
from jinja2 import DictLoader, Environment, select_autoescape

from celadon_theme.generator.opencode import OpenCodeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

STUB_TEMPLATE = """\
{
  "$schema": "https://opencode.ai/theme.json",
  "theme": {
    "primary": {"dark": "#{{ theme.base }}", "light": "#{{ theme.base }}"},
    "text": {"dark": "#{{ theme.text }}", "light": "#{{ theme.text }}"}
  }
}
"""


def _build_env(template: str = STUB_TEMPLATE) -> Environment:
    return Environment(
        loader=DictLoader({"opencode-theme.json.j2": template}),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


def test_opencode_generator_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    The rendered theme must be valid JSON without a name key, since
    OpenCode derives the theme name from the file name.
    """
    generator = OpenCodeGenerator(
        mock_palette,
        mock_config,
        _build_env(),
        dist_path=tmp_path / "dist",
    )
    generator.generate_theme_files()

    out_file = tmp_path / "dist" / "celadon-opencode.json"
    assert out_file.exists()

    content = json.loads(out_file.read_text(encoding="utf-8"))
    assert "name" not in content
    assert content["theme"]["primary"] == {
        "dark": f"#{mock_palette.theme['base']}",
        "light": f"#{mock_palette.theme['base']}",
    }
    assert content["theme"]["text"] == {
        "dark": f"#{mock_palette.theme['text']}",
        "light": f"#{mock_palette.theme['text']}",
    }


def test_opencode_generator_metadata_is_noop(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    generator = OpenCodeGenerator(
        mock_palette,
        mock_config,
        _build_env(),
        dist_path=tmp_path / "dist",
    )

    assert generator.template_name == "opencode-theme.json.j2"
    assert generator.output_file_name == "celadon-opencode.json"
    assert generator.validate_name is False

    generator.generate_theme_metadata()

    # Metadata generation is a no-op. It must not create the dist directory.
    assert not (tmp_path / "dist").exists()


INVALID_TEMPLATE_CASES = [
    pytest.param(
        '{\n  "theme": {"primary": "#ZZZZZZ"}\n}',
        "#ZZZZZZ",
        id="invalid-hex",
    ),
    pytest.param(
        '{\n  "theme": {"primary": {"dark": "#123456"',
        "not valid JSON",
        id="malformed-json",
    ),
]


@pytest.mark.parametrize(("template", "match"), INVALID_TEMPLATE_CASES)
def test_opencode_generator_rejects_invalid_theme(
    template: str,
    match: str,
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    tmp_path: Path,
) -> None:
    """
    A rendered theme with a non-hex color or malformed JSON must abort
    generation instead of shipping a broken theme.
    """
    generator = OpenCodeGenerator(
        mock_palette,
        mock_config,
        _build_env(template),
        dist_path=tmp_path / "dist",
    )

    with pytest.raises(ValueError, match=match):
        generator.generate_theme_files()

    # The rendered file is left on disk for inspection; generation aborts after it.
    assert (tmp_path / "dist" / "celadon-opencode.json").exists()
