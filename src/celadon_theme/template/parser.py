import json
import logging
from pathlib import Path

import yaml

from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

logger = logging.getLogger(__name__)


class ThemeParser:
    """
    Parser for palette.yml and config.json.
    """

    @staticmethod
    def load_palette(path: Path) -> PaletteModel:
        logger.info("Loading palette from %s", path)

        with path.open(encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)

        palette_model = PaletteModel(**raw_data)
        logger.info("PaletteModel loaded: %s", palette_model)
        return palette_model

    @staticmethod
    def load_config(path: Path) -> ConfigModel:
        logger.info("Loading config from %s", path)

        with path.open(encoding="utf-8") as f:
            raw_data = json.load(f)

        config_model = ConfigModel(**raw_data)
        logger.info("ConfigModel loaded: %s", config_model)
        return config_model
