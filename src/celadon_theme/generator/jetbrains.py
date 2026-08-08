import logging
import shutil
from pathlib import Path

from jinja2 import Environment
from markdown_it import MarkdownIt

from celadon_theme.config.paths import (
    CHANGELOG_FILE,
    JETBRAINS_DIR,
    TEMPLATES_DIR,
)
from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

logger = logging.getLogger(__name__)


class JetBrainsGenerator(AbstractThemeGenerator):
    """
    Generator for JetBrains IDEs.
    """

    def __init__(
        self,
        palette: PaletteModel,
        config: ConfigModel,
        env: Environment,
        dist_path: Path = JETBRAINS_DIR,
    ) -> None:
        super().__init__(palette, config, env)
        self.dist_path = dist_path
        self.resources_path = self.dist_path / "src/main/resources"
        self.themes_path = self.resources_path / "themes"
        self.meta_inf_path = self.resources_path / "META-INF"

    def generate_theme_files(self) -> None:
        """
        Generate core theme files (XML and JSON).
        """
        logger.info("Generating JetBrains theme files")
        self.dist_path.mkdir(parents=True, exist_ok=True)
        self.themes_path.mkdir(parents=True, exist_ok=True)

        self._render_to_file("jetbrains.icls.j2", self.themes_path / "Celadon.xml")

        theme_json_outputs = (
            ("celadon.theme.json", False),
            ("celadon-islands.theme.json", True),
        )
        for output_name, is_islands in theme_json_outputs:
            self._render_to_file(
                "jetbrains-theme.json.j2",
                self.themes_path / output_name,
                is_islands=is_islands,
            )

        # Project files
        self._render_to_file(
            "jetbrains-gradle.properties.j2", self.dist_path / "gradle.properties"
        )

        logger.info("JetBrains theme files generated")

    def generate_theme_metadata(self) -> None:
        """
        Generate metadata (plugin.xml) and copy icons.
        """
        logger.info("Generating JetBrains theme metadata")
        self.meta_inf_path.mkdir(parents=True, exist_ok=True)

        # Prepare change notes from CHANGELOG.md as HTML for JetBrains plugin.xml
        # If unavailable, fall back to config.change_notes
        change_notes_html = None
        try:
            if CHANGELOG_FILE.exists():
                logger.info("Converting CHANGELOG.md to HTML for change notes")
                md = MarkdownIt("commonmark")
                # Read whole changelog, JetBrains supports long HTML inside CDATA
                with CHANGELOG_FILE.open(encoding="utf-8") as f:
                    changelog_md = f.read()
                change_notes_html = md.render(changelog_md)
                logger.info("Successfully converted CHANGELOG.md to HTML")
            else:
                logger.warning(
                    "File: %s not found, skipping changelog HTML conversion for %s",
                    CHANGELOG_FILE.name,
                    self,
                )
        except (OSError, ValueError) as exc:
            # Do not fail generation purely due to changelog conversion
            logger.warning(
                "Failed to convert CHANGELOG.md to HTML due to error: %s",
                exc,
            )

        fallback_notes = self.config.change_notes
        change_notes_html = change_notes_html or fallback_notes or ""

        # plugin.xml
        plugin_xml = self.meta_inf_path / "plugin.xml"
        self._render_to_file(
            "jetbrains-plugin.xml.j2",
            plugin_xml,
            change_notes_html=change_notes_html,
        )

        # Static assets
        icon_file = "pluginIcon.svg"
        icon_src = TEMPLATES_DIR / icon_file
        icon_dest = self.meta_inf_path / icon_file
        if icon_src.exists():
            logger.info("Copying %s to %s", icon_src.name, icon_dest.parent)
            shutil.copy(icon_src, icon_dest)
            logger.info("Successfully copied %s", icon_file)
        else:
            logger.warning(
                "File: %s not found, skipping copy step for %s",
                icon_src.name,
                self,
            )

        logger.info("JetBrains theme metadata generated")
