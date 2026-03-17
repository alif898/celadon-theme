import pytest
from celadon_theme.models.palette import PaletteModel
from celadon_theme.models.config import ConfigModel
from celadon_theme.generator.base import AbstractThemeGenerator
from jinja2 import Environment, DictLoader

@pytest.fixture
def mock_palette() -> PaletteModel:
    return PaletteModel(
        theme={
            "colors": {
                "base": "#FFFFFF",
                "text": "#000000"
            },
            "ansi": {
                "black": "#000000",
                "red": "#FF0000"
            }
        }
    )

@pytest.fixture
def mock_config() -> ConfigModel:
    return ConfigModel(
        id="test.id",
        name="Test Theme",
        version="1.0.0",
        short_description="Test Short Description",
        plugin_name="Test Plugin",
        author="Test Author",
        description="Test Description",
        change_notes="Fixes bug"
    )

def test_abstract_generator(mock_palette: PaletteModel, mock_config: ConfigModel) -> None:
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

    env = Environment(loader=DictLoader({}))
    generator = DummyGenerator(mock_palette, mock_config, env)
    
    assert str(generator) == "DummyGenerator"
    # Call abstract methods which do nothing (pass)
    generator.generate_theme_files()
    generator.generate_theme_metadata()
