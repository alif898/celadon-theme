import logging
from pathlib import Path

from jinja2 import Environment
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

from celadon_theme.config.paths import (
    CHANGELOG_FILE,
    LICENSE_FILE,
    PLUGIN_ICON_SVG,
    VSCODE_DIR,
)
from celadon_theme.generator.base import AbstractThemeGenerator, compose_screenshot_url
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

logger = logging.getLogger(__name__)

VSCODE_THEME_TEMPLATE = "vscode-theme.json.j2"


class VsCodeGenerator(AbstractThemeGenerator):
    """
    Generator for VSCode.
    """

    def __init__(
        self,
        palette: PaletteModel,
        config: ConfigModel,
        env: Environment,
        dist_path: Path = VSCODE_DIR,
    ) -> None:
        super().__init__(palette, config, env)
        self.dist_path = dist_path
        self.themes_path = self.dist_path / "themes"

    def generate_theme_files(self) -> None:
        """
        Generate core theme files (JSON).
        """
        logger.info("Generating %s theme files", self)
        self.themes_path.mkdir(parents=True, exist_ok=True)

        self._render_to_file(
            VSCODE_THEME_TEMPLATE,
            self.themes_path / "celadon-theme-color-theme.json",
        )

        logger.info("%s theme files generated", self)

    def generate_theme_metadata(self) -> None:
        """
        Generate metadata (package.json) and copy README/CHANGELOG/LICENSE/Icon.
        """
        logger.info("Generating %s theme metadata", self)
        self.dist_path.mkdir(parents=True, exist_ok=True)

        self._render_to_file("vscode-package.json.j2", self.dist_path / "package.json")
        self._generate_readme()
        self._copy_files_if_exist(self.dist_path, [CHANGELOG_FILE, LICENSE_FILE])
        self._generate_icon()

        logger.info("%s theme metadata generated", self)

    def _generate_readme(self) -> None:
        """
        Generate README from config description.
        """
        readme_path = self.dist_path / "README.md"
        readme_content = self.config.description

        # Prepend the version-pinned screenshot image when a URL is available.
        screenshot_url = compose_screenshot_url(self.config)
        if screenshot_url:
            prefix = f"![Theme Preview]({screenshot_url})"
            readme_content = f"{prefix}\n{readme_content}"

        logger.info("Generating %s", readme_path.name)
        with readme_path.open("w", encoding="utf-8") as f:
            f.write(readme_content)
        logger.info("Successfully generated %s", readme_path.name)

    def _generate_icon(self) -> None:
        """
        Convert SVG icon to PNG for VSCode.
        """
        if not PLUGIN_ICON_SVG.exists():
            logger.warning(
                "File: %s not found, skipping icon conversion step for %s",
                PLUGIN_ICON_SVG.name,
                self,
            )
            return

        logger.info("Converting %s to PNG", PLUGIN_ICON_SVG.name)
        try:
            drawing = svg2rlg(PLUGIN_ICON_SVG)
        except (OSError, ValueError, AttributeError):
            logger.exception("Failed to load SVG from %s", PLUGIN_ICON_SVG)
            return

        if drawing is None or not drawing.width or not drawing.height:
            logger.error("Failed to load SVG from %s", PLUGIN_ICON_SVG)
            return

        # Ensure minimum resolution of 256x256.
        target_size = 256
        scale_x = target_size / drawing.width
        scale_y = target_size / drawing.height
        scale = max(scale_x, scale_y)

        drawing.scale(scale, scale)
        drawing.width *= scale
        drawing.height *= scale

        icon_png_path = self.dist_path / "icon.png"
        logger.info("Generating %s", icon_png_path.name)
        try:
            renderPM.drawToFile(drawing, str(icon_png_path), fmt="PNG")
        except (OSError, ValueError):
            logger.exception("Failed to render PNG from %s", PLUGIN_ICON_SVG)
            return
        logger.info("Successfully generated %s", icon_png_path.name)
