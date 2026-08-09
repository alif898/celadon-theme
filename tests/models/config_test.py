import pytest
from pydantic import ValidationError

from celadon_theme.models.config import ConfigModel


def test_url_fields_default_to_empty_string() -> None:
    """
    URL fields must default to an empty string so templates render valid
    values instead of the literal string "None".
    """
    model = ConfigModel(
        id="test.id",
        name="Test Theme",
        version="1.0.0",
        short_description="Test Short Description",
        plugin_name="Test Plugin",
        author="Test Author",
        description="Test Description",
    )

    assert model.vendor_url == ""
    assert model.github_url == ""
    assert model.vs_code_publisher == ""
    assert model.direct_git_url == ""
    assert model.issues_url == ""
    assert model.sponsor_url == ""


def test_description_file_accepts_file_only_config() -> None:
    """
    Config may reference an external description file instead of inlining
    the long-form description in config.json.
    """
    model = ConfigModel(
        id="test.id",
        name="Test Theme",
        version="1.0.0",
        short_description="Test Short Description",
        plugin_name="Test Plugin",
        author="Test Author",
        description_file="description.html",
    )

    assert model.description == ""
    assert model.description_file == "description.html"


def test_config_requires_description_source() -> None:
    """
    A config without 'description' or 'description_file' must be rejected
    so templates never render an empty description.
    """
    with pytest.raises(ValidationError):
        ConfigModel(
            id="test.id",
            name="Test Theme",
            version="1.0.0",
            short_description="Test Short Description",
            plugin_name="Test Plugin",
            author="Test Author",
        )


@pytest.mark.parametrize(
    ("description", "description_file"),
    [("   ", ""), ("", "   ")],
)
def test_config_rejects_whitespace_only_description_source(
    description: str,
    description_file: str,
) -> None:
    """
    Whitespace-only description sources must be rejected so templates never
    render an empty description.
    """
    with pytest.raises(ValidationError):
        ConfigModel(
            id="test.id",
            name="Test Theme",
            version="1.0.0",
            short_description="Test Short Description",
            plugin_name="Test Plugin",
            author="Test Author",
            description=description,
            description_file=description_file,
        )
