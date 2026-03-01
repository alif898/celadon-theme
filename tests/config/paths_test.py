from pathlib import Path
from celadon_theme.config.paths import get_project_root, ROOT_DIR, TEMPLATES_DIR, JETBRAINS_DIR, PALETTE_FILE, CONFIG_FILE

def test_get_project_root() -> None:
    root = get_project_root()
    assert isinstance(root, Path)
    assert (root / "pyproject.toml").exists()

def test_paths_constants() -> None:
    assert ROOT_DIR.exists()
    assert TEMPLATES_DIR == ROOT_DIR / "templates"
    assert JETBRAINS_DIR == ROOT_DIR / "jetbrains"
    assert PALETTE_FILE == ROOT_DIR / "palette.yml"
    assert CONFIG_FILE == ROOT_DIR / "config.json"
