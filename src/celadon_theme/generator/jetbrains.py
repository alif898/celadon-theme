import logging
import shutil
from pathlib import Path

from jinja2 import Environment
from celadon_theme.generator.base import AbstractThemeGenerator
from celadon_theme.config.paths import JETBRAINS_DIR, TEMPLATES_DIR
from celadon_theme.models.palette import PaletteModel
from celadon_theme.models.config import ConfigModel


logger = logging.getLogger(__name__)


class JetbrainsGenerator(AbstractThemeGenerator):
    """
    Generator for JetBrains IDEs
    """

    def __init__(self, palette: PaletteModel, config: ConfigModel, env: Environment, dist_path: Path = JETBRAINS_DIR):
        super().__init__(palette, config, env)
        self.dist_path = dist_path
        self.resources_path = self.dist_path / "src/main/resources"
        self.themes_path = self.resources_path / "themes"
        self.meta_inf_path = self.resources_path / "META-INF"

    def generate_theme_files(self) -> None:
        """
        Generate core theme files (XML and JSON)
        """
        logger.info("Generating JetBrains theme files")
        self.themes_path.mkdir(parents=True, exist_ok=True)
        
        context = {
            **self.palette.model_dump(),
            "manifest": self.config.model_dump()
        }

        files = {
            "celadon.icls.j2": self.themes_path / "Celadon.xml",
            "celadon.theme.json.j2": self.themes_path / "celadon.theme.json"
        }

        for tpl_name, out_path in files.items():
            template = self.env.get_template(tpl_name)
            content = template.render(**context)
            with open(out_path, "w") as f:
                f.write(content)
        
        # Project files
        gradle_props = self.dist_path / "gradle.properties"
        template = self.env.get_template("gradle.properties.j2")
        content = template.render(**context)
        with open(gradle_props, "w") as f:
            f.write(content)

        logger.info("JetBrains theme files generated")

    def generate_theme_metadata(self) -> None:
        """
        Generate metadata (plugin.xml) and copy icons
        """
        logger.info("Generating JetBrains theme metadata")
        self.meta_inf_path.mkdir(parents=True, exist_ok=True)

        context = {
            **self.palette.model_dump(),
            "manifest": self.config.model_dump()
        }

        # plugin.xml
        plugin_xml = self.meta_inf_path / "plugin.xml"
        template = self.env.get_template("plugin.xml.j2")
        content = template.render(**context)
        with open(plugin_xml, "w") as f:
            f.write(content)

        # Static assets
        shutil.copy(TEMPLATES_DIR / "pluginIcon.svg", self.meta_inf_path / "pluginIcon.svg")

        logger.info("JetBrains theme metadata generated")
