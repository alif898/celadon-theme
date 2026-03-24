import logging
from logging.config import dictConfig

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config.logging_config import logging_config
from .config.paths import CONFIG_FILE, PALETTE_FILE, TEMPLATES_DIR
from .generator.jetbrains import JetBrainsGenerator
from .generator.vscode import VsCodeGenerator
from .template.parser import ThemeParser


def main() -> None:
    """
    Main function used to generate theme files.
    """
    dictConfig(logging_config.model_dump())
    logger = logging.getLogger(__name__)
    logger.info("Starting theme generation")

    # Load palette and config data
    logger.info("Loading palette and config data")
    palette = ThemeParser.load_palette(PALETTE_FILE)
    config = ThemeParser.load_config(CONFIG_FILE)
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )
    logger.info(
        "Successfully loaded palette and config data, found version: %s", config.version
    )

    # Initialize theme generators, for any new target theme type, add class here
    generators = [
        JetBrainsGenerator(palette, config, env),
        VsCodeGenerator(palette, config, env),
    ]
    logger.info("Initialized theme generators: %s", generators)

    for generator in generators:
        generator.generate_theme_files()
        generator.generate_theme_metadata()

    logger.info(
        "Theme generation completed successfully for version: %s", config.version
    )


if __name__ == "__main__":
    main()
