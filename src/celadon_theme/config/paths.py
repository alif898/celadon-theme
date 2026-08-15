import logging
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT_FIXED_DEPTH = 3
PYPROJECT_FILE = "pyproject.toml"


def get_project_root() -> Path:
    """
    Finds the project root by looking for pyproject.toml.
    """
    logger.info("Finding project root")

    current = Path(__file__).resolve().parent
    logger.info("Current directory: %s", current)
    for parent in [current, *list(current.parents)]:
        logger.info("Checking parent: %s", parent)
        if (parent / PYPROJECT_FILE).exists():
            logger.info("Project root found: %s", parent)
            return parent
        logger.warning(
            "File: %s not found, skipping root check step for %s",
            PYPROJECT_FILE,
            parent,
        )

    # Fallback to a fixed depth if not found (src/celadon_theme/config/paths.py).
    logger.warning("Project root not found, using fixed depth: %s", ROOT_FIXED_DEPTH)
    return Path(__file__).resolve().parents[ROOT_FIXED_DEPTH]


# Set up commonly used paths.
ROOT_DIR = get_project_root()
TEMPLATES_DIR = ROOT_DIR / "templates"
JETBRAINS_DIR = ROOT_DIR / "jetbrains"
VSCODE_DIR = ROOT_DIR / "vscode"
CLAUDE_CODE_DIR = ROOT_DIR / "claude-code"
QWEN_CODE_DIR = ROOT_DIR / "qwen-code"
KIMI_CODE_DIR = ROOT_DIR / "kimi-code"
PI_DIR = ROOT_DIR / "pi"
WINDOWS_TERMINAL_DIR = ROOT_DIR / "windows-terminal"
OPENCODE_DIR = ROOT_DIR / "opencode"
NPM_DIR = ROOT_DIR / "npm"
PALETTE_FILE = ROOT_DIR / "palette.yml"
CONFIG_FILE = ROOT_DIR / "config.json"
CHANGELOG_FILE = ROOT_DIR / "CHANGELOG.md"
LICENSE_FILE = ROOT_DIR / "LICENSE.md"
INSTRUCTIONS_FILE = ROOT_DIR / "INSTRUCTIONS.md"
PLUGIN_ICON_SVG = TEMPLATES_DIR / "pluginIcon.svg"
SAMPLE_PROJECTS_DIR = ROOT_DIR / "sample-projects"
