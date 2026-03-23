import logging
import shutil
from pathlib import Path

from jinja2 import Environment

from celadon_theme.config.paths import JETBRAINS_DIR, TEMPLATES_DIR
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
        self.themes_path.mkdir(parents=True, exist_ok=True)

        context = {
            **self.palette.model_dump(),
            "config": self.config.model_dump(),
        }

        files = {
            "celadon.icls.j2": self.themes_path / "Celadon.xml",
            "celadon.theme.json.j2": self.themes_path / "celadon.theme.json",
        }

        for tpl_name, out_path in files.items():
            logger.info("Generating %s", out_path.name)
            template = self.env.get_template(tpl_name)
            content = template.render(**context)
            with out_path.open("w") as f:
                f.write(content)
            logger.info("Successfully generated %s", out_path.name)

        # Project files
        gradle_props = self.dist_path / "gradle.properties"
        logger.info("Generating %s", gradle_props.name)
        template = self.env.get_template("gradle.properties.j2")
        content = template.render(**context)
        with gradle_props.open("w") as f:
            f.write(content)
        logger.info("Successfully generated %s", gradle_props.name)

        logger.info("JetBrains theme files generated")

    def generate_theme_metadata(self) -> None:
        """
        Generate metadata (plugin.xml) and copy icons.
        """
        logger.info("Generating JetBrains theme metadata")
        self.meta_inf_path.mkdir(parents=True, exist_ok=True)

        context = {
            **self.palette.model_dump(),
            "config": self.config.model_dump(),
        }

        # plugin.xml
        plugin_xml = self.meta_inf_path / "plugin.xml"
        logger.info("Generating %s", plugin_xml.name)
        template = self.env.get_template("plugin.xml.j2")
        content = template.render(**context)
        with plugin_xml.open("w") as f:
            f.write(content)
        logger.info("Successfully generated %s", plugin_xml.name)

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
