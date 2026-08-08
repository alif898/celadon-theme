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
