import logging
import shutil
from pathlib import Path

from jinja2 import Environment

from celadon_theme.config.paths import (
    CHANGELOG_FILE,
    INSTRUCTIONS_FILE,
    LICENSE_FILE,
    NPM_DIR,
)
from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.generator.claude_code import ClaudeCodeGenerator
from celadon_theme.generator.kimi_code import KimiCodeGenerator
from celadon_theme.generator.pi import PiGenerator
from celadon_theme.generator.qwen_code import QwenCodeGenerator
from celadon_theme.generator.single_file import SingleFileThemeGenerator
from celadon_theme.generator.windows_terminal import WindowsTerminalGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

logger = logging.getLogger(__name__)

# Single-file generators whose themes ship in the npm package. Their
# output_file_name, dist_dir, and label attributes are the single source of
# truth for the package contents.
SINGLE_FILE_THEME_GENERATORS: tuple[type[SingleFileThemeGenerator], ...] = (
    ClaudeCodeGenerator,
    QwenCodeGenerator,
    KimiCodeGenerator,
    PiGenerator,
    WindowsTerminalGenerator,
)

# Map of theme file name to the single-file dist directory that produces it.
THEME_SOURCE_FILES: dict[str, Path] = {
    generator_cls.output_file_name: generator_cls.dist_dir
    for generator_cls in SINGLE_FILE_THEME_GENERATORS
}

# Pairs of theme file name and target label, rendered into the package README.
THEME_TARGETS: list[tuple[str, str]] = [
    (generator_cls.output_file_name, generator_cls.label)
    for generator_cls in SINGLE_FILE_THEME_GENERATORS
]


class NpmGenerator(AbstractThemeGenerator):
    """
    Generator for the npm package that ships CLI agent and terminal themes.
    """

    def __init__(
        self,
        palette: PaletteModel,
        config: ConfigModel,
        env: Environment,
        dist_path: Path = NPM_DIR,
    ) -> None:
        super().__init__(palette, config, env)
        self.dist_path = dist_path
        self.themes_path = self.dist_path / "themes"

    def generate_theme_files(self) -> None:
        """
        Copy the generated single-file themes into the npm package.
        """
        logger.info("Generating %s theme files", self)
        self.themes_path.mkdir(parents=True, exist_ok=True)

        # Remove stale theme files left over from previous generations.
        for stale in self.themes_path.glob("*.json"):
            if stale.name not in THEME_SOURCE_FILES:
                stale.unlink()

        for file_name, source_dir in THEME_SOURCE_FILES.items():
            source = source_dir / file_name
            if not source.is_file():
                message = f"Required theme file not found: {source}"
                raise FileNotFoundError(message)
            shutil.copy(source, self.themes_path / file_name)

        logger.info("%s theme files generated", self)

    def generate_theme_metadata(self) -> None:
        """
        Render package metadata and copy instructions, README, and LICENSE.
        """
        logger.info("Generating %s theme metadata", self)
        self.dist_path.mkdir(parents=True, exist_ok=True)

        self._render_to_file("npm-package.json.j2", self.dist_path / "package.json")
        self._render_to_file(
            "npm-README.md.j2",
            self.dist_path / "README.md",
            theme_targets=THEME_TARGETS,
        )
        self._copy_files_if_exist(
            self.dist_path, [INSTRUCTIONS_FILE, CHANGELOG_FILE, LICENSE_FILE]
        )

        logger.info("%s theme metadata generated", self)
