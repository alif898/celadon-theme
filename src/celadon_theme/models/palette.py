import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict


def validate_hex(v: str) -> str:
    """
    Validate that the color is a 6 or 8 character hex string.
    """
    if not re.fullmatch(r"[0-9a-fA-F]{6}([0-9a-fA-F]{2})?", v):
        msg = f"'{v}' is not a valid hex color"
        raise ValueError(msg)
    return v


HexColor = Annotated[str, AfterValidator(validate_hex)]


class PaletteModel(BaseModel):
    """
    Flexible model of palette.yml to hold palette colors.
    """

    model_config = ConfigDict(extra="allow")
    theme: dict[str, HexColor]
