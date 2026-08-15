from jinja2 import DictLoader, Environment, select_autoescape

from celadon_theme.generator.base import AbstractThemeGenerator, compose_screenshot_url
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel


def test_abstract_generator(
    mock_palette: PaletteModel, mock_config: ConfigModel
) -> None:
    class DummyGenerator(AbstractThemeGenerator):
        def generate_theme_files(self) -> None:
            AbstractThemeGenerator.generate_theme_files(self)

        def generate_theme_metadata(self) -> None:
            AbstractThemeGenerator.generate_theme_metadata(self)

    env = Environment(
        loader=DictLoader({}),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )
    generator = DummyGenerator(mock_palette, mock_config, env)

    assert str(generator) == "DummyGenerator"
    # Call abstract methods which do nothing (pass).
    generator.generate_theme_files()
    generator.generate_theme_metadata()


def test_compose_screenshot_url(mock_config: ConfigModel) -> None:
    # A screenshot path and a full GitHub URL produce a jsDelivr URL pinned
    # to the version tag.
    mock_config.vscode_screenshot_path = "screenshots/vscode.png"
    mock_config.version = "1.2.3"
    mock_config.github_url = "https://github.com/alif898/celadon-theme"

    assert compose_screenshot_url(mock_config) == (
        "https://cdn.jsdelivr.net/gh/"
        "alif898/celadon-theme@v1.2.3/screenshots/vscode.png"
    )


def test_compose_screenshot_url_version_with_v_prefix(
    mock_config: ConfigModel,
) -> None:
    # A version that already starts with "v" must not produce a "vv" tag.
    mock_config.vscode_screenshot_path = "screenshots/vscode.png"
    mock_config.version = "v1.2.3"
    mock_config.github_url = "https://github.com/alif898/celadon-theme"

    assert compose_screenshot_url(mock_config) == (
        "https://cdn.jsdelivr.net/gh/"
        "alif898/celadon-theme@v1.2.3/screenshots/vscode.png"
    )


def test_compose_screenshot_url_missing_screenshot_path(
    mock_config: ConfigModel,
) -> None:
    # Without a screenshot path, no URL can be composed.
    mock_config.github_url = "https://github.com/alif898/celadon-theme"

    assert compose_screenshot_url(mock_config) is None


def test_compose_screenshot_url_missing_github_url(
    mock_config: ConfigModel,
) -> None:
    # A screenshot path without a GitHub URL cannot be resolved.
    mock_config.vscode_screenshot_path = "screenshots/vscode.png"
    mock_config.github_url = ""

    assert compose_screenshot_url(mock_config) is None


def test_compose_screenshot_url_short_github_url(
    mock_config: ConfigModel,
) -> None:
    # A GitHub URL with only one path segment cannot be split into owner and
    # repo, so no URL is composed.
    mock_config.vscode_screenshot_path = "screenshots/vscode.png"
    mock_config.github_url = "https://github.com/alif898"

    assert compose_screenshot_url(mock_config) is None
