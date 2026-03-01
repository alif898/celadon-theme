import json
import yaml
import logging
from pathlib import Path
from jinja2 import Template
from celadon_theme.models.palette import PaletteModel
from celadon_theme.models.config import ConfigModel


logger = logging.getLogger(__name__)


class ThemeParser:
    """
    Parser for palette and config
    """

    @staticmethod
    def load_palette(path: Path) -> PaletteModel:
        logger.info(f"Loading palette from {path}")

        with open(path, "r") as f:
            raw_data = yaml.safe_load(f)

        # Resolve internal YAML references
        logger.info(f"Resolving internal YAML references for {path}")
        yaml_as_str = yaml.dump(raw_data)
        resolved_str = Template(yaml_as_str).render(**raw_data)
        resolved_data = yaml.safe_load(resolved_str)

        palette_model = PaletteModel(**resolved_data)
        logger.info(f"PaletteModel loaded: {palette_model}")
        return palette_model

    @staticmethod
    def load_config(path: Path) -> ConfigModel:
        logger.info(f"Loading config from {path}")

        with open(path, "r") as f:
            raw_data = json.load(f)

        config_model = ConfigModel(**raw_data)
        logger.info(f"ConfigModel loaded: {config_model}")
        return config_model
