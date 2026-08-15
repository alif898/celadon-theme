from jinja2 import StrictUndefined

from celadon_theme.generator.npm import NpmGenerator
from celadon_theme.main import _build_environment, _build_generators
from celadon_theme.models.config import ConfigModel
from celadon_theme.models.palette import PaletteModel


def test_main_environment_uses_strict_undefined() -> None:
    """
    The generator environment must fail fast on missing template keys
    instead of silently rendering empty strings.
    """
    env = _build_environment()
    assert env.undefined is StrictUndefined


def test_build_generators_keeps_npm_last(
    mock_palette: PaletteModel, mock_config: ConfigModel
) -> None:
    """
    NpmGenerator packages the single-file theme outputs of the other
    generators, so it must always be the last generator in the list.
    """
    env = _build_environment()

    generators = _build_generators(mock_palette, mock_config, env)

    assert type(generators[-1]) is NpmGenerator
