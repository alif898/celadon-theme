from jinja2 import DictLoader, Environment

from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel


def test_abstract_generator(
    mock_palette: PaletteModel, mock_config: ConfigModel
) -> None:
    class DummyGenerator(AbstractThemeGenerator):
        def generate_theme_files(self) -> None:
            # Call abstract methods to maintain 100% coverage
            # and to satisfy mypy's safe-super, we skip calling super()
            # but we still want to hit the abstract methods in base.py
            # Actually, to hit the code in base.py, we NEED to call them.
            # Let's try to call them via super() but ignore the error if needed,
            # OR just call AbstractThemeGenerator methods directly.
            AbstractThemeGenerator.generate_theme_files(self)

        def generate_theme_metadata(self) -> None:
            AbstractThemeGenerator.generate_theme_metadata(self)

    env = Environment(loader=DictLoader({}), autoescape=True)
    generator = DummyGenerator(mock_palette, mock_config, env)

    assert str(generator) == "DummyGenerator"
    # Call abstract methods which do nothing (pass)
    generator.generate_theme_files()
    generator.generate_theme_metadata()
