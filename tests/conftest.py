import pytest

from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel


@pytest.fixture
def mock_palette() -> PaletteModel:
    return PaletteModel(
        theme={
            "base": "FFFFFF",
            "text": "000000",
            "black": "000000",
            "red": "FF0000",
        },
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
        change_notes="Fixes bug",
    )
