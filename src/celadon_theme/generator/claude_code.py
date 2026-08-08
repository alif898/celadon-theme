import logging
from pathlib import Path

from jinja2 import Environment

from celadon_theme.config.paths import CLAUDE_CODE_DIR
from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

logger = logging.getLogger(__name__)


class ClaudeCodeGenerator(AbstractThemeGenerator):
    """
    Generator for Claude Code themes.
    """

    def __init__(
        self,
        palette: PaletteModel,
        config: ConfigModel,
        env: Environment,
        dist_path: Path = CLAUDE_CODE_DIR,
    ) -> None:
        super().__init__(palette, config, env)
        self.dist_path = dist_path

    def generate_theme_files(self) -> None:
        """
        Generate the Claude Code theme JSON file.
        """
        logger.info("Generating Claude Code theme files")
        self.dist_path.mkdir(parents=True, exist_ok=True)

        self._render_to_file(
            "claude-code-theme.json.j2", self.dist_path / "celadon-claude-code.json"
        )

        logger.info("Claude Code theme files generated")

    def generate_theme_metadata(self) -> None:
        """
        No-op: Claude Code themes are installed manually, no packaging needed.
        """
        logger.info("Claude Code has no metadata to generate, skipping")
