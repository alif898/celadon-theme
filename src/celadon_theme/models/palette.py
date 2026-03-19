from typing import Any

from pydantic import BaseModel, ConfigDict


class PaletteModel(BaseModel):
    """
    Flexible model of palette.yml to hold palette colors
    """

    model_config = ConfigDict(extra="allow")
    theme: dict[str, Any]
