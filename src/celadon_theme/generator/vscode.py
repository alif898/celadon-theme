import logging
import shutil
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

from celadon_theme.config.paths import (
    CHANGELOG_FILE,
    LICENSE_FILE,
    PLUGIN_ICON_SVG,
    VSCODE_DIR,
)
from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

logger = logging.getLogger(__name__)

MIN_GH_PATH_PARTS = 2


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
        logger.info("Generating VSCode theme files")
        self.themes_path.mkdir(parents=True, exist_ok=True)

        context = {
            **self.palette.model_dump(),
            "theme": self.palette.theme,
            "config": self.config.model_dump(),
        }

        # Theme JSON
        template = self.env.get_template("vscode-theme.json.j2")
        content = template.render(**context)
        out_path = self.themes_path / "celadon-theme-color-theme.json"
        logger.info("Generating %s", out_path.name)
        with out_path.open("w") as f:
            f.write(content)
        logger.info("Successfully generated %s", out_path.name)

        logger.info("VSCode theme files generated")

    def generate_theme_metadata(self) -> None:
        """
        Generate metadata (package.json) and copy README/CHANGELOG/LICENSE/Icon.
        """
        logger.info("Generating VSCode theme metadata")
        self.dist_path.mkdir(parents=True, exist_ok=True)

        context = {
            **self.palette.model_dump(),
            "theme": self.palette.theme,
            "config": self.config.model_dump(),
        }

        self._generate_package_json(context)
        self._generate_readme()
        self._copy_metadata_files()
        self._generate_icon()

        logger.info("VSCode theme metadata generated")

    def _generate_package_json(self, context: dict) -> None:
        """
        Generate package.json for VSCode.
        """
        template = self.env.get_template("vscode-package.json.j2")
        content = template.render(**context)
        out_path = self.dist_path / "package.json"
        logger.info("Generating %s", out_path.name)
        with out_path.open("w") as f:
            f.write(content)
        logger.info("Successfully generated %s", out_path.name)

    def _generate_readme(self) -> None:
        """
        Generate README from config description.
        """
        readme_path = self.dist_path / "README.md"
        readme_content = self.config.description

        # Compose jsDelivr URL from screenshot path + version
        if self.config.vscode_screenshot_path:
            owner: str | None = None
            repo: str | None = None

            if self.config.github_url:
                parsed = urlparse(self.config.github_url)
                parts = [p for p in parsed.path.split("/") if p]
                if len(parts) >= MIN_GH_PATH_PARTS:
                    owner, repo = parts[0], parts[1]
                    logger.info(
                        "Found owner: %s, repo: %s from github_url", owner, repo
                    )

            if owner and repo:
                tag = f"v{self.config.version}"
                cdn_url = (
                    "https://cdn.jsdelivr.net/gh/"
                    f"{owner}/{repo}@{tag}/{self.config.vscode_screenshot_path}"
                )
                logger.info("Composed jsDelivr URL: %s", cdn_url)
                prefix = f"![Theme Preview]({cdn_url})"
                readme_content = f"{prefix}\n{readme_content}"
            else:
                logger.warning(
                    "Skipping screenshot prefix: missing or invalid github_url."
                )

        logger.info("Generating %s", readme_path.name)
        with readme_path.open("w") as f:
            f.write(readme_content)
        logger.info("Successfully generated %s", readme_path.name)

    def _copy_metadata_files(self) -> None:
        """
        Copy CHANGELOG and LICENSE if they exist.
        """
        files_to_copy = [CHANGELOG_FILE, LICENSE_FILE]
        for src_file in files_to_copy:
            if src_file.exists():
                dest = self.dist_path / src_file.name
                logger.info("Copying %s to %s", src_file.name, dest.parent)
                shutil.copy(src_file, dest)
                logger.info("Successfully copied %s", src_file.name)
            else:
                logger.warning(
                    "File: %s not found, skipping copy step for %s",
                    src_file.name,
                    self,
                )

    def _generate_icon(self) -> None:
        """
        Convert SVG icon to PNG for VSCode.
        """
        if PLUGIN_ICON_SVG.exists():
            logger.info("Converting %s to PNG", PLUGIN_ICON_SVG.name)
            drawing = svg2rlg(PLUGIN_ICON_SVG)

            if drawing is None:
                logger.error("Failed to load SVG from %s", PLUGIN_ICON_SVG)
                return

            # Ensure minimum resolution of 256x256
            target_size = 256
            scale_x = target_size / drawing.width
            scale_y = target_size / drawing.height
            scale = max(scale_x, scale_y)

            drawing.scale(scale, scale)
            drawing.width *= scale
            drawing.height *= scale

            icon_png_path = self.dist_path / "icon.png"
            logger.info("Generating %s", icon_png_path.name)
            renderPM.drawToFile(drawing, str(icon_png_path), fmt="PNG")
            logger.info("Successfully generated %s", icon_png_path.name)
        else:
            logger.warning(
                "File: %s not found, skipping icon conversion step for %s",
                PLUGIN_ICON_SVG.name,
                self,
            )
