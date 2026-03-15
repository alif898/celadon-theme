import logging
import shutil
from pathlib import Path

from jinja2 import Environment
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.config.paths import VSCODE_DIR, README_FILE, CHANGELOG_FILE, LICENSE_FILE, PLUGIN_ICON_SVG
from celadon_theme.models.palette import PaletteModel
from celadon_theme.models.config import ConfigModel


logger = logging.getLogger(__name__)


class VsCodeGenerator(AbstractThemeGenerator):
    """
    Generator for VSCode themes
    """

    def __init__(self, palette: PaletteModel, config: ConfigModel, env: Environment, dist_path: Path = VSCODE_DIR):
        super().__init__(palette, config, env)
        self.dist_path = dist_path
        self.themes_path = self.dist_path / "themes"

    def generate_theme_files(self) -> None:
        """
        Generate core theme files (JSON)
        """
        logger.info("Generating VSCode theme files")
        self.themes_path.mkdir(parents=True, exist_ok=True)

        context = {
            **self.palette.model_dump(),
            "theme": self.palette.theme,
            "config": self.config.model_dump()
        }

        # Theme JSON
        template = self.env.get_template("vscode-theme.json.j2")
        content = template.render(**context)
        out_path = self.themes_path / "celadon-theme-color-theme.json"
        with open(out_path, "w") as f:
            f.write(content)

        logger.info("VSCode theme files generated")

    def generate_theme_metadata(self) -> None:
        """
        Generate metadata (package.json) and copy README/CHANGELOG/LICENSE/Icon
        """
        logger.info("Generating VSCode theme metadata")
        self.dist_path.mkdir(parents=True, exist_ok=True)

        context = {
            **self.palette.model_dump(),
            "theme": self.palette.theme,
            "config": self.config.model_dump()
        }

        # package.json
        template = self.env.get_template("vscode-package.json.j2")
        content = template.render(**context)
        out_path = self.dist_path / "package.json"
        with open(out_path, "w") as f:
            f.write(content)

        # Generate README from config description
        readme_path = self.dist_path / "README.md"
        readme_content = self.config.description
        if self.config.vscode_description_prefix:
            readme_content = f"{self.config.vscode_description_prefix}\n{readme_content}"
            
        with open(readme_path, "w") as f:
            f.write(readme_content)
        
        if CHANGELOG_FILE.exists():
            shutil.copy(CHANGELOG_FILE, self.dist_path / "CHANGELOG.md")

        if LICENSE_FILE.exists():
            shutil.copy(LICENSE_FILE, self.dist_path / "LICENSE.md")

        if PLUGIN_ICON_SVG.exists():
            logger.info(f"Converting {PLUGIN_ICON_SVG} to PNG")
            drawing = svg2rlg(PLUGIN_ICON_SVG)
            
            if drawing is None:
                logger.error(f"Failed to load SVG from {PLUGIN_ICON_SVG}")
                return

            # Ensure minimum resolution of 256x256
            target_size = 256
            scale_x = target_size / drawing.width
            scale_y = target_size / drawing.height
            scale = max(scale_x, scale_y)
            
            drawing.scale(scale, scale)
            drawing.width *= scale
            drawing.height *= scale
            
            renderPM.drawToFile(drawing, str(self.dist_path / "icon.png"), fmt="PNG")

        logger.info("VSCode theme metadata generated")
