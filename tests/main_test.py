from jinja2 import StrictUndefined

from celadon_theme.main import _build_environment


def test_main_environment_uses_strict_undefined() -> None:
    """
    The generator environment must fail fast on missing template keys
    instead of silently rendering empty strings.
    """
    env = _build_environment()
    assert env.undefined is StrictUndefined
