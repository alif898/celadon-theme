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
        # Named color
        "red",
        # Hash prefix (not allowed by our regex)
        "#123456",
        # Too short
        "123",
        # 5 chars
        "12345",
        # 7 chars
        "1234567",
        # Too long
        "123456789",
        # Non-hex characters
        "GGGGGG",
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
