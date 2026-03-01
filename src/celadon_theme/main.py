import logging
from jinja2 import Environment, FileSystemLoader
from logging.config import dictConfig

from .config.logging_config import logging_config
from .config.paths import PALETTE_FILE, CONFIG_FILE, TEMPLATES_DIR
from .generator.jetbrains import JetbrainsGenerator
from .template.parser import ThemeParser


def main() -> None:
    dictConfig(logging_config.model_dump())
    logger = logging.getLogger(__name__)
    logger.info("Starting theme generation")

    # Load data
    palette = ThemeParser.load_palette(PALETTE_FILE)
    config = ThemeParser.load_config(CONFIG_FILE)
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    
    # Initialize theme generators
    generators = [
        JetbrainsGenerator(palette, config, env)
    ]
    logger.info(f"Initialized theme generators: {generators}")
    
    for generator in generators:
        generator.generate_theme_files()
        generator.generate_theme_metadata()
    
    logger.info("Theme generation completed successfully")


if __name__ == "__main__":
    main()