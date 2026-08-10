from pydantic import BaseModel, model_validator


class ConfigModel(BaseModel):
    """
    Model for config.json.
    """

    id: str
    name: str
    version: str
    short_description: str
    npm_description: str = ""
    vscode_screenshot_path: str | None = None
    plugin_name: str
    author: str
    vendor_url: str = ""
    description: str = ""
    description_file: str = ""
    jetbrains_description_suffix: str = ""
    change_notes: str | None = None
    github_url: str = ""
    vs_code_publisher: str = ""
    direct_git_url: str = ""
    issues_url: str = ""
    sponsor_url: str = ""

    @model_validator(mode="after")
    def _require_description_source(self) -> "ConfigModel":
        """
        Require at least one non-blank description source to avoid an empty
        description.
        """
        if not self.description.strip() and not self.description_file.strip():
            message = "config.json must provide 'description' or 'description_file'."
            raise ValueError(message)
        return self
