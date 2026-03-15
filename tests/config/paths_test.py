import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from celadon_theme.config.paths import get_project_root, ROOT_DIR, TEMPLATES_DIR, JETBRAINS_DIR, PALETTE_FILE, CONFIG_FILE

def test_get_project_root() -> None:
    root = get_project_root()
    assert isinstance(root, Path)
    assert (root / "pyproject.toml").exists()

def test_get_project_root_fallback() -> None:
    # Test fallback by mocking Path.exists to always return False
    with patch.object(Path, "exists", return_value=False):
        # We need to use a different approach because get_project_root is called during module import
        # But we can call the function directly
        root = get_project_root()
        # The implementation in src/celadon_theme/config/paths.py uses:
        # Path(__file__).resolve().parents[3]
        # Since that file is in src/celadon_theme/config/, it's 3 levels from root
        import celadon_theme.config.paths as paths_mod
        expected = Path(paths_mod.__file__).resolve().parents[3]
        assert root == expected

def test_paths_constants() -> None:
    assert ROOT_DIR.exists()
    assert TEMPLATES_DIR == ROOT_DIR / "templates"
    assert JETBRAINS_DIR == ROOT_DIR / "jetbrains"
    assert PALETTE_FILE == ROOT_DIR / "palette.yml"
    assert CONFIG_FILE == ROOT_DIR / "config.json"
