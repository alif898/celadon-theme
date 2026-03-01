from pydantic import BaseModel, ConfigDict
from typing import Any


class PaletteModel(BaseModel):
    """
    Flexible model to hold palette colors
    """
    model_config = ConfigDict(extra="allow")
    theme: dict[str, Any]
