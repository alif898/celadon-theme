import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """
    Finds the project root by looking for pyproject.toml
    """
    logger.info("Finding project root")

    current = Path(__file__).resolve().parent
    logger.info(f"Current directory: {current}")
    for parent in [current] + list(current.parents):
        logger.info(f"Checking parent: {parent}")
        if (parent / "pyproject.toml").exists():
            logger.info(f"Project root found: {parent}")
            return parent
    
    # Fallback to a fixed depth if not found (src/celadon_theme/core/paths.py)
    logger.warning("Project root not found, using fixed depth")
    return Path(__file__).resolve().parents[3]


ROOT_DIR = get_project_root()
TEMPLATES_DIR = ROOT_DIR / "templates"
JETBRAINS_DIR = ROOT_DIR / "jetbrains"
PALETTE_FILE = ROOT_DIR / "palette.yml"
CONFIG_FILE = ROOT_DIR / "config.json"
