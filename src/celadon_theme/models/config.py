import re

from pydantic import BaseModel, field_validator, model_validator

# Canonical SemVer (semver.org). Keep in sync with the ERE used to validate
# release tags in .github/workflows/release.yml.
_SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(-((0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(\.(0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(\+([0-9a-zA-Z-]+(\.[0-9a-zA-Z-]+)*))?$"
)


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

    @field_validator("version")
    @classmethod
    def _validate_semver(cls, value: str) -> str:
        """
        Require the version to be valid SemVer.
        """
        if not _SEMVER_PATTERN.fullmatch(value):
            message = (
                f"'{value}' is not valid SemVer (expected X.Y.Z[-prerelease][+build])."
            )
            raise ValueError(message)
        return value

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
