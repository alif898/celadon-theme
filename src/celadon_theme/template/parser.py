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
        logger.info("%s loaded: %s", type(palette_model).__name__, palette_model)
        return palette_model

    @staticmethod
    def load_config(path: Path) -> ConfigModel:
        logger.info("Loading config from %s", path)

        with path.open(encoding="utf-8") as f:
            raw_data = json.load(f)

        config_model = ConfigModel(**raw_data)

        # Long-form description lives in a separate HTML file referenced by
        # config.json, so the JSON itself stays short and diffable.
        if config_model.description_file:
            description_path = path.parent / config_model.description_file
            if not description_path.exists():
                message = (
                    f"Description file '{description_path}' referenced by {path} "
                    "was not found."
                )
                raise FileNotFoundError(message)
            logger.info("Loading description from %s", description_path)
            with description_path.open(encoding="utf-8") as f:
                description = f.read().strip()
            if not description:
                message = (
                    f"Description file '{description_path}' contains no "
                    "description content."
                )
                raise ValueError(message)
            config_model.description = description
        else:
            logger.info("Using description from %s", path)

        logger.info("%s loaded: %s", type(config_model).__name__, config_model)
        return config_model
