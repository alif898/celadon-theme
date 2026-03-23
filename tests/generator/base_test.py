from jinja2 import DictLoader, Environment, select_autoescape

from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel


def test_abstract_generator(
    mock_palette: PaletteModel, mock_config: ConfigModel
) -> None:
    class DummyGenerator(AbstractThemeGenerator):
        def generate_theme_files(self) -> None:
            AbstractThemeGenerator.generate_theme_files(self)

        def generate_theme_metadata(self) -> None:
            AbstractThemeGenerator.generate_theme_metadata(self)

    env = Environment(
        loader=DictLoader({}),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )
    generator = DummyGenerator(mock_palette, mock_config, env)

    assert str(generator) == "DummyGenerator"
    # Call abstract methods which do nothing (pass)
    generator.generate_theme_files()
    generator.generate_theme_metadata()
