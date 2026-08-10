import logging
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import override

from jinja2 import Environment

from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

logger = logging.getLogger(__name__)


class AbstractThemeGenerator(ABC):
    """
    Abstract class to represent the generator code for a specific target IDE.
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
        Method to generate core theme files.
        """

    @abstractmethod
    def generate_theme_metadata(self) -> None:
        """
        Method to populate theme metadata, such as plugin details, icons, etc.
        """

    @override
    def __repr__(self) -> str:
        return self.__class__.__name__

    def _copy_files_if_exist(self, dest_path: Path, files_to_copy: list[Path]) -> None:
        """
        Copy each file into the destination directory if it exists.
        """
        for src_file in files_to_copy:
            if src_file.exists():
                dest = dest_path / src_file.name
                logger.info("Copying %s to %s", src_file.name, dest.parent)
                shutil.copy(src_file, dest)
                logger.info("Successfully copied %s", src_file.name)
            else:
                logger.warning(
                    "File: %s not found, skipping copy step for %s",
                    src_file.name,
                    self,
                )

    def _render_to_file(
        self, template_name: str, out_path: Path, **extra: object
    ) -> None:
        """
        Render a template to a file using UTF-8 encoding.
        """
        logger.info("Generating %s", out_path.name)
        context = {
            **self.palette.model_dump(),
            "theme": self.palette.theme,
            "config": self.config.model_dump(),
            **extra,
        }
        content = self.env.get_template(template_name).render(**context)
        with out_path.open("w", encoding="utf-8") as f:
            f.write(content)
        logger.info("Successfully generated %s", out_path.name)
