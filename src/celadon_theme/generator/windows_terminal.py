import logging
from pathlib import Path

from jinja2 import Environment

from celadon_theme.config.paths import WINDOWS_TERMINAL_DIR
from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

logger = logging.getLogger(__name__)


class WindowsTerminalGenerator(AbstractThemeGenerator):
    """
    Generator for Windows Terminal themes.
    """

    def __init__(
        self,
        palette: PaletteModel,
        config: ConfigModel,
        env: Environment,
        dist_path: Path = WINDOWS_TERMINAL_DIR,
    ) -> None:
        super().__init__(palette, config, env)
        self.dist_path = dist_path

    def generate_theme_files(self) -> None:
        """
        Generate the Windows Terminal color scheme JSON file.
        """
        logger.info("Generating %s theme files", self)
        self.dist_path.mkdir(parents=True, exist_ok=True)

        self._render_to_file(
            "windows-terminal-theme.json.j2",
            self.dist_path / "celadon-windows-terminal.json",
        )

        logger.info("%s theme files generated", self)

    def generate_theme_metadata(self) -> None:
        """
        No-op: Windows Terminal themes are installed manually, no packaging needed.
        """
        logger.info("%s has no metadata to generate, skipping", self)
