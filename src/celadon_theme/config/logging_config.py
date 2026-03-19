from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings

LOGGER_FORMAT = (
    "[%(asctime)s][%(levelname)s][%(name)s][%(funcName)s:%(lineno)d]: %(message)s"
)


class LoggingConfig(BaseSettings):
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict[str, Any] = Field(default_factory=dict)
    handlers: dict[str, Any] = Field(default_factory=dict)
    loggers: dict[str, Any] = Field(default_factory=dict)


logging_config = LoggingConfig(
    formatters={
        "standard": {
            "format": LOGGER_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    handlers={
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    loggers={
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
)
