from pydantic import BaseModel


class ConfigModel(BaseModel):
    """
    Model for config.json.
    """

    id: str
    name: str
    version: str
    short_description: str
    vscode_screenshot_path: str | None = None
    plugin_name: str
    author: str
    vendor_url: str = ""
    description: str
    jetbrains_description_suffix: str = ""
    change_notes: str | None = None
    github_url: str = ""
    vs_code_publisher: str = ""
    direct_git_url: str = ""
    issues_url: str = ""
    sponsor_url: str = ""
