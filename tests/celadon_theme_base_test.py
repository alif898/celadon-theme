import pytest
from celadon_theme.models.palette import PaletteModel
from celadon_theme.models.config import ConfigModel

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
        plugin_name="Test Plugin",
        author="Test Author",
        description="Test Description"
    )
