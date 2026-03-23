import importlib.metadata
import json
from pathlib import Path


def test_version_sync() -> None:
    """
    Ensure the installed package version matches config.json.
    """
    with Path("config.json").open() as f:
        config = json.load(f)

    expected_version = config["version"]
    # This checks the version of the package installed in the 'uv' environment
    actual_version = importlib.metadata.version("celadon-theme")

    assert actual_version == expected_version, (
        f"Sync Error: config.json: {expected_version}, package: {actual_version}"
    )
