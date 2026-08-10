from pathlib import Path

import pytest
from jinja2 import DictLoader, Environment, select_autoescape

import celadon_theme.generator.npm as npm_mod
from celadon_theme.generator.npm import NpmGenerator
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel

THEME_FILE_NAMES = [
    "celadon-claude-code.json",
    "celadon-qwen-code.json",
    "celadon-kimi-code.json",
    "celadon-pi.json",
    "celadon-windows-terminal.json",
]


class NpmPackageSetup:
    """
    Test context with dist path, theme sources, and metadata files.
    """

    def __init__(self, tmp_path: Path) -> None:
        self.dist_path = tmp_path / "npm"
        self.metadata_root = tmp_path

        self.theme_sources: dict[str, Path] = {}
        for file_name in THEME_FILE_NAMES:
            source_dir = tmp_path / file_name.removesuffix(".json")
            source_dir.mkdir()
            theme_file = source_dir / file_name
            theme_file.write_text(f'{{"name": "{file_name}"}}', encoding="utf-8")
            self.theme_sources[file_name] = theme_file

        (tmp_path / "CHANGELOG.md").write_text("Change Log Content")
        (tmp_path / "LICENSE.md").write_text("License Content")
        (tmp_path / "INSTRUCTIONS.md").write_text("Instructions Content")


@pytest.fixture
def mock_env() -> Environment:
    return Environment(
        loader=DictLoader(
            {
                "npm-package.json.j2": "PACKAGE: {{ config.version }}",
                "npm-README.md.j2": (
                    "README: {{ config.name }} | {{ theme_targets | length }} targets"
                ),
            }
        ),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


@pytest.fixture
def npm_package_setup(tmp_path: Path) -> NpmPackageSetup:
    """
    Build the dist path, theme sources, and metadata files for a test.
    """
    return NpmPackageSetup(tmp_path)


def _patch_theme_sources(
    monkeypatch: pytest.MonkeyPatch,
    theme_sources: dict[str, Path],
) -> None:
    monkeypatch.setattr(
        npm_mod,
        "THEME_SOURCE_FILES",
        {
            file_name: theme_file.parent
            for file_name, theme_file in theme_sources.items()
        },
    )


def _patch_metadata_sources(
    monkeypatch: pytest.MonkeyPatch,
    setup: NpmPackageSetup,
    metadata_root: Path | None = None,
) -> None:
    root = metadata_root or setup.metadata_root
    monkeypatch.setattr(npm_mod, "CHANGELOG_FILE", root / "CHANGELOG.md")
    monkeypatch.setattr(npm_mod, "LICENSE_FILE", root / "LICENSE.md")
    monkeypatch.setattr(npm_mod, "INSTRUCTIONS_FILE", root / "INSTRUCTIONS.md")


def test_npm_generator_theme_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    npm_package_setup: NpmPackageSetup,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    setup = npm_package_setup
    _patch_theme_sources(monkeypatch, setup.theme_sources)

    generator = NpmGenerator(
        mock_palette, mock_config, mock_env, dist_path=setup.dist_path
    )
    generator.generate_theme_files()

    for file_name, theme_file in setup.theme_sources.items():
        out_file = setup.dist_path / "themes" / file_name
        assert out_file.exists()
        assert out_file.read_text() == theme_file.read_text()


def test_npm_generator_theme_files_missing_source_raises(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    npm_package_setup: NpmPackageSetup,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A missing required source must abort generation instead of being skipped.
    setup = npm_package_setup
    missing = "celadon-pi.json"
    sources = {
        file_name: theme_file.parent
        for file_name, theme_file in setup.theme_sources.items()
    }
    sources[missing] = setup.dist_path.parent / "does-not-exist"
    monkeypatch.setattr(npm_mod, "THEME_SOURCE_FILES", sources)

    generator = NpmGenerator(
        mock_palette, mock_config, mock_env, dist_path=setup.dist_path
    )
    with pytest.raises(FileNotFoundError):
        generator.generate_theme_files()


def test_npm_generator_theme_files_removes_stale_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    npm_package_setup: NpmPackageSetup,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Theme JSONs no longer part of THEME_SOURCE_FILES must be removed.
    setup = npm_package_setup
    _patch_theme_sources(monkeypatch, setup.theme_sources)
    stale_file = setup.dist_path / "themes" / "celadon-obsolete.json"

    generator = NpmGenerator(
        mock_palette, mock_config, mock_env, dist_path=setup.dist_path
    )
    generator.generate_theme_files()
    stale_file.write_text('{"name": "obsolete"}', encoding="utf-8")
    generator.generate_theme_files()

    assert not stale_file.exists()
    for file_name in THEME_FILE_NAMES:
        assert (setup.dist_path / "themes" / file_name).exists()


def test_npm_generator_metadata(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    npm_package_setup: NpmPackageSetup,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    setup = npm_package_setup
    _patch_theme_sources(monkeypatch, setup.theme_sources)
    _patch_metadata_sources(monkeypatch, setup)

    generator = NpmGenerator(
        mock_palette, mock_config, mock_env, dist_path=setup.dist_path
    )
    generator.generate_theme_metadata()

    assert (setup.dist_path / "package.json").read_text() == (
        f"PACKAGE: {mock_config.version}"
    )
    assert (setup.dist_path / "README.md").read_text() == (
        f"README: {mock_config.name} | {len(npm_mod.THEME_TARGETS)} targets"
    )
    assert (setup.dist_path / "INSTRUCTIONS.md").read_text() == ("Instructions Content")
    assert (setup.dist_path / "CHANGELOG.md").read_text() == "Change Log Content"
    assert (setup.dist_path / "LICENSE.md").read_text() == "License Content"


def test_npm_generator_metadata_missing_files(
    mock_palette: PaletteModel,
    mock_config: ConfigModel,
    mock_env: Environment,
    npm_package_setup: NpmPackageSetup,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    setup = npm_package_setup
    _patch_theme_sources(monkeypatch, setup.theme_sources)
    missing_root = setup.metadata_root / "missing"
    _patch_metadata_sources(monkeypatch, setup, metadata_root=missing_root)

    generator = NpmGenerator(
        mock_palette, mock_config, mock_env, dist_path=setup.dist_path
    )
    generator.generate_theme_metadata()

    assert not (setup.dist_path / "CHANGELOG.md").exists()
    assert not (setup.dist_path / "LICENSE.md").exists()
    assert not (setup.dist_path / "INSTRUCTIONS.md").exists()
    assert (setup.dist_path / "package.json").exists()
    assert (setup.dist_path / "README.md").exists()
