import logging
from pathlib import Path
from typing import ClassVar

from jinja2 import Environment

from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel


class SingleFileThemeGenerator(AbstractThemeGenerator):
    """
    Base class for targets that ship a single generated theme JSON file.
    """

    template_name: ClassVar[str]
    output_file_name: ClassVar[str]
    dist_dir: ClassVar[Path]

    def __init__(
        self,
        palette: PaletteModel,
        config: ConfigModel,
        env: Environment,
        dist_path: Path | None = None,
    ) -> None:
        super().__init__(palette, config, env)
        self.dist_path = dist_path or self.dist_dir

    @property
    def logger(self) -> logging.Logger:
        """
        Logger named after the concrete generator's module.
        """
        return logging.getLogger(self.__class__.__module__)

    def generate_theme_files(self) -> None:
        """
        Generate the theme JSON file into the dist directory.
        """
        self.logger.info("Generating %s theme files", self)
        self.dist_path.mkdir(parents=True, exist_ok=True)

        self._render_to_file(self.template_name, self.dist_path / self.output_file_name)

        self.logger.info("%s theme files generated", self)

    def generate_theme_metadata(self) -> None:
        """
        No-op. Single-file themes are installed manually and require no packaging.
        """
        self.logger.info("%s has no metadata to generate, skipping", self)
