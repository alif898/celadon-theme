import json
import re
import tomllib
from pathlib import Path


def test_version_logic() -> None:
    """
    Verify that the build backend (Hatch) is correctly configured
    to pull the version from config.json.
    """
    # Get the version from config.json
    with Path("config.json").open() as f:
        config = json.load(f)
    expected_version = config["version"]

    # Parse pyproject.toml to find the Hatch Regex
    with Path("pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    pattern = pyproject["tool"]["hatch"]["version"]["pattern"]

    # Verify the regex actually finds the version in config.json
    config_content = Path("config.json").read_text()
    match = re.search(pattern, config_content)

    assert match is not None, "Hatch regex failed to find version in config.json"
    assert match.group("version") == expected_version, (
        f"Regex mismatch: Found {match.group('version')}, expected {expected_version}"
    )
