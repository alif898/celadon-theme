import pytest
from pydantic import ValidationError

from celadon_theme.models.palette import PaletteModel


def test_palette_model_valid() -> None:
    """
    Test PaletteModel with valid hex colors.
    """
    valid_data = {
        "theme": {
            "base0": "1b2222",
            "green_alt2": "75C2B333",
            "white": "FFFFFF",
            "black": "000000FF",
        }
    }
    model = PaletteModel(**valid_data)
    assert model.theme["base0"] == "1b2222"
    assert model.theme["green_alt2"] == "75C2B333"


@pytest.mark.parametrize(
    "invalid_color",
    [
        "red",  # Named color
        "#123456",  # Hash prefix (not allowed by our regex)
        "123",  # Too short
        "12345",  # 5 chars
        "1234567",  # 7 chars
        "123456789",  # Too long
        "GGGGGG",  # Non-hex characters
    ],
)
def test_palette_model_invalid(invalid_color: str) -> None:
    """
    Test PaletteModel with invalid hex colors.
    """
    invalid_data = {"theme": {"color": invalid_color}}
    with pytest.raises(ValidationError) as exc_info:
        PaletteModel(**invalid_data)
    assert f"'{invalid_color}' is not a valid hex color" in str(exc_info.value)
