from pydantic import BaseModel


class ConfigModel(BaseModel):
    """
    Model for config.json
    """
    id: str
    name: str
    version: str
    group: str | None = None
    plugin_name: str
    author: str
    vendor_url: str | None = None
    description: str
    change_notes: str | None = None
    github_url: str | None = None
