import logging
from abc import ABC, abstractmethod
from typing import override

from jinja2 import Environment

from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

logger = logging.getLogger(__name__)


class AbstractThemeGenerator(ABC):
    """
    Abstract class to represent the generator code for a specific target IDE
    """

    palette: PaletteModel
    config: ConfigModel
    env: Environment

    def __init__(
        self, palette: PaletteModel, config: ConfigModel, env: Environment
    ) -> None:
        self.palette = palette
        self.config = config
        self.env = env
        logger.info("Initialized %s", self)

    @abstractmethod
    def generate_theme_files(self) -> None:
        """
        Method to generate core theme files
        """

    @abstractmethod
    def generate_theme_metadata(self) -> None:
        """
        Method to populate theme metadata, such as plugin details, icons, etc
        """

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
