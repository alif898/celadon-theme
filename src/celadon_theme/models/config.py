from pydantic import BaseModel


class ConfigModel(BaseModel):
    """
    Model for config.json.
    """

    id: str
    name: str
    version: str
    short_description: str
    vscode_description_prefix: str | None = None
    plugin_name: str
    author: str
    vendor_url: str | None = None
    description: str
    change_notes: str | None = None
    github_url: str | None = None
    vs_code_publisher: str | None = None
    direct_git_url: str | None = None
    issues_url: str | None = None
    sponsor_url: str | None = None
