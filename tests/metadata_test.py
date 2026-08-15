import json
import re
import tomllib

from celadon_theme.config.paths import CONFIG_FILE, ROOT_DIR


def test_version_logic() -> None:
    """
    Verify that the build backend (Hatch) is correctly configured
    to pull the version from config.json.
    """
    # Get the version from config.json.
    with CONFIG_FILE.open(encoding="utf-8") as f:
        config = json.load(f)
    expected_version = config["version"]

    # Parse pyproject.toml to find the Hatch Regex.
    with (ROOT_DIR / "pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    pattern = pyproject["tool"]["hatch"]["version"]["pattern"]

    # Verify the regex actually finds the version in config.json.
    config_content = CONFIG_FILE.read_text(encoding="utf-8")
    match = re.search(pattern, config_content)

    assert match is not None, "Hatch regex failed to find version in config.json"
    assert match.group("version") == expected_version, (
        f"Regex mismatch: Found {match.group('version')}, expected {expected_version}"
    )


def test_license_metadata() -> None:
    """
    Verify that the project license uses PEP 639 SPDX metadata instead of
    the deprecated `license = { file = ... }` table.
    """
    with (ROOT_DIR / "pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    project = pyproject["project"]
    assert project["license"] == "MIT"
    assert "LICENSE.md" in project["license-files"]
